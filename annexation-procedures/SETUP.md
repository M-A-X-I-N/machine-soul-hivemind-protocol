# Modular Annexation Setup

The setup layer is intentionally split into independent actions. Each configurable capability gets its own setup action, with OS-specific entry points where necessary.

Current structure:

```text
annexation-procedures/
├── setup.ps1
├── setup.sh
├── machine-soul-root/
│   ├── setup.ps1
│   └── setup.sh
└── contour/
    ├── setup.ps1
    └── setup.sh
```

The top-level scripts are orchestrators only. They may invoke all setup actions for the current OS, invoke one named action directly, or present an interactive menu.

Current actions:

- `machine-soul-root` establishes the `MACHINE_SOUL` environment variable pointing at the repository root.
- `contour` enables the canonical Contour configuration by linking the platform's default Contour config path to `assimilation-directives/contour/contour.yml`.

Future capabilities such as Oh My Posh, Fish, Bash, Zsh, and PowerShell should follow the same pattern:

```text
annexation-procedures/<capability>/setup.ps1
annexation-procedures/<capability>/setup.sh
```

Only the platform-specific files that make sense for a capability need meaningful implementation. The orchestration layer should remain generic and treat each capability as an independent action.

Examples:

```powershell
./setup.ps1 -All
./setup.ps1 -Action contour
```

```bash
bash ./setup.sh --all
bash ./setup.sh contour
```
