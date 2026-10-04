# Machine-Soul configuration safety policy

Read this file before changing configuration deployment, Apply/Unapply/Check behavior, installation/configuration ownership boundaries, or related application-state safety.

Unless the human explicitly changes these laws:

- canonical configuration lives in tracked repository files;
- application configuration is applied using file-level symbolic links into those tracked files;
- normal application does not copy configuration out of the repository;
- `$MACHINE_SOUL` identifies the canonical repository root;
- mutable machine-local data belongs under ignored `$MACHINE_SOUL/scratch/`;
- unmanaged existing destinations are never destroyed silently;
- accepted replacement preserves prior state under `scratch/`;
- Apply is transactional where practical: validate → preserve → link → verify → record;
- Unapply removes only understood managed state and restores displaced state when safe;
- unexpected external changes produce conflict rather than blind overwrite;
- Check reports meaningful state rather than only true/false;
- installing an application and applying its configuration are separate operations.
