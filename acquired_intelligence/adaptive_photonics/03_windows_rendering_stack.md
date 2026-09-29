# Windows rendering stack

## Recommended Advanced Color representation

Microsoft recommends FP16 scRGB for general-purpose Advanced Color applications.

Core recipe:
- flip-model swapchain;
- `DXGI_FORMAT_R16G16B16A16_FLOAT`;
- scRGB / extended linear sRGB color space;
- let DWM/display pipeline convert to the monitor's native output representation.

Primary source:
https://learn.microsoft.com/en-us/windows/win32/direct3darticles/high-dynamic-range

Why this fits:
- floating-point;
- linear light;
- values above SDR reference white;
- natural for composition;
- avoids manually encoding every UI pixel as PQ.

## Reference white

Windows defines nominal scRGB/sRGB reference white as 80 nits in the Advanced Color model.

Conceptually:
- 0.0 = black;
- 1.0 linear white = 80 nit reference white;
- >1.0 can represent brighter values.

But Windows exposes a user-adjustable SDR white level in HDR mode. If mixing SDR assets with HDR/scRGB output, query and respect it.

Useful docs:
- https://learn.microsoft.com/en-us/windows/win32/api/wingdi/ns-wingdi-displayconfig_sdr_white_level
- https://learn.microsoft.com/en-us/uwp/api/windows.graphics.display.advancedcolorinfo.sdrwhitelevelinnits
- https://learn.microsoft.com/en-us/windows/win32/direct2d/white-level-adjustment-effect

Do not hard-code "1.0 always visually equals 80 nits in the user's desktop setup" without understanding DWM/reference-white handling.

## Suggested Windows renderer

```text
image decoder
  ↓
color transform to linear working space
  ↓
background analysis compute shaders
  ↓
glyph masks / protection field
  ↓
adaptive background transform
  ↓
text composite
  ↓
FP16 scRGB render target
  ↓
DXGI flip-model swapchain
  ↓
DWM Advanced Color
  ↓
display
```

Candidate APIs:
- D3D11 or D3D12;
- Direct2D where convenient;
- DirectWrite for shaping/layout/rasterization;
- DXGI for swapchain/output capability;
- optionally DirectComposition for window-composition-heavy designs.

D3D11 is likely sufficient for an MVP. D3D12 is not automatically better for a 2D compositor.

## DirectWrite

DirectWrite supports:
- text layout;
- shaping/fallback through Windows stack;
- subpixel positioning;
- grayscale or ClearType rendering modes;
- custom text renderers;
- glyph-run callbacks.

Sources:
- https://learn.microsoft.com/en-us/windows/win32/directwrite/introducing-directwrite
- https://learn.microsoft.com/en-us/windows/win32/directwrite/rendering-directwrite
- https://learn.microsoft.com/en-us/windows/win32/direct2d/direct2d-and-directwrite

Crucial need: obtain/use glyph coverage before final scene composition.

A custom renderer can convert glyph runs into masks/geometry that the adaptive pipeline owns.

## ClearType warning

Classic ClearType assumes suitable stripe geometry.

On a nonstandard OLED:
- prefer grayscale AA first;
- evaluate ClearType only if panel layout is known compatible;
- a 2026 RGB-stripe OLED may make ordinary subpixel AA viable again.

At 27" 4K, grayscale AA is a serious default candidate.

## Vulkan on Windows

A cross-platform Vulkan renderer is plausible:
- same analysis/composition shaders;
- Windows surface/swapchain backend;
- `VK_EXT_swapchain_colorspace`;
- HDR metadata for HDR10 path.

However:
- scRGB integration is native/convenient in DXGI/DWM;
- DirectWrite integration is easier in a DirectX-centered backend;
- Vulkan's value rises if sharing a renderer with Linux matters more than native integration.

Do not force one graphics API merely for ideological portability.

## Qt RHI tangent

Qt's `QRhiSwapChain` exposes HDR swapchain formats including extended linear sRGB/scRGB and HDR10:
https://doc.qt.io/qt-6/qrhiswapchain.html

Potential upside:
- cross-platform windowing;
- backend abstraction;
- less raw DXGI/Vulkan boilerplate.

Potential downside:
- exact Wayland color-management behavior needs verification;
- experimental renderer may eventually require lower-level control.

Worth a prototype, not an assumed final architecture.

## Windows Terminal as an extremely cheap algorithm testbed

Windows Terminal has experimental HLSL pixel shaders:
- `experimental.pixelShaderPath`;
- `experimental.pixelShaderImagePath`;
- terminal contents exposed as a texture;
- image exposed as another texture.

Docs/sample:
- https://learn.microsoft.com/en-us/windows/terminal/customize-settings/profile-appearance
- https://github.com/microsoft/terminal/blob/main/samples/PixelShaders/README.md
- https://github.com/microsoft/terminal/blob/main/samples/PixelShaders/BackgroundImage.hlsl

This is close to tailor-made for an early proof:
- infer terminal foreground from terminal texture;
- derive local text neighborhood;
- dim/desaturate/smooth wallpaper near text;
- composite.

Limitations:
- not necessarily HDR/FP16;
- terminal texture semantics may not expose clean semantic glyph coverage;
- shader API is experimental.

Still very useful because it can validate the visual algorithm before building a text/windowing stack.

## Editor integration possibilities

### Standalone renderer/editor prototype
Best control, worst editor functionality.

### Windows Terminal
Best quick visual proof for monospaced text.

### VS Code extension
Public decoration APIs can alter ranges/backgrounds but do not naturally expose a final per-pixel compositor.
https://code.visualstudio.com/api/references/vscode-api

### JetBrains plugin
Potentially richer editor painting hooks; requires dedicated API research.

### Cooperative sidecar
An editor plugin could publish glyph/protection masks and viewport transforms to a separate GPU compositor.

### Fork/patch editor
Maximum control, maximum maintenance. Avoid until the algorithm is proven.

## HDR metadata versus scRGB

For scRGB FP16 through Windows compositor:
- not the same workflow as manually emitting HDR10 PQ frames;
- compositor can perform display mapping;
- UI math remains simple linear-light composition.

HDR10 swapchain:
- app deals directly with Rec.2020/PQ semantics;
- HDR metadata becomes more relevant;
- more natural for video/game content than a mixed UI compositor.

For this application: **scRGB first**.

## Windows experiments

1. Create FP16 scRGB window and verify values >1.0 exceed reference white.
2. Query SDR-white level and verify mapping.
3. Render grayscale-AA tiny code at 27" 4K and compare DirectWrite modes.
4. Render restrained luminance patches and establish comfortable dark-room targets.
5. Observe whether DWM/display tone mapping changes with APL.
6. Observe ASBL while content is mostly static but caret/text changes.
