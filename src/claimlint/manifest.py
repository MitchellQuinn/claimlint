from __future__ import annotations

import fnmatch
import hashlib
from pathlib import Path
from typing import Any

import yaml

from .types import InputFile, ManifestSelection


SUPPORTED_EXTENSIONS = {
    ".md",
    ".txt",
    ".py",
    ".json",
    ".yml",
    ".yaml",
    ".csv",
    ".toml",
}


class ManifestError(ValueError):
    """Raised when the input manifest is invalid for this runtime."""


def load_manifest(repo_path: str | Path, manifest_path: str | Path) -> ManifestSelection:
    repo = Path(repo_path).resolve()
    manifest = Path(manifest_path).resolve()

    if not repo.exists() or not repo.is_dir():
        raise ManifestError(f"Repository path does not exist or is not a directory: {repo}")
    if not manifest.exists() or not manifest.is_file():
        raise ManifestError(f"Manifest path does not exist or is not a file: {manifest}")

    try:
        data = yaml.safe_load(manifest.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        raise ManifestError(f"Manifest YAML could not be parsed: {exc}") from exc

    include = data.get("include")
    if not isinstance(include, list) or not include:
        raise ManifestError("Manifest must contain a non-empty include list.")

    exclude_patterns = _exclude_patterns(data.get("exclude", []))
    limits = data.get("limits") or {}
    max_file_bytes = int(limits.get("max_file_bytes", 500000))
    max_total_files = int(limits.get("max_total_files", 200))
    if max_file_bytes <= 0 or max_total_files <= 0:
        raise ManifestError("Manifest limits must be positive integers.")

    warnings: list[str] = []
    selected: dict[str, InputFile] = {}

    for entry in include:
        if not isinstance(entry, dict):
            warnings.append("Ignored include entry that is not an object.")
            continue

        role = str(entry.get("role") or "unspecified")
        candidates: list[Path] = []

        if "path" in entry:
            rel_path = str(entry["path"]).replace("\\", "/")
            path = (repo / rel_path).resolve()
            if not _is_within_repo(repo, path):
                warnings.append(f"Ignored path outside repository: {rel_path}")
                continue
            if not path.exists():
                warnings.append(f"Manifest path not found: {rel_path}")
                continue
            candidates = [path]
        elif "glob" in entry:
            pattern = str(entry["glob"])
            candidates = sorted(
                (p.resolve() for p in repo.glob(pattern) if p.is_file()),
                key=lambda p: _relative_posix(repo, p),
            )
            if not candidates:
                warnings.append(f"Manifest glob matched no files: {pattern}")
        else:
            warnings.append("Ignored include entry without path or glob.")
            continue

        for candidate in candidates:
            if not candidate.is_file() or not _is_within_repo(repo, candidate):
                continue
            rel = _relative_posix(repo, candidate)
            if _matches_any(rel, exclude_patterns):
                continue
            if candidate.suffix.lower() not in SUPPORTED_EXTENSIONS:
                warnings.append(f"Unsupported file type skipped: {rel}")
                continue
            size_bytes = candidate.stat().st_size
            if size_bytes > max_file_bytes:
                warnings.append(f"File exceeds max_file_bytes and was skipped: {rel}")
                continue
            selected.setdefault(
                rel,
                InputFile(
                    path=rel,
                    role=role,
                    size_bytes=size_bytes,
                    sha256=_sha256_file(candidate),
                ),
            )

    input_files = [selected[key] for key in sorted(selected)]
    if len(input_files) > max_total_files:
        warnings.append(
            f"Manifest selected {len(input_files)} files; truncated to max_total_files={max_total_files}."
        )
        input_files = input_files[:max_total_files]

    if not input_files:
        raise ManifestError("Manifest selected no supported input files.")

    return ManifestSelection(input_files=input_files, warnings=warnings)


def manifest_to_dict(selection: ManifestSelection) -> dict[str, Any]:
    return {
        "input_files": [input_file.__dict__ for input_file in selection.input_files],
        "manifest_warnings": list(selection.warnings),
    }


def _exclude_patterns(exclude: object) -> list[str]:
    if not isinstance(exclude, list):
        return []
    patterns: list[str] = []
    for entry in exclude:
        if isinstance(entry, dict) and "glob" in entry:
            patterns.append(str(entry["glob"]).replace("\\", "/"))
    return patterns


def _matches_any(rel_path: str, patterns: list[str]) -> bool:
    rel_path = rel_path.replace("\\", "/")
    for pattern in patterns:
        pattern = pattern.replace("\\", "/")
        if fnmatch.fnmatchcase(rel_path, pattern) or fnmatch.fnmatchcase(
            f"./{rel_path}", pattern
        ):
            return True
    return False


def _relative_posix(repo: Path, path: Path) -> str:
    return path.resolve().relative_to(repo.resolve()).as_posix()


def _is_within_repo(repo: Path, path: Path) -> bool:
    try:
        path.resolve().relative_to(repo.resolve())
    except ValueError:
        return False
    return True


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()

