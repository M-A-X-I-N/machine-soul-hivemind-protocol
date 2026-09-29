# Calibration, measurement, and color-management plumbing

At some point "30 nits" needs to mean something more rigorous than "a float that looked nice."

This file maps how to characterize the display and how much trust to place in OS/display metadata.

## There are three different questions

1. **What does the OS/display claim the panel can do?**
2. **What transformation is the OS currently applying?**
3. **What photons actually come out?**

Do not confuse them.

## Windows display capability APIs

`AdvancedColorInfo` exposes quantitative characteristics including:
- maximum peak luminance;
- maximum average full-frame luminance;
- minimum luminance;
- SDR white level in nits;
- RGB primaries;
- white point;
- active/supported Advanced Color state.

Docs:
https://learn.microsoft.com/en-us/uwp/api/windows.graphics.display.advancedcolorinfo

The state can change while the app is running because of:
- user settings;
- OS policy;
- monitor changes.

Therefore presentation capability must be live state, not startup configuration.

## DXGI output description

`DXGI_OUTPUT_DESC1` / `IDXGIOutput6` also expose:
- bits per color;
- active color space;
- RGB primaries;
- white point;
- min luminance;
- max luminance;
- max full-frame luminance.

Use this for native DirectX integration, but note that newer Windows Advanced Color APIs cover scenarios DXGI alone cannot fully distinguish.

## Windows MHC2 calibration profiles

Windows 10 2004+ has a GPU hardware display color-calibration pipeline controlled through ICC profiles carrying the private **MHC2** tag.

Microsoft documents that MHC profiles can include:
- matrix transforms;
- 1D LUTs;
- peak luminance;
- max full-frame luminance;
- min luminance;
- RGB primaries;
- white point.

Source:
https://learn.microsoft.com/en-us/windows/win32/wcs/display-calibration-mhc

Important consequence:
Windows may rationalize HDR display metadata from:
- EDID / DisplayID;
- graphics driver;
- calibration profile.

A suitable MHC profile can override less trustworthy monitor metadata.

For an experimental renderer, this means the OS-reported values may already incorporate calibration rather than merely parroting EDID.

## ICC and Advanced Color

When Windows Advanced Color/auto-color-management is active, ordinary applications generally should **not** manually double-apply the display ICC transform.

Correct conceptual flow:
- tag/describe application content correctly;
- let Windows map it to the display;
- perform explicit custom gamut mapping only if needed.

If the app starts consuming display profiles itself, verify that the OS is not already applying equivalent transforms.

## LittleCMS

LittleCMS is a small, portable C color-management engine implementing ICC v2/v4.

Source:
https://littlecms.com/color-engine/

Potential uses:
- read source image profiles;
- convert wallpaper images into project working space;
- inspect arbitrary ICC profiles;
- test transformations offline;
- generate/debug profiles;
- gamut checks.

It supports floating-point workflows and is MIT-licensed at core.

This is useful even if Windows/KWin ultimately own display conversion, because **input assets still need sane color interpretation**.

## ICC limitations around HDR

Classic ICC display profiles were created primarily around traditional display characterization and do not magically describe every HDR behavior.

There are extended ICC/iccMAX efforts for HDR/extended-range workflows, while platform-specific HDR metadata and color-management APIs remain important.

Practical rule:
- use ICC for what it accurately describes;
- use platform HDR capability metadata for dynamic-range characteristics;
- measure the physical display if exact luminance matters.

## Wayland color-management ICC path

Wayland color-management-v1 includes an ICC creator path for ICC v2/v4 profiles as one way to describe a surface/output color space.

That is useful interoperability but does not imply the application should install/manage monitor profiles itself.

KWin/compositor remains responsible for display mapping.

## Measurement beats metadata

Monitor EDID/firmware values can be:
- approximate;
- rounded;
- factory targets rather than exact sample measurements;
- affected by current monitor brightness/settings;
- affected by OLED thermal/power behavior.

For serious calibration, use an instrument.

## Colorimeter versus spectrometer

### Colorimeter

Advantages:
- fast;
- sensitive at low light;
- relatively affordable;
- excellent for repeated display measurements.

Weakness:
- spectral sensitivity does not perfectly match the eye;
- accuracy depends on correction matrix/spectral correction for display technology.

### Spectrometer

Advantages:
- measures spectral power distribution directly;
- can create corrections for colorimeters;
- less dependent on knowing display technology.

Weakness:
- expensive;
- slower;
- often noisier at extremely low luminance.

Practical enthusiast route:
**good colorimeter + correct spectral correction for the exact OLED technology.**

## CCSS / CCMX correction files

ArgyllCMS and DisplayCAL ecosystems use correction data such as:
- CCSS spectral sample sets;
- CCMX correction matrices.

This matters for OLED because QD-OLED, WOLED, RGB OLED, LCD phosphors, etc. have very different spectral distributions.

Using a generic "OLED" correction can be worse than using a correction matching the actual panel generation.

## ArgyllCMS tangent

ArgyllCMS is a broad open-source color measurement/calibration suite.

Potentially useful pieces:
- spot luminance measurement;
- patch measurement;
- display characterization;
- instrument access;
- CGATS data generation;
- CCSS/CCMX workflows.

Even if its native Wayland display-control path is awkward, the **instrument-measurement machinery remains useful**.

One possible project workflow:
1. renderer displays known test patch;
2. Argyll/spotread measures it;
3. script records requested linear/scRGB value vs measured luminance/chromaticity;
4. fit display response / validate OS mapping.

That avoids requiring Argyll to own KWin's calibration pipeline.

## Build a characterization utility

Eventually create a tiny tool independent of the compositor:

```text
display-characterize
    --output <monitor>
    --mode sdr|hdr
    --patch-size 1%,10%,100%
    --value <linear/scRGB/PQ>
    --settle-ms ...
```

Log:
- OS capability metadata;
- monitor mode/settings manually noted;
- requested pixel values;
- patch size/APL;
- measured cd/m²;
- xy chromaticity if instrument supports it;
- refresh rate;
- VRR state;
- HDR state;
- temperature/time since panel refresh.

This dataset could answer:
- how linear is low-luminance output?
- where does black crush begin?
- does APL change requested luminance?
- does static dimming begin after N seconds?
- does refresh rate shift gamma?

## Low-luminance measurement is hard

For this project, 1–20 nit behavior may be more important than 1000-nit highlights.

At low luminance:
- instrument dark noise matters;
- ambient/reflected light matters;
- OLED temporal behavior matters;
- test-patch size can matter;
- eye adaptation changes subjective visibility.

Measure in controlled room conditions and do multiple samples.

## Physical luminance should be an optional policy

The compositor should support:

### Calibrated mode
Known display/output:
- target exact-ish nits;
- use measured mapping/capabilities.

### Relative mode
Unknown/remote/SDR display:
- use reference-white-relative values;
- enforce relative contrast;
- no promise of physical luminance.

This keeps the renderer useful when precise calibration is unavailable.

## Dithering and precision

A monitor can accept a 10-bit signal while using:
- native 10-bit panel behavior;
- 8-bit + FRC/temporal dithering;
- internal higher-precision processing.

Do not infer panel-native precision solely from OS output bit depth.

For this project:
- send the highest sensible precision through the OS pipeline;
- avoid self-inflicted 8-bit banding;
- evaluate near-black temporal artifacts on the actual panel.

## Instrumented regression tests

If the project becomes serious, hardware tests could assert tolerances such as:
- scRGB reference patch maps within X% of expected luminance;
- background suppression does not exceed target;
- no clipping until expected level;
- display state-change event updates backend;
- SDR fallback clips/rolls off predictably.

Hardware-in-loop tests are absurd for an editor background.

They are also exactly the kind of absurdity this project may eventually deserve.
