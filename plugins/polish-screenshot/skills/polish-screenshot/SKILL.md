---
name: polish-screenshot
description: Edit and polish raw window or application screenshots locally, including non-generative privacy redaction with blur, pixelation, or solid masks plus deterministic backgrounds, padding, rounded corners, borders, and soft shadows. Use when Codex needs to obscure confidential screenshot regions, visually verify redactions, beautify or frame screenshots, prepare LinkedIn or social images, create a consistent screenshot series, generate reusable backgrounds, compare screenshot treatments, or process sensitive captures without uploading them.
---

# Polish Screenshot

Edit and compose screenshots locally with the bundled deterministic CLI. Operate only on existing pixels. Never use Image Gen, generative fill, inpainting, or reconstructed interface content for this workflow.

## Workflow

1. Identify the source screenshot and intended channel. If the user has not provided a file, capture only the requested window or ask for the image.
2. Inspect the source at its original resolution. Check for private content, accidental overlays, unreadable text, and excessive empty chrome.
3. Follow the user's visibility instructions exactly. If the redaction scope is ambiguous, propose the regions before applying them. Infer broadly only when the user explicitly asks to hide all sensitive content. Never silently hide additional content.
4. If redaction is requested, create a coordinate guide, inspect it, and render a standalone 1:1 redacted preview before composing the final image.
5. Open the redacted preview at original resolution. If protected content remains recognizable or the mask looks careless, adjust bounds, padding, style, or strength and render again. Do not accept a one-pass result without inspection.
6. Choose a canvas and background. If the user gives no visual direction, produce two or three contrasting presets instead of guessing one final style.
7. Run `scripts/polish_screenshot.py polish` from this skill directory, using the accepted redacted preview as input.
8. Inspect the final composition. Check redactions, text legibility, even padding, shadow clipping, corner quality, and visual emphasis. Iterate until both privacy and presentation are satisfactory.
9. Save the selected output near the user's requested deliverables. Never overwrite the source unless explicitly requested.

All processing is local. Do not upload a screenshot to an external service unless the user explicitly authorizes that destination and the image content.

## Privacy redaction

Generate a temporary coordinate guide:

```powershell
python scripts/polish_screenshot.py guide raw-window.png `
  --output raw-window-guide.png `
  --grid 100
```

Render a 1:1 blur preview. Repeat `--redact-region` for multiple areas; coordinates use source-image pixels:

```powershell
python scripts/polish_screenshot.py redact raw-window.png `
  --output raw-window-redacted.png `
  --redact-region 180,460,350,105 `
  --redact-region 180,735,260,42 `
  --redaction-style blur `
  --redaction-strength 24
```

Use `blur` for natural-looking visual concealment. Treat it as obfuscation, not guaranteed secure erasure. Use strong `pixelate` or `solid` with `--redaction-feather 0` for secrets, identifiers, credentials, or any content that must not be recoverable from the published pixels.

Read [references/redaction-guide.md](references/redaction-guide.md) before selecting regions or judging a redacted preview.

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

The `polish` command also accepts the same repeatable redaction arguments, but first validate the same regions with the standalone `redact` command. Use the accepted redacted preview as the final composition input to make the privacy review explicit.

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
