# Swedish OLED monitor watch procedure

This is the repeatable pseudo-skill.

A fresh agent should be able to execute the watch by reading this file and its linked sources of truth, without needing the conversation that created it.

## 0. Read context and prior state

Read, in order:

1. `../21_monitor_purchase_context.md`
2. `README.md`
3. `SCHEMA.md`
4. `sources/retailers.yaml`
5. `sources/discovery_sources.yaml`
6. `models/monitors.yaml`
7. `shortlist/current.yaml`
8. the newest file under `price_snapshots/`

Repository state is authoritative over remembered chat context.

## 1. Establish the run identity

Record:

- local run-start timestamp;
- timezone: `Europe/Stockholm`;
- currency: SEK;
- previous snapshot;
- a filesystem-safe timestamp slug derived from run start.

Use full ISO-8601 inside YAML, for example:

~~~text
2026-10-01T04:45:27+02:00
~~~

Use a colon-free local timestamp in the filename:

~~~text
2026-10-01T044527+0200.yaml
~~~

A completed snapshot is immutable historical observation. Every later sweep — even minutes later on the same date — creates a new timestamped file.

## 2. Sweep required retailers directly

Visit every retailer in `sources/retailers.yaml` with:

~~~yaml
enabled: true
sweep_required: true
~~~

Search broadly enough to discover products not already in the catalogue.

Useful queries/categories include:

- OLED monitor / OLED bildskärm / OLED gamingskärm
- 4K OLED
- 3840x2160 OLED
- 27 OLED 4K
- 32 OLED 4K
- 240 Hz OLED
- 480 Hz / dual mode

Do not search only for known model names.

Record every in-scope offer found.

If a retailer cannot be searched or its catalogue cannot be retrieved, record a coverage failure. **Failure is not zero inventory.**

### Offer fields

Capture where available:

- `model_id`
- exact MPN / EAN / regional suffix
- item price
- shipping
- effective total
- stock state
- new/open-box/demo/refurbished condition
- campaign/member/coupon restrictions
- campaign end date
- source URL
- source freshness
- notes

Never mix open-box/demo pricing into the new-product price series.

## 3. Sweep aggregators and discovery sources

Visit every enabled required source in `sources/discovery_sources.yaml`.

At minimum:

- Prisjakt
- PriceRunner
- manufacturer Sweden/EU catalogues

Use optional sources when they improve coverage, including Priceway, Priskolla and SweClockers Priser.

Use aggregators to discover:

- models the direct sweep missed;
- additional retailers;
- price-history clues;
- contradictory prices;
- exact EAN/MPN identity.

Do **not** trust aggregator engineering metadata without primary verification. Known examples include flat monitors marked curved, coating mismatches, and refresh-rate/model-name confusion.

## 4. Grow the retailer registry

When a discovery source exposes a retailer absent from `sources/retailers.yaml`:

1. add it;
2. classify it;
3. note Sweden-based / marketplace / Nordic cross-border / other status;
4. deliberately decide whether future runs must sweep it directly.

Do not redefine "all major retailers" from scratch on every run.

## 5. Grow the model catalogue

Every new in-scope product gets a stable `model_id`.

Identity is manufacturer + exact model/SKU lineage, **not specifications**.

Preserve when known:

- marketing model
- regional suffix
- MPN
- EAN/GTIN
- relationship to sibling variants

Do not assume similarly named regional variants are identical until verified.

## 6. Verify model facts

For every new model, and every existing model with conflicting facts:

### Primary sources

Prefer manufacturer material for:

- size
- resolution
- flat/curved
- panel family
- refresh modes
- ports
- USB-C power
- KVM
- warranty duration
- explicit burn-in wording
- regional identity

### Independent measured sources

Prefer instrumented reviewers for:

- minimum SDR luminance
- text clarity
- subpixel layout
- coating behavior
- ABL / ASBL / static dimming
- near-black behavior
- firmware annoyances
- real HDR/SDR performance

Represent uncertainty explicitly instead of inventing precision.

## 7. Write the timestamped snapshot

Create:

~~~text
price_snapshots/YYYY-MM-DDTHHMMSS+HHMM.yaml
~~~

The timestamp is the **run start** in Europe/Stockholm. Store both `started_at` and `finished_at` as full ISO-8601 metadata inside the snapshot.

Include:

- run metadata
- coverage summary
- per-retailer result
- discovery-source coverage
- direct retailer offers
- aggregator/price-history observations
- contradictions/stale-data notes
- newly discovered models
- newly discovered retailers
- unresolved verification work

Never overwrite an older snapshot merely to make it "current."

## 8. Refresh shortlist state

Update `shortlist/current.yaml`.

Rules:

- do not delete rejected models;
- preserve why they were rejected;
- preserve the price threshold that would resurrect price-only rejects;
- curved products remain catalogued but excluded while flat-only is a requirement;
- price changes can promote/demote interest without changing model facts.

### Filtered-lane refresh

If `shortlist/current.yaml` defines one or more orthogonal filtered lanes:

1. inherit the normal purchase rules unless the lane explicitly overrides them;
2. apply the lane's extra hard requirement(s);
3. keep normal price/value logic fully active unless the lane explicitly says otherwise;
4. reuse the normal shortlist statuses inside the lane;
5. preserve strict technology definitions — e.g. RGB Q-Stripe or Matrix-Pure do not satisfy a strict conventional RGB-stripe requirement;
6. allow the same monitor to appear in the normal shortlist and one or more filtered lanes;
7. mention promotions/demotions inside filtered lanes when a market-watch run changes them.

## 9. Report only meaningful movement

Summarize:

- newly discovered models
- newly discovered retailers
- large price movements
- crossed buy/watch thresholds
- shortlist promotions/demotions
- filtered-lane promotions/demotions
- suspicious or stale listings
- verification conflicts
- genuinely stupid deals

Do not dump every unchanged row into chat unless asked.

## 10. Validate before commit

Check:

- every offer/shortlist `model_id` exists in `models/monitors.yaml`;
- every retailer ID exists in `sources/retailers.yaml`;
- snapshot filename/run-start timestamp and ISO metadata agree;
- required-retailer coverage reconciles;
- old snapshots remain unchanged;
- source URLs are retained;
- aggregator-only engineering claims did not silently become verified facts;
- YAML remains mechanically simple and human-readable.

## First-run lesson

The first structured run immediately demonstrated why immutable source-tagged observations are necessary:

- Prisjakt surfaced Dell AW2725Q from **6,960 SEK**, while Inet's opened retailer page showed **8,990 SEK**.
- An indexed Elgiganten result retained LG 32GX850A-B at **6,997 SEK**, while the opened retailer page showed **8,999 SEK**.

Both observations are useful.

Neither should silently overwrite the other.
