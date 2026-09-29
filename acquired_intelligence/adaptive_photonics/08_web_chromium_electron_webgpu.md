# Chromium, Electron, WebGPU, and CSS HDR tangent

This entire route looked much less serious before the second research pass.

It is now worth treating a **standalone Chromium/Electron/WebGPU prototype** as a first-class option, because modern Chromium has real HDR color-space machinery, WebGPU can use FP16 canvas formats with extended tone mapping, and Chromium's Wayland stack gained upstream color-management support.

None of this proves that an Electron app will behave perfectly on the exact Windows/KDE/NVIDIA setup. It makes it cheap enough to test.

## Chromium has explicit HDR/scRGB color-space machinery

Chromium's `gfx::ColorSpace` includes constructors for:
- extended sRGB;
- linear sRGB/scRGB;
- scRGB linear with an 80-nit SDR-white convention;
- HDR10 / BT.2020 + PQ;
- HLG.

Source:
https://chromium.googlesource.com/chromium/src/+/main/ui/gfx/color_space.h

That means Chromium internally understands the conceptual spaces this project cares about rather than treating HDR as video-only magic.

## Wayland color-management support

Chromium added support for the upstream Wayland `color-management-v1` path in 2025-era development, enabling HDR surface rendering in modern Wayland environments.

This matters for Electron because Electron rides Chromium's graphics stack.

Do not assume:
- every Electron release enables every Chrome flag/path identically;
- every Linux compositor/GPU combination works;
- an HDR WebGPU canvas automatically becomes an ideal Wayland scRGB surface.

But the dependency chain is promising enough to prototype.

## Electron state in 2026

Electron 44 was released August 25, 2026 and ships Chromium 152.

Sources:
- https://www.electronjs.org/blog/electron-44-0
- https://releases.electronjs.org/release/v44.0.0

Electron also moved to Wayland-native behavior on Linux in its recent platform work.

This makes a modern Electron build materially different from the older "Electron means XWayland and SDR browser canvas" mental model.

## WebGPU HDR canvas

Chrome/WebGPU added an extended tone-mapping mode.

Conceptual configuration:

```javascript
context.configure({
    device,
    format: "rgba16float",
    toneMapping: { mode: "extended" },
});
```

In `standard` mode, output is constrained to the SDR display range. In `extended` mode, values can use the display's extended dynamic range where supported.

Source:
https://developer.chrome.com/blog/new-in-webgpu-129

Chrome 131 added a way to inspect the configured tone-mapping mode through `getConfiguration()`.

Source:
https://developer.chrome.com/blog/new-in-webgpu-131

### Why this is exciting

WebGPU gives us:
- compute shaders;
- fragment shaders;
- FP16 render targets;
- textures;
- multi-pass filtering;
- high-performance image processing;
- cross-platform API surface.

That is almost exactly what the adaptive algorithm needs.

A standalone Electron/WebGPU prototype could therefore implement:

```text
wallpaper texture
   ↓
compute: pyramid / gradients / luminance
   ↓
glyph-mask texture
   ↓
compute: conflict / protection
   ↓
compute or fragment: local suppression
   ↓
FP16 final surface
   ↓
extended WebGPU tone mapping
   ↓
Chromium platform compositor
```

without writing DXGI or Vulkan platform code on day one.

## CSS Color HDR

The CSS Color HDR Level 1 draft introduces HDR-oriented color spaces and dynamic-range control.

Current draft:
https://www.w3.org/TR/css-color-hdr-1/

Relevant concepts include:
- `rec2100-pq`;
- `rec2100-hlg`;
- `rec2100-linear`;
- HDR reference white;
- `dynamic-range-limit`.

The `dynamic-range-limit` property is particularly interesting because it gives a declarative way to constrain how far HDR content may exceed reference white.

For a renderer implemented mostly in WebGPU, CSS HDR may still matter for:
- surrounding UI;
- native DOM controls;
- text/UI elements outside the canvas;
- testing browser color-management behavior.

## Dynamic-range media query

The web platform has `dynamic-range` media features that can indicate an HDR-capable output environment.

Important caveat:
**capability is not necessarily equivalent to "the exact output path is currently in HDR and will preserve my values."**

Feature-detect the real rendering path and test output rather than trusting one media query.

## Float ImageData / canvas machinery

Modern Chromium/web standards also include float16 image-data support.

Potential uses:
- debug/export intermediate HDR buffers;
- CPU-generated reference images;
- comparison tests;
- synthetic patterns.

Do not move large 4K frames through JS CPU memory every refresh if WebGPU can keep them resident on GPU.

## Electron as a possible editor shell

A standalone Electron app could provide:
- Monaco or another code-editor component;
- custom WebGPU background canvas;
- DOM text/editor overlay;
- IPC/native helpers only where necessary.

But there is a major architectural question:

### DOM text over WebGPU background

If text is rendered independently by Chromium, the WebGPU layer needs to know exact glyph geometry/masks to adapt the wallpaper.

Possible routes:
1. accept coarse rectangles around text runs;
2. render code text inside the same WebGPU canvas;
3. use browser APIs/canvas text to generate masks;
4. have editor layout expose visible token/glyph geometry;
5. render adaptive background first, then let Chromium draw text normally.

Option 5 is particularly interesting:
- the adaptive algorithm does **not** need to render the text itself if the editor can provide enough geometry for a protection mask;
- Chromium can keep doing its mature text shaping/rasterization;
- only background processing becomes custom.

The mask could begin as token/line bounding boxes and later become glyph-level.

## VS Code tangent

VS Code is Electron, but this does not mean an extension can simply seize the final Chromium compositor.

A normal extension does not have arbitrary control over:
- Chromium swapchain format;
- editor's final GPU composition;
- underlying workbench renderer.

However, the Chromium/WebGPU research is still relevant because:
- a fork/experimental build of an Electron editor is more plausible than before;
- webview/custom editor prototypes may demonstrate pieces;
- upstream Electron eventually makes HDR-aware application UI less exotic.

## WebGPU versus native Vulkan/D3D

### WebGPU advantages
- dramatically less platform boilerplate;
- same shaders/API on Windows and Linux;
- Electron window/input/UI for free;
- easy interactive parameter controls;
- excellent prototype velocity.

### Native advantages
- precise presentation control;
- easier access to platform display capability APIs;
- fewer browser/compositor unknowns;
- better control over text rasterization if desired;
- potentially lower overhead / more predictable HDR mapping.

Recommended approach:
**WebGPU prototype first if HDR actually reaches the panel correctly on both target OSes.**
If it does not, retain the algorithm/shader work and replace only the presentation backend.

## Critical experiments

Build the smallest possible Electron/WebGPU app that:

1. requests `rgba16float`;
2. requests extended tone mapping;
3. draws patches at 0.5, 1.0, 2.0, 4.0 relative values;
4. reports browser/Electron/Chromium versions;
5. runs on Windows HDR;
6. runs on KDE Wayland HDR;
7. checks whether >1.0 visibly/predictably survives;
8. compares against a known native scRGB test program.

Then test:
- mixed DOM SDR text over HDR canvas;
- DOM opacity/transforms;
- screen capture;
- screenshot behavior;
- moving the window between SDR/HDR displays.

If these tests pass, Electron may be the fastest serious implementation route.

## Browser implementation warning

The browser owns several layers:
- canvas color space;
- WebGPU texture format;
- Skia;
- Viz compositor;
- OS surface/swapchain;
- Wayland or Windows color management.

A bug or policy in any one can change the result.

Therefore expose a **platform validation screen** with known test patches before trusting the adaptive algorithm.

## Interesting future possibility

A standalone Electron editor could eventually offer:
- normal Chromium text/layout;
- WebGPU wallpaper analysis;
- HDR-aware adaptive background;
- CSS HDR UI accents;
- platform-native helper only for display characterization.

That is a surprisingly attractive compromise between "hack an existing IDE" and "write a code editor from scratch."
