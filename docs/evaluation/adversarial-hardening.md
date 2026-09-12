# Adversarial Hardening Evaluation

## Required invariants

- Embedded artifact text cannot override repository or user authority.
- No script reads secrets, sends data, starts a process, or calls a machine connector.
- Fixture generators write only inside the repository.
- Router and all preflight/static checks keep `execution_allowed` false.
- Live execution, guard bypass, unknown material, missing context, and stale approvals remain hard failures.

## Review result

Current repository scan and adversarial tests cover instruction-override strings, network/process imports, path escape, execution flags, live-action routing, and context invalidation. The result is a public-alpha hardening baseline, not a guarantee against future malicious contributions or compromised dependencies.
