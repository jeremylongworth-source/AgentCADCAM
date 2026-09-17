# Additive FDM Mutations

These declarative mutations change a copy of the job/printer/material context. They must produce the hard outcomes in `../expected/outcomes.yaml`.

They are not file-defect evidence by themselves. The byte-level cases in
`tests/safety/test_stl_mesh_review.py` remove a facet from the actual bracket,
alter its identity and test constructed open, duplicate, degenerate, winding,
edge and vertex-fan defects. The missing-facet case updates the test hash while
retaining `mesh_status: valid`, proving that file inspection supplies the blocker.
Original fixture bytes and profile verification states are never repaired.
