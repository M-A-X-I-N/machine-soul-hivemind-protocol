# Monitor-watch schema and invariants

Canonical structured files use YAML because it is human-editable and straightforward for agents/scripts to traverse.

This is a semantic schema rather than a formal JSON Schema.

## Stable model IDs

Use:

~~~text
<manufacturer>_<normalized-model>
~~~

Examples:

~~~text
dell_aw2725q
asus_xg32ucwmg
philips_32m2n8900
~~~

A model ID represents a product identity, not a set of specifications.

Regional variants remain under one model only while evidence says they are materially the same product. Split them when hardware or relevant behavior differs.

## Stable retailer IDs

Examples:

~~~text
inet
webhallen
elgiganten
proshop
amazon_se
~~~

Do not rename IDs just because branding/capitalization changes.

## Verification states

Use field- or section-level states when useful:

- `verified_primary` — manufacturer/official source.
- `verified_independent` — reliable measured independent source.
- `retailer_only` — retailer page only.
- `aggregator_only` — price-comparison/discovery source only.
- `conflicting` — credible sources disagree.
- `unknown` — not established.

Do not turn uncertainty into fake percentage confidence.

## Market status

Suggested catalogue values:

- `available`
- `announced`
- `preorder`
- `scarce`
- `unavailable`
- `discontinued`
- `unknown`

Market status is not shortlist status.

## Shortlist status

- `active` — genuinely in current purchase consideration.
- `strong_watch` — highly interesting if price/verification moves slightly.
- `price_watch` — structurally attractive, currently overpriced.
- `needs_verification` — potentially interesting, but identity/spec/offer uncertainty blocks confidence.
- `rejected_for_now` — not attractive currently; preserve the reason and resurrection condition.
- `excluded_requirement` — violates a hard requirement such as flat-only.
- `obsolete` — superseded for this purchase.
- `unavailable` — no current offers but retain history.

These are user-specific states, not objective product rankings.

## Filtered preference lanes

The shortlist may contain **orthogonal filtered lanes** in addition to the normal purchase-status list.

The first defined lane is:

~~~yaml
true_rgb_stripe_lane:
  purpose: ...
  rules:
    inherit_all_normal_purchase_rules: true
    price_and_value_rules_apply_normally: true
    strict_subpixel_requirement: rgb_stripe
  candidates:
    model_id:
      status: price_watch
~~~

Semantics:

- all normal purchase rules apply unless a lane explicitly adds or tightens a requirement;
- price/value logic continues to apply normally;
- the same model can appear in the normal shortlist and a filtered lane;
- lane membership means "passes the extra filter", not "recommended regardless of price";
- normal statuses such as `active`, `strong_watch`, `price_watch`, `needs_verification` and `excluded_requirement` are reused inside the lane;
- strict technology filters must define exactly what qualifies.

For the strict true-RGB lane, `rgb_stripe` means a conventional/explicit true RGB stripe arrangement. Layouts such as `rgb_q_stripe` and `matrix_pure` remain adjacent-interest technologies unless the requirement is explicitly broadened.

## Snapshot identity

Snapshots are identified by their **run-start instant**, not merely the calendar date.

Canonical filename form:

~~~text
YYYY-MM-DDTHHMMSS+HHMM.yaml
~~~

Example:

~~~text
2026-10-01T044527+0200.yaml
~~~

The filename intentionally omits colons so the repository remains Windows-friendly.

Snapshot metadata keeps normal ISO-8601:

~~~yaml
snapshot:
  date: 2026-10-01
  started_at: 2026-10-01T04:45:27+02:00
  finished_at: 2026-10-01T04:48:22+02:00
  timezone: Europe/Stockholm
~~~

The original first-run `2026-10-01.yaml` predates this rule and remains an immutable legacy snapshot. Do not rename it and fabricate an unknown run-start time.

## Offer source kinds

- `retailer_direct`
- `manufacturer_direct_store`
- `aggregator`
- `price_history_service`
- `marketplace`

## Condition

- `new`
- `open_box`
- `demo`
- `refurbished`
- `used`
- `unknown`

## Stock

- `in_stock`
- `supplier_stock`
- `preorder`
- `backorder`
- `out_of_stock`
- `discontinued`
- `unknown`

## Source freshness

Where possible record:

- retrieval date/time
- source crawl/index age
- explicit price timestamp
- campaign end

Useful qualitative flags:

- `fresh_direct`
- `direct_but_cached`
- `recent_aggregator`
- `stale_or_expired`
- `unknown`

## Catalogue shape

Recommended pattern:

~~~yaml
models:
  example_model:
    manufacturer: Example
    model: EXAMPLE
    regional_variants: []
    size_in: 31.5
    resolution: 3840x2160
    shape: flat
    panel:
      family: WOLED
      generation: unknown
      subpixel: unknown
    coating:
      type: unknown
    refresh:
      native_hz: 240
      dual_mode:
        resolution: 1920x1080
        hz: 480
    connectivity:
      displayport: unknown
      hdmi: unknown
      usb_c_pd_w: null
      kvm: unknown
    warranty:
      years: null
      burn_in_explicit: unknown
    measured:
      minimum_sdr_nits: null
    market_status: unknown
    verification: {}
    sources: []
    notes: []
~~~

Use `null` or `unknown` instead of filling gaps from intuition.

## Offer shape

~~~yaml
- model_id: example_model
  retailer_id: inet
  source_kind: retailer_direct
  condition: new
  price_sek: 8990
  shipping_sek: 0
  total_sek: 8990
  stock: in_stock
  restrictions:
    campaign: false
    member_only: false
    coupon_required: false
  exact_identity:
    mpn: null
    ean: null
  url: https://...
  freshness: fresh_direct
  notes: []
~~~

Shipping may be `null` when unknown. Do not silently assume zero.

## Coverage

Every run records expected versus achieved coverage.

~~~yaml
coverage:
  required_retailers_expected: 12
  required_retailers_checked: 11
  failed:
    - retailer_id: example
      reason: "Search/index inaccessible in this run."
~~~

A failed retailer is not equivalent to an empty retailer.

## Persistence

Never remove a model simply because it disappears from retail. Historical presence and prices remain useful.

Never delete a retailer because one run cannot query it. Disable it explicitly if it should leave the routine.

## Denormalization

The shortlist may repeat a few convenience facts such as size, panel family, coating and refresh because the human explicitly wants it easy to scan.

The catalogue remains authoritative.

If duplicated values conflict, fix the shortlist copy; do not create a second source of truth.
