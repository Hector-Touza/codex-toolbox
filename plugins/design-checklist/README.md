# Design Checklist for Codex

[![License: MIT](https://img.shields.io/badge/License-MIT-0f766e.svg)](LICENSE)
[![Codex skill](https://img.shields.io/badge/Codex-skill-2563eb.svg)](skills/design-checklist/SKILL.md)

Design Checklist is a Codex plugin for evidence-led UX/UI review and restrained implementation polish. It selects the smallest useful set of design lenses for the product at hand, grounds findings in rendered evidence, and verifies the result across interaction states and responsive layouts.

The workflow is inspired by [Checklist Design](https://www.checklist.design/), created by George Hatzis. The plugin links to the live source pages and contains an original review synthesis; it does not mirror the source catalog.

## What it does

- Starts from the product's existing design system and user task.
- Routes to focused checklists for surfaces, components, and flows.
- Separates observed passes, risks, failures, and unverified states.
- Implements a compact polish pass instead of a speculative redesign.
- Checks hierarchy, tokens, states, accessibility, tables, filters, and responsive behavior.
- Creates honest before/after controls with matched data and viewports.

## Install

Add Codex Toolbox, then install Design Checklist:

```bash
codex plugin marketplace add Hector-Touza/codex-toolbox --ref main
codex plugin add design-checklist@codex-toolbox
```

## Use

Invoke the bundled skill explicitly as `$design-checklist`, or ask Codex to review and polish an existing product interface:

```text
Use $design-checklist to audit this operations dashboard, implement the highest-impact improvements, and leave an honest before/after comparison.
```

Rendered access is important. If the interface cannot be captured, the skill can still run structural and automated checks, but it must report visual QA as incomplete.

## Source and limitations

- Checklist Design remains the authoritative source for its current checklists.
- This plugin is independent and is not affiliated with or endorsed by Checklist Design.
- The workflow provides product-design guidance, not formal accessibility certification.

## License

[MIT](LICENSE) © 2026 Hector Touza.
