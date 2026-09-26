# Windows POSIX-shell deployment adapter

## Why it exists

Fish/Bash/Zsh on Windows may run inside MSYS2/Cygwin-style compatibility environments. Their effective HOME and path syntax are not the same thing as PowerShell's Windows user profile paths.

Guessing those destinations from pure PowerShell would risk linking the wrong file.

## Current solution

The supported Windows POSIX path is:

1. run the application operation from the POSIX shell;
2. use that environment's HOME to identify the native shell config destination;
3. use cygpath to convert the repository root and destination to Windows-native paths;
4. invoke powershell.exe;
5. delegate the actual file-level symbolic-link/backup/state operation to the shared Windows MachineSoul.psm1 runtime.

This preserves the hard invariant that the native config file is a real Windows symbolic link into the tracked repository file instead of relying on whatever symlink emulation/copy behavior the compatibility layer might use.

## Requirements

- cygpath available in the POSIX environment;
- powershell.exe reachable from that environment;
- Windows symbolic-link capability sufficient for the shared runtime.

## CI validation

windows-latest is exercised through Git Bash/MSYS-compatible bash. The test runs Fish/Bash/Zsh Windows operation scripts, while the Windows PowerShell configuration-deployment runtime remains the authority for checking link ownership/state.

## Pure PowerShell entry points

The original .ps1 stubs for Fish/Bash/Zsh intentionally remain NOT_IMPLEMENTED when invoked without the compatibility-shell context. The supported entry points for those Windows shell configs are the .sh scripts under `annexation-procedures/<application>/windows/`.