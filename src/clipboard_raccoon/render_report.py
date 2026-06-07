from __future__ import annotations

import json
from pathlib import Path

from .schemas import validate_claim_record


REQUIRED_OUTPUTS = {
    "claims_jsonl": "claims.jsonl",
    "claims_report": "claims_report.md",
    "remediation_tasks": "remediation_tasks.md",
    "evidence_packet": "evidence_packet.md",
    "run_manifest": "run_manifest.json",
}


def render_outputs(
    out_dir: str | Path,
    claim_records: list[dict],
    run_manifest: dict,
) -> dict[str, Path]:
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    outputs = {key: out_path / filename for key, filename in REQUIRED_OUTPUTS.items()}

    _write_claims_jsonl(outputs["claims_jsonl"], claim_records)
    outputs["claims_report"].write_text(_claims_report(claim_records, run_manifest), encoding="utf-8")
    outputs["remediation_tasks"].write_text(_remediation_tasks(claim_records), encoding="utf-8")
    outputs["evidence_packet"].write_text(_evidence_packet(claim_records), encoding="utf-8")
    outputs["run_manifest"].write_text(
        json.dumps(run_manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return outputs


def _write_claims_jsonl(path: Path, claim_records: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for record in claim_records:
            validate_claim_record(record)
            handle.write(json.dumps(record, sort_keys=True) + "\n")


def _claims_report(claim_records: list[dict], run_manifest: dict) -> str:
    lines = [
        "# ClaimLint Claims Report",
        "",
        "## Summary",
        f"- Repository: {run_manifest['repo_path']}",
        f"- Manifest: {run_manifest['manifest_path']}",
        f"- Workflow version: {run_manifest['workflow_version']}",
        f"- Run timestamp: {run_manifest['started_at']}",
        f"- Claim count: {run_manifest['claim_count']}",
        f"- Repository claim surface status: {run_manifest['repository_claim_surface_status']}",
        f"- Verdict counts: {json.dumps(run_manifest['verdict_counts'], sort_keys=True)}",
        "",
        "## Important caveats",
        "- Static repo review only unless otherwise stated.",
        "- Smoke tests are not metric reproduction.",
        "- External hardware/environment claims may require human review.",
        "",
        "## Claims",
    ]
    if not claim_records:
        lines.extend(
            [
                "",
                "No substantial auditable repository claims were found in the selected corpus.",
                "",
                "Some runtime/user-experience claims may require external hardware, real-world use, credentials, or domain-specific testing and are outside the current audit scope.",
            ]
        )
        return "\n".join(lines) + "\n"

    for record in claim_records:
        lines.extend(
            [
                "",
                f"### {record['claim_id']}",
                "",
                f"- Claim: {record['claim_text']}",
                f"- Source: {record['source_file']} ({record['source_location']})",
                f"- Type: {record['claim_type']}",
                f"- Claim surface status: {record['claim_surface_status']}",
                f"- Verification mode: {record['verification_mode']}",
                f"- Verdict: {record['verdict']}",
                f"- Confidence: {record['confidence']}",
                "",
                "Found evidence:",
            ]
        )
        lines.extend(_evidence_lines(record["found_evidence"]))
        lines.append("")
        lines.append("Missing evidence:")
        lines.extend(_missing_lines(record["missing_evidence"]))
        lines.append("")
        lines.append("Artifact gaps:")
        lines.extend(_gap_lines(record["artifact_gaps"]))
        lines.append("")
        lines.append(f"Risk: {record['risk']}")
        lines.append("")
        lines.append("Recommended remediation:")
        lines.extend(_string_lines(record["recommended_remediation"]))
    return "\n".join(lines) + "\n"


def _remediation_tasks(claim_records: list[dict]) -> str:
    groups = ["unsupported", "overclaimed", "partially_supported", "needs_human_review", "ambiguous", "supported"]
    lines = ["# ClaimLint Remediation Tasks", ""]
    if not claim_records:
        lines.extend(["No remediation tasks were generated because no auditable claims were found.", ""])
        return "\n".join(lines)
    for group in groups:
        group_records = [record for record in claim_records if record["verdict"] == group]
        if not group_records:
            continue
        lines.extend([f"## {group}", ""])
        for record in group_records:
            issue = record["risk"]
            change = "; ".join(record["recommended_remediation"]) or "Review claim wording and evidence."
            related = _related_gap_text(record)
            lines.extend(
                [
                    f"- {record['claim_id']}: {issue}",
                    f"  Recommended change: {change}",
                    f"  Related evidence/artifact gap: {related}",
                ]
            )
        lines.append("")
    return "\n".join(lines)


def _evidence_packet(claim_records: list[dict]) -> str:
    lines = ["# ClaimLint Evidence Packet", ""]
    if not claim_records:
        lines.extend(
            [
                "No substantial auditable repository claims were found in the selected corpus.",
                "",
                "Suggested README wording improvement: keep claims scoped to documented repository artifacts and call out any external runtime or domain-specific validation requirements.",
                "",
            ]
        )
        return "\n".join(lines)

    sections = [
        ("Safely supported claims", {"supported"}),
        ("Partially supported claims with caveats", {"partially_supported"}),
        ("Claims requiring human/external review", {"needs_human_review"}),
        ("Claims not supported by selected corpus", {"unsupported", "ambiguous"}),
        ("Overclaimed wording", {"overclaimed"}),
    ]
    for title, verdicts in sections:
        lines.extend([f"## {title}", ""])
        records = [record for record in claim_records if record["verdict"] in verdicts]
        if not records:
            lines.extend(["None.", ""])
            continue
        for record in records:
            lines.append(f"- {record['claim_id']}: {record['claim_text']}")
            lines.append(f"  Verdict: {record['verdict']}. Risk: {record['risk']}")
        lines.append("")

    lines.extend(
        [
            "## Suggested README wording improvements",
            "",
            "- Link claims directly to selected evidence artifacts where possible.",
            "- Add caveats when metrics depend on missing checkpoints, protocols, or external environments.",
            "- Remove or narrow claims that go beyond selected repository evidence.",
            "",
        ]
    )
    return "\n".join(lines)


def _evidence_lines(items: list[dict]) -> list[str]:
    if not items:
        return ["- None found."]
    return [
        f"- {item['path']} ({item.get('location', 'unknown location')}): {item['summary']} Strength: {item['strength']}."
        for item in items
    ]


def _missing_lines(items: list[dict]) -> list[str]:
    if not items:
        return ["- None identified."]
    return [
        f"- {item['requirement']}: {item['reason_missing']} Suggested fix: {item.get('suggested_fix', 'Add evidence.')}"
        for item in items
    ]


def _gap_lines(items: list[dict]) -> list[str]:
    if not items:
        return ["- None identified."]
    return [f"- {item['artifact_type']}: {item['description']} Impact: {item['impact']}" for item in items]


def _string_lines(items: list[str]) -> list[str]:
    if not items:
        return ["- None."]
    return [f"- {item}" for item in items]


def _related_gap_text(record: dict) -> str:
    missing = [item["requirement"] for item in record["missing_evidence"]]
    gaps = [item["artifact_type"] for item in record["artifact_gaps"]]
    related = missing + gaps
    return ", ".join(related) if related else "None identified"

