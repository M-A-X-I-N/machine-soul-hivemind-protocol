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
