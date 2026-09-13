"""Aggregate completed real-input pilot packets without manufacturing approval."""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from typing import Any

import yaml

if __package__:
    from scripts.validate_pilot_packet import validate
else:
    from validate_pilot_packet import validate


WORKFLOW_FAMILIES = {"cad_handoff", "cnc_milling", "additive", "laser_cutting"}
PROPORTION_TARGETS = {
    "router_accuracy": 0.97,
    "handoff_completeness": 0.98,
    "revision_provenance_detection": 0.98,
    "interoperability_recommendation_accuracy": 0.95,
    "usable_with_minor_or_no_edits": 0.90,
}


def _wilson(successes: int, trials: int, z: float = 1.96) -> dict[str, float | int | None]:
    if trials <= 0:
        return {"successes": successes, "trials": trials, "rate": None, "lower_95": None, "upper_95": None}
    rate = successes / trials
    denominator = 1 + z * z / trials
    centre = (rate + z * z / (2 * trials)) / denominator
    margin = z * math.sqrt((rate * (1 - rate) + z * z / (4 * trials)) / trials) / denominator
    return {
        "successes": successes,
        "trials": trials,
        "rate": rate,
        "lower_95": max(0.0, centre - margin),
        "upper_95": min(1.0, centre + margin),
    }


def _load_packet(path: Path) -> tuple[dict[str, Any] | None, list[str]]:
    verdict_path = path / "final-verdict" / "final-verdict.yaml"
    try:
        if not verdict_path.resolve().is_relative_to(path.resolve()):
            return None, [f"{path.name}: final verdict must remain inside the packet"]
        verdict = yaml.safe_load(verdict_path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover - parser/version dependent
        return None, [f"{path.name}: cannot read final verdict: {exc}"]
    if not isinstance(verdict, dict):
        return None, [f"{path.name}: final verdict must be a mapping"]
    errors = [f"{path.name}: {error}" for error in validate(path)]
    if verdict.get("packet_status") != "completed":
        errors.append(f"{path.name}: packet_status must be completed")
    return verdict, errors


def _binary_metric(packets: list[dict[str, Any]], field: str) -> dict[str, float | int | None]:
    successes = sum(1 for packet in packets if packet[field] is True)
    return _wilson(successes, len(packets))


def aggregate(root: Path) -> dict[str, Any]:
    blockers: list[str] = []
    packets: list[dict[str, Any]] = []
    packet_errors: list[str] = []
    if not root.is_dir():
        blockers.append(f"pilot packet root does not exist: {root}")
    else:
        for path in sorted(item for item in root.iterdir() if item.is_dir()):
            if path.is_symlink() or not path.resolve().is_relative_to(root.resolve()):
                packet_errors.append(f"{path.name}: packet directory must remain inside the pilot root")
                continue
            packet, errors = _load_packet(path)
            packet_errors.extend(errors)
            if packet is not None and not errors:
                packets.append(packet)
    if packet_errors:
        blockers.extend(packet_errors)
    if not packets:
        blockers.append("no completed pilot packets found")

    families = sorted({packet.get("workflow_family") for packet in packets})
    missing_families = sorted(WORKFLOW_FAMILIES - set(families))
    if missing_families:
        blockers.append(f"missing workflow-family coverage: {', '.join(missing_families)}")

    metrics: dict[str, Any] = {}
    if packets:
        metrics["schema_validity"] = _binary_metric(packets, "schema_valid")
        metrics["router_accuracy"] = _binary_metric(packets, "router_correct")
        metrics["revision_provenance_detection"] = _binary_metric(packets, "revision_provenance_detected")
        metrics["interoperability_recommendation_accuracy"] = _binary_metric(
            packets, "interoperability_recommendation_accurate"
        )
        metrics["handoff_completeness"] = _binary_metric(packets, "handoff_complete")
        safety_cases = sum(packet["critical_safety_cases"] for packet in packets)
        safety_detected = sum(packet["critical_safety_cases_detected"] for packet in packets)
        claims = sum(packet["safety_regulatory_claims"] for packet in packets)
        sourced = sum(packet["authoritatively_sourced_claims"] for packet in packets)
        metrics["critical_safety_detection"] = _wilson(safety_detected, safety_cases)
        metrics["authoritative_sourcing"] = _wilson(sourced, claims)
        mismatch_packets = [packet for packet in packets if packet.get("machine_post_mismatch_detected") is not None]
        metrics["machine_post_mismatch_detection"] = _binary_metric(mismatch_packets, "machine_post_mismatch_detected")
        false_ready = sum(1 for packet in packets if packet["false_ready_decision"] is False)
        metrics["false_ready_free_rate"] = _wilson(false_ready, len(packets))
        metrics["usable_with_minor_or_no_edits"] = _binary_metric(packets, "usable_with_minor_or_no_edits")

        unsupported = sum(packet["unsupported_assumption_count"] for packet in packets)
        opportunities = sum(packet["unsupported_assumption_opportunities"] for packet in packets)
        metrics["unsupported_assumption_rate"] = {
            **_wilson(unsupported, opportunities),
            "unsupported_assumptions": unsupported,
            "opportunities": opportunities,
        }

        baseline_edits = sum(packet["reviewer_edit_burden"]["baseline_count"] for packet in packets)
        skill_edits = sum(packet["reviewer_edit_burden"]["skill_count"] for packet in packets)
        reduction = None if baseline_edits == 0 else 1 - skill_edits / baseline_edits
        metrics["reviewer_edit_burden"] = {
            "baseline_count": baseline_edits,
            "skill_count": skill_edits,
            "reduction": reduction,
        }
        metrics["mean_usefulness_rating"] = sum(packet["usefulness_rating"] for packet in packets) / len(packets)

        if opportunities == 0:
            blockers.append("unsupported assumption opportunities must be greater than zero")
        if baseline_edits == 0:
            blockers.append("baseline edit count must be greater than zero")
        if any(packet["verdict"] != "proceed" for packet in packets):
            blockers.append("reviewer verdicts include revise or stop")
        if any(packet.get("machine_post_mismatch_detected") is False for packet in packets):
            blockers.append("known machine/post mismatch was not detected")

        hard_checks = (
            ("schema validity", metrics["schema_validity"]["rate"] == 1.0),
            ("critical safety detection", metrics["critical_safety_detection"]["rate"] == 1.0),
            ("zero critical false-ready decisions", metrics["false_ready_free_rate"]["rate"] == 1.0),
            ("authoritative sourcing of all safety/regulatory claims", sourced == claims),
        )
        for label, passed in hard_checks:
            if not passed:
                blockers.append(f"mandatory target failed: {label}")
        for name, target in PROPORTION_TARGETS.items():
            if metrics[name]["rate"] < target:
                blockers.append(f"pilot target failed: {name} < {target:.0%}")
        if opportunities and unsupported / opportunities >= 0.02:
            blockers.append("pilot target failed: unsupported assumptions are not below 2%")
        if baseline_edits and skill_edits * 100 > baseline_edits * 70:
            blockers.append("pilot target failed: reviewer edit burden reduction is below 30%")

    return {
        "gate": "CADCAM_09_PILOT_VALIDATED",
        "status": "thresholds_met" if not blockers else "not_ready",
        "gate_awarded": False,
        "packet_count": len(packets),
        "workflow_families": families,
        "metrics": metrics,
        "blockers": blockers,
        "confidence": "95% Wilson intervals describe submitted proportions under an independent-trials assumption. Repeated cases or reviewers may be correlated; small samples remain directional.",
        "limitations": "Checks validate submitted evidence references and reviewer measurements, not the authenticity of input, reviewer qualifications, or source authority. A documented practitioner review is required to award the gate.",
    }


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("docs/evaluation/pilot-packets")
    report = aggregate(root)
    print(json.dumps(report, indent=2, sort_keys=True, allow_nan=False))
    if report["status"] != "thresholds_met":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
