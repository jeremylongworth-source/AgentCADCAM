"""Synthetic declarations for isolated tests; never real rights/export clearance."""


def declare_test_governance(state):
    state["ip_status"] = {
        "ownership_status": "owned", "licence_status": "permitted",
        "confidentiality": "public", "third_party_restrictions": [],
        "redistribution_authorized": True,
    }
    state["export_review_status"] = "not_required"
