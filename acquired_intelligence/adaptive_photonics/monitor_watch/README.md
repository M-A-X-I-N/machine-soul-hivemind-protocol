# Swedish OLED monitor watch

This directory is the canonical recurring market-watch workspace for the monitor purchase that grew out of the adaptive-photonics research.

The deliberately short fresh-session instruction is:

> Read `PROCESS.md` and run the Swedish OLED monitor watch.

Everything needed to understand that instruction should live here or in the files it explicitly links.

## Sources of truth

- `PROCESS.md` — repeatable pseudo-skill / operating procedure.
- `SCHEMA.md` — data model, identity rules, verification states, and invariants.
- `sources/retailers.yaml` — persistent retailer registry. "All major retailers" means the enabled required entries here, not whatever an agent happens to remember.
- `sources/discovery_sources.yaml` — aggregators, price-history sites, and manufacturer-catalog discovery sources.
- `models/monitors.yaml` — persistent monitor catalogue. Models remain here after disappearing from retail.
- `shortlist/current.yaml` — current "in the running", price-watch, verification, and exclusion state.
- `price_snapshots/YYYY-MM-DD.yaml` — immutable dated offer observations plus run-coverage metadata.

The human purchase criteria remain authoritative in [../21_monitor_purchase_context.md](../21_monitor_purchase_context.md).

## The three data classes

Keep these strictly separate:

1. **Model facts** — comparatively stable; belong in `models/monitors.yaml`.
2. **Offers/prices** — volatile observations; belong in dated snapshots.
3. **Current interest/status** — human-specific evaluation; belongs in `shortlist/current.yaml`.

A price is never a model property.

A monitor leaving the shortlist does not remove it from the catalogue.

A retailer failing to return data does not mean a product disappeared.

## Default scope

Discover broadly around:

- roughly 26.5–32 inches;
- 3840×2160 / 4K;
- OLED-family panels;
- Sweden-accessible consumer purchase.

Flat panels are purchase-eligible. Curved products can be catalogued for market completeness but remain excluded while the current flat-only requirement stands.

Do **not** restrict discovery to the current shortlist. The entire point is to find obscure models and weird Swedish deals.

## Price truth

Manufacturer MSRP is not Swedish street price.

Retailer pages are preferred for that retailer's current listed price. Aggregators remain valuable for:

- discovering obscure models;
- discovering obscure retailers;
- historical pricing;
- finding suspicious deals worth opening directly;
- cross-checking.

Contradictory observations are preserved rather than "resolved" by deleting whichever one is inconvenient.

## Human value philosophy

The maintainer is cheap in either direction.

A high absolute price can be good value if it buys a qualitatively different, long-lived result. A low absolute price can be bad value if it buys an intermediate compromise likely to be replaced.

The watch therefore tracks **price discontinuities and resurrection thresholds**, not merely the numerically cheapest SKU.

And yes: Mr. Samtron remains employed.
