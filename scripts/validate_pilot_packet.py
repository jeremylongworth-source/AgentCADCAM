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


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    for directory in REQUIRED_DIRS:
        if not (root / directory).is_dir():
            errors.append(f"missing pilot packet directory: {directory}")
    verdict_path = root / "final-verdict" / "final-verdict.yaml"
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
        for field in REQUIRED_FIELDS:
            if field not in verdict:
                errors.append(f"final verdict missing field: {field}")
        if verdict.get("packet_status") != "template":
            if verdict.get("consent_recorded") is not True:
                errors.append("pilot consent must be recorded")
            if verdict.get("sanitized") is not True:
                errors.append("pilot packet must be sanitized")
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
