# Contour Assimilation Directive

Canonical Contour terminal configuration lives here in a single file:

```text
contour/
├── README.md
└── contour.yml
```

The `default` profile contains the shared baseline for all hosts.

Host-specific profiles contain only sanctioned deviations from that baseline.
For now the only explicit host profile is `spaceship`.

Conceptually:

```text
default
  └── shared Contour doctrine

spaceship
  └── inherits default and overrides only what differs
```

This keeps the configuration fully tracked in the repository without duplicating
nearly-identical `contour.yml` files per workstation.

If a future host needs a profile-scoped difference, add another profile to the
same file and keep the override as small as possible.

If a future difference turns out to require non-profile/global settings, that can
be handled separately without changing the basic single-file policy.
