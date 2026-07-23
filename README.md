# Excalidraw Studio for Codex

[![License: MIT](https://img.shields.io/badge/License-MIT-0f766e.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-2563eb.svg)](https://www.python.org/)
[![Local first](https://img.shields.io/badge/workflow-local--first-7c3aed.svg)](#local-first-by-design)

Excalidraw Studio is a local-first Codex plugin for creating, validating, rendering, and visually refining editable Excalidraw diagrams inside a Git repository.

It solves a practical agent workflow gap: generating `.excalidraw` JSON is easy, but ensuring that the file is valid, readable, visually balanced, editable, and safely stored in the right repository takes a repeatable toolchain. Excalidraw Studio bundles that toolchain as one skill, one local MCP server, and one dependency-free Python CLI.

![Excalidraw Studio local workflow](plugins/excalidraw-studio/assets/preview.png)

## What it does

- Compiles a compact diagram specification into a native, editable `.excalidraw` scene.
- Validates scene structure, element IDs, arrow bindings, and repository confinement.
- Inspects geometry for overlaps, clipping, ambiguous connections, and weak hierarchy.
- Renders a local SVG preview and, when Microsoft Edge is available, a local PNG preview.
- Gives Codex a deliberate visual QA loop: create → validate → render → inspect → adjust.
- Keeps the canonical diagram, previews, and reviewable diffs in your repository.

The bundled tools are `excalidraw_doctor`, `create_excalidraw_diagram`, `validate_excalidraw_diagram`, `inspect_excalidraw_diagram`, and `render_excalidraw_preview`.

## Why this exists

Without a dedicated workflow, an agent can produce syntactically plausible Excalidraw JSON that still has overlapping labels, broken arrow bindings, unreadable spacing, or an output path outside the intended project. Screenshots alone are not editable, while cloud share links move the source out of version control.

Excalidraw Studio treats the `.excalidraw` file as source code: local, editable, diffable, validated, and accompanied by a preview that Codex can actually inspect before declaring the diagram finished.

## Install

### From this public marketplace repository

Add this repository as a Codex plugin marketplace:

```bash
codex plugin marketplace add Hector-Touza/excalidraw-studio --ref main
```

Then restart the ChatGPT desktop app, open **Plugins**, choose **Excalidraw Studio**, and install it. In Codex CLI, open `/plugins`, select the `Excalidraw Studio` marketplace, and install the plugin. Start a new task or CLI session so the bundled skill and MCP tools are loaded.

This repository is the current public distribution channel. Excalidraw Studio has not yet been submitted to the official OpenAI Plugins Directory, so there is no official store listing to link to today.

### Ask Codex to install it for you

Paste this into Codex:

```text
Install and verify Excalidraw Studio from the public marketplace repository
https://github.com/Hector-Touza/excalidraw-studio. Use the official Codex plugin
marketplace flow, preserve my existing marketplaces, restart or start a new session
if required, and run its doctor check inside my current Git repository.
```

### Recommended: ask Codex to build your own version

The repository is intentionally small and auditable. If you prefer a version tailored to your operating system, policies, paths, and diagram style, ask Codex to recreate the capability rather than installing this exact bundle:

```text
Use the built-in plugin-creator and skill-creator workflows to build me a personal
Codex plugin equivalent to Excalidraw Studio, adapted to this machine and my active
Git repository. It must create and edit native .excalidraw files, validate scene
structure and arrow bindings, inspect layout defects, render local SVG and PNG
previews, and visually review the PNG before finishing. Keep every write inside the
Git root; refuse accidental overwrites; preserve stable element IDs during edits;
and keep the editable .excalidraw file as the canonical artifact. Use a local stdio
MCP server plus a dependency-free Python CLI fallback. Do not require Excalidraw+,
an Excalidraw account, npm, an API key, cloud storage, uploads, or share links. Add a
personal marketplace entry, validate the manifest and skill, and forward-test the
complete create → validate → render → inspect → adjust loop in a temporary Git repo.
```

## Use

Ask for the result, not the implementation details:

```text
Use Excalidraw Studio to create a deployment architecture diagram in
docs/diagrams/deployment.excalidraw. Render it locally, inspect the PNG, and make up
to three small layout improvements before returning the source and preview paths.
```

You can also invoke the bundled skill explicitly as `$excalidraw-studio`.

### CLI fallback

If MCP tools are unavailable, the same workflow is available through the bundled CLI:

```bash
python plugins/excalidraw-studio/scripts/excalidraw_studio.py doctor --workspace .
python plugins/excalidraw-studio/scripts/excalidraw_studio.py create \
  --workspace . \
  --output docs/diagrams/example.excalidraw \
  --spec examples/local-workflow-spec.json
python plugins/excalidraw-studio/scripts/excalidraw_studio.py validate \
  --workspace . --file docs/diagrams/example.excalidraw
python plugins/excalidraw-studio/scripts/excalidraw_studio.py inspect \
  --workspace . --file docs/diagrams/example.excalidraw
```

On PowerShell, use backticks or place the command on one line instead of the Bash line continuations shown above.

## How it works

| Layer | Responsibility |
| --- | --- |
| Skill | Teaches Codex the design system, local-only guardrails, and visual iteration loop. |
| MCP server | Exposes structured tools over local stdio; it does not open a network port. |
| Python CLI | Implements deterministic scene compilation, validation, inspection, and rendering. |
| Git repository | Owns the editable source and previews; paths outside the repo are rejected. |
| Excalidraw | Opens the resulting `.excalidraw` file in the free editor for manual refinement. |

The renderer creates SVG directly from the scene. On Windows it can use the system Microsoft Edge executable in headless mode to capture a PNG. The preview is intentionally lightweight; the `.excalidraw` scene remains the canonical artifact and the free Excalidraw editor remains the final-fidelity view.

## Local-first by design

- No Excalidraw account or paid tier.
- No API key, npm install, background daemon, or hosted service.
- No upload, cloud storage, telemetry, or share-link creation.
- Writes are resolved against `git rev-parse --show-toplevel` and rejected if they escape that root.
- Existing diagrams are protected unless overwrite is explicitly requested.
- The MCP server communicates over stdio and uses only the Python standard library.

Review any third-party plugin before installing it. Codex sandbox and approval policies still apply when a plugin tool runs.

## Requirements

- Codex or the ChatGPT desktop app with plugin support.
- Git available on `PATH`.
- Python 3.10 or newer available as `python`.
- Microsoft Edge is optional and used only for PNG previews; SVG rendering works without it.
- A free Excalidraw editor, such as [excalidraw.com](https://excalidraw.com/), to open and manually refine the source file.

## Repository layout

```text
.agents/plugins/marketplace.json             Public marketplace catalog
plugins/excalidraw-studio/.codex-plugin/     Plugin manifest
plugins/excalidraw-studio/skills/            Codex workflow and design references
plugins/excalidraw-studio/mcp/                Local stdio MCP server
plugins/excalidraw-studio/scripts/            Dependency-free Python implementation
plugins/excalidraw-studio/assets/preview.png  English workflow illustration
examples/local-workflow-spec.json             Editable example input
examples/local-workflow.excalidraw             Generated editable example
```

## Development and verification

From the repository root:

```bash
python -m py_compile \
  plugins/excalidraw-studio/scripts/excalidraw_studio.py \
  plugins/excalidraw-studio/mcp/server.py
python plugins/excalidraw-studio/scripts/excalidraw_studio.py doctor --workspace .
```

A meaningful smoke test creates a diagram from `examples/local-workflow-spec.json`, validates and inspects it, renders both previews, and opens the `.excalidraw` source in the free editor.

## Status and limitations

This is an early public release. The compact compiler currently supports rectangles, ellipses, diamonds, free-standing text, straight or elbow arrows, semantic colors, and solid/dashed/dotted strokes. It is not a full replacement for the Excalidraw UI or renderer.

Excalidraw Studio is an independent community project and is not affiliated with or endorsed by Excalidraw or OpenAI.

## License

[MIT](LICENSE) © 2026 Hector Touza.
