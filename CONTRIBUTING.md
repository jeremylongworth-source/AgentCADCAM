# Contributing

Thank you for helping build a careful, vendor-neutral manufacturing reasoning layer.

## Before contributing

For vulnerabilities or unsafe-ready-state reports, follow [SECURITY.md](SECURITY.md)
and its current channel-availability warning. Do not attach sensitive artifacts
to public issues or pull requests.

Read:

1. [ROADMAP.md](ROADMAP.md)
2. [AGENTS.md](AGENTS.md)
3. The applicable standards in `docs/standards/`
4. The relevant architecture contract in `docs/architecture/`

During foundation development, changes should advance the current roadmap gate rather than add speculative process coverage.

## Contributions

Each change should include:

- the user or workflow problem addressed;
- affected schemas, skills, router paths, and state invalidation behavior;
- evidence and source metadata for factual claims;
- positive, negative, and regression fixtures where applicable;
- explicit safety and human-review implications;
- validation output from `python scripts/validate_foundation.py` and `python scripts/validate_schema_instances.py`, plus the relevant tests. Install `requirements-test.txt` for the portable suite; see [test setup](tests/README.md).

## Skill contributions

Skills must have a narrow contract, explicit inputs and outputs, stop conditions, source requirements, and review status. Vendor-specific assumptions must be isolated and labeled. A skill must not authorize physical execution.

## Pull requests

Keep pull requests focused. Explain any change to scope, taxonomy, schemas, approval semantics, or invalidation rules. Breaking changes require a migration note and changelog entry.

All contributions are subject to review. Passing automated validation does not replace qualified manufacturing, safety, regulatory, or supplier review.
