# Existing implementation reuse matrix and extra laboratories

Research snapshot: 2026-09-30.

This file consolidates the third shotgun pass into a practical question:

> Which existing projects should we **depend on**, **study deeply**, **use as experiment hosts**, **benchmark against**, or merely **steal one idea from**?

The answer is emphatically not "pick one project and fork it." The useful pieces are scattered across editor plugins, terminals, video renderers, compositors, capture tools, HDR modding ecosystems, and accessibility/AR research.

---

## 1. Ghostty — an unexpectedly clean background-only shader laboratory

Official project:

https://github.com/ghostty-org/ghostty

Ghostty has:
- built-in background image support;
- custom GLSL post-process shaders;
- Shadertoy-like uniforms;
- `iChannel0` containing the already-rendered terminal frame;
- multiple `custom-shader` entries that can be chained.

Official docs:
https://ghostty.org/docs/config/reference#custom-shader

Ghostty is MIT-licensed and very actively developed at the snapshot date.

### Why its alpha behavior is unusually useful

A community shader repository provides an especially revealing implementation:

https://github.com/lexrus/lex-ghostty-shaders

The `neuro_noise.glsl` shader explicitly documents a Ghostty configuration in which:
- glyph pixels from `iChannel0` are opaque/premultiplied;
- terminal background is transparent;
- generated visual content is composited behind the terminal frame;
- glyphs remain unchanged on top.

Its core composition is effectively:

```glsl
vec4 term = texture(iChannel0, uv);

float backA = 1.0 - term.a;

vec3 finalColor =
    term.rgb +
    generatedBackground.rgb * backA;

float finalAlpha =
    term.a +
    generatedBackground.a * backA;
```

This is profound for our experiments because it means we may not need to **infer** the glyph mask at all.

The terminal's own alpha can become the protection mask.

### What Ghostty can test cheaply

- wallpaper/pattern underneath real glyphs;
- preserve glyphs exactly while processing only background;
- local luminance suppression driven by terminal alpha;
- local detail suppression;
- glyph-distance-field generation from alpha;
- chained multi-pass filters;
- scroll behavior;
- background dither/banding;
- exact comparison of text untouched vs altered.

### Limitation versus kitty

Ghostty's custom-shader model appears cleaner for **foreground/background separation**.

kitty's newer custom-shader system is richer for:
- named intermediate textures;
- event-aware execution;
- persistent frame-to-frame state;
- Slang.

So they are complementary:

| Experiment | Prefer |
|---|---|
| easiest exact background-only transform | Ghostty |
| temporal persistence / multi-stage state | kitty |
| generated depth/parallax baseline | WezTerm |
| Windows equivalent simple shader | Windows Terminal |

### Interesting community lesson: dither

The inspected Ghostty `neuro_noise.glsl` deliberately adds roughly 1/256 noise to suppress visible banding in dark gradient regions.

That independently echoes KWin Acrylic-style/noise practices found elsewhere.

The repeated convergence suggests:
**after aggressively suppressing local wallpaper contrast, tiny dither/noise may become useful to prevent visible flat-gradient banding.**

---

## 2. JetBrains already solves wallpaper insertion

Before building editor-specific wallpaper mechanics, remember:

**JetBrains IDEs already support background images.**

The IntelliJ Platform theme system supports a `background` object with:
- image;
- transparency;
- fill;
- anchor.

JetBrains also exposes "Set Background Image" functionality in the IDE.

Therefore a JetBrains integration does not need to solve:
> How do we get an image behind code?

The real integration questions are:
- can a plugin obtain exact visible glyph geometry?
- can it provide or receive a GPU mask?
- can it alter only editor background rendering?
- can it cooperate with a native sidecar?
- can the native renderer avoid fighting JetBrains' own image implementation?

### Current Glass Effect plugin

A current JetBrains Marketplace plugin named **Glass Effect** provides:
- Windows 10/11 Acrylic-like blur;
- adjustable opacity;
- click-through support;
- compatibility with multiple JetBrains IDEs.

This is useful current evidence that:
- JetBrains window/native-material manipulation remains possible in 2026;
- users want translucency behind IDEs;
- JetBrains plugin + native Windows visual effects is not an alien integration model.

Do not confuse it with GlassCode:
- Glass Effect = current visual-material/transparency plugin;
- GlassCode = older capture/process/replacement architecture with foreground-shape detection.

Both are useful for different reasons.

---

## 3. DWMBlurGlass — concrete Acrylic-material implementation

Repository:

https://github.com/Maplespe/DWMBlurGlass

License: LGPL-3.0.

DWMBlurGlass modifies Windows title-bar/system materials and explicitly implements Acrylic-like processing.

Its relevance is **not** that we should hook DWM.

Its relevance is that it contains another concrete implementation of the familiar material stack:
- background;
- blur;
- contrast/exclusion treatment;
- saturation/tint;
- noise.

This reinforces a recurring lesson from Microsoft Acrylic, KWin blur, and community shaders:

> A convincing readable translucent material is rarely just "blur texture."

Useful reference topics:
- blur kernels;
- material noise;
- luminance/tint;
- how small amounts of noise prevent sterile/banded gradients;
- Windows composition edge cases.

Avoid DWM hooking/injection as a core architecture.

---

## 4. Reuse strategy matrix

| Project / system | Category | Best thing to steal | Dependency candidate? | Prototype host? |
|---|---|---|---|---|
| **libplacebo** | HDR/image rendering library | color/HDR/ICC/dither/GPU abstraction; HF/LF feature maps | **Yes, investigate** | Yes |
| **GlassCode** | JetBrains capture/overlay plugin | capture→classify→replace architecture; JetBrains sidecar pattern | Probably no | Baseline/reference |
| **Gamescope** | Wayland/Vulkan compositor | current scRGB/PQ Wayland implementation | No | Linux reference/test host |
| **Magpie** | Windows capture/postprocess | mature arbitrary-window capture + multipass D3D graph | Probably no | **Yes** |
| **OBS + shaderfilter** | capture/filter platform | color-tagged filter graph; arbitrary shader on captured source | No | **Yes** |
| **RenoDX** | DirectX HDR surgery | swapchain/resource upgrade; UI-vs-scene luminance | No | Reference |
| **ReShade HDR shaders** | HDR diagnostics | scRGB/PQ math, nit/debug visualizations | No | **Yes** |
| **Ghostty** | terminal renderer | direct terminal alpha + post-process chain | No | **Excellent** |
| **kitty** | terminal renderer | linear-RGB Slang shader graph + persistent textures | No | **Excellent** |
| **Windows Terminal** | terminal renderer | easy HLSL postprocess over real text | No | **Excellent** |
| **WezTerm** | terminal/background renderer | layered/parallax depth baseline | No | Baseline |
| **Zed/GPUI** | full GPU-native editor | actual glyph-aware renderer seam | Maybe fork/reference | Potential |
| **Wallpaper Setting** | VS Code patch | background-only transparency + per-region opacity | No | Baseline/reference |
| **vscode-background** | VS Code ecosystem | mature wallpaper integration/compatibility | No | Baseline |
| **SmartText** | image/text layout | saliency-aware text-safe regions | No | Offline analysis |
| **PosterLayout** | dataset/layout model | validation corpus for safe/unsafe image regions | No | Dataset |
| **smartcrop.js** | image crop heuristic | cheap interest map/crop optimization | Maybe tiny code reuse | Offline |
| **Android Palette** | adaptive color utility | minimum intervention to satisfy contrast | No | Baseline |
| **Material scrims** | UI design system | smooth local text-protection field | No | Baseline |
| **SmartColor / AR work** | perceptual UI research | conditional show-upon-contrast policy | No | Algorithm inspiration |
| **KWin / Wayfire blur** | compositor | damage expansion, multipass blur, noise/banding handling | No | Source reference |
| **DWMBlurGlass** | Windows material hack | Acrylic implementation details | No | Source reference |

---

## 5. Dependency versus source-reading classification

### Serious dependency candidate

#### libplacebo

This is the one project from the pass that may deserve becoming actual infrastructure.

Reasons:
- LGPL rather than GPL application copyleft;
- already abstracts D3D11/Vulkan/OpenGL;
- understands HDR/SDR/ICC/color spaces;
- exposes custom shader hooks;
- provides high-precision temporary textures;
- already solves gamut/tone mapping/dithering;
- actively maintained;
- contains a relevant high-/low-frequency contrast-recovery algorithm.

Before adopting, prototype:
1. load linear/HDR wallpaper;
2. attach custom shader hook at `PL_HOOK_LINEAR` or another appropriate stage;
3. pass external glyph-mask texture;
4. suppress detail;
5. render through D3D11 and Vulkan;
6. determine what presentation/platform glue remains.

If it works, this may save an enormous amount of undifferentiated rendering plumbing.

### Architecture/reference projects

Read deeply but probably do not depend on:
- Gamescope;
- OBS;
- GlassCode;
- RenoDX;
- KWin;
- Magpie.

These contain answers to concrete implementation questions.

### Experiment hosts

Install/use rather than embed:
- Ghostty;
- kitty;
- Windows Terminal;
- WezTerm;
- OBS + shaderfilter;
- Magpie;
- ReShade/Lilium tools.

### Baselines

Implement equivalents so the fancy method has to earn itself:
- static background opacity;
- black/white foreground switching;
- outline;
- drop shadow;
- subtitle box;
- Material scrim;
- GlassCode-like local-background classifier;
- global blur.

---

## 6. Licensing snapshot and caution

This pass is research, not a license audit.

Known SPDX-style licenses observed from repository metadata:

### MIT
- Ghostty;
- RenoDX;
- SmartText;
- smartcrop.js;
- Wallpaper Setting;
- vscode-background.

### LGPL
- libplacebo: LGPL-2.1-or-later;
- DWMBlurGlass: LGPL-3.0.

### GPL
- GlassCode: GPL-3.0;
- Magpie: GPL-3.0;
- ReShade HDR shaders: GPL-3.0;
- obs-shaderfilter: GPL-2.0.

### Verify before code reuse
- Gamescope;
- OBS Studio;
- KWin;
- Wayfire;
- PosterLayout dataset/code;
- community Ghostty shader repositories;
- individual shader snippets from forums/gists.

General rule:

> Learning an algorithm or architectural pattern is not the same thing as copying code.

If this project eventually acquires a license, review compatibility before importing any source.

---

## 7. Updated cheapest-to-most-serious prototype sequence

The third pass changes the likely order again.

### Phase A — offline reference

Build deterministic image + text-mask prototype.

Include baselines:
- Material scrim;
- Palette-style minimum foreground adjustment;
- GlassCode-like local background classifier;
- local luminance suppression;
- libplacebo-inspired low/high-frequency detail attenuation.

### Phase B — real text, no editor

#### Linux / cross-platform terminal
Start with **Ghostty** if alpha gives direct glyph/background separation.

Then **kitty** for:
- persistent temporal state;
- richer multipass shader experiments.

Use **WezTerm** as depth/parallax/static-filter baseline.

#### Windows
Use **Windows Terminal** HLSL.

Alternative:
- OBS capture + shaderfilter;
- MagpieFX.

### Phase C — HDR capability

Try Electron/WebGPU FP16 extended output.

Separately prototype **libplacebo**:
- D3D11;
- Vulkan;
- custom linear hook;
- HDR target.

### Phase D — real editor integration

Likely candidates:
1. JetBrains cooperative plugin + sidecar;
2. Zed/GPUI experimental branch;
3. Electron/Monaco standalone editor;
4. VS Code patch only if worth maintenance;
5. capture-based GlassCode-style compatibility fallback.

### Phase E — production presentation

Only after the algorithm proves useful:
- Windows scRGB/Advanced Color backend;
- KDE Wayland color-management backend;
- display characterization/calibration.

---

## 8. A surprisingly attractive hybrid architecture

The accumulated existing implementations suggest:

```text
JetBrains / editor plugin
    │
    ├── visible text/glyph geometry
    ├── viewport
    ├── cursor/selection
    └── semantic token info
              │
              ▼
       native sidecar
              │
       libplacebo GPU layer
       ├── wallpaper decode/color
       ├── linear FP16 working surface
       ├── custom adaptive hook
       ├── ICC/gamut/tone mapping
       └── dither/output prep
              │
       platform presentation
       ├── Windows scRGB
       └── Wayland scRGB
```

Fallback:

```text
no cooperative plugin
      ↓
window capture
      ↓
GlassCode-inspired shape inference
      ↓
same adaptive renderer
```

This is far more grounded now than the original "maybe write our own renderer or some shit."

---

## 9. New benchmark idea: implementation ancestry ladder

Rather than compare only algorithm variants, compare **historically existing solution classes**:

```text
0. raw wallpaper
1. editor global opacity/filter
2. subtitle outline/shadow
3. Material local scrim
4. GlassCode-style inferred foreground/background
5. simple glyph-mask local dim
6. glyph-mask detail-band suppression
7. perception-weighted adaptive filter
8. HDR calibrated version
```

This makes the research question concrete:

> At which rung does the improvement become large enough that additional complexity stops being silly?

If rung 5 already feels perfect, we happily never implement rung 7.

---

## 10. Useful philosophical convergence

Across unrelated systems we repeatedly found the same rules:

### Preserve foreground when possible
- Ghostty alpha composition;
- GlassCode foreground-shape preservation;
- background-only blur;
- Material text protection.

### Modify only enough to restore legibility
- Android Palette minimum-alpha calculation;
- SmartColor show-upon-contrast;
- system-bar contrast enforcement.

### Separate low-frequency scene from high-frequency detail
- libplacebo contrast recovery;
- local-Laplacian literature;
- blur/material systems.

### Keep explicit color metadata
- OBS;
- libplacebo;
- Gamescope;
- modern HDR APIs.

### Treat smoothing as spatially nonlocal for damage
- KWin;
- Wayfire.

### Expect banding after flattening gradients
- KWin noise;
- Acrylic noise;
- Ghostty community dither.

This convergence is valuable: the project is not inventing one giant bizarre idea from nothing.

It is combining several established techniques at a much finer, glyph-aware granularity.

## Key sources

- Ghostty: https://github.com/ghostty-org/ghostty
- Ghostty custom shaders: https://ghostty.org/docs/config/reference#custom-shader
- Ghostty community background-compositing shader: https://github.com/lexrus/lex-ghostty-shaders
- libplacebo: https://github.com/haasn/libplacebo
- GlassCode: https://github.com/gileli121/GlassCode
- Gamescope: https://github.com/ValveSoftware/gamescope
- Magpie: https://github.com/Blinue/Magpie
- OBS Studio: https://github.com/obsproject/obs-studio
- RenoDX: https://github.com/clshortfuse/renodx
- KWin: https://github.com/KDE/kwin
- DWMBlurGlass: https://github.com/Maplespe/DWMBlurGlass
