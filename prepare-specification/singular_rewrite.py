

from __future__ import annotations
import json, re, inflect
from xxlimited import Str
from tokenize import group
from enum import Enum
from pydantic import BaseModel, ConfigDict, Field, RootModel, field_validator, model_validator
from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap, CommentedSeq
from pathlib import Path
from typing import Any, Callable, Iterable, List, Literal, Optional, Tuple, TypeVar; T = TypeVar('T')

# region serialization _______________________________________________________

def load_json(path: str | Path) -> dict[str, Any]:
    """Load a JSON file and return its contents"""
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)

yaml = YAML()
yaml.default_flow_style = False
yaml.indent(sequence=2, offset=0)
yaml.width = 120

def load_yaml(path: str | Path) -> dict[str, Any]:
    """Load a YAML file and return its contents"""
    with open(path, "r", encoding="utf-8") as fh:
        return YAML(typ="safe").load(fh)

def write_yaml(data: dict[str, Any], path: str | Path) -> None:
    with open(path, "w", encoding="utf-8") as fh:
        yaml.dump(data, fh)

def write_sql(sql: str, path: str | Path) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write(sql)

# endregion __________________________________________________________________

# region Iter_Utils _______________________________________________________

def partition(
    iterable: Iterable[T],
    predicate: Callable[[T], bool],
) -> Tuple[List[T], List[T]]:
    """
    Splits an iterable into `truthy` and `falsey` lists based on a predicate.
    
    >>> partition([1, 2, 3, 4], lambda x: x % 2 == 0)
        ([2, 4], [1, 3])
    """
    t1, t2 = [], []
    for item in iterable:
        (t1 if predicate(item) else t2).append(item)
    return t1, t2

def separate_into_words(string: str) -> list[str]:
    """
    Splits PascalCase string into words: 'PascalCase' → ['Pascal', 'Case']
    Assumes that PascalCase logically dictates the splitter rule.
    """
    words: list[str] = []; 
    current = string[0]
    for char in string[1:]:
        # Begin a new word when lowercase → uppercase transition happens
        prev = current[-1]
        if char.isupper() and not prev.isupper():
            words.append(current)
            current = char
        else:
            current += char
    words.append(current)
    return words

# endregion __________________________________________________________________

# region regex

def _to_snake(name: str) -> str:
    """Converts CamelCase or mixedCase to snake_case."""
    name = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1_\2', name)
    name = re.sub(r'ID$', 'Id', name)
    return re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', name).lower()

# endregion

# region OpenAPI

class In(str, Enum):
    """Path parameters are part of the URL template itself."""
    path = "path"
    """Query parameters appear after the '?' in a URL."""
    query = "query"
    header = "header"
    cookie = "cookie"

class Reference(BaseModel):
    ref: str = Field(alias="$ref")
    model_config = ConfigDict(validate_by_alias=True)

    def dereference(self) -> Any:
        if not self.ref.startswith("#/components/"): raise ValueError(f"Invalid $ref '{self.ref}'")
        category, key = self.ref[len("#/components/"):].split("/", 1)
        try: return getattr(OPENAPI.components, category)[key]
        except AttributeError: raise KeyError(f"'{category}' not found in '#/components/'")
        except KeyError: raise KeyError(f"'{key}' not found in '#/components/{category}/'")

type SchemaRef = Schema | Reference
type SchemaList = list[SchemaRef]
type SchemaDict = dict[str, SchemaRef]

class Schema(BaseModel):
    model_config = ConfigDict(extra="forbid")
    type: Optional[str] = None
    properties: Optional[SchemaDict] = None
    items: Optional[SchemaRef] = None
    allOf: Optional[SchemaList] = None
    anyOf: Optional[SchemaList] = None
    oneOf: Optional[SchemaList] = None
    # * Pydantic coerces JSON list[str] --> set[str]
    required: Optional[set[str]] = None
    enum: Optional[list[Any]] = None
    description: Optional[str] = None
    example: Optional[Any] = None
    deprecated: Optional[bool] = None
    default: Optional[Any] = None
    pattern: Optional[str] = None
    format: Optional[str] = None
    title: Optional[str] = None
    format: Optional[str] = None
    minLength: Optional[int] = None
    maxLength: Optional[int] = None
    minimum: Optional[float] = None
    maximum: Optional[float] = None
    nullable: Optional[bool] = None

    def has_id(schema: Schema) -> bool:
        """A resource has an ID or id field."""
        return schema.properties and ("ID" in schema.properties or "id" in schema.properties)

    def get_properties(self):
        properties = None
        if self.items is not None:
            schema = self.items.dereference()
            properties = schema.properties
        elif self.properties:
            properties = self.properties
        return properties

    def dereference(self): return self

    def is_primitive(self) -> bool:
        return not (
            self.allOf or self.anyOf or self.oneOf or
            self.type in ("object", "array", None) or
            self.properties or self.items
        )

class MediaType(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_: Optional[Schema | Reference] = Field(alias="schema", default=None)
    example: Optional[Any] = None

class Content(BaseModel):
    model_config = ConfigDict(extra="forbid")
    description: Optional[str] = None
    content: dict[str, MediaType] = Field(default_factory=dict)
    def schema(self) -> Optional[SchemaRef]:
        m: MediaType = self.content.get("application/json")
        return m.schema_ if m else None

class Operation(BaseModel):
    #model_config = ConfigDict(extra="forbid")
    operationId: Optional[str] = None
    parameters: list[Parameter | Reference] = Field(default_factory=list)
    requestBody: Optional[Content] = None
    responses: dict[str, Content] = Field(default_factory=dict)
    tags: Optional[list[str]] = None
    #summary: Optional[str]
    description: Optional[str]

class Parameter(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str
    in_: In = Field(alias="in")
    required: Optional[bool] = None
    schema_: Optional[Schema | Reference] = Field(alias="schema", default=None)
    content: Optional[dict[str, Content]] = None
    description: Optional[str] = None
    example: Optional[Any] = None

    @model_validator(mode="after")
    def validate(self):
        if self.in_ == In.path and not self.required:
            logger.warning(f"Parameter '{self.name}' (path) → required=True")
            self.required = True
        if not (self.schema_ or self.content):
            raise ValueError(f"Parameter '{self.name}' needs schema or content")
        return self

class PathItem(BaseModel):
    singleResourceName: Optional[str] = None
    model_config = ConfigDict(extra="forbid")
    """https://swagger.io/docs/specification/v3_0/paths-and-operations/"""
    parameters: list[Parameter | Reference] = Field(default_factory=list)
    get: Optional[Operation] = None
    post: Optional[Operation] = None
    put: Optional[Operation] = None
    patch: Optional[Operation] = None
    delete: Optional[Operation] = None
    options: Optional[Operation] = None 
    head: Optional[Operation] = None 
    trace: Optional[Operation] = None

class Components(BaseModel):
    model_config = ConfigDict(extra="forbid")
    parameters: dict[str, Parameter] = Field(default_factory=dict)
    schemas: dict[str, Schema] = Field(default_factory=dict)

class OpenAPI(BaseModel):
    model_config = ConfigDict(extra="forbid")
    openapi: str                         
    info: dict[str, Any]                 
    servers: Optional[list[dict[str, Any]]] = None
    paths: dict[str, PathItem]
    components: Components = Field(default_factory=Components)
    
DIR = Path(__file__).parent
OPENAPI = OpenAPI.model_validate(load_json(DIR / "openapi.json"))
COMPONENTS_PARAMETERS: dict[str, Parameter] = OPENAPI.components.parameters
COMPONENTS_SCHEMAS: dict[str, Schema] = OPENAPI.components.schemas
DEBUG_UNFILTERED = False

# endregion

# region Config

class Filter(BaseModel):
    paths: Optional[dict[str, set[str]]] = None
    schema_fields: dict[str, set[str]] = Field(default_factory=dict)

class Config(BaseModel):
    filter: Optional[Filter] = Filter
    defaults: Optional[dict[str, int]] = None
    table_name: Optional[dict[str, str]] = None
    exclude_from_database_columns: Optional[dict[str, set[str]]] = None
    force_tables: Optional[List[str]] = None
    junction_tables: Optional[dict[str, List[str]]] = None
    URL_PREFIX_PATTERN: Optional[str] = None
    NO_EXAMPLES: bool = False
    NO_TAGS: bool = False
    NO_SQL: bool = False
    SERVER_URL: Optional[str] = "/"
    schema_aliases: Optional[dict[str, str]] = None

# region SQL

class Column:
    __slots__ = ("name", "pg_type", "nullable", "is_pk", "fk")

    def __init__(self, name: str, pg_type: str, *, nullable=True, pk=False, fk=None):
        self.name = name
        self.pg_type = pg_type
        self.nullable = nullable
        self.is_pk = pk
        self.fk = fk

    def sql(self, emitted=None) -> str:
        parts = [self.name, self.pg_type]
        if not self.nullable:
            parts.append("NOT NULL")
        if self.fk and emitted and self.fk in emitted:
            parts.append(f"REFERENCES {self.fk} (id)")
        return " ".join(parts)

class Table:
    def __init__(self, name: str, schema_name: str):
        self.name = name
        self.schema_name = schema_name
        self.columns: list[Column] = []

    @property
    def pk(self):
        return [c.name for c in self.columns if c.is_pk]

    def sql(self, emitted=None) -> str:
        cols = [c.sql(emitted) for c in self.columns]
        if self.pk:
            cols.append(f"PRIMARY KEY ({', '.join(self.pk)})")
        return f"CREATE TABLE {self.name} (\n  " + ",\n  ".join(cols) + "\n);"

def pg_type(schema: Schema) -> str:
    """Map OpenAPI primitive → PostgreSQL type."""
    return {
        "integer": "BIGINT",
        "number": "NUMERIC",
        "boolean": "BOOLEAN",
    }.get(schema.type) or (
        "TIMESTAMP WITH TIME ZONE" if schema.type == "string" and schema.format == "date-time"
        else "DATE" if schema.type == "string" and schema.format == "date"
        else "TEXT"
    )

def table_name(schema_name: str) -> str:
    if CONFIG.table_name:
        if schema_name in CONFIG.table_name:
            return CONFIG.table_name[schema_name]
    
    snake = _to_snake(schema_name)

    def plural(word: str) -> str:
        return INFLECT_ENGINE.plural(str(word)) or word + "s"

    if "_" in snake:
        prefix, end = snake.rsplit("_", 1)
        return f"{prefix}_{plural(end)}"

    return plural(snake)

def build_stem_index(tables: dict[str, Table]) -> dict[str, str]:
    index = {}

    for t in tables.values():
        # table name → sites
        index[t.name] = t.name

        # schema name → Site → site
        snake = _to_snake(t.schema_name)
        index[snake] = t.name

        # singular form → site
        singular = INFLECT_ENGINE.singular_noun(snake)
        if singular:
            index[singular] = t.name

    return index

def table_names() -> dict[str, Table]:
    return {
        table_name(name): Table(table_name(name), name)
        for name, schema in COMPONENTS_SCHEMAS.items()
        if schema.has_id()
    }

def build_stem_index(tables: dict[str, Table]) -> dict[str, str]:
    index = {}

    for t in tables.values():
        # table name → sites
        index[t.name] = t.name

        # schema name → Site → site
        snake = _to_snake(t.schema_name)
        index[snake] = t.name

        # singular form → site
        singular = INFLECT_ENGINE.singular_noun(snake)
        if singular:
            index[singular] = t.name

    return index

def is_forced_table(name: str) -> bool:
    if not CONFIG.force_tables:
        return False

    snake = _to_snake(name)
    return any(
        _to_snake(t) == snake
        for t in CONFIG.force_tables
    )

def populate_columns(tables: dict[str, Table]) -> None:
    stem_index = build_stem_index(tables)
    
    for table in list(tables.values()):
        schema = COMPONENTS_SCHEMAS.get(table.schema_name)
        if not schema or not schema.properties:
            continue

        required = schema.required or set()

        for name, prop in schema.properties.items():
            if name in CONFIG.exclude_from_database_columns['*']: # Asterisk : ALL
                continue
            
            if CONFIG.schema_aliases:
                name = CONFIG.schema_aliases.get(name, name)
            
            col = _to_snake(name)
            
            nullable = name not in required
            s = prop.dereference()

            if name in ("ID", "id"):
                table.columns.insert(0, Column("id", "BIGINT", nullable=False, pk=True))
                continue

            if s.type == "array":
                if not s.items:
                    table.columns.append(Column(col, "JSONB", nullable=nullable))
                    continue
                else:
                    items = s.items.dereference()
                    if items.has_id():
                        jt_name = f"{table.name}_{_to_snake(name)}"
                        
                        if jt_name in tables:
                            continue
                                                
                        jt = Table(jt_name, jt_name)

                        target = stem_index.get(_to_snake(name[:-1]))
                        jt.columns.append(Column(f"{table.name[:-1]}_id", "BIGINT", nullable=False, pk=True, fk=table.name))
                        jt.columns.append(Column(f"{_to_snake(name[:-1])}_id", "BIGINT", nullable=False, pk=True, fk=target))

                        tables[jt_name] = jt
                        continue

            if s.type == "object" and s.properties:
                # ONLY promote to table if explicitly forced
                if not is_forced_table(name):
                    fk = stem_index.get(_to_snake(name))
                    table.columns.append(
                        Column(
                            f"{col}_id" if fk else col,
                            "BIGINT" if fk else "JSONB",
                            nullable=nullable,
                            fk=fk
                        )
                    )
                    continue

                # --- forced table logic ---
                child_table_name = table_name(name)

                if child_table_name in tables:
                    continue

                child = Table(child_table_name, name)

                # PK (modern Postgres style)
                child.columns.append(
                    Column("id", "BIGINT GENERATED ALWAYS AS IDENTITY", nullable=False, pk=True)
                )

                # FK back to parent
                parent_fk = INFLECT_ENGINE.singular_noun(table.name) or table.name
                child.columns.append(
                    Column(f"{parent_fk}_id", "BIGINT", nullable=False, fk=table.name)
                )

                # populate child columns
                for sub_name, sub_prop in s.properties.items():
                    sub_col = _to_snake(sub_name)
                    sub_schema = sub_prop.dereference()

                    if sub_schema.type == "object" or sub_schema.properties:
                        fk = stem_index.get(_to_snake(sub_name))
                        if fk:
                            child.columns.append(
                                Column(f"{sub_col}_id", "BIGINT", fk=fk)
                            )
                            continue

                    if sub_name.endswith(("ID", "Id")):
                        stem = _to_snake(sub_name).replace("_id", "")
                        fk = stem_index.get(stem)
                        if fk:
                            child.columns.append(
                                Column(sub_col, "BIGINT", fk=fk)
                            )
                            continue

                    child.columns.append(Column(sub_col, pg_type(sub_schema)))

                tables[child_table_name] = child
                continue

            if name.endswith(("ID", "Id")):
                stem = _to_snake(name).replace("_id", "")
                fk = stem_index.get(stem)
                if fk:
                    table.columns.append(Column(col, "BIGINT", nullable=nullable, fk=fk))
                    continue

            table.columns.append(Column(col, pg_type(s), nullable=nullable))

def singular(name: str) -> str:
    return INFLECT_ENGINE.singular_noun(name) or name

def add_config_junction_tables(tables: dict[str, Table]) -> None:
    if not CONFIG.junction_tables:
        return

    for jt_name, (left, right) in CONFIG.junction_tables.items():
        jt = Table(jt_name, jt_name)

        # normalize table names (important!)
        left_table = tables.get(left)
        right_table = tables.get(right)

        if not left_table or not right_table:
            raise ValueError(f"Invalid junction table '{jt_name}': {left}, {right}")

        # column names (singularized)
        left_col = f"{singular(left)}_id"
        right_col = f"{singular(right)}_id"

        jt.columns.append(Column(left_col, "BIGINT", nullable=False, pk=True, fk=left))
        jt.columns.append(Column(right_col, "BIGINT", nullable=False, pk=True, fk=right))

        tables[jt_name] = jt

def topological_sort(tables: dict[str, Table]) -> list[Table]:
    deps = {t.name: {c.fk for c in t.columns if c.fk} for t in tables.values()}

    ordered = []
    while deps:
        ready = [t for t, d in deps.items() if not d]
        if not ready:
            break  # cycle

        for r in ready:
            ordered.append(tables[r])
            deps.pop(r)
            for d in deps.values():
                d.discard(r)

    return ordered + [tables[t] for t in deps]  # remaining = cycles

def render_sql(tables: dict[str, Table]) -> str:
    ordered: list[Table] = topological_sort(tables)

    emitted = set()
    out = []

    for t in ordered:
        out.append(t.sql(emitted))
        emitted.add(t.name)

    return "\n\n".join(out)

# endregion

DIR = Path(__file__).parent
CONFIG = Config.model_validate(load_yaml(DIR / "config.yaml"))

# Reserved keywords in Rust, SQL and other languages
RESERVED_KEYWORDS = {"DEFAULT", "REF", "TYPE"}

# # A compiled regex pattern that strips the common URL prefix 
URL_PREFIX_PATTERN = re.compile(CONFIG.URL_PREFIX_PATTERN)

FIELDS_TO_INCLUDE = {
    name: set(fields)
    for name, fields in (CONFIG.filter.schema_fields).items()
    if fields
}

PATHS_TO_INCLUDE = set(CONFIG.filter.paths)

# English pluralisation/singularisation rules
INFLECT_ENGINE = inflect.engine()

# endregion

def deduplicate_parameters(
    path: str, 
    obj: Path | Operation, 
    url_parameters_covered: set[str]
):
           
    for i, parameter in enumerate(obj.parameters):
        
        if isinstance(parameter, Reference):
            parameter: Parameter = parameter.dereference()
            if parameter.in_ == In.path: 
                if not parameter.name:
                    raise ValueError( f"components.parameters['{key}'] is missing required field 'name'.")
                else:
                    url_parameters_covered.add(parameter.name)        
            continue
                    
        else:       
            if not parameter.name: 
                raise ValueError(
                    f"Inline parameter at index {i} in path '{path}' \
                    is missing 'name'."
                )
                
            if CONFIG.defaults and parameter.name in CONFIG.defaults:
                parameter.schema_.default = CONFIG.defaults[parameter.name]
                            
            name: str = parameter.name
            key: str = name
            
            if parameter.in_ == In.path:
                url_parameters_covered.add(name)
                
            if key in COMPONENTS_PARAMETERS:
                entry = COMPONENTS_PARAMETERS[key]
                
                if entry.in_ == parameter.in_:
                    # Same name AND same location
                    # --> Reuse existing definition
                    key = name
                
                else:
                    # Same name DIFFERENT location (`ParamLocation`)
                    # --> Create new definition (e.g. "companyId_query")
                    key = f"{name}_{parameter.in_}" 

            if key not in COMPONENTS_PARAMETERS:
                COMPONENTS_PARAMETERS[key] = parameter
                
            # Replace inline definition with JSON '$ref':
            obj.parameters[i] = Reference(**{"$ref": f"#/components/parameters/{key}"} )

def deduplicate_schema(
    schema: Schema | Reference,
    key: str, # e.g. SiteBody
    resource_name: str,
) -> Schema | Reference:
    
    schema = schema.dereference()
    
    if CONFIG.schema_aliases:
        if field_alias := CONFIG.schema_aliases.get(key):
            key = field_alias # E.G. Block : ScheduleBlock
    
    def capitalize(word: str) -> str:
        return word[:1].upper() + word[1:]

    def safe_name(field: str) -> str:
        return field + "Value" if field.upper() in RESERVED_KEYWORDS \
            else field

    properties_to_assign = {}
    fields_to_include = set()

    if key in FIELDS_TO_INCLUDE:
        fields_to_include: set[str] = FIELDS_TO_INCLUDE[key]

    # Iterate over properties {}
    if schema.properties:
        for field, subSchema in schema.properties.items():
            if fields_to_include and field not in fields_to_include:
                continue
            
            subSchema = subSchema.dereference()
            if subSchema.deprecated is True: 
                continue
            
            # Conversion to PascalCase and avoidance of reserved words:
            safeName = safe_name(field)
            words = [capitalize(w) for w in separate_into_words(safeName)]
            schemaName = "".join(words)

            # Use the raw API field name mapping
            properties_to_assign[field] = deduplicate_schema(
                subSchema,
                schemaName,
                resource_name=key
            )
    
        schema.properties = properties_to_assign

    # Iterate over "array" items
    if schema.items:
        """
        Arrays are collections (e.g. "Sites"), but the schema for each
        element should be named as a single item (e.g. "Site").
        The $ref is nested within "items" (e.g. { "type": "array", "items": { "type": "object", "properties": {} } } )
        """
        item_name = INFLECT_ENGINE.singular_noun(key) or key
        item_schema = schema.items.dereference()
        processed = deduplicate_schema(item_schema, item_name, resource_name=key)
        if isinstance(processed, Reference): schema.items = processed.dereference()   # inline the actual schema
        else: schema.items = processed

    # Iterate over "allOf", "anyOf", "oneOf"
    for variantsKey, variantsList in [
        ("allOf", schema.allOf),
        ("anyOf", schema.anyOf),
        ("oneOf", schema.oneOf),
    ]:
        if variantsList:
            newVariantsList: list[SchemaRef] = []
            
            for i, schemaVariant in enumerate(variantsList):
                if isinstance(schemaVariant, Reference): 
                    reference = schemaVariant
                    newVariantsList.append(reference)
                    continue
                
                # Recursively deduplicate:
                # - Primitives stay inline (Schema)
                # - Complex objects become $ref (Reference) 
                variantKey = f"{key}{variantsKey.capitalize()}{i}" # E.G. 'SiteVariant4'
                reference_or_primitive = deduplicate_schema(
                    schemaVariant, 
                    variantKey, 
                    resource_name=key
                )
                newVariantsList.append(reference_or_primitive)

            setattr(schema, variantsKey, newVariantsList)

    if schema.is_primitive():
        return schema # STAY INLINE #
        
    COMPONENTS_SCHEMAS.setdefault(key, schema)
    return Reference(**{"$ref": f"#/components/schemas/{key}"} )

import logging
logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

COMMON_FIELDS: dict[str, set[Tuple[str, str]]] = {}

def process_openapi() -> None:

    for path, pathObj in OPENAPI.paths.items():
        
        if CONFIG.filter.paths and \
            not DEBUG_UNFILTERED and \
                path not in CONFIG.filter.paths:
                    continue
        
        # r"^/api/v1\.0(/companies/\{companyID\}/(setup/)?(accounts/)?)?"
        # → /api/v1.0/companies/{companyID}/
        # → /api/v1.0/companies/{companyID}/setup/
        # → /api/v1.0/companies/{companyID}/accounts/
        # → /api/v1.0/companies/{companyID}/setup/accounts/
        endpoint = URL_PREFIX_PATTERN.sub("", path)
        
        # EXAMPLE:
        # → "sites/" → ["sites"]
        # → "sites/{siteID}" → ["sites", "{siteID}"]
        # → "jobs/{jobID}/notes" → ["jobs", "{jobID}", "notes"]
        endpoint_segments = [seg for seg in endpoint.strip("/").split("/") if seg]
        
        def is_parameter(s: str) -> bool:
            return s.startswith("{") and s.endswith("}")
                
        url_parameters, words = partition(endpoint_segments, is_parameter)
        url_parameters = [p[1:-1] for p in url_parameters] # Strip { and }

        def singularize(word: str) -> str:
            """Returns the singular form of word."""
            return INFLECT_ENGINE.singular_noun(word) or word

        def capitalize(word: str) -> str:
            """Capitalises the first letter of a word."""
            return word[:1].upper() + word[1:]

        resourceNameParts =  [capitalize(singularize(word)) for word in words]
        singleResourceName: str = "".join(resourceNameParts) # --- Use as a prefix for the schema key of Response and Request objects 
        COMMON_FIELDS[singleResourceName] = set() # --- Will be used to store common fields

        # URLs ending with "}" are single-item paths.
        # All others (e.g. '/sites/') are collections.
        # Collections pluralize the end word (e.g. 'JobNote' -> 'JobNotes').
        url_template = path
        is_collection: bool = not (url_template.rstrip("/").endswith("}"))
        
        if is_collection: 
            lastWord = resourceNameParts[-1]
            resourceNameParts[-1] = capitalize(INFLECT_ENGINE.plural(lastWord.lower()))
            
        resourceName: str = "".join(resourceNameParts) # --- Use as a prefix for the operationId of HTTP methods ("get", "put", etc ...)
        url_parameters_covered: set[str] = set()
 
        # Replace inline objects with references to "#/components/parameters/"
        deduplicate_parameters(path, pathObj, url_parameters_covered)

        # OpenAPI requires {placeholder}s in paths (URL templates) 
        # to have corresponding parameters with `in="path"``.
        for required in url_parameters:
            if required not in url_parameters_covered:
                raise ValueError(f"Missing 'in: path' parameter '{required}' in parameters for path '{path}'")
               
        for method, operation in [
            ("get", pathObj.get),
            ("post", pathObj.post),
            ("put", pathObj.put),
            ("delete", pathObj.delete),
            ("patch", pathObj.patch)
        ]:
            if not operation: 
                continue

            if CONFIG.filter.paths and \
                not DEBUG_UNFILTERED and \
                    method not in CONFIG.filter.paths[path]:
                        continue

            # ("get", "Sites")        → "getSites"
            # ("post", "SiteNotes")   → "postSiteNotes"
            operation.operationId = f"{method}{resourceName}"

            # Replace inline objects with references to 
            # "#/components/parameters/"
            deduplicate_parameters(path, operation, url_parameters_covered)
            
            # These could be deduplicated more!
            if operation.requestBody:
                media = operation.requestBody.content.get("application/json")
                if schema := media.schema_:
                    # The KEY in '#components/schemas'
                    key = capitalize(method) + singleResourceName
                    # Reassign to ["application/json"]["schema"]
                    media.schema_ = reference = deduplicate_schema(schema, key,  singleResourceName)
                    # Include the fields for this Schema

            # RESPONSE
            for HTTPCode, response in operation.responses.items():
                if schema := response.schema():
                    # For success responses (200/201) use the resource name as the schema name.
                    # For other codes (400, 404, 500 ...) use a more specific name that includes the operationId.
                    key = (singleResourceName if HTTPCode in ["200", "201"] else f"{operation.operationId}Response{HTTPCode}")
                    media = response.content.get("application/json")
                    if media:
                        if schema := media.schema_: 
                            reference = deduplicate_schema(schema, key, resource_name=singleResourceName)
                            if schema.items: schema.items = reference
                            else: media.schema_ = reference

    # FILTER
    if CONFIG.filter.paths and not DEBUG_UNFILTERED:
        OPENAPI.paths = {
            path: obj 
            for path, obj in OPENAPI.paths.items() 
            if path in CONFIG.filter.paths
        }
        for path, obj in OPENAPI.paths.items():
            for method in ("get","post","put","patch","delete","options","head","trace"):
                if method not in CONFIG.filter.paths[path]:
                    setattr(obj, method, None)
        
    tables = table_names()
    populate_columns(tables)
    add_config_junction_tables(tables) 
    sql = render_sql(tables)
    write_sql(sql, Path("init.sql"))

process_openapi()

data: dict[str, Any] = OPENAPI.model_dump(
    by_alias=True, 
    exclude_none=True, 
    mode="json"
)

write_yaml(
    data, 
    path=Path("openapi.yaml")
)
