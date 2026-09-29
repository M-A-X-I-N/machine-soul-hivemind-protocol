# Adaptive compositor architecture

This is a design hypothesis, not a final architecture.

## Core principle

Keep three models separate:

1. **Content model** — background image + shaped text + theme semantics.
2. **Perception model** — decides how much conflict exists and what intervention is justified.
3. **Presentation model** — converts the final linear scene to the platform/display.

Never let Wayland protocol objects, DXGI enums, or monitor-specific hacks leak into the perception model.

## Internal color representation

Recommended default:
- floating-point;
- linear-light;
- known primaries, probably Rec.709/sRGB initially;
- scene values allowed above nominal SDR white;
- explicit conversion at image ingress and platform egress.

Do not perform local contrast math on gamma-encoded RGB.

Useful luminance proxy for linear Rec.709/sRGB:

```text
Y ≈ 0.2126 R + 0.7152 G + 0.0722 B
```

This is useful, but not a complete perceptual model.

## Inputs

Per frame:
- background image in linear working space;
- glyph coverage texture;
- glyph semantic metadata (token class, selection, cursor, active line);
- viewport geometry;
- display capability snapshot;
- user tuning profile;
- previous temporal state.

Optional future:
- depth map;
- eye tracking;
- ambient light sensor;
- HDR calibration measurements;
- font grade axis;
- monitor subpixel geometry.

Do not require optional inputs for MVP.

## Glyph protection field

Start from glyph alpha/coverage `G(x,y)`.

Derive:
- `G_exact`: exact coverage;
- `G_binary`: thresholded stroke region;
- `G_near`: morphological dilation;
- `G_falloff`: blurred/distance falloff around strokes.

This field tells the background algorithm where destruction is allowed/needed.

An SDF generated from the glyph mask could make distance-aware suppression cheap even if the glyph itself is rendered from a normal coverage bitmap.

## Analyze background conflict

At minimum compute near each glyph:

### Luminance
- local mean;
- luminance directly under glyph stroke;
- min/max;
- local dynamic range.

### Detail
- gradient magnitude;
- local variance;
- high-pass energy;
- multi-scale detail energy.

### Edge conflict
Future experiment:
- compare background gradient orientation with nearby glyph-edge orientation;
- crossing/parallel strong edges may need stronger suppression than smooth detail.

### Chroma
A colorful background edge may interfere with syntax colors even when luminance contrast is decent.

## Conceptual conflict score

```text
conflict =
    w_luma   * luminance_conflict
  + w_detail * detail_energy
  + w_edge   * edge_alignment_conflict
  + w_chroma * chroma_conflict
  + w_size   * small_glyph_penalty
```

Then modulate by the glyph protection field.

Goal: **minimal intervention for reliable recognition**, not maximum contrast.

## Background interventions

### Luminance attenuation

```text
background_linear *= attenuation
```

Use smooth bounded curves.

### Contrast compression

Move pixels toward local mean rather than uniformly dimming:

```text
B' = mean + k * (B - mean),  0 <= k <= 1
```

This preserves large scene structure while shrinking texture contrast.

### High-frequency suppression

Use multi-scale decomposition:

```text
B = low_frequency + detail
B' = low_frequency + detail * k
```

with smaller `k` near glyphs.

This is probably closer to the objective than blur.

### Edge-aware/guided suppression

Use text mask as part of filter policy so image edges are preserved where harmless but sacrificed where they collide with strokes.

### Chroma reduction

Reduce chroma locally without destroying luminance structure unnecessarily.

### Hue-aware syntax protection

Very future:
if a syntax token and underlying image edge occupy confusingly similar hue/luminance, suppress only conflicting chroma.

## Text interventions

Keep conservative:
- target text luminance adjustment;
- antialiasing mode;
- perhaps tiny grade/weight changes;
- semantic brightness tiers.

Avoid per-glyph luminance pumping inside a token. Background may vary per pixel; foreground policy should probably vary more slowly (run/token/line).

## Target-luminance mode

A future HDR-capable path can express desired physical targets approximately.

Illustrative low-luminance hypotheses for this maintainer:

```text
background mean:           3–10 nit
background local peak cap: 10–20 nit
ordinary text:             20–40 nit
active text:               25–50 nit
cursor/critical UI cap:    40–70 nit
```

These are experiments, not prescriptions.

SDR fallback should express the same relationships in normalized relative units.

## Absolute versus relative policy

Core policy should support both:

```text
struct LuminancePolicy {
    optional<float> absolute_nits;
    float relative_to_reference_white;
    float min_contrast;
    float max_contrast;
}
```

Platform backend resolves actual output based on:
- current SDR reference white;
- HDR mode;
- display capability;
- calibration.

This avoids turning one monitor's scRGB values into universal truth.

## Temporal adaptation

Track:
- current conflict;
- filtered conflict;
- previous suppression;
- attack coefficient;
- release coefficient.

Useful behavior:
- protect quickly when readability drops;
- relax slowly when conflict disappears.

Avoid dark halos visibly pumping while scrolling.

## Spatial falloff

Hard rectangles behind code defeat the aesthetic objective.

Use:
- distance transform from glyph edges;
- separate inner/outer radii;
- strong intervention directly under stroke;
- weaker intervention nearby;
- none beyond threshold.

At 4K, test whether a few physical pixels of soft falloff are perceptually invisible but useful.

## Multi-scale decomposition

Promising model:

```text
background
  ├── L0 very-low-frequency illumination/large gradients
  ├── L1 large structures
  ├── L2 medium detail
  ├── L3 fine detail
  └── L4 noise/texture
```

Near glyphs:
- preserve L0/L1 almost fully;
- attenuate L3/L4 aggressively;
- conditionally attenuate L2;
- preserve hue unless it conflicts.

This directly attacks the complaint with global blur: **keep large-scale depth while deleting only detail that competes with text**.

## Background-depth preservation hypothesis

Depth cues live at multiple scales:
- perspective/converging lines;
- occlusion;
- relative size;
- atmospheric gradients;
- large foreground/background structures.

A huge blur removes many of them. A glyph-local multi-scale filter should preserve most because:
- intervention occupies only small regions;
- low-frequency structure remains;
- detail returns immediately outside glyph proximity.

This hypothesis should be explicitly tested.

## Selection and cursor

Selections are hard because a solid selection rectangle is itself a background.

Options:
- treat selection as semantic foreground plane;
- simplify wallpaper more strongly under selection;
- use outline selection;
- allow selection to temporarily prioritize function over subtlety.

Cursor:
- needs immediate visibility;
- can have higher luminance;
- should not become an annoying HDR beacon.

## Syntax colors

Policy/tuning may benefit from perceptual spaces such as Oklab/OKLCH.

W3C CSS Color 4:
https://www.w3.org/TR/css-color-4/

Final physical-light composition should still happen in linear RGB.

Think:
- analyze/tune in perceptual space where useful;
- render/composite in linear RGB.

## Performance

At 4K/240 Hz:
- 8.29 million pixels × 240 ≈ 2 billion pixel updates/s before multi-pass filtering.

GPUs can handle massive pixel throughput, but full-frame multi-scale work every frame is wasteful for a mostly static editor.

Use:
- cached background analysis;
- dirty regions/tiles;
- lower-resolution analysis buffers where acceptable;
- incremental text-mask updates;
- recomputation only on meaningful image/viewport change.

## Dirty-region model

Maintain:
- background-analysis cache;
- text-mask tiles;
- conflict tiles;
- temporal state.

Invalidate on:
- scroll;
- edit;
- cursor move;
- selection change;
- font/theme change;
- resize;
- wallpaper frame/change;
- display profile change.

A blinking cursor should not trigger full 4K image decomposition 240 times per second.

## Animated wallpaper

If supported:
- analysis may need each frame;
- lower-res analysis can drive full-res transform;
- temporal stability becomes harder;
- motion may reduce burn-in risk but increase distraction.

Later scope.

## Security/privacy tangent

If implementation obtains editor pixels by screen capture:
- code becomes captured texture;
- screen-capture permissions/security apply;
- protected-content behavior differs;
- latency rises;
- reliable glyph extraction becomes harder.

Prefer cooperative integration or owned rendering over capture.

## Metrics

Do not evaluate only screenshots.

Measure:
- character/pseudoword identification error;
- time to discriminate ambiguous code fragments;
- proofreading error rate;
- minimum comfortable font size;
- subjective fatigue;
- preserved-background-depth rating;
- intervention visibility;
- temporal stability;
- GPU time;
- power;
- OLED dimming behavior.

Adversarial backgrounds:
- branches/cables behind stems;
- checkerboards;
- bright windows behind light text;
- saturated edges matching syntax colors;
- star fields;
- high-frequency foliage;
- smooth gradients;
- faces;
- perspective architecture.

## Architecture sketch

```text
                        ┌────────────────────┐
                        │   User policy      │
                        └─────────┬──────────┘
                                  │
┌──────────────┐          ┌───────▼─────────┐
│ Background   │─────────►│ Image analysis  │
└──────────────┘          └───────┬─────────┘
                                  │
┌──────────────┐          ┌───────▼─────────┐
│ Text shaper  │─────────►│ Glyph masks     │
└──────┬───────┘          └───────┬─────────┘
       │                           │
       │                   ┌───────▼─────────┐
       └──────────────────►│ Conflict model  │
                           └───────┬─────────┘
                                   │
                           ┌───────▼─────────┐
                           │ Temporal policy │
                           └───────┬─────────┘
                                   │
                           ┌───────▼─────────┐
                           │ Linear renderer │
                           └───────┬─────────┘
                                   │
                 ┌─────────────────┴─────────────────┐
                 ▼                                   ▼
        Windows Advanced Color             Wayland color mgmt
                 │                                   │
                 └─────────────────┬─────────────────┘
                                   ▼
                                Display
```
