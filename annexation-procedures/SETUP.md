# Discovery-Driven Annexation Setup

The setup layer is intentionally split into three concerns:

1. **Top-level orchestration** discovers setup actions automatically.
2. **Platform primitives** contain reusable Windows/Linux operations.
3. **Application actions** contain only the small amount of application-specific glue needed to enable canonical configuration.

Current structure:

```text
annexation-procedures/
├── setup.ps1
├── setup.sh
├── SETUP.md
├── windows/
│   ├── setup-machine-soul.ps1
│   └── make-symlink.ps1
├── linux/
│   ├── setup-machine-soul.sh
│   └── make-symlink.sh
└── actions/
    └── contour/
        ├── setup.ps1
        └── setup.sh
```

## Discovery contract

The wrapper does **not** contain a registry of applications.

Each direct child of `actions/` is a potential setup action. Availability is determined only by the presence of the platform-specific entry point:

```text
actions/<name>/setup.ps1   -> Windows setup is available
actions/<name>/setup.sh    -> Linux setup is available
```

Therefore adding a future application does not require editing `setup.ps1` or `setup.sh`.

Examples:

```text
actions/contour/setup.ps1
    -> Contour appears in the Windows menu

actions/contour/setup.sh
    -> Contour appears in the Linux menu

actions/some-bs-thing/
    -> no setup script, therefore no action is exposed
```

A capability may support one platform, both platforms, or neither without needing placeholder scripts.

## Platform primitives

Reusable behavior belongs under the platform directories rather than being copied into application actions.

For example, Contour currently requires little more than connecting one canonical file to one native configuration path. Its application-specific setup therefore resolves the source and target and delegates the actual filesystem work to:

```text
windows/make-symlink.ps1
linux/make-symlink.sh
```

The symlink helpers own common behavior such as:

- creating missing parent directories;
- detecting an already-correct link;
- preserving an existing target before replacement;
- creating the new symbolic link.

Future applications requiring symbolic links should reuse the same primitive.

This gives global filesystem behavior one implementation per operating system without introducing a manifest/parser DSL.

## MACHINE_SOUL bootstrap

`MACHINE_SOUL` is framework infrastructure rather than an application action, so its setup remains under the platform layer:

```text
windows/setup-machine-soul.ps1
linux/setup-machine-soul.sh
```

The top-level `--all` / `-All` operation establishes `MACHINE_SOUL` first, then executes every discovered application action for the current platform.

It is also exposed independently because establishing the repository root and enabling an application configuration are distinct operations.

## Usage

Windows:

```powershell
./setup.ps1
./setup.ps1 -All
./setup.ps1 -List
./setup.ps1 -MachineSoul
./setup.ps1 -Action contour
```

Linux:

```bash
bash ./setup.sh
bash ./setup.sh --all
bash ./setup.sh --list
bash ./setup.sh --machine-soul
bash ./setup.sh contour
```

With no arguments, the wrapper constructs its interactive menu dynamically from the setup scripts actually available for the current operating system.

## Future growth

Adding Oh My Posh, Fish, Bash, Zsh, PowerShell, or another capability should normally require only:

```text
actions/<capability>/setup.ps1
and/or
actions/<capability>/setup.sh
```

If several applications begin repeating the same operation, that operation should graduate into a reusable platform primitive rather than becoming copy-pasted doctrine.

The intended boundary is deliberately simple:

```text
wrapper
  -> discovers WHAT can be set up

action
  -> knows WHAT an application needs

platform primitive
  -> knows HOW the operating system performs a generic operation
```

This keeps discovery convention-based while avoiding the brittleness and maintenance overhead of a general-purpose setup manifest/parser.
