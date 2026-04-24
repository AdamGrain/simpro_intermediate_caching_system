from __future__ import annotations

import sys
from pathlib import Path

from dotenv import load_dotenv

from utils.logging import setup_logging
from utils.serialize import load_json, write_yaml
from utils.config import (
    NO_EXAMPLES,
    NO_TAGS,
    NO_SQL,
    OUTPUT_OPENAPI,
    OUTPUT_SQL,
    SOURCE_OPENAPI,
    SERVER_URL,
)
from utils.processor import (
    _strip_keys,
    deduplicate_identical_schemas,
    enrich_list_schemas,
    process_paths,
    prune_unused_examples,
    prune_unused_parameters,
    prune_unused_schemas,
    trim_spec,
    validate,
)
from utils.sql import generate_sql, setup_junction_yaml


def main() -> None:
    try:
        load_dotenv()
        setup_logging(Path(__file__).parent / "logs")

        # ── Load ─────────────────────────────────────────────
        openapi = load_json(SOURCE_OPENAPI)
        components = openapi.setdefault("components", {})
        components.setdefault("parameters", {})
        components.setdefault("schemas", {})
        components.setdefault("examples", {})

        paths = openapi["paths"]

        # ── Process ──────────────────────────────────────────
        process_paths(
            paths,
            components["parameters"],
            components["schemas"],
            components["examples"],
        )

        print(f"\nList enrichment: {enrich_list_schemas(paths, components['schemas'])}")

        errors = validate(paths, components["parameters"])
        print("Validation:", "OK" if errors == 0 else f"{errors} issue(s)")
        if errors:
            sys.exit(1)

        merged = deduplicate_identical_schemas(openapi)
        if merged:
            print(f"Schema dedup: {merged}")

        pruned = prune_unused_schemas(openapi)
        if pruned:
            print(f"Pruned schemas: {pruned}")

        if SERVER_URL:
            openapi["servers"] = [{"url": SERVER_URL}]

        if NO_EXAMPLES:
            _strip_keys(openapi, "example", "examples")

        if NO_TAGS:
            _strip_keys(openapi, "tags")

        # ── Write canonical ───────────────────────────────────
        write_yaml(openapi, OUTPUT_OPENAPI)
        print(f"Wrote canonical → {OUTPUT_OPENAPI}")

        # ── Trim (optional) ───────────────────────────────────
        trimmed = trim_spec(openapi)
        active = trimmed if trimmed is not None else openapi

        if trimmed:
            pruned = (
                prune_unused_schemas(trimmed)
                + prune_unused_parameters(trimmed)
                + prune_unused_examples(trimmed)
            )
            if pruned:
                print(f"Trim prune: {pruned}")

            write_yaml(trimmed, OUTPUT_OPENAPI)
            print("Wrote trimmed")

        # ── SQL ──────────────────────────────────────────────
        if not NO_SQL:
            setup_junction_yaml(active)
            sql = generate_sql(active)
            OUTPUT_SQL.write_text(sql, encoding="utf-8")

            print(
                f"{len(active.get('components', {}).get('schemas', {}))} schemas → "
                f"{sql.count('CREATE TABLE')} tables "
                f"({sql.count('REFERENCES')} FKs)"
            )
            print(f"Wrote {OUTPUT_SQL}")

    except Exception as exc:
        print(f"Pipeline error: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()