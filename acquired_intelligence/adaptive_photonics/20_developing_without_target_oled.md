# Developing without the target OLED

Research/design note: it is meaningfully possible to develop **most of the complete system without owning the final HDR OLED**, provided luminance is treated as an explicit numeric contract rather than something tuned by eye on the developer's monitor.

This is not merely "the selective blur can be prototyped in SDR."

The majority of the actual renderer can be developed, tested, replayed, fuzzed, and safety-bounded without an OLED.

The part that genuinely requires target hardware is the last-mile perceptual calibration and panel-behavior validation.

## Core rule

Never encode brightness policy as an arbitrary display-relative float whose meaning depends on whatever monitor the developer currently owns.

Bad:

```text
text_brightness = 1.7
wallpaper_brightness = 0.2
```

Better:

```text
wallpaper_target_nits
text_target_nits
ui_reference_white_nits
normal_output_ceiling_nits
absolute_safety_ceiling_nits
```

Then convert those domain-level luminance targets into platform-specific representations only at the presentation boundary.

That keeps:
- Windows scRGB details;
- Wayland Windows-scRGB/reference-white semantics;
- SDR fallback;
- display calibration;
- compositor mapping;

out of the core perception/rendering algorithm.

## Why accidental flashbangs are avoidable

HDR does **not** mean:

> normalized value 1.0 = whatever absurd maximum brightness the monitor can produce.

Correctly tagged HDR/scRGB output carries luminance semantics.

On Windows Advanced Color, the scRGB stimulus model uses the familiar nominal relationship where linear RGB 1.0 corresponds to 80 cd/m², while the user's SDR-white setting and display mapping still need to be respected.

On Wayland, Windows-scRGB has similar stimulus semantics but different/explicit reference-white handling; this distinction belongs in the platform backend.

The important point is architectural:

> A 1500-nit-capable OLED does not need to emit 1500 nits merely because it receives a white application pixel.

The renderer can therefore enforce conservative luminance targets long before target hardware exists.

## Mandatory safety model

HDR output should be impossible unless the renderer can assign known meaning to every output value.

Possible configuration:

```text
preferred_wallpaper_average_nits
preferred_wallpaper_peak_nits
preferred_text_nits
preferred_ui_white_nits
normal_pixel_ceiling_nits
absolute_safety_ceiling_nits
```

The exact defaults are future tuning questions.

The invariant is more important than the numbers.

### Example paranoid policy

```text
if output_semantics_unknown:
    disable_hdr_output

if any_pixel_nits > absolute_safety_ceiling:
    clamp_or_abort_frame

if text_pixel_nits > text_ceiling:
    clamp

if frame_average_nits > configured_desktop_average_ceiling:
    warn_or_clamp
```

The renderer should be able to run in an intentionally conservative mode where it **cannot** generate unexpectedly bright desktop content.

## Useful diagnostics

Every debug build should be able to report frame luminance statistics such as:

```text
background:
    median
    p95
    p99
    maximum

text:
    median
    p95
    p99
    maximum

full frame:
    average
    p99
    maximum
    percentage above 80 nit
    percentage above 100 nit
    percentage above 200 nit
```

A nit heatmap is also useful:

```text
<   1 nit   very dark
<  10 nit   dark
<  50 nit   ordinary low-luminance content
< 100 nit   bright desktop content
< 200 nit   high desktop/HDR UI region
> ceiling   flagged
```

The exact visualization colors are irrelevant; the important feature is immediate exposure of accidental high-luminance pixels.

## Separate UI/code from HDR highlight headroom

A monitor having a 1000+ nit peak does **not** imply code should ever approach that.

A sensible architecture should classify content:

```text
wallpaper / scene
    ↓
low, comfortable luminance

code and ordinary UI
    ↓
desktop/reference-white region

optional HDR image highlights
    ↓
strictly bounded extended headroom
```

A very good early safety rule is:

> ordinary code text is not allowed to enter the "HDR highlight" range at all.

HDR is valuable because it provides:
- extended precision;
- larger luminance separation;
- clean low/high relationships;
- display-aware mapping;

not because text should become a miniature welding arc.

## What can be developed without OLED hardware

A large majority of the system:

### Core algorithm
- glyph protection masks;
- distance fields;
- local luminance analysis;
- spatial-frequency/detail analysis;
- multi-scale decomposition;
- conflict scoring;
- chroma analysis;
- conditional intervention;
- temporal hysteresis;
- dirty-region logic.

### Text
- shaping;
- glyph-mask generation;
- grayscale/subpixel experiments;
- font-size/PPI simulations;
- adversarial glyph-discrimination tests.

### Rendering
- FP16 linear-light pipeline;
- shader graph;
- color-space metadata;
- premultiplied-alpha correctness;
- HDR/SDR code paths;
- deterministic frame replay;
- OpenEXR intermediate/debug dumps.

### Platform
- Windows Advanced Color/scRGB backend;
- Wayland color-management backend;
- Vulkan/D3D/libplacebo plumbing;
- capability queries;
- reference-white translation;
- fallback behavior;
- multi-monitor state handling.

### Safety
- hard luminance ceilings;
- frame statistics;
- clipping detection;
- safe-mode fallback;
- unknown-semantics refusal;
- regression tests for maximum output.

### Simulated visualization

An SDR monitor can display different *exposure views* of an HDR frame:

```text
view A: map 0–20 nit into SDR range
view B: map 0–100 nit into SDR range
view C: map 0–500 nit into SDR range
view D: false-color luminance heatmap
```

This does not reproduce the real perceptual HDR experience.

It **does** allow inspection of:
- shadow structure;
- clipping;
- relative luminance policy;
- whether a local filter pushed detail below intended thresholds;
- whether accidental high values exist.

## What cannot be honestly finished without the target display

### Near-black perception

OLED near-black behavior differs substantially from ordinary LCD.

Questions requiring real hardware:
- does 0.2–2 nit wallpaper detail remain visible?
- does the panel crush intended shadow detail?
- do near-black gradients band?
- does the chosen black floor preserve depth?

The software can mathematically generate these values.

Only the physical display can tell us whether they remain perceptually useful.

### Bright-on-black comfort

A mathematically reasonable relationship such as:

```text
wallpaper ≈ a few nits
text      ≈ tens of nits
```

may still feel more aggressive on OLED because the surrounding black is much closer to zero emission than on an LCD.

This is likely a tuning problem:
- reduce text from e.g. 70 to 45 nit;
- lift the wallpaper floor;
- soften the contrast.

It should not require architectural redesign if the system is correctly parameterized.

### ABL / ASBL / static dimming

OLED power and protection behavior is physical panel/firmware behavior.

Need real hardware to learn:
- whether large bright regions trigger ABL;
- whether a static coding screen triggers ASBL;
- whether the panel dims while reading;
- whether normal typing prevents static dimming;
- whether luminance policy and panel protection interact unpleasantly.

### Refresh-dependent low-luminance behavior

Need hardware for:
- VRR flicker;
- low-refresh gamma shifts;
- temporal dithering/FRC behavior;
- sample-and-hold scrolling perception;
- very-dark gray stability.

### Actual monitor tone mapping

The renderer can guarantee:

> a correctly tagged value intended to represent X luminance was submitted.

It cannot guarantee:

> every physical monitor emits exactly X cd/m².

Real displays differ in:
- EOTF tracking;
- firmware;
- picture mode;
- calibration;
- peak/full-screen limits;
- user settings;
- panel state.

Final validation therefore needs:
- real display;
- ideally a colorimeter.

## Development confidence model

A useful rough split is:

```text
without target OLED:
    ~90–95% of software engineering can be completed

with target OLED:
    final perceptual tuning
    panel-behavior validation
    calibration
    comfort defaults
```

The exact percentage is intentionally approximate.

The key distinction is:

**missing OLED hardware blocks trustworthy defaults, not most implementation.**

## Hardware-free regression strategy

The renderer should have deterministic reference tests.

Example fixture:

```text
frame/
    wallpaper.exr
    glyph_mask.exr
    metadata.json
    display_profile.json
    policy.json
```

Tests can assert:

```text
max_output_nits <= safety_ceiling
text_max_nits <= text_ceiling
background_average_nits within expected range
no NaN / infinities
no unexpected clipping
cross-backend numerical agreement within tolerance
```

This is stronger than visually testing one developer monitor.

## Fake display profiles

Create synthetic profiles such as:

```text
dim_oled
    peak: 400 nit
    full_frame: 200 nit
    min: near zero

bright_oled
    peak: 1500 nit
    full_frame: 300 nit

ordinary_hdr_lcd
    peak: 600 nit
    min: 0.1 nit

sdr_display
    white: 80–200 nit relative model
```

Then fuzz:
- reference white;
- peak luminance;
- minimum luminance;
- gamut;
- HDR unavailable;
- metadata incomplete.

The renderer should remain safe under all of them.

## Unknown output semantics must fail closed

One important invariant:

> If the platform backend cannot establish how its output values are interpreted, it must not guess and emit HDR.

Fallback options:
1. use known-safe SDR;
2. clamp into ordinary reference-white range;
3. display a diagnostic and disable HDR mode.

Never let "unknown" mean "probably multiply by peak brightness."

## First real-OLED bring-up procedure

When target hardware finally exists:

1. Set monitor to conservative brightness.
2. Disable experimental highlight headroom initially.
3. Start with an intentionally low global safety ceiling.
4. Display grayscale/near-black test patterns.
5. Validate reference white.
6. Validate text target luminance.
7. Test static coding screen for ASBL.
8. Test scrolling and refresh behavior.
9. Test worst-case white-heavy source file.
10. Increase permitted headroom only after measurement/comfort validation.

If a colorimeter is available:
- measure requested vs emitted luminance;
- fit/record calibration;
- validate panel metadata;
- establish first-visible dark levels.

## Why developing without OLED may improve the architecture

Without target hardware, it is impossible to get away with:

```text
brightness = 1.37  // looked nice on my monitor
```

That forces:
- physical or explicitly relative units;
- clear platform conversion boundaries;
- synthetic display profiles;
- deterministic reference frames;
- hard safety ceilings;
- debug heatmaps;
- reproducible calibration state.

Those are all things the final renderer should have anyway.

Therefore the lack of an OLED during early development is not merely tolerable.

It may actively prevent accidental coupling to one monitor.

## Bottom line

The project can be developed very far without the final OLED.

What cannot be completed honestly without real HDR/OLED hardware is the statement:

> these defaults are comfortable, preserve the intended image depth, and behave correctly on a real low-luminance OLED desktop.

What **can** be guaranteed in software long before then is:

> this renderer knows what luminance it intends to emit, refuses unknown HDR semantics, enforces conservative ceilings, and cannot casually turn a code caret into a 1500-nit flashbang.
