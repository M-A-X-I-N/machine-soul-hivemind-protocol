# SSH, sudo, root, and shell process boundaries

Machine-Soul treats shell/process boundaries literally.

## SSH

When a local shell runs `ssh <remote_host>`, the local shell remains local and waits for the SSH client. The remote SSH server starts a new process on the target host, normally the configured login shell.

Therefore the local Fish/Bash/Zsh process does not become remote, local Oh My Posh prompt state does not travel across SSH, the remote machine needs its own Machine-Soul checkout/binding and shell initialization, and fonts remain a local terminal-rendering concern even when remote OMP emits glyphs.

For Machine-Soul, the important inputs after SSH are the remote host/account and that remote environment's MACHINE_SOUL.

## sudo/root

sudo creates another process/account boundary. Root's config is independently resolved.

This is why Linux host variants can resolve separate OMP files for a normal target account and a privileged target account while reusing the same configuration-deployment runtime.

## Validation boundary

Machine-Soul does not implement SSH transport and does not need to test SSH encryption/authentication itself.

CI validates the behavior Machine-Soul owns: a clean remote-like process with only remote host/account context, an actual Ubuntu sudo root process, independent account-specific config selection and deployment state, root versus normal-user OMP targets, and safe Apply/Unapply across those process/account boundaries.

## Logical target versus execution identity

Future Python operations carry the target account explicitly in operation context.

The account being managed is not inferred again after an elevation/process boundary. For example, an operation started by a normal user with target `root` remains logically targeted at `root` even if only one primitive is executed through `sudo`.

Likewise, an elevated helper must not reinterpret "current user" and accidentally write root-owned state for a configuration operation that logically targets the invoking user.

Target account identity therefore owns configuration selection and destination resolution. Configuration-deployment provenance is target-account scoped.

Installation provenance is different: its ownership namespace follows the actual installation scope. User-scoped installation provenance belongs to the relevant host/account; machine-scoped installation provenance belongs to the host/machine rather than whichever account requested the operation. Execution identity owns the permissions/security context of the process performing a particular action and must not be conflated with either target account or installation scope.

See [`INSTALLATION_SCOPE.md`](INSTALLATION_SCOPE.md).
