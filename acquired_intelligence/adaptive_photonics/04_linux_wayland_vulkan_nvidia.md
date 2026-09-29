# Linux / Wayland / Vulkan / NVIDIA

Snapshot date: 2026-09-29. Recheck fast-moving details before coding.

## Target desktop

Intended Linux environment:

**KDE Plasma + Wayland + NVIDIA**

X11 is not the architectural target for HDR/color-managed experimentation.

## Wayland color-management-v1

Protocol:
https://wayland.app/protocols/color-management-v1

The protocol lets clients describe how surface pixel values should be interpreted. Relevant capabilities include:
- primaries;
- transfer functions;
- luminance ranges;
- mastering metadata;
- MaxCLL;
- MaxFALL;
- predefined image descriptions.

Most interestingly, it includes:

`create_windows_scrgb`

which creates a predefined image description for Windows-scRGB stimulus encoding.

This is useful convergence: a linear extended-sRGB working/output model can plausibly exist on both Windows and Wayland.

### Stability warning

The protocol is still a fast-moving area of the ecosystem. Treat it as a backend detail, not a core domain model.

## Vulkan surface/color-space support

### VK_EXT_swapchain_colorspace

Adds color-space enums beyond ordinary sRGB, including:
- `VK_COLOR_SPACE_EXTENDED_SRGB_LINEAR_EXT`;
- `VK_COLOR_SPACE_HDR10_ST2084_EXT`;
- `VK_COLOR_SPACE_HDR10_HLG_EXT`;
- BT.2020 linear;
- Display-P3 variants;
- pass-through.

Docs:
https://docs.vulkan.org/refpages/latest/refpages/source/VK_EXT_swapchain_colorspace.html

A notable Wayland-specific capability is pass-through when explicit Wayland color management owns interpretation.

### VK_EXT_hdr_metadata

Associates SMPTE ST 2086 and CTA-861 HDR metadata with swapchains.

Docs:
https://docs.vulkan.org/refpages/latest/refpages/source/VK_EXT_hdr_metadata.html

For an scRGB/linear UI compositor, HDR10 metadata may not be the primary mechanism, but it remains important background.

## KDE / KWin state

Useful milestones:
- Plasma 6: initial HDR on Wayland.
- Plasma 6.2: broader Wayland color management, HDR brightness handling, KWin tone mapping.
- Plasma 6.4-era work: switch toward the upstream Wayland color-management protocol.
- Plasma 6.7 development: ICC profiles usable while HDR is active.

Sources:
- https://kde.org/announcements/megarelease/6/
- https://kde.org/announcements/plasma/6/6.2.0/
- https://kde.org/announcements/changelogs/plasma/6/6.3.5-6.3.90/
- https://blogs.kde.org/2026/05/09/this-week-in-plasma-icc-profiles-%EF%B8%8F-hdr/

Target the upstream protocol, not old compositor-private color protocols, unless a temporary compatibility adapter is unavoidable.

## Linux DRM color pipeline

Kernel docs:
https://docs.kernel.org/gpu/rfc/color_pipeline.html

The per-plane color-pipeline API models hardware color operations as discoverable pipeline blocks so compositors can offload transforms instead of always doing them in shaders.

This is mostly a compositor/kernel concern, not something the application should directly depend upon.

The application architecture should normally stop at Wayland/Vulkan and let KWin own DRM/KMS.

## NVIDIA state in late September 2026

Current production driver on the research date:
**595.104.02**, released 2026-09-22.

NVIDIA release notes mention fixing invalid `VkHdrMetadataEXT` values being forwarded into Wayland `color-management-v1`, evidence that the current stack participates in this exact pipeline.

Source:
https://www.nvidia.com/en-us/drivers/details/279961/

NVIDIA's Wayland known-issues docs state that on Linux 6.19+ `nvidia-drm` supports the upstream per-plane DRM color pipeline for color management/HDR.

Source:
https://download.nvidia.com/XFree86/Linux-aarch64/610.43.03/README/wayland-issues.html

### Caveat

NVIDIA warns that some compositors may mishandle non-bypassable color operations and can produce blank output with system HDR; a `color_pipeline=0` workaround exists.

This is exactly why platform details belong behind an abstraction.

## Recommended Linux layering

```text
shared perception + composition shaders
          ↓
       Vulkan
          ↓
Wayland WSI / explicit color description
          ↓
wp_color_management_surface_v1
          ↓
         KWin
          ↓
 DRM/KMS color pipeline where useful
          ↓
      NVIDIA driver
          ↓
         OLED
```

Do not attempt to own KMS in ordinary desktop mode.

## scRGB-like path on Wayland

Ideal path to investigate:
1. FP16 swapchain/buffer.
2. linear extended-sRGB values.
3. Wayland `create_windows_scrgb` image description.
4. attach description to the surface.
5. compositor maps surface to display output.

Critical unknowns to test on actual KWin/NVIDIA:
- which Vulkan format/color-space combinations expose FP16 cleanly;
- whether Vulkan WSI color management or explicit Wayland protocol should own the description;
- whether KWin preserves out-of-SDR-range values;
- whether transforms/tone mapping introduce clipping;
- whether direct scanout changes behavior;
- how mixed SDR/HDR surfaces are handled;
- whether ICC+HDR behavior is stable on the exact Plasma release.

Do not infer these solely from protocol existence.

## Why Vulkan is attractive

The adaptive part is naturally GPU work:
- local luminance maps;
- blur pyramids;
- gradients;
- guided/bilateral-like filters;
- mask dilation;
- temporal accumulation;
- final linear-light composition.

However, "Vulkan because Linux" should not become needless complexity. A Qt RHI or OpenGL proof can answer visual-algorithm questions first.

## Qt as a bridge

Qt exposes HDR-capable `QRhiSwapChain` formats including extended linear sRGB/scRGB:
https://doc.qt.io/qt-6/qrhiswapchain.html

QColorSpace supports modern transfer/color-space descriptions:
https://doc.qt.io/qt-6/qcolorspace.html

Potential architecture:
- Qt window/input;
- QRhi for cross-platform render abstraction;
- custom shaders;
- drop to native Wayland/DXGI only where QRhi lacks necessary control.

Needs validation on Plasma/NVIDIA before commitment.

## KWin-effect tangent

A compositor-level effect sounds attractive because it could alter any editor without patching it.

Problem: KWin does not inherently know which pixels are glyphs, comments, cursor, etc. Pure post-processing must infer text from already-composited pixels.

More plausible advanced architecture:
- editor/plugin exports a glyph/protection mask surface;
- KWin effect or companion compositor receives editor surface + mask;
- compositor modifies only background regions behind text.

High-complexity. Do not precede standalone proof.

## Linux text path

Natural native stack:
- HarfBuzz for shaping;
- FreeType for glyph loading/rasterization;
- Fontconfig for discovery/fallback;
- GPU upload/caching for coverage masks.

This also makes FreeType Harmony subpixel geometry experimentally possible.

If using Qt, avoid duplicating its text stack unless custom coverage control demands it.

## No Linux gaming requirement

Do not let Gamescope/Proton hijack scope.

They are useful examples because they exercise HDR/Vulkan/Wayland. They are not requirements. Windows exists specifically to keep gaming boring.

## Diagnostic checklist

Before blaming the algorithm:
1. confirm Wayland session;
2. log Vulkan surface format + color space;
3. log advertised Wayland color-management features;
4. log image-description success/failure;
5. confirm KWin HDR setting and output capability;
6. confirm NVIDIA driver + kernel;
7. check DRM color-pipeline status;
8. compare SDR-range test pattern;
9. compare >1.0 extended-range test pattern;
10. test with/without ICC profile;
11. inspect direct-scanout behavior;
12. compare against known-good HDR content/app;
13. only then debug adaptive-compositor math.


## Second-pass Windows-scRGB semantics correction

The predefined Wayland `create_windows_scrgb` description is more nuanced than a simple "linear FP16 where 1.0 is reference white."

The protocol states:
- channel 0.0 maps to 0 cd/m²;
- channel 1.0 maps to 80 cd/m² in the Windows-scRGB stimulus encoding;
- extended values and negative values are valid when the pixel format can represent them;
- the **reference white level is unknown/variable**;
- if compositor processing needs an assumed reference white, use 2.5375 (= 203 cd/m²) following BT.2408 guidance;
- EGL scRGB-linear differs because it defines 1.0 as reference white.

This distinction belongs entirely inside the Wayland/presentation backend.

Source:
https://wayland.app/protocols/color-management-v1

## Vulkan pass-through interaction

On Wayland, `VK_COLOR_SPACE_PASS_THROUGH_EXT` is relevant when the application intends to manage the Wayland surface's image description explicitly through `wp_color_management_surface_v1` rather than have Vulkan WSI own color management.

This can avoid creating two competing color-management objects for the same surface.

Source:
https://docs.vulkan.org/spec/latest/chapters/VK_KHR_surface/wsi.html

Experiment both paths rather than assuming which KWin/NVIDIA combination behaves best:
1. Vulkan WSI extended-sRGB color space;
2. pass-through WSI + explicit Wayland image description.
