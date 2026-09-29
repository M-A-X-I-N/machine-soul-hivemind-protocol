# Miscellaneous implementation ammunition

This is the intentionally miscellaneous file: things that are not yet important enough to own an architecture, but have a nontrivial chance of saving pain later.

## Variable-font optical sizing

OpenType defines the registered `opsz` axis specifically for adapting a typeface to the size at which it is viewed.

Source:
https://learn.microsoft.com/en-us/typography/opentype/spec/dvaraxistag_opsz

Typical optical-size design changes can include:
- glyph proportions;
- stem weights;
- fine detail;
- widths/apertures.

The OpenType spec explicitly notes that **viewing distance matters**, not only physical size.

This is unusually relevant because the project is trying to push code text smaller than the user's current comfortable threshold.

Experiment:
- fonts with `opsz` automatic/default;
- force smaller optical size;
- force larger optical size;
- measure ambiguous-glyph discrimination at equal physical text size.

A coding font with genuinely good optical-size masters could improve readability before any custom shader runs.

## Variable-font grade

Some font families expose a grade-like axis even when not standardized as universally as the core registered axes.

Grade changes stroke darkness while trying to preserve advance width/layout more closely than normal weight changes.

Potential use:
- a one-time font tuning control for high-PPI dark-mode coding;
- perhaps a small global grade increase at very low luminance.

Avoid local per-glyph adaptive grade unless testing proves it is not visually disgusting.

## Skia's "gamma hack"

Skia documents text-rasterization behavior under the wonderfully named **Raster Tragedy**.

Source:
https://docs.skia.org/docs/dev/design/raster_tragedy/

Important lesson:
- geometric glyph coverage is not necessarily perceptually neutral;
- light-on-dark can visually bloom/change weight;
- Skia applies destination/color-aware adjustments in some text paths;
- such adjustment belongs at the final coverage/blend stage.

This reinforces an architectural separation:

```text
raw glyph coverage
    ↓
optional hint/subpixel geometry
    ↓
perceptual coverage correction
    ↓
final blend
```

Do not destroy raw coverage in the glyph cache if later stages may need different correction for:
- polarity;
- luminance;
- output display.

## Cross-platform shader source: Slang

Slang is a modern HLSL-like shading language/compiler with targets including:
- DXIL / Direct3D;
- SPIR-V / Vulkan;
- GLSL;
- Metal;
- WGSL;
- CUDA;
- C/C++ host forms.

Docs:
- https://docs.shader-slang.org/
- https://docs.shader-slang.org/en/stable/external/slang/docs/command-line-slangc-reference.html

This is extremely tempting for the project because the same core image-processing kernels could potentially compile to:
- Windows native D3D;
- Linux Vulkan;
- WebGPU/WGSL experiments.

Caveats:
- target feature parity differs;
- WGSL backend has restrictions;
- generated code/bindings must be validated;
- bringing a compiler dependency is not free.

Still, before maintaining separate HLSL/SPIR-V/WGSL shader sources, evaluate Slang.

Bonus: kitty 0.49 custom shaders are themselves written in Slang, making this ecosystem even more relevant.

## Shader architecture

Try to make algorithms backend-neutral:

```text
analysis_luminance
analysis_detail_pyramid
build_protection_field
compute_conflict
apply_background_transform
composite_debug_views
```

Avoid having one giant platform shader containing:
- DXGI assumptions;
- Wayland assumptions;
- editor semantics.

Small kernels are easier to:
- compare between D3D/Vulkan/WebGPU;
- unit-test;
- profile;
- visualize.

## OpenEXR for debug/reference frames

OpenEXR stores high-dynamic-range floating-point image data and is designed around scene-linear values.

Sources:
- https://openexr.com/en/latest/
- https://openexr.com/en/latest/SceneLinear.html

For project debugging, EXR is attractive for:
- exact-ish linear intermediate dumps;
- values >1.0;
- negative extended-gamut values if needed;
- multi-channel debug output.

Possible channels:
- R/G/B final linear scene;
- glyph mask;
- protection field;
- conflict score;
- suppression amount;
- depth estimate;
- spatial-frequency energy.

A single multi-channel EXR could preserve an entire frame's analysis state for offline replay.

This is vastly better than taking a PNG screenshot and wondering where the HDR went.

## Deterministic frame replay

Build the renderer so a bug can be reduced to:

```text
replay-frame/
    background.exr
    glyph_mask.exr
    metadata.json
    expected_settings.json
```

Then reproduce the exact adaptive pass without:
- editor;
- Wayland;
- Windows;
- timing;
- monitor.

This separates:
- algorithm bugs;
- presentation bugs;
- editor-integration bugs.

## GPU debugging

### PIX on Windows

PIX GPU captures can inspect:
- pipeline state;
- bound resources;
- render targets;
- shader execution;
- pixel history;
- individual shader debugging.

Source:
https://devblogs.microsoft.com/pix/gpu-captures/

This will be invaluable if a pixel is "wrong" after several compute/render passes.

### RenderDoc

RenderDoc is a standard cross-API graphics debugger for Vulkan/D3D/OpenGL-class workflows.

Potential use:
- inspect FP16 textures;
- verify intermediate masks;
- examine render-pass order;
- debug Linux Vulkan path.

Exact HDR presentation may not be faithfully represented by a debugger screenshot, but intermediate GPU resources are still inspectable.

### NVIDIA Nsight

Given the user's NVIDIA GPU:
- Nsight Graphics can profile/debug Vulkan/D3D;
- useful if shader cost or synchronization becomes weird.

Do not add vendor-specific runtime dependencies; use as developer tooling.

## GPU timestamp queries

Do not profile image processing with CPU wall-clock around `present()`.

Add GPU timestamp queries around:
- pyramid generation;
- mask dilation;
- conflict computation;
- reconstruction;
- final composite.

The project should know whether an algorithm costs:
- 0.05 ms;
- 0.5 ms;
- 5 ms.

That determines whether expensive perception work belongs:
- per frame;
- on dirty tiles;
- at lower resolution;
- offline/cache time.

## Offline golden tests

For every algorithm:
- fixed input image;
- fixed text mask;
- fixed parameters;
- deterministic output buffer.

Store:
- numeric error tolerances;
- reference EXR;
- debug intermediates.

Cross-backend test:
- D3D output;
- Vulkan output;
- WebGPU output.

They should match within documented floating-point tolerance before display mapping.

## Precision choices

Use FP16 for most real-time color/image surfaces unless proven insufficient.

Potential exceptions:
- accumulated temporal state;
- high-order filters;
- CPU reference implementation;
- sensitive low-luminance calculations.

Create a FP32 reference path offline so FP16 errors can be quantified rather than guessed.

## Premultiplied alpha

Be explicit.

For a compositor doing many layers/masks:
- choose premultiplied-alpha conventions;
- document them;
- ensure color-space conversion and alpha treatment are correct.

A huge class of "weird dark fringe around text" bugs is actually alpha/color math.

Never gamma-encode alpha.

## Color-space tagging of input wallpaper

Wallpaper files can contain:
- sRGB;
- Display P3;
- embedded ICC;
- HDR PQ/HLG;
- no metadata.

Input decode should produce:
- known linear working-space RGB;
- explicit metadata;
- warning/fallback for untagged content.

Otherwise an adaptive algorithm comparing numerical luminance is meaningless.

## HDR wallpaper itself

If the source wallpaper is HDR:
- preserve its relative scene structure;
- tone-map/cap it aggressively for the user's low-luminance coding mode;
- do not automatically let its highlights reach gaming/movie HDR brightness.

Coding mode can use an HDR source while intentionally mapping the whole image into a low-luminance band.

That may actually preserve **more** shadow/highlight structure than starting from an SDR-compressed wallpaper.

## Synthetic depth backgrounds

A tangent that may be aesthetically useful without ML:
- layered 2D wallpaper;
- known depth per layer;
- subtle parallax;
- optional blur per layer;
- adaptive protection applied independently per layer.

WezTerm's parallax layer system demonstrates the basic concept.

This gives perfect depth metadata without running a monocular depth model.

## Subpixel microscope test

If the actual panel is purchased:
- macro/microscope photo subpixels;
- determine orientation/order;
- compare against manufacturer claims;
- measure pixel pitch.

Then:
- FreeType Harmony geometry experiment;
- ClearType on/off;
- grayscale AA;
- custom subpixel kernel.

This is unnecessary if RGB-stripe 4K looks perfect.

It is also irresistible.

## Window-system event logging

Every presentation backend should log capability transitions:
- display added/removed;
- HDR toggled;
- ICC profile changed;
- window changes dominant output;
- DPI changed;
- refresh changed.

Include enough state in bug reports to recreate display assumptions.

## Explicit debug modes

Build these early:
- show raw wallpaper;
- show linear luminance;
- show spatial-frequency bands;
- show glyph coverage;
- show dilated protection mask;
- show conflict heatmap;
- show suppression amount;
- show pre-tone-map final;
- show clipped/out-of-gamut pixels;
- show target-nit estimate.

A visual algorithm without visual diagnostics becomes superstition very quickly.

## Final miscellaneous principle

Whenever a feature can be represented as data rather than hidden behavior, prefer data.

Examples:
- protection field texture;
- conflict texture;
- display capability struct;
- calibration curve;
- text mask;
- per-band gain map.

Inspectable intermediate state is the difference between a fun graphics experiment and six months of "why the fuck is that letter darker on Tuesdays?"
