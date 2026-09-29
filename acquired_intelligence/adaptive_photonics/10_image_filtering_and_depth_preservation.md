# Image filtering and preservation of spatial depth

The original complaint is unusually specific:

> A huge blur makes text readable, but it destroys the visual depth that made the wallpaper desirable.

That is not merely aesthetic hand-waving. Pictorial depth is carried by multiple image structures, and indiscriminate blur/contrast reduction can weaken them.

## Pictorial depth cues worth preserving

Research literature identifies cues including:
- linear perspective;
- occlusion;
- relative size;
- shading;
- cast shadows;
- aerial perspective;
- texture gradients;
- blur/sharpness relationships;
- contrast relationships.

Useful references:
- https://pmc.ncbi.nlm.nih.gov/articles/PMC3490636/
- https://pubmed.ncbi.nlm.nih.gov/9488884/
- https://pubmed.ncbi.nlm.nih.gov/7941367/
- https://pubmed.ncbi.nlm.nih.gov/27115522/

Blur itself can act as a depth cue, but **the relative distribution of sharp and blurred structures matters**.

If the entire image is globally blurred:
- sharp/blur contrast disappears;
- texture gradients flatten;
- occlusion boundaries soften;
- small perspective details disappear;
- local contrast relationships are altered.

So the user's observation that aggressive blur makes the scene feel flatter is entirely plausible.

## Design goal

The renderer should preserve:
- low-frequency illumination gradients;
- major perspective lines;
- important occlusion boundaries;
- broad object silhouettes;
- depth-related contrast relationships;
- sharp detail where it does not interfere with glyphs.

And sacrifice:
- high-frequency texture immediately under glyph strokes;
- strong edges crossing/confusing glyph edges;
- chroma/luminance contrast that masks text.

This is **selective destruction**, not beautification.

## Gaussian blur baseline

Gaussian blur is useful because:
- cheap;
- separable;
- predictable;
- excellent baseline.

But it is content-agnostic:
- smears across object boundaries;
- removes all detail bands together;
- creates visible frosted zones when localized aggressively.

Keep it as the stupid baseline every smarter algorithm must beat.

## Multi-scale Gaussian/Laplacian pyramid

Probably the best first serious approach.

Decompose:

```text
image = coarse base
      + medium band
      + fine band
      + very-fine band
```

Then use the glyph protection/conflict field to control gains per band.

Example:

```text
far from glyph:
    all gains = 1.0

near glyph:
    coarse       = 1.0
    medium       = 0.8
    fine         = 0.35
    very_fine    = 0.1
```

This directly preserves global scene/depth structure while removing detail that competes with text.

It is also extremely GPU-friendly.

## Local Laplacian filters

Local Laplacian filtering manipulates contrast at multiple scales using a Laplacian pyramid and local remapping.

Source material:
- https://people.csail.mit.edu/fredo/comp-photo-book/05-edges-matter-05-local-laplacian-filters.html
- https://people.csail.mit.edu/hasinoff/pubs/ParisEtAl11-lapfilters.pdf

Why it is fascinating here:
- designed for edge-aware detail/tone manipulation;
- can reduce or enhance detail;
- can perform tone mapping;
- specifically designed to avoid halos/ringing seen in simpler edge-aware decompositions.

The project could invert its usual photographic objective:
instead of enhancing local detail, **suppress local detail only inside the glyph protection field**.

Potential problem:
the original algorithm is more expensive/complex than simple pyramids. Start with simple band gains; promote to local-Laplacian only if artifacts justify it.

## Guided filter

Guided filtering:
- edge-aware;
- linear-time formulation;
- used for smoothing/detail/tone manipulation.

Reference:
https://pubmed.ncbi.nlm.nih.gov/23599054/

Potential use:
derive a smooth base layer and suppress residual detail near glyphs.

Caveat:
an edge the filter wants to preserve may be exactly the branch/wire that collides with a glyph.

Therefore "edge-aware" must not mean "always preserve image edges." Text conflict should override image-edge preservation when needed.

## Bilateral filtering

Bilateral filters combine spatial and range similarity so they smooth within regions while preserving stronger edges.

Useful background:
https://doi.org/10.1145/1401132.1401134

Potential uses:
- base/detail decomposition;
- local contrast reduction;
- noise/texture suppression.

Problems:
- naive bilateral filters are expensive;
- parameter tuning can create halos/gradient reversals;
- edge preservation can work against the text objective.

Still worth benchmarking.

## Domain Transform

Domain-transform filtering provides fast edge-aware image/video processing, designed to operate efficiently across scales.

This is attractive for:
- real-time GPU/CPU implementations;
- animated backgrounds;
- interactive parameter changes.

Keep it as a candidate if local-Laplacian/guided approaches are too expensive.

## Fast bilateral solver

The fast bilateral solver turns edge-aware smoothing into an optimization problem that can be solved efficiently in a bilateral-space representation.

Potentially useful if the desired background transform becomes a constrained optimization:
- preserve image away from text;
- minimize detail near text;
- maintain smooth transition.

Probably too much machinery for MVP but highly relevant if hand-authored filters produce halos.

## Orientation-aware conflict

Not all high-frequency detail is equally bad.

Suppose:
- glyph has a vertical stem;
- background has vertical wire aligned immediately beside it.

That can be more confusing than:
- a horizontal low-contrast texture with the same RMS energy.

Potential analysis:
1. compute Sobel/Scharr gradients;
2. derive orientation histogram;
3. estimate glyph edge orientations from mask;
4. score orientation overlap inside glyph neighborhood.

Then attenuate only strongly conflicting bands/orientations.

This starts to resemble oriented/Gabor filtering and links directly to contrast-sensitivity models.

## Gabor / steerable pyramid tangent

Human vision is often modeled in orientation/spatial-frequency channels.

A steerable-pyramid or Gabor-bank representation could separate wallpaper into:
- scale;
- orientation;
- local position.

Then suppress only channels that compete with local glyph structure.

This is an advanced direction, but intellectually cleaner than indiscriminate blur.

Potential runtime optimization:
- do detailed oriented analysis at low resolution;
- use result only to drive coarse suppression parameters.

## Depth-aware filtering

Optional future input: monocular depth estimate.

A depth model could provide:
- object/depth discontinuities;
- likely occlusion boundaries;
- coarse depth layers.

Then the compositor could preferentially preserve:
- strong depth discontinuities;
- foreground silhouettes;
- major perspective structure;

while still suppressing texture within surfaces.

This is tempting because it directly serves the user's desire to preserve "looking into a place."

But it adds:
- ML inference;
- temporal instability;
- hallucinated/inaccurate depth;
- latency/GPU cost;
- extra dependencies.

Do not require depth estimation until ordinary multi-scale suppression proves insufficient.

## Segmentation tangent

Semantic segmentation may be even more useful than depth in some scenes.

Example:
- preserve face/eye boundaries;
- preserve architectural silhouette;
- sacrifice grass/foliage texture behind code.

Again: wildly optional.

## Contrast as a depth cue

Lower-contrast objects can appear farther away, consistent with aerial perspective.

Reference:
https://pubmed.ncbi.nlm.nih.gov/7941367/

This is a subtle warning:
if the compositor locally reduces background contrast around text, it may also locally alter perceived depth.

The soft/local nature of the intervention should minimize this, but it deserves subjective testing.

Potentially the effect is even beneficial: background under text recedes slightly while surrounding scene remains intact.

## Blur as a depth cue

Blur/sharpness and occlusion-edge blur can signal relative depth.

References:
- https://pubmed.ncbi.nlm.nih.gov/9488884/
- https://pubmed.ncbi.nlm.nih.gov/8867752/
- https://pubmed.ncbi.nlm.nih.gov/27115522/

This suggests a sophisticated rule:
**do not uniformly alter every depth-significant edge merely because it falls near text.**

Instead choose the lowest intervention that reaches the readability target.

## Protection-field-aware pyramid algorithm

A practical first algorithm:

1. Decode wallpaper to linear RGB.
2. Build Gaussian pyramid.
3. Build Laplacian detail bands.
4. Rasterize glyph coverage.
5. Dilate/blur coverage to protection field.
6. Compute local luminance + detail conflict.
7. For each detail band, compute suppression gain:
   - more suppression for fine bands;
   - less for coarse bands;
   - stronger where conflict high.
8. Reconstruct image.
9. Optionally compress luminance/chroma near glyph.
10. Composite text in linear light.
11. Apply temporal smoothing to suppression state.

This is simple enough to implement in compute shaders and rich enough to test the core hypothesis.

## Preserve detail inside glyph counters?

Interesting micro-question:

For letters like:
- `o`;
- `e`;
- `a`;
- `8`;
- `0`;

should background detail inside the enclosed counter be preserved or suppressed?

Hypotheses:
- suppressing detail inside counters may improve shape recognition;
- preserving it may make the intervention less visible;
- exact answer may depend on font size/PPI.

A glyph-distance field allows different policies for:
- stroke footprint;
- immediately adjacent exterior;
- counters/interiors.

## Use background transform, not text outline, when possible

A common readability trick is text shadow/outline.

That may work, but:
- changes glyph silhouette;
- can make tiny fonts look heavier/blurry;
- hides the exact benefit of high PPI;
- can resemble haloed subtitles.

The adaptive-background approach has a unique advantage:
**it can preserve the intended glyph raster exactly and manipulate only what competes with it.**

Text outline remains a baseline.

## Algorithm ranking to test

In order:

1. static global brightness/saturation reduction;
2. local luminance reduction under glyph protection field;
3. local Gaussian detail reduction;
4. simple Laplacian-pyramid band suppression;
5. guided-filter base/detail;
6. local Laplacian;
7. orientation-aware multi-scale suppression;
8. depth/segmentation-assisted policy.

Each step must demonstrate a real improvement before earning its complexity.

## What "preserve depth" should mean experimentally

Do not rely only on a subjective word.

Ask users:
- does the image still feel spatial?
- can you still identify near/far layers?
- do foreground objects still pop?
- do architecture/perspective lines remain clear?
- does the scene feel like a window rather than frosted glass?
- is the local text treatment visible?

Potential objective proxies:
- preserve major edge map outside glyph mask;
- preserve low-frequency structural similarity;
- preserve saliency map;
- minimize perceptual VDP difference outside text region.

The final judge is still a human staring at code for a stupid number of hours.
