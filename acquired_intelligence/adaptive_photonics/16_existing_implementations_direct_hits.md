# Existing implementations — direct and near-direct hits

Research snapshot: 2026-09-30.

This pass asks a deliberately different question from the earlier technology surveys:

> Who has already built something that resembles the desired result, even if their implementation is primitive, platform-specific, ugly, abandoned, or solving a neighboring problem?

The strongest result is **GlassCode**, which is close enough to count as an ancestor of the proposed capture/sidecar architecture.

## 1. GlassCode — direct historical ancestor

Repository:

https://github.com/gileli121/GlassCode

License: GPL-3.0.

At the snapshot date the repository is not archived; its most recent code push was 2024-09-04.

### What it does

GlassCode is a JetBrains plugin for Windows that makes the IDE visually transparent while keeping code/UI shapes sharp and independently bright.

Its public controls include:
- background opacity;
- brightness behind the window;
- blur level;
- extra text brightness;
- high-contrast-theme integration;
- optional CUDA acceleration.

The README is unusually explicit that its image-processing algorithm attempts to apply opacity to the **background but not detected text/shapes**.

That is already much closer to this project than a normal transparency plugin.

### Source architecture

The implementation is split between a Java JetBrains plugin and a native Windows renderer process.

#### JetBrains side

`JAVA/src/main/java/glasscode/Renderer.java`

The plugin:
1. resolves the JetBrains project window HWND;
2. launches a native `Renderer.exe`;
3. passes window id and visual settings;
4. communicates updates through `WM_COPYDATA`;
5. exposes opacity, background brightness, text brightness, and blur.

This is architecturally important:

> **editor plugin as control/semantic integration + external native renderer sidecar**

is already proven as a viable packaging pattern.

Our sidecar could be much cleaner because it should ideally receive glyph/protection information directly rather than reconstructing everything from the captured pixels.

#### Capture side

`CPP/capture_layer.cpp`

GlassCode uses **Windows Graphics Capture**:
- `Windows.Graphics.Capture.GraphicsCaptureItem`;
- `Direct3D11CaptureFramePool`;
- direct HWND capture via `IGraphicsCaptureItemInterop::CreateForWindow`;
- captured frame is exposed as `ID3D11Texture2D`;
- cursor capture is disabled;
- frame pool is recreated on resize.

Its implementation predates our HDR concern and uses `B8G8R8A8UIntNormalized`, so it is SDR/8-bit rather than a model to copy literally.

Still, it proves the capture path.

#### Display/overlay side

`CPP/display_layer.cpp`

GlassCode creates layered, no-activate, input-transparent overlay windows and aligns them with the original JetBrains window.

It uses:
- `WS_EX_LAYERED`;
- `WS_EX_TRANSPARENT`;
- DWM extended frame bounds;
- Windows Composition / `Windows.UI.Composition`;
- a swapchain-backed composition surface.

It can make the original target window almost completely transparent and show the processed captured copy in the overlay.

That gives a very concrete answer to the question:

> Can an external process replace the appearance of an existing editor without owning the editor renderer?

Yes, at least on Windows.

The production-quality answer may still be "please do not do this unless necessary," but it is not hypothetical.

### Its text/shape detector

The most valuable part is the crude shape detector in:

- `CPP/process_layer_cpu.cpp`
- `CPP/process_layer_gpu.cu`

The CPU algorithm uses small local blocks (5×5 in the current implementation).

For each block it approximately:
1. reduces pixels to average-channel brightness;
2. builds a local histogram;
3. treats the most frequent local value as the likely background;
4. runs simple horizontal/vertical noise reduction on that reduced background map;
5. treats pixels differing from the inferred background as **shape pixels**;
6. preserves or brightens those shape pixels;
7. applies opacity/brightness changes to background pixels separately.

There is also separate machinery attempting to detect image regions so arbitrary image texture is not misclassified as UI shapes.

The CUDA implementation performs the same class of operation on the GPU and uses D3D11/CUDA resource interop.

### Why this matters

GlassCode is an empirical baseline for a fallback architecture:

```text
existing editor window
        ↓
Windows Graphics Capture
        ↓
infer background / text-like shapes
        ↓
process background separately
        ↓
preserve/brighten shapes
        ↓
layered replacement/overlay window
```

Our desired architecture improves almost every stage:

```text
existing editor/plugin
        ↓
explicit glyph/protection mask
        ↓
known wallpaper texture
        ↓
linear-light local conflict analysis
        ↓
selective luminance/detail/chroma suppression
        ↓
HDR/scRGB-aware output
```

The GlassCode lesson is therefore **not** "reuse its classifier."

The lesson is:

> The horrible capture-and-reconstruct fallback is sufficiently viable that someone shipped it years ago.

### Lessons from its weaknesses

Its source also explains why semantic cooperation is better:

- local background inference is theme-sensitive;
- the README recommends high-contrast themes with fewer colors because classification becomes easier;
- image regions need special-case detection;
- text and generic UI shapes are conflated;
- block classification destroys precise glyph semantics;
- 8-bit gamma-space processing is unsuitable for our desired HDR/perceptual math;
- CPU performance was poor enough that CUDA acceleration was strongly recommended;
- platform integration is Windows-only;
- the overlay/capture architecture accumulates resize/z-order/window-style complexity.

A cooperative glyph mask avoids almost all of those problems.

### Licensing note

GlassCode is GPL-3.0.

Its source is excellent research/reference material, but copying code into a differently licensed future project would require deliberate license compatibility decisions.

Treat algorithms/architecture as learned prior art unless the future project's licensing explicitly permits reuse.

---

## 2. Wallpaper Setting — VS Code background isolation

Repository:

https://github.com/Angelmaneuver/wallpaper-setting

License: MIT.

The extension's explicit design claim is unusually relevant: it tries to make **only VS Code's background transparent** while keeping code and UI visually sharp.

It supports:
- image backgrounds;
- slideshows;
- video wallpaper;
- different opacity per VS Code region;
- blur;
- brightness;
- contrast;
- grayscale;
- saturation;
- sepia.

### How it integrates

It modifies VS Code's internal:

`Resources/app/out/vs/code/electron-sandbox/workbench/workbench.js`

rather than relying solely on stable public extension APIs.

That causes the expected unsupported-installation warning and creates update/maintenance risk.

### What to steal conceptually

- The demand already exists: people actively want imagery behind code while retaining sharp foreground UI.
- Per-region opacity is useful even before per-glyph adaptation:
  - editor;
  - sidebar;
  - panel;
  - auxiliary bar;
  - chrome.
- A practical product may combine:
  - coarse UI-region policy;
  - fine glyph-local policy.

### What not to infer

This is not an adaptive local-contrast renderer.

Its filters are global/static image transformations.

It is a baseline and integration precedent, not the final algorithm.

---

## 3. vscode-background — mature wallpaper injection ecosystem

Repository:

https://github.com/shalldie/vscode-background

License: MIT.

At the snapshot date it is actively maintained and has a much larger user base than most editor-wallpaper experiments.

It supports backgrounds for:
- fullscreen;
- editor;
- sidebar;
- auxiliary bar;
- panel;
- custom layouts;
- custom styles.

Why preserve it:
- mature evidence for where users want backgrounds;
- source for VS Code workbench patching/injection techniques;
- useful compatibility baseline for future VS Code integration;
- likely collection of update/version edge cases worth studying before touching Electron internals.

Again, it does not solve adaptive readability.

---

## 4. SmartText — text placement over natural images

Repository:

https://github.com/intchous/SmartText

License: MIT.

Paper/system:
**Harmonious Textual Layout Generation over Natural Images via Deep Aesthetics Learning**.

Its two-stage model:
1. saliency-aware text-region proposal;
2. aesthetics-based textual-layout selection.

It explicitly combines semantic visual saliency and perceptual/aesthetic scoring to decide where text belongs on a natural image.

### Our problem is the inverse

SmartText asks:

> Where should I put text so the image and typography cooperate?

Our editor cannot freely move code.

But we can invert its result:

> Given immovable text, which image regions are expensive/dangerous underneath it?

Useful concepts:
- saliency maps;
- candidate safe regions;
- semantic image content;
- aesthetics-based score;
- offline wallpaper suitability analysis.

Possible feature:
**wallpaper preflight**

Before using an image, produce:
- editor-safe regions;
- dangerous high-saliency/detail regions;
- recommended crop/position;
- expected intervention cost.

Then choose the crop that minimizes how much runtime suppression is needed.

---

## 5. PosterLayout — content-aware visual/textual layout benchmark

Repository:

https://github.com/PKU-ICST-MIPL/PosterLayout-CVPR2023

Paper:
**PosterLayout: A New Benchmark and Approach for Content-Aware Visual-Textual Presentation Layout**, CVPR 2023.

Its dataset layout includes:
- image canvases;
- inpainted posters;
- saliency maps from multiple models;
- layout annotations;
- nearly ten thousand training entries.

### Why it is potentially valuable

This is a large existing corpus of the exact broad problem:

> place readable/useful typography while respecting important image content.

Even if its model is irrelevant, the dataset may be useful for:
- validating an image "text hostility" metric;
- testing saliency-vs-readability hypotheses;
- generating wallpaper/layout examples;
- learning which image structures professional/generated layouts avoid covering.

Possible future experiment:
1. take poster background and known text region;
2. compute our conflict score on the text region;
3. compare against random placements;
4. see whether human-designed/training placements statistically fall into lower-conflict regions.

That would validate the conflict metric without first running our own user study.

License status of the dataset/code should be checked carefully before reuse; GitHub does not currently expose a standard SPDX license for this repository.

---

## 6. smartcrop.js — tiny useful saliency heuristic

Repository:

https://github.com/jwagner/smartcrop.js

License: MIT.

Algorithm summary from its own README:
1. Laplacian edge detection;
2. skin-like-region detection;
3. saturation detection;
4. optional boosted regions such as faces;
5. sliding-window crop candidates;
6. importance weighting;
7. choose best candidate.

This is intentionally simple and fast.

### Invert it for our wallpaper

Instead of:

> put interesting regions in the crop center

use:

> keep interesting/high-detail regions away from dense code regions.

Potential wallpaper-placement mode:
- derive code-density map from editor layout;
- derive image-interest map from smartcrop-like analysis;
- optimize image translation/crop to minimize overlap.

This could reduce runtime filtering dramatically.

### Caution

Do not move/reposition wallpaper continuously while typing.

That would be visually nauseating.

Use it for:
- initial crop;
- window-resize recomputation;
- deliberate wallpaper changes;
- perhaps extremely slow/hysteretic layout adaptation.

---

## 7. Existing editor-background ecosystem as requirements evidence

A useful meta-finding:

There are many editor/terminal background projects, but the overwhelming majority stop at some combination of:
- static opacity;
- global blur;
- global brightness;
- saturation;
- CSS filters;
- transparency.

That is precisely the gap this project is exploring.

The proposed differentiator is not "editor wallpaper."

It is:

> **text-aware, locally adaptive preservation of image structure.**

GlassCode is the notable exception because it actually separates inferred foreground shapes from background pixels.

---

## 8. Direct-hit implementation hierarchy

From closest to most indirect:

| Existing project | What already exists | What we still need |
|---|---|---|
| GlassCode | editor capture, text/shape inference, separate bg/fg processing, CUDA, overlay | semantic glyph mask, linear/HDR math, depth-preserving local filter, cross-platform |
| Wallpaper Setting | background-only transparency, image filters, VS Code injection | adaptive/local behavior |
| vscode-background | robust VS Code wallpaper ecosystem | adaptive/local behavior |
| SmartText | saliency-aware text-over-image placement | invert placement metric for fixed code |
| PosterLayout | text-over-image dataset + saliency/layout models | adapt benchmark/metric to code |
| smartcrop.js | cheap image-interest map / crop optimizer | invert objective around code-density map |

## 9. Immediate implementation consequences

The existing-implementation pass changes several assumptions:

1. **Capture fallback is proven enough to prototype.**
   GlassCode already did the ugly version.

2. **Editor cooperation should remain preferred.**
   GlassCode's classifier complexity is a warning about reconstructing semantics from pixels.

3. **Wallpaper placement should become part of the algorithm.**
   We should not only ask how to transform an image; we can also choose where the image sits.

4. **Safe-region/saliency precomputation may save GPU work.**
   SmartText/PosterLayout/smartcrop-style analysis can happen when wallpaper/layout changes rather than every frame.

5. **A real prototype should include a GlassCode-style baseline.**
   Something like:
   - infer local background;
   - preserve differing foreground pixels;
   - dim everything else.

   Our fancy algorithm should visibly outperform it before it earns complexity.

## Sources

- GlassCode: https://github.com/gileli121/GlassCode
- Wallpaper Setting: https://github.com/Angelmaneuver/wallpaper-setting
- vscode-background: https://github.com/shalldie/vscode-background
- SmartText: https://github.com/intchous/SmartText
- PosterLayout: https://github.com/PKU-ICST-MIPL/PosterLayout-CVPR2023
- smartcrop.js: https://github.com/jwagner/smartcrop.js
