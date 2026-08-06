---
name: polish-screenshot
description: Turn raw window or application screenshots into polished, publication-ready compositions with deterministic local backgrounds, padding, rounded corners, borders, and soft shadows. Use when Codex needs to beautify or frame screenshots, prepare LinkedIn or social images, create a consistent screenshot series, generate reusable backgrounds, compare screenshot treatments, or process sensitive screenshots without uploading them.
---

# Polish Screenshot

Create screenshot compositions locally with the bundled deterministic CLI. Keep the source content unchanged; improve only its framing and presentation.

## Workflow

1. Identify the source screenshot and intended channel. If the user has not provided a file, capture only the requested window or ask for the image.
2. Inspect the source before processing. Check for private content, accidental overlays, unreadable text, and excessive empty chrome.
3. Choose a canvas and background. If the user gives no visual direction, produce two or three contrasting presets instead of guessing one final style.
4. Run `scripts/polish_screenshot.py polish` from this skill directory.
5. Inspect every rendered candidate as an image. Check text legibility, even padding, shadow clipping, corner quality, and visual emphasis.
6. Adjust one or two parameters, render again, and keep only materially different candidates.
7. Save the selected output near the user's requested deliverables. Do not overwrite the source unless explicitly requested.

All processing is local. Do not upload a screenshot to an external service unless the user explicitly authorizes that destination and the image content.

## Quick start

Install the only runtime dependency when needed:

```powershell
python -m pip install "Pillow>=10"
```

List the built-in visual directions:

```powershell
python scripts/polish_screenshot.py presets
```

Create a LinkedIn-ready composition:

```powershell
python scripts/polish_screenshot.py polish raw-window.png `
  --output polished-window.png `
  --canvas 1536x864 `
  --background-preset coral-waves `
  --padding 96 `
  --radius 22 `
  --shadow-blur 42 `
  --shadow-opacity 0.26
```

Use a private branded background instead of a preset:

```powershell
python scripts/polish_screenshot.py polish raw-window.png `
  --output branded-window.png `
  --background-image brand-background.png
```

Render the built-in backgrounds as reusable PNG files:

```powershell
python scripts/polish_screenshot.py backgrounds `
  --output-dir backgrounds `
  --canvas 1536x864
```

## Preset selection

- Use `coral-waves` for warm editorial and social content.
- Use `aurora-night` for dark product, developer, or AI interfaces.
- Use `cobalt-grid` for technical and structured product material.
- Use `paper-sunrise` for understated light compositions.

Use `--background-color` for strict brand colors. Use `--background-image` for a supplied wallpaper, gradient, or campaign asset. These options are mutually exclusive with `--background-preset`.

## Capture guidance

On Windows, use `Alt+Print Screen` to copy the active window or use `Win+Shift+S` and select Window mode. Prefer a deliberately sized, non-maximized window when the result should read as a card. Exclude unrelated windows, notifications, menus, and private data.

When a browser or app screenshot tool is available, capture the exact target surface through that tool. Do not reconstruct or invent the screenshot's contents to make the example look cleaner.

## Refinement rules

- Preserve the source aspect ratio.
- Keep text at a readable final size; reduce padding before shrinking the screenshot too far.
- Use 6–10% canvas padding as the normal range.
- Keep corner radius proportional and restrained; 18–28 px works well at 1536x864.
- Prefer a broad, low-opacity shadow over a short, dark shadow.
- Keep backgrounds quieter than the screenshot.
- Produce PNG for text-heavy interfaces. Use JPEG or WebP only when smaller size matters.

Read [references/composition-guide.md](references/composition-guide.md) when choosing channel dimensions, diagnosing a weak render, or preparing a consistent multi-image series. Pre-rendered versions of all presets are available under `assets/backgrounds/` for inspection or direct reuse.
