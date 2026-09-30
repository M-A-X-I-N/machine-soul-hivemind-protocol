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


## Miscellaneous implementation sources

- OpenType optical-size axis (`opsz`)  
  https://learn.microsoft.com/en-us/typography/opentype/spec/dvaraxistag_opsz  
  Size-specific font design; explicitly discusses physical size and viewing-distance considerations.

- Skia — The Raster Tragedy / gamma handling for text  
  https://docs.skia.org/docs/dev/design/raster_tragedy/

- Slang shader compiler/language  
  https://docs.shader-slang.org/  
  Cross-target shader source including DXIL, SPIR-V, WGSL, Metal, GLSL, etc.

- Slang target/compiler reference  
  https://docs.shader-slang.org/en/stable/external/slang/docs/command-line-slangc-reference.html

- OpenEXR  
  https://openexr.com/en/latest/  
  Floating-point HDR/scene-linear image storage useful for deterministic debug captures.

- OpenEXR scene-linear representation  
  https://openexr.com/en/latest/SceneLinear.html

- PIX GPU captures  
  https://devblogs.microsoft.com/pix/gpu-captures/  
  Pipeline/resource inspection, pixel history, shader debugging.


# Third shotgun pass — existing implementations and prior art

## Direct editor / wallpaper ancestors

- GlassCode — JetBrains capture/process/overlay plugin  
  https://github.com/gileli121/GlassCode  
  Windows Graphics Capture, D3D11/CUDA processing, local shape/background inference, separate text brightness/background opacity, layered replacement windows.

- Wallpaper Setting — VS Code background-only transparency / filtering  
  https://github.com/Angelmaneuver/wallpaper-setting

- vscode-background — mature VS Code wallpaper injection ecosystem  
  https://github.com/shalldie/vscode-background

- IntelliJ Platform UI theme background images  
  https://plugins.jetbrains.com/docs/intellij/themes-intro.html  
  JetBrains already has platform-level background-image/theme support; exact theme/background APIs should be rechecked against the current SDK when implementing.

- DWMBlurGlass — Windows Acrylic/material implementation reference  
  https://github.com/Maplespe/DWMBlurGlass

## Text-over-image / safe-region systems

- SmartText — Harmonious Textual Layout Generation over Natural Images  
  https://github.com/intchous/SmartText

- PosterLayout CVPR 2023 — content-aware visual-textual presentation layout benchmark  
  https://github.com/PKU-ICST-MIPL/PosterLayout-CVPR2023

- smartcrop.js — cheap saliency/edge/skin/saturation crop heuristic  
  https://github.com/jwagner/smartcrop.js

## Existing adaptive foreground/readability patterns

- AndroidX Palette source — minimum-alpha text colors over image swatches  
  https://android.googlesource.com/platform/frameworks/support/+/refs/heads/androidx-main/palette/palette/src/main/java/androidx/palette/graphics/Palette.java

- 2024 AR text-readability literature review  
  https://link.springer.com/article/10.1007/s10055-024-00949-6

- Edward Swan publication archive / AR text-display studies  
  https://ed-swan.github.io/publications/

- SmartColor — real-time color/contrast adaptation for optical see-through displays  
  https://hci.cs.umanitoba.ca/Publications/details/smartcolor-real-time-color-correction-and-contrast-for-optical-see-through

- Material Design imagery — text-protection scrims  
  https://m1.material.io/style/imagery.html

- Android edge-to-edge / system-bar protection  
  https://developer.android.com/develop/ui/compose/system/system-bars

- Adaptive subtitle color-management patent, US 12,549,822  
  https://patents.justia.com/patent/12549822

- mpv/libass subtitle styles and background boxes  
  https://mpv.io/manual/master/

## Translucent material / backdrop-filter systems

- Microsoft Acrylic  
  https://learn.microsoft.com/en-us/windows/apps/design/style/acrylic  
  Blur + contrast/exclusion + tint + noise material pipeline.

- Apple NSVisualEffectView / vibrancy  
  https://developer.apple.com/documentation/appkit/nsvisualeffectview

- GNOME Shell BlurEffect  
  https://gnome.pages.gitlab.gnome.org/gnome-shell/shell/class.BlurEffect.html

- KWin blur implementation  
  https://github.com/KDE/kwin/blob/master/src/plugins/blur/blur.cpp  
  Dual-Kawase-style blur, saturation/contrast transforms, damage handling, noise to mask banding.

- Wayfire blur plugin  
  https://github.com/WayfireWM/wayfire/blob/master/plugins/blur/blur.cpp

- picom backdrop blur methods  
  https://github.com/yshui/picom

## HDR / color / GPU infrastructure worth mining

- libplacebo  
  https://github.com/haasn/libplacebo  
  HDR/color/ICC/gamut/tone/dither/GPU abstraction with custom shader hooks.

- libplacebo custom shader hooks  
  https://github.com/haasn/libplacebo/blob/master/src/include/libplacebo/shaders/custom.h

- libplacebo renderer / contrast recovery  
  https://github.com/haasn/libplacebo/blob/master/src/renderer.c

- libplacebo color shader feature extraction  
  https://github.com/haasn/libplacebo/blob/master/src/shaders/colorspace.c  
  Perceptual intensity feature map + low/high-frequency detail used for HDR contrast recovery; especially relevant as an inverse cousin of glyph-local detail suppression.

- Gamescope  
  https://github.com/ValveSoftware/gamescope  
  Current Vulkan/DRM/Wayland HDR implementation and concrete upstream color-management-v1 / Windows-scRGB usage.

- VK_hdr_layer  
  https://github.com/Zamundaaa/VK_hdr_layer  
  Small historical Vulkan↔Wayland HDR bridge; educational reference, not a recommended modern dependency.

- Magpie  
  https://github.com/Blinue/Magpie  
  Windows capture plus multipass GPU processing.

- MagpieFX format  
  https://github.com/Blinue/Magpie/blob/dev/docs/MagpieFX.md  
  D3D11 compute-shader graph, intermediate textures, FP16 formats, user parameters.

- OBS Studio  
  https://github.com/obsproject/obs-studio  
  Cross-platform color-space-aware capture/filter/render graph including scRGB/16F paths.

- obs-shaderfilter  
  https://github.com/exeldro/obs-shaderfilter  
  Arbitrary shader experiments on OBS sources, including extra texture inputs/masking.

- RenoDX  
  https://github.com/clshortfuse/renodx  
  ReShade-based DirectX shader/resource/swapchain surgery; strong reference for upgrading 8-bit pipelines to FP16/HDR and separating scene from UI brightness.

- ReShade HDR shaders / Lilium  
  https://github.com/EndlesslyFlowering/ReShade_HDR_shaders  
  scRGB/HDR10 analysis, tone mapping, nit/debug visualizations.

## Terminal shader laboratories

- Ghostty  
  https://github.com/ghostty-org/ghostty

- Ghostty custom shader configuration  
  https://ghostty.org/docs/config/reference#custom-shader  
  Post-process GLSL with the rendered terminal in iChannel0; shader chaining.

- lex-ghostty-shaders  
  https://github.com/lexrus/lex-ghostty-shaders  
  Community examples; `neuro_noise.glsl` explicitly composites generated imagery behind a premultiplied terminal foreground using terminal alpha so glyphs remain untouched.

- kitty custom shaders  
  https://sw.kovidgoyal.net/kitty/custom-shaders/

- Windows Terminal pixel shaders  
  https://github.com/microsoft/terminal/tree/main/samples/PixelShaders

- WezTerm layered backgrounds  
  https://wezterm.org/config/lua/config/background.html

## License caution

Repository licenses differ substantially (MIT, LGPL, GPL, and unclassified/asset-specific cases). The source map records projects for research. Before importing implementation code rather than merely learning from it, perform a fresh license/dependency review of the exact version/file being reused.


# Monitor purchase research — Swedish market snapshot 2026-09-30

Prices below are volatile. Prisjakt is used for Swedish price discovery/history; primary manufacturer/reviewer sources are used for actual engineering specifications.

## Swedish price discovery

- Dell Alienware AW2725Q  
  https://www.prisjakt.nu/produkt.php?p=14642119

- Lenovo Legion Pro 27UD-10  
  https://www.prisjakt.nu/produkt.php?p=15421779

- AOC AGON PRO AG276UZD  
  https://www.prisjakt.nu/produkt.php?p=14829774

- MSI MAG 272UP X24  
  https://www.prisjakt.nu/produkt.php?p=15261414

- Philips Evnia 32M2N8900  
  https://www.prisjakt.nu/produkt.php?p=14567413

- Gigabyte MO32U2  
  https://www.prisjakt.nu/produkt.php?p=16632529

- MSI MPG 321URX  
  https://www.prisjakt.nu/produkt.php?p=13326290

- ASUS XG32UCWMGZ campaign SKU  
  https://www.prisjakt.nu/produkt.php?p=17123345

- General Prisjakt searches were also used for LG 32GS94UX, ASRock PGO32UFS, ASUS XG32UCWG, Samsung G8 variants, and Lenovo 32UD-10.

### Aggregator warning

Observed metadata errors include:
- MSI MPG 321URX incorrectly described as curved on a Prisjakt record;
- some coating descriptions conflicting with manufacturer/reviewer material;
- MSI MAG 322UP listing titles reporting 240 Hz while the currently indexed MSI MAG 322UP QD-OLED E16 manufacturer page says 165 Hz.

Never use aggregator metadata as the final engineering source. Verify exact SKU/EAN.

## ASUS 32-inch glossy WOLED

- ROG Strix OLED XG32UCWG Swedish specifications  
  https://rog.asus.com/se/monitors/27-to-31-5-inches/rog-strix-oled-xg32ucwg/spec/  
  31.5-inch flat WOLED, TrueBlack Glossy, 4K165/FHD330, Auto KVM, DP1.4 DSC, HDMI2.1, 3-year warranty including panel burn-in.

- ASUS XG32U announcement / TrueBlack Glossy / OLED Care Pro  
  https://www.asus.com/se/news/mksxwdkf04dlg6s9/  
  Covers XG32UCWG and XG32UCWMG; Clear Pixel Edge, Neo Proximity Sensor, dual mode, burn-in warranty.

- TFTCentral XG32UCWMG review  
  https://tftcentral.co.uk/reviews/asus-rog-strix-xg32ucwmg  
  Measured Uniform Brightness behavior and roughly 32-nit minimum with UB enabled; glossy WOLED/ambient-black discussion.

- Tom's Hardware XG32UCWMG review  
  https://www.tomshardware.com/monitors/gaming-monitors/asus-rog-strix-xg32ucwmg-4k-oled-gaming-monitor-review  
  4K240/FHD480 behavior, brightness tables, HDR measurements, OLED-care/KVM details.

- RTINGS XG32UCWMG review  
  https://www.rtings.com/monitor/reviews/asus/rog-strix-oled-xg32ucwmg  
  Sharp text, glossy clarity, WOLED black-level behavior, dual mode.

## ASRock PGO32UFS

- ASRock official product page  
  https://pg.asrock.com/Monitors/PGO32UFS/  
  Flat WOLED, 4K240/FHD480, KVM, USB-C 65W, Pixel Clean/logo dimming.

- TFTCentral review  
  https://tftcentral.co.uk/reviews/asrock-phantom-gaming-pgo32ufs  
  Measured ~21-nit minimum, updated WOLED subpixel layout/text clarity, matte coating, burn-in warranty confirmation from ASRock.

## LG 32-inch dual-mode WOLED

- LG 32GS94UX product page  
  https://www.lg.com/de/monitore/gaming/32gs94ux-b/

- TFTCentral LG 32GS95UE review  
  https://tftcentral.co.uk/reviews/lg-32gs95ue  
  Closely related 32-inch 4K240/FHD480 WOLED platform; measured ~18–19-nit minimum, uniform SDR behavior, matte coating, text clarity.

- LG Sweden warranty terms  
  https://www.lg.com/se/support/garanti/  
  General monitor warranty listed as 25 months; no clear monitor burn-in inclusion on the general page.

## Lenovo Legion OLED monitors

- Lenovo Sweden Legion monitor family  
  https://www.lenovo.com/se/sv/legion-gaming-monitors/  
  OLED Care Technology description.

- Legion Pro 27UD-10 PSREF  
  https://psref.lenovo.com/Product/Legion_Pro_27UD_10_Monitor?tab=spec  
  3-year limited warranty, ports/specifications.

- Legion Pro 32UD-10 PSREF  
  https://psref.lenovo.com/syspool/Sys/PDF/Lenovo_Monitors/Lenovo_Legion_Pro_32UD_10/Lenovo_Legion_Pro_32UD_10_Spec.pdf  
  3-year limited warranty and 4K240-capable HDMI/DP details.

Important: primary material located during this pass does not explicitly state that Lenovo's limited warranty includes burn-in. Confirm before purchase.

## Philips Evnia 32M2N8900

- Philips Sweden product page  
  https://www.philips.se/c-p/32M2N8900_01/4k-uhd-gaming-monitor-qd-oled-spelskaerm

- Philips Sweden support page  
  https://www.philips.se/c-p/32M2N8900_00/4k-uhd-gaming-monitor-qd-oled-gaming-monitor/kundtjanst

- Swedish price page  
  https://www.prisjakt.nu/produkt.php?p=14567413

Exact regional suffix/SKU should be checked because current price listings mix /00, /01 and distributor naming.

## MSI 32-inch QD-OLED

- MPG 321URX Swedish price page  
  https://www.prisjakt.nu/produkt.php?p=13326290

- MSI MAG 322UP QD-OLED E16 official  
  https://www.msi.com/Monitor/MAG-322UP-QD-OLED-E16  
  Useful warning case: MSI's currently indexed E16 page specifies 165 Hz despite some Swedish aggregator titles saying 240 Hz.

- MSI OLED Care / 3-year burn-in coverage appears explicitly across current MSI QD-OLED product material.

## 2026 true RGB-stripe / premium watch

- ASUS Swedish TrueBlack Glossy model list including PG32UCWM  
  https://rog.asus.com/se/monitors-group/allmodels/?items=130448

- ASUS PG32UCWM was observed around 14.4–14.5k SEK in Swedish/Amazon price listings during the snapshot.

- ASUS PG27UCWM was observed around 13.49k SEK through Inet Sweden during the snapshot.

- MSI announced MPG 322URDX36 with fifth-generation Penta-Tandem QD-OLED RGB stripe and multi-mode 360/520/680 Hz in 2026; recheck Swedish availability/pricing when it reaches retail.

## General OLED/text/coating references reused for buying analysis

- RTINGS WOLED vs QD-OLED  
  https://www.rtings.com/monitor/learn/woled-vs-qd-oled

- RTINGS glossy vs matte  
  https://www.rtings.com/monitor/learn/glossy-vs-matte

- TFTCentral RGB-stripe OLED panels  
  https://tftcentral.co.uk/articles/oled-rgb-stripe-panels-explained-should-you-wait

- TFTCentral OLED black crush / shadow detail  
  https://tftcentral.co.uk/articles/does-oled-have-a-black-crush-problem-understanding-and-testing-oled-shadow-detail
