# Installation discovery investigation

Status: completed research output for MSHP-DISC-A-020.

This file preserves the detailed evidence map used by later DISC-A synthesis. It is workspace material, not the permanent architecture contract.

## Core finding: historical installer provenance is often unknowable

The ideal question "was this installed by the preferred method?" has to split into two questions:

1. Does the discovered installation match or remain manageable through the preferred Machine-Soul strategy?
2. What evidence exists about the historical acquisition or installer channel?

Those are not equivalent.

### Windows and WinGet

Microsoft documents that winget list includes applications installed through WinGet and applications installed by other means. WinGet can also uninstall applications it did not install.

Therefore a correlated WinGet package ID/source is strong evidence that an installed application maps to a preferred WinGet package and can likely be managed through that package identity. It is not proof that WinGet originally installed it.

WinGet correlation uses installed-system identities such as ARP/MSI ProductCode and MSIX PackageFamilyName against available-source manifest metadata. winget export similarly attempts to correlate installed applications to available sources and warns when it cannot.

The optional Microsoft.WinGet.Client PowerShell module exposes Get-WinGetPackage, returning structured installed-package objects; uncorrelated entries may retain ARP/MSIX-style identifiers. This is attractive for rich discovery when available, but must not become an undeclared hard dependency without a separate decision.

Sources:
- https://learn.microsoft.com/en-us/windows/package-manager/winget/list
- https://learn.microsoft.com/en-us/windows/package-manager/winget/uninstall
- https://learn.microsoft.com/en-us/windows/package-manager/winget/export
- https://github.com/microsoft/winget-cli/blob/master/src/PowerShell/Help/Microsoft.WinGet.Client/Get-WinGetPackage.md

### Windows MSI and Add/Remove Programs registration

Windows Installer writes product registration under the Uninstall registry area using the product-code GUID. Useful fields include DisplayName, DisplayVersion, Publisher, InstallLocation, InstallSource, and UninstallString.

An MSI/ARP record can therefore strongly identify a registered product, version, product code, uninstall mechanism, and sometimes install/source paths. It does not prove whether the MSI was launched manually, by WinGet, or by another frontend.

Source:
- https://learn.microsoft.com/en-us/windows/win32/msi/uninstall-registry-key

### Windows MSIX/AppX

Get-AppxPackage reports installed AppX/MSIX packages for a user and can inspect other/all users with required permissions. Package APIs expose package family/full names and package paths.

This proves package registration and identity and can identify scope/user context. It does not by itself prove whether acquisition was Microsoft Store, WinGet, GitHub MSIX, or another deployment mechanism.

Sources:
- https://learn.microsoft.com/en-us/powershell/module/appx/get-appxpackage
- https://learn.microsoft.com/en-us/windows/win32/appxpkg/functions

### Linux dpkg and apt

dpkg-query exposes the installed package database, including package identity, installed version, package status, architecture, source-package fields, and package-owned file lists.

For Debian/Ubuntu-family systems this provides strong evidence that a specific dpkg package is installed and which files belong to it. It can correlate an executable path back to a package.

However, the dpkg database does not prove that historical acquisition happened through apt; the same package can be installed with dpkg -i and later be visible/manageable through the same dpkg/apt substrate.

Therefore an AptPackage("fish") preferred strategy should normally treat exact installed dpkg package identity as preferred-strategy compatible, while historical "apt itself performed installation" remains unknown unless separate trustworthy evidence exists.

Source:
- https://manpages.debian.org/unstable/dpkg/dpkg-query.1.en.html

## Evidence classes

Installation discovery should collect independent observations rather than jumping directly to one status.

Useful observation kinds include:

- manager_registration: exact native/package-manager registration exists;
- catalog_correlation: installed registration correlates to a package identity in a preferred or known catalog;
- native_package_registration: MSI/ARP or MSIX/AppX identity;
- executable_path: executable exists at a resolved path;
- version_probe: executable/application reports a version;
- file_owner: native package database owns a discovered executable/file;
- uninstall_registration: uninstall identity or command exists;
- machine_soul_provenance: Machine-Soul install state claims ownership;
- historical_hint: logs/history/source paths that may suggest acquisition but are not durable proof.

Each observation should carry its source and evidence authority.

## Proposed candidate model

The later implementation should support an InstallationCandidate carrying at least:

- native identity and display identity;
- version;
- one or more executable/install paths;
- scope: user, machine, package-user, or unknown;
- registration kind: dpkg, ARP/MSI, MSIX, portable, compatibility-environment package, etc.;
- historical acquisition channel when evidence exists, otherwise unknown;
- acquisition evidence;
- preferred-strategy match;
- manageability by preferred strategy;
- Machine-Soul ownership state;
- uninstall identity where available;
- observations.

The overall InstallationAssessment carries presence (present, absent, ambiguous, unknown), all candidates, an optional preferred candidate, and Machine-Soul state.

Do not encode independent dimensions into combinatorial result codes.

## Preferred match versus acquisition channel

For Machine-Soul's practical purpose, preferred_match should mean the discovered installation matches the identity or management substrate expected by the declared preferred strategy.

Examples:

- dpkg package fish is installed while Machine-Soul declares AptPackage("fish"):
  preferred match yes; historical acquisition may be apt, direct dpkg, or unknown; Machine-Soul ownership remains independent.

- WinGet correlates installed Oh My Posh to JanDeDobbeleer.OhMyPosh:
  preferred match/manageability yes; historical acquisition through WinGet is not proven by correlation; Machine-Soul ownership remains independent.

This gives the human the useful right-way/wrong-way distinction without inventing history the platform did not preserve.

## Discovery must be independent from installation capability

Current code derives check_installed from PlatformDeclaration.install_strategy. That is too restrictive.

Applications can be discoverable even if Machine-Soul cannot install/uninstall them:

- CMD is an OS component and can be discovered without an install strategy.
- Windows Terminal can be detected through MSIX/AppX, WinGet correlation, and executable/package identity while installation remains unimplemented.
- PowerShell can be detected through MSIX, MSI/ARP, executable path/version, or ZIP-like portable layout.
- Bash, Zsh, and Fish on Windows may be discovered inside MSYS2/Cygwin even if Machine-Soul does not install them.
- Contour can be detected through MSI, dpkg, Flatpak, executable paths, etc. while installation remains unimplemented.

The declaration model therefore needs separate installation-discovery descriptors/hints rather than making CHECK_INSTALLED contingent on install_strategy.

## Current application evidence map

### Fish

Linux preferred strategy today is AptPackage("fish").

Strong preferred evidence is exact dpkg package fish status/version plus package file ownership for the resolved executable. Foreign/alternate evidence includes executables outside package-owned paths, source builds, and other package ecosystems where present.

Fish upstream currently documents many package-manager and source-build routes. On Windows, Fish is available through MSYS2 and Cygwin; those environments require their own package-registration strategies if later supported.

Source:
- https://fishshell.com/

### Oh My Posh

Windows preferred strategy today is WingetPackage("JanDeDobbeleer.OhMyPosh").

Upstream documents WinGet, a manual PowerShell installer, and Chocolatey on Windows. Therefore executable presence is insufficient to infer mechanism.

WinGet correlation to the exact package ID is strong preferred-match evidence, not historical WinGet provenance. Chocolatey registration or manual-script layout can become alternate candidate evidence.

On Linux, the upstream install script defaults to ~/bin or ~/.local/bin, or an existing executable directory, illustrating a user-scoped/manual candidate with no native package-manager registration.

Sources:
- https://ohmyposh.dev/docs/installation/windows
- https://ohmyposh.dev/docs/installation/linux

### PowerShell

Current installation operations are not implemented, but discovery can be rich.

Microsoft documents WinGet installation; current PowerShell 7.6 WinGet defaults to MSIX, can select an MSI/WiX installer, and manual MSI remains available. ZIP deployment is also documented and can live at arbitrary paths.

Candidate evidence therefore spans MSIX/AppX registration, MSI/ARP registration, WinGet correlation, resolved pwsh.exe path/version, and portable/ZIP paths with no installer registration.

Package format and acquisition frontend are separate dimensions.

Source:
- https://learn.microsoft.com/en-us/powershell/scripting/install/install-powershell-on-windows

### Windows Terminal

Microsoft documents Store installation as normal, GitHub release builds as an alternative, and other package managers including WinGet. The WinGet manifest identifies Microsoft.WindowsTerminal and package family Microsoft.WindowsTerminal_8wekyb3d8bbwe.

Strong discovery can use MSIX package identity plus executable/package path. Store versus GitHub/WinGet acquisition may remain unknown from package identity alone.

Sources:
- https://learn.microsoft.com/en-us/windows/terminal/install
- https://learn.microsoft.com/en-us/windows/package-manager/package/manifest

### Contour

Upstream currently documents Windows MSI, Ubuntu downloaded .deb installed with dpkg, distro-native packages, Flatpak, and source builds.

This is a strong representative for multi-candidate discovery. On Ubuntu, dpkg registration can strongly identify the package even though apt may not have been the acquisition frontend. On Windows, MSI/ARP registration can identify product/version without proving how the MSI was obtained.

Source:
- https://contour-terminal.org/install/

### Bash and Zsh

On Linux these may be distribution packages and/or baseline OS components. Package registration plus executable/file-owner evidence is useful even without Machine-Soul install capability.

On Windows, Machine-Soul configuration explicitly targets a POSIX compatibility environment. Discovery needs environment-specific hints for MSYS2/Cygwin rather than checking arbitrary native PATH and assuming it is the configured runtime.

### CMD

Treat as a built-in/platform capability rather than a package-manager install. Discovery can establish executable/platform presence while Install/Uninstall remain unsupported or not implemented.

## Generic strategy candidates

The investigation supports reusable discovery capabilities along these lines:

- exact dpkg package registration and file ownership;
- WinGet installed-package correlation;
- Windows ARP/MSI product registration;
- Windows MSIX/AppX package identity;
- executable/path plus version probe;
- compatibility-environment package/query strategy for MSYS2/Cygwin;
- Flatpak package identity when an application declares one;
- optional other-manager strategies only when a managed application actually needs them.

Application declarations should supply identities/hints and combine reusable strategies. Avoid scanning every package manager on Earth by default.

## Absence and ambiguity

Not found by the preferred strategy is not absent.

A defensible absence conclusion requires completion of the application's declared discovery plan at the evidence level considered sufficient. If preferred lookup fails but executable or alternate registrations exist, presence is foreign/alternate.

If probes fail because a discovery backend is unavailable, permissions block inspection, or evidence conflicts, return unknown or ambiguous rather than absent.

Multiple legitimate candidates must be retained, for example side-by-side PowerShell versions or a system package plus a portable executable earlier on PATH.

## Takeover relevance

Future takeover needs exact candidate identity, registration kind, scope, executable paths, version, preferred-strategy compatibility, uninstall identity, and Machine-Soul ownership.

Discovery should capture these facts now. It must not itself adopt, uninstall, reinstall, or mutate anything.
