# Composition guide

## Canvas choices

| Use | Canvas | Notes |
| --- | --- | --- |
| LinkedIn landscape | 1536x864 | Strong default for a single product screenshot. |
| Presentation or demo | 1600x900 | Familiar 16:9 output for slides and video. |
| Documentation | 1600x1000 | Gives dense application windows more vertical room. |
| Square social post | 1200x1200 | Use more padding; avoid shrinking text below legibility. |

## Starting values

Use these values at 1536x864, then scale them proportionally for another canvas:

- Padding: 90–110 px.
- Corner radius: 20–24 px.
- Shadow blur: 36–48 px.
- Shadow vertical offset: 18–28 px.
- Shadow opacity: 0.20–0.28.

## Diagnose and correct

| Symptom | First correction |
| --- | --- |
| Interface text is hard to read | Reduce padding or choose a larger canvas. |
| Screenshot feels cramped | Increase padding by 12–24 px. |
| Result looks like a pasted rectangle | Increase shadow blur and reduce shadow opacity. |
| Background competes with the UI | Choose a quieter preset or a solid brand color. |
| Rounded corners cut controls | Reduce the radius; do not crop the source content. |
| Shadow disappears on a dark background | Increase opacity slightly, not blur. |
| Series feels inconsistent | Lock canvas, padding, radius, shadow, and one background family. |

## Candidate strategy

When visual direction is unknown, render:

1. `coral-waves` as the warm editorial option.
2. `aurora-night` as the dark high-contrast option.
3. `paper-sunrise` as the restrained light option.

Inspect those three before adding more variants. Keep only candidates that represent a real decision.
