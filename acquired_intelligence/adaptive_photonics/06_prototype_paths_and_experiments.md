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
