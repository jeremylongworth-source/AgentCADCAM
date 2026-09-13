"""Bounded state fingerprinting and approval invalidation utilities."""

from __future__ import annotations

import copy
import hashlib
import json
from typing import Any


INVALIDATING_FIELDS = (
    "job_id",
    "source_artifact_hashes",
    "revision",
    "units",
    "process_family",
    "material",
    "machine_profile",
    "controller_profile",
    "setup",
    "workholding",
    "work_coordinate_system",
    "tool_library",
    "postprocessor",
    "post_version",
    "generated_manufacturing_output",
    "cam_system",
    "simulation_status",
    "verification_results",
    "jurisdiction",
    "ip_status",
    "export_review_status",
)
FINGERPRINT_VERSION = 2


def _canonical_json(value: Any) -> str:
    def check(item):
        if isinstance(item, dict):
            if any(not isinstance(key, str) for key in item):
                raise TypeError("job context object keys must be strings")
            for child in item.values():
                check(child)
        elif isinstance(item, list):
            for child in item:
                check(child)
        elif item is not None and type(item) not in (str, bool, int, float):
            raise TypeError("job context must contain JSON values only")
    check(value)
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def context_fingerprint(state: dict[str, Any]) -> str:
    payload = {field: state.get(field) for field in INVALIDATING_FIELDS}
    encoded = _canonical_json({"version": FINGERPRINT_VERSION, "context": payload}).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def changed_fields(previous: dict[str, Any], current: dict[str, Any]) -> list[str]:
    return [field for field in INVALIDATING_FIELDS if _canonical_json(previous.get(field)) != _canonical_json(current.get(field))]


def invalidate_approval(previous: dict[str, Any], current: dict[str, Any], approval: dict[str, Any]) -> dict[str, Any]:
    result = copy.deepcopy(approval)
    fields = changed_fields(previous, current)
    if fields and result.get("status") == "approved":
        result["status"] = "invalidated"
        result["invalidation_reason"] = "context changed"
        result["changed_fields"] = fields
    return result
