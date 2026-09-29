# Capture, compositor, overlay, and editor-integration routes

The ideal architecture owns text geometry before final composition.

Reality may force integration with an existing editor. This file maps increasingly cursed alternatives.

## Route A — own the whole renderer

```text
editor model
  ↓
text layout/shaping
  ↓
glyph mask + theme
  ↓
adaptive wallpaper
  ↓
final composite
```

Pros:
- perfect semantic and geometric knowledge;
- easiest perceptual algorithm;
- easiest HDR composition.

Cons:
- accidentally writing a code editor.

Use for standalone prototype, not necessarily product.

## Route B — editor cooperates, sidecar renders background

Potential sweet spot.

Editor/plugin provides:
- visible viewport coordinates;
- line/token rectangles;
- exact glyph masks if possible;
- syntax colors;
- cursor/selection regions;
- scrolling transform.

Sidecar provides:
- wallpaper;
- GPU analysis;
- HDR output/background surface.

The existing editor continues rendering text.

This means the compositor only needs to know **where text will appear**, not reproduce the editor's entire font/layout engine.

### Coarse-to-fine cooperation

Version 0:
- line rectangles.

Version 1:
- token rectangles.

Version 2:
- glyph bounding boxes.

Version 3:
- real glyph coverage mask.

The value of each sophistication level can be measured before building the next.

## Route C — capture the editor

Windows Graphics Capture can capture windows/displays through D3D.

Microsoft explicitly notes that on HDR/Windows HD Color systems, using 8-bit BGRA can clip/ wash out HDR content and recommends `DXGI_FORMAT_R16G16B16A16_FLOAT` through **every component** of the capture pipeline when HDR must be preserved.

Source:
https://learn.microsoft.com/en-us/windows/uwp/audio-video-camera/screen-capture

That makes an HDR-capable sidecar technically more plausible than expected.

### Capture-based flow

```text
editor window
   ↓
Windows Graphics Capture FP16
   ↓
detect/extract text regions
   ↓
separate desired wallpaper/background?
   ↓
adaptive post-process
   ↓
overlay/replacement surface
```

But this is still inferior to cooperation because:
- semantic text information is lost;
- foreground and background may already be composited;
- glyph masks must be inferred;
- capture adds latency;
- privacy/security/capture permissions matter;
- recursive capture/overlay feedback must be prevented;
- screenshots of HDR may not preserve intended semantics.

Use capture as a research tool or compatibility fallback, not first architecture.

## OCR / text-detection tangent

If forced to infer text from final pixels, full OCR is probably the wrong tool.

We usually know:
- editor font;
- theme colors;
- grid/line spacing;
- viewport geometry;
- likely text regions.

Better approaches:
- color-key likely foreground pixels;
- compare temporal differences when wallpaper is known separately;
- edge/template detect glyph-like structures;
- editor accessibility tree for text + bounding ranges;
- cooperative plugin supplies logical text and locations while capture supplies exact pixels.

Full OCR can be a diagnostic/reference route but should not sit in the 240 Hz loop.

## Route D — transparent editor over a wallpaper compositor

Another possibility:

```text
adaptive wallpaper window
       ↓
transparent editor window
       ↓
desktop compositor
```

The adaptive wallpaper process receives text geometry from a plugin and only modifies the wallpaper.

Advantages:
- editor text renderer remains untouched;
- HDR background and text may be separate surfaces;
- integration can be loosely coupled.

Risks:
- transparent-window composition paths differ across platforms;
- text may render differently on transparent versus opaque surfaces;
- ClearType/subpixel AA is often restricted or altered for transparency;
- window shadows/blur/acrylic effects complicate exact geometry;
- multi-monitor coordinates/scaling;
- z-order/focus/input;
- HDR/SDR mixing between the two surfaces.

This should be tested very early before relying on it.

## Route E — compositor plugin/effect

### KWin

A KWin effect could theoretically modify final window content or background before presentation.

Problem:
KWin does not know which pixels correspond to glyph semantics.

A better advanced architecture could define a cooperating Wayland surface:
- editor/main surface;
- auxiliary mask/protection surface;
- compositor effect consumes both.

This becomes custom protocol/compositor work and is not an MVP.

### Windows DWM

DWM is not a friendly public "write arbitrary per-window shader" extension point.

Avoid architectures that require unsupported DWM injection/hooking.

Use ordinary DirectComposition/overlay windows or own swapchain instead.

## Route F — terminal as a sandbox

Terminals are attractive because:
- monospace grid;
- lots of real text;
- simple background model;
- scrolling;
- already GPU-rendered.

### Windows Terminal

Experimental HLSL post-processing shaders can access terminal/background textures.

Excellent first shader sandbox.

### kitty

As of kitty 0.49.0 (2026-09-21), kitty has official custom shaders.

Docs:
https://sw.kovidgoyal.net/kitty/custom-shaders/

Properties especially relevant here:
- shaders run at the end of kitty's rendering pipeline;
- color is linear RGB;
- shader pipeline can chain multiple groups;
- named intermediate textures exist;
- persistent texture is available;
- event-driven activation can save work.

This is even better than expected for:
- multi-pass detail analysis;
- temporal state experiments;
- debugging halos/shimmer.

Caveat:
at end-of-pipeline, text and background are already rendered together. The available shader data must be inspected to determine whether text/background/mask information can be separated cleanly.

Kitty's graphics protocol also explicitly supports images below text with alpha blending:
https://sw.kovidgoyal.net/kitty/graphics-protocol/

That may allow designing test scenes where wallpaper is known and text composition behavior is controlled.

### WezTerm

WezTerm directly supports:
- background images;
- HSB transforms;
- layered backgrounds;
- alpha;
- parallax attachment.

Docs:
- https://wezterm.org/config/lua/config/window_background_image.html
- https://wezterm.org/config/lua/config/window_background_image_hsb.html
- https://wezterm.org/config/lua/config/background.html

The parallax background feature is particularly relevant to the user's desire for a stronger sense of depth.

WezTerm already recognizes the basic readability problem and provides brightness/saturation transformations, but they are global/static rather than glyph-local.

Possible experiment:
use WezTerm as a "baseline product" and compare adaptive processing against its static HSB/background settings.

## Route G — custom-GPU code editor

### Zed

Zed is an unusually interesting future integration target because it already uses a custom GPU UI renderer rather than a DOM.

Zed describes its GPUI architecture as rendering the editor like a videogame, with custom shaders for primitives such as rectangles, shadows, text, icons, and images.

Source:
https://zed.dev/blog/videogame

Potential advantages:
- open source;
- real editor;
- renderer is already explicit/native/GPU;
- glyph atlas/text pipeline exists;
- likely much easier to add a background-processing pass than in VS Code DOM.

Research questions:
- Windows/Linux backend parity;
- exact color-management support;
- HDR swapchain support;
- where wallpaper/background would enter renderer;
- how text alpha/glyph atlas is represented;
- whether renderer already works in linear light;
- how hard a custom experimental branch would be to maintain.

Do not assume the user wants to switch editors. Treat Zed as a **reference implementation and laboratory**.

## Route H — Electron/WebGPU editor

Covered in `08_web_chromium_electron_webgpu.md`.

Potentially:
- Monaco/editor for interaction;
- WebGPU background;
- browser text;
- plugin/DOM supplies protection geometry.

This route could preserve mature code editing while avoiding native graphics plumbing.

## Linux screenshot/portal caution

The XDG screenshot portal returns ordinary screenshot files and its color-pick API exposes sRGB-like normalized values.

Do not assume portal screenshots preserve:
- HDR headroom;
- scRGB values;
- display mastering metadata;
- original surface color descriptions.

Therefore screenshots are not a trustworthy way to validate HDR luminance mapping.

Use:
- known shader test patterns;
- compositor/debug logs;
- actual display measurement.

## Remote desktop tangent

Remote desktop/streaming can destroy or reinterpret:
- HDR transfer functions;
- color profiles;
- subpixel assumptions;
- physical luminance;
- DPI;
- text antialiasing.

Therefore:
- the visual algorithm might still function remotely;
- physical-nit calibration absolutely cannot be assumed portable through remote sessions.

Detect remote/virtual displays and fall back to relative SDR semantics unless proven otherwise.

## Window movement between displays

A serious implementation must handle:
- SDR → HDR monitor;
- HDR → SDR monitor;
- mixed DPI;
- different primaries;
- different SDR white level;
- different minimum/peak luminance;
- partially spanning displays.

Display capability is not startup-only state.

Windows explicitly notes Advanced Color state/capabilities can change due to user/OS policy.

Wayland output descriptions can likewise change.

The presentation backend needs a live capability/update model.

## Integration principle

Prefer this order:

1. **own glyph mask**
2. **cooperate with editor**
3. **use editor GPU hooks**
4. **use transparent/sidecar composition**
5. **infer from captured pixels**
6. **hook the desktop compositor**

Every step downward loses semantic information and adds platform fragility.
