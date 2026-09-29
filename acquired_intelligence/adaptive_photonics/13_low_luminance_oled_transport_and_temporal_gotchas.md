# Low-luminance OLED, signal transport, and temporal gotchas

For this project, the usual review obsession with maximum HDR brightness is almost inverted.

The maintainer intends to spend substantial time at very low luminance, with tiny high-contrast text. That makes several "boring" display behaviors disproportionately important.

## Near-black detail / black crush

OLED can produce true black, but that does not mean it perfectly resolves every shade immediately above black.

TFTCentral's 2026 investigation discusses OLED shadow-detail loss / black crush and notes that exact mathematical gamma tracking near black can make the darkest shades practically indistinguishable.

Source:
https://tftcentral.co.uk/articles/does-oled-have-a-black-crush-problem-understanding-and-testing-oled-shadow-detail

Why this matters here:
- dark wallpaper details may disappear;
- syntax-theme differences near black may collapse;
- local suppression may accidentally push image structure below visible threshold;
- "0 nit black" is not useful if every intended 0.3–1 nit nuance disappears too.

The adaptive algorithm therefore needs a **minimum-visible-background floor** rather than blindly multiplying dark pixels toward zero.

## Perceptual floor versus physical floor

Possible policy:

```text
if background_detail_should_remain_visible:
    do not suppress below measured/perceptual near-black threshold
else:
    black is allowed
```

That threshold may depend on:
- display;
- gamma/EOTF mode;
- ambient light;
- viewer adaptation;
- refresh rate.

A calibrated profile could include a measured "first reliably distinguishable dark level."

## Low-refresh-rate gamma shift

RTINGS found gamma shifts on OLED monitors at low refresh rates, with dark shades affected most strongly.

Source:
https://www.rtings.com/monitor/learn/gamma-shift-investigation

This is distinct from ordinary VRR flicker.

Consequences:
- the same requested dark-gray value may appear different as refresh behavior changes;
- a renderer tuned at fixed 240 Hz may not look identical at lower refresh;
- dark-mode UI is exactly where the difference is easiest to see.

For desktop coding, refresh rate is usually stable, so this may be much less problematic than gaming.

Still:
- avoid unusual dynamic-refresh/power-saving modes while evaluating output;
- record refresh rate during color measurements.

## VRR flicker

OLED and VA displays can visibly flicker in dark scenes when frame times vary under VRR.

Source:
https://www.rtings.com/monitor/learn/research/vrr-flicker

This is principally a gaming issue for this user because Linux coding does not need VRR.

Practical split:
- desktop/coding mode: fixed high refresh may provide most stable low-luminance appearance;
- gaming mode: VRR enabled if desired, accept/model-specific flicker behavior.

The monitor should be evaluated for both modes separately.

## Why dark scenes expose flicker

Small absolute luminance changes can represent a large relative change near black.

If an OLED's electro-optical response shifts with refresh/frame timing, dark grays can visibly jump even when brighter regions seem stable.

This is another reason the adaptive compositor should not pin meaningful wallpaper structure to razor-thin near-black distinctions.

## Static dimming / ASBL

Programming is an unusually static workload.

Potential symptoms:
- entire display slowly dims while reading;
- brightness pops back after significant content change;
- algorithm thinks output luminance changed because of its own policy when panel protection actually changed it.

Test:
1. fixed dark editor scene;
2. no input for several minutes;
3. periodic instrument readings if available;
4. tiny caret blink only;
5. normal typing;
6. large scroll.

Record whether protection is triggered by:
- pixel activity;
- average luminance;
- time;
- UI/menu detection.

Do not disable safety features through unsupported service menus as a design assumption.

## OLED uniformity / vertical banding

Near-black gray uniformity can reveal:
- vertical bands;
- mura;
- tint;
- panel variation.

This may be much more visible to this maintainer than to a normal bright-desktop user because:
- dark gray occupies most of the UI;
- code editor backgrounds are large uniform regions.

Therefore read dark-gray uniformity sections of reviews, not merely black uniformity.

A monitor can have "perfect black" and still have ugly 2–5% gray uniformity.

## QD-OLED ambient-light black raise

Some QD-OLED panel/coating designs show elevated/purplish-looking blacks under ambient light compared with dark-room behavior.

For a user who runs very low brightness:
- uncontrolled ambient reflections can become a significant fraction of perceived black;
- room lighting can destroy the very contrast advantage being purchased.

A darker room favors OLED strongly.

## RGB-stripe 2026 development

TFTCentral notes the industry push toward RGB-stripe OLED layouts specifically to improve text clarity/image sharpness.

Source:
https://tftcentral.co.uk/articles/oled-rgb-stripe-panels-explained-should-you-wait

For this project, RGB stripe helps:
- tiny text;
- predictable subpixel AA;
- fewer colored fringes;
- custom raster experiments.

But high PPI still matters independently.

## Chroma 4:4:4 is non-negotiable for desktop text

A 4K panel can still look stupid if the transport path subsamples chroma.

RTINGS' current explanation emphasizes that chroma subsampling is particularly visible on PC text and flat colored edges.

Source:
https://www.rtings.com/tv/learn/chroma-subsampling

For desktop use target:
- RGB full-range; or
- YCbCr 4:4:4 where appropriate.

Avoid:
- 4:2:2;
- 4:2:0;

unless diagnosing bandwidth constraints.

This is especially relevant to syntax highlighting because colored fine edges are exactly what chroma subsampling damages.

## 10-bit signal versus panel-native precision

The GPU may output 10 bpc while the panel uses:
- native 10-bit addressing;
- 8-bit + FRC;
- other temporal/spatial dithering.

For the project, the critical questions are:
- does the complete path avoid visible banding?
- is temporal dithering visible/annoying at low luminance?
- does capture/screenshot preserve source precision?
- do low-end gray steps remain stable?

Do not fetishize "native 10-bit" as a label if measured output is good.

## Windows Advanced Color precision

Windows Advanced Color composes the desktop in FP16, preserving high precision before converting to the output signal.

Source:
https://learn.microsoft.com/en-us/windows/win32/direct3darticles/high-dynamic-range

That means application-side FP16 is meaningful even if the final link/panel is 10-bit or dithered.

The high-precision internal pipeline reduces self-inflicted quantization before the final stage.

## DSC

4K high-refresh monitors frequently rely on Display Stream Compression depending on link bandwidth.

For this project, the important point is not ideological fear of compression; it is ensuring the resulting mode still provides:
- native 3840×2160;
- target refresh rate;
- 10-bit/HDR where desired;
- RGB/4:4:4;
- no fallback to chroma subsampling.

Validate actual GPU output mode after connecting the monitor.

### Multi-monitor GPU resource tangent

Very high pixel-clock modes can consume additional display-engine resources on GPUs independent of raw memory bandwidth.

This matters because the user currently runs three monitors.

On specific GPU generations, multiple 4K high-refresh displays may hit display-head/resource limits even if connectors exist.

Therefore before buying:
- inspect the exact NVIDIA GPU's max simultaneous display/mode limits;
- include DSC/head-bonding behavior;
- test desired old side monitors + new 4K OLED configuration.

Do not assume "four ports = four arbitrary high-bandwidth displays."

## HDMI vs DisplayPort

Do not pick by logo alone.

For the exact monitor/GPU, compare supported combinations:
- 4K refresh rate;
- RGB 4:4:4;
- bit depth;
- VRR;
- HDR;
- DSC;
- multi-monitor limitations;
- sleep/wake behavior on Linux.

The best connector is the one that preserves the desired mode reliably.

## Full versus limited RGB range

PC desktop should normally use full-range RGB semantics.

A full/limited mismatch can cause:
- raised blacks;
- crushed blacks;
- wrong contrast.

Because this project deliberately works near black, a range mismatch would completely invalidate experiments.

Add a simple black/near-black/white range test to setup diagnostics.

## OLED pixel response and sample-and-hold

OLED transition response is extremely fast, but sample-and-hold persistence still exists.

At low frame/refresh rates:
- motion can stutter;
- scrolling text can blur perceptually from eye tracking even if pixel response is instant.

For code:
- high refresh can improve scrolling legibility and cursor motion;
- the adaptive temporal algorithm should not assume every frame is inspected statically.

## PWM / temporal modulation tangent

Some displays use temporal brightness-control mechanisms:
- PWM;
- DC dimming;
- dithering/FRC;
- panel compensation.

At extremely low brightness, temporal modulation can become more relevant for sensitive users.

Review/test:
- flicker measurements at minimum brightness;
- whether brightness setting changes modulation;
- whether HDR mode changes it.

Do not infer temporal stability from static photos.

## Pixel shifting and geometry

OLED protection may shift the image by a few pixels periodically.

Usually this is intentionally subtle.

For a custom renderer:
- do not attempt to counteract panel pixel shift;
- screen coordinates are still logical display pixels;
- the monitor applies shift after signal receipt.

For pixel-perfect subpixel experimentation, however, panel shift means a microscope/photo comparison may need to account for time-varying physical placement.

## OLED wear and adaptive UI

A fun future tangent:
the renderer itself could reduce static wear by tiny, non-distracting changes:
- vary wallpaper;
- shift noncritical background;
- avoid permanent pure-white chrome;
- occasionally reflow non-text decorative elements.

Do **not** move code glyphs around merely for burn-in prevention; positional stability matters more.

Monitor firmware already implements protection. Application-level wear mitigation is optional icing.

## Mode checklist after purchase

For each OS record:

```text
resolution:
refresh:
connector:
DSC:
GPU output color format:
GPU output dynamic range:
GPU output bit depth:
HDR enabled:
VRR enabled:
ICC/profile:
monitor picture mode:
monitor brightness:
ASBL/protection settings:
```

Then validate:
- chroma 4:4:4 pattern;
- black/near-black range;
- gradient banding;
- tiny text;
- HDR test patches;
- sleep/wake;
- multi-monitor behavior.

This baseline prevents debugging the renderer when the real problem is "NVIDIA silently selected YCbCr 4:2:2."
