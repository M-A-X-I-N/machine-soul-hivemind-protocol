# Conversation brain dump

## Initial monitor/text problem

The motivating display is 1080p. The practical complaint is not "small text is literally unreadable"; it is that below a certain size there are insufficient physical samples to recognize ambiguous character sequences at a glance while simultaneously thinking about code.

Observed subjective thresholds from the conversation:
- below roughly 16 px, characters start looking visibly compromised;
- with less humanist/more code-oriented monospace fonts, below roughly 13 px certain glyph sequences become materially harder to distinguish;
- tiny text can still be decoded, but decoding costs attention: e.g. deciding whether a cluster is `rn`, `m`, `mm`, `ro`, `rb`, etc.;
- the actual objective is therefore **higher information density without sacrificing instant glyph discrimination**.

Approximate reference densities:

| Size / resolution | Approximate PPI |
|---|---:|
| 24" 1920×1080 | 92 |
| 27" 1920×1080 | 82 |
| 27" 2560×1440 | 109 |
| 32" 3840×2160 | 138 |
| 27" 3840×2160 | 163 |

At equal physical glyph size, 4K provides far more samples for the outline/coverage than 1080p. OS DPI scaling can preserve similar logical geometry while increasing physical sampling quality.

## Why OLED entered the picture

The display is also used for gaming. The purchasing preference is effectively: once spending substantial money, spending more for an objectively better long-lived result can feel "cheaper" than buying an intermediate compromise twice.

Therefore the target drifted from merely "high-PPI coding panel" toward a good 4K OLED that is also an excellent gaming monitor.

## Extremely low-brightness preference

The maintainer strongly prefers dark mode and very low emitted light:
- phone commonly uses eye-comfort and extra-dim settings except in direct sunlight;
- two current monitors are run at brightness 0;
- another is at 7 because 6 turns it completely black.

Consequences:
1. headline full-screen OLED brightness is almost irrelevant to normal coding comfort;
2. low-black-level performance and fine low-end control matter much more;
3. high peak brightness remains useful for gaming/HDR content and experimental local highlights, but the adaptive compositor should use it sparingly;
4. aggressive OLED ABL may matter less at these ordinary levels, but ASBL/static dimming can still be annoying for programming;
5. burn-in exposure is plausibly reduced by low luminance, but static UI remains a genuine workload risk.

## Background-image requirement

The maintainer dislikes coding for long periods against a conventional flat/static background.

Desired images have strong spatial-depth cues: perspective, layered distance, foreground/background separation, scale, atmospheric depth, etc. "Depth of field" was used colloquially in conversation but is too narrow.

The subjective effect is that an image with convincing depth makes the physical screen plane feel less like a flat wall. A plain background eventually creates a "pseudo-claustrophobic" feeling.

Current workaround:
- place image behind editor;
- blur image so heavily that code remains readable.

Failure:
- giant blur destroys exactly the spatial detail/depth cues for which the image exists.

Hence the desired system should preserve the image globally and make only local interventions where code and image compete.

## The HDR terminology correction

The initial mental model of HDR was roughly:

> independently control brightness in different sections of the screen, with HDR quality determined by section size and brightness variation.

That actually describes **spatial light control/local dimming** much more than HDR.

Corrected separation:
- **SDR/HDR**: what luminance/color range and transfer semantics the signal can describe;
- **bit depth/gamut**: numerical/color resolution and reachable colors;
- **LCD/Mini-LED/OLED**: physical display technology;
- **local dimming / per-pixel emission**: spatial precision of emitted light;
- **HDR10 / HLG / Dolby Vision / etc.**: content/transport/metadata schemes;
- **DisplayHDR / DisplayHDR True Black**: VESA display-performance certifications.

An OLED can have per-pixel spatial luminance control while displaying entirely SDR content. An edge-lit LCD can accept a legitimate HDR signal while reproducing it poorly.

## The adaptive-compositor idea

```text
detailed wallpaper
      │
      ├── local luminance analysis
      ├── local detail/edge analysis
      └── optional chroma analysis
              │
glyph coverage/mask ──> conflict model
              │
              ▼
    glyph protection field
              │
        ┌─────┴─────┐
        ▼           ▼
background       text policy
suppression      / luminance
        └─────┬─────┘
              ▼
      linear-light composite
              ▼
     SDR or HDR presentation
```

Possible interventions:
- lower local background luminance;
- compress background contrast;
- suppress high spatial frequencies/detail;
- apply edge-aware smoothing rather than naive global Gaussian blur;
- gently reduce local saturation/chroma;
- raise glyph luminance;
- alter anti-aliasing or glyph weight;
- extend influence with a soft protection field invisible as a discrete rectangle.

The goal is not "brighter text." The goal is **stable perceptual separation with the minimum amount of image destruction**.

## Operating-system split

The machine is deliberately dual-boot:
- Windows on a separate M.2 is the "I want to play the game, not debug Linux" environment.
- Linux is acceptable and enjoyable when the purpose is experimentation/tinkering.
- KDE Plasma is strongly preferred.
- Linux target should therefore be **KDE Plasma + Wayland**.
- Existing GPU is NVIDIA.
- NVIDIA is accepted as an extra source of platform friction rather than a reason to replace hardware.

Architectural implication:

**Windows and Wayland backends are adapters. Neither owns the perception/rendering algorithm.**

## Abstraction preference

Protocol instability is acceptable if hidden behind a clean platform boundary. A moving Wayland color-management protocol should not force changes in the conflict model or image-processing core.

## Gaming scope

Linux gaming compatibility is explicitly not a project requirement. Windows exists specifically to keep gaming boring.

Gamescope/Proton remain useful research references because they exercise HDR/color-management machinery, not because this project needs to become a Linux-gaming stack.

## Desired philosophical outcome

The renderer should eventually answer:

> Given this exact background, these exact glyphs, this display's capabilities, and the user's comfort targets, what is the least destructive transformation that makes the code immediately legible?

That is the real problem statement.
