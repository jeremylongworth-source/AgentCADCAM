"""In-memory CAD integration controls; no actual manufacturing review or approval."""

import json
from pathlib import Path

from state.state import context_fingerprint, verification_context_fingerprint
from tests.schema.test_profile_lifecycle import synthetic_review
from tests.routing.governance_fixture import declare_test_governance
from tests.routing.source_fixture import declare_test_source_review


ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "fixtures/cad/bracket"
CHECKS = ("cad_provenance", "cad_interoperability", "cad_manufacturability", "cad_drawing_pmi", "cad_handoff")


def rebind(state):
    for record in state["verification_results"]:
        if "context_binding" in record:
            record["context_binding"] = {"version": 1, "fingerprint": verification_context_fingerprint(state)}


def make_cad_review():
    state = json.loads((ROOT / "docs/evaluation/cad-runs/2026-09-17-manufacturing-intent/state.json").read_text(encoding="utf-8"))
    metadata = json.loads((FIXTURE / "metadata/revision.json").read_text(encoding="utf-8"))
    binding = json.loads((FIXTURE / "metadata/derivation.json").read_text(encoding="utf-8"))
    descriptors = [binding["source"]] + [entry["artifact"] for entry in binding["derivatives"]]
    artifacts = {a["path"]: (FIXTURE / a["path"]).read_bytes() for a in descriptors}
    state["job_id"] = metadata["job_id"]
    for key, filename in (("machine_profile", "machine"), ("material", "material")):
        state[key] = synthetic_review(json.loads((ROOT / f"fixtures/cnc/mill-bracket/contexts/{filename}.json").read_text(encoding="utf-8")))
    context = {"process_family": "cnc_milling", "material_id": state["material"]["material_id"],
               "requirements": ["Non-operational test declaration, not product acceptance criteria"],
               "drawing_pmi_basis": "Test-only controlled-alternative declaration, not complete PMI",
               "sources": [{"title": "Synthetic CAD integration declaration", "publisher": "AgentCADCAM tests",
                            "locator": "test-only:cad-context", "published_at": None, "accessed_at": "2026-09-17",
                            "scope": "Router tests only, not manufacturing context",
                            "claims": ["Synthetic record consistency control, not a qualified review."]}]}
    for source in context["sources"]:
        declare_test_source_review(source, "cad_manufacturing_context")
    state["setup"] = {"cad_handoff": {"review_profile": "cad-bracket-basic-v2", "metadata": metadata,
                                       "derivation": binding, "manufacturing_context": context}}
    state["verification_results"] = [{"check_id": key, "kind": "verification", "status": "passed",
                                      "summary": "Test-only declaration, not a real review", "evidence": [f"test-only:{key}"],
                                      "context_binding": {}} for key in CHECKS]
    declare_test_governance(state)
    rebind(state)
    request = {"process_family": "cad_handoff", "artifact_class": "handoff", "requested_action": "prepare_handoff",
               "consequence_level": "execution_adjacent"}
    approval = {"approval_id": "synthetic-cad-review", "status": "approved", "scope": ["manufacturing_handoff"],
                "context_fingerprint": context_fingerprint(state), "reviewer": "test-reviewer",
                "reviewed_at": "2026-09-17T12:00:00Z"}
    return state, request, approval, artifacts
