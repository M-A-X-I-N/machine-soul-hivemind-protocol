# Monitor purchase context

Conversation snapshot: 2026-09-30.

This document deliberately records the **actual human buying criteria** for the monitor search rather than pretending the correct purchase can be derived from a spec-sheet sort.

It belongs in this research directory because the eventual target monitor also affects adaptive-photonics development and validation.

## Current physical setup

Current center monitor:
- approximately 27";
- 1920×1080;
- bought roughly around 2013;
- panel type not remembered with confidence (VA/IPS uncertainty is irrelevant to the buying goal);
- typically used at extremely low brightness;
- sometimes viewed from a frankly stupid distance: **roughly 30 cm**.

Side monitors:
- another roughly 24" older LCD, received around Christmas 2008/2009;
- **Samtron 74V**, ancient, legendary, possibly old enough to predate the maintainer, refuses retirement and performs light duties.

Mr. Samtron is infrastructure and shall not be casually decommissioned.

## Monitor arrangement is intentionally not normal

Do not assume:
- three equal monitors;
- touching bezels;
- equal distance;
- symmetrical arc.

The real arrangement frequently includes:
- large odd-shaped gaps;
- center monitor substantially closer to the viewer;
- side monitors at idiosyncratic angles/distances;
- no requirement for geometric continuity across screens.

Conversation sketch, expressed approximately:

```text
              large back/side monitor region
        ┌──────────────────────────────────┐
        │                                  │
        │                                  │
        └───────────────────────┐          │
                                │          │

           side display      center display
               \              [close]
                \             /
                 viewer / chair

       another side display can be much farther
       away with large gaps between everything
```

The important buying consequence:

> A 27" or 32" replacement does not need to preserve a conventional triple-monitor geometry.

The center monitor can simply move backward or forward as required.

## Viewing-distance behavior

The maintainer sometimes sits around **30 cm from a 27" monitor** because filling more of the visual field is desirable.

This is acknowledged as objectively too close for a conventional setup.

A 32" monitor therefore has an extra advantage beyond physical size:
- it can be moved farther back;
- it can still occupy a large visual angle;
- 4K pixel density remains a huge upgrade over the current 27" 1080p panel.

However, 32" is not mandatory.

The correct purchase logic is:

> search 27" and 32" together, then let Swedish price and panel quality decide.

A ridiculous 27" bargain remains desirable even if the current leaning is toward 32".

## Primary workload

Programming / desktop work is the main reason the display-resolution problem matters.

Important objective:
- fit more code on one physical display;
- use smaller logical font sizes without losing immediate glyph discrimination;
- reduce the need to move the head between monitors;
- improve tiny-text sharpness substantially.

Current pain:
- low-PPI 1080p text becomes difficult to parse at small sizes;
- the issue is not literal readability but instant recognition of ambiguous glyph clusters.

Therefore:
- 4K matters;
- physical PPI matters;
- subpixel arrangement matters somewhat;
- coating/sharpness matters;
- conventional RGB stripe can justify a **reasonable** premium.

## Gaming behavior

Gaming matters enough that OLED/high refresh is attractive, but gaming feature premiums must remain rational.

Two very different modes:

### Pretty / cinematic / normal games

Likely:
- 4K;
- roughly 60 FPS or whatever looks good;
- HDR/OLED image quality valued strongly;
- side monitors may simply be switched off to maximize dark-room immersion.

### Competitive-shooter brain

The maintainer is a Counter-Strike player at heart.

The desired philosophy is unironically:

```text
pretty mode:
    4K60-ish / high quality

competitive mode:
    cursed low render resolution
    × MAXIMUM PRACTICAL REFRESH RATE
```

A dual-mode monitor is therefore a **real feature**, not pure gamer marketing.

Examples:
- 4K 165/240 Hz normally;
- 1080p 330/480 Hz competitive mode.

The game itself can render below 1080p and be GPU-scaled into the monitor's high-refresh 1080p mode.

## Refresh-rate pricing philosophy

Higher refresh has value.

But value depends on **incremental price**, not abstract superiority.

Example:

```text
165 Hz model: 8,500 SEK
240 Hz model: 8,900 SEK

→ absolutely pay the 400 SEK
```

Versus:

```text
240/300 Hz model: 9,000 SEK
480/500 Hz model: 14,000 SEK

→ get fucked unless something else materially improves
```

The user is not feature-averse.

The user is **bad-value-averse**.

## The unusual definition of "cheap"

This is the central buying rule.

The maintainer is "cheap in either direction."

A 4,000 SEK monitor can be expensive if:
- it is a compromised intermediate purchase;
- a far better long-lived option exists for a few thousand more.

A 10,000 SEK monitor can be cheap if:
- it is an enormous qualitative upgrade;
- it avoids needing another replacement;
- the extra money buys substantial, visible capability.

Conversely:
- paying +50% for an abstract HDR tier;
- paying several thousand for DP 2.1 alone;
- paying huge money for refresh rates beyond already-extreme levels;

can be bad value even when technically superior.

The search must therefore look for **price/performance discontinuities**, not merely cheapest SKU.

## Swedish pricing is authoritative

Manufacturer MSRP and US pricing are not purchase prices.

All buying research should prioritize:
1. Swedish street prices;
2. Swedish/EU availability;
3. reputable Swedish retailers;
4. Swedish/EU warranty handling;
5. price-comparison services such as Prisjakt/PriceRunner where useful.

Manufacturer pages remain useful for:
- exact specifications;
- warranty wording;
- panel generation;
- supported modes.

They are not trusted as local price/availability truth.

## Size preference

Current lean:
- 32" is appealing;
- 27" remains completely acceptable;
- current 27" size itself is not a dissatisfaction.

Why 32" is interesting:
- larger physical area;
- can move farther back;
- still a huge PPI upgrade from 27" 1080p;
- perhaps more immersive for games/video.

Why 27" remains interesting:
- ~166 PPI at 4K;
- maximum small-text density/clarity;
- often substantially cheaper;
- still familiar physical size.

Rule:

> amazing deal beats size preference.

## Flat only

**Curved monitors are excluded.**

No amount of technical merit compensates for being curved for this purchase.

## Coating / environment

Work normally happens in a **very dark room**.

The room is not laboratory-dark because:
- two other non-OLED monitors may be on;
- they emit some ambient light.

However:
- all screens are normally dark-mode;
- current displays run at extremely low brightness;
- the side monitors are not aimed directly at the center panel;
- physical layout can include large gaps;
- for peak cinematic OLED use the side monitors may simply be switched off.

Therefore:

**glossy or very clear semi-glossy is preferred.**

Ambient-light handling is:
- relevant;
- worth considering as a tiebreaker;
- **not** worth hijacking the purchase decision.

QD-OLED ambient black raise is real but should not automatically disqualify it in this unusually dark setup.

## OLED motivation

The maintainer has never actually seen a "real OLED" display in person.

OLED is attractive because:
- per-pixel black;
- no uniformly illuminated LCD frame in a dark room;
- excellent response;
- HDR capability;
- gaming performance;
- direct relevance to adaptive-photonics experiments.

The especially compelling aesthetic concept is:

> black portions of the display can visually disappear into the dark room, leaving luminous content seemingly floating rather than living inside a glowing rectangle.

This is a strong subjective bonus.

## Brightness preference

Extremely low.

Known behavior:
- two current desktop monitors at brightness **0**;
- third at brightness **7** because **6 literally turns the display black**;
- phone commonly uses extra-dim/eye-comfort behavior.

Therefore purchase research must not overvalue peak brightness.

More relevant:
- minimum brightness;
- near-black gradation;
- black crush;
- low-luminance uniformity;
- static dimming;
- whether OLED protection makes a mostly-static coding desktop visibly pump.

Peak HDR brightness remains a bonus for games/media, not the primary purchasing metric.

## Subpixel / text quality

The maintainer expects basically any modern 4K OLED to be a mind-blowing improvement over current 1080p hardware.

Still:

> if sharper lines are available for a sensible premium, consider paying it.

Therefore:
- 27" 4K conventional RGB stripe is extremely interesting;
- 32" 4K RGB stripe is interesting if available;
- high-PPI QD-OLED remains perfectly acceptable when RGB-stripe premium becomes stupid;
- exact text measurements/photos matter more than theoretical fear of nonstandard subpixels.

RGB stripe is allowed a **real but finite** price premium.

## DisplayPort 2.1

No standalone value.

The current NVIDIA setup only needs the monitor to operate at its intended full modes through the available connection.

If:
- DP 1.4a + DSC;
- HDMI 2.1;
- another existing interface;

provides native resolution, refresh, HDR, 10-bit output, and 4:4:4/RGB correctly, then that is sufficient.

Do not pay a large premium merely for "DP 2.1."

## DSC

Not considered a meaningful disadvantage if:
- desired mode works;
- RGB/4:4:4 is preserved;
- HDR/10-bit works;
- image is visually lossless as intended.

A monitor that quietly drops to chroma subsampling is unacceptable for desktop text.

## KVM

Monitor KVM is understood as the same basic concept as server KVM, miniaturized into the display:

```text
desktop:
  video + USB upstream
         \
          monitor USB hub → keyboard/mouse/etc.
         /
laptop:
  USB-C video/data/charging
```

When the display input changes, the monitor can switch peripherals to the corresponding host.

For this purchase:
- useful bonus;
- not worth paying a large premium by itself.

## Burn-in

Programming is static enough that warranty treatment matters.

Research should explicitly record:
- warranty length;
- whether OLED burn-in is explicitly covered;
- exclusions/wording;
- retailer versus manufacturer handling.

Low brightness probably reduces wear materially, but does not make the concern disappear.

## Multi-monitor reality

The new OLED needs to coexist with older non-OLED monitors.

Do not assume the user is buying three OLEDs.

Research/review claims about ambient-light performance should therefore be interpreted under:
- one center OLED;
- two dim dark-mode LCD side displays;
- irregular angles/gaps;
- side displays optionally off for cinematic use.

This makes ambient-black resilience a **bonus/tiebreaker**, not a central requirement.

## Mr. Samtron

Mr. Samtron 74V:
- is ancient;
- may plausibly be older than the maintainer;
- rejected retirement;
- now performs light work;
- retains tenure.

Any proposed monitor arrangement must respect this institutional reality.

## Current target envelope for the next research pass

Search broadly around:

- 27–32";
- 3840×2160;
- OLED;
- flat;
- preferably glossy / very clear semi-gloss;
- Swedish street price ideally <= ~10,000 SEK;
- allow somewhat higher prices only for **materially different panel quality**, especially conventional RGB stripe or another directly relevant improvement;
- native refresh >= 165 Hz is already plenty;
- 240 Hz is desirable when incremental price is small;
- dual-mode 330/480 Hz is legitimately useful;
- ignore DP 2.1 premiums unless bundled with something else worthwhile.

Do not artificially cap research at 10,000 SEK:
expensive models should remain in the comparison if they define what a meaningful premium could buy.

The purpose is to find:
- stupid-good bargains;
- reasonable premiums;
- stupid premiums;
- models worth price-watching.
