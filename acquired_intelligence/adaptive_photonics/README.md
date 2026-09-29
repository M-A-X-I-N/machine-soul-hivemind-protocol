# Adaptive photonics

Research dump, design scratchpad, and implementation launchpad for an adaptive code/text compositor that preserves visually deep imagery behind text while dynamically protecting glyph readability through local luminance/detail manipulation.

Research snapshot: 2026-09-29.

This directory is intentionally broad. It captures the conversation that spawned the idea, corrected terminology, display physics, HDR/SDR/color-management machinery, Windows and Linux rendering paths, font shaping/rasterization, human-vision considerations, plausible algorithms, prototype paths, current OLED concerns, and sources worth returning to.

It is not a committed architecture. Anything dependent on fast-moving Wayland/KDE/NVIDIA/OLED support should be rechecked before implementation.

## Why this exists

The initiating problem is not simply "put a wallpaper behind code."

The desired experience is:

1. Very high pixel density so small programming text remains immediately discriminable rather than merely decipherable.
2. A detailed image with strong spatial/depth cues behind the editor, because a flat/static background becomes unpleasant over long sessions.
3. Preserve much more of that image than a giant Gaussian blur allows.
4. Make text legible by locally changing the relationship between glyphs and the imagery beneath them:
   - reduce background luminance only where needed;
   - selectively suppress local detail/spatial frequency near glyphs;
   - optionally reduce local chroma;
   - optionally raise text luminance;
   - use soft spatial and temporal transitions so the intervention is mostly invisible.
5. Exploit OLED's per-pixel emission and, where useful, HDR/scRGB's extended luminance representation.
6. Keep the perception/image algorithm independent of Windows/Linux display plumbing.

The working concept is an **adaptive local-contrast compositor**.

## Directory map

- [00_conversation_brain_dump.md](00_conversation_brain_dump.md) — requirements, preferences, terminology corrections, and useful conversational conclusions.
- [01_display_hdr_oled_foundations.md](01_display_hdr_oled_foundations.md) — SDR/HDR, local dimming, PQ/HLG/scRGB, OLED, ABL/ASBL, subpixels, PPI, and monitor implications.
- [02_text_rendering_and_human_vision.md](02_text_rendering_and_human_vision.md) — shaping, rasterization, hinting, anti-aliasing, subpixel geometry, gamma-correct compositing, readability, contrast, and perception.
- [03_windows_rendering_stack.md](03_windows_rendering_stack.md) — Windows Advanced Color, DXGI/D3D, scRGB FP16, DirectWrite/Direct2D, and fast prototype surfaces.
- [04_linux_wayland_vulkan_nvidia.md](04_linux_wayland_vulkan_nvidia.md) — Wayland color-management-v1, Vulkan HDR/color-space support, KWin/KDE, DRM color pipelines, and current NVIDIA state.
- [05_adaptive_compositor_architecture.md](05_adaptive_compositor_architecture.md) — proposed platform-neutral pipeline, algorithms, data flow, abstractions, and edge cases.
- [06_prototype_paths_and_experiments.md](06_prototype_paths_and_experiments.md) — staged experiments designed to answer unknowns cheaply before writing an editor.
- [07_perceptual_models_and_metrics.md](07_perceptual_models_and_metrics.md) — contrast-sensitivity models, visual angle, spatial/temporal frequency, and perceptual evaluation.
- [08_web_chromium_electron_webgpu.md](08_web_chromium_electron_webgpu.md) — Chromium HDR/scRGB machinery, Electron, WebGPU FP16/extended tone mapping, and CSS HDR.
- [09_capture_compositor_and_integration_routes.md](09_capture_compositor_and_integration_routes.md) — cooperative sidecars, capture, overlays, compositor routes, and editor integration.
- [10_image_filtering_and_depth_preservation.md](10_image_filtering_and_depth_preservation.md) — Laplacian pyramids, local Laplacian/guided/bilateral filtering, depth cues, and selective detail destruction.
- [11_calibration_measurement_and_color_management.md](11_calibration_measurement_and_color_management.md) — display characterization, Windows MHC2, ICC, LittleCMS, instruments, and physical-nit measurement.
- [12_renderer_editor_and_terminal_laboratories.md](12_renderer_editor_and_terminal_laboratories.md) — Windows Terminal, kitty, WezTerm, Zed/GPUI, Qt, SDL, and other implementation laboratories.
- [13_low_luminance_oled_transport_and_temporal_gotchas.md](13_low_luminance_oled_transport_and_temporal_gotchas.md) — near-black OLED behavior, VRR/gamma shifts, 4:4:4, DSC, precision, and multi-monitor transport issues.
- [14_second_pass_open_questions.md](14_second_pass_open_questions.md) — unresolved questions and future research queue.
- [SOURCES.md](SOURCES.md) — primary/secondary source map with notes.

## One-sentence mental model

**HDR describes a wider/more meaningful color/luminance signal; OLED/local dimming describes how spatially precisely the display hardware can realize that signal; the proposed compositor is an application-side algorithm that manipulates local contrast before presentation.**

## Likely long-term layering

```text
adaptive-photonics/
├── perception/
│   ├── luminance analysis
│   ├── spatial-frequency analysis
│   ├── glyph conflict model
│   └── adaptation/hysteresis
├── text/
│   ├── shaping
│   ├── glyph coverage
│   ├── raster/cache
│   └── semantic classes
├── renderer/
│   ├── image decode/color conversion
│   ├── linear-light composition
│   └── shaders
└── platform/
    ├── windows_advanced_color/
    └── wayland_color_management/
```

The point of the abstraction boundary is that Wayland protocol churn, NVIDIA behavior, DXGI details, and monitor behavior must not contaminate the perceptual algorithm.

## Near-term recommendation

Do not begin with a full code editor.

Begin with a renderer that accepts:
- a background image;
- shaped or pre-rendered text;
- a glyph/text mask;
- configurable display characteristics;
- optionally an HDR-capable output surface.

Then compare it against:
1. plain text over image;
2. globally dimmed image;
3. globally blurred image;
4. static translucent rectangle behind text.

Only after the adaptive approach wins should editor integration become the next hard problem.


## Second shotgun pass

A second deliberately over-broad research pass added four major directions that were not obvious from the first pass:

1. **Perception-informed conflict scoring** — castleCSF and related models make it plausible to reason in spatial/temporal frequency, luminance, visual angle, and chromatic sensitivity rather than inventing a readability score entirely from vibes.
2. **WebGPU/Electron as a serious prototype** — modern Chromium/WebGPU has FP16 HDR canvas support and extended tone mapping, making a portable HDR compute-shader prototype worth testing before committing to raw D3D/Vulkan.
3. **Existing renderer laboratories** — kitty 0.49 custom shaders, Windows Terminal shaders, WezTerm layered/parallax backgrounds, and Zed's GPU-native GPUI create much cheaper experimentation paths than building everything immediately.
4. **Low-luminance behavior as a first-class hardware criterion** — near-black crush, gray uniformity, refresh-dependent gamma, VRR flicker, 4:4:4 transport, and actual minimum-brightness behavior matter unusually much for this use case.

The first-pass architecture remains plausible, but these routes substantially expand the space of cheap prototypes and measurement techniques.
