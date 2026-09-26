# Installation mechanism investigation — 2026-09

This note preserves the current upstream/native installation findings used to define v2's installation architecture.

## Windows Package Manager

Microsoft documents WinGet's `install` and `uninstall` commands and recommends exact package identity when ambiguity is possible.

Useful architecture consequence:

- WinGet is a suitable Windows strategy when an application has an appropriate package.
- Use exact IDs and explicit source where sensible.
- Do not treat fuzzy search as stable automation.

Sources:

- https://learn.microsoft.com/en-us/windows/package-manager/winget/install
- https://learn.microsoft.com/en-us/windows/package-manager/winget/uninstall

## PowerShell

Microsoft's current PowerShell-on-Windows documentation provides WinGet installation using the `Microsoft.PowerShell` package ID.

Source:

- https://learn.microsoft.com/en-us/powershell/scripting/install/install-powershell-on-windows

## Windows Terminal

Microsoft documents Microsoft Store as the normal route and also points to GitHub releases/package-manager alternatives.

Source:

- https://learn.microsoft.com/en-us/windows/terminal/install

## Oh My Posh

Current upstream guidance:

- Windows: WinGet is an official installation path (`JanDeDobbeleer.OhMyPosh`).
- Linux: upstream provides its own shell installer and documents prerequisite tools.
- OMP configuration is independent from installation and supports multiple shells.

Sources:

- https://ohmyposh.dev/docs/installation/windows
- https://ohmyposh.dev/docs/installation/linux
- https://ohmyposh.dev/

## Fish

Fish's upstream documentation/homepage supplies current platform/distribution installation guidance. On Linux this normally maps to distribution/package mechanisms.

Sources:

- https://fishshell.com/
- https://fishshell.com/docs/current/

## Contour

Contour documents platform-specific install mechanisms:

- Windows MSI;
- distro/package options on Linux;
- Ubuntu `.deb` download/install;
- Flatpak;
- source build where desired.

This is a good example of why Machine-Soul should not force every application into one universal package-manager abstraction.

Source:

- https://contour-terminal.org/install/

## Derived design conclusions

1. Keep application install strategy declarative/per-platform.
2. Prefer platform/upstream-supported mechanisms rather than a universal bespoke installer.
3. Installation scripts must use baseline platform runtimes, not the target shell.
4. Record installation provenance so Uninstall does not remove software merely because it exists.
5. Keep Install/Uninstall semantically separate from Apply/Unapply/Check.
