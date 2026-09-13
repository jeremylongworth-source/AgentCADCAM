"""Check declared CNC handoff context completeness, not physical machine safety."""

from __future__ import annotations

import math


def _text(value):
    return isinstance(value, str) and bool(value.strip())


def _positive(value):
    return (type(value) is int and value > 0) or (
        type(value) is float and math.isfinite(value) and value > 0
    )


def _units(value):
    return "in" if value in ("in", "inch") else "mm" if value == "mm" else None


def check_cnc_context(state, validate):
    """Return blockers/findings; validate is the caller's local-schema checker."""
    blockers = set()
    findings = []

    def missing(message, blocker="MISSING_CONTEXT"):
        blockers.add(blocker)
        findings.append(message)

    machine = state.get("machine_profile") or {}
    controller = state.get("controller_profile") or {}
    units = _units(state.get("units"))
    supported_units = controller.get("supported_units")
    if (
        units is None
        or not isinstance(supported_units, list)
        or units not in [_units(value) for value in supported_units]
    ):
        missing("job units are missing or unsupported by the controller")

    setup = state.get("setup")
    if not isinstance(setup, dict) or not validate(setup, "setup.schema.json", "setup"):
        missing("CNC setup context is missing or invalid")
    else:
        stock = setup.get("stock", {})
        if (
            not isinstance(stock, dict)
            or _units(stock.get("units")) != units
            or not all(_positive(stock.get(axis)) for axis in ("x", "y", "z"))
        ):
            missing("stock dimensions/units are missing or conflict with the job")
        if not setup.get("orientation"):
            missing("setup orientation is unresolved")
        root_workholding = state.get("workholding")
        setup_workholding = setup.get("workholding")
        workholding = root_workholding if root_workholding is not None else setup_workholding
        if (
            not isinstance(workholding, dict)
            or not _text(workholding.get("type"))
            or workholding.get("clamps_clear") is not True
        ):
            missing("workholding identity or clamp-clearance review is unresolved")
        if isinstance(root_workholding, dict) and isinstance(setup_workholding, dict):
            if any(
                root_workholding[key] != setup_workholding[key]
                or type(root_workholding[key]) is not type(setup_workholding[key])
                for key in root_workholding.keys() & setup_workholding.keys()
            ):
                missing("root and setup workholding declarations conflict")
        if setup.get("wcs_status") != "verified":
            missing("setup WCS has not been verified")

    wcs = state.get("work_coordinate_system")
    modes = controller.get("modes_and_offsets")
    supported_wcs = modes.get("wcs") if isinstance(modes, dict) else None
    if (
        not isinstance(supported_wcs, list)
        or not isinstance(wcs, dict)
        or wcs.get("status") != "verified"
        or not _text(wcs.get("code"))
        or wcs["code"] not in supported_wcs
    ):
        missing("explicit verified WCS is missing or unsupported by the controller")

    library = state.get("tool_library")
    tools = library.get("tools") if isinstance(library, dict) else None
    if not isinstance(tools, list) or not tools:
        missing("CNC tooling context requires a nonempty tools list")
    else:
        ids, numbers = set(), set()
        for index, tool in enumerate(tools):
            if not isinstance(tool, dict) or not validate(tool, "tool.schema.json", f"tool_library/tools/{index}"):
                missing("a tool profile is invalid")
                continue
            number = tool.get("tool_number")
            if type(number) is not int or number < 0 or number in numbers or tool["tool_id"] in ids:
                missing("tool IDs/numbers are missing, invalid, or duplicated")
            else:
                numbers.add(number)
                ids.add(tool["tool_id"])
            geometry = tool.get("geometry")
            if not isinstance(geometry, dict) or not _text(geometry.get("type")) or not _positive(geometry.get("diameter")):
                missing("tool geometry is unresolved")
            if not _text(tool.get("holder")) or not _positive(tool.get("reach")) or tool.get("availability") != "available":
                missing("tool holder, reach, or availability is unresolved")

    post = state.get("postprocessor")
    if not isinstance(post, dict) or not validate(post, "post.schema.json", "postprocessor"):
        missing("postprocessor context is missing or invalid", "SOURCE_VERIFICATION_REQUIRED")
    else:
        for field, expected in (
            ("machine_id", machine.get("machine_id")),
            ("controller_id", controller.get("controller_id")),
            ("cam_system", state.get("cam_system")),
            ("post_version", state.get("post_version")),
        ):
            if not _text(expected) or post.get(field) != expected:
                missing(f"postprocessor {field} is missing or conflicts with job context", "SOURCE_VERIFICATION_REQUIRED")
        if post.get("validation_state") != "verified":
            missing("postprocessor validation is not verified", "SOURCE_VERIFICATION_REQUIRED")
    return blockers, findings
