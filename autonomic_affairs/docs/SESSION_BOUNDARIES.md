# SSH, sudo, root, and shell process boundaries

Machine-Soul treats shell/process boundaries literally.

## SSH

When a local shell runs ssh workhorse, the local shell remains local and waits for the SSH client. The remote SSH server starts a new process on workhorse, normally the configured login shell.

Therefore the local Fish/Bash/Zsh process does not become remote, local Oh My Posh prompt state does not travel across SSH, the remote machine needs its own Machine-Soul checkout/binding and shell initialization, and fonts remain a local terminal-rendering concern even when remote OMP emits glyphs.

For Machine-Soul, the important inputs after SSH are the remote host/account and that remote environment's MACHINE_SOUL.

## sudo/root

sudo creates another process/account boundary. Root's config is independently resolved.

This is why workhorse and runar can resolve separate OMP files for m-a-x-i-n and root while reusing the same configuration-deployment runtime.

## Validation boundary

Machine-Soul does not implement SSH transport and does not need to test SSH encryption/authentication itself.

CI validates the behavior Machine-Soul owns: a clean remote-like process with only remote host/account context, an actual Ubuntu sudo root process, independent account-specific config selection and deployment state, root versus normal-user OMP targets, and safe Apply/Unapply across those process/account boundaries.

## Logical target versus execution identity

Future Python operations carry the target account explicitly in operation context.

The account being managed is not inferred again after an elevation/process boundary. For example, an operation started by a normal user with target `root` remains logically targeted at `root` even if only one primitive is executed through `sudo`.

Likewise, an elevated helper must not reinterpret "current user" and accidentally write root-owned state for a configuration operation that logically targets the invoking user.

Target account identity therefore owns configuration selection, destination resolution, and deployment/install provenance. Execution identity owns only the permissions of the process performing a particular action.
