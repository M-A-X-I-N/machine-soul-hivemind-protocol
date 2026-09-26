# Symlink implementation notes

## Linux: do not canonicalize the destination through the final symlink

Verified in CI on Ubuntu 24.04.

A managed config destination must be normalized **without following its final path component**.

The first Linux runtime implementation used:

```bash
realpath -m "$destination"
```

After a symlink was created, that dereferenced the destination and returned the target path. Verification then inspected the tracked source itself rather than the native config link and falsely reported failure.

The fix is `ms_abs_path_no_follow`: canonicalize only the parent directory, then append the destination basename unchanged.

Use normal target canonicalization for the **link target**, but preserve destination identity.

## Windows PowerShell bootstrap compatibility

The Windows shared runtime must remain callable from Windows PowerShell 5.1 because it may be responsible for installing newer PowerShell.

Avoid PowerShell 7/.NET Core-only conveniences in baseline runtime code. Already encountered/replaced:

- `SHA256.HashData`;
- `Convert.ToHexString`;
- `Path.GetRelativePath`;
- `utf8NoBOM` encoding shorthand;
- constructor syntax relying on newer conveniences.

CI explicitly runs the Windows framework under the `powershell` shell to keep this compatibility visible.
