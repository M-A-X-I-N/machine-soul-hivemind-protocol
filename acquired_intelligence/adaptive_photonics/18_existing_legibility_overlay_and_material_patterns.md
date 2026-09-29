# Existing legibility, overlay, scrim, subtitle, and translucent-material patterns

Research snapshot: 2026-09-30.

A surprising amount of this project's UX problem already exists elsewhere:

> put important text/UI over visually uncontrolled imagery and keep it readable without destroying the underlying scene.

The neighboring domains include:
- augmented reality;
- subtitles;
- mobile text-over-image design;
- system bars;
- translucent OS materials;
- compositor blur effects.

They converge on a small set of patterns:
- change foreground color;
- add outline/shadow;
- add a local panel/scrim;
- alter background behind foreground;
- activate support only when contrast is insufficient.

Our proposed renderer can be viewed as a **high-resolution, continuous, glyph-shaped adaptive scrim**.

---

## 1. Augmented-reality text readability — unusually relevant research domain

AR is a brutal version of our problem.

Text is rendered over:
- arbitrary natural scenes;
- changing local brightness;
- uncontrolled texture;
- motion;
- colors the renderer does not own.

That is almost our wallpaper problem with the difficulty turned up.

### Drawing styles studied in AR

Existing studies compare:
- plain text;
- billboard / opaque panel;
- drop shadow;
- outline.

A large literature review published in 2024 summarizes that a billboard/panel is generally a robust readability mechanism because it creates a controlled local background.

This is exactly why subtitles and UI chips so often use boxes.

### Local background complexity matters

The AR literature repeatedly distinguishes **local texture around the text** from merely global image complexity.

That strongly supports our approach:

> do not globally blur the scene; modify only the region that perceptually competes with the text.

The user's original intuition turns out to match a mature research domain.

---

## 2. Gabbard et al. adaptive drawing-style algorithms

The AR work by Gabbard and collaborators tested active algorithms that adapt text/drawing-style color based on the scene.

Two notable algorithms:
- maximum HSV complement;
- **maximum brightness contrast**.

The maximum-brightness-contrast algorithm uses CIE XYZ luminance behavior and chooses a drawing-style brightness maximizing contrast against the local averaged background.

The studies found it performed better than simpler complement strategies, though robust billboard/panel approaches often remained more generally dependable.

### Important result for us

Changing the **foreground alone** can help, but a controlled local background is robust.

Our renderer can combine both:

```text
background intervention
    +
small foreground luminance adjustment
```

instead of making syntax colors swing between black/white based on wallpaper.

### Two separate contrast relationships

AR drawing styles reveal a useful conceptual distinction:

For plain text:
- text ↔ scene background contrast matters directly.

For a billboard:
- text ↔ billboard contrast;
- billboard ↔ scene contrast.

For an outline:
- text ↔ outline;
- outline ↔ scene.

Our proposed protection field creates the same layered relationship:

```text
glyph
  ↕
locally transformed wallpaper
  ↕
untouched wallpaper
```

This gives us two knobs:
1. glyph-to-protected-region separation;
2. protected-region-to-surrounding-scene continuity.

That second knob is basically **"can I see the halo?"**

---

## 3. SmartColor — "show upon contrast" is almost our policy philosophy

Project/paper:
**SmartColor: Real-Time Color Correction and Contrast for Optical See-Through Head-Mounted Displays**

Project page:
https://hci.cs.umanitoba.ca/Publications/details/smartcolor-real-time-color-correction-and-contrast-for-optical-see-through

SmartColor describes three strategies:

### Correction
Choose an alternate displayed color that best preserves the intended perceived color after scene/display blending.

### Contrast
Choose a color that preserves as much hue as practical while ensuring legibility.

### Show-upon-contrast
Make an additional component visible **only when a related component lacks enough contrast**.

That last strategy is philosophically dead-on.

Instead of always drawing a background panel:

```text
if readability is already fine:
    do nothing
else:
    reveal/apply support
```

Our equivalent:

```text
if glyph-background conflict < threshold:
    wallpaper untouched
else:
    progressively suppress only the conflicting background structure
```

This should be a core design principle.

The adaptive effect is not a permanent visual style.

It is an **intervention that earns its visibility**.

---

## 4. Android Palette — simple minimum-change foreground adaptation

AndroidX Palette has a tiny but useful production algorithm for choosing readable text colors over an extracted image swatch.

Source:
https://android.googlesource.com/platform/frameworks/support/+/refs/heads/androidx-main/palette/palette/src/main/java/androidx/palette/graphics/Palette.java

`Palette.Swatch` exposes:
- title text color;
- body text color.

Internally it:
1. tries white;
2. computes the **minimum alpha** needed to meet target contrast;
3. tries black if white cannot meet it;
4. uses separate title/body contrast targets.

Current source constants use approximately:
- 3.0 for title;
- 4.5 for body.

### Why it matters

The important pattern is not "use black or white."

It is:

> Find the **minimum intervention** that satisfies a readability constraint.

That maps directly onto our desired background algorithm.

Instead of:
- always darken wallpaper 40%;

solve:
- what is the smallest local detail/luminance suppression needed to meet the target?

This could become an iterative/binary-search policy around a conflict metric.

---

## 5. Android Material text-protection scrims

Material Design explicitly documents **text protection** for typography over imagery.

Classic guidance uses a translucent gradient scrim:
- stronger near the text;
- smoothly falling to zero;
- avoid blanketing the whole image;
- use only as much opacity as needed;
- keep gradients long/smooth enough to avoid visible banding.

Source:
https://m1.material.io/style/imagery.html

That is remarkably close to our protection-field concept.

### Our generalization

Material scrim:

```text
fixed region
× fixed black alpha gradient
```

Adaptive photonics:

```text
glyph distance field
× background conflict
× frequency-band suppression
× luminance/chroma policy
```

So this project can be described as:

> an adaptive, content-aware, per-glyph generalization of a well-established text-protection scrim.

That is a useful conceptual anchor.

---

## 6. Android system-bar contrast enforcement

Modern Android edge-to-edge UI also has a very practical existing pattern.

When navigation/system UI may sit over arbitrary app content:
- transparent bars are preferred where safe;
- the system can apply a **translucent contrast scrim** when necessary;
- apps can provide gradient protection behind system-bar content.

Current Android docs explicitly describe:
- contrast-enforced navigation bars;
- gradient status-bar protection;
- light/dark icon adaptation.

This is another production implementation of:

> let content show through until it would threaten foreground readability, then add local protection.

The region is coarse (system bar), but the policy is directly relevant.

---

## 7. Adaptive subtitle color management — direct video analogue

A 2026 eBay patent describes an **adaptive subtitle color management engine**.

Patent:
US 12,549,822.

High-level behavior:
1. use subtitle timestamps to identify video frames;
2. analyze the subtitle display region;
3. compute average background brightness/intensity;
4. choose a contrast subtitle color;
5. one implementation switches between white and black based on a threshold;
6. repeat as scene/background changes.

This is a relatively crude algorithm, but it is direct prior art for:

> foreground text color adapts over time based on the background beneath its display region.

For our purposes it is mostly a baseline to beat.

Problems:
- average color ignores local high-frequency texture;
- black/white switching can be visually unstable;
- syntax colors carry meaning and should not be destroyed;
- background modification is often preferable.

---

## 8. libass/mpv subtitles — battle-tested static baselines

mpv/libass expose several robust subtitle drawing styles:
- outline + shadow;
- background box;
- border blur;
- configurable foreground/background colors.

mpv's `background-box` mode draws a box around subtitle lines and corresponds to libass-specific `BorderStyle=4`.

Source:
https://mpv.io/manual/master/

Why this matters:

Every adaptive fancy algorithm needs to beat these dumb baselines:
- black outline;
- drop shadow;
- translucent box.

If a 2 px outline gives equal readability with less visual annoyance than our 14-pass frequency decomposition, the 14-pass filter has not earned its existence.

But outlines have a weakness important for tiny code:
- they change the apparent glyph silhouette/stroke weight.

Our background-only transform may preserve high-PPI glyph geometry better.

---

## 9. Windows Acrylic — production multi-layer readability material

Microsoft's Acrylic material is more sophisticated than "blur behind window."

Official design recipe:
1. background;
2. blur;
3. **exclusion blend layer to ensure contrast/legibility**;
4. tint;
5. noise.

Microsoft explicitly says the resources were tuned so text maintains acceptable contrast.

Source:
https://learn.microsoft.com/en-us/windows/apps/design/style/acrylic

### Useful lessons

#### Blur alone is not enough

Microsoft adds a separate contrast layer.

That is strong precedent for our separation of:
- detail suppression;
- luminance/contrast management.

#### Noise has a purpose

Acrylic adds noise not merely as decoration; smooth translucent/blurred gradients are prone to visible artifacts.

KWin independently uses noise after blur to mask banding.

That makes **tiny controlled noise/dither** worth preserving as a possible final step around locally flattened wallpaper regions.

#### Avoid overusing translucent material

Microsoft warns that large or layered acrylic regions can become visually distracting.

That aligns with our "minimal intervention" requirement.

---

## 10. Apple Vibrancy — foreground/background co-adaptation

Apple's `NSVisualEffectView` provides:
- translucency;
- background blur;
- **vibrancy**.

Apple describes vibrancy as subtly blending foreground/background colors to increase contrast and make foreground content stand out.

Standard AppKit controls such as `NSTextField` automatically participate where appropriate.

Source:
https://developer.apple.com/documentation/appkit/nsvisualeffectview

### Why this matters

Acrylic mostly highlights a transformed background material.

Vibrancy explicitly acknowledges:
- foreground and background can be co-adapted;
- grayscale foregrounds are easier to preserve predictably;
- arbitrary foreground/background hue interactions can be dangerous.

That is directly relevant to code syntax colors.

Potential policy:
- preserve syntax hue;
- adapt luminance/chroma only within constrained ranges;
- do not blindly "vibrancy blend" strongly colored syntax tokens.

---

## 11. GNOME Shell BlurEffect — clean background-only abstraction

GNOME Shell's `Shell.BlurEffect` supports:
- actor blur;
- **background blur** that blurs pixels beneath an actor without blurring the actor;
- optional brightness adjustment.

Source:
https://gnome.pages.gitlab.gnome.org/gnome-shell/shell/class.BlurEffect.html

The docs warn background mode is expensive because content beneath the actor cannot simply be cached.

This is a nice existing abstraction pattern:

```text
foreground actor
    untouched

background beneath actor
    blur + brightness
```

Our project is basically asking for a much more granular version driven by glyph masks.

---

## 12. KWin Blur — production compositor implementation worth mining

Current KWin blur source:
https://github.com/KDE/kwin/blob/master/src/plugins/blur/blur.cpp

Implementation details observed:
- dual-Kawase downsample/upsample blur;
- saturation transform;
- contrast transform;
- multi-pass framebuffer chain;
- additive noise after blur specifically to mask banding in smooth color transitions;
- damage-aware rendering.

### Very relevant engineering detail: damage expansion

Blur means a changed pixel affects neighbors.

Therefore the compositor must expand the damaged region by the filter radius.

Our local detail filter has the exact same issue.

If a glyph changes at x/y:
- the protection field changes around it;
- the filtered wallpaper in neighboring pixels changes too.

Dirty-tile invalidation must include filter/support radius.

KWin and Wayfire already contain production examples of this bookkeeping.

### Noise after local smoothing

KWin explicitly adds noise because smooth blurred gradients can band.

If our detail suppression creates flat local regions at extremely low OLED luminance, the same issue may appear.

Controlled dither/noise belongs in the experiment matrix.

---

## 13. Wayfire blur — another damage-aware compositor reference

Wayfire's blur plugin expands render damage based on blur radius before performing its effect.

Source:
https://github.com/WayfireWM/wayfire/blob/master/plugins/blur/blur.cpp

This is useful because it isolates the architecture more cleanly than a huge compositor:
- blur node/transform;
- algorithm provider;
- damage expansion.

If we ever write a KWin effect or other compositor-side experiment, Wayfire is a compact source-reading reference.

---

## 14. picom — historical X11 background-blur laboratory

picom supports multiple background blur methods:
- Gaussian;
- box;
- custom kernel;
- dual Kawase.

Source:
https://github.com/yshui/picom

X11 is not our target.

Still useful:
- comparison of blur techniques;
- long history of performance/driver edge cases;
- opacity/blur interaction;
- evidence that compositor background blur gets surprisingly messy.

This is historical reference, not implementation target.

---

## 15. Pattern taxonomy

### Pattern A — foreground adaptation

Examples:
- Android Palette;
- adaptive subtitle colors;
- AR maximum brightness contrast;
- Apple vibrancy.

Strength:
- minimal background disturbance.

Weakness:
- foreground semantics/colors can be destroyed;
- textured backgrounds may remain distracting.

### Pattern B — glyph decoration

Examples:
- outline;
- drop shadow;
- glow.

Strength:
- cheap;
- local;
- robust.

Weakness:
- changes tiny glyph silhouette;
- can create halos;
- may reduce high-PPI benefit.

### Pattern C — panel / scrim

Examples:
- AR billboard;
- subtitle background box;
- Material text-protection scrim;
- Android system-bar protection.

Strength:
- extremely robust.

Weakness:
- obscures image;
- visually obvious.

### Pattern D — transformed local backdrop

Examples:
- Acrylic;
- GNOME/KWin background blur;
- our proposed compositor.

Strength:
- preserves foreground raster;
- can retain scene context.

Weakness:
- more GPU work;
- halo/banding/temporal artifacts;
- needs good conflict policy.

### Pattern E — conditional support

Examples:
- SmartColor show-upon-contrast;
- Android contrast enforcement;
- our intended conflict-threshold behavior.

Strength:
- minimal intervention;
- preserves image whenever possible.

This is the preferred policy layer regardless of the actual transform.

---

## 16. Baselines every prototype should render side-by-side

For the same text/background:

1. unmodified wallpaper;
2. white/black foreground switch;
3. Android-Palette-style minimum foreground adjustment;
4. 1–2 px outline;
5. drop shadow;
6. translucent rectangular box;
7. smooth Material-style scrim;
8. global blur;
9. glyph-local blur;
10. local luminance suppression;
11. local detail/frequency suppression;
12. combined adaptive method.

The fancy method should win on:
- recognition accuracy;
- preserved image depth;
- low intervention visibility;
- stable motion.

If not, use the simpler thing.

## Sources

- AR readability review: https://link.springer.com/article/10.1007/s10055-024-00949-6
- Gabbard AR studies: https://ed-swan.github.io/publications/
- SmartColor: https://hci.cs.umanitoba.ca/Publications/details/smartcolor-real-time-color-correction-and-contrast-for-optical-see-through
- Android Palette: https://android.googlesource.com/platform/frameworks/support/+/refs/heads/androidx-main/palette/palette/src/main/java/androidx/palette/graphics/Palette.java
- Material imagery/text protection: https://m1.material.io/style/imagery.html
- Android system-bar protection: https://developer.android.com/develop/ui/compose/system/system-bars
- adaptive subtitle patent: https://patents.justia.com/patent/12549822
- mpv/libass options: https://mpv.io/manual/master/
- Windows Acrylic: https://learn.microsoft.com/en-us/windows/apps/design/style/acrylic
- Apple NSVisualEffectView: https://developer.apple.com/documentation/appkit/nsvisualeffectview
- GNOME Shell BlurEffect: https://gnome.pages.gitlab.gnome.org/gnome-shell/shell/class.BlurEffect.html
- KWin blur: https://github.com/KDE/kwin/blob/master/src/plugins/blur/blur.cpp
- Wayfire blur: https://github.com/WayfireWM/wayfire/blob/master/plugins/blur/blur.cpp
- picom: https://github.com/yshui/picom
