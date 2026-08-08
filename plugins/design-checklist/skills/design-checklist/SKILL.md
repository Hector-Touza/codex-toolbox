---
name: design-checklist
description: Audit and polish an existing website, web app, mobile interface, component, or product flow with evidence-led design checklists. Use when Codex needs to review UX/UI quality, prioritize concrete improvements, implement a restrained polish pass, validate responsive and accessible states, or create an honest before/after comparison grounded in Checklist Design and the product's own design system.
---

# Design Checklist

Review the product that exists, select only the checklist lenses that fit its surface, and turn observable gaps into a small, verified polish pass. Preserve product intent and brand character; do not flatten a distinctive interface into generic dashboard styling.

## Read the right references

- Read [references/source-map.md](references/source-map.md) to select current Checklist Design pages for the surface under review.
- Read [references/review-lenses.md](references/review-lenses.md) for the distilled baseline when the source is unavailable or when a compact first pass is enough.
- For a data-heavy operational surface, start with admin panel, table, filtering, empty/loading/error states, typography, spacing, color, and interaction states.
- For a bounded component, load only that component's source page plus the relevant system foundations.

Treat Checklist Design as a third-party reference, not content to reproduce. Paraphrase criteria, link to the original pages, and fetch the smallest relevant set of pages when current web access is available.

## Workflow

### 1. Fix the review frame

State the product surface, primary user task, target viewports, important states, and non-negotiable constraints. Inspect the product's existing tokens, components, nearby screens, and product documentation before proposing changes.

Use the same data, route, viewport, and interaction state for comparisons. Do not manufacture a stronger after-state with friendlier data or a weaker before-state with an error or empty state.

### 2. Capture evidence before judging

Inspect the rendered interface at its normal desktop width and at one representative narrow width. Capture the main task and any loading, empty, error, success, disabled, selected, and focus states that matter.

Record each criterion as one of:

- `pass`: visibly and behaviorally satisfied;
- `risk`: partially satisfied or fragile;
- `fail`: a user-facing gap with evidence;
- `not observed`: cannot be judged from the available state.

Never claim visual, responsive, keyboard, zoom, or assistive-technology verification that did not run.

### 3. Prioritize the polish

Prefer a few changes that improve task comprehension and control:

1. Clarify hierarchy, labels, and next actions.
2. Make loading, empty, error, success, disabled, selected, and focus states distinct.
3. Normalize spacing, type roles, color roles, and interactive states through existing tokens.
4. Improve dense tables, filters, and narrow-layout behavior without hiding essential data.
5. Remove decorative noise only when it competes with the user's task.

Reject attractive changes that weaken brand, provenance, operational accuracy, or information density needed by the target user.

### 4. Implement in the existing system

Reuse present components and tokens. Introduce a new token only when it replaces repeated arbitrary values or expresses a missing semantic role. Keep controls native and semantic where possible, preserve visible focus, respect reduced motion, and pair status color with text or another non-color cue.

For data tables:

- keep column meaning and sort state explicit;
- place search and filters next to the collection they affect;
- expose applied filters and a clear reset path;
- distinguish no data, no results, load failure, and in-progress states;
- choose deliberate narrow-layout behavior: prioritized columns, stacked rows, or labeled horizontal scroll.

### 5. Build honest before/after comparisons

When the user asks for a toggle, comparison, or reveal:

- use a segmented control, tabs, or radio group for `Before` and `After`; do not use an on/off switch for two alternative versions;
- keep both views in the same build and on the same data;
- default to `After`, unless the user asks otherwise;
- announce the selected view programmatically;
- preserve the original version closely enough that the comparison remains credible;
- avoid duplicating application state when a root class or shared presentation mode can switch the visual layer safely.

### 6. Verify and iterate

Re-capture before and after at matching viewports and states. Compare the images together, then check:

- primary task clarity and interaction feedback;
- focus visibility and keyboard order;
- semantic labels and status communication without color alone;
- responsive reflow, horizontal overflow, truncation, and tap targets;
- 200% zoom resilience when practical;
- loading, empty, no-results, error, and success distinctions;
- console errors, broken links, and relevant automated checks.

Fix visible regressions before handoff. If rendered capture is blocked, finish only the checks that remain trustworthy and name visual QA as incomplete.

## Handoff

Lead with the visible result. Report:

- the most consequential improvements;
- the preserved strengths;
- the exact checks completed;
- unresolved risks or unobserved states;
- where the before/after control lives, when included.

Keep the report short. Link to Checklist Design only for the source pages that materially shaped the pass.
