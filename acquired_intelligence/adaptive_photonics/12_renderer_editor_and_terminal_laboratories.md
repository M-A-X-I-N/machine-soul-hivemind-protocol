# Renderer, editor, and terminal laboratories

Before inventing machinery, steal ideas from software that already solved adjacent parts of the problem.

## Ranking by experimental usefulness

Roughly:

1. **Windows Terminal HLSL** — cheapest Windows post-process experiment.
2. **kitty custom shaders** — surprisingly rich Linux/cross-platform multi-pass post-process lab.
3. **WezTerm** — excellent baseline for layered/depth-oriented wallpaper presentation.
4. **Standalone Electron/WebGPU** — potentially easiest serious cross-platform HDR/compute prototype.
5. **Zed/GPUI** — unusually compelling full-editor reference or eventual fork.
6. **Qt RHI / SDL3** — useful native-ish abstraction candidates.
7. **Raw D3D/Vulkan** — final-control path when abstractions become the limitation.

## Windows Terminal

Existing research already identified:
- experimental pixel shader path;
- background image texture;
- real text and scrolling.

Use it for:
- local dimming around text;
- cheap masks;
- temporal stability;
- proving the aesthetic concept.

Do not demand HDR from this first sandbox.

## kitty 0.49 custom shaders

kitty 0.49.0, released 2026-09-21, added official custom shader support.

Docs:
- https://sw.kovidgoyal.net/kitty/custom-shaders/
- https://sw.kovidgoyal.net/kitty/changelog/

Notable details:
- shaders are written in Slang;
- shaders run at the end of kitty's rendering pipeline;
- input/output colors are linear RGB;
- multiple shader groups can be chained;
- named offscreen textures `a` and `b` exist;
- a persistent texture exists for frame-to-frame state;
- groups can run only on selected events/animations.

This is **extremely useful**.

Potential experiments:
- multi-pass local edge map;
- temporal smoothing using persistent texture;
- visualization of local contrast;
- suppression fields;
- scrolling behavior;
- GPU cost;
- custom debugging overlays.

### Limitation

Because custom shaders run after kitty's own rendering, the fully rendered terminal frame may already combine:
- text;
- cell backgrounds;
- images.

Need inspect `KittyTextures` and available uniforms/textures to learn whether:
- clean text masks are available;
- background images can be sampled separately;
- cell semantic data is exposed.

If not, use controlled colors/backgrounds so text can be inferred for the experiment.

## kitty graphics protocol

The kitty graphics protocol allows images:
- at pixel positions;
- below text;
- above text;
- alpha blended;
- scrolling with terminal content.

Docs:
https://sw.kovidgoyal.net/kitty/graphics-protocol/

This gives a way to create controlled test scenes:
- wallpaper/image below text;
- known image data;
- known terminal foreground.

It may be enough to build the first Linux proof without touching KWin/Vulkan directly.

## WezTerm

WezTerm already supports:
- wallpaper images;
- brightness/saturation/hue transforms;
- multiple image/gradient/color layers;
- opacity;
- parallax scrolling attachments.

Docs:
- https://wezterm.org/config/lua/config/window_background_image.html
- https://wezterm.org/config/lua/config/window_background_image_hsb.html
- https://wezterm.org/config/lua/config/background.html
- https://wezterm.org/config/appearance.html

The parallax feature is especially fun because it explicitly increases the impression that a background layer is spatially farther away.

This makes WezTerm useful in two ways:

### Baseline
How far can static global transformations get before adaptive rendering matters?

### Inspiration
Depth-enhancing wallpaper behavior may be complementary to glyph protection.

Imagine:
- subtle parallax;
- strong spatial-depth image;
- adaptive detail suppression only under text.

That is closer to the user's aesthetic objective than a normal translucent terminal.

## Zed / GPUI

Zed's GPUI is designed around a custom GPU renderer.

Zed describes:
- custom shader per primitive;
- GPU-rendered rectangles, shadows, text, icons, images;
- cached glyph rendering;
- aggressive 120 FPS responsiveness.

Source:
https://zed.dev/blog/videogame

Why it is unusually relevant:
- full code editor;
- open source;
- GPU-native;
- text-intensive;
- custom UI framework instead of Chromium DOM.

Potential integration route:
1. add wallpaper/image primitive behind editor;
2. capture glyph coverage/text geometry already known to renderer;
3. build conflict/protection texture;
4. run background-processing pass;
5. leave text rendering mostly untouched.

This could be dramatically easier than integrating at equivalent depth into VS Code.

### Research questions before considering a fork

- Which backends are used on Windows/Linux?
- Is rendering linear/gamma-correct?
- How are glyph atlases stored?
- Is text mask alpha directly available to a shader?
- Does GPUI support HDR swapchains/colorspaces?
- Can a custom post-process be isolated to one editor pane?
- How invasive would background-image support be?
- Can the experiment remain a patch/plugin instead of permanent fork?

Even if never used, Zed is a valuable reference codebase.

## Glyph atlas sampling warning

GPU text renderers often cache glyph coverage in atlases.

Potential pitfalls:
- bilinear filtering leaks neighboring coverage;
- half-texel positioning;
- atlas padding;
- mipmaps;
- subpixel phase variants;
- fractional positioning;
- gamma-correct mask interpretation.

A tiny one-pixel gray fringe that is irrelevant in ordinary UI can become obvious on OLED at high contrast.

When building custom text:
- test nearest vs linear sampling;
- pad atlas entries;
- inspect fractional coordinate math;
- use explicit coverage semantics.

## Skia tangent

Skia is relevant both directly and through Chromium.

Its text-rendering history includes deliberate gamma adjustments to compensate for how light-on-dark/dark-on-light text perceptually changes weight.

That is a reminder:
**geometric coverage is not necessarily the final perceptually ideal alpha mask.**

Potential architecture:
- keep raw coverage;
- optionally apply perceptual/gamma correction as a final mask stage;
- make correction polarity/luminance-aware.

Do not bake such correction irreversibly into glyph cache.

## Qt RHI

Qt's Rendering Hardware Interface can abstract across graphics APIs and exposes HDR-capable swapchain formats.

Docs:
https://doc.qt.io/qt-6/qrhiswapchain.html

Potential use:
- native desktop shell;
- high-performance custom shaders;
- fewer platform-specific presentation details initially.

Risks:
- if precise Wayland color description or Windows scRGB behavior is missing, eventually need native escape hatch;
- Qt text rendering may not expose exactly the glyph masks desired.

Still an excellent prototype candidate.

## SDL3 color machinery

SDL3 has substantially more color-space awareness than old SDL mental models suggest.

Its surfaces/rendering machinery includes:
- colorspace tags;
- SDR white point;
- HDR headroom;
- linear-space rendering concepts;
- HDR10/BT.2020-related formats.

Potential role:
- portable native window/input layer;
- Vulkan/D3D rendering owned by project;
- easier prototype lifecycle than raw platform windowing.

Needs validation specifically for:
- HDR window surfaces;
- Wayland color-management-v1 integration;
- Windows Advanced Color swapchains.

## GLFW

GLFW remains excellent for simple native windows and Vulkan surface creation.

But long-running HDR feature requests suggest it should **not** be expected to solve color-management/presentation semantics for us.

If used:
- treat GLFW as "make a window";
- own Vulkan/DXGI color management separately.

## Alacritty / Rio / other terminals

These are useful references for:
- glyph atlases;
- GPU text;
- cell damage tracking;
- render performance.

Rio's WebGPU-oriented renderer is especially interesting as a reference for a GPU terminal built on modern portable graphics abstractions.

No need to integrate unless its architecture proves uniquely convenient.

## Renderer-laboratory decision tree

```text
Need to test visual idea only?
    ├── Windows → Windows Terminal shader
    └── Linux   → kitty custom shader

Need multi-layer/depth wallpaper baseline?
    └── WezTerm

Need serious portable GPU prototype?
    ├── Electron/WebGPU
    ├── Qt RHI
    └── SDL + own GPU backend

Need real editor renderer?
    └── inspect Zed GPUI

Need exact platform/HDR control?
    ├── Windows → D3D/DXGI/scRGB
    └── Linux   → Vulkan/Wayland color-management
```

## Useful source-reading strategy

For every reference implementation, specifically inspect:
- glyph raster format;
- glyph atlas cache;
- text blend shader;
- gamma/coverage correction;
- background/image primitive;
- color-space conversion;
- swapchain format;
- dirty-region model;
- frame pacing;
- multi-monitor updates;
- HDR capability detection.

This avoids reading entire UI frameworks when only five rendering seams actually matter.


## Third-pass addition — Ghostty custom shaders

Ghostty is now one of the most attractive first live-text laboratories.

Official project/docs:
- https://github.com/ghostty-org/ghostty
- https://ghostty.org/docs/config/reference#custom-shader

Ghostty supports custom GLSL post-process shaders with the rendered terminal exposed through `iChannel0`, and multiple shaders may be chained.

A community implementation at https://github.com/lexrus/lex-ghostty-shaders demonstrates a particularly useful composition pattern: with a transparent terminal background, terminal glyph pixels remain in the foreground texture while generated imagery is composited only where terminal alpha leaves room. The shader performs premultiplied-alpha "over" composition so glyphs remain unchanged.

That gives a cheap route to:
- use real terminal glyph alpha as the protection mask;
- generate or sample wallpaper underneath it;
- locally dim/filter only the background;
- compare exact untouched glyphs against adaptive-background processing.

### Ghostty versus kitty

- **Ghostty:** likely simpler for direct glyph/background separation through alpha.
- **kitty:** richer experimental shader graph, intermediate textures, persistent state, event-driven execution, Slang.
- **WezTerm:** strongest existing layered/parallax wallpaper baseline.

Use all three as complementary laboratories rather than trying to pick a winner.

## Third-pass addition — JetBrains already owns wallpaper insertion

JetBrains IDEs/platform themes already support background images and transparency. Current plugins also provide background images and Windows Acrylic-style effects.

Therefore a JetBrains prototype should focus on the unsolved seam:
- visible glyph geometry / coverage;
- viewport transforms;
- semantic token metadata;
- communication with a GPU sidecar;

rather than spending engineering effort merely putting an image behind the editor.

## Third-pass addition — capture/filter laboratories

Before building a dedicated capture backend, useful existing hosts include:

- **Magpie / MagpieFX:** mature Windows Graphics Capture plus multipass D3D11 compute-shader effects, FP16-capable intermediate formats.
- **OBS + obs-shaderfilter:** capture any editor window, then run arbitrary shader experiments in a color-aware filter pipeline.
- **GlassCode:** direct JetBrains capture/process/overlay ancestor and crude foreground/background-classification baseline.

These can validate filter behavior independently of production integration.
