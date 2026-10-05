# MSHP-AGENT-BASELINE-B-060 — Baseline repository population validation

## Target

`M-A-X-I-N/baseline`

The repository was renamed by the maintainer from `M-A-X-I-N/template` before B-060 execution.

At initial task start GitHub reported:

- public repository;
- GitHub template repository: `is_template: true`;
- default branch: `main`;
- size: `0`;
- no commits (`409 Git Repository is empty`).

No pre-existing content required preservation.

B-060 was reopened once after human review because the first generic seed placed task/reminder/initiative files directly at repository root. That was functionally valid but created unnecessary root clutter. The corrected seed groups those repository-control surfaces under `project_control/`.

## Final populated structure

```text
AGENTS.md

.agents/
├── README.md
├── baseline/
│   ├── WORKFLOW.md
│   ├── GIT.md
│   ├── PROVENANCE.md
│   └── KNOWLEDGE.md
├── local/
│   ├── README.md
│   └── REPOSITORY.md
└── memory/
    └── README.md

project_control/
├── tasks.md
├── tasks/
│   └── README.md
├── reminders.md
└── initiatives/
    └── README.md
```

The seed deliberately does not reproduce MSHP's `autonomic_affairs/` layout or its memory category taxonomy.

`project_control/` is a generic repository-owned organizational container, not baseline policy. A consumer repository may choose different local paths by updating local-owned routing/policy without editing baseline-owned files.

## Baseline equality

The baseline-owned files in `M-A-X-I-N/baseline` remain byte-identical to the validated live MSHP baseline-owned source.

| File | Blob | Equal |
|---|---|---|
| `.agents/README.md` | `22f3d75f7f057671cd60ae18038ea942411416f4` | yes |
| `.agents/baseline/WORKFLOW.md` | `08cfdd47ebabf9b90564785ac4adc112455580a8` | yes |
| `.agents/baseline/GIT.md` | `21caa58693358f230e2647f0331cebe847b24587` | yes |
| `.agents/baseline/PROVENANCE.md` | `a040e776c75bbbbbf02cde048c9992d8f8a71bfd` | yes |
| `.agents/baseline/KNOWLEDGE.md` | `89a5c0f34b3fd64a69fd069de702df7bdf6f12c0` | yes |

## Leakage scan

The final template was searched for representative MSHP-only identifiers and paths:

- `MSHP`;
- `Machine-Soul` / `machine-soul`;
- `autonomic_affairs`;
- `assimilation_directives`;
- `annexation_procedures`;
- `accumulated_instruments`;
- `CodeQL`;
- `selector.yml`;
- `MSHP-AGENT-BASELINE`.

Result: **zero matches**.

## Fresh-navigation walk

Verified the generated-repository path:

1. root `AGENTS.md` routes to `.agents/README.md`, `.agents/local/README.md`, and `project_control/tasks.md`;
2. the generic router routes substantial work to `baseline/WORKFLOW.md` plus the stable `local/README.md` entrypoint;
3. the local router owns discovery of `local/REPOSITORY.md`, `project_control/` task/reminder/initiative locations, and memory placement;
4. `project_control/tasks.md` points lifecycle semantics back to baseline `WORKFLOW.md`;
5. `project_control/tasks/README.md`, reminders, and initiatives resolve their relative links inside the grouped control directory;
6. memory has only a repository-owned README and no speculative empty taxonomy.

A repository generated from this template can add arbitrary local instruction files by updating only `.agents/local/README.md`; baseline-owned routing does not need modification.

## Root-clutter result

The final repository's top-level control/navigation surface is intentionally small:

```text
AGENTS.md
.agents/
project_control/
```

Future normal project files such as `README.md`, source directories, licenses, build files, and documentation therefore do not have to compete with four separate baseline workflow artifacts at repository root.

## Result

B-060 acceptance criteria are satisfied after the layout correction.

No updater, manifest/version machinery, shared runtime, CI automation, or other consumer repository was added or modified.
