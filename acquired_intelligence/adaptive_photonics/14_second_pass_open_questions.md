# Second-pass open questions and research queue

This file is deliberately not an executable task list. It is a parking lot of questions whose answers could materially change implementation choices.

## Highest-value unknowns

### 1. Can Electron/WebGPU actually deliver HDR headroom on both target OSes?

Need empirical answer on:
- Windows 11 HDR;
- KDE Plasma Wayland HDR;
- NVIDIA current driver;
- Electron 44+ / Chromium 152+.

Test:
- `rgba16float`;
- extended tone mapping;
- values >1.0;
- known native scRGB comparison.

If yes, this may be the fastest serious prototype route.

### 2. What exact textures/data do kitty custom shaders receive?

Need inspect:
- `KittyTextures`;
- whether text/background/images are separable;
- whether only final backbuffer exists;
- persistent texture semantics;
- shader precision/formats;
- Windows/Linux support differences.

If enough information is available, kitty may be the best algorithm laboratory.

### 3. Can Zed expose the right renderer seam cheaply?

Need source investigation of:
- text/glyph atlas;
- editor background primitive;
- GPUI platform backend;
- color space;
- swapchain format;
- post-process hooks.

Could become the first real-editor proof if the architecture is friendly.

### 4. How does KWin handle a real FP16 Windows-scRGB Wayland surface on current NVIDIA?

Protocol existence is not proof.

Need:
- advertised features;
- buffer format;
- explicit `create_windows_scrgb`;
- values >1.0;
- ICC profile active/inactive;
- direct scanout;
- window moved between outputs.

### 5. What does the eventual OLED actually do below 10 nits?

Need measurements or at minimum review-specific investigation:
- first visible gray;
- black crush;
- banding;
- static dimming;
- low-refresh gamma shift;
- minimum brightness;
- pixel-uniformity.

For this user, this may matter more than peak brightness.

## Algorithm unknowns

### Minimum useful intervention

How much can be achieved with:
- local luminance reduction only;
- detail-band suppression only;
- both?

Do not overbuild before this is known.

### Best spatial mask

Compare:
- rectangular line/token masks;
- glyph bounding boxes;
- exact coverage;
- distance field.

This determines how much editor cooperation is actually required.

### Counter/interior policy

Should wallpaper remain untouched inside glyph counters, or be suppressed there too?

### Fine-detail bands

Which spatial-frequency bands cause the largest recognition penalty for small monospace glyphs?

Potentially derive from:
- empirical tests;
- castleCSF weighting;
- font stroke geometry.

### Edge orientation

Does background-edge orientation relative to glyph stroke materially affect error rate?

If not, do not implement Gabor/steerable analysis.

### Chroma versus luminance conflict

How often does syntax-color confusion occur independently of luminance/detail?

If rare, defer chroma-aware policy.

### Text luminance adaptation granularity

Per:
- whole theme;
- token class;
- line;
- token;
- glyph?

Prediction: background can adapt per-pixel, but foreground should adapt much more coarsely to avoid visible pumping.

## Human-vision unknowns

### Viewing distance

Need actual desk distance eventually.

Physical PPI alone is incomplete.

### Ambient light

Need rough coding-room environment:
- dark;
- dim indirect;
- daylight.

Could matter enormously for:
- pupil size;
- QD-OLED black raise;
- near-black perception.

### Personal sensitivity

User preference for extreme dimness does not prove that the smallest-code condition will be most legible at minimum luminance.

Run actual identification tests.

### Long-session adaptation

A setting that looks beautiful for 30 seconds may cause:
- eye fatigue;
- headache;
- contrast adaptation;
- annoying halo perception after an hour.

Test long sessions after short-form algorithm selection.

## Text-rendering unknowns

### Grayscale versus subpixel at 27" 4K RGB stripe

At ~163 PPI, grayscale may be sufficient and more robust.

Test before spending effort on custom subpixel AA.

### Font hinting

Does hinting still materially improve the user's target sizes at 4K PPI?

### Variable-font grade

Can small grade changes improve tiny text without changing layout or looking unstable?

### Gamma correction

How should glyph coverage be adjusted for:
- bright-on-dark;
- actual target luminance;
- OLED?

Skia/FreeType/DirectWrite behavior may differ.

## Presentation unknowns

### Reference white semantics

Need explicit backend model distinguishing:
- stimulus mapping;
- SDR white;
- HDR reference white;
- compositor assumed white;
- user SDR brightness slider.

Do not expose one ambiguous `reference_white` float.

### Tone mapping ownership

For each backend:
- application;
- OS compositor;
- monitor.

Need to know who clips/rolls off and under what conditions.

### Multi-display windows

What happens when:
- most window on HDR display;
- center crosses into SDR;
- Windows reclassifies "main" output;
- Wayland surface spans outputs?

Perhaps simply prohibit/disable calibrated HDR adaptation when spanning.

### Screenshot/capture

How should debug dumps encode:
- SDR PNG;
- HDR AVIF/JXL/EXR;
- linear EXR;
- sidecar metadata?

A screenshot that clips HDR is useless as a bug report.

## Hardware-selection unknowns

### Exact 2026 panel choice

At purchase time compare:
- 27" 4K RGB-stripe OLED;
- 32" 4K OLED;
- WOLED vs QD-OLED;
- minimum brightness;
- near-black behavior;
- coating;
- burn-in warranty;
- ASBL;
- Linux compatibility.

### Three-monitor topology

Check exact NVIDIA generation/display-head limits with:
- one 4K high-refresh OLED;
- existing two side monitors;
- desired refresh rates;
- DSC.

### Connection

Compare HDMI vs DP on exact monitor/GPU:
- 4:4:4;
- 10 bit;
- DSC;
- HDR;
- VRR;
- Linux sleep/wake.

## Fun but not justified yet

- monocular depth estimation;
- semantic segmentation;
- eye tracking;
- ambient-light sensor;
- learned readability model;
- neural local filter;
- CSF-weighted Gabor bank;
- per-panel custom subpixel renderer;
- KWin custom protocol/effect;
- compositor-level cooperative glyph mask;
- hardware-in-loop CI with colorimeter.

These are preserved because the whole point of this directory is not to lose possibly useful insanity.

## Suggested next investigation order if implementation begins

1. Offline SDR image + text-mask prototype.
2. kitty and/or Windows Terminal shader prototype.
3. Electron/WebGPU HDR capability probe.
4. Acquire/characterize high-PPI OLED.
5. Standalone HDR renderer.
6. Cross-platform Windows/KDE equivalence tests.
7. Only then choose editor integration target.

The visual algorithm should earn the infrastructure.
