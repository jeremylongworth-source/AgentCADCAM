"""Bounded state fingerprinting and approval invalidation utilities."""

from __future__ import annotations

import copy
import hashlib
import json
from typing import Any


INVALIDATING_FIELDS = (
    "source_artifact_hashes",
    "revision",
    "units",
    "process_family",
    "material",
    "machine_profile",
    "controller_profile",
    "setup",
    "work_coordinate_system",
    "tool_library",
    "postprocessor",
    "post_version",
    "generated_manufacturing_output",
)


def context_fingerprint(state: dict[str, Any]) -> str:
    payload = {field: state.get(field) for field in INVALIDATING_FIELDS}
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def changed_fields(previous: dict[str, Any], current: dict[str, Any]) -> list[str]:
    return [field for field in INVALIDATING_FIELDS if previous.get(field) != current.get(field)]


def invalidate_approval(previous: dict[str, Any], current: dict[str, Any], approval: dict[str, Any]) -> dict[str, Any]:
    result = copy.deepcopy(approval)
    fields = changed_fields(previous, current)
    if fields and result.get("status") == "approved":
        result["status"] = "invalidated"
        result["invalidation_reason"] = "context changed"
        result["changed_fields"] = fields
    return result
