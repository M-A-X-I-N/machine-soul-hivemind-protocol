# Host inventory

Host identity is declarative. Application scripts should consume these records rather than scattering hostname/platform facts through code.

Each host currently uses a simple `.env`-style record so both PowerShell and Bash can parse it without extra dependencies.

Current hosts:

- `spaceship` — Windows workstation.
- `workhorse` — Ubuntu/Linux server.
- `runar` — Ubuntu-like server.

Account lists are advisory inventory, not authentication or authorization policy.
