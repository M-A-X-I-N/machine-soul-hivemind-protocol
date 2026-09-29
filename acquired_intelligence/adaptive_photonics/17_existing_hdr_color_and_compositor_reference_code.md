# Existing HDR, color-management, capture, and compositor reference code

Research snapshot: 2026-09-30.

This file collects projects that do **not** solve the adaptive-code-background problem directly, but already contain difficult infrastructure or algorithms we may be stupid to reimplement.

The most important discovery is **libplacebo's HDR contrast-recovery pipeline**, which is strikingly close to an inverse version of one of our proposed filters.

---

## 1. libplacebo — potentially reusable rendering/color infrastructure

Repository:

https://github.com/haasn/libplacebo

License: LGPL-2.1-or-later.

The project describes itself as the core rendering algorithms/ideas of mpv rewritten as an independent library.

It supports:
- Vulkan;
- OpenGL;
- Direct3D 11;
- HDR tone mapping;
- dynamic histogram/peak measurement;
- gamut mapping;
- ICC profiles;
- 3D LUTs;
- dithering/error diffusion;
- debanding;
- scaling;
- custom shaders;
- high-level rendering abstractions.

### Why it may be more than a reference

The public API deliberately exposes multiple abstraction levels:
- raw color-space/math helpers;
- GPU abstraction;
- shader-generation primitives;
- shader dispatch;
- high-level renderer.

The README explicitly says one design goal is to hide GPU state/synchronization/color-space/subsampling/metadata complexity for image-processing applications.

That sounds suspiciously like infrastructure this project would otherwise rebuild.

### Custom hook system

`src/include/libplacebo/shaders/custom.h` exposes hooks at stages such as:

- RGB input;
- native color representation;
- converted RGB;
- **linearized** RGB;
- pre/post scaling;
- scaled;
- pre-output;
- final output before dithering.

The hook API exposes:
- current color representation;
- current color space;
- source/destination rectangles;
- GPU object;
- shader dispatch object;
- current texture or sampled color;
- temporary high-precision textures supplied by the renderer.

Temporary hook textures are documented as using sane renderable formats, generally **16-bit or floating point**.

This means a future native implementation could plausibly let libplacebo own:
- source image color interpretation;
- ICC;
- HDR/SDR transformations;
- gamut mapping;
- dithering;
- GPU abstraction;

while our hook owns:
- glyph protection texture;
- conflict map;
- local detail attenuation;
- wallpaper transform.

That is an architecture worth prototyping before custom-building the whole color pipeline.

---

## 2. libplacebo contrast recovery — almost our inverse algorithm

This is the most important algorithmic implementation found in the pass.

libplacebo has explicit HDR parameters:

- `contrast_recovery`;
- `contrast_smoothness`.

Its public documentation says the source is divided into **high-frequency and low-frequency components**, and a portion of high-frequency detail is added back after tone mapping.

### Renderer implementation

In `src/renderer.c`, `get_feature_map()`:

1. the rendered source is sampled;
2. `pl_shader_extract_features()` generates a perceptual intensity feature map;
3. the feature map is reduced to a lower resolution based on `contrast_smoothness`;
4. a low-pass sampler generates a smoothed/low-frequency map;
5. this texture is supplied to the color-mapping shader.

### Feature extraction

In `src/shaders/colorspace.c`, `pl_shader_extract_features()`:

1. source is linearized;
2. RGB is transformed toward LMS/IPT-style perceptual intensity;
3. nonlinear perceptual transforms are applied;
4. the shader outputs a single intensity feature.

This is already more perceptually informed than simply computing `(R+G+B)/3`.

### Detail reconstruction

During color mapping, libplacebo reconstructs a low-frequency value from the feature map and computes approximately:

```text
highres = perceptual source intensity
lowres  = smoothed feature intensity

detail = highres - lowres

base  = tone_map(highres)
sharp = tone_map(lowres) + detail

output = mix(base, sharp, contrast_recovery)
```

### Our inverse cousin

libplacebo wants:

> Tone mapping flattened local texture. Restore some of the high-frequency residual.

We want, near glyphs:

> Background detail competes with the glyph. Reduce selected high-frequency residual while preserving the low-frequency scene structure.

Conceptually:

```text
detail = highres - lowres

glyph_gain = 1.0 far from text
glyph_gain = 0.0..1.0 near conflicting text

output_intensity =
    lowres
  + detail * glyph_gain
```

More sophisticated:
- multiple frequency bands;
- glyph conflict controls gain;
- luminance/chroma separate;
- preserve major depth cues.

But libplacebo gives us a real production-quality example of:
- perceptual feature extraction;
- low-pass feature map;
- high-frequency residual recovery;
- GPU implementation;
- tunable smoothing scale.

This should be one of the first codebases examined when implementing the actual filter.

---

## 3. Gamescope — current Linux HDR/Wayland implementation reference

Repository:

https://github.com/ValveSoftware/gamescope

Gamescope is extremely useful because it exercises the exact modern Linux HDR stack we care about.

Current `src/Backends/WaylandBackend.cpp` contains upstream Wayland color-management support.

It creates image descriptions including:

### HDR10/PQ
Parametric image descriptions with HDR metadata/primaries/transfer functions.

### scRGB

The current source directly calls:

`wp_color_manager_v1_create_windows_scrgb(...)`

for Gamescope's scRGB application texture color space.

That makes Gamescope a concrete current implementation of the exact API our Wayland backend would use.

### Other reusable references

Gamescope also contains:
- output capability negotiation;
- Wayland image-description feedback;
- luminance/primaries/ICC information callbacks;
- Vulkan rendering;
- DRM/KMS output;
- nested Wayland compositor operation;
- HDR metadata;
- explicit content color-space tags;
- SDR-content-in-HDR handling;
- ReShade/effect support;
- HDR diagnostics/heatmaps and command-line tuning.

### Why it matters

When implementing Linux:

> Read Gamescope before interpreting the protocol from scratch.

It gives us working answers for:
- protocol feature detection;
- image-description lifetime;
- scRGB/PQ setup;
- output feedback;
- how a real compositor carries colorspace metadata alongside planes/textures.

### Secondary use: controlled test host

Gamescope can also act as a nested environment for some experiments.

Even though Linux gaming is not a project requirement, the compositor can be useful as a test laboratory because it already has extensive HDR instrumentation.

---

## 4. VK_hdr_layer — tiny historical bridge worth reading

Repository:

https://github.com/Zamundaaa/VK_hdr_layer

The README says the layer is no longer necessary with Mesa 25.1+ because Mesa gained direct color-management support.

It implemented:
- `VK_EXT_swapchain_colorspace`;
- `VK_EXT_hdr_metadata`;

by bridging Vulkan behavior to Wayland color-management protocols.

The author's own README says, essentially, "hacks; don't use for serious color work."

That makes it **bad infrastructure to depend on** but potentially **excellent educational source code**.

Why preserve:
- much smaller than Mesa/KWin/Gamescope;
- directly maps Vulkan HDR concepts onto Wayland protocol objects;
- useful for understanding the seam between WSI and compositor color management.

Use as a code-reading aid, not production dependency.

---

## 5. Magpie — robust arbitrary-window capture → multipass GPU transform

Repository:

https://github.com/Blinue/Magpie

License: GPL-3.0.

Magpie is a Windows window-scaling/postprocessing application with a mature capture/render pipeline.

It supports multiple capture methods:
- Windows Graphics Capture;
- Desktop Duplication;
- GDI;
- DWM shared-surface approaches.

Its current documentation recommends **Graphics Capture** for general use because of compatibility and smoothness.

### MagpieFX

MagpieFX is especially relevant.

It is a custom DirectX 11 compute-shader/effect format supporting:
- arbitrary input/output sizes;
- multiple intermediate textures;
- multiple passes;
- runtime parameters;
- FP16 capability declaration;
- many texture formats including `R16G16B16A16_FLOAT`;
- point/linear/wrap/clamp sampling;
- compute-style and pixel-shader-style passes;
- multiple render targets.

This is extremely close to the infrastructure a capture-based adaptive compositor needs.

### Relevance to this project

If GlassCode proves "capture and replace editor appearance is possible," Magpie proves:

> capture arbitrary Windows content and run a serious multipass GPU image-processing graph on it.

Potential uses:
- study robust window capture;
- study resize/frame pacing/display behavior;
- use MagpieFX as a quick algorithm sandbox if a no-op/no-scale configuration is practical;
- borrow effect-file ideas for our own shader graph.

### Caveat

Do **not** assume Magpie's current output path is HDR/scRGB-correct for our needs without dedicated verification.

Its value is primarily capture + GPU postprocessing architecture.

---

## 6. OBS Studio — mature cross-platform color-aware filter architecture

Repository:

https://github.com/obsproject/obs-studio

OBS contains another highly relevant reusable pattern:

> every image source/filter carries explicit color-space metadata through a portable graphics abstraction.

Its graphics API defines:

```text
GS_CS_SRGB          // SDR
GS_CS_SRGB_16F      // high-precision SDR
GS_CS_709_EXTENDED  // HDR / canvas / Mac EDR
GS_CS_709_SCRGB     // Windows/Linux HDR, 1.0 = 80 nits
```

and includes:
- `GS_RGBA16F`;
- D3D11/OpenGL/Metal abstractions;
- color-aware texture renders;
- source filters;
- capture systems;
- HDR/SDR conversion.

### Filter API

OBS exposes:

`obs_source_process_filter_begin_with_color_space(...)`

so filters can explicitly request/preserve the source color space rather than silently assuming SDR.

Built-in filters use this machinery.

This is a useful model for our own architecture:

```text
ImageSurface {
    texture
    representation
    color_space
    alpha_mode
    dynamic_range_metadata
}
```

rather than passing anonymous textures through the pipeline.

### scRGB handling

Current OBS source contains explicit SDR/scRGB multipliers based on its configured SDR white level and the 80-nit scRGB stimulus convention.

This is another production implementation to study when we get confused by reference-white semantics.

---

## 7. obs-shaderfilter — extremely cheap captured-window shader sandbox

Repository:

https://github.com/exeldro/obs-shaderfilter

License: GPL-2.0.

This plugin lets an OBS source run arbitrary user-defined shader code.

Features:
- HLSL-like OBS effects;
- custom uniforms exposed automatically as UI controls;
- extra texture inputs;
- configurable extra pixels around source;
- many included examples;
- works on an already-captured window source.

### Experimental use

A fast zero-product prototype could be:

```text
OBS Window Capture(editor)
        ↓
obs-shaderfilter
        ↓
prototype local mask / contrast algorithm
        ↓
OBS preview
```

This is not for daily coding.

It is for proving:
- filter math;
- shape inference;
- local contrast suppression;
- shader performance;
- parameter ranges.

The plugin even has dynamic-mask examples that demonstrate using another source as a texture input.

This could let an editor/plugin or synthetic test source provide a mask to the shader.

---

## 8. RenoDX — existing HDR pipeline surgery

Repository:

https://github.com/clshortfuse/renodx

License: MIT.

RenoDX modifies existing DirectX applications using the ReShade add-on system.

Its toolset can:
- replace shaders;
- inject buffers;
- add overlays;
- upgrade swapchains;
- upgrade texture resources;
- expose user settings.

Real mods commonly:
- upgrade RGBA8 render targets to RGBA16F;
- separate scene brightness from UI/HUD brightness;
- expose peak brightness;
- preserve unclamped highlight information;
- replace/fix tone mapping.

### Why it matters

RenoDX is practical evidence that an existing renderer can be retrofitted from:

`8-bit SDR assumptions`

to:

`floating-point intermediate + HDR output + independently controlled UI brightness`.

The independent **UI brightness** control is directly adjacent to our idea of placing code/UI in a different luminance band from the wallpaper.

### Potential code-reference topics

- swapchain upgrade;
- display peak detection;
- UI-vs-scene separation;
- shader replacement/injection;
- resource-format upgrades;
- where 8-bit clamping unexpectedly breaks HDR.

Even if we never hook another editor process, this code is useful for understanding Windows HDR surgery.

---

## 9. ReShade HDR shaders / Lilium — HDR analysis and debugging toolkit

Repository:

https://github.com/EndlesslyFlowering/ReShade_HDR_shaders

License: GPL-3.0.

This project focuses on:
- HDR analysis;
- postprocessing;
- inverse tone mapping;
- HDR10/scRGB interpretation.

Its analysis tooling recognizes explicit color-space modes such as:
- `CSP_HDR10`;
- `CSP_SCRGB`.

Why useful:
- reference HDR transfer/color math;
- visual nit-range analysis;
- waveform/debug views;
- black-floor/shadow debugging;
- sanity-checking output.

A future renderer should not invent every HDR diagnostic visualization from scratch.

This project can inspire/debug:
- "show me which pixels exceed X nits";
- black-level heatmaps;
- HDR-space conversions;
- clipping detection;
- reference-white overlays.

License must be considered before copying shader code.

---

## 10. Production infrastructure matrix

| Project | Hard problem already solved | Possible role |
|---|---|---|
| libplacebo | GPU/color abstraction, HDR/ICC/tone/gamut/dither, custom hooks, HF/LF contrast decomposition | library or core reference |
| Gamescope | modern Wayland HDR/scRGB + Vulkan/DRM | Linux backend reference/test host |
| VK_hdr_layer | minimal Vulkan↔Wayland HDR bridge | educational reference |
| Magpie | arbitrary Windows capture + multipass D3D11 compute effects | capture-backend reference/sandbox |
| OBS | cross-platform color-space-aware filter graph + capture | architecture reference/sandbox |
| obs-shaderfilter | arbitrary GPU shader over captured source | cheap experiment |
| RenoDX | upgrade existing SDR DirectX pipelines to HDR/FP16; separate UI brightness | Windows HDR surgery reference |
| ReShade HDR shaders | HDR analysis/debug/tonemapping shaders | validation/debug reference |

---

## 11. A less-stupid native architecture after this pass

Before:

```text
write D3D/Vulkan renderer
write color transforms
write HDR mapping
write filtering
write diagnostics
write everything
```

After studying existing implementations, a plausible architecture becomes:

```text
our domain
├── glyph/protection masks
├── perception/conflict model
├── adaptive detail suppression
├── user policy
└── editor integration

existing infrastructure
├── libplacebo or equivalent
│   ├── GPU abstraction
│   ├── colorspace conversion
│   ├── ICC
│   ├── tone/gamut mapping
│   ├── high-precision FBO management
│   └── dithering
│
├── Gamescope/KWin source
│   └── Linux presentation reference
│
└── native Windows presentation
    └── DXGI/scRGB
```

This is not yet an architecture decision.

But **"use libplacebo underneath our adaptive logic" is now a concrete option that deserves an early feasibility prototype**.

---

## 12. Particularly stealable implementation patterns

### Feature map + residual

From libplacebo:

```text
feature = perceptual_intensity(source)
low     = lowpass(feature)
detail  = feature - low
```

Our transform can modulate `detail` by glyph conflict.

### Explicit image metadata

From OBS/libplacebo:

Every texture should carry:
- color space;
- transfer;
- alpha mode;
- target/reference-white semantics.

Never pass a naked `Texture2D` and hope everybody remembers what its numbers mean.

### Platform capability objects

From Gamescope/OBS:
- inspect output capabilities;
- react to changes;
- explicitly tag surface/frame colorspace.

### Multipass declarative shader graph

From MagpieFX/libplacebo hooks:
- separate resources;
- named intermediate textures;
- small passes;
- dynamic parameters.

### UI-vs-scene luminance bands

From RenoDX:
- distinguish content scene brightness from UI brightness explicitly.

This maps almost perfectly onto:
- wallpaper luminance policy;
- code/UI luminance policy.

## Sources

- libplacebo: https://github.com/haasn/libplacebo
- Gamescope: https://github.com/ValveSoftware/gamescope
- VK_hdr_layer: https://github.com/Zamundaaa/VK_hdr_layer
- Magpie: https://github.com/Blinue/Magpie
- OBS Studio: https://github.com/obsproject/obs-studio
- obs-shaderfilter: https://github.com/exeldro/obs-shaderfilter
- RenoDX: https://github.com/clshortfuse/renodx
- ReShade HDR shaders: https://github.com/EndlesslyFlowering/ReShade_HDR_shaders
