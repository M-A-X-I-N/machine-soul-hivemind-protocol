# Python/declarative migration completion

## Status

V2-63 completes the migration phase defined by V2-44 through V2-63.

The active architecture no longer has parallel Bash/PowerShell policy engines. Application operation entry points are platform-neutral Python wrappers over shared Python engines and declarative application definitions.

## Proven parity

The migration preserved or re-established coverage for:

- safe file-symlink classification and lifecycle;
- backup/restore and external-mutation conflict handling;
- checkout-relocation repair with restore-lineage preservation;
- explicit target-account semantics including an actual Linux sudo/root boundary;
- Apt and WinGet managed/unmanaged installation ownership;
- Windows CMD AutoRun integration through Python `winreg`;
- Windows POSIX compatibility destinations through the declared HOME + `cygpath` translation strategy;
- imported and standalone wrapper execution;
- common result serialization/exit semantics;
- native primitive process/protocol failure distinction;
- wrapper-driven orchestration and partial-change preservation;
- fresh-clone operation behavior on Linux and Windows.

## Deliberate compatibility retained

Legacy config/install state readers remain in the Python state layer. They exist to preserve ownership, backup, and restore lineage created by the old runtime and are not evidence of an active legacy implementation.

Do not remove those readers until the idiot human explicitly decides old state can no longer exist or a separate migration safely converts it.

## Runtime shape

No production Bash/PowerShell operation policy scripts remain. Shell/PowerShell scripts under `meta/tests/` are test harnesses. Scripts under `assimilation/` are canonical user configuration when applicable, not Machine-Soul runtime code.

The native-primitive protocol remains available for future platform operations that genuinely earn a process boundary; no old runtime script was grandfathered into primitive status.
