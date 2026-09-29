# Text rendering and human-vision notes

The project only works if "text readability" is treated as a rendering/perception problem rather than a single contrast-ratio number.

## Text has stages

```text
Unicode
  ↓
segmentation / direction / script / language
  ↓
font selection + fallback
  ↓
shaping
  ↓
glyph IDs + positions + clusters
  ↓
outline/bitmap acquisition
  ↓
hinting
  ↓
rasterization / coverage
  ↓
anti-aliasing
  ↓
linear-light composition
  ↓
display color transform
```

Do not collapse shaping and rasterization.

### HarfBuzz

HarfBuzz shapes Unicode sequences into positioned glyphs. Output includes glyph IDs, clusters, advances, and offsets.

Sources:
- https://harfbuzz.github.io/harfbuzz-hb-shape.html
- https://harfbuzz.github.io/shaping-and-shape-plans.html

Even if the first prototype is ASCII code, do not make shaping impossible later. Editors inevitably encounter:
- Unicode identifiers;
- combining marks;
- bidi text;
- emoji/fallback;
- programming ligatures;
- complex scripts in comments/strings.

## Rasterization and hinting

At small sizes the vector outline alone is not enough. Hinting changes how outlines align to the pixel grid.

FreeType:
- https://freetype.org/freetype2/docs/hinting/text-rendering-general.html
- https://freetype.org/freetype2/docs/hinting/subpixel-hinting.html

Relevant distinction:
- **layout fidelity**: preserve intended advances/shapes;
- **pixel sharpness**: snap/adjust stems for the actual raster grid.

High PPI shifts the tradeoff toward design fidelity because less brutal grid fitting is needed.

## Grayscale vs subpixel antialiasing

### Grayscale AA
One coverage alpha per physical pixel.

Advantages:
- independent of RGB/BGR/subpixel geometry;
- works naturally on unusual OLED layouts;
- easier to composite over arbitrary imagery;
- simpler to reason about in linear light.

Disadvantage:
- less apparent horizontal sampling resolution on low-PPI classic RGB LCDs.

### Subpixel AA
Uses individual color subpixels to gain apparent resolution along the stripe direction.

Advantages:
- can materially improve low-PPI text clarity.

Problems:
- assumes known physical geometry;
- wrong geometry creates colored fringes;
- rotation breaks the assumption;
- transparent/arbitrary backgrounds complicate correct blending;
- OLED layouts may be triangular or four-subpixel rather than simple RGB stripe.

FreeType Harmony is interesting because it can be told arbitrary regular subpixel coordinates:
https://freetype.org/freetype2/docs/reference/ft2-lcd_rendering.html

Possible future research: panel-aware subpixel AA for OLED. Do not make this the first milestone. At ~163 PPI, grayscale AA may already win subjectively.

## Linear-light alpha blending matters

A glyph coverage value is geometric coverage, not an sRGB brightness code.

Conceptually:

```text
linear_output = coverage * linear_text + (1 - coverage) * linear_background
```

Only later encode through the output transfer function.

Compositing directly in gamma-encoded sRGB can alter apparent stem weight.

FreeType discusses gamma-correct alpha blending:
https://freetype.org/freetype2/docs/hinting/text-rendering-general.html

The adaptive-background math and final text composite should be linear-light.

## Glyph coverage is also a control signal

The compositor needs the pre-composite glyph coverage mask.

Derive:
- exact glyph coverage;
- thresholded stroke mask;
- dilated near-glyph region;
- blurred/distance falloff protection field;
- distance to glyph edge;
- optional per-line/per-token semantic masks.

These control background suppression separately from text blending.

Do not infer text after it has already been flattened into the scene if the renderer owns the text.

## Direct raster masks versus SDF/MSDF

Signed-distance-field rendering is useful for scalable GPU text. Multi-channel SDFs preserve corners better than monochrome SDFs.

Implementations:
- https://github.com/Chlumsky/msdfgen
- https://github.com/Chlumsky/msdf-atlas-gen

But for small fixed-size code text:
- direct rasterization can preserve carefully hinted pixel coverage;
- MSDF reconstruction can introduce small-size artifacts;
- atlas resolution/range choices matter;
- hinting integration is less direct.

Compare:
1. DirectWrite raster mask.
2. FreeType grayscale mask.
3. high-resolution outline rasterization/downsample.
4. MSDF/MTSDF at several atlas sizes.

Judge `rn/m/mm` discrimination, not only screenshot beauty.

## Programming-font variables worth testing

- x-height;
- stem width;
- aperture openness;
- zero/slash form;
- `l/I/1`;
- `rn/m`;
- brace/bracket shape;
- punctuation weight;
- italic angle;
- ligatures on/off;
- variable-font weight/grade axes.

A grade axis is interesting because it can alter stroke thickness with less metric change than normal weight, but adaptive per-background grade could become visually unstable.

## Contrast is local

Classic WCAG 2 contrast is useful as a conservative accessibility floor:
https://www.w3.org/WAI/WCAG21/Understanding/contrast-minimum

But a single global foreground/background ratio cannot capture:
- edges crossing glyph strokes;
- high-frequency texture behind text;
- tiny holes/counters;
- spatial adaptation;
- anti-aliased partial coverage;
- temporal motion;
- absolute luminance.

Treat contrast metrics as inputs/constraints, not the whole algorithm.

## Negative polarity and absolute luminance

The maintainer strongly prefers light text on dark background. Controlled studies often find a positive-polarity advantage, particularly for small text.

Useful studies:
- https://pubmed.ncbi.nlm.nih.gov/28166901/
- https://pubmed.ncbi.nlm.nih.gov/25135324/
- https://pubmed.ncbi.nlm.nih.gov/19562598/
- https://pubmed.ncbi.nlm.nih.gov/25141597/
- https://pubmed.ncbi.nlm.nih.gov/31875153/

A recurring explanation is that brighter overall display luminance constricts the pupil, which can improve fine-detail discrimination.

This does not imply "use light mode." It means absolute luminance and pupil size are variables worth measuring when the goal is smaller text.

## Very bright text on dark backgrounds can be counterproductive

Perceived halo/flare can come from display optics/coating, ocular scatter, aberrations, pupil size, and raster behavior.

Do not depend on "more text nits = always better."

Experiment with:
- off-white instead of peak-white;
- slightly lifted black versus true zero;
- modest text/background luminance ratios;
- different ambient lighting;
- actual error rate rather than aesthetics alone.

## High spatial frequencies are the enemy

The reason huge blur helps readability is that it removes detailed edges competing with glyph edges.

Candidate conflict signals:
- gradient magnitude (Sobel/Scharr);
- Laplacian/high-pass energy;
- local variance;
- multi-scale Gaussian/Laplacian pyramid energy;
- oriented gradients compared with glyph-edge orientation;
- frequency-band energy.

Interesting hypothesis:
a vertical tree branch may interfere more with a vertical glyph stem than a smooth sky gradient with the same mean luminance.

## Edge-aware smoothing and detail decomposition

Potential tools:
- bilateral filter;
- guided filter;
- local Laplacian filter;
- frequency-selective attenuation;
- anisotropic diffusion.

Guided filter:
https://pubmed.ncbi.nlm.nih.gov/23599054/

Bilateral filtering overview:
https://doi.org/10.1145/1401132.1401134

Subtlety: preserving a background edge is normally desirable, but if that edge crosses a glyph then preserving it may be exactly wrong. The text-protection field should therefore influence where detail is allowed to be destroyed.

## Temporal stability

If every glyph's background adjustment immediately reacts to every scroll/pixel change, the result may shimmer or breathe.

Use:
- exponential smoothing;
- hysteresis;
- separate attack/release rates;
- quantized policy bands;
- intelligent reseeding on large scrolls/wallpaper changes.

The viewer should notice clean text, not a living halo.

## Semantic brightness is tempting, but dangerous

Luminance could become another syntax channel:
- comments dimmer;
- active symbol brighter;
- error token brighter;
- current line emphasized;
- cursor highest salience.

Do not overload luminance until basic readability is solved.

## Personalization controls worth preserving

- target text luminance;
- minimum local contrast;
- maximum background suppression;
- detail-suppression strength;
- halo radius/falloff;
- chroma reduction;
- temporal smoothing;
- preserve syntax colors strictly vs adaptive color;
- SDR-only mode;
- HDR physical-nit mode.
