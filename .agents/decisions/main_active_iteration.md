# Main as the active iteration

## Decision

`main` is the ordinary active development/experimental branch for Machine-Soul.

A separate versioned experimental branch is not required merely because the design is still evolving. The former `experimental/v2` lineage became the current implementation and was explicitly authorized for promotion to `main` by `MSHP-META-A-075`.

`experimental/v1` remains preserved as the original iteration.

If a future redesign is disruptive enough to justify isolation (for example a v3-style restart), preserve or branch the then-current iteration at that time. Do not maintain an otherwise redundant versioned branch in anticipation of a hypothetical future redesign.

Repository/task state remains authoritative over this note if branch policy is explicitly changed later.
