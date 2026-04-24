
from __future__ import annotations 

import copy      
import hashlib   
import json      
import re        
from typing import Any

import inflect  

from .config import (
    URL_PREFIX_PATTERN,       
    FILTER_PATHS,             
    FILTER_RESPONSE_FIELDS,   
    HTTP_METHODS,             
    PARAM_DEFAULTS,           
)

INFLECT = inflect.engine()
_RESERVED_KEYWORDS: frozenset[str] = frozenset({"Default", "Ref", "Type"})


def _to_single(word: str) -> str:
    """Return the singular form of word, or word unchanged if already singular."""
    result = INFLECT.singular_noun(word)  # type: ignore[arg-type]
    return result if isinstance(result, str) else word


def _plural(word: str) -> str:
    """Return the plural form of word, or word+'s' if inflect cannot determine one."""
    result = INFLECT.plural(word)  # type: ignore[arg-type]
    return result if isinstance(result, str) else word + "s"


def _to_pascal(word: str) -> str:
    """Capitalise the first character of a word, leaving the rest unchanged."""
    return word[:1].upper() + word[1:]


def _extract_segments(url: str) -> list[str]:
    """Strip the common URL prefix and return the non-empty path segments."""
    url = URL_PREFIX_PATTERN.sub("", url).rstrip("/")
    return [seg for seg in url.split("/") if seg]

def _strip_keys(obj: Any, *keys: str) -> None:
    if isinstance(obj, dict):
        for k in keys:
            obj.pop(k, None)
        for v in obj.values():
            _strip_keys(v, *keys)
    elif isinstance(obj, list):
        for item in obj:
            _strip_keys(item, *keys)

def _reduce_segments(parts: list[str]) -> list[str]:
    """
    Remove path parameter elements and singularize each word in a path.

    Examples:
        ["companies", "0", "sites", "{siteID}"]  → ["site"]
        ["jobs", "{jobID}", "notes"]              → ["job", "note"]
        ["staff"]                                 → ["staff"]
    """
    cleaned: list[str] = []
    for seg in parts:
        if seg.startswith("{") and seg.endswith("}"):
            continue
        seg = _to_single(seg)
        cleaned.append(seg)
    return cleaned


def _is_collection(url: str) -> bool:
    """Return True when the URL addresses a collection.
      - /sites/              → collection  (returns all sites)
      - /sites/{siteID}      → single item (returns one site)
    """
    return not url.rstrip("/").endswith("}")


def _find_single_item_path(list_path: str, all_paths: dict[str, Any]) -> str | None:
    """
    For a collection path like /sites/, the single-item sibling is
    /sites/{siteID} — a path that starts with the same prefix and ends
    with exactly one path parameter placeholder.

    We need this to enrich list-endpoint schemas: if GET /sites/ doesn't
    specify what shape its items have, we look at GET /sites/{siteID} to
    find out.
    """
    prefix = list_path.rstrip("/")
    for candidate in all_paths:
        # The sibling must start with the same prefix plus "/"
        if not candidate.startswith(prefix + "/"):
            continue
        # Everything after the shared prefix must be exactly one {placeholder}
        remainder = candidate[len(prefix) + 1:]
        # re.fullmatch ensures the entire remainder matches {something}
        if re.fullmatch(r"\{[^}]+\}", remainder):
            return candidate
    return None

def _build_resource_name(url: str) -> str:
    """
    Derive an UpperCamelCase resource name from a URL path.
    
    Examples:
        "/api/.../sites/"                  → "Sites"
        "/api/.../sites/{siteID}"          → "Site"
        "/api/.../jobs/{jobID}/notes/"     → "JobNotes"
        "/api/.../jobs/{jobID}/notes/{id}" → "JobNote"
    """
    # Reduce the URL to only its meaningful segments (singularised, no params)
    parts = _reduce_segments(_extract_segments(url))
    if not parts:
        # URL had no meaningful segments after stripping — return empty string.
        return ""
    # Capitalise each segment to get PascalCase words
    name_parts = [_to_pascal(word) for word in parts]
    if _is_collection(url):
        # (collections only): re-pluralise the last word.
        last_lower = parts[-1]
        name_parts[-1] = _to_pascal(_plural(last_lower))
    # concatenate all words → "Job" + "Notes" = "JobNotes"
    return "".join(name_parts)


def _build_operation_id(method: str, resource_name: str) -> str:
    """
    Build an operationId from a HTTP method and resource name.

    An operationId is the unique name for a single API operation, used by code
    generators. Convention is <method><ResourceName>, e.g.:
        GET  /sites/       → getSites
        POST /sites/       → postSites
        GET  /sites/{id}   → getSite

    """
    return method + re.sub(r"By[A-Z][A-Za-z0-9]*", "", resource_name)


def _url_parameters(path: str) -> list[str]:
    """
    Return all {placeholder} names found in a URL path template.

    URL path parameters are enclosed in curly braces.
    
    re.findall returns all non-overlapping matches of the group inside {…}.
    """
    return re.findall(r"\{([^}]+)\}", path)


def _register_and_ref_params(params: list[dict[str, Any]], components: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Register each parameter in components and return a list of $ref dicts.

    DISAMBIGUATION: The same parameter name can appear in different "locations"
    (the "in" field). For example, "type" might be both a path parameter
    (in: path) and a query parameter (in: query). When we encounter this we
    append "_<location>" to the key so both coexist without conflict.

    Args:
        params:     List of parameter dicts, possibly already containing $refs.
        components: The shared components/parameters dict (mutated in-place).

    Returns:
        A list of {"$ref": "#/components/parameters/<key>"} dicts replacing the
        original inline definitions.
    """
    refs: list[dict[str, Any]] = []
    for param in params:
        # If it's already a $ref, nothing to register — keep it as-is.
        if "$ref" in param:
            refs.append(param)
            continue

        name = param["name"]          # e.g. "siteID"
        in_type = param.get("in", "") # e.g. "path", "query", "header"

        if name not in components:
            if name in PARAM_DEFAULTS:
                schema = {**param.get("schema", {}), "default": PARAM_DEFAULTS[name]}
                param = {**param, "schema": schema}
            components[name] = param
            key = name
        elif components[name].get("in") == in_type:
            # Same name AND same location — this is a duplicate declaration.
            # Reuse the existing canonical definition; do not overwrite it.
            key = name
        else:
            # Same name, DIFFERENT location (e.g. "type" used as both path and query param).
            # We need two separate component entries to preserve both definitions.
            key = f"{name}_{in_type}"  # e.g. "type_query"
            if key not in components:
                components[key] = param

        # Replace the inline definition with a pointer to the component entry.
        refs.append({"$ref": f"#/components/parameters/{key}"})
    return refs


def _split_and_ref_params(params: list[dict[str, Any]], components: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Register params in components and return $refs — path params first.

    Why separate path from non-path? Path parameters (in: path) must be declared
    to match every {placeholder} in the URL. Keeping them first makes validation
    easier and the output more readable.
    """
    inline = [p for p in params if "$ref" not in p]
    existing_refs = [p for p in params if "$ref" in p]

    return (
        # Path params first (in: path)
        _register_and_ref_params([p for p in inline if p.get("in") == "path"], components)
        # Then all other params (query, header, cookie…)
        + _register_and_ref_params([p for p in inline if p.get("in") != "path"], components)
        # Keep any pre-existing $refs at the end
        + existing_refs
    )


def _declared_param_names(params: list[dict[str, Any]], components: dict[str, Any]) -> set[str]:
    """
    Return the set of parameter names already declared in the params list.

    A parameter list can contain either:
      - An inline definition: {"name": "siteID", "in": "path", ...}
      - A $ref pointer:       {"$ref": "#/components/parameters/siteID"}

    We need the actual name in both cases so we can compare against the
    {placeholder} names extracted from the URL string.

    Args:
        params:     The list of parameter objects (mix of inline and $ref).
        components: The components/parameters dict, used to resolve $refs.

    Returns:
        A set of parameter name strings, e.g. {"siteID", "page", "filter"}
    """
    names: set[str] = set()
    for param in params:
        if "$ref" in param:
            # $ref looks like "#/components/parameters/siteID" — take the last segment
            ref_key = param["$ref"].split("/")[-1]
            # Look up the actual definition to get the "name" field
            resolved = components.get(ref_key)
            if resolved:
                names.add(resolved["name"])
        elif "name" in param:
            # Inline definition — the name is right there
            names.add(param["name"])
    return names


def _ensure_path_params_present(params: list[dict[str, Any]], path: str, components: dict[str, Any]) -> list[dict[str, Any]]:
    """
    OpenAPI requires that every {placeholder} in a URL template has a
    corresponding parameter with in="path". This function guarantees the spec is valid 
    by synthesising any missing path parameters.

    When a parameter name is not yet in components, we create a minimal
    definition with type=integer (since IDs are always integers).
    If it's already in components (registered from another endpoint), we just
    create a $ref to the existing definition.
    """
    covered = _declared_param_names(params, components)
    for required in _url_parameters(path):
        if required not in covered:
            if required not in components:
                # No existing definition for this parameter anywhere — synthesise one.
                # We assume integer type because URL {...} IDs are always integers.
                components[required] = {
                    "name": required,
                    "in": "path",
                    "required": True,          # Path params are always required by definition
                    "schema": {"type": "integer"},
                }
            # Append a $ref so this operation's parameter list includes it
            params.append({"$ref": f"#/components/parameters/{required}"})
            covered.add(required)
    return params


# ── Schema deduplication ──────────────────────────────────────────────────────
# The goal of this section is to give every inline schema object a stable name
# and move it into components/schemas, replacing it with a "$ref" pointer.
#
# WHY? Code generators like progenitor derive Rust struct names directly from
# component keys. Without this step, deeply nested inline objects get auto-names
# like "_200ResponseInner" which are ugly and unstable across regenerations.


def _schema_hash(obj: dict[str, Any]) -> str:
    """Return a stable SHA-256 hex digest for a schema dict, used for equality checks.

    We need to compare two schema objects to decide if they're identical. Python
    dict equality (==) works, but we often need a short fingerprint to use as a
    map key or suffix. A hash gives us that.

    We serialise the dict to JSON with sorted keys so that {"b":1,"a":2} and
    {"a":2,"b":1} produce the same hash (key order doesn't matter semantically).

    Returns the full 64-character hex digest (we often slice it to 6 chars for
    readable suffixes in schema names).
    """
    # json.dumps with sort_keys=True ensures key order is canonical
    # separators=(",", ":") removes whitespace for a compact, deterministic string
    canonical = json.dumps(obj, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode()).hexdigest()


def _normalize_schema_key(name: str) -> str:
    """Convert a property name to UpperCamelCase safe for use as a Rust identifier.

    Transformations applied:
      - Split the name into words by finding uppercase/lowercase transitions.
      - Re-join with each word capitalised → UpperCamelCase.
      - Normalise trailing ALL-CAPS abbreviations so they survive snake_case
        conversion without producing ugly names:
          SiteID    → SiteId   (not SiteI_D)
          TypeUUID  → TypeUuid (not TypeU_U_I_D)
      - If the result is a reserved Rust name, append "Value":
          "default" → "Default" → "DefaultValue"

    Examples:
        "siteID"       → "SiteId"
        "typeID"       → "TypeId"
        "default"      → "DefaultValue"
        "workOrderID"  → "WorkOrderId"
    """
    # re.findall with this pattern splits a CamelCase name into words:
    #   [A-Z]+(?=[A-Z][a-z])  → catches "ID" in "IDCard" (all-caps before Cap+lower)
    #   [A-Z]?[a-z]+          → catches "site", "Id"
    #   [A-Z]+                → catches isolated all-caps like "ID" at end
    #   [0-9]+                → catches numeric segments
    words: list[str] = re.findall(r"[A-Z]+(?=[A-Z][a-z])|[A-Z]?[a-z]+|[A-Z]+|[0-9]+", name)
    # Capitalise each word and join → UpperCamelCase
    normalized = "".join(w.capitalize() for w in words) if words else name
    # Guard against Rust reserved names
    if normalized in _RESERVED_KEYWORDS:
        normalized += "Value"
    return normalized


def _merge_schemas(existing: dict[str, Any], incoming: dict[str, Any]) -> dict[str, Any]:
    """Union two schemas for the same component name, dropping all required constraints.

    PROBLEM: Multiple endpoints can return a schema under the same name but with
    different subsets of fields. For example, "Site" returned by GET /sites/ might
    have 5 fields while GET /sites/{siteID} returns 20 fields.

    We can't know which is "canonical", so we take the union: include ALL fields
    from both schemas. To avoid breaking consumers that only expect the smaller set,
    we make EVERYTHING optional by dropping the "required" list.

    A union schema is always backward-compatible: a consumer that expects a 5-field
    Site will still work if the actual response has 20 fields — the extra fields are
    just ignored.

    Resolution for top-level scalar fields (type, format, description):
    "existing wins" — the first registered version is kept on conflict.

    Args:
        existing: The schema already stored in components (first-seen).
        incoming: The new schema being merged in.

    Returns:
        A new dict that is the union of both schemas.
    """
    # Start with a shallow copy of the existing schema
    merged = dict(existing)

    existing_props = existing.get("properties", {})
    incoming_props = incoming.get("properties", {})

    if existing_props or incoming_props:
        # Union the properties dicts. Where keys clash, incoming wins for the property
        # definition, but we've already captured the existing value above.
        merged["properties"] = {**existing_props, **incoming_props}
        # Drop "required": neither schema's required list is valid for the union,
        # because a field required in one might be absent from the other variant.
        merged.pop("required", None)
        # Explicitly mark type=object to be unambiguous
        merged["type"] = "object"

    # For primitive-level fields: only copy from incoming if missing in existing.
    # This implements "existing wins on conflict".
    for key in ("format", "description", "example", "enum", "minimum", "maximum", "default", "nullable"):
        if key not in merged and key in incoming:
            merged[key] = incoming[key]

    return merged


def _apply_field_filter(schema: dict[str, Any], allowed: set[str]) -> dict[str, Any]:
    """Return a copy of schema with properties restricted to the allowed set.

    When config.yaml specifies filter.response_fields for a schema, we keep only
    the listed properties and discard all others. This reduces the generated Rust
    types to only the fields the application actually uses.

    We also update the "required" list to remove any fields that were filtered out,
    since a required field that doesn't exist in the schema would be invalid OpenAPI.

    Args:
        schema:  The full schema dict (not mutated).
        allowed: A set of property names to keep.

    Returns:
        A new schema dict with only the allowed properties.
    """
    props = schema.get("properties")
    if not props:
        # Schema has no properties (e.g. it's a scalar or array) — nothing to filter
        return schema

    # Build a new schema dict that replaces "properties" with only the allowed subset
    filtered = {**schema, "properties": {k: v for k, v in props.items() if k in allowed}}

    if "required" in filtered:
        # Remove from "required" any field that was filtered out
        kept = [f for f in filtered["required"] if f in allowed]
        if kept:
            filtered["required"] = kept
        else:
            # All required fields were filtered — remove the key entirely
            del filtered["required"]

    return filtered


def _unique_name(base: str, obj: dict[str, Any], components: dict[str, Any], context: str = "") -> str:
    """Return a component name for a schema that collides with an existing entry.

    Called when we want to register a schema under `base` but something different
    is already there. We try two strategies:

    Strategy 1 — Context prefix:
        If a `context` (parent schema name) is provided, try `context + base`.
        For example, if "Staff" is taken and context is "Schedule", try "ScheduleStaff".
        This is preferred because it produces readable names.

    Strategy 2 — Hash suffix:
        If the context slot is also taken by a different schema, fall back to
        `base + <6-char hash>`. This is always unique but less readable.
        Example: "Staff3f9a1c"

    We check if the slot is taken by a DIFFERENT schema (same hash → same content
    → reuse is safe, no suffix needed).
    """
    if context:
        # Build the candidate by prepending context if base doesn't already start with it
        candidate = base if base.startswith(context) else context + base
        # Reuse if slot is empty OR already holds the same schema (by hash)
        if candidate not in components or _schema_hash(components[candidate]) == _schema_hash(obj):
            return candidate
    # Fall back to a short hash suffix for uniqueness
    return f"{base}{_schema_hash(obj)[:6].capitalize()}"


def _is_primitive(obj: dict[str, Any]) -> bool:
    """Return True when obj is a scalar schema with no sub-structure worth extracting.

    Primitive schemas are things like:
        {"type": "string"}
        {"type": "integer", "format": "int64"}
        {"type": "boolean"}
        {"type": "string", "enum": ["active", "inactive"]}

    These don't produce meaningful named types in code generators — a Rust type
    alias for `String` gains nothing. We keep them inline rather than extracting
    them to components.

    Non-primitive schemas have "properties" (object), "allOf"/"anyOf"/"oneOf"
    (composition), "type": "array", or "items" (array).
    """
    if not isinstance(obj, dict) or "$ref" in obj:
        # Not a dict, or already a $ref → treat as non-primitive (don't extract)
        return False
    # A schema is primitive if it has none of these complex structure indicators
    return not (
        obj.get("properties") or obj.get("allOf") or obj.get("anyOf")
        or obj.get("oneOf") or obj.get("type") == "array" or obj.get("items")
    )


def _is_pure_array(obj: dict[str, Any]) -> bool:
    """Return True when obj is a plain array schema with no inline object structure.

    A pure array looks like:
        {"type": "array", "items": { ... }}

    This is different from an object schema that happens to have array properties.
    We handle pure arrays specially: the array wrapper stays inline (it becomes
    Vec<T> in Rust), but if the items are a complex object we extract the items
    under a stable name so progenitor generates a proper struct for the element type.
    """
    return (
        isinstance(obj, dict) and obj.get("type") == "array"
        # Must not have object structure at the array level itself
        and not obj.get("properties") and not obj.get("allOf")
        and not obj.get("anyOf") and not obj.get("oneOf")
    )


def _is_deprecated(obj: dict[str, Any]) -> bool:
    """Return True when the schema is marked as deprecated.

    We detect deprecation two ways:
      1. The OpenAPI "deprecated: true" flag on the schema object.
      2. The word "deprecated" anywhere in the description string (case-insensitive).
         This catches schemas that were deprecated informally before the flag existed.

    Deprecated schemas are skipped during deduplication — we don't want to
    generate Rust types for API fields that are scheduled for removal.
    """
    if obj.get("deprecated") is True:
        return True
    desc = obj.get("description", "")
    return isinstance(desc, str) and "deprecated" in desc.lower()


def _deduplicate_schemas(properties: dict[str, Any], components: dict[str, Any], parent_name: str = "") -> dict[str, Any]:
    """Register each property schema in components and return a $ref mapping.

    This is the heart of schema deduplication. For every property in a schema's
    "properties" dict, we decide whether to:
      A) Keep it inline (primitives, pure arrays with primitive items)
      B) Extract the items to components and keep the array wrapper inline
      C) Extract the whole thing to components and replace with a $ref

    COLLISION HANDLING when the normalised name already exists in components:
      1. If the incoming schema's properties are a non-empty SUBSET of the existing
         canonical's properties → it's a narrower view of the same resource
         (e.g. a nested "Site" that only includes a few fields). We reuse the
         canonical $ref instead of creating a near-duplicate type.
      2. Otherwise the schemas are genuinely different → generate an alias name
         (context prefix + base, or hash suffix) so both coexist.

    Args:
        properties:  The "properties" dict from a parent schema.
        components:  The shared components/schemas dict (mutated in-place).
        parent_name: The normalised name of the containing schema, used as a
                     namespace prefix when resolving name collisions.

    Returns:
        A new dict mapping original property names to either their original inline
        schema (primitives/arrays) or a {"$ref": "..."} dict (extracted objects).
    """
    refs: dict[str, Any] = {}

    for name, obj in properties.items():
        # Skip deprecated properties entirely — don't include them in the output
        if isinstance(obj, dict) and _is_deprecated(obj):
            continue

        # ── $ref pass-through ─────────────────────────────────────────────────
        # A property value that is already a {"$ref": "..."} must be kept as-is.
        # Without this guard, the code below would try to register the $ref dict
        # itself as a new named component — creating bogus aliases like
        # "LeadScheduleScheduleRate = {$ref: ScheduleRate}", which changes the
        # hash of the containing schema and breaks deduplication of identical
        # schemas (e.g. the various XxxScheduleBlock variants).
        if isinstance(obj, dict) and "$ref" in obj:
            refs[name] = obj
            continue

        # ── Case A: Primitive scalar — keep inline, no component entry needed ──
        if _is_primitive(obj):
            refs[name] = obj
            continue

        # ── Case B: Pure array — keep wrapper inline, but extract complex items ──
        if _is_pure_array(obj):
            items = obj.get("items")
            if (
                isinstance(items, dict) and "$ref" not in items
                and (
                    # Items are a complex object (has properties, or type=object, or combiners)
                    items.get("properties") or items.get("type") == "object"
                    or items.get("allOf") or items.get("anyOf") or items.get("oneOf")
                )
            ):
                # Derive a stable name for the item type.
                # We singularise the property name (e.g. "notes" → "note") and
                # normalise it (e.g. "note" → "Note").
                singular = _normalize_schema_key(_to_single(name) or name)
                # Prefix with parent_name to avoid collisions between same-named item
                # types from different parents (e.g. "Note" in "Job" vs "Note" in "Site").
                item_name = (
                    parent_name + singular
                    if parent_name and not singular.startswith(parent_name)
                    else singular
                )
                if item_name not in components:
                    # First time we see this item type — register it
                    components[item_name] = items
                elif _schema_hash(components[item_name]) != _schema_hash(items):
                    # Name collision with a DIFFERENT schema — generate an alias
                    item_name = _unique_name(item_name, items, components, parent_name)
                    components[item_name] = items
                # Replace inline items with a $ref to the now-registered item type
                obj = {**obj, "items": {"$ref": f"#/components/schemas/{item_name}"}}
            refs[name] = obj
            continue

        # ── Media-type key guard ──────────────────────────────────────────────
        # Property names containing "/" are media-type specifiers like
        # "application/json" used as keys inside "content" maps. These are NOT
        # actual schema property names and must not be extracted as components.
        if "/" in name:
            refs[name] = obj
            continue

        # ── Case C: Complex object — extract to components, replace with $ref ─
        normalized_name = _normalize_schema_key(name)

        # Apply field filter if config.yaml specifies one for this schema name
        if FILTER_RESPONSE_FIELDS and normalized_name in FILTER_RESPONSE_FIELDS:
            obj = _apply_field_filter(obj, FILTER_RESPONSE_FIELDS[normalized_name])

        if normalized_name in components:
            if _schema_hash(components[normalized_name]) != _schema_hash(obj):
                # A DIFFERENT schema is already registered under this name.
                # Check if the incoming one is just a subset view of the canonical.
                canonical_props = set((components[normalized_name].get("properties") or {}).keys())
                obj_props = set((obj.get("properties") or {}).keys())
                if obj_props and obj_props.issubset(canonical_props):
                    # Incoming is a strict subset of the canonical — safe to reuse
                    # the canonical $ref. This avoids generating a near-duplicate
                    # type that's just the canonical with some fields missing.
                    refs[name] = {"$ref": f"#/components/schemas/{normalized_name}"}
                    continue
                # Genuinely different schema — create an alias so both coexist
                alias = _unique_name(normalized_name, obj, components, parent_name)
                if alias not in components:
                    components[alias] = obj
                refs[name] = {"$ref": f"#/components/schemas/{alias}"}
            else:
                # Same schema already registered under this name — just reuse it
                refs[name] = {"$ref": f"#/components/schemas/{normalized_name}"}
        else:
            # Not yet registered — register it and create the $ref
            components[normalized_name] = obj
            refs[name] = {"$ref": f"#/components/schemas/{normalized_name}"}

    return refs


def _dedup_schema(schema: dict[str, Any], schemas: dict[str, Any], parent_name: str = "") -> None:
    """Recursively replace inline property schemas with $refs (depth-first).

    This walks the full tree of a schema object and calls _deduplicate_schemas
    on every "properties" dict it finds, at every level of nesting.

    WHY DEPTH-FIRST? We must process inner nested objects BEFORE the object that
    contains them. If we processed top-down, a parent schema would be registered
    in components while its properties still contain deep inline objects (no $refs).
    Later references to that component would then get the bloated inline version.
    By going depth-first, each component stored in `schemas` already has $refs
    at every level — a clean, fully-normalised representation.

    Args:
        schema:      The schema dict to process (mutated in-place at properties level).
        schemas:     The shared components/schemas dict (mutated in-place).
        parent_name: Passed through to _deduplicate_schemas for collision context.
    """
    # Base case: stop recursing if it's not a dict or it's already a $ref pointer
    if not isinstance(schema, dict) or "$ref" in schema:
        return

    # ── Recurse into array items ──────────────────────────────────────────────
    # If this schema is an array, process its items schema first (depth-first)
    items = schema.get("items")
    if isinstance(items, dict) and "$ref" not in items:
        _dedup_schema(items, schemas, parent_name)

    # ── Recurse into composition keywords ────────────────────────────────────
    # allOf/anyOf/oneOf contain a list of sub-schemas; process each one
    for combiner in ("allOf", "anyOf", "oneOf"):
        for sub in schema.get(combiner) or []:
            if isinstance(sub, dict) and "$ref" not in sub:
                _dedup_schema(sub, schemas, parent_name)

    # ── Process properties (the main payload) ────────────────────────────────
    props = schema.get("properties")
    if isinstance(props, dict):
        for prop_name, prop_schema in props.items():
            if isinstance(prop_schema, dict) and "$ref" not in prop_schema:
                # Determine the sub-parent context for this property.
                # If the property is a complex object (has its own properties or
                # combiners), use the property's own normalised name as context
                # so child schemas get namespaced under it.
                # If the property is a scalar or simple type, inherit parent_name
                # so the parent namespace is used.
                sub_parent = (
                    _normalize_schema_key(prop_name)
                    if (
                        prop_schema.get("properties") or prop_schema.get("allOf")
                        or prop_schema.get("anyOf") or prop_schema.get("oneOf")
                    )
                    else parent_name
                )
                _dedup_schema(prop_schema, schemas, sub_parent)
        # After recursing into all property values, deduplicate the properties dict
        # itself — replace complex inline objects with $refs to components/schemas.
        schema["properties"] = _deduplicate_schemas(props, schemas, parent_name)


def _extract_media_schema(media: dict[str, Any], schema_name: str, schemas: dict[str, Any]) -> None:
    """Register an inline media schema (or its array items) in components/schemas.

    This is called after _dedup_schema has processed the schema's properties.
    It handles the final step: registering the TOP-LEVEL schema object (the one
    that represents the entire request or response body) in components/schemas.

    WHY? After _dedup_schema, inner properties are replaced with $refs, but the
    top-level media schema object itself is still inline in the path operation.
    progenitor derives Rust type names from component keys, so without this step
    the top-level type has no stable name — progenitor would auto-name it
    something like `GetSitesResponse200` which is opaque and unstable.

    Handles two cases:
      - Array response (e.g. GET /sites/ returns [Site, ...]): extract the items
        type under the singular schema_name and keep the array wrapper in place.
      - Object response: extract the whole schema under schema_name.

    In both cases, if the name already exists in components we merge schemas
    (union of all fields, drop required constraints) rather than overwriting.
    """
    schema = media.get("schema")
    # Nothing to do if there's no schema, or it's already a $ref pointer
    if not isinstance(schema, dict) or "$ref" in schema:
        return

    if schema.get("type") == "array":
        # The response body is a JSON array like [{...}, {...}]
        items = schema.get("items")
        if isinstance(items, dict) and "$ref" not in items:
            # The item type name should be the singular of the collection name.
            # e.g. schema_name="Sites" → item_name="Site"
            item_name = _to_single(schema_name)
            # Apply field filter if configured for this item type
            if FILTER_RESPONSE_FIELDS and item_name in FILTER_RESPONSE_FIELDS:
                items = _apply_field_filter(items, FILTER_RESPONSE_FIELDS[item_name])
            if item_name not in schemas:
                schemas[item_name] = items
            elif _schema_hash(schemas[item_name]) != _schema_hash(items):
                # Different definition seen for the same item name — merge them
                schemas[item_name] = _merge_schemas(schemas[item_name], items)
            # Replace inline items with a $ref
            schema["items"] = {"$ref": f"#/components/schemas/{item_name}"}
    elif (
        # The response body is a JSON object
        schema.get("properties") or schema.get("type") == "object"
        or schema.get("allOf") or schema.get("anyOf") or schema.get("oneOf")
    ):
        # Apply field filter if configured for this schema name
        if FILTER_RESPONSE_FIELDS and schema_name in FILTER_RESPONSE_FIELDS:
            schema = _apply_field_filter(schema, FILTER_RESPONSE_FIELDS[schema_name])
            # Update the media object so the filtered schema is written back
            media["schema"] = schema
        if schema_name not in schemas:
            schemas[schema_name] = schema
        elif _schema_hash(schemas[schema_name]) != _schema_hash(schema):
            schemas[schema_name] = _merge_schemas(schemas[schema_name], schema)
        # Replace the inline top-level schema with a $ref
        media["schema"] = {"$ref": f"#/components/schemas/{schema_name}"}


def _process_json_media(
    media: dict[str, Any], example_key: str, examples: dict[str, Any], schemas: dict[str, Any],
) -> None:
    """Normalise an application/json media object in-place.

    Called for every JSON media object found under a request body or response.
    Performs three normalisation steps in order:

      1. LIFT EXAMPLES: If the media object has an inline "example" value, move it
         to components/examples and replace it with a $ref. This reduces duplication
         and makes examples reusable.

      2. DEDUP PROPERTIES: Walk the schema's properties tree depth-first and
         extract all complex inline objects to components/schemas with $refs.

      3. EXTRACT TOP-LEVEL SCHEMA: Register the whole top-level schema (or its
         array item type) in components/schemas.

    Args:
        media:       The application/json media dict (mutated in-place).
        example_key: The base name to use for examples/schemas derived from this media.
                     e.g. "Sites" for a GET /sites/ 200 response.
        examples:    The shared components/examples dict (mutated in-place).
        schemas:     The shared components/schemas dict (mutated in-place).
    """
    # Step 1: lift inline example to components/examples
    if "example" in media:
        example = media.pop("example")  # Remove "example" from the media object
        # Register it under the example_key in components
        examples[example_key] = {"summary": example_key, "value": example}
        # Replace with a $ref to the now-registered example
        media["examples"] = {"default": {"$ref": f"#/components/examples/{example_key}"}}

    # Derive the schema name: example_key with first letter capitalised.
    # e.g. "sites" → "Sites", "siteBody" → "SiteBody"
    schema_name = example_key[0].upper() + example_key[1:]
    # For dedup context: use the singular of the schema name as the parent namespace.
    # e.g. "Sites" → "Site", "SiteNotes" → "SiteNote"
    parent_name = _to_single(schema_name) or schema_name

    # Step 2: recursively deduplicate schema properties (depth-first)
    if isinstance(media.get("schema"), dict):
        _dedup_schema(media["schema"], schemas, parent_name)

    # Step 3: extract the top-level schema (or array items) to components
    _extract_media_schema(media, schema_name, schemas)


# ── Main processing passes ────────────────────────────────────────────────────


def process_paths(
    paths: dict[str, Any],
    components_parameters: dict[str, Any],
    components_schemas: dict[str, Any],
    components_examples: dict[str, Any],
) -> None:
    """Normalise every path and operation in paths in-place.

    This is Pass 1 — the most substantial transformation. For each path + operation
    in the spec:

      PATH LEVEL:
        - Pop inline path-level parameters, register them in components, and
          replace with $refs (deduplication across all endpoints).
        - Synthesise $refs for any {placeholder} in the URL that isn't already
          covered by a parameter declaration.

      OPERATION LEVEL (for each HTTP method):
        - Assign a unique operationId derived from method + URL resource name.
          Collisions (two paths mapping to the same base id) are resolved by
          appending an incrementing numeric suffix (e.g. getSites2).
        - Register and ref method-level parameters.
        - Lift inline examples to components/examples.
        - Extract inline schemas to components/schemas.
        - Re-order the serialised keys so operationId appears first in YAML output
          (purely cosmetic — makes the output easier to read).

    Args:
        paths:                 The spec's "paths" dict (mutated in-place).
        components_parameters: The spec's components/parameters dict (mutated in-place).
        components_schemas:    The spec's components/schemas dict (mutated in-place).
        components_examples:   The spec's components/examples dict (mutated in-place).
    """
    # Track all operationIds assigned so far in this pass so we can detect collisions
    operation_ids: set[str] = set()

    for path, path_obj in paths.items():
        # Derive the UpperCamelCase resource name for this URL (e.g. "Sites", "JobNotes")
        resource_name = _build_resource_name(path)

        # ── Path-level parameters ─────────────────────────────────────────────
        # Pop the "parameters" key from the path object (we'll replace it below).
        # "or []" handles the case where it's missing or None.
        raw: list[dict] = path_obj.pop("parameters", None) or []
        # Register inline definitions → replace with $refs, path params first
        deduped = _split_and_ref_params(raw, components_parameters)
        # Add $refs for any {placeholder} in the URL not already in the list
        deduped = _ensure_path_params_present(deduped, path, components_parameters)
        if deduped:
            path_obj["parameters"] = deduped

        # ── Operation-level processing ────────────────────────────────────────
        for method in list(path_obj.keys()):
            op = path_obj[method]
            # Skip non-HTTP-method keys (e.g. "parameters", "summary", "description")
            if method not in HTTP_METHODS or not isinstance(op, dict):
                continue

            # ── Assign operationId ────────────────────────────────────────────
            # Build the base id from method + resource name: "get" + "Sites" → "getSites"
            base_id = _build_operation_id(method, resource_name)
            operation_id, i = base_id, 2
            while operation_id in operation_ids:
                # This id is already taken by another endpoint.
                # Append an incrementing suffix: "getSites2", "getSites3", ...
                operation_id = f"{base_id}{i}"
                i += 1
            operation_ids.add(operation_id)

            # Build a NEW dict for this operation with operationId first.
            # Python dicts preserve insertion order (since 3.7), so putting
            # operationId first means it serialises first in the YAML output,
            # making the file much easier to read and diff.
            new_op: dict[str, Any] = {"operationId": operation_id}

            # ── Method-level parameters ───────────────────────────────────────
            # Pop parameters from the original op (we add the processed version to new_op)
            raw_method: list[dict] = op.pop("parameters", [])
            if raw_method:
                new_op["parameters"] = _split_and_ref_params(raw_method, components_parameters)

            # ── Request body ──────────────────────────────────────────────────
            # Request bodies are only present on POST/PUT/PATCH operations.
            # We navigate down to the application/json media object if it exists.
            rb_media = op.get("requestBody", {}).get("content", {}).get("application/json", {})
            if rb_media:
                # Name the body schema as "<ResourceName>Body" e.g. "SiteBody"
                _process_json_media(
                    rb_media, f"{resource_name}Body",
                    components_examples, components_schemas,
                )

            # ── Responses ─────────────────────────────────────────────────────
            for code, response in op.get("responses", {}).items():
                # Navigate to the application/json media object for this status code
                media = response.get("content", {}).get("application/json", {})
                # For success responses (200/201) use the resource name as the schema name.
                # For other codes (400, 404, 500 ...) use a more specific name that
                # includes the operationId so it doesn't collide with the success schema.
                schema_name = (
                    resource_name if code in ["200", "201"]
                    else f"{operation_id}Response{code}"
                )
                _process_json_media(
                    media, schema_name, components_examples, components_schemas,
                )

            # ── Rebuild op dict with operationId first ────────────────────────
            # Copy all remaining keys from the original op into new_op.
            # Skip "operationId" because the original op might have it as None
            # (missing in the raw spec) and we don't want to overwrite our value.
            for k, v in op.items():
                if k != "operationId":
                    new_op[k] = v
            # Replace the operation in the path object with our cleaned version
            path_obj[method] = new_op


def enrich_list_schemas(paths: dict[str, Any], components_schemas: dict[str, Any]) -> int:
    """Replace each collection GET response schema with {type: array, items: <single>}.

    PROBLEM: The raw simPRO spec often provides a vague or missing response schema
    for list endpoints (e.g. GET /sites/ might have schema: {} or no schema at all).
    Code generators then produce useless types like `Vec<serde_json::Value>`.

    SOLUTION: For each collection endpoint, find its single-item sibling and use
    THAT endpoint's response schema as the array item type. For example:
        GET /sites/{siteID} → 200 → schema: {"$ref": "#/components/schemas/Site"}
        GET /sites/         → 200 → schema becomes: {type: array, items: <same ref>}

    This gives consumers a precise, typed list element — `Vec<Site>` in Rust.

    Returns the number of endpoints whose schemas were enriched.
    """
    enriched = 0

    for path, path_obj in paths.items():
        # Only process collection paths (those not ending with a path parameter)
        if not _is_collection(path):
            continue

        # Only process paths that have a GET operation
        get_op = path_obj.get("get")
        if not isinstance(get_op, dict):
            continue

        # Find the single-item sibling path (e.g. /sites/ → /sites/{siteID})
        single_path = _find_single_item_path(path, paths)
        if not single_path:
            continue  # No sibling found — can't infer the item type

        single_get = paths[single_path].get("get")
        if not isinstance(single_get, dict):
            continue  # Sibling doesn't have a GET operation

        # Extract the 200 response schema from the single-item GET endpoint
        single_schema = (
            single_get.get("responses", {})
            .get("200", {}).get("content", {})
            .get("application/json", {}).get("schema")
        )
        if not single_schema:
            continue  # Single-item endpoint has no response schema — can't infer

        # Navigate to the list endpoint's 200 response media object
        list_media = (
            get_op.get("responses", {})
            .get("200", {}).get("content", {})
            .get("application/json", {})
        )
        if not isinstance(list_media, dict):
            continue

        # Build the items schema (what each element in the list looks like)
        if "$ref" in single_schema:
            # Single-item schema is already a $ref — use it directly as items
            items_schema = single_schema
        else:
            # Single-item schema is inline — register it in components and use a $ref
            item_name = _build_resource_name(single_path)
            if item_name and item_name not in components_schemas:
                components_schemas[item_name] = single_schema
            items_schema = (
                {"$ref": f"#/components/schemas/{item_name}"} if item_name else single_schema
            )

        # Replace the list endpoint's response schema with a typed array
        list_media["schema"] = {"type": "array", "items": items_schema}
        enriched += 1

    return enriched


def validate(paths: dict[str, Any], components_parameters: dict[str, Any]) -> int:
    """Check for broken $refs and undeclared path parameters. Returns error count.

    After process_paths() runs, every parameter in every operation should be a
    $ref pointing to a registered component. This pass verifies that:

      1. BROKEN $REFS: Every "$ref" in a parameters list actually resolves to an
         entry in components_parameters. A broken ref would cause code generators
         to fail with a cryptic error.

      2. MISSING PATH PARAMS: Every {placeholder} in a URL template has a
         corresponding parameter declared somewhere in the operation (either at
         the path level or the operation level).

    These checks help catch bugs introduced by _ensure_path_params_present or
    edge cases in the raw spec that weren't handled.
    """
    errors = 0

    for path, path_obj in paths.items():
        for method, op in path_obj.items():
            if method not in HTTP_METHODS or not isinstance(op, dict):
                continue

            # Collect all parameters for this operation: path-level + method-level.
            # Path-level parameters apply to ALL methods on this path; method-level
            # parameters are specific to this HTTP verb.
            combined = list(path_obj.get("parameters", [])) + list(op.get("parameters", []))

            declared: set[str] = set()  # Names of parameters we've confirmed exist
            for param in combined:
                if "$ref" in param:
                    # Resolve the $ref to check if the target component exists
                    ref_key = param["$ref"].split("/")[-1]
                    if ref_key not in components_parameters:
                        # The $ref points to something that doesn't exist!
                        print(f"  BROKEN REF   {method.upper():6s} {path}  →  {param['$ref']}")
                        errors += 1
                        continue
                    # $ref is valid — record the parameter's actual name
                    declared.add(components_parameters[ref_key]["name"])
                elif "name" in param:
                    # Inline parameter (should have been processed, but be defensive)
                    declared.add(param["name"])

            # Check that every {placeholder} in the URL has been declared
            missing = set(_url_parameters(path)) - declared
            if missing:
                print(f"  MISSING PARAM {method.upper():6s} {path}  →  {missing}")
                errors += 1

    return errors


# ── Component pruning ─────────────────────────────────────────────────────────
# After processing, some schemas/parameters/examples may be orphaned — they were
# registered during processing but nothing in the final spec actually references
# them via a $ref. These unused components increase the spec file size and cause
# code generators to emit unused Rust types. We prune them here.


def _collect_refs(obj: Any, component_type: str) -> set[str]:
    """Recursively collect all $ref names of the given component type from obj.

    Walks any nested dict/list structure and returns the set of component names
    referenced by $refs of the specified type.

    For example, with component_type="schemas", a "$ref" like
        "#/components/schemas/Site"
    contributes "Site" to the returned set.

    Args:
        obj:            Any Python value (dict, list, str, etc.) — recursion handles all.
        component_type: One of "schemas", "parameters", "examples".
    """
    # Build the prefix we're looking for in "$ref" values
    prefix = f"#/components/{component_type}/"

    if isinstance(obj, dict):
        refs: set[str] = set()
        for k, v in obj.items():
            if k == "$ref" and isinstance(v, str) and v.startswith(prefix):
                # This $ref points to the component type we're collecting
                # Slice off the prefix to get just the component name
                refs.add(v[len(prefix):])
            else:
                # Recurse into non-$ref values
                refs |= _collect_refs(v, component_type)
        return refs

    if isinstance(obj, list):
        # Recurse into each list element and union all results
        return {r for item in obj for r in _collect_refs(item, component_type)}

    # Scalar value (str, int, bool, None) — no $refs here
    return set()


def prune_unused_schemas(openapi: dict[str, Any]) -> int:
    """Remove schemas not reachable from any path operation via $ref traversal.

    ALGORITHM (Breadth-First Search through the schema dependency graph):
      1. Start: collect all schema names directly referenced from paths (roots).
      2. Also collect schemas referenced from other components (parameters, examples)
         since those may transitively reference schemas.
      3. BFS expansion: for each reachable schema, add schemas IT references to
         the queue. Repeat until no new schemas are found.
      4. Any schema not in the reachable set is pruned.

    WHY BFS? Some schemas are composed of other schemas via $refs. A schema
    "JobNote" might be referenced from paths, and "JobNote" might internally
    reference "Author". We need to transitively follow all $refs so we don't
    accidentally prune schemas that are only referenced indirectly.

    Handles circular references: the `reachable` set prevents revisiting, so
    circular $ref chains (A → B → A) don't cause infinite loops.

    Returns the number of schemas removed.
    """
    schemas: dict[str, Any] = openapi.get("components", {}).get("schemas", {})

    # Seed the BFS with schemas referenced directly from path operations
    roots: set[str] = _collect_refs(openapi.get("paths", {}), "schemas")

    # Also include schemas referenced from other components (parameters, examples)
    # because those components might inline or reference schema types
    for key, val in openapi.get("components", {}).items():
        if key != "schemas":  # Don't recurse into the schemas dict itself at this stage
            roots |= _collect_refs(val, "schemas")

    # BFS: start from roots, expand by following schema-level $refs
    reachable: set[str] = set()
    queue = list(roots)
    while queue:
        name = queue.pop()
        if name in reachable:
            continue  # Already processed — avoid infinite loops on circular refs
        reachable.add(name)
        if name in schemas:
            # Add any schemas that THIS schema references (minus already-visited ones)
            queue.extend(_collect_refs(schemas[name], "schemas") - reachable)

    # Any schema not reached by the BFS is unused — delete it
    unused = [name for name in list(schemas.keys()) if name not in reachable]
    for name in unused:
        del schemas[name]
    return len(unused)


def prune_unused_parameters(openapi: dict[str, Any]) -> int:
    """Remove components/parameters not referenced from any path. Returns count removed.

    A parameter component that no path operation references via $ref is orphaned.
    This can happen when a path is removed by trim_spec() but its parameters remain.
    """
    parameters = openapi.get("components", {}).get("parameters", {})
    if not parameters:
        return 0
    # Collect all parameter names referenced from path operations
    used = _collect_refs(openapi.get("paths", {}), "parameters")
    # Delete any parameter not in the used set
    unused = [name for name in list(parameters.keys()) if name not in used]
    for name in unused:
        del parameters[name]
    return len(unused)


def prune_unused_examples(openapi: dict[str, Any]) -> int:
    """Remove components/examples not referenced from paths or other components. Returns count removed.

    Similar to prune_unused_parameters, but examples can also be referenced from
    within other components (e.g. a schema might reference an example), so we
    search both paths AND all non-examples components.
    """
    examples: dict[str, Any] = openapi.get("components", {}).get("examples", {})
    if not examples:
        return 0
    components = openapi.get("components", {})
    # Collect examples referenced from path operations
    used: set[str] = _collect_refs(openapi.get("paths", {}), "examples")
    # Also collect examples referenced from within other components
    for key, val in components.items():
        if key != "examples":
            used |= _collect_refs(val, "examples")
    # Delete any example not in the used set
    unused = [name for name in list(examples.keys()) if name not in used]
    for name in unused:
        del examples[name]
    return len(unused)


# ── Schema identity deduplication ────────────────────────────────────────────


# Regex that matches the 6-character hash suffix appended by _unique_name when it
# can't find a better alias: one uppercase hex digit followed by five lowercase hex
# digits at the end of the string.  e.g. "ScheduleBlockD5ad0d" → suffix "D5ad0d".
_HASH_SUFFIX_RE = re.compile(r"[0-9A-F][0-9a-f]{5}$")


def deduplicate_identical_schemas(openapi: dict[str, Any]) -> int:
    """Iteratively merge schemas that have identical content into a single canonical entry.

    WHY THIS PASS EXISTS
    ────────────────────
    The processor registers a new schema name for every (parent_context, property)
    combination it encounters. When multiple parents have a property with the same
    shape — like XxxScheduleBlock or XxxReference variants — each gets its own name
    even though a single schema would suffice. This pass collapses those duplicates
    back to one canonical name.

    WHAT COUNTS AS A COLLAPSIBLE FAMILY?
    ─────────────────────────────────────
    Two or more schemas are collapsed only when they all share the same TERMINAL
    CamelCase WORD (the last capitalised word in their name, after stripping any
    hash suffix). Examples:

      • "LeadScheduleBlock", "ActivityScheduleBlock", "ScheduleBlockD5ad0d"
        → terminal word "Block" for all → collapse to "ScheduleBlock" ✓
      • "AssetTypeReference", "AssetTypeBodyReference", "AssetTypesBodyReference"
        → terminal word "Reference" for all → collapse to "AssetTypeReference" ✓
      • "Uom", "ScheduleRate", "Staff", "Activity"  (all {id, name} schemas)
        → terminal words "Uom", "Rate", "Staff", "Activity" — all different
        → do NOT collapse — semantically distinct concepts, preserved separately ✓

    CANONICAL NAME ELECTION
    ────────────────────────
    Within a collapsible family, the canonical is the schema whose INTENDED name
    (hash suffix stripped) is shortest. This makes "ScheduleBlockD5ad0d" donate its
    content to "ScheduleBlock" (13 chars) rather than losing out to the longer but
    hash-free "ActivityScheduleBlock" (21 chars).

    If the intended clean name is already occupied by a schema outside the group
    (genuinely different content), we fall back to the shortest non-hash name within
    the group.

    WHY ITERATIVE?
    ──────────────
    A single pass can miss duplicates that only become visible AFTER an earlier merge.
    After collapsing sub-schemas, their parent schemas may become identical too —
    but only a subsequent pass can detect that. We loop until convergence.

    Returns the total number of schema entries removed (or renamed) across all passes.
    """
    schemas: dict[str, Any] = openapi.get("components", {}).get("schemas", {})
    if not schemas:
        return 0

    def _rewrite_refs(obj: Any, remap: dict[str, str]) -> None:
        """Walk the entire spec tree in-place, redirecting non-canonical schema $refs."""
        if isinstance(obj, dict):
            ref = obj.get("$ref")
            if isinstance(ref, str) and ref.startswith("#/components/schemas/"):
                key = ref[len("#/components/schemas/"):]
                if key in remap:
                    obj["$ref"] = f"#/components/schemas/{remap[key]}"
            for v in obj.values():
                _rewrite_refs(v, remap)
        elif isinstance(obj, list):
            for item in obj:
                _rewrite_refs(item, remap)

    def _terminal_word(name: str) -> str:
        """Last PascalCase word after stripping any hash suffix, normalised to singular.

        Singularising means "WorkOrders" and "WorkOrder" compare equal, so
        "JobSectionCostCenterWorkOrder" and "JobSectionCostCenterWorkOrders"
        are recognised as the same family and collapsed.

        "LeadScheduleBlock"               → "Block"
        "ScheduleBlockD5ad0d"             → "Block"   (D5ad0d stripped first)
        "AssetTypeBodyReference"          → "Reference"
        "JobSectionCostCenterWorkOrders"  → "Order"   (Orders → Order)
        "Uom"                             → "Uom"
        """
        base = _HASH_SUFFIX_RE.sub("", name)
        words = re.findall(r"[A-Z][a-z0-9]*", base)
        word = words[-1] if words else base
        return _to_single(word) or word  # singular form, fall back to original

    def _intended(name: str) -> str:
        """The name we would ideally use — hash suffix stripped."""
        return _HASH_SUFFIX_RE.sub("", name)

    total_merged = 0
    iteration = 0

    while True:
        iteration += 1
        print(f"\n  [dedup] ── Iteration {iteration} ({len(schemas)} schemas) ──────────────")

        # ── Group schemas by content hash ─────────────────────────────────────
        hash_to_names: dict[str, list[str]] = {}
        for name, schema in schemas.items():
            hash_to_names.setdefault(_schema_hash(schema), []).append(name)

        # Log all duplicate groups (regardless of whether they'll be collapsed)
        dup_groups = {h: ns for h, ns in hash_to_names.items() if len(ns) > 1}
        print(f"  [dedup]   {len(dup_groups)} group(s) with duplicate content:")
        for h, ns in sorted(dup_groups.items(), key=lambda kv: sorted(kv[1])):
            twords = {_terminal_word(n) for n in ns}
            print(f"  [dedup]     hash={h[:8]}  terminal_words={sorted(twords)}  names={sorted(ns)}")

        remap: dict[str, str] = {}

        for names_list in hash_to_names.values():
            terminal_words = {_terminal_word(n) for n in names_list}
            if len(terminal_words) > 1:
                # Different terminal words — semantically distinct, skip
                print(f"  [dedup]     SKIP (mixed terminal words {sorted(terminal_words)}): {sorted(names_list)}")
                continue

            def _canon_key(n: str) -> tuple:
                i = _intended(n)
                return (len(i), bool(_HASH_SUFFIX_RE.search(n)), i)

            canonical_name = min(names_list, key=_canon_key)
            effective = _intended(canonical_name)

            if effective in schemas and effective not in names_list:
                clean = _intended(canonical_name)
                existing_props = set((schemas[clean].get("properties") or {}).keys())
                group_props    = set((schemas[names_list[0]].get("properties") or {}).keys())
                if group_props and (group_props == existing_props or group_props.issubset(existing_props)):
                    # Same or compatible property structure — the existing schema under
                    # the clean name is an acceptable canonical. The only difference
                    # is in the VALUES of some properties (e.g. $ref targets that
                    # point to structurally identical but differently-named schemas).
                    # Remap all group members to the existing clean name as-is.
                    print(f"  [dedup]     LENIENT merge: group props ⊆ '{clean}' props → remap group to '{clean}'")
                else:
                    # Genuinely different property structure — fall back to shortest
                    # non-hash name within the group to at least avoid a hash suffix.
                    non_hash = [n for n in names_list if not _HASH_SUFFIX_RE.search(n)]
                    effective = min(non_hash, key=lambda n: (len(n), n)) if non_hash else canonical_name
                    print(f"  [dedup]     CONFLICT: '{clean}' props differ → fallback='{effective}'")

            for name in names_list:
                if name != effective:
                    remap[name] = effective


        # Build a set of schema names that appear as property names
        referenced_as_property: set[str] = set()
        for schema in schemas.values():
            for prop in (schema.get("properties") or {}):
                referenced_as_property.add(prop)

        # ── Secondary pass: merge by terminal word + identical property names ───
        # Catches schemas that represent the same concept but have different hashes
        # because their $ref targets were renamed differently by an earlier pass.
        # Example: "LeadScheduleBlock" ($ref:ScheduleRate) and "ScheduleBlock"
        # ($ref:Uom) have the same 6 property keys and terminal word "Block" — they
        # should be one schema even though their hashes differ.
        #
        # Guard: only merge when the property KEY SETS are identical (not just
        # a subset). Identical keys = structural twins that only diverge in $ref
        # targets — safe to merge via _merge_schemas (union, existing wins).
        word_props_to_names: dict[tuple, list[str]] = {}
        for name, schema in schemas.items():
            word  = _terminal_word(name)
            props = frozenset((schema.get("properties") or {}).keys())
            if props:  # skip empty/scalar schemas
                word_props_to_names.setdefault((word, props), []).append(name)

        for (_word, _), word_names in word_props_to_names.items():
            if len(word_names) <= 1:
                continue
            canonical = min(word_names, key=lambda n: (bool(_HASH_SUFFIX_RE.search(n)), len(n), n))
            merged_schema = schemas[canonical]
            for name in word_names:
                if name != canonical:
                    merged_schema = _merge_schemas(merged_schema, schemas[name])
                    remap[name] = canonical
                    print(f"  [dedup]     PROP-MERGE: '{name}' → '{canonical}' (terminal='{_word}')")
            schemas[canonical] = merged_schema

        if not remap:
            print(f"  [dedup]   No remaps — converged after {iteration} iteration(s).")
            break

        print(f"  [dedup]   Applying {len(remap)} remap(s):")
        for old, new in sorted(remap.items()):
            print(f"  [dedup]     {old}  →  {new}")

        for old, new in remap.items():
            if new not in schemas and old in schemas:
                schemas[new] = schemas[old]

        _rewrite_refs(openapi, remap)

        for old in remap:
            schemas.pop(old, None)

        total_merged += len(remap)

    return total_merged


# ── Endpoint filter ───────────────────────────────────────────────────────────


def trim_spec(openapi: dict[str, Any]) -> "dict[str, Any] | None":
    """Return a deep copy of openapi filtered to config.yaml filter.paths, or None.

    If config.yaml specifies a "filter.paths" allowlist, this pass creates a
    new spec that contains ONLY the paths and HTTP methods listed in the allowlist.
    All other paths are dropped.

    This is useful when you only need a subset of the API in your application —
    you can include only the endpoints you actually call, keeping the generated
    Rust code small and compile times fast.

    Returns None when no filter is configured (the full spec is kept as-is).
    The caller is responsible for running prune_*() after this to remove any
    schemas/parameters/examples that are now orphaned because their only
    referencing paths were trimmed away.

    Example config.yaml:
        filter:
          paths:
            /api/v1.0/companies/0/sites/:     [get]
            /api/v1.0/companies/0/sites/{id}: [get, patch]

    In this example, only GET /sites/ and GET+PATCH /sites/{id} are kept.
    All other paths and methods are dropped.
    """
    if FILTER_PATHS is None:
        # No filter configured — keep everything
        print("  No paths filter in config.yaml — all endpoints retained.")
        return None

    # Count total operations in the unfiltered spec for the summary message
    total = sum(
        1 for path_obj in openapi["paths"].values()
        if isinstance(path_obj, dict)
        for m in path_obj if m in HTTP_METHODS
    )

    # Deep copy so we don't mutate the original spec — the caller may still use it
    trimmed = copy.deepcopy(openapi)
    new_paths: dict[str, dict[str, Any]] = {}

    for path, path_obj in trimmed["paths"].items():
        # Look up the allowed methods for this path in the filter config
        allowed_methods = FILTER_PATHS.get(path)
        if allowed_methods is None:
            # This path is not in the allowlist — drop it entirely
            continue

        new_path_obj: dict[str, Any] = {}
        for key, value in path_obj.items():
            if key in HTTP_METHODS:
                # This is an HTTP method entry — only keep it if it's in the allowlist
                if key in allowed_methods:
                    new_path_obj[key] = value
                # else: method not allowed — drop it silently
            else:
                # Non-method key (e.g. "parameters", "summary") — always keep
                new_path_obj[key] = value

        # Only include this path in the output if it has at least one allowed method
        if any(m in new_path_obj for m in HTTP_METHODS):
            new_paths[path] = new_path_obj

    trimmed["paths"] = new_paths

    # Count how many operations survived the filter
    kept = sum(1 for path_obj in trimmed["paths"].values() for m in path_obj if m in HTTP_METHODS)
    print(f"  config.yaml filter: {kept} operation(s) retained from {total}.")
    return trimmed
