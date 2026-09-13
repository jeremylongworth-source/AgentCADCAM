"""Validate the structure and minimum metadata of a pilot packet."""

from __future__ import annotations

import sys
from pathlib import Path

import yaml


REQUIRED_DIRS = (
    "input",
    "baseline-output",
    "skill-output",
    "reviewer-findings",
    "required-edits",
    "safety-findings",
    "final-verdict",
)
REQUIRED_FIELDS = (
    "workflow_family",
    "participant_role",
    "qualified_reviewer",
    "consent_recorded",
    "sanitized",
    "false_ready_decision",
    "safety_findings",
    "required_edits",
    "verdict",
)
BOOLEAN_MEASURES = (
    "schema_valid",
    "router_correct",
    "revision_provenance_detected",
    "interoperability_recommendation_accurate",
    "handoff_complete",
    "false_ready_decision",
    "usable_with_minor_or_no_edits",
)
COUNT_MEASURES = (
    "unsupported_assumption_count",
    "unsupported_assumption_opportunities",
    "critical_safety_cases",
    "critical_safety_cases_detected",
    "safety_regulatory_claims",
    "authoritatively_sourced_claims",
)


def _is_nonnegative_int(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    for directory in REQUIRED_DIRS:
        if not (root / directory).is_dir():
            errors.append(f"missing pilot packet directory: {directory}")
    verdict_path = root / "final-verdict" / "final-verdict.yaml"
    if not verdict_path.resolve().is_relative_to(root.resolve()):
        errors.append("final verdict must remain inside the packet")
        return errors
    if not verdict_path.is_file():
        errors.append("missing final-verdict/final-verdict.yaml")
        return errors
    try:
        verdict = yaml.safe_load(verdict_path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover - parser/version dependent
        errors.append(f"invalid final-verdict.yaml: {exc}")
        return errors
    if not isinstance(verdict, dict):
        errors.append("final verdict must be a mapping")
    else:
        if verdict.get("packet_status") not in ("template", "draft", "completed"):
            errors.append("packet_status must be template, draft, or completed")
        for field in REQUIRED_FIELDS:
            if field not in verdict:
                errors.append(f"final verdict missing field: {field}")
        if verdict.get("packet_status") != "template":
            if verdict.get("consent_recorded") is not True:
                errors.append("pilot consent must be recorded")
            if verdict.get("sanitized") is not True:
                errors.append("pilot packet must be sanitized")
        if verdict.get("packet_status") == "completed":
            if verdict.get("workflow_family") not in ("cad_handoff", "cnc_milling", "additive", "laser_cutting"):
                errors.append("completed packet has an invalid workflow_family")
            if not isinstance(verdict.get("participant_role"), str) or not verdict.get("participant_role", "").strip():
                errors.append("completed packet requires participant_role")
            if verdict.get("qualified_reviewer") is not True:
                errors.append("completed packet requires a qualified reviewer")
            for field in ("reviewer_id", "reviewer_experience"):
                if not isinstance(verdict.get(field), str) or not verdict[field].strip():
                    errors.append(f"completed packet requires non-empty {field}")
            if verdict.get("input_origin") not in ("real", "sanitized_real"):
                errors.append("completed pilot packet requires real or sanitized_real input_origin")
            for field in ("safety_findings", "required_edits"):
                if not isinstance(verdict.get(field), list):
                    errors.append(f"{field} must be a list")
            for field in BOOLEAN_MEASURES:
                if not isinstance(verdict.get(field), bool):
                    errors.append(f"completed packet measure must be boolean: {field}")
            for field in COUNT_MEASURES:
                if not _is_nonnegative_int(verdict.get(field)):
                    errors.append(f"completed packet measure must be a non-negative integer: {field}")
            unsupported = verdict.get("unsupported_assumption_count")
            opportunities = verdict.get("unsupported_assumption_opportunities")
            if _is_nonnegative_int(unsupported) and _is_nonnegative_int(opportunities) and unsupported > opportunities:
                errors.append("unsupported assumption count cannot exceed opportunities")
            for numerator, denominator in (
                ("critical_safety_cases_detected", "critical_safety_cases"),
                ("authoritatively_sourced_claims", "safety_regulatory_claims"),
            ):
                count, total = verdict.get(numerator), verdict.get(denominator)
                if _is_nonnegative_int(count) and _is_nonnegative_int(total) and count > total:
                    errors.append(f"{numerator} cannot exceed {denominator}")
            mismatch = verdict.get("machine_post_mismatch_detected")
            if verdict.get("workflow_family") == "cnc_milling" and not isinstance(mismatch, bool):
                errors.append("CNC packet requires boolean machine_post_mismatch_detected")
            elif mismatch is not None and not isinstance(mismatch, bool):
                errors.append("machine_post_mismatch_detected must be boolean or null")
            burden = verdict.get("reviewer_edit_burden")
            if not isinstance(burden, dict):
                errors.append("completed packet requires reviewer_edit_burden mapping")
            else:
                for field in ("baseline_count", "skill_count"):
                    if not _is_nonnegative_int(burden.get(field)):
                        errors.append(f"reviewer_edit_burden requires non-negative integer: {field}")
            usefulness = verdict.get("usefulness_rating")
            if not isinstance(usefulness, int) or isinstance(usefulness, bool) or not 1 <= usefulness <= 5:
                errors.append("completed packet usefulness_rating must be an integer from 1 to 5")
            if verdict.get("verdict") not in ("proceed", "revise", "stop"):
                errors.append("completed packet verdict must be proceed, revise, or stop")
            evidence = verdict.get("evidence")
            if not isinstance(evidence, dict):
                errors.append("completed packet requires an evidence mapping")
            else:
                for directory in REQUIRED_DIRS[:-1]:
                    refs = evidence.get(directory)
                    if not isinstance(refs, list) or not refs:
                        errors.append(f"evidence requires at least one file for {directory}")
                        continue
                    for ref in refs:
                        if not isinstance(ref, str) or not ref.strip():
                            errors.append(f"invalid evidence path for {directory}")
                            continue
                        try:
                            relative = Path(ref)
                            resolved = (root / relative).resolve()
                            # Reject absolute paths, traversal, and links outside the packet/category.
                            if relative.is_absolute() or ".." in relative.parts or not resolved.is_relative_to(root.resolve() / directory):
                                raise ValueError("evidence must remain in its packet directory")
                            if not resolved.is_file() or resolved.stat().st_size == 0:
                                raise ValueError("evidence file is missing or empty")
                        except (OSError, ValueError, RuntimeError) as exc:
                            errors.append(f"invalid evidence {ref!r}: {exc}")
    return errors


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("docs/evaluation/pilot-packet-template")
    errors = validate(root)
    if errors:
        print("PILOT PACKET VALIDATION FAILED")
        for error in errors:
            print(f"- {error}")
        return 1
    print("PILOT PACKET VALIDATION PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
