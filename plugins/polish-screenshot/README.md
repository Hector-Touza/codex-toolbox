# Polish Screenshot for Codex

[![License: MIT](https://img.shields.io/badge/License-MIT-0f766e.svg)](LICENSE)
[![Codex skill](https://img.shields.io/badge/Codex-skill-E96872.svg)](skills/polish-screenshot/SKILL.md)

Polish Screenshot edits original screenshot pixels locally, optionally obscures confidential regions with blur, pixelation, or solid masks, and turns the result into a publication-ready composition. It adds reusable local backgrounds, balanced padding, restrained rounded corners, a subtle border, and a soft two-layer shadow.

The workflow runs locally. It does not send screenshots to a rendering service.

![Four local background treatments applied to the same sample window](assets/preview.png)

## What it does

- Polishes PNG, JPEG, and WebP screenshots with one deterministic Python CLI.
- Redacts repeatable pixel-coordinate regions with blur, pixelation, or solid masks.
- Generates coordinate-grid guides for visually selecting and refining regions.
- Includes four contrasting background presets and supports custom colors or images.
- Generates reusable background PNG files at any canvas size.
- Guides Codex through capture, visual inspection, correction, and export.
- Keeps sensitive screenshot content on the local machine.
- Never uses Image Gen, inpainting, generative fill, or reconstructed interface pixels.

## Install

Add Codex Toolbox and install the plugin:

```bash
codex plugin marketplace add Hector-Touza/codex-toolbox --ref main
codex plugin add polish-screenshot@codex-toolbox
```

Install the runtime dependency:

```bash
python -m pip install "Pillow>=10"
```

## Use

Invoke the skill as `$polish-screenshot`, or run its CLI from this plugin directory:

```powershell
python skills/polish-screenshot/scripts/polish_screenshot.py polish `
  examples/sample-window.png `
  --output polished-window.png `
  --canvas 1536x864 `
  --background-preset aurora-night
```

List or render the supplied backgrounds:

```powershell
python skills/polish-screenshot/scripts/polish_screenshot.py presets
python skills/polish-screenshot/scripts/polish_screenshot.py backgrounds `
  --output-dir backgrounds
```

Create a temporary coordinate guide and a 1:1 redacted preview before polishing:

```powershell
python skills/polish-screenshot/scripts/polish_screenshot.py guide raw-window.png `
  --output raw-window-guide.png

python skills/polish-screenshot/scripts/polish_screenshot.py redact raw-window.png `
  --output raw-window-redacted.png `
  --redact-region 180,460,350,105 `
  --redaction-style blur `
  --redaction-strength 24
```

Inspect the redacted preview at original resolution and adjust its regions before creating the final composition. Follow the user's requested visibility scope exactly. Use `solid` with `--redaction-feather 0` when disclosure would have meaningful consequences; blur is visual obfuscation, not guaranteed secure erasure.

## Presets

| Preset | Direction |
| --- | --- |
| `coral-waves` | Warm editorial color with quiet flowing lines. |
| `aurora-night` | Dark developer-focused field with colored light. |
| `cobalt-grid` | Structured blue technical treatment. |
| `paper-sunrise` | Understated light composition with warm color. |

Use `--background-image` for a brand asset or `--background-color` for a strict solid color. Canvas, padding, radius, shadow blur, shadow opacity, and export quality are configurable.

## Requirements and limitations

- Python 3.10 or newer.
- Pillow 10 or newer.
- The CLI composes an existing screenshot; it does not capture arbitrary desktop windows itself.
- Redaction regions use `X,Y,WIDTH,HEIGHT` in source-image pixels and may be repeated.
- The skill can guide native Windows window capture or use a browser/app screenshot tool when one is available.
- Always inspect the final image. Small interface text can become unreadable when the source window is too large for the chosen canvas.

## License

[MIT](LICENSE) © 2026 Hector Touza.
