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
    assert all(input_file.source_role == "claim_source" for input_file in selection.input_files)
    assert all(input_file.extract_claims for input_file in selection.input_files)
    assert all(input_file.use_as_evidence for input_file in selection.input_files)


def test_excludes_are_respected(tmp_path):
    excluded = FIXTURE / "output"
    excluded.mkdir(exist_ok=True)
    ignored = excluded / "ignored.md"
    ignored.write_text("The ignored file supports nothing.", encoding="utf-8")
    try:
        selection = load_manifest(FIXTURE, FIXTURE / "input_manifest.yml")
        assert "output/ignored.md" not in [input_file.path for input_file in selection.input_files]
    finally:
        ignored.unlink(missing_ok=True)
        excluded.rmdir()


def test_markdown_chunking_preserves_path_and_line_numbers():
    selection = load_manifest(FIXTURE, FIXTURE / "input_manifest.yml")
    chunks = ingest_files(FIXTURE, selection.input_files)
    readme_chunks = [chunk for chunk in chunks if chunk.path == "README.md"]
    assert readme_chunks
    assert all(chunk.start_line >= 1 for chunk in readme_chunks)
    assert all(chunk.source_role == "claim_source" for chunk in readme_chunks)
    assert any("Results" in chunk.heading_path for chunk in readme_chunks)


def test_reference_source_roles_are_inferred_inside_broad_globs(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "docs").mkdir()
    (repo / "schemas").mkdir()
    (repo / "workflows").mkdir()

    files = {
        "README.md": "# Project\n\nThe tool supports trace capture.\n",
        "docs/architecture.md": "# Architecture\n\nThe implementation has separate layers.\n",
        "docs/claim_taxonomy.md": "# Taxonomy\n\n`licensing_rights`: license statements.\n",
        "docs/verdict_rules.md": "# Verdict Rules\n\nUse when evidence is missing.\n",
        "docs/manifest_contract.md": "# Manifest Contract\n\nThe manifest selects inputs.\n",
        "schemas/claim_record.schema.json": '{"type": "object"}\n',
        "workflows/claim_audit.yml": "id: claimlint.claim-audit\n",
    }
    for rel_path, text in files.items():
        path = repo / rel_path
        path.write_text(text, encoding="utf-8")

    manifest = repo / "input_manifest.yml"
    manifest.write_text(
        """
version: 0.1
include:
  - path: README.md
    role: primary_readme
  - glob: docs/**/*.md
    role: documentation
    source_role: claim_source
    extract_claims: true
    use_as_evidence: true
  - glob: schemas/**/*.json
    role: documentation
    source_role: claim_source
    extract_claims: true
    use_as_evidence: true
  - glob: workflows/**/*.yml
    role: documentation
    source_role: claim_source
    extract_claims: true
    use_as_evidence: true
exclude: []
limits:
  max_file_bytes: 500000
  max_total_files: 50
""".lstrip(),
        encoding="utf-8",
    )

    selection = load_manifest(repo, manifest)
    by_path = {input_file.path: input_file for input_file in selection.input_files}

    assert by_path["docs/architecture.md"].source_role == "claim_source"
    assert by_path["docs/architecture.md"].extract_claims is True
    assert by_path["docs/claim_taxonomy.md"].source_role == "reference_only"
    assert by_path["docs/claim_taxonomy.md"].extract_claims is False
    assert by_path["docs/verdict_rules.md"].source_role == "reference_only"
    assert by_path["docs/verdict_rules.md"].extract_claims is False
    assert by_path["docs/manifest_contract.md"].source_role == "runtime_contract"
    assert by_path["docs/manifest_contract.md"].extract_claims is False
    assert by_path["schemas/claim_record.schema.json"].source_role == "schema_reference"
    assert by_path["schemas/claim_record.schema.json"].extract_claims is False
    assert by_path["workflows/claim_audit.yml"].source_role == "workflow_contract"
    assert by_path["workflows/claim_audit.yml"].extract_claims is False
    assert all(input_file.use_as_evidence for input_file in by_path.values())
