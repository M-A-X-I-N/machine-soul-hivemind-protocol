# Declarative application schema

V2-51 established actual side-effect-free declaration types under `accumulated_instruments.machine_soul.model`.

Per-application modules will be named `_application.py` and expose `APPLICATION = Application(...)`.

Important rules:

- import is side-effect free;
- repository app IDs are snake_case;
- capabilities are explicit `Support` values;
- source declarations identify a leaf, not host/account-specific resolved paths;
- destination/install behavior is selected through reusable strategy value types;
- strategies contain data, not imperative step programs;
- add reusable strategy abstractions before custom app code when behavior repeats;
- `CustomInstaller` is the escape hatch for genuinely unique procedural work;
- generic engines must not grow app-name conditionals.

The initial model is intentionally incomplete in behavior. Later tasks define engines, wrappers, results, primitives, and convert real applications.
