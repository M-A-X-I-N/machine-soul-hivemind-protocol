# Python runtime conventions

V2-50 established the shared Python runtime boundary.

- Minimum Python: 3.10.
- Python is an external prerequisite; do not implement Python bootstrap/install behavior without new authorization.
- Shared package: `accumulated_instruments.machine_soul`.
- Repository-local imports are intentional; no editable/site-packages install is required.
- Standard library first; add dependency tooling only when a real dependency justifies it.
- Importing the package must be side-effect free.
- Direct atomic wrappers use a small standardized `sys.path` bootstrap from their own path so they remain runnable from any working directory.
- That bootstrap is the only acceptable repeated infrastructure in wrappers; business logic belongs in shared libraries.
- Do not create empty package taxonomy just to mirror design diagrams. Add modules when they gain real behavior.
