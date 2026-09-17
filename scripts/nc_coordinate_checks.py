"""Declared fixed Cartesian target-bound arithmetic, never physical verification."""

from decimal import Decimal, localcontext

if __package__:
    from .validate_schema_instances import validator_for
else:
    from validate_schema_instances import validator_for


def _finite(value):
    if type(value) not in (int, float):
        return None
    number = Decimal(str(value))
    return number if number.is_finite() else None


def _add(left, right):
    # Preserve even very small limit exceedances; do not round to default precision.
    with localcontext() as context:
        context.prec = (max(left.adjusted(), right.adjusted(), 0)
                        - min(left.as_tuple().exponent, right.as_tuple().exponent, 0) + 2)
        return left + right


def review_coordinate_model(model, blocks, contexts, selected_wcs, axis_bounds, program_supported):
    result = {"status": "not_run", "blockers": [], "findings": [], "targets": [],
              "scope": "declared machine-axis initial position and linear targets after the first tool change; no collision or physical-motion verification"}

    def block(message, code="MISSING_CONTEXT"):
        result["blockers"].append(code)
        result["findings"].append(message)

    schema = validator_for("setup.schema.json")
    model_schema = schema.evolve(schema={"$ref": schema.schema["$id"] + "#/$defs/coordinate_model"})
    if not model_schema.is_valid(model):
        block("coordinate model is missing, unsupported or schema-invalid")
        return result
    machine, setup, tool, controller, job = (contexts.get(key, {}) for key in ("machine", "setup", "tool", "controller", "job"))
    for field, expected in (("machine_id", machine.get("machine_id")), ("controller_id", controller.get("controller_id")),
                            ("setup_id", setup.get("setup_id")), ("tool_id", tool.get("tool_id")), ("wcs", selected_wcs)):
        if model[field] != expected:
            block(f"coordinate model {field} conflicts with selected context")
    units = "in" if job.get("units") in ("in", "inch") else job.get("units")
    if model["units"] != units or model["lifecycle"]["units"].get("length") != units:
        block("coordinate model units conflict with the job or model lifecycle")
    verification = model["lifecycle"]["verification"]
    if verification["status"] != "verified" or verification["reviewed_revision"] != model["lifecycle"]["revision"]:
        block("coordinate model lacks current revision-scoped review evidence", "SOURCE_VERIFICATION_REQUIRED")
    capabilities = machine.get("capabilities") or {}
    limits = machine.get("limits") or {}
    if (not isinstance(capabilities, dict) or type(capabilities.get("axes")) is not int or capabilities["axes"] != 3
            or not isinstance(limits, dict) or limits.get("coordinate_frame") != "machine_axes" or len(axis_bounds) != 3):
        block("coordinate review requires three Cartesian axes and explicit machine-axis bounds", "MACHINE_CONTEXT_REQUIRED")
    translation = {axis: _finite(model["translation"][axis.lower()]) for axis in "XYZ"}
    position = {axis: _finite(model["initial_machine_position"][axis.lower()]) for axis in "XYZ"}
    if any(value is None for value in (*translation.values(), *position.values())):
        block("coordinate translation and initial position must be finite JSON numbers")
    if not program_supported:
        block("unsupported NC syntax or commands prevent fixed-coordinate review", "SOURCE_VERIFICATION_REQUIRED")
    if result["blockers"]:
        result["blockers"] = sorted(set(result["blockers"]))
        return result

    def check_position(label):
        for axis in "XYZ":
            if not axis_bounds[axis][0] <= position[axis] <= axis_bounds[axis][1]:
                block(f"{label}: {axis}{position[axis]} exceeds the declared machine-axis bound", "MACHINE_CONTEXT_REQUIRED")

    check_position("initial position after tool change")
    length_mode = distance_mode = wcs = motion = None
    changes = 0
    ended = False
    for number, words in blocks:
        commands = {(letter, value) for letter, value in words if letter in "GM"}
        values = {letter: value for letter, value in words}
        for letter, value in words:
            if letter != "G":
                continue
            if value in (20, 21):
                length_mode = value
            elif value == 90:
                distance_mode = value
            elif value == 54:
                wcs = "G54"
            elif value in (0, 1):
                motion = value
        if ("M", 6) in commands:
            changes += 1
            if changes > 1 or result["targets"]:
                block(f"line {number}: another tool change needs new position/transform evidence", "SOURCE_VERIFICATION_REQUIRED")
        if any(axis in values for axis in "XYZ"):
            if (changes != 1 or ended or distance_mode != 90 or wcs != model["wcs"] or motion is None
                    or length_mode != (21 if units == "mm" else 20)):
                block(f"line {number}: fixed-coordinate prerequisites are missing or changed")
                continue
            for axis in "XYZ":
                if axis in values:
                    position[axis] = _add(values[axis], translation[axis])
            check_position(f"line {number}")
            result["targets"].append({"line": number, "machine_target": {axis.lower(): str(position[axis]) for axis in "XYZ"}})
        if ("M", 30) in commands:
            ended = True
    if not result["targets"]:
        block("no supported machine-axis targets were available for review")
    result["blockers"] = sorted(set(result["blockers"]))
    result["status"] = "blocked" if result["blockers"] else "checked_declared_bounds"
    return result
