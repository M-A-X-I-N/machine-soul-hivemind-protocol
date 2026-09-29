# Prototype paths and experiments

The goal is to kill bad ideas cheaply and preserve good ones before editor integration explodes in scope.

## Stage 0 — establish visual ground truth

### PPI sanity

Render the same monospace font at matched physical sizes on current 1080p and high-PPI displays.

Include adversarial strings:
- `rn m nn mm`
- `Il1|!`
- `0OQ`
- `{}[]()`
- `.,:;'`
- long snake_case and camelCase identifiers.

Record subjective minimum glance-readable size.

Purpose:
separate "font sucks" from "not enough physical samples."

### Scaling

On 4K compare logical desktop scaling:
- 100%;
- 125%;
- 150%;
- 175%;
- 200%;

then independently adjust editor font size.

Purpose:
find comfortable workspace versus physical glyph resolution.

## Stage 1 — prove algorithm in SDR

### Static offline compositor

Inputs:
- wallpaper;
- known glyph mask;
- rendered code text.

Generate:
1. raw image + text;
2. global dim;
3. global Gaussian blur;
4. translucent rectangle;
5. local luminance suppression;
6. local detail suppression;
7. local luminance + detail suppression;
8. local luminance + detail + chroma suppression.

Blind compare.

If 5–8 do not beat the simple baselines, stop.

### Protection radius

Sweep halo radius/falloff and find:
- first radius that helps;
- first radius where the viewer notices a "text cloud."

### Multi-scale suppression

Create Gaussian/Laplacian pyramid.
Suppress fine bands around glyphs while retaining low-frequency structure.

This directly tests the original "preserve depth" objective.

## Stage 2 — interactive shader without editor integration

### Windows Terminal path

Use:
- `experimental.pixelShaderPath`;
- `experimental.pixelShaderImagePath`.

Start from:
https://github.com/microsoft/terminal/blob/main/samples/PixelShaders/BackgroundImage.hlsl

Prototype:
- infer terminal foreground;
- build a cheap local text mask/neighborhood;
- dim/desaturate/smooth wallpaper near glyphs;
- composite.

Advantages:
- minimal scaffolding;
- real monospaced text;
- real scrolling;
- HLSL;
- immediate visual feedback.

This can reveal temporal problems early.

## Stage 3 — standalone linear/HDR renderer

Build a small program with:
- image;
- text input;
- font selector;
- font size;
- adaptive controls;
- SDR/HDR toggle;
- debug visualization layers.

Debug views:
- luminance map;
- gradient/detail map;
- exact glyph mask;
- protection field;
- conflict score;
- suppression amount;
- output-nit estimate.

### Windows backend
FP16 scRGB through DXGI.

### Linux backend
Vulkan + Wayland color management.

Do not add actual code editing yet.

## Stage 4 — cross-platform equivalence

Same machine, NVIDIA GPU, same monitor.

Render deterministic scenes through:
- Windows scRGB;
- Linux/KWin/Wayland.

Compare:
- test-pattern clipping;
- reference white;
- low-end behavior;
- out-of-SDR-range highlights;
- colorimeter readings if available.

Goal:
distinguish platform mapping differences from algorithm bugs.

## Stage 5 — text renderer evaluation

Compare:
- DirectWrite grayscale;
- DirectWrite ClearType on RGB-stripe panel;
- FreeType grayscale;
- FreeType Harmony with exact geometry;
- MSDF/MTSDF;
- high-resolution raster + downsample.

Metrics:
- `rn/m` discrimination;
- punctuation;
- braces;
- italic comments;
- thin syntax colors;
- font sizes near threshold.

## Stage 6 — restrained HDR luminance experiment

Example sweep:
- background means: 2, 4, 6, 10 nit;
- text: 15, 20, 30, 40, 60 nit;
- local-background attenuation: 0–60%.

Test:
- immediate readability;
- comfort after extended use;
- perceived halo;
- black crush;
- monitor ASBL.

Do not start with absurdly bright text because "HDR."

## Stage 7 — temporal algorithm

Test:
- scrolling code over static image;
- moving wallpaper;
- typing;
- caret blink;
- selection drag;
- resize;
- image crossfade.

Compare:
- no smoothing;
- EMA;
- attack-fast/release-slow hysteresis;
- quantized intervention levels.

Reject designs that visibly pulse around code.

## Stage 8 — editor integration survey

Only after visual concept wins.

### VS Code
Research how far public decoration APIs go before Chromium/Electron internals are required.

### JetBrains
Research editor paint hooks, highlighters/renderers, background painters, and whether a plugin can provide:
- exact visible glyph geometry;
- token color;
- viewport transforms;
- a background render layer.

### Cooperative sidecar
Potentially editor plugin publishes:
- glyph/protection mask;
- viewport transform;
- semantic regions;
to a separate GPU compositor.

This may be cleaner than embedding Vulkan/D3D into every editor plugin.

## Stage 9 — panel-aware text

If non-RGB OLED is purchased or the experiment is irresistible:
- obtain microscope/macro image of subpixels;
- encode physical geometry;
- use FreeType Harmony geometry or custom rasterizer;
- compare against grayscale AA at high PPI.

This can become its own project.

## Stage 10 — hardware characterization

With colorimeter:
- scRGB value → emitted luminance mapping;
- reference white;
- minimum stable luminance;
- near-black steps;
- ABL by window size;
- static dimming over time;
- EOTF tracking.

Without colorimeter:
- use visual test patterns for software behavior;
- do not pretend screenshots measure emitted luminance.

## Algorithm candidates

### Cheap
- local mean/variance;
- Sobel gradient;
- Gaussian blur of text mask;
- contrast compression toward local mean.

### Medium
- multi-scale Gaussian/Laplacian decomposition;
- guided filter;
- bilateral filter;
- tiled compute analysis.

### Excessively fun
- orientation-aware edge conflict;
- perceptual visibility model;
- small neural network predicting suppression;
- eye tracking;
- semantic code importance;
- adaptive font grade;
- wallpaper depth-map awareness.

Make the algorithm earn every layer of complexity.

## Failure modes

- visible dark halo around glyphs;
- shimmering when scrolling;
- text luminance pumping;
- syntax colors shifting unpleasantly;
- crushed wallpaper detail;
- OLED black crush;
- ASBL triggering during coding;
- display tone mapping undoing intended differences;
- managed/unmanaged windows behaving differently;
- subpixel fringing worse than expected;
- GPU cost absurd at 4K/high refresh;
- Windows/Linux mismatch;
- screenshot/capture tools losing HDR semantics;
- remote desktop destroying color semantics.

## Successful early prototype

A useful success criterion:

> The wallpaper still looks spatially deep rather than frosted, and the viewer stops noticing that anything special is happening around the code.

That is stronger than "the shader works."


## Second-pass prototype shortcuts

The research above was intentionally platform-first. The second pass found several cheaper laboratories worth inserting before a native standalone renderer.

### kitty custom-shader prototype

kitty 0.49.0 added an end-of-pipeline, linear-RGB custom shader system with chained passes and persistent intermediate textures.

Use it to test:
- multi-pass detail suppression;
- temporal state/hysteresis;
- local contrast maps;
- scroll stability.

First inspect what clean text/background information is available to the shader. If only the final backbuffer is exposed, use controlled foreground/background colors to construct a usable mask.

### WezTerm depth baseline

Use WezTerm's layered backgrounds, HSB transform, and parallax attachment as a baseline for "good spatial wallpaper without adaptation."

This is useful because the project should beat an already-pretty static solution, not only beat raw wallpaper.

### Electron/WebGPU capability probe

Before writing DXGI/Vulkan plumbing, build a tiny Electron/WebGPU HDR probe:
- rgba16float canvas;
- extended tone mapping;
- >1.0 values;
- Windows HDR and KDE Wayland HDR;
- known reference patches.

If that reaches the panel correctly, use it for the first serious interactive compositor prototype.

### Zed source experiment

If a real-editor proof becomes desirable, inspect Zed/GPUI before VS Code/JetBrains internals. Its custom GPU renderer may already expose the exact glyph/background seam the experiment needs.

### Updated cheap-to-expensive sequence

```text
offline SDR reference compositor
        ↓
Windows Terminal / kitty shader
        ↓
WezTerm baseline comparisons
        ↓
Electron/WebGPU HDR probe
        ↓
standalone native HDR renderer if needed
        ↓
Zed/editor integration experiment
        ↓
production-quality platform backends
```


## Third-pass revised experiment ladder

Existing implementations give us better cheap checkpoints.

### A. Offline ancestry baselines

Render the same test scene using:
1. raw wallpaper;
2. black/white adaptive foreground;
3. outline/drop shadow;
4. Material-style gradient scrim;
5. GlassCode-style inferred local background versus shape classifier;
6. exact glyph-mask local luminance reduction;
7. exact glyph-mask high-frequency/detail suppression;
8. perception-weighted variant.

This directly answers which generation of solution actually earns its complexity.

### B. Ghostty — exact foreground-alpha experiment

When configured so terminal background alpha remains transparent, use `iChannel0.a` as a real terminal-derived foreground/protection signal.

Test:
- wallpaper below glyphs;
- glyph-distance falloff;
- local luminance suppression;
- local multi-scale detail suppression;
- dither after locally flattened gradients.

This may be the cheapest proof that the visual idea works with real rendered text.

### C. kitty — temporal/multipass extension

Port the winning Ghostty/static algorithm into kitty's richer shader system and test:
- persistent temporal state;
- attack/release hysteresis;
- event-driven recomputation;
- chained intermediate maps.

### D. Windows capture shader hosts

Before writing our own capture/overlay backend, test algorithms in:
- Windows Terminal HLSL when its texture inputs are enough;
- OBS Window Capture + obs-shaderfilter;
- MagpieFX if a no-scale/window-processing setup is convenient.

### E. libplacebo feasibility spike

Before committing to native custom D3D/Vulkan infrastructure:
1. create a libplacebo GPU/context;
2. load wallpaper into a correctly tagged color space;
3. attach custom shader at a linear/high-precision hook stage;
4. bind an external glyph-mask texture;
5. implement a simple low/high-frequency attenuation pass;
6. render to Windows and Linux targets;
7. inventory remaining presentation glue.

Specifically compare our first implementation against libplacebo's own **contrast-recovery** feature-map machinery, whose high-frequency residual is conceptually the inverse of what we need near glyphs.

### F. Cooperative editor integration

Only after the shader earns itself:
- JetBrains plugin exposes visible text/protection geometry to sidecar;
- Zed/GPUI branch exposes renderer-native glyph data;
- Electron/Monaco path exposes layout + WebGPU background;
- VS Code patching remains an option, not the default assumption.

### G. Capture fallback

If no editor can cooperate, reproduce the GlassCode architecture with modern pieces:
- FP16 Windows Graphics Capture where HDR matters;
- explicit color metadata;
- better foreground mask inference;
- adaptive renderer;
- overlay/replacement window.

The existence of GlassCode means this is ugly, not imaginary.
