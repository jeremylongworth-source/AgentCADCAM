# Interoperability Tests

Validate format semantics, unit/revision handling, provenance, and derivative-artifact rules.

`test_cad_fixture_review.py` mutates copied source/drawing/exchange files and checks that the CAD fixture CLI incorporates failed content checks, including nonzero exit status for blockers. Its positive JSON report is retained under `fixtures/cad/bracket/expected/file-review.json`. These checks are bounded to the synthetic bracket; see the [evaluation scope and remaining evidence](../../docs/evaluation/cad-handoff-evaluation.md).
