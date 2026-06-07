from pathlib import Path

from claimlint.ingest_markdown import ingest_files
from claimlint.manifest import load_manifest


FIXTURE = Path(__file__).parent / "fixtures" / "small_repo"


def test_manifest_loads_fixture_files():
    selection = load_manifest(FIXTURE, FIXTURE / "input_manifest.yml")
    paths = [input_file.path for input_file in selection.input_files]
    assert "README.md" in paths
    assert "docs/technical_notes.md" in paths
    assert "metrics/validation_metrics.json" in paths


def test_excludes_are_respected(tmp_path):
    excluded = FIXTURE / "runs"
    excluded.mkdir(exist_ok=True)
    ignored = excluded / "ignored.md"
    ignored.write_text("The ignored file supports nothing.", encoding="utf-8")
    try:
        selection = load_manifest(FIXTURE, FIXTURE / "input_manifest.yml")
        assert "runs/ignored.md" not in [input_file.path for input_file in selection.input_files]
    finally:
        ignored.unlink(missing_ok=True)
        excluded.rmdir()


def test_markdown_chunking_preserves_path_and_line_numbers():
    selection = load_manifest(FIXTURE, FIXTURE / "input_manifest.yml")
    chunks = ingest_files(FIXTURE, selection.input_files)
    readme_chunks = [chunk for chunk in chunks if chunk.path == "README.md"]
    assert readme_chunks
    assert all(chunk.start_line >= 1 for chunk in readme_chunks)
    assert any("Results" in chunk.heading_path for chunk in readme_chunks)

