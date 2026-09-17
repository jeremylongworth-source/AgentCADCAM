# Private security reporting decision

Status: `REVIEW_REQUIRED` — reporting enabled; signed-in form and notification checks outstanding.

On 2026-09-17 the maintainer selected GitHub private vulnerability reporting and
authorized enabling it if needed. This authorization does not permit changing
repository visibility or publishing the project.

## Initial configuration

- The repository API reported `visibility: private` and administrator permission.
- GET and PUT requests to the repository's `private-vulnerability-reporting`
  endpoint returned HTTP 404. Enablement was not confirmed.
- [GitHub's configuration documentation](https://docs.github.com/en/code-security/how-tos/report-and-fix-vulnerabilities/configure-vulnerability-reporting/configure-for-a-repository),
  checked on 2026-09-17, describes this feature for public repositories.
- No visibility change was made and no alternative private contact was supplied.

An HTTP 404 alone does not identify every possible configuration or permission
cause. The observed private visibility and documented feature scope are a
prerequisite to resolve, not evidence that reporting is enabled.

## Follow-up configuration — 2026-09-17

The repository API subsequently reported public visibility. This agent did not
change visibility. The previously authorized PUT request now succeeded and a
separate GET returned `enabled: true`.

The public advisories page visibly offers **Report a vulnerability**. Following
that link reaches GitHub sign-in in the available browser session. The enabled
setting and public entry point are verified; the authenticated report form,
recipient notifications and triage ownership are not. No report was submitted,
and no credentials or security reports were accessed.

## Remaining release prerequisite

Keep Phase 7 public-alpha acceptance open. A signed-in maintainer should confirm
the private report form is available and assign notification/triage responsibility
before announcing public alpha. Do not submit a dummy vulnerability report merely
to test it. Public repository visibility is not itself a release-gate decision.

If the reporting form cannot be used, obtain an explicitly designated interim
private contact from the maintainer. Do not invent an email address or use public
issues as a substitute.
