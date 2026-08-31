# Design Checklist for Codex

[![License: MIT](https://img.shields.io/badge/License-MIT-0f766e.svg)](LICENSE)
[![Codex skill](https://img.shields.io/badge/Codex-skill-2563eb.svg)](skills/design-checklist/SKILL.md)

Design Checklist is a Codex plugin that acts as a design-development partner and evidence-led QA gate. It turns a product outcome into a falsifiable design hypothesis, chooses between repair, restructure, and redesign, accompanies implementation through rendered checkpoints, and verifies whether the result creates a material improvement.

The workflow is inspired by [Checklist Design](https://www.checklist.design/), created by George Hatzis. The plugin links to the live source pages and contains an original synthesis; it does not mirror the source catalog.

## What it does

- Defines the user task, five-second takeaway, actions, constraints, and success evidence before code.
- Selects repair, restructure, or redesign instead of defaulting to polish.
- Requires a concrete design direction and falsifiable hypothesis for structural work.
- Reviews the first viewport, interactions, consequential states, responsive behavior, and release candidate during development.
- Uses `pass`, `risk`, `fail`, and `not observed` evidence instead of unsupported claims.
- Rejects redesign experiments that only change spacing, type size, borders, or decoration.
- Creates honest before/after experiments with matched data and materially distinct presentation trees.

## Install

Add Codex Toolbox, then install Design Checklist:

```bash
codex plugin marketplace add Hector-Touza/codex-toolbox --ref main
codex plugin add design-checklist@codex-toolbox
```

## Use

Invoke the bundled skill explicitly as `$design-checklist`:

```text
Use $design-checklist as a development partner for this operations product. Define a falsifiable redesign hypothesis, guide the build through its quality gates, and launch an honest before/after experiment only if the difference is material.
```

The skill also supports bounded audits and repairs. It chooses the intervention level from the user outcome and evidence rather than treating every request as a redesign.

Rendered access is important. If the interface cannot be exercised or captured, the skill must leave the affected gates as `not observed`.

## Source and limitations

- Checklist Design remains the authoritative source for its current checklists.
- This plugin is independent and is not affiliated with or endorsed by Checklist Design.
- The workflow provides product-design guidance, not formal accessibility certification.

## License

[MIT](LICENSE) © 2026 Hector Touza.
