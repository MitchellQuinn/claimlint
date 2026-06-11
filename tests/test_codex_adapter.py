import json
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
CODEX_ADAPTER = ROOT / "adapters" / "codex"
REQUIRED_CONTRACT_REFERENCES = [
    "workflows/claim_audit.yml",
    "docs/runtime_contract.md",
    "schemas/claim_record.schema.json",
]


def test_codex_adapter_docs_point_to_shared_contracts():
    readme = (CODEX_ADAPTER / "README.md").read_text(encoding="utf-8")
    skill = (ROOT / "skills" / "claimlint" / "SKILL.md").read_text(encoding="utf-8")

    for reference in REQUIRED_CONTRACT_REFERENCES:
        assert reference in readme
        assert reference in skill

    assert "claimlint audit --repo" in readme
    assert "claimlint audit-remote" in readme
    assert "claimlint audit-remote" in skill
    assert "Do not pass `--out`" in readme
    assert "Do not pass `--out`" in skill


def test_codex_install_scripts_install_repo_scoped_skill():
    shell_script = (CODEX_ADAPTER / "install.sh").read_text(encoding="utf-8")
    powershell_script = (CODEX_ADAPTER / "install.ps1").read_text(encoding="utf-8")

    for script in (shell_script, powershell_script):
        assert "skills/claimlint" in script.replace("\\", "/")
        assert ".agents/skills/claimlint" in script.replace("\\", "/")


def test_codex_plugin_packages_same_claimlint_skill():
    root_skill = (ROOT / "skills" / "claimlint" / "SKILL.md").read_text(encoding="utf-8")
    plugin_skill = (
        CODEX_ADAPTER / "plugin" / "claimlint" / "skills" / "claimlint" / "SKILL.md"
    ).read_text(encoding="utf-8")
    assert plugin_skill == root_skill


def test_codex_plugin_manifest_is_thin_adapter_package():
    manifest_path = CODEX_ADAPTER / "plugin" / "claimlint" / ".codex-plugin" / "plugin.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    assert manifest["name"] == "claimlint"
    assert manifest["version"] == "0.1.0"
    assert manifest["skills"] == "./skills/"
    assert "apps" not in manifest
    assert "mcpServers" not in manifest
    assert "hooks" not in manifest
    assert "workflow" not in manifest
    assert "cli" not in manifest
    assert "ClaimLint" in manifest["interface"]["displayName"]


def test_codex_verification_docs_keep_out_default_contract():
    verification = (CODEX_ADAPTER / "VERIFY.md").read_text(encoding="utf-8")

    assert "claimlint audit --repo tests/fixtures/small_repo" in verification
    assert "claimlint audit-remote" in verification
    assert "Do not pass --out" in verification
    for filename in (
        "claims.jsonl",
        "claims_report.md",
        "remediation_tasks.md",
        "evidence_packet.md",
        "run_manifest.json",
    ):
        assert filename in verification


def test_codex_adapter_status_remains_untested_until_end_to_end_run():
    status = yaml.safe_load((ROOT / "adapters" / "status.yml").read_text(encoding="utf-8"))

    assert status["codex"]["status"] == "untested"
    assert "end-to-end Codex execution" in status["codex"]["notes"]
