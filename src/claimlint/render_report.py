from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from .schemas import validate_claim_record


REQUIRED_OUTPUTS = {
    "claims_jsonl": "claims.jsonl",
    "claims_report": "claims_report.md",
    "remediation_tasks": "remediation_tasks.md",
    "evidence_packet": "evidence_packet.md",
    "run_manifest": "run_manifest.json",
}

DOMAIN_ORDER = [
    ("licensing_rights", "Licensing and Rights"),
    ("dataset_redistribution", "Dataset Redistribution"),
    ("artifact_distribution", "Artifact Distribution"),
    ("model_performance", "Model Performance"),
    ("generalisation_scope", "Generalisation and Scope"),
    ("technical_capability", "Technical Capability"),
    ("runtime_behavior", "Runtime Behavior"),
    ("architecture", "Architecture"),
    ("documentation_policy", "Documentation Policy"),
    ("process_traceability", "Process and Traceability"),
    ("adoption_usability", "Adoption and Usability"),
    ("other", "Other"),
]
DOMAIN_LABELS = dict(DOMAIN_ORDER)
VERDICT_ORDER = [
    "overclaimed",
    "unsupported",
    "partially_supported",
    "needs_human_review",
    "ambiguous",
    "supported",
]
LOW_QUALITY_EXTRACTIONS = {
    "heading_or_label",
    "heading_label",
    "table_header",
    "incomplete_fragment",
    "code_or_error_fragment",
    "code_or_config_fragment",
    "metric_data_point",
    "other_low_quality",
    "taxonomy_definition",
    "verdict_rule_definition",
    "schema_definition",
    "workflow_instruction",
    "runtime_instruction",
    "adapter_instruction",
}
NON_ACTIONS = {
    "no_action",
    "keep_evidence_linked",
    "ignore_low_quality_extraction",
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
    lines = ["# ClaimLint Claims Report", ""]
    lines.extend(_executive_summary(claim_records, run_manifest))
    lines.extend(_verdict_summary(claim_records, run_manifest))
    lines.extend(_domain_summary(claim_records))
    lines.extend(_priority_findings(claim_records))
    lines.extend(_high_importance_actions(claim_records))
    lines.extend(_claims_grouped_by_domain(claim_records))
    lines.extend(_suppressed_reference_records(claim_records))
    lines.extend(_full_claim_listing(claim_records))
    return "\n".join(lines) + "\n"


def _executive_summary(claim_records: list[dict], run_manifest: dict) -> list[str]:
    auditable_records = [record for record in claim_records if _is_auditable_record(record)]
    action_count = sum(1 for record in claim_records if _requires_action(record))
    high_count = sum(1 for record in auditable_records if record["claim_importance"] == "high")
    demoted_count = sum(1 for record in claim_records if not _is_auditable_record(record))
    lines = [
        "## Executive Summary",
        "",
        f"- Repository: {run_manifest['repo_path']}",
        f"- Manifest: {run_manifest['manifest_path']}",
        f"- Workflow version: {run_manifest['workflow_version']}",
        f"- Run timestamp: {run_manifest['started_at']}",
        f"- Claim count: {run_manifest['claim_count']}",
        f"- Auditable claim count: {len(auditable_records)}",
        f"- Repository claim surface status: {run_manifest['repository_claim_surface_status']}",
        f"- High-importance claims: {high_count}",
        f"- Claims requiring action: {action_count}",
        f"- Suppressed reference or low-quality records: {demoted_count}",
        "",
    ]
    if not auditable_records:
        lines.extend(
            [
                "No substantial auditable repository claims were found in the selected corpus.",
                "",
                "Some runtime/user-experience claims may require external hardware, real-world use, credentials, or domain-specific testing and are outside the current audit scope.",
                "",
            ]
        )
        return lines
    lines.extend(
        [
            "Static repository review only unless otherwise stated. Smoke tests are not metric reproduction, and external hardware/environment claims may require human review.",
            "",
            "Rights, licensing, dataset redistribution, and artifact distribution claims are separated from technical, scientific, and model-performance claims by `claim_domain`.",
            "",
        ]
    )
    return lines


def _verdict_summary(claim_records: list[dict], run_manifest: dict) -> list[str]:
    counts = Counter(record["verdict"] for record in claim_records)
    manifest_counts = run_manifest.get("verdict_counts", {})
    lines = [
        "## Verdict Summary",
        "",
        "| Verdict | Count |",
        "| --- | ---: |",
    ]
    verdicts = [verdict for verdict in VERDICT_ORDER if counts.get(verdict) or manifest_counts.get(verdict)]
    if not verdicts:
        verdicts = VERDICT_ORDER
    for verdict in verdicts:
        lines.append(f"| {verdict} | {counts.get(verdict, 0)} |")
    lines.append("")
    return lines


def _domain_summary(claim_records: list[dict]) -> list[str]:
    lines = [
        "## Domain Summary",
        "",
        "| Domain | Count | Auditable | High Importance | Requiring Action | Suppressed/Reference |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    if not claim_records:
        lines.extend(["| None | 0 | 0 | 0 | 0 | 0 |", ""])
        return lines
    for domain, label in _ordered_domains(claim_records):
        records = [record for record in claim_records if record["claim_domain"] == domain]
        auditable_count = sum(1 for record in records if _is_auditable_record(record))
        high_count = sum(
            1
            for record in records
            if _is_auditable_record(record) and record["claim_importance"] == "high"
        )
        action_count = sum(1 for record in records if _requires_action(record))
        demoted_count = sum(1 for record in records if not _is_auditable_record(record))
        lines.append(
            f"| {label} | {len(records)} | {auditable_count} | {high_count} | {action_count} | {demoted_count} |"
        )
    lines.append("")
    return lines


def _priority_findings(claim_records: list[dict]) -> list[str]:
    findings = [
        record
        for record in sorted(claim_records, key=_priority_sort_key)
        if _requires_action(record) and _is_auditable_record(record) and not _is_low_quality(record)
    ]
    lines = ["## Priority Findings", ""]
    if not findings:
        lines.extend(["No priority findings outside auditable claim-source records.", ""])
        return lines
    for record in findings[:15]:
        lines.append(_compact_claim_line(record))
        lines.append(f"  Risk: {record['risk']}")
    if len(findings) > 15:
        lines.append(f"- {len(findings) - 15} additional priority finding(s) are listed in the domain and full listings.")
    lines.append("")
    return lines


def _high_importance_actions(claim_records: list[dict]) -> list[str]:
    records = [
        record
        for record in sorted(claim_records, key=_priority_sort_key)
        if (
            record["claim_importance"] == "high"
            and _requires_action(record)
            and _is_auditable_record(record)
            and not _is_low_quality(record)
        )
    ]
    lines = [
        "## High-Importance Claims Requiring Action",
        "",
        "| Claim | Domain | Verdict | Action | Source |",
        "| --- | --- | --- | --- | --- |",
    ]
    if not records:
        lines.extend(["| None | - | - | - | - |", ""])
        return lines
    for record in records:
        lines.append(
            "| "
            + " | ".join(
                [
                    f"{record['claim_id']}: {_truncate(record['claim_text'], 90)}",
                    _domain_label(record["claim_domain"]),
                    record["verdict"],
                    record["review_action"],
                    f"{record['source_file']} ({record['source_location']})",
                ]
            )
            + " |"
        )
    lines.append("")
    return lines


def _claims_grouped_by_domain(claim_records: list[dict]) -> list[str]:
    lines = ["## Claims Grouped by Domain", ""]
    if not claim_records:
        lines.extend(["No claims to group by domain.", ""])
        return lines
    for domain, label in _ordered_domains(claim_records):
        records = [record for record in claim_records if record["claim_domain"] == domain]
        visible_records = [
            record
            for record in records
            if _is_auditable_record(record) and not _is_low_quality(record)
        ]
        demoted_count = len(records) - len(visible_records)
        lines.extend([f"### {label}", ""])
        if not visible_records:
            lines.append("No audit-ready claims in this domain.")
        else:
            for record in sorted(visible_records, key=_priority_sort_key):
                lines.append(_compact_claim_line(record))
        if demoted_count:
            lines.append(
                f"- {demoted_count} suppressed reference or low-quality record(s) in this domain are listed separately or in the Full Claim Listing."
            )
        lines.append("")
    return lines


def _suppressed_reference_records(claim_records: list[dict]) -> list[str]:
    records = [record for record in claim_records if not _is_auditable_record(record)]
    lines = ["## Suppressed Reference Records", ""]
    if not records:
        lines.extend(["No suppressed reference or low-quality records.", ""])
        return lines
    for record in sorted(records, key=_priority_sort_key):
        lines.append(
            f"- {record['claim_id']} | {record['source_role']} | {record['extraction_quality']} | "
            f"{_truncate(record['claim_text'], 140)}"
        )
    lines.append("")
    return lines


def _full_claim_listing(claim_records: list[dict]) -> list[str]:
    lines = ["## Full Claim Listing"]
    if not claim_records:
        lines.extend(["", "No claims to list.", ""])
        return lines

    for record in claim_records:
        lines.extend(
            [
                "",
                f"### {record['claim_id']}",
                "",
                f"- Claim: {record['claim_text']}",
                f"- Source: {record['source_file']} ({record['source_location']})",
                f"- Source role: {record['source_role']}",
                f"- Auditable claim: {record['is_auditable_claim']}",
                f"- Type: {record['claim_type']}",
                f"- Domain: {_domain_label(record['claim_domain'])}",
                f"- Importance: {record['claim_importance']}",
                f"- Review action: {record['review_action']}",
                f"- Extraction quality: {record['extraction_quality']}",
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
    return lines


def _remediation_tasks(claim_records: list[dict]) -> str:
    claim_records = [record for record in claim_records if _is_auditable_record(record)]
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
    claim_records = [record for record in claim_records if _is_auditable_record(record)]
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


def _ordered_domains(claim_records: list[dict]) -> list[tuple[str, str]]:
    present = {record["claim_domain"] for record in claim_records}
    ordered = [(domain, label) for domain, label in DOMAIN_ORDER if domain in present]
    known = {domain for domain, _ in DOMAIN_ORDER}
    extras = sorted(present - known)
    ordered.extend((domain, domain.replace("_", " ").title()) for domain in extras)
    return ordered


def _domain_label(domain: str) -> str:
    return DOMAIN_LABELS.get(domain, domain.replace("_", " ").title())


def _requires_action(record: dict) -> bool:
    if not _is_auditable_record(record):
        return False
    return record["review_action"] not in NON_ACTIONS


def _is_low_quality(record: dict) -> bool:
    return record["extraction_quality"] in LOW_QUALITY_EXTRACTIONS


def _is_auditable_record(record: dict) -> bool:
    return bool(
        record.get("is_auditable_claim", record.get("source_role", "claim_source") == "claim_source")
    )


def _priority_sort_key(record: dict) -> tuple[int, int, int, int, str]:
    action_rank = {
        "narrow_or_remove_claim": 0,
        "add_evidence_or_remove_claim": 1,
        "human_review_required": 2,
        "add_missing_evidence": 3,
        "clarify_claim_wording": 4,
        "keep_evidence_linked": 5,
        "no_action": 6,
        "ignore_low_quality_extraction": 7,
    }
    importance_rank = {"high": 0, "medium": 1, "low": 2}
    verdict_rank = {verdict: index for index, verdict in enumerate(VERDICT_ORDER)}
    domain_rank = {domain: index for index, (domain, _) in enumerate(DOMAIN_ORDER)}
    return (
        action_rank.get(record["review_action"], 99),
        importance_rank.get(record["claim_importance"], 99),
        verdict_rank.get(record["verdict"], 99),
        domain_rank.get(record["claim_domain"], 99),
        record["claim_id"],
    )


def _compact_claim_line(record: dict) -> str:
    return (
        f"- {record['claim_id']} | {_domain_label(record['claim_domain'])} | "
        f"{record['claim_importance']} | {record['verdict']} | {record['review_action']} | "
        f"{_truncate(record['claim_text'], 140)}"
    )


def _truncate(text: str, max_chars: int) -> str:
    compact = " ".join(text.split())
    if len(compact) <= max_chars:
        return compact
    return compact[: max_chars - 3].rstrip() + "..."


def _evidence_lines(items: list[dict]) -> list[str]:
    if not items:
        return ["- None found."]
    lines: list[str] = []
    for item in items:
        role = item.get("source_role")
        role_text = f" Source role: {role}." if role else ""
        lines.append(
            f"- {item['path']} ({item.get('location', 'unknown location')}): {item['summary']} Strength: {item['strength']}.{role_text}"
        )
    return lines


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
