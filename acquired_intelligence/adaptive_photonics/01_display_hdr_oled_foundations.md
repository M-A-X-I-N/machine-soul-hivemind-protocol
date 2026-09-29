# Display, HDR, SDR, OLED, and pixel-density foundations

## Separate the concepts

| Concept | What it answers |
|---|---|
| SDR / HDR | What range/meaning of luminance and color can the signal represent? |
| Transfer function (sRGB, PQ, HLG) | How are code values mapped to light or scene values? |
| Color primaries/gamut | Which colors can be represented? |
| Bit depth | How finely can channels be quantized? |
| Tone mapping | How is content adapted when source range exceeds display range? |
| Local dimming | How spatially independently can an LCD backlight vary? |
| OLED per-pixel emission | How spatially independently can emitted light vary? |
| DisplayHDR | Did the physical display pass a VESA performance tier? |
| HDR10 | Does the signal use the HDR10 ecosystem: PQ/BT.2020 container plus static metadata? |

Do not let monitor marketing collapse these into one word.

## SDR is not "fake HDR"

SDR still allows every individual RGB pixel value to vary. On an OLED, an SDR image can put an off pixel directly beside a bright pixel. What SDR lacks is the extended HDR signal model/range and related transfer semantics.

A surprisingly large amount of the adaptive-background concept can be prototyped entirely in SDR:
- render detailed image;
- derive glyph coverage;
- dim/smooth/desaturate locally;
- composite text;
- exploit OLED's per-pixel black level.

HDR adds extra luminance/color headroom and more explicit luminance semantics.

## PQ / SMPTE ST 2084

PQ is a perceptual transfer function used by HDR10 and other HDR systems. ITU-R BT.2100 standardizes PQ and HLG for HDR television.

Important conceptual property: PQ is tied to absolute display luminance much more directly than classic relative SDR gamma.

Source:
https://www.itu.int/rec/R-REC-BT.2100

## HLG

Hybrid Log-Gamma is another HDR transfer system, designed with broadcast/relative-display behavior and compatibility considerations different from PQ.

HLG is useful background knowledge but is unlikely to be the natural internal representation for an interactive compositor.

## scRGB / extended linear sRGB

This is much more interesting for the renderer.

Windows Advanced Color guidance recommends an FP16 swapchain using `DXGI_FORMAT_R16G16B16A16_FLOAT` with scRGB for general-purpose advanced-color apps.

In Windows' scRGB convention:
- `(1.0, 1.0, 1.0)` nominally corresponds to 80 nit D65 reference white;
- values above 1.0 are valid;
- the representation is linear-light, making composition/math much saner.

Wayland color-management-v1 explicitly defines a predefined Windows-scRGB stimulus encoding too.

Sources:
- https://learn.microsoft.com/en-us/windows/win32/direct3darticles/high-dynamic-range
- https://wayland.app/protocols/color-management-v1

Internal representation should probably be floating-point linear light regardless of final presentation encoding.

## Tone mapping

If content describes luminance beyond what the monitor can reproduce, some mapping is required:
- clipping;
- highlight compression/roll-off;
- global remapping;
- local/dynamic remapping.

For a custom UI compositor, avoid unnecessary tone-mapping ambiguity by keeping intended UI luminances comfortably within measured display capability.

## APL / ABL / static dimming

OLED peak brightness depends heavily on how much of the panel is lit and for how long.

Relevant terms:
- **APL** — average picture level;
- **ABL** — automatic brightness limiter, usually power/thermal behavior tied to bright image area;
- **ASBL/TPC/static dimming** — brightness reduction when content remains static, often burn-in protection.

VESA's current DisplayHDR/True Black criteria explicitly distinguish small-window and full-screen requirements:
https://displayhdr.org/performance-criteria/

Programming is unusually static, so **ASBL behavior may be more important than headline HDR peak brightness**.

For the maintainer's very low brightness preference, ABL may rarely engage in normal editor use. ASBL may still be annoying because typing/reading can leave most of the frame unchanged.

## OLED burn-in

Burn-in is differential aging of emissive elements. It is not the same as temporary image retention.

Programming contains many persistent structures:
- menu chrome;
- tabs;
- line-number gutter;
- status bars;
- scrollbars;
- static panes;
- code that can remain on screen for hours.

Mixed use and low brightness are favorable conditions, but neither makes burn-in impossible.

Useful long-run secondary sources:
- https://www.rtings.com/tv/learn/oled-burn-in-not-improved-as-expected
- https://www.rtings.com/tv/learn/longevity-results-after-10-months

Monitor selection should include:
- burn-in warranty;
- pixel-shift behavior;
- static-dimming behavior;
- panel refresh cycles;
- whether protection features are configurable through supported settings.

## OLED's spatial advantage

Mini-LED LCD:
- LCD pixels modulate a backlight;
- many pixels share one backlight zone;
- bright content near dark content can bloom because the lighting zone is larger than a glyph edge.

OLED:
- each pixel is emissive;
- black can be physically near-zero emission;
- a bright glyph edge can sit beside a dark background pixel with no backlight-zone halo.

This is close to ideal for a compositor that intentionally creates tiny local luminance relationships around glyphs.

That property is **OLED**, not "HDR."

## Subpixel layout is crucial for programming

Traditional LCD text rendering often assumes a regular RGB stripe.

OLED monitors historically violate that assumption:
- older WOLED: RWBG;
- newer WOLED generations: RGWB;
- QD-OLED generations through 2025/early 2026: triangular RGB arrangements;
- newer 2026 OLED panels are beginning to use more conventional stripe/V-stripe arrangements.

Windows ClearType docs explicitly describe stripe orientation/order dependence:
https://learn.microsoft.com/en-us/windows/win32/gdi/cleartype-antialiasing

FreeType can model arbitrary regular subpixel geometry in its Harmony LCD renderer, including unusual geometries:
https://freetype.org/freetype2/docs/reference/ft2-lcd_rendering.html

RTINGS text-clarity material:
- https://www.rtings.com/monitor/tests/picture-quality/text-clarity
- https://www.rtings.com/monitor/learn/woled-vs-qd-oled

### 2026 development worth watching

27" 4K RGB-stripe OLED panels are entering the monitor market. TFTCentral reports LG Display's 27" 4K RGB-stripe WOLED panel in mass production, and 2026 reviews are appearing for RGB-stripe 27" 4K OLED products.

Sources:
- https://tftcentral.co.uk/articles/oled-rgb-stripe-panels-explained-should-you-wait
- https://www.wired.com/review/asus-rog-swift-rgb-stripe-oled-pg27ucwm/

Availability, pricing, and exact panel sourcing are volatile. Recheck before purchase.

## Why 27" 4K is interesting

Approximate PPI:
- 27" 4K: ~163;
- 32" 4K: ~138;
- 27" 1440p: ~109;
- 27" 1080p: ~82.

At 27" 4K, grayscale antialiasing can become more attractive because brute-force physical sampling is high enough that subpixel AA's extra horizontal resolution matters less, while avoiding subpixel-layout assumptions.

Test this with the exact panel/font/viewing distance rather than treating it as dogma.

## Screen coating and ambient light

OLED black level is only "zero" for emitted light. Reflections still exist.

Some QD-OLED/coating stacks can show raised/purple-looking blacks in brighter ambient conditions. Matte coatings reduce mirror-like reflections but can reduce apparent clarity.

The maintainer normally runs displays extremely dim, suggesting a relatively dark viewing environment; that favors OLED contrast.

## Purchase-oriented research questions

Before buying:
1. Exact physical subpixel layout, not merely "OLED."
2. 27" 4K versus 32" 4K at actual desk distance.
3. Minimum brightness and low-luminance stability.
4. ASBL/static-dimming behavior during typing/reading.
5. Burn-in warranty wording.
6. Supported HDR modes on Windows and Linux.
7. NVIDIA compatibility reports for the exact monitor/connection.
8. DisplayPort/HDMI bandwidth and DSC behavior at 4K high refresh.
9. Screen coating/reflection behavior.
10. Whether HDR and VRR coexist reliably.
11. Whether the monitor exposes sensible calibration/ICC behavior.
12. Whether text looks better with grayscale AA, OS subpixel AA, or custom panel-aware AA.


## Second-pass scRGB reference-white nuance

The convenient statement "scRGB 1.0 = 80 nits" needs careful scope.

For Windows-scRGB stimulus encoding, the Wayland protocol specifies:
- R=G=B=0.0 corresponds to 0 cd/m²;
- R=G=B=1.0 corresponds to 80 cd/m²;
- values can extend above 1.0 (up to the protocol-described 10,000-nit mapping range).

However, the same protocol explicitly says the **reference white level of Windows-scRGB is unknown/variable**. When a compositor must assume a reference white for processing, it recommends R=G=B=2.5375, corresponding to **203 cd/m²** per ITU-R BT.2408-7.

It also warns that `EGL_EXT_gl_colorspace_scrgb_linear` has different semantics: there 1.0 is defined as reference white.

Source:
https://wayland.app/protocols/color-management-v1

Practical rule:
- distinguish **stimulus luminance mapping** from **reference white for composition/viewing semantics**;
- do not bake a single universal "1.0 = reference white" assumption into the core renderer;
- platform backend owns this translation.
