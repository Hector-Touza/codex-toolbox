---
name: excalidraw-studio
description: Create, edit, validate, render, and visually refine editable Excalidraw diagrams stored locally inside the active Git repository. Use when Codex needs architecture diagrams, flowcharts, system maps, sequence-like flows, decision diagrams, or improvements to an existing .excalidraw file while preserving a free/local-only workflow with no Excalidraw+ dependency, cloud upload, or share link.
---

# Excalidraw Studio

Keep the editable `.excalidraw` source inside the active Git repository. Default to
`docs/diagrams/<slug>.excalidraw`. Never upload the scene or create a share link unless the user
explicitly changes the local-only requirement.

## Workflow

1. Resolve the repository root with `git rev-parse --show-toplevel`.
2. Read `references/design-system.md` before creating or materially redesigning a scene.
3. Use `create_excalidraw_diagram` with a compact spec from `references/spec-format.md`, or make a
   minimal edit to an existing `.excalidraw` file.
4. Run `validate_excalidraw_diagram`, then `inspect_excalidraw_diagram`.
5. Run `render_excalidraw_preview`. Inspect the PNG with the local image viewer.
6. Fix clipping, overlap, weak hierarchy, ambiguous arrows, or excessive containers. Repeat the
   inspect/render loop up to three times unless the user asks for more.
7. Return the repo-relative paths to the `.excalidraw` source and previews. Treat the source file,
   not the preview, as the canonical artifact.

If MCP tools are unavailable, infer `<plugin-root>` as two directories above this skill folder
(`.../skills/excalidraw-studio` -> plugin root), then use the bundled CLI:

```powershell
python <plugin-root>\scripts\excalidraw_studio.py doctor --workspace <repo>
python <plugin-root>\scripts\excalidraw_studio.py create --workspace <repo> --output docs/diagrams/name.excalidraw --spec <repo-spec.json>
python <plugin-root>\scripts\excalidraw_studio.py inspect --workspace <repo> --file docs/diagrams/name.excalidraw
python <plugin-root>\scripts\excalidraw_studio.py render --workspace <repo> --file docs/diagrams/name.excalidraw
```

## Guardrails

- Require every write target to remain inside the resolved Git repository.
- Do not overwrite an existing diagram unless the user requested an update or `overwrite=true` is
  intentionally supplied.
- Do not require an Excalidraw account, API key, paid tier, npm, or a background daemon.
- Prefer free-standing text and whitespace over a box around every idea.
- Keep predictions, assumptions, and unverified relationships visibly qualified in the diagram.
- Preserve existing element IDs when editing so diffs remain intelligible.
