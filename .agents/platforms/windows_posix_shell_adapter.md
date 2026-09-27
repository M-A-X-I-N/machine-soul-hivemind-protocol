# Windows POSIX-shell destination compatibility

## Why this still matters

Fish/Bash/Zsh on Windows may run inside MSYS2/Cygwin-style compatibility environments. Their effective `HOME` and path syntax can differ from the ordinary Windows profile paths visible to a PowerShell process.

Machine-Soul must therefore respect the compatibility environment rather than guessing the destination from a Windows profile.

## Current solution

The **operation policy is Python** and uses the same platform-neutral wrappers as every other application.

For Windows Fish/Bash/Zsh declarations, `WindowsPosixHomeDestination` resolves the native destination by:

1. reading the compatibility process's `HOME`;
2. invoking `cygpath -w` as the narrow external path-translation boundary;
3. returning that translated destination to the generic Python configuration engine.

Python itself performs the symlink classification/mutation, backup/state lifecycle, and result handling. There is no Bash→PowerShell policy chain and no separate Windows PowerShell configuration runtime.

## Requirements

- invoke the wrapper from an environment that exposes the intended compatibility-shell `HOME`;
- `cygpath` must be reachable through that environment's `PATH`;
- Python must have sufficient Windows symlink capability for the requested mutation.

If those compatibility-environment requirements are absent, destination resolution fails explicitly rather than guessing another profile path.

## CI validation

Windows CI exercises the Python wrappers from Git Bash/MSYS-compatible Bash and verifies the resulting compatibility-home configuration lifecycle. The ordinary Windows Python suite separately validates wrapper import/direct execution and generic symlink/state behavior.

## Historical note

The earlier v2 implementation used POSIX Bash adapters which translated paths and delegated link/state policy to a PowerShell `MachineSoul.psm1` runtime. V2-60/V2-61 retired that parallel implementation after Python parity was proven.
