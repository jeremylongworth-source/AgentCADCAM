"""Isolated synthetic approval-record lifecycle controls, not review decisions."""

import copy
import json

from router.handoff_review import review_handoff
from state.state import context_fingerprint
from tests.routing.handoff_fixture import FAMILIES, make_handoff_review, renew_test_review


def observe(handoff, state, approval, byte_inputs):
    before = copy.deepcopy((handoff, state, approval, byte_inputs))
    result = review_handoff(handoff, state, approval, **byte_inputs)
    if before != (handoff, state, approval, byte_inputs):
        raise AssertionError("consumer mutated supplied control inputs")
    return {
        "current_fingerprint": context_fingerprint(state),
        "supplied_handoff_fingerprint": handoff["context_fingerprint"],
        "supplied_approval_fingerprint": approval["context_fingerprint"],
        "returned_handoff_fingerprint": result["handoff"]["context_fingerprint"],
        "returned_approval_fingerprint": result["approval_record"]["context_fingerprint"],
        "status": result["status"], "approval_state": result["approval_state"],
        "handoff_status": result["handoff"]["status"], "blockers": result["blockers"],
        "findings": result["findings"], "validation_errors": result["validation_errors"],
        "review_required": result["review_required"], "execution_allowed": result["execution_allowed"],
    }


def replay():
    observations = {}
    for family in FAMILIES:
        handoff, state, approval, byte_inputs = make_handoff_review(family)
        cases = {"matching_test_record": observe(handoff, state, approval, byte_inputs)}

        # Change a bound review instruction, not physical machine configuration.
        state["setup"]["handoff_review"]["human_review"]["action"] = "Changed test-only reviewer action"
        cases["changed_review_stale_packet_and_record"] = observe(handoff, state, approval, byte_inputs)

        handoff["human_review"] = copy.deepcopy(state["setup"]["handoff_review"]["human_review"])
        handoff["context_fingerprint"] = context_fingerprint(state)
        approval["context_fingerprint"] = handoff["context_fingerprint"]
        cases["new_test_record_stale_verification"] = observe(handoff, state, approval, byte_inputs)

        # Test-only declarations re-bound; never a real review or approval API.
        renew_test_review(handoff, state, approval)
        cases["renewed_test_verification_and_record"] = observe(handoff, state, approval, byte_inputs)

        changed_bytes = copy.deepcopy(byte_inputs)
        key = next(iter(changed_bytes))
        if family == "cad_handoff":
            changed_bytes[key]["source/bracket.svg"] += b"\n"
        else:
            changed_bytes[key] += b"\n"
        cases["different_actual_bytes"] = observe(handoff, state, approval, changed_bytes)

        handoff.update(status="blocked", consequence_level="live_execution", blockers=["BLOCK_EXECUTION"])
        cases["live_execution"] = observe(handoff, state, approval, byte_inputs)
        observations[family] = cases
    return {"scope": "Isolated test-only lifecycle declarations; no actual approval, qualified review or manufacturing parameters",
            "factory": "tests/routing/handoff_fixture.py:make_handoff_review",
            "observations": observations}


if __name__ == "__main__":
    print(json.dumps(replay(), indent=2, sort_keys=True))
