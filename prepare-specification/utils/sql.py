"""
PostgreSQL DDL generator from a processed OpenAPI spec, plus interactive
junction table setup.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BACKGROUND: WHAT IS DDL AND WHY ARE WE GENERATING IT?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DDL stands for Data Definition Language — the subset of SQL that creates the
structure of a database. The main statement we emit is CREATE TABLE, e.g.:

    CREATE TABLE sites (
        id       BIGINT NOT NULL,
        name     TEXT,
        company_id BIGINT REFERENCES companies (id),
        PRIMARY KEY (id)
    );

We derive these table definitions automatically from the OpenAPI spec rather
than writing them by hand. The spec already describes the shape of every API
response object; we convert those shapes into relational tables.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
KEY CONCEPTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

RESOURCE SCHEMA: An OpenAPI schema object that represents an API resource —
    a "thing" with its own identity. We identify resources by the presence of
    an "ID" or "id" property. Each resource becomes a database table.

FOREIGN KEY (FK): A column whose value must match the primary key of another
    table's row, enforcing referential integrity. For example, a "note" row
    might have a "site_id" column that references the "sites" table.

JUNCTION TABLE: A table used to model a many-to-many relationship. For example,
    if a job can have many staff members AND a staff member can belong to many
    jobs, we create a job_staff table with columns (job_id, staff_id).

TOPOLOGICAL SORT: An ordering of tables such that if table A references table B
    via a foreign key, then B appears before A in the output. This ensures that
    when PostgreSQL executes the CREATE TABLE statements in order, the referenced
    table always exists before the referencing table tries to use it.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ALGORITHM OVERVIEW (four passes)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Pass 1 — (_build_tables):
    Walk all schemas in components/schemas. Any schema that has an ID/id
    property is a "resource" and gets its own table. The table name is derived
    from the schema name: UpperCamelCase → plural snake_case
    (e.g. "WorkOrder" → "work_orders").

  Pass 2 — (_populate_columns):
    For each resource table, walk the schema's properties and decide what column
    each property becomes:
      - $ref to a resource   → BIGINT FK column
      - $ref to a non-resource with sub-properties → inline its scalars
      - array of resources   → junction table
      - array of non-resources → JSONB column
      - object with a name matching a table → BIGINT FK column
      - object with properties → inline its scalars
      - string ending in ID/Id → BIGINT FK candidate
      - scalar (string, int, bool, ...) → appropriate PG type

  Pass 3 — (_detect_junction_tables, _apply_declarative_junctions):
    Auto-detect junction tables: a table with ≥2 FK columns, no non-FK columns,
    and no own PK is treated as a junction table (compound PK from its FK columns).
    Declarative junction tables from config.yaml are also applied here.

  Pass 4 — (_topo_sort, _render_create_table):
    Sort tables topologically so FK targets are defined first.
    Render each table as a CREATE TABLE block. FK constraints that would
    reference a table not yet emitted (cycles) become ALTER TABLE statements
    appended at the end of the file.

Junction tables are either auto-detected (pass 3) or declared in config.yaml
under junction_tables.  setup_junction_yaml() prompts the user interactively
and writes the result back to config.yaml before generate_sql() is called.
"""

from __future__ import annotations  # Allow "str | None" type hints in Python 3.8

import contextlib   # For nullcontext() — a no-op context manager when rich is absent
import io           # For StringIO — an in-memory file object used to capture YAML output
import re           # For regular expressions — used in name normalisation
import sys          # For sys.stdin.isatty() — detect interactive vs CI environment
import types        # For types.ModuleType — used in the _ask_confirm signature
from collections import deque              # For the BFS queue in topological sort
from collections.abc import Callable      # For type-annotating callback functions
from concurrent.futures import ThreadPoolExecutor  # For parallel DDL rendering
from functools import lru_cache           # Memoisation — cache results of expensive pure functions
from typing import Any                    # For "Any" type annotation

import inflect  # English pluralisation / singularisation rules

from .config import EXCLUDE_COLUMNS, CONFIG_FILE, FORCE_TABLES, TABLE_NAMES

# inflect.engine() gives us an object that knows English grammar:
#   _inflect.plural("site")        → "sites"
#   _inflect.singular_noun("sites") → "site"
#   _inflect.singular_noun("site")  → False  (already singular)
_inflect = inflect.engine()


def _singular_noun(word: str) -> str | None:
    """Return the singular form of word, or None if word is already singular.

    inflect.singular_noun() returns False (not a string) when the word is
    already singular. We normalise False → None so every call site gets either
    a string or None — no boolean weirdness to handle.
    """
    result = _inflect.singular_noun(word)  # type: ignore[arg-type]
    return result if isinstance(result, str) else None


def _plural(word: str) -> str:
    """Return the plural form of word, falling back to appending 's' if inflect fails."""
    return _inflect.plural(word) or word + 's'  # type: ignore[arg-type]


# Words that are "uncountable" in English — their plural is the same as their
# singular. inflect sometimes gets these wrong (e.g. "staffs" is not a word),
# so we handle them manually.
_UNCOUNTABLE = frozenset({
    'staff', 'equipment', 'information', 'metadata', 'media',
    'news', 'series', 'species', 'aircraft', 'footage',
})

# PostgreSQL reserved keywords that cannot be used as unquoted column or table
# names. If a property maps to one of these, we prefix it with "_" to make it
# a safe identifier (e.g. a column named "end" becomes "_end").
_PG_RESERVED = frozenset({
    'all', 'analyse', 'analyze', 'and', 'any', 'array', 'as', 'asc',
    'asymmetric', 'both', 'case', 'cast', 'check', 'collate', 'column',
    'constraint', 'create', 'current_catalog', 'current_date', 'current_role',
    'current_schema', 'current_time', 'current_timestamp', 'current_user',
    'default', 'deferrable', 'desc', 'distinct', 'do', 'else', 'end',
    'except', 'false', 'fetch', 'for', 'foreign', 'from', 'grant', 'group',
    'having', 'in', 'initially', 'intersect', 'into', 'lateral', 'leading',
    'limit', 'localtime', 'localtimestamp', 'not', 'null', 'offset', 'on',
    'only', 'or', 'order', 'placing', 'primary', 'references', 'returning',
    'select', 'session_user', 'some', 'symmetric', 'table', 'then', 'to',
    'trailing', 'true', 'union', 'unique', 'user', 'using', 'variadic',
    'when', 'where', 'window', 'with',
    # Additional names that are not strict keywords but cause problems in practice:
    'date', 'time', 'timestamp', 'interval', 'type', 'format',
    'value', 'key', 'index', 'schema', 'data', 'start', 'end',
})


# ── Name helpers ──────────────────────────────────────────────────────────────

# Regex to detect HTTP-method prefixes added by process_paths (e.g. "GetSites").
# We strip these when deriving table names — the HTTP method is an implementation
# detail, not part of the resource concept.
_OP_PREFIX_RE = re.compile(r'^(Get|Post|Put|Patch|Delete)(?=[A-Z])')

# Regex to detect response-wrapper suffixes added during spec processing.
# "SitesList", "SiteItem", "SiteBody", "SiteResponse200" are all wrappers
# around the underlying "Site" concept. We strip them to get the base name.
_OP_SUFFIX_RE = re.compile(r'(List|Request|Response\d*(?:Item)?|Item|Body)$')


@lru_cache(maxsize=None)
def _strip_op_name(name: str) -> str:
    """Remove HTTP-method prefixes and response-wrapper suffixes from a schema name.

    @lru_cache means this function's results are memoised — the same input always
    produces the same output, so we cache it to avoid recomputing.

    Examples:
        "GetSites"         → "Sites"       (prefix stripped)
        "SitesList"        → "Sites"       (suffix stripped)
        "GetSiteResponse"  → "Site"        (both stripped)
        "WorkOrder"        → "WorkOrder"   (nothing to strip)
    """
    name = _OP_PREFIX_RE.sub('', name)   # Remove prefix like "Get", "Post"
    name = _OP_SUFFIX_RE.sub('', name)   # Remove suffix like "List", "Response200"
    return name


@lru_cache(maxsize=None)
def _to_snake(name: str) -> str:
    """Convert UpperCamelCase or mixedCase to snake_case.

    Examples:
        "WorkOrder"  → "work_order"
        "SiteID"     → "site_i_d"   (note: call _col_name for ID normalisation)
        "companyId"  → "company_id"

    Two passes of regex are needed:
      Pass 1: "ABCDef" → "ABC_Def"  (handles runs of capitals before a cap+lower)
      Pass 2: "siteDef" → "site_Def" → "site_def"  (handles lower-to-upper transitions)
    """
    # Insert underscore between a run of capitals and a following Cap+lower
    # e.g. "XMLParser" → "XML_Parser"
    name = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1_\2', name)
    # Insert underscore between a lower/digit and a following capital
    # e.g. "siteId" → "site_Id"
    name = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', name)
    return name.lower()


@lru_cache(maxsize=None)
def _col_name(prop: str) -> str:
    """Convert a property name to a safe PostgreSQL column name.

    Steps:
      1. Normalise trailing "ID" → "Id" before snake-casing.
         Without this, "SiteID" → "site_i_d" (ugly). With it: "SiteId" → "site_id".
      2. Apply snake_case conversion.
      3. Prefix with "_" if the result is a PostgreSQL reserved keyword.

    Examples:
        "SiteID"   → "site_id"
        "Name"     → "name"
        "default"  → "_default"  (reserved keyword)
        "EndDate"  → "end_date"  ("end_date" is not reserved, only "end" alone is.
    """
    # Normalise "ID" suffix → "Id" for snake_case output
    prop = re.sub(r'ID$', 'Id', prop)
    name = _to_snake(prop)
    # Prefix with "_" if the result is a reserved keyword
    return f'_{name}' if name in _PG_RESERVED else name


def _trim_overlap(parent_singular: str, col_nm: str) -> str:
    """Remove leading overlap between the tail of parent_singular and col_nm.

    PROBLEM: When a "work_order" table has a property "work_order_assets", the
    naive junction table name would be "work_order_work_order_assets" — the parent
    name is repeated. We detect this overlap and trim the redundant prefix.

    ALGORITHM: Try progressively longer suffixes of parent_singular. If col_nm
    starts with that suffix followed by "_", strip it.

    Examples:
        parent_singular="work_order", col_nm="work_order_assets" → "assets"
        parent_singular="site",       col_nm="site_notes"         → "notes"
        parent_singular="job",        col_nm="tasks"              → "tasks" (no overlap)
    """
    parts = parent_singular.split('_')  # e.g. ["work", "order"]
    for length in range(len(parts), 0, -1):
        # Build the candidate overlap: try longest suffix first
        suffix = '_'.join(parts[-length:])  # e.g. "work_order", then "order"
        if col_nm == suffix:
            # col_nm IS the suffix (exact match) — can't trim further
            return col_nm
        if col_nm.startswith(suffix + '_'):
            # col_nm starts with the suffix + underscore — strip it
            trimmed = col_nm[len(suffix) + 1:]
            return trimmed if trimmed else col_nm  # Guard against empty result
    return col_nm  # No overlap found


@lru_cache(maxsize=None)
def _canonical_plural(word: str) -> str:
    """Return the canonical plural of word, handling irregular English forms.

    WHY RE-PLURALISE? Input like "statuses" might already be plural, but inflect's
    plural() would turn "statuses" into "statuseses". By singularising first we
    normalise to "status" and then re-pluralise to "statuses" correctly.

    The _UNCOUNTABLE set protects words like "staff" from being pluralised to "staffs".

    Examples:
        "status"    → "statuses"
        "statuses"  → "statuses"  (singularises to "status" first, then pluralises)
        "staff"     → "staff"     (uncountable — unchanged)
        "activity"  → "activities"
    """
    if word in _UNCOUNTABLE:
        return word  # Uncountable words are the same in both singular and plural

    singular = _singular_noun(word)  # Try to singularise (returns None if already singular)
    if singular:
        repluralised = _plural(str(singular))
        if repluralised and repluralised.lower() == word.lower():
            # Re-pluralising the singularised form gives us back the same word —
            # this means the input was already a valid canonical plural. Return it.
            return repluralised
    # Either word was already singular, or re-pluralising produced a different result.
    # Just pluralise the input directly.
    return _plural(word)


@lru_cache(maxsize=None)
def _table_name(schema_name: str) -> str:
    """Derive a pluralised snake_case table name from a schema name.

    This is the main naming function for tables. It converts an OpenAPI schema
    name like "WorkOrder" into a PostgreSQL table name like "work_orders".

    WHY only pluralise the LAST word? For compound names like "work_order" we
    want "work_orders" not "works_orders". Only the final noun is pluralised.

    Examples:
        "Site"         → "sites"
        "WorkOrder"    → "work_orders"
        "JobNote"      → "job_notes"
        "GetSites"     → "sites"    (prefix stripped first)
        "SitesList"    → "sites"    (suffix stripped first)
        "Staff"        → "staff"    (uncountable — unchanged)
    """
    # Strip HTTP-method prefixes and response-wrapper suffixes first
    base = _strip_op_name(schema_name) or schema_name
    snake = _to_snake(base)  # e.g. "WorkOrder" → "work_order"

    if '_' in snake:
        # Split on last underscore to isolate the final word
        prefix, last = snake.rsplit('_', 1)
        return f'{prefix}_{_canonical_plural(last)}'  # e.g. "work_orders"
    # Single-word name — just pluralise it
    return _canonical_plural(snake)


# ── Schema resolution ─────────────────────────────────────────────────────────
# These helpers translate between the $ref pointer format used in OpenAPI and the
# actual schema dicts stored in all_schemas.


def _resolve_ref(ref: str, all_schemas: dict[str, Any]) -> tuple[str, dict[str, Any] | None]:
    """Return (schema_name, schema_dict) for a $ref string, or (name, None) if missing.

    A $ref string looks like "#/components/schemas/Site". The schema name is the
    last segment after the final "/".

    Args:
        ref:         A $ref string like "#/components/schemas/Site"
        all_schemas: The full components/schemas dict from the processed spec.

    Returns:
        A tuple (name, schema_dict), where schema_dict is None if the name is not
        found in all_schemas (broken $ref).
    """
    name = ref.split('/')[-1]  # Extract "Site" from "#/components/schemas/Site"
    return name, all_schemas.get(name)


def _resolve(schema: Any, all_schemas: dict[str, Any]) -> tuple[str | None, dict[str, Any] | None]:
    """Resolve a schema to (ref_name, schema_dict).

    Handles both inline schemas and $ref pointers uniformly.

    Returns:
        - (ref_name, schema_dict) when schema is a $ref
        - (None, schema)          when schema is an inline dict
        - (None, None)            when schema is not a dict at all
    """
    if isinstance(schema, dict):
        if '$ref' in schema:
            # It's a pointer — look up the target
            return _resolve_ref(schema['$ref'], all_schemas)
        # It's an inline schema dict
        return None, schema
    # Scalar value, list, or None — not a schema
    return None, None


# ── Schema classification ─────────────────────────────────────────────────────


def _is_resource(schema: Any) -> bool:
    """Return True when schema represents a resource (has an ID or id property).

    WHAT IS A RESOURCE? In simPRO's API, a "resource" is an object that has a
    unique numeric identifier. Examples: Site (has SiteID), Job (has JobID),
    Customer (has ID). These become database tables.

    Non-resources are value objects embedded within resources: an "Address" sub-
    object might have street/suburb/postcode but no ID of its own. These become
    inline columns on the parent table rather than their own table.

    WHY BOTH 'ID' AND 'id'? The simPRO spec is inconsistent — some schemas use
    "ID" (the full caps form) and some use "id" (lowercase). We check both.
    """
    if not isinstance(schema, dict):
        return False
    props = schema.get('properties', {})
    # A schema is a resource if its properties dict contains "ID" or "id"
    return isinstance(props, dict) and ('ID' in props or 'id' in props)


def _pg_type_primitive(schema: dict[str, Any]) -> str | None:
    """Map a scalar OpenAPI schema to its PostgreSQL type, or None for non-primitives.

    OpenAPI has a simple type system with "type" and optional "format" fields:
        {"type": "integer"}                    → BIGINT
        {"type": "number"}                     → NUMERIC
        {"type": "boolean"}                    → BOOLEAN
        {"type": "string"}                     → TEXT
        {"type": "string", "format": "date-time"} → TIMESTAMP WITH TIME ZONE
        {"type": "string", "format": "date"}   → DATE

    Returns None for complex schemas (objects, arrays) because those need special
    handling in the column population logic.

    WHY BIGINT for integers? simPRO IDs are large positive integers. BIGINT
    (64-bit signed) avoids overflow; INTEGER (32-bit) would cap at ~2 billion.
    """
    typ = schema.get('type', '')
    fmt = schema.get('format', '')
    if typ == 'integer':
        return 'BIGINT'
    if typ == 'number':
        return 'NUMERIC'   # Variable-precision decimal — preserves fractional values
    if typ == 'boolean':
        return 'BOOLEAN'
    if typ == 'string':
        if fmt == 'date-time':
            return 'TIMESTAMP WITH TIME ZONE'  # Full datetime with timezone offset
        if fmt == 'date':
            return 'DATE'                       # Date only (no time component)
        return 'TEXT'                           # Generic string — PostgreSQL TEXT is unlimited length
    return None  # Not a scalar type — caller must handle this


# ── Table / Column model ──────────────────────────────────────────────────────


class Column:
    """A single column in a generated DDL table.

    Holds all the information needed to render one line of a CREATE TABLE
    statement, for example:
        site_id BIGINT NOT NULL REFERENCES sites (id)

    Attributes:
        name:     The column name in snake_case (e.g. "site_id", "created_date")
        pg_type:  The PostgreSQL data type (e.g. "BIGINT", "TEXT", "JSONB")
        nullable: True → column is optional (no NOT NULL constraint)
                  False → column is required (adds NOT NULL)
        is_pk:    True → this column is part of the table's PRIMARY KEY
        fk_table: The name of the table this column references (REFERENCES <fk_table> (id)),
                  or None if this column is not a foreign key.
    """

    # __slots__ restricts the instance to only these attributes.
    # This saves memory (no per-instance __dict__) and makes typos detectable
    # at runtime (assigning an unknown attribute raises AttributeError).
    __slots__ = ('name', 'pg_type', 'nullable', 'is_pk', 'fk_table')

    def __init__(self, name: str, pg_type: str, nullable: bool = True,
                 is_pk: bool = False, fk_table: str | None = None):
        self.name = name
        self.pg_type = pg_type
        self.nullable = nullable
        self.is_pk = is_pk
        self.fk_table = fk_table


class Table:
    """A generated DDL table with its columns and metadata.

    Attributes:
        name:        The snake_case table name (e.g. "work_orders")
        schema_name: The UpperCamelCase OpenAPI schema name this table came from
                     (e.g. "WorkOrder"). Used to look up the schema for column
                     generation and for config.yaml overrides.
        declarative: If True, this table was declared explicitly in config.yaml
                     (under junction_tables) rather than derived from a schema.
                     Declarative tables skip the automated column-population pass
                     because their columns are set directly.
        columns:     The list of Column objects, in the order they'll appear in
                     the CREATE TABLE statement.
    """

    def __init__(self, name: str, schema_name: str, declarative: bool = False):
        self.name = name
        self.schema_name = schema_name
        self.declarative = declarative
        self.columns: list[Column] = []

    @property
    def pk_columns(self) -> list[Column]:
        """All columns that form part of the PRIMARY KEY."""
        return [c for c in self.columns if c.is_pk]

    @property
    def fk_columns(self) -> list[Column]:
        """All columns that reference another table (have a fk_table set)."""
        return [c for c in self.columns if c.fk_table is not None]


# ── Pass 1: discover resource schemas ────────────────────────────────────────


def _normalize_alias_tables(
    all_schemas: dict[str, Any],
    schema_to_table: dict[str, str],
    tables: dict[str, Table],
) -> None:
    """Remap contextual alias schemas (e.g. JobSite) to their canonical base tables.

    PROBLEM: The spec often has schemas like "JobSite" that are essentially "Site"
    with a subset of fields, tailored for a nested context (a site as it appears
    within a job response). These would naively generate a separate table "job_sites"
    that duplicates the "sites" table with fewer columns.

    SOLUTION: Detect alias schemas and redirect them to the canonical base table.
    A schema S is an alias for base B when:
      1. S's name ends with B's name (e.g. "Job" + "Site" = "JobSite")
      2. B is an independent resource (has its own entry in resource_names)
      3. S's properties are a non-empty subset of B's properties

    When an alias is detected, schema_to_table[S] is updated to point at B's table.
    The alias table is removed from `tables` (we don't create "job_sites" — just "sites").
    """
    # Collect all schema names that are independent resources (have an ID property)
    resource_names = frozenset(
        n for n, s in all_schemas.items()
        if isinstance(s, dict) and _is_resource(s)
    )

    def _props(schema_name: str) -> frozenset[str]:
        """Return the set of property names for a schema, or empty set if not found."""
        s = all_schemas.get(schema_name)
        return frozenset((s.get("properties") or {}).keys()) if isinstance(s, dict) else frozenset()

    def _words(name: str) -> list[str]:
        """Split a CamelCase name into its component words.
        e.g. "JobSite" → ["Job", "Site"], "WorkOrderNote" → ["Work", "Order", "Note"]
        """
        return re.findall(r'[A-Z][a-z0-9]*', name)

    remappings: dict[str, str] = {}
    for schema_name in list(schema_to_table.keys()):
        words = _words(schema_name)
        if len(words) < 2:
            continue  # Single-word names can't be aliases (no prefix to strip)
        s_props = _props(schema_name)
        if not s_props:
            continue  # No properties — can't check subset relationship

        # Try every suffix of the word list as a potential base name.
        # For "JobSite" with words ["Job", "Site"]: try "Site" (i=1).
        # For "WorkOrderNote" with words ["Work", "Order", "Note"]: try "OrderNote" (i=1), then "Note" (i=2).
        for i in range(1, len(words)):
            base_name = ''.join(words[i:])  # e.g. "Site", "OrderNote", "Note"
            if base_name not in resource_names or base_name == schema_name:
                continue  # Not an independent resource, or same name — skip
            if s_props.issubset(_props(base_name)):
                # S's properties are a subset of B's — S is an alias for B
                remappings[schema_name] = base_name
                break  # Found a base — stop trying longer suffixes

    # Apply the remappings: redirect alias schema_to_table entries to the base table
    for alias_name, base_name in remappings.items():
        alias_table = schema_to_table[alias_name]
        base_table = schema_to_table.get(base_name) or _table_name(base_name)
        schema_to_table[alias_name] = base_table  # Redirect alias → base table

        if base_table != alias_table:
            # Ensure the base table exists in tables (it might not if it was also an alias)
            if base_table not in tables:
                tables[base_table] = Table(base_table, base_name)
            # Remove the alias table — we don't want a separate "job_sites" table
            tables.pop(alias_table, None)


def _build_tables(all_schemas: dict[str, Any]) -> tuple[dict[str, Table], dict[str, str]]:
    """Return (table_name → Table, schema_name → table_name) for all resources.

    This is Pass 1: identify every resource schema and create an empty Table object
    for it. The columns are populated later in Pass 2.

    When multiple schema names map to the same table name (e.g. "Site" and "GetSite"
    both map to "sites"), we keep the CANONICAL schema — the one without an HTTP-
    method prefix, or the shorter name if both are unprefixed. The canonical schema
    is what we'll use to look up properties in Pass 2.

    Returns:
        tables:         Maps table names to Table objects (empty columns at this stage).
        schema_to_table: Maps every resource schema name to its table name.
                         This includes both canonical schemas AND alias schemas
                         that are redirected by _normalize_alias_tables.
    """
    # Start by mapping every resource schema name to its derived table name
    schema_to_table: dict[str, str] = {
        name: _table_name(name)
        for name, schema in all_schemas.items()
        if isinstance(schema, dict) and _is_resource(schema)
    }

    # Apply explicit table-name overrides from config.yaml (table_names section).
    # This lets users correct any name that the auto-derivation gets wrong.
    for schema_name, target_table in TABLE_NAMES.items():
        schema_to_table[schema_name] = target_table

    # When multiple schemas map to the same table name, pick the canonical schema.
    # Priority: (1) no HTTP-method prefix, (2) shorter name.
    table_to_canonical: dict[str, str] = {}
    for schema_name, tname in schema_to_table.items():
        if tname not in table_to_canonical:
            # First schema to claim this table name — it's the initial candidate
            table_to_canonical[tname] = schema_name
            continue

        existing = table_to_canonical[tname]
        existing_prefixed = bool(_OP_PREFIX_RE.match(existing))  # e.g. "GetSite"
        new_prefixed = bool(_OP_PREFIX_RE.match(schema_name))

        if existing_prefixed and not new_prefixed:
            # New schema has no prefix, existing does — new is more canonical
            table_to_canonical[tname] = schema_name
        elif not existing_prefixed and new_prefixed:
            # Existing has no prefix, new does — keep existing (it's more canonical)
            pass
        elif len(schema_name) < len(existing):
            # Both prefixed or both unprefixed — prefer the shorter name
            # (shorter names tend to be less specific / more canonical)
            table_to_canonical[tname] = schema_name

    # Create a Table object for each canonical schema → table mapping
    tables: dict[str, Table] = {
        tname: Table(tname, sname)
        for tname, sname in table_to_canonical.items()
    }

    # Remap alias schemas (e.g. JobSite → sites) to avoid duplicate tables
    _normalize_alias_tables(all_schemas, schema_to_table, tables)
    return tables, schema_to_table


# ── Pass 2: populate columns and FKs ─────────────────────────────────────────


def _timestamp_if_date_time(col_nm: str, pg_type: str) -> str:
    """Upgrade TEXT to TIMESTAMP WITH TIME ZONE when the column name contains 'date'.

    PROBLEM: Some date/time columns in the simPRO spec have type=string but no
    format hint. Without a format, we'd type them as TEXT. But any column whose
    name contains "date" or "iso8601" almost certainly stores a date/time value.

    SOLUTION: When we'd assign TEXT and the column name contains "date", upgrade
    to TIMESTAMP WITH TIME ZONE. This is a heuristic — it may be wrong for columns
    like "update_date" that are actually date-only, but TIMESTAMP is more general
    than DATE and can store either.

    Examples:
        col_nm="created_date", pg_type="TEXT"   → "TIMESTAMP WITH TIME ZONE"
        col_nm="name",         pg_type="TEXT"   → "TEXT"  (no change)
        col_nm="site_id",      pg_type="BIGINT" → "BIGINT" (no change — not TEXT)
    """
    if pg_type == 'TEXT' and ('date' in col_nm or 'iso8601' in col_nm):
        return 'TIMESTAMP WITH TIME ZONE'
    return pg_type


@lru_cache(maxsize=None)
def _singular(name: str) -> str:
    """Return the singular form of a snake_case table name, only singularising the last word.

    We only singularise the LAST word segment because compound names like
    "work_orders" should become "work_order" (not "work_order" via full singularisation
    which would be the same, but "work_orders" → "work_order" correctly).

    For uncountable words, the name is returned unchanged.

    Examples:
        "sites"       → "site"
        "work_orders" → "work_order"
        "staff"       → "staff"       (uncountable)
        "categories"  → "category"
    """
    if name in _UNCOUNTABLE:
        return name

    if '_' in name:
        # Split on last underscore and singularise only the last part
        prefix, last = name.rsplit('_', 1)
        s = _singular_noun(last)
        return f'{prefix}_{s}' if s else name  # Keep original if already singular
    # Single-word name
    s = _singular_noun(name)
    return s if s else name  # Return original if already singular (singular_noun → None)


def _build_stem_index(tables: dict[str, Table]) -> dict[str, str]:
    """Build a lookup from name stems to table names for FK resolution.

    PROBLEM: A schema property like "SiteID" (type: string, no $ref) should
    become a BIGINT foreign key to the "sites" table. But how do we know to
    link "SiteID" to "sites"? We need to match the stem "site" to the table.

    SOLUTION: Build an index from name stems → table names. For each table we
    register multiple stem variants:
      - The table name itself:              "sites"
      - The snake_case schema name:         "site"
      - The stripped schema name:           "site" (same here, but differs for wrapped names)
      - Singular forms of all the above:    "site"

    When resolving a property name ending in "ID/Id", we strip "_id" and look
    up the result in this index.

    Example index entries for a "sites" table (schema: "Site"):
        "sites"     → "sites"
        "site"      → "sites"
        "work_orders" → "work_orders"
        "work_order"  → "work_orders"
    """
    stem_to_table: dict[str, str] = {}
    for tname, table in tables.items():
        # Generate all candidate stems for this table
        for candidate in (
            tname,                                                         # e.g. "sites"
            _to_snake(table.schema_name),                                  # e.g. "site"
            _to_snake(_strip_op_name(table.schema_name) or table.schema_name),  # stripped variant
        ):
            stem_to_table[candidate] = tname
            # Also add the singular form (e.g. "sites" → "site")
            singular = _singular_noun(candidate)
            if singular:
                stem_to_table[singular] = tname

    return stem_to_table


def _create_junction_table(
    parent_table: Table, col_nm: str, items_ref: str,
    schema_to_table: dict[str, str], tables: dict[str, Table],
) -> None:
    """Create and register a junction table for a many-to-many array property.

    Called when we find an array property whose items are a resource schema
    (i.e. the items have their own ID). This means the parent has a many-to-many
    or one-to-many relationship that should be modelled as a separate table.

    For example, if "Job" has a property "staff" (array of Staff resources):
      - parent_table = jobs table
      - col_nm       = "staff"
      - items_ref    = "Staff"
      - Creates: job_staff table with columns (job_id, staff_id)

    The junction table name is: <parent_singular>_<col_nm_trimmed>
    Overlap is trimmed to avoid redundancy (see _trim_overlap).

    If the junction table already exists (e.g. declared in config.yaml), we skip it.
    """
    parent_singular = _singular(parent_table.name)  # e.g. "jobs" → "job"
    # Build junction table name, trimming redundant prefix overlap
    junction_name = f'{parent_singular}_{_trim_overlap(parent_singular, col_nm)}'

    if junction_name in tables:
        return  # Already exists (from config.yaml or a previous property visit)

    # Find the table name for the item type (e.g. "Staff" → "staff")
    item_table_name = schema_to_table.get(items_ref) or _table_name(items_ref)

    jt = Table(junction_name, junction_name)  # No schema_name — synthetic table

    # Add the parent FK column: e.g. "job_id" BIGINT NOT NULL REFERENCES jobs (id)
    jt.columns.append(Column(
        f'{parent_singular}_id', 'BIGINT',
        nullable=False,   # FK columns in junction tables are always required
        is_pk=True,       # Both columns together form the compound primary key
        fk_table=parent_table.name,
    ))

    # Add the item FK column: e.g. "staff_id" BIGINT NOT NULL REFERENCES staff (id)
    jt.columns.append(Column(
        f'{_singular(item_table_name)}_id', 'BIGINT',
        nullable=False,
        is_pk=True,
        fk_table=item_table_name,
    ))

    tables[junction_name] = jt


def _create_force_table(
    parent_table: Table, col_nm: str, items_resolved: dict[str, Any],
    all_schemas: dict[str, Any], tables: dict[str, Table],
) -> None:
    """Create a child table for an array property declared in force_tables.

    Used when the items schema has no ID of its own (so it can't become a
    junction table), but we still want a proper relational table rather than
    a JSONB column — e.g. schedule blocks that belong to a schedule.

    The generated table has:
      - id  BIGSERIAL PRIMARY KEY  (surrogate key; multiple rows per parent)
      - <parent_singular>_id  BIGINT NOT NULL REFERENCES <parent_table> (id)
      - one column per scalar property of the items schema
    """
    parent_singular = _singular(parent_table.name)
    child_name = f'{parent_singular}_{_trim_overlap(parent_singular, col_nm)}'

    if child_name in tables:
        return

    child = Table(child_name, child_name)

    # Surrogate PK — BIGSERIAL so the DB assigns it; callers insert without supplying it
    child.columns.append(Column('id', 'BIGSERIAL', nullable=False, is_pk=True))

    # FK back to the parent row
    child.columns.append(Column(
        f'{parent_singular}_id', 'BIGINT',
        nullable=False, fk_table=parent_table.name,
    ))

    # Scalar columns from the items schema properties
    props = items_resolved.get('properties') or {}
    for prop_name, prop_schema in props.items():
        if prop_name in ('ID', 'id'):
            continue
        c_col = _col_name(prop_name)
        _ref_name, resolved = _resolve(prop_schema, all_schemas)
        if isinstance(resolved, dict):
            pt = _pg_type_primitive(resolved)
            child.columns.append(Column(c_col, _timestamp_if_date_time(c_col, pt or 'JSONB'), nullable=True))

    tables[child_name] = child


def _dedup_key(name: str) -> str:
    """Normalise a column name for deduplication by collapsing variant spellings.

    Some simPRO schema properties have both British and American spellings
    (e.g. "IsAuthorised" and "IsAuthorized"). When we flatten a sub-object's
    properties onto the parent table, we might encounter both forms, which would
    normally produce two separate columns with nearly identical meaning.

    We normalise "iz" → "is" so "authorised" and "authorized" collapse to the
    same dedup key "authorised", allowing us to skip the duplicate.

    This is a targeted heuristic for the most common variant — not a full
    spelling normaliser.
    """
    return re.sub(r'iz', 'is', name)


def _inline_object_props(
    table: Table, prefix: str, schema: dict[str, Any], all_schemas: dict[str, Any],
    seen_dedup_keys: set[str], nullable: bool,
) -> None:
    """Flatten a non-resource object schema into prefixed columns on table.

    When a property resolves to an object that is NOT a resource (no ID), we
    don't create a separate table — instead we inline its scalar leaf properties
    directly onto the parent table with a prefix.

    For example, if "Site" has a property "address" (an Address object with
    street, suburb, postcode), we add columns:
        address_street   TEXT
        address_suburb   TEXT
        address_postcode TEXT

    WHY INLINE? Non-resource objects have no independent identity — they're
    just a group of related values. Inlining preserves queryability (you can
    filter by address_suburb) without creating a pointless one-to-one table.

    Only SCALAR leaf properties are inlined. Nested objects within the inlined
    object are added as JSONB. The "id"/"ID" property of the inlined object
    is always skipped (it would duplicate the parent table's FK column).

    Args:
        table:           The parent table to add columns to.
        prefix:          The column name prefix (the property name, snake_cased).
        schema:          The schema of the non-resource object to inline.
        all_schemas:     The full components/schemas dict for $ref resolution.
        seen_dedup_keys: Column names already added (deduplication tracking).
        nullable:        Whether the parent property was optional (propagated to columns).
    """
    props = schema.get('properties', {})
    if not isinstance(props, dict):
        return

    for prop_name, prop_schema in props.items():
        # Don't inline the ID — that's the FK column on the parent table itself
        if prop_name in ('ID', 'id'):
            continue

        # Build the column name: e.g. prefix="address", prop_name="Street" → "address_street"
        child_raw = re.sub(r'ID$', 'Id', prop_name)  # Normalise trailing ID → Id
        col_nm = f'{prefix}_{_to_snake(child_raw)}'

        # Check for duplicates using the normalised dedup key
        dk = _dedup_key(col_nm)
        if dk in seen_dedup_keys:
            continue  # Already added an equivalent column — skip
        seen_dedup_keys.add(dk)

        # Resolve the property's schema (follow $ref if needed)
        _ref_name, resolved = _resolve(prop_schema, all_schemas)

        if isinstance(resolved, dict):
            pt = _pg_type_primitive(resolved)
            # Map to PG type; fall back to JSONB for complex nested objects;
            # upgrade TEXT to TIMESTAMP if the column name contains "date"
            pg_type = _timestamp_if_date_time(col_nm, pt or 'JSONB')
        else:
            continue  # Couldn't resolve schema — skip this property

        table.columns.append(Column(col_nm, pg_type, nullable=nullable))


def _process_props(
    table: Table, props: dict[str, Any], required_set: set[str],
    tables: dict[str, Table], schema_to_table: dict[str, str], all_schemas: dict[str, Any],
    stem_to_table: dict[str, str],
) -> None:
    """Populate table.columns by walking every property in props.

    This is the core of Pass 2. For each property in the resource schema's
    "properties" dict, we decide what kind of column (or table) to create.

    RESOLUTION PRIORITY (checked in this order):
      1. $ref to a known resource table           → BIGINT FK column
      2. $ref to a non-resource with properties   → inline its scalar props
      3. array of resource items                  → create a junction table
      4. array of non-resources / primitives      → JSONB column
      5. inline object whose name matches a table → BIGINT FK column
      6. inline object with properties            → inline its scalars
      7. string ending in ID/Id                   → BIGINT FK via stem index
      8. scalar (string, int, bool, number)       → direct PG type mapping

    COLUMN NULLABILITY: A column is NOT NULL only when the property appears in
    the schema's "required" list. Everything else is nullable (optional).

    EXCLUSIONS: Properties listed in EXCLUDE_COLUMNS (global "*" wildcard or
    per-schema by schema name) are skipped entirely — they produce no column.

    Args:
        table:          The Table object to populate with Column objects.
        props:          The "properties" dict from the resource schema.
        required_set:   Set of property names listed as "required" in the schema.
        tables:         All tables (used for FK target resolution and junction table registration).
        schema_to_table: Maps schema names to table names.
        all_schemas:    The full components/schemas dict (for $ref resolution).
        stem_to_table:  The stem index built by _build_stem_index (for string-ID FK lookup).
    """
    # Load exclusion lists: "*" applies to all tables, schema_name is table-specific
    _global_skip = EXCLUDE_COLUMNS.get("*") or set()
    _schema_skip = EXCLUDE_COLUMNS.get(table.schema_name) or set()

    for prop_name, prop_schema in props.items():
        # Skip properties listed in the exclusion config
        if prop_name in _global_skip or prop_name in _schema_skip:
            continue

        col_nm = _col_name(prop_name)               # e.g. "SiteID" → "site_id"
        nullable = prop_name not in required_set     # True if property is optional

        # ── Primary key: ID / id property ────────────────────────────────────
        if prop_name in ('ID', 'id'):
            # The identity property becomes the primary key column.
            # We insert it at position 0 so it appears first in the DDL output.
            table.columns.insert(0, Column('id', 'BIGINT', nullable=False, is_pk=True))
            continue

        # Resolve the property's schema: follow $ref or use inline dict
        ref_name, resolved = _resolve(prop_schema, all_schemas)

        # ── Case 1: $ref property ─────────────────────────────────────────────
        if ref_name is not None:
            # Try to find a table for the referenced schema
            fk_tname = schema_to_table.get(ref_name)
            if fk_tname is None or fk_tname not in tables:
                # The $ref doesn't directly map to a table — try the stem index
                # This catches cases where the property name itself hints at the FK
                # (e.g. property "site" with $ref to "SiteInfo" — stem "site" → "sites")
                stem = stem_to_table.get(_to_snake(prop_name))
                if stem:
                    fk_tname = stem

            if fk_tname and fk_tname in tables:
                # Found an FK target — create a BIGINT FK column
                # Ensure the column name ends with "_id" (convention for FK cols)
                fk_col = col_nm if col_nm.endswith('_id') else _col_name(prop_name + 'Id')
                table.columns.append(Column(fk_col, 'BIGINT', nullable=nullable, fk_table=fk_tname))
            elif isinstance(resolved, dict) and resolved.get('properties'):
                # The $ref target is a non-resource object with properties.
                # Inline its scalar properties onto this table with col_nm as prefix.
                seen_dk = {_dedup_key(c.name) for c in table.columns}
                _inline_object_props(table, col_nm, resolved, all_schemas, seen_dk, nullable)
            else:
                # The $ref resolves to something we can't FK or inline — use primitive type
                pt = _pg_type_primitive(resolved or {})
                table.columns.append(Column(col_nm, _timestamp_if_date_time(col_nm, pt or 'JSONB'), nullable=nullable))
            continue

        # ── Non-$ref properties ───────────────────────────────────────────────
        if not isinstance(resolved, dict):
            continue  # Couldn't resolve the schema — skip this property

        prop_type = resolved.get('type', '')

        # ── Case 2: Array property ────────────────────────────────────────────
        if prop_type == 'array':
            items_ref, items_resolved = _resolve(resolved.get('items', {}), all_schemas)
            if items_ref and items_resolved and _is_resource(items_resolved):
                # Array of resources → create a junction table for this relationship.
                # e.g. job.staff (array of Staff) → creates job_staff junction table.
                _create_junction_table(table, col_nm, items_ref, schema_to_table, tables)
            elif prop_name in FORCE_TABLES and items_resolved:
                # force_tables config: promote this array to a proper child table
                # instead of a JSONB column, even though items have no ID.
                _create_force_table(table, col_nm, items_resolved, all_schemas, tables)
            else:
                # Array of non-resources (scalars, anonymous objects) → JSONB column.
                # JSONB stores arbitrary JSON data and supports querying in PostgreSQL.
                table.columns.append(Column(col_nm, 'JSONB', nullable=nullable))
            continue

        # ── Case 3: Inline object property ───────────────────────────────────
        if prop_type == 'object' or resolved.get('properties') or resolved.get('allOf'):
            # Check if the property name matches a known table via the stem index
            fk_tname = stem_to_table.get(_to_snake(prop_name))
            if fk_tname:
                # Property name hints at a FK relationship (e.g. "site" → "sites")
                fk_col = col_nm if col_nm.endswith('_id') else _col_name(prop_name + 'Id')
                table.columns.append(Column(fk_col, 'BIGINT', nullable=nullable, fk_table=fk_tname))
            elif resolved.get('properties'):
                # Non-resource object with properties → inline its scalar leaves
                seen_dk = {_dedup_key(c.name) for c in table.columns}
                _inline_object_props(table, col_nm, resolved, all_schemas, seen_dk, nullable)
            else:
                # Object with allOf but no direct properties (composition) → JSONB
                table.columns.append(Column(col_nm, 'JSONB', nullable=nullable))
            continue

        # ── Case 4: String ending in ID/Id → FK candidate ────────────────────
        if prop_name.endswith('ID') or prop_name.endswith('Id'):
            # Properties like "SiteID" (type: string or integer with no $ref) often
            # represent foreign keys. We strip "_id" from the column name and look
            # up the stem to find the target table.
            stem = re.sub(r'_id$', '', col_nm)  # e.g. "site_id" → "site"
            fk_tname = stem_to_table.get(stem)
            if fk_tname and fk_tname != table.name:
                # Found a FK target that's a different table (not self-referential)
                table.columns.append(Column(col_nm, 'BIGINT', nullable=nullable, fk_table=fk_tname))
                continue
            # No matching table found — treat as a plain BIGINT (probably just a number)

        # ── Case 5: Scalar property ───────────────────────────────────────────
        pt = _pg_type_primitive(resolved)
        # pt is None for non-primitives — fall back to TEXT (should be caught above,
        # but this handles any remaining edge cases)
        table.columns.append(Column(col_nm, _timestamp_if_date_time(col_nm, pt or 'TEXT'), nullable=nullable))


def _populate_columns(
    tables: dict[str, Table], schema_to_table: dict[str, str], all_schemas: dict[str, Any],
    on_progress: Callable[[int, int], None] | None = None,
) -> None:
    """Populate columns for every non-declarative table by processing its schema properties.

    This is the driver for Pass 2. It iterates through all tables, finds each
    table's canonical schema in all_schemas, and calls _process_props to fill
    in the columns.

    Declarative tables (declared in config.yaml junction_tables) are skipped here
    because their columns are set directly by _apply_declarative_junctions.

    The on_progress callback, if provided, is called after each table with
    (current_count, total_count) so the caller can update a progress bar.
    """
    stem_to_table = _build_stem_index(tables)  # Build FK stem lookup once, reuse for all tables
    table_list = list(tables.values())          # Snapshot to avoid mutation issues during iteration

    for i, table in enumerate(table_list, 1):
        if table.declarative:
            continue  # Skip config.yaml-declared junction tables

        # Look up the canonical schema for this table
        schema = all_schemas.get(table.schema_name)
        if not isinstance(schema, dict):
            continue  # Schema not found — table has no definition to derive columns from

        props = schema.get('properties', {})
        if not isinstance(props, dict):
            continue  # Schema has no properties dict

        # Determine which properties are required (non-nullable)
        required_set = set(schema.get('required', []))

        # Populate this table's columns from the schema properties
        _process_props(table, props, required_set, tables, schema_to_table, all_schemas, stem_to_table)

        if on_progress:
            on_progress(i, len(table_list))  # Report progress for UI


# ── Pass 3: junction tables ───────────────────────────────────────────────────


def _apply_declarative_junctions(tables: dict[str, Table], junction_defs: dict[str, list[str]]) -> None:
    """Apply junction tables declared in config.yaml, replacing any auto-generated table of the same name.

    config.yaml can declare junction tables explicitly under the "junction_tables" key:

        junction_tables:
          job_cost_centre:
            - jobs
            - cost_centres

    This creates a table "job_cost_centre" with columns:
        job_id          BIGINT NOT NULL REFERENCES jobs (id)
        cost_centre_id  BIGINT NOT NULL REFERENCES cost_centres (id)
        PRIMARY KEY (job_id, cost_centre_id)

    Declarative junction tables take precedence over auto-detected ones: if the
    auto-detection already created a table with the same name, it's replaced here.

    The Table is marked declarative=True so _populate_columns skips it — the
    columns are set right here, not derived from a schema.
    """
    for jname, ref_tables in junction_defs.items():
        if not ref_tables or len(ref_tables) < 2:
            continue  # A junction table needs at least 2 sides to make sense

        jt = Table(jname, jname, declarative=True)

        for ref in ref_tables:
            singular = _singular(ref)  # e.g. "jobs" → "job" for the column name
            # The FK target is this table if it exists, otherwise it's a forward reference
            target = ref if ref in tables else None
            jt.columns.append(Column(
                f"{singular}_id", 'BIGINT',
                nullable=False,  # Junction table FK columns are always required
                is_pk=True,      # Both columns form a compound primary key
                fk_table=target,
            ))

        # Replace any existing table with this name (overrides auto-detection)
        tables[jname] = jt


def _detect_junction_tables(tables: dict[str, Table]) -> None:
    """Give compound PKs to auto-detected junction tables (≥2 FK cols, no own ID, no other cols).

    WHAT IS AN AUTO-DETECTED JUNCTION TABLE? A table created by _create_junction_table
    during _process_props. These tables were built to model many-to-many array
    relationships. They have two FK columns and no other columns.

    COMPOUND PRIMARY KEY: For a junction table, the pair (parent_id, item_id) should
    be unique — we don't want duplicate rows saying "job 5 has staff member 3" twice.
    A compound primary key on both FK columns enforces this constraint.

    We identify junction candidates by these criteria:
      1. No existing PK columns (the table hasn't had a PK assigned yet)
      2. At least 2 FK columns
      3. Zero non-FK columns (only FKs — no extra payload columns)
    """
    for table in tables.values():
        if table.pk_columns:
            continue  # Already has a PK — not a junction candidate

        fk_cols = [c for c in table.columns if c.fk_table is not None]
        non_fk = [c for c in table.columns if c.fk_table is None]

        if len(fk_cols) >= 2 and not non_fk:
            # Mark all FK columns as part of the compound primary key
            for c in fk_cols:
                c.is_pk = True


# ── Topological sort ──────────────────────────────────────────────────────────


def _topo_sort(tables: dict[str, Table]) -> list[Table]:
    """Order tables so FK targets are created before the tables that reference them.

    PROBLEM: PostgreSQL evaluates REFERENCES constraints when executing CREATE TABLE.
    If table A references table B via a FK, B must already exist when A's CREATE TABLE
    runs. Without sorting, we'd get errors like "relation 'sites' does not exist".

    ALGORITHM (Kahn's algorithm — a standard topological sort):
      1. Build a dependency graph: for each table, record which other tables it
         depends on (FK targets that are different tables).
      2. Start with tables that have zero dependencies (no FK targets) — these
         can be created first.
      3. Repeatedly: take a table from the zero-dependency queue, emit it, and
         decrement the in-degree of tables that depended on it. When a table's
         in-degree reaches zero, add it to the queue.
      4. Tables with remaining dependencies after the queue empties are in CYCLES
         (A → B → A). Append them in sorted order — their FK constraints must
         become ALTER TABLE statements emitted AFTER all CREATE TABLEs.

    Returns:
        A list of Table objects in a valid creation order.
    """
    # Build the dependency set for each table
    # deps[table_name] = set of table names that must be created BEFORE table_name
    deps: dict[str, set[str]] = {t: set() for t in tables}
    for tname, table in tables.items():
        for col in table.fk_columns:
            # Only add a dependency if the FK target exists as a table AND is different
            # from the current table (self-referential FKs don't block creation)
            if col.fk_table and col.fk_table in tables and col.fk_table != tname:
                deps[tname].add(col.fk_table)

    # in_degree[table_name] = how many tables this table still depends on
    in_degree = {t: len(d) for t, d in deps.items()}

    # Start with all tables that have no dependencies (can be created immediately)
    # sorted() gives a deterministic order within the "ready" set
    queue: deque[str] = deque(sorted(t for t, d in in_degree.items() if d == 0))
    ordered: list[Table] = []

    while queue:
        tname = queue.popleft()      # Take the next table that's ready to emit
        ordered.append(tables[tname])

        # For every other table: if it depended on `tname`, decrement its in-degree.
        # When a table's in-degree hits 0, all its dependencies have been emitted —
        # add it to the queue.
        for other in sorted(deps.keys()):
            if tname in deps[other]:
                deps[other].discard(tname)   # Remove the satisfied dependency
                in_degree[other] -= 1
                if in_degree[other] == 0:
                    queue.append(other)      # Ready to emit

    # Any tables not in `ordered` are involved in reference cycles.
    # Append them in sorted order — their FK constraints will be emitted as
    # ALTER TABLE statements after all CREATE TABLEs.
    emitted = {t.name for t in ordered}
    for tname in sorted(tables.keys()):
        if tname not in emitted:
            ordered.append(tables[tname])

    return ordered


# ── DDL rendering ─────────────────────────────────────────────────────────────


def _render_create_table(table: Table, emitted: frozenset[str]) -> str:
    """Render a CREATE TABLE statement for table, inlining REFERENCES where the target is already emitted.

    Generates the SQL for one table. The `emitted` set tells us which tables have
    already been output in the DDL file BEFORE this table. We can only inline a
    REFERENCES clause if the target table was already created — otherwise we'd get
    a "relation does not exist" error from PostgreSQL.

    FK columns whose target has NOT yet been emitted are left WITHOUT a REFERENCES
    clause here; the caller collects them and emits ALTER TABLE ... ADD CONSTRAINT
    statements at the end of the file (after all tables exist).

    Example output:
        CREATE TABLE job_notes (
            id            BIGINT NOT NULL,
            job_id        BIGINT REFERENCES jobs (id),
            content       TEXT,
            created_date  TIMESTAMP WITH TIME ZONE,
            PRIMARY KEY (id)
        );
    """
    col_defs: list[str] = []

    for col in table.columns:
        # Build the NOT NULL clause (empty string = nullable, i.e. column is optional)
        null_str = '' if col.nullable else ' NOT NULL'
        # Build the REFERENCES clause only when the FK target is already emitted
        ref_str = f' REFERENCES {col.fk_table} (id)' if col.fk_table and col.fk_table in emitted else ''
        col_defs.append(f'    {col.name} {col.pg_type}{null_str}{ref_str}')

    pks = table.pk_columns
    if pks:
        # Render the PRIMARY KEY constraint as the last entry in the column list
        col_defs.append(f'    PRIMARY KEY ({", ".join(c.name for c in pks)})')

    return f'CREATE TABLE {table.name} (\n' + ',\n'.join(col_defs) + '\n);'


# ── Junction table config loading (lazy — reads after setup_junction_yaml writes) ──


def _load_junction_tables() -> dict[str, list[str]]:
    """Load junction_tables from config.yaml at call time (not module load time).

    WHY LAZY? setup_junction_yaml() may write new junction tables to config.yaml
    earlier in the same pipeline run. If we loaded junction_tables at module import
    time (before setup_junction_yaml runs), we'd miss those changes.

    By loading inside generate_sql() (which is called AFTER setup_junction_yaml()),
    we always see the most up-to-date config.yaml content.

    Returns an empty dict if config.yaml doesn't exist or has no junction_tables.
    """
    if not CONFIG_FILE.exists():
        return {}
    try:
        from ruamel.yaml import YAML as _YAML
        _yaml = _YAML(typ="safe")  # Safe mode: no arbitrary Python object deserialisation
        data = _yaml.load(CONFIG_FILE.read_text(encoding="utf-8")) or {}
        return data.get("junction_tables") or {}
    except Exception:
        return {}  # If anything goes wrong reading config, continue without junction tables


# ── Public API ────────────────────────────────────────────────────────────────


def generate_sql(openapi: dict[str, Any]) -> str:
    """Derive a PostgreSQL DDL schema from a processed OpenAPI spec dict.

    Runs the four passes described in the module docstring and returns the
    complete DDL as a string ready to write to init.sql.

    Uses the `rich` library for progress bars if it's installed. If `rich` is
    not available (optional dependency), falls back to a no-op context so all
    the progress-update calls are silently ignored.

    The rendering step uses a thread pool to parallelise CREATE TABLE generation
    across all tables, since each table is independent.
    """
    # Extract the processed schema definitions from the spec
    all_schemas: dict[str, Any] = openapi.get('components', {}).get('schemas', {})

    # Try to import rich for a nice progress display; fall back gracefully if absent
    try:
        from rich.console import Console
        from rich.progress import BarColumn, MofNCompleteColumn, Progress, SpinnerColumn, TextColumn
        _progress_cm: Any = Progress(
            SpinnerColumn(),
            TextColumn('[cyan]{task.description}'),
            BarColumn(),
            MofNCompleteColumn(),
            console=Console(stderr=True, highlight=False),
            transient=True,  # Progress bar disappears when done (keeps terminal clean)
        )
    except ImportError:
        # rich not installed — use a no-op context manager
        _progress_cm = contextlib.nullcontext()

    with _progress_cm as progress:
        # Helper: add a progress task only when rich is available
        def _task(desc: str, total: int | None = None) -> Any:
            return progress.add_task(desc, total=total) if progress else None

        # Helper: update a task only when rich is available
        def _update(task: Any, **kw: Any) -> None:
            if progress and task is not None:
                progress.update(task, **kw)

        # ── Pass 1: Identify schemas → create empty Table objects ─────────────
        t1 = _task('Identifying schemas', total=None)
        tables, schema_to_table = _build_tables(all_schemas)
        _update(t1, total=1, completed=1)

        # ── Pass 2: Populate columns for each table ───────────────────────────
        t2 = _task('Processing columns', total=len(tables))

        def _on_progress(done: int, total: int) -> None:
            _update(t2, completed=done, total=total)

        _populate_columns(tables, schema_to_table, all_schemas, on_progress=_on_progress)
        _update(t2, total=1, completed=1)

        # ── Pass 3: Finalise junction tables, sort ────────────────────────────
        t3 = _task('Sorting tables', total=None)
        _detect_junction_tables(tables)                             # Auto-detect from structure
        _apply_declarative_junctions(tables, _load_junction_tables()) # Apply config.yaml declarations
        ordered = _topo_sort(tables)                                # Order for safe FK creation
        _update(t3, total=1, completed=1)

        # Pre-compute which tables have been emitted before each position in `ordered`.
        # This is used in rendering to know which REFERENCES clauses are safe to inline.
        # emitted_at[i] = frozenset of table names that appear before ordered[i].
        existing_tables = set(tables.keys())
        emitted_at: list[frozenset[str]] = []
        seen: set[str] = set()
        for tbl in ordered:
            emitted_at.append(frozenset(seen))
            seen.add(tbl.name)

        # ── Pass 4: Render DDL ────────────────────────────────────────────────
        t4 = _task('Rendering DDL', total=len(ordered))

        def _render_one(args: tuple[Table, frozenset[str]]) -> tuple[str | None, list[str]]:
            """Render one table's CREATE TABLE statement plus any deferred FKs.

            Returns:
                create:   The CREATE TABLE SQL string, or None if the table has no columns.
                deferred: ALTER TABLE statements for FK constraints that couldn't be
                          inlined (because the target table comes later in the file).
            """
            tbl, emitted = args

            if not tbl.columns:
                # Table has no columns — don't emit anything (would be invalid SQL)
                if progress and t4 is not None:
                    progress.advance(t4)
                return None, []

            create = _render_create_table(tbl, emitted)

            # Collect FK constraints that couldn't be inlined because the target
            # table wasn't emitted yet. These become ALTER TABLE statements.
            deferred = [
                f'ALTER TABLE {tbl.name}\n'
                f'    ADD CONSTRAINT fk_{tbl.name}_{col.name}\n'
                f'    FOREIGN KEY ({col.name}) REFERENCES {col.fk_table} (id);'
                for col in tbl.fk_columns
                if col.fk_table in existing_tables and col.fk_table not in emitted
            ]

            if progress and t4 is not None:
                progress.advance(t4)
            return create, deferred

        # Render all tables in parallel using a thread pool.
        # Each table is independent, so parallelism is safe.
        with ThreadPoolExecutor() as executor:
            results = list(executor.map(_render_one, zip(ordered, emitted_at)))

    # Collect all CREATE TABLE statements (filter out None for empty tables)
    create_stmts = [c for c, _ in results if c]
    # Collect all deferred ALTER TABLE statements
    fk_stmts = [stmt for _, deferred in results for stmt in deferred]

    sections = create_stmts[:]
    if fk_stmts:
        # Add a comment header before the deferred FK section for readability
        sections += ['-- Deferred foreign key constraints (cycles / self-references)'] + fk_stmts

    # Join all sections with a blank line between each statement
    return '\n\n'.join(sections)


# ── Interactive junction table setup ─────────────────────────────────────────


def _save_junction_tables(junction_tables: dict[str, list[str]]) -> None:
    """Write junction_tables back into config.yaml, preserving all other content.

    Uses ruamel.yaml in round-trip mode so that comments and formatting in
    config.yaml are preserved — only the junction_tables section is updated.
    The junction table lists are written in block style (one table per line)
    for readability.
    """
    from ruamel.yaml import YAML
    from ruamel.yaml.comments import CommentedSeq  # Allows controlling YAML list style

    yaml = YAML()  # Round-trip mode: preserves comments and formatting
    yaml.default_flow_style = False

    # Load existing config.yaml (or start fresh if it doesn't exist)
    if CONFIG_FILE.exists():
        data = yaml.load(CONFIG_FILE.read_text(encoding="utf-8")) or {}
    else:
        data = {}

    # Build the junction_tables map with block-style lists
    jt_map: dict[str, Any] = {}
    for name, table_list in junction_tables.items():
        seq = CommentedSeq(table_list)  # A list that supports YAML formatting attributes
        seq.fa.set_block_style()         # Emit as YAML block list (one item per line)
        jt_map[name] = seq
    data["junction_tables"] = jt_map

    # Write to an in-memory string first, then flush to disk
    buf = io.StringIO()
    yaml.dump(data, buf)
    CONFIG_FILE.write_text(buf.getvalue(), encoding="utf-8")
    print(f"  Written: {CONFIG_FILE} ({len(junction_tables)} junction table(s))")


def _ask_confirm(message: str, default: bool = False, q: types.ModuleType | None = None) -> bool:
    """Prompt for yes/no confirmation and return the result.

    Three modes:
      - questionary available AND stdin is a TTY: use styled questionary prompt.
      - stdin is not a TTY (CI environment): return `default` without prompting.
        This prevents pipelines from hanging waiting for user input that will never come.
      - questionary not available, stdin IS a TTY: fall back to plain input().

    Args:
        message: The question to display (without the [y/N] suffix).
        default: The answer to return when running non-interactively.
        q:       The questionary module if available, or None.
    """
    if q is not None and sys.stdin.isatty():
        # Rich interactive prompt via questionary
        result: bool | None = q.confirm(message, default=default).ask()
        return result if result is not None else default  # Handle Ctrl-C → return default

    if not sys.stdin.isatty():
        # Non-interactive (CI) — don't prompt, use default
        return default

    # Plain terminal fallback: show [y/N] or [Y/n] suffix based on default
    suffix = " [y/N] " if not default else " [Y/n] "
    try:
        ans = input(message + suffix).strip().lower()
    except (EOFError, KeyboardInterrupt):
        return default  # Handle Ctrl-C or EOF gracefully
    # If user pressed Enter without typing, return default; otherwise check for yes
    return ans in ("y", "yes") if ans else default


def _input_line(prompt: str) -> str:
    """Read a line of input, returning an empty string on EOF or Ctrl-C."""
    try:
        return input(prompt).strip()
    except (EOFError, KeyboardInterrupt):
        return ""


def setup_junction_yaml(openapi: dict[str, Any]) -> None:
    """Prompt the user to define junction tables, then write them to config.yaml.

    This is called before generate_sql() so that user-defined junction tables are
    available when column processing runs.

    Table selection uses plain text input: type one table name at a time and press
    Enter. Invalid names are rejected with an error and re-prompted. A blank entry
    signals that you are done adding tables for the current junction table.

    In non-interactive environments (stdin is not a TTY, e.g. CI), the function
    returns immediately without writing anything.
    """
    print("\n── Junction table setup ────────────────────────────────────────────────")

    if not sys.stdin.isatty():
        print("  stdin is not a TTY — skipping interactive prompt.")
        return

    # Build the set of valid table names from the spec
    table_names_sorted = sorted(
        _build_tables(openapi.get("components", {}).get("schemas", {}))[0].keys()
    )
    valid_tables: set[str] = set(table_names_sorted)

    if not table_names_sorted:
        print("  No tables derived from spec.")
        _save_junction_tables({})
        return

    print(f"  {len(table_names_sorted)} table(s) available:")
    # Print the table list in columns of ~4 so it is readable but compact
    col_width = max(len(n) for n in table_names_sorted) + 2
    cols = max(1, 80 // col_width)
    for i in range(0, len(table_names_sorted), cols):
        print("  " + "".join(n.ljust(col_width) for n in table_names_sorted[i:i + cols]))
    print()

    if not _ask_confirm(
        "Define junction tables? (overwrites junction_tables in config.yaml)",
        default=False,
    ):
        return

    junction_tables: dict[str, list[str]] = {}

    while True:
        # ── Get the junction table name ───────────────────────────────────────
        name = _input_line("\nJunction table name (blank to finish): ")
        if not name:
            break

        # ── Collect participating tables one at a time ────────────────────────
        selected: list[str] = []
        print(f"  Type a table name to add to '{name}', blank when done.")
        while True:
            entry = _input_line(f"  Table ({len(selected)} so far, blank to finish): ")
            if not entry:
                break
            if entry not in valid_tables:
                # Reject immediately and stay in the loop — no need to re-print the list
                print(f"  '{entry}' is not a known table — check spelling and try again.")
                continue
            if entry in selected:
                print(f"  '{entry}' is already in the list.")
                continue
            selected.append(entry)
            print(f"  ✓ {entry}")

        if len(selected) < 2:
            print("  Need at least 2 tables — skipped.")
            continue

        junction_tables[name] = selected
        print(f"  Defined: {name} ← {', '.join(selected)}")

        if not _ask_confirm("Add another junction table?", default=False):
            break

    _save_junction_tables(junction_tables)
