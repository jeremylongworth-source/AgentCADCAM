# Private security reporting decision

Status: `REVIEW_REQUIRED` — channel selected; activation outstanding.

On 2026-09-17 the maintainer selected GitHub private vulnerability reporting and
authorized enabling it if needed. This authorization does not permit changing
repository visibility or publishing the project.

## Observed configuration

- The repository API reported `visibility: private` and administrator permission.
- GET and PUT requests to the repository's `private-vulnerability-reporting`
  endpoint returned HTTP 404. Enablement was not confirmed.
- [GitHub's configuration documentation](https://docs.github.com/en/code-security/how-tos/report-and-fix-vulnerabilities/configure-vulnerability-reporting/configure-for-a-repository),
  checked on 2026-09-17, describes this feature for public repositories.
- No visibility change was made and no alternative private contact was supplied.

An HTTP 404 alone does not identify every possible configuration or permission
cause. The observed private visibility and documented feature scope are a
prerequisite to resolve, not evidence that reporting is enabled.

## Release prerequisite

Keep Phase 7 public-alpha acceptance open. When the maintainer separately
authorizes publication, coordinate enablement with the visibility change and
verify both the enabled setting and the private report form before announcing
the public alpha. Do not submit a dummy vulnerability report merely to test it.
Update `SECURITY.md` with verified availability at that time.

If private intake is needed before publication, obtain an explicitly designated
interim private contact from the maintainer. Do not invent an email address or
use public issues as a substitute. Other source-audit and safety-corpus work can
continue while activation is outstanding.
