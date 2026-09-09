# Contour Assimilation Directive

Canonical Contour terminal configuration lives here.

The host resolver follows the repository-wide assimilation model:

```text
contour/<hostname>/
    if present
otherwise
contour/default/
```

`shared/` contains reusable fragments or reference material only; it is not intended to be linked directly as Contour's active configuration.

Initial skeleton:

```text
contour/
├── README.md
├── shared/
│   └── README.md
├── default/
│   └── contour.yml
└── spaceship/
    └── contour.yml
```

`default/` is the fallback manifestation for unspecialized hosts.

`spaceship/` is the first explicit workstation-specific manifestation.

The active Contour configuration on a host should ultimately be linked or otherwise resolved to the appropriate `contour.yml` in this tree.
