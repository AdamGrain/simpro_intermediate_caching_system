from __future__ import annotations
import re
from pathlib import Path
from typing import Any
from utils.serialize import load_yaml

MAIN_DIR = Path(__file__).parent.parent

CONFIG_FILE = MAIN_DIR / "config.yaml"

try: _CFG = load_yaml(CONFIG_FILE)
except Exception as exc: raise RuntimeError(f"Failed to load config.yaml: {CONFIG_FILE}") from exc

HTTP_METHODS = {"get", "post", "put", "patch", "delete"}

SERVER_URL = _CFG.get("server_url", "/")

SOURCE_OPENAPI = MAIN_DIR / "openapi.json"

OUTPUT_OPENAPI = MAIN_DIR / "output" / "openapi.yaml"

OUTPUT_SQL = MAIN_DIR / "output" / "init.sql"

# ──────────────────────────────────────────────────────────────────────────────
# FLAGS
# ──────────────────────────────────────────────────────────────────────────────

def _flag(key: str) -> bool:
    return str(_CFG.get(key, False)).lower() in ("1", "true", "yes", "on")

NO_EXAMPLES = _flag("no_examples")
NO_TAGS = _flag("no_tags")
NO_SQL = _flag("no_sql")
CLEAN = _flag("clean")

# ──────────────────────────────────────────────────────────────────────────────
# PROCESSING CONFIGURATION
# ──────────────────────────────────────────────────────────────────────────────

URL_PREFIX_PATTERN = re.compile(_CFG.get("URL_PREFIX_PATTERN", r"(?!)"))
TABLE_NAMES = _CFG.get("table_name", {})
JUNCTION_TABLES = _CFG.get("junction_tables", {})
FORCE_TABLES = set(_CFG.get("force_tables", []))
PARAM_DEFAULTS = _CFG.get("defaults", {})

filter_cfg = _CFG.get("filter", {})

FILTER_PATHS = {
    path: {m.lower() for m in methods}
    for path, methods in (filter_cfg.get("paths") or {}).items()
} or None


FILTER_RESPONSE_FIELDS = {
    name: set(fields)
    for name, fields in (filter_cfg.get("response_objects") or {}).items()
    if fields
} or None


EXCLUDE_COLUMNS = {
    k: set(v)
    for k, v in (filter_cfg.get("exclude_from_database_columns") or {}).items()
    if v
}