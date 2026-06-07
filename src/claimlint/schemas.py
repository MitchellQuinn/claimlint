from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError


class SchemaValidationError(ValueError):
    """Raised when generated output fails JSON Schema validation."""


def validate_claim_record(record: dict[str, Any]) -> None:
    _validate("claim_record.schema.json", record)


def validate_run_manifest(record: dict[str, Any]) -> None:
    _validate("run_manifest.schema.json", record)


def validate_audit_summary(record: dict[str, Any]) -> None:
    _validate("audit_summary.schema.json", record)


@lru_cache(maxsize=None)
def load_schema(schema_name: str) -> dict[str, Any]:
    path = _schema_dir() / schema_name
    return json.loads(path.read_text(encoding="utf-8"))


def _validate(schema_name: str, record: dict[str, Any]) -> None:
    schema = load_schema(schema_name)
    validator = Draft202012Validator(schema)
    try:
        validator.validate(record)
    except ValidationError as exc:
        path = ".".join(str(part) for part in exc.absolute_path) or "<root>"
        raise SchemaValidationError(f"{schema_name} validation failed at {path}: {exc.message}") from exc


def _schema_dir() -> Path:
    return Path(__file__).resolve().parents[2] / "schemas"

