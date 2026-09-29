# Perceptual models, visual angle, and evaluation metrics

This file exists because the renderer should eventually be able to answer a more serious question than "is the pixel contrast high enough?":

> At this viewing distance, display luminance, glyph size, background detail, and motion state, how visible/disruptive is this feature likely to be to a human observer?

A full human-vision model is overkill for an MVP, but the literature provides extremely useful variables and validation tools.

## Contrast sensitivity is frequency-dependent

Human contrast sensitivity is not flat across spatial frequency.

A visual feature can be described in **cycles per degree** (cpd): how many light/dark cycles fit into one degree of visual angle.

That immediately connects the project to:
- monitor PPI;
- physical font size;
- viewing distance;
- glyph stroke width;
- background texture scale.

The same 2-pixel branch behind a glyph is not perceptually the same on:
- 82 PPI at 60 cm;
- 163 PPI at 60 cm;
- 163 PPI at 100 cm.

A useful early utility should convert physical pixels and viewing distance into degrees/cycles-per-degree.

## castleCSF

castleCSF is an open contrast-sensitivity model from the University of Cambridge Graphics & Displays group.

Repository:
https://github.com/gfxdisp/castleCSF

Inputs include:
- spatial frequency in cycles/degree;
- temporal frequency in Hz;
- eccentricity in visual degrees;
- luminance in cd/m²;
- stimulus area in square degrees;
- background chromaticity;
- chromatic modulation direction;
- stimulus shape.

This is remarkably aligned with the adaptive-compositor problem.

Potential uses:

### Offline heuristic fitting

Do **not** begin by putting a MATLAB vision model in the frame loop.

Instead:
1. generate a grid of representative code/background conditions;
2. evaluate approximate visibility/sensitivity with castleCSF;
3. fit a simpler analytic/table-driven heuristic;
4. use that heuristic live.

### Parameterizing background-detail danger

Suppose a glyph stroke occupies a spatial-frequency band around the visual system's most sensitive range. Background energy in the same band may deserve stronger attenuation than equally energetic detail at much higher or lower frequency.

This suggests a conflict term like:

```text
weighted_detail =
    Σ_band CSF_weight(band, luminance, viewing_geometry)
         * background_energy(band)
         * glyph_overlap(band)
```

This is a research hypothesis, not a validated metric for text readability.

### Temporal behavior

Scrolling converts spatial texture into temporal modulation.

castleCSF includes temporal frequency, which means a future model could distinguish:
- static busy foliage behind code;
- the same foliage moving rapidly while scrolling;
- animated wallpaper;
- cursor blink.

That may help explain why an adaptation that looks fine in a screenshot becomes irritating in motion.

## Visual angle utility

A reusable utility should accept:

- panel diagonal/resolution or measured pixel pitch;
- viewing distance;
- pixel count / glyph dimensions.

Approximate small-angle relationship:

```text
visual_angle_rad ≈ physical_size / viewing_distance
visual_angle_deg = visual_angle_rad * 180 / π
```

Exact form:

```text
angle = 2 * atan(size / (2 * distance))
```

Then cycles/degree can be estimated from the spatial period.

This would make project tuning portable across display sizes instead of encoding "6 pixels is fine."

## Acuity and low luminance

Human high-frequency sensitivity drops at low adaptation luminance.

This is especially relevant because the maintainer deliberately runs screens at extremely low brightness.

Consequences:
- a high-PPI panel can physically resolve tiny glyphs that the eye still cannot discriminate comfortably at very low luminance;
- raising glyph luminance slightly may improve acuity more than changing its RGB contrast ratio suggests;
- there may be a practical lower limit where "make everything darker" stops helping.

This is a strong argument for measuring:
- minimum comfortable text luminance;
- minimum readable stroke size;
- error rate at several ambient/adaptation levels.

## Polarity

Previous research in this directory already notes evidence that positive polarity can improve fine-detail reading in some conditions, often attributed partly to pupil constriction.

That should not override the maintainer's dark-mode preference.

Instead preserve this as:
- evidence that pupil size/absolute luminance matter;
- motivation to test off-black / modest text luminance rather than assuming maximum darkness is ideal.

## APCA / readability models

APCA-style contrast models are useful because they treat text size/weight/polarity more seriously than a simple luminance ratio.

They are still not a complete solution for:
- textured backgrounds;
- per-pixel antialiasing;
- HDR absolute luminance;
- local spatial-frequency conflict.

Treat them as possible guardrails, not the compositor's objective function.

## Perceptual image-difference metrics

The project needs two almost-opposed metrics:

1. **Text should become more visible.**
2. **Background intervention should become less visible.**

Pixel RMSE cannot tell us either very well.

### PU21

PU21 is a perceptually uniform encoding for HDR luminance. It is designed so ordinary image-quality metrics can be applied more meaningfully to HDR values.

Potential use:
- encode reference and transformed wallpaper into PU21;
- compare with SSIM/MS-SSIM or other metrics;
- optimize for low perceptual change outside glyph-protection regions.

Do not confuse "low image difference" with "preserved depth"; still use human tests.

### Visual difference predictors

The Cambridge Graphics & Displays ecosystem includes perceptual video/display difference models such as FovVideoVDP/ColorVideoVDP.

Potential use:
- predict whether the darkening/detail-suppression halo itself should be noticeable;
- compare temporal artifacts between smoothing strategies;
- evaluate HDR differences at real display luminance.

These models may be too expensive for runtime use but excellent for offline test generation.

### FLIP and related metrics

NVIDIA's FLIP family is designed around perceptual image differences. Baseline variants target SDR/reference rendering comparisons; HDR-aware variants/research may still be useful as an evaluation tangent.

## The key algorithmic implication

The original conflict model:

```text
busy background + low contrast = bad
```

can evolve into something closer to:

```text
conflict =
    visibility_of_background_structure
  × overlap_with_glyph_structure
  × insufficient_foreground_separation
  × temporal_salience
```

where visibility is a function of:
- spatial frequency;
- luminance;
- color direction;
- physical size;
- viewing distance;
- possibly motion.

That is a much better long-term research direction.

## Human tests still win

No model should replace actual reading tests.

Build adversarial code strings and measure:
- response time;
- identification accuracy;
- proofreading errors;
- subjective effort;
- fatigue after extended use.

Particularly useful strings:
- `rn / m / nn / mm`;
- `Il1|!`;
- `0OQ`;
- punctuation-dense syntax;
- long identifiers differing by one glyph;
- braces at several nesting levels.

Background conditions:
- high-frequency foliage;
- wires/branches parallel to stems;
- saturated texture;
- smooth gradients;
- bright windows;
- dark shadow detail;
- moving/scrolling detail.

## Future stupidly-good experiment

If display geometry and viewing distance are known:

1. compute glyph stroke spatial-frequency range in cycles/degree;
2. build a Laplacian/Gabor-like background decomposition;
3. weight background bands with a simplified CSF;
4. attenuate only the bands likely to mask those glyph strokes;
5. preserve other bands.

That would turn "blur around text" into **vision-aware frequency-selective camouflage removal**.

It is exactly excessive enough to deserve investigation.
