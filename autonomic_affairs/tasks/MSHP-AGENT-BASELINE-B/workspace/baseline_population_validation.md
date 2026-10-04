# MSHP-AGENT-BASELINE-B-060 — Baseline repository population validation

## Target

`M-A-X-I-N/baseline`

The repository was renamed by the maintainer from `M-A-X-I-N/template` before B-060 execution.

At task start GitHub reported:

- public repository;
- GitHub template repository: `is_template: true`;
- default branch: `main`;
- size: `0`;
- no commits (`409 Git Repository is empty`).

No pre-existing content required preservation.

## Populated structure

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

tasks.md
tasks/
└── README.md
reminders.md
initiatives/
└── README.md
```

The seed deliberately does not reproduce MSHP's `autonomic_affairs/` layout or its memory category taxonomy. Local paths are repository-owned and the template uses a generic root-level task/reminder/initiative layout.

## Baseline equality

The baseline-owned files in `M-A-X-I-N/baseline` are byte-identical to the validated live MSHP baseline-owned source.

| File | MSHP blob | Baseline blob | Equal |
|---|---|---|---|
| `.agents/README.md` | `22f3d75f7f057671cd60ae18038ea942411416f4` | `22f3d75f7f057671cd60ae18038ea942411416f4` | yes |
| `.agents/baseline/WORKFLOW.md` | `08cfdd47ebabf9b90564785ac4adc112455580a8` | `08cfdd47ebabf9b90564785ac4adc112455580a8` | yes |
| `.agents/baseline/GIT.md` | `21caa58693358f230e2647f0331cebe847b24587` | `21caa58693358f230e2647f0331cebe847b24587` | yes |
| `.agents/baseline/PROVENANCE.md` | `a040e776c75bbbbbf02cde048c9992d8f8a71bfd` | `a040e776c75bbbbbf02cde048c9992d8f8a71bfd` | yes |
| `.agents/baseline/KNOWLEDGE.md` | `89a5c0f34b3fd64a69fd069de702df7bdf6f12c0` | `89a5c0f34b3fd64a69fd069de702df7bdf6f12c0` | yes |

## Leakage scan

All tracked Markdown seed files were scanned for representative MSHP-only identifiers and paths:

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

1. root `AGENTS.md` routes to `.agents/README.md`, `.agents/local/README.md`, and `tasks.md`;
2. the generic router routes substantial work to `baseline/WORKFLOW.md` plus the stable `local/README.md` entrypoint;
3. the local router owns discovery of `local/REPOSITORY.md`, task/reminder/initiative locations, and memory placement;
4. `tasks.md` points lifecycle semantics back to baseline `WORKFLOW.md`;
5. memory has only a repository-owned README and no speculative empty taxonomy.

A repository generated from this template can add arbitrary local instruction files by updating only `.agents/local/README.md`; baseline-owned routing does not need modification.

## Result

B-060 acceptance criteria are satisfied.

No updater, manifest/version machinery, shared runtime, CI automation, or other consumer repository was added or modified.
