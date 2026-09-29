# Research source map

Snapshot gathered 2026-09-29. Primary sources are preferred where available. Secondary display-review sources remain useful because panel behavior/subpixel layout is often measured better than vendor marketing describes it.

## Windows HDR / Advanced Color

- Microsoft — DirectX with Advanced Color  
  https://learn.microsoft.com/en-us/windows/win32/direct3darticles/high-dynamic-range  
  FP16 scRGB recommendation, flip model, reference white, SDR/HDR mixing.

- Microsoft — DISPLAYCONFIG_SDR_WHITE_LEVEL  
  https://learn.microsoft.com/en-us/windows/win32/api/wingdi/ns-wingdi-displayconfig_sdr_white_level

- Microsoft — AdvancedColorInfo.SdrWhiteLevelInNits  
  https://learn.microsoft.com/en-us/uwp/api/windows.graphics.display.advancedcolorinfo.sdrwhitelevelinnits

- Microsoft — Direct2D white-level adjustment  
  https://learn.microsoft.com/en-us/windows/win32/direct2d/white-level-adjustment-effect

## Windows text

- Microsoft — Introducing DirectWrite  
  https://learn.microsoft.com/en-us/windows/win32/directwrite/introducing-directwrite

- Microsoft — Rendering DirectWrite  
  https://learn.microsoft.com/en-us/windows/win32/directwrite/rendering-directwrite

- Microsoft — Direct2D and DirectWrite  
  https://learn.microsoft.com/en-us/windows/win32/direct2d/direct2d-and-directwrite

- Microsoft — ClearType antialiasing  
  https://learn.microsoft.com/en-us/windows/win32/gdi/cleartype-antialiasing

## Windows Terminal prototype surface

- Microsoft — Terminal appearance / pixel shader  
  https://learn.microsoft.com/en-us/windows/terminal/customize-settings/profile-appearance

- Microsoft Terminal — pixel shader samples  
  https://github.com/microsoft/terminal/blob/main/samples/PixelShaders/README.md

- Microsoft Terminal — background-image HLSL sample  
  https://github.com/microsoft/terminal/blob/main/samples/PixelShaders/BackgroundImage.hlsl

## Wayland / Linux color management

- Wayland Explorer — color-management-v1  
  https://wayland.app/protocols/color-management-v1  
  Image descriptions, parametric color metadata, MaxCLL/MaxFALL, Windows-scRGB stimulus encoding.

- Linux kernel — per-plane color pipeline API  
  https://docs.kernel.org/gpu/rfc/color_pipeline.html

## Vulkan

- Khronos — VK_EXT_swapchain_colorspace  
  https://docs.vulkan.org/refpages/latest/refpages/source/VK_EXT_swapchain_colorspace.html

- Khronos — VK_EXT_hdr_metadata  
  https://docs.vulkan.org/refpages/latest/refpages/source/VK_EXT_hdr_metadata.html

- Khronos — WSI chapter  
  https://docs.vulkan.org/spec/latest/chapters/VK_KHR_surface/wsi.html

## KDE / KWin

- KDE MegaRelease 6  
  https://kde.org/announcements/megarelease/6/

- Plasma 6.2  
  https://kde.org/announcements/plasma/6/6.2.0/

- Plasma 6.4 development changelog  
  https://kde.org/announcements/changelogs/plasma/6/6.3.5-6.3.90/

- KDE May 2026 — ICC profiles with HDR  
  https://blogs.kde.org/2026/05/09/this-week-in-plasma-icc-profiles-%EF%B8%8F-hdr/

## NVIDIA Linux

- NVIDIA Linux 595.104.02, 2026-09-22  
  https://www.nvidia.com/en-us/drivers/details/279961/  
  Includes Wayland color-management-v1 / VkHdrMetadataEXT-related fix.

- NVIDIA Wayland known issues  
  https://download.nvidia.com/XFree86/Linux-aarch64/610.43.03/README/wayland-issues.html  
  Linux 6.19 per-plane DRM color pipeline and known compositor interaction caveats.

## HDR standards

- ITU-R BT.2100  
  https://www.itu.int/rec/R-REC-BT.2100

- VESA DisplayHDR performance criteria  
  https://displayhdr.org/performance-criteria/

## Text shaping / rasterization

- HarfBuzz manual  
  https://harfbuzz.github.io/

- HarfBuzz shaping  
  https://harfbuzz.github.io/harfbuzz-hb-shape.html

- HarfBuzz shaping plans / clusters  
  https://harfbuzz.github.io/shaping-and-shape-plans.html

- FreeType LCD/subpixel rendering  
  https://freetype.org/freetype2/docs/reference/ft2-lcd_rendering.html

- FreeType text rendering / hinting / gamma  
  https://freetype.org/freetype2/docs/hinting/text-rendering-general.html

- FreeType subpixel hinting  
  https://freetype.org/freetype2/docs/hinting/subpixel-hinting.html

- msdfgen  
  https://github.com/Chlumsky/msdfgen

- msdf-atlas-gen  
  https://github.com/Chlumsky/msdf-atlas-gen

## Image filtering / adaptive background techniques

- He, Sun, Tang — Guided Image Filtering  
  https://pubmed.ncbi.nlm.nih.gov/23599054/

- Paris et al. — bilateral filtering overview  
  https://doi.org/10.1145/1401132.1401134

## Contrast / readability / perception

- W3C WCAG contrast explanation  
  https://www.w3.org/WAI/WCAG21/Understanding/contrast-minimum

- Effects of ambient illumination, polarity, letter size  
  https://pubmed.ncbi.nlm.nih.gov/28166901/

- Smaller pupil size / proofreading with positive polarity  
  https://pubmed.ncbi.nlm.nih.gov/25135324/

- Display luminance and polarity  
  https://pubmed.ncbi.nlm.nih.gov/19562598/

- Positive polarity advantage for small characters  
  https://pubmed.ncbi.nlm.nih.gov/25141597/

- Pupil size and fine-detail discrimination  
  https://pubmed.ncbi.nlm.nih.gov/31875153/

- Brightness contrast under negative polarity  
  https://pubmed.ncbi.nlm.nih.gov/34856871/

Do not overgeneralize these studies into "dark mode bad." They show that absolute luminance, pupil size, character size, and polarity interact.

## Color spaces

- W3C CSS Color 4 — Oklab/OKLCH  
  https://www.w3.org/TR/css-color-4/

- Qt QColorSpace  
  https://doc.qt.io/qt-6/qcolorspace.html

- Qt QRhiSwapChain HDR formats  
  https://doc.qt.io/qt-6/qrhiswapchain.html

## OLED / text / panel behavior — secondary sources

- RTINGS text clarity methodology  
  https://www.rtings.com/monitor/tests/picture-quality/text-clarity

- RTINGS WOLED vs QD-OLED  
  https://www.rtings.com/monitor/learn/woled-vs-qd-oled

- RTINGS IPS vs OLED  
  https://www.rtings.com/monitor/learn/ips-vs-oled

- RTINGS OLED burn-in discussion  
  https://www.rtings.com/tv/learn/oled-burn-in-not-improved-as-expected

- RTINGS image retention methodology  
  https://www.rtings.com/monitor/tests/picture-quality/image-retention

- RTINGS peak brightness methodology  
  https://www.rtings.com/monitor/tests/picture-quality/peak-brightness

## 2026 RGB-stripe OLED

- TFTCentral — RGB-stripe OLED panels  
  https://tftcentral.co.uk/articles/oled-rgb-stripe-panels-explained-should-you-wait

- WIRED — 27" 4K RGB-stripe OLED review  
  https://www.wired.com/review/asus-rog-swift-rgb-stripe-oled-pg27ucwm/

Product availability/specs are volatile and must be rechecked before purchase.

## VS Code integration tangent

- VS Code extension API  
  https://code.visualstudio.com/api/references/vscode-api

Public decoration controls are useful but do not obviously expose the full final-pixel compositor required by the concept. Dedicated integration research remains future work.


# Second shotgun pass sources

## Human visual system / perceptual models

- castleCSF — open contrast-sensitivity model and dataset  
  https://github.com/gfxdisp/castleCSF  
  Spatial frequency, temporal frequency, luminance, eccentricity, area, chromaticity, chromatic modulation, stimulus shape.

- Graphics & Displays group, University of Cambridge  
  https://github.com/gfxdisp  
  Related HDR/perceptual tooling and datasets.

- Blur and contrast as pictorial depth cues  
  https://pubmed.ncbi.nlm.nih.gov/9488884/

- Contrast as a depth cue  
  https://pubmed.ncbi.nlm.nih.gov/7941367/

- Blur and the perception of depth at occlusions  
  https://pubmed.ncbi.nlm.nih.gov/27115522/

- Occlusion edge blur as a relative-depth cue  
  https://pubmed.ncbi.nlm.nih.gov/8867752/

- Stereoscopy / pictorial depth cue overview  
  https://pmc.ncbi.nlm.nih.gov/articles/PMC3490636/

## Edge-aware and multi-scale filtering

- Local Laplacian Filters explanatory chapter  
  https://people.csail.mit.edu/fredo/comp-photo-book/05-edges-matter-05-local-laplacian-filters.html

- Paris, Hasinoff, Kautz — Local Laplacian Filters paper  
  https://people.csail.mit.edu/hasinoff/pubs/ParisEtAl11-lapfilters.pdf

- Guided Image Filtering  
  https://pubmed.ncbi.nlm.nih.gov/23599054/

- Bilateral filtering overview  
  https://doi.org/10.1145/1401132.1401134

## Chromium / Electron / WebGPU / web HDR

- Chromium gfx::ColorSpace  
  https://chromium.googlesource.com/chromium/src/+/main/ui/gfx/color_space.h  
  Extended sRGB, scRGB linear, scRGB 80-nit convention, HDR10, HLG.

- Chrome WebGPU 129 — HDR canvas extended tone mapping  
  https://developer.chrome.com/blog/new-in-webgpu-129

- Chrome WebGPU 131 — inspect configured tone-mapping mode  
  https://developer.chrome.com/blog/new-in-webgpu-131

- CSS Color HDR Level 1, July 2026 Working Draft  
  https://www.w3.org/TR/2026/WD-css-color-hdr-1-20260728/

- Electron 44  
  https://www.electronjs.org/blog/electron-44-0  
  Chromium 152-era Electron baseline.

- Electron release schedule  
  https://releases.electronjs.org/schedule

## Terminal / editor rendering laboratories

- kitty custom shaders  
  https://sw.kovidgoyal.net/kitty/custom-shaders/  
  Added in kitty 0.49.0; linear-RGB end-of-pipeline shaders, chained groups, intermediate/persistent textures.

- kitty 0.49 changelog  
  https://sw.kovidgoyal.net/kitty/changelog/

- kitty graphics protocol  
  https://sw.kovidgoyal.net/kitty/graphics-protocol/

- WezTerm background image  
  https://wezterm.org/config/lua/config/window_background_image.html

- WezTerm background HSB transform  
  https://wezterm.org/config/lua/config/window_background_image_hsb.html

- WezTerm layered/parallax background system  
  https://wezterm.org/config/lua/config/background.html

- Zed / GPUI GPU-rendering architecture  
  https://zed.dev/blog/videogame

## Windows capture / display calibration

- Windows Graphics Capture  
  https://learn.microsoft.com/en-us/windows/uwp/audio-video-camera/screen-capture  
  Important HDR note: use R16G16B16A16_FLOAT throughout capture pipeline to avoid HDR clipping/washout.

- Windows AdvancedColorInfo  
  https://learn.microsoft.com/en-us/uwp/api/windows.graphics.display.advancedcolorinfo  
  Peak/full-frame/min luminance, SDR white, primaries, white point, dynamic state.

- Windows MHC2 hardware display calibration pipeline  
  https://learn.microsoft.com/en-us/windows/win32/wcs/display-calibration-mhc

- Windows Advanced Color architecture  
  https://learn.microsoft.com/en-us/windows/win32/direct3darticles/high-dynamic-range

- LittleCMS  
  https://littlecms.com/color-engine/

## Wayland details revisited

- Wayland color-management-v1  
  https://wayland.app/protocols/color-management-v1  
  Important nuance: Windows-scRGB stimulus maps 1.0 to 80 cd/m², but the protocol calls reference white unknown/variable and uses 203 cd/m² when compositor processing must assume one.

- Vulkan WSI  
  https://docs.vulkan.org/spec/latest/chapters/VK_KHR_surface/wsi.html  
  Relevant to Wayland pass-through color space + explicit color-management surface ownership.

## Low-luminance OLED / signal transport

- TFTCentral — OLED black crush and shadow detail  
  https://tftcentral.co.uk/articles/does-oled-have-a-black-crush-problem-understanding-and-testing-oled-shadow-detail

- RTINGS — OLED low-refresh gamma shift  
  https://www.rtings.com/monitor/learn/gamma-shift-investigation

- RTINGS — VRR flicker research  
  https://www.rtings.com/monitor/learn/research/vrr-flicker

- RTINGS — chroma subsampling and PC text  
  https://www.rtings.com/tv/learn/chroma-subsampling

- TFTCentral — 2026 RGB-stripe OLED development  
  https://tftcentral.co.uk/articles/oled-rgb-stripe-panels-explained-should-you-wait

## Notes about source quality

- Platform/API claims should prefer Microsoft, Khronos, Wayland protocol XML/docs, Linux kernel docs, KDE/NVIDIA first-party sources, or source code.
- Display behavior (black crush, text clarity, flicker, subpixel geometry) often requires instrumented secondary reviewers such as RTINGS/TFTCentral because vendors rarely publish the ugly details.
- Psychology/vision conclusions should be treated as evidence about variables and mechanisms, not as universal ergonomic prescriptions.
