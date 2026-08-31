---
name: design-checklist
description: Act as a design-development partner and evidence-led QA gate for new interfaces, redesigns, existing-product improvements, and before/after experiments. Use when Codex needs to define a product and design hypothesis, choose between repair, restructure, or redesign, guide implementation checkpoints, audit UX/UI and accessibility states, prevent cosmetic-only changes from masquerading as a redesign, or verify that a shipped interface creates a material and observable improvement grounded in Checklist Design and the product's own constraints.
---

# Design Checklist

Turn a user outcome into a design contract, accompany implementation, and verify the rendered result. Do not assume that improvement means polish. Choose the smallest intervention capable of changing the user's experience, and reject a nominal redesign whose difference is only decorative.

## Read the right references

- Read [references/source-map.md](references/source-map.md) to select current Checklist Design pages for the surface.
- Read [references/review-lenses.md](references/review-lenses.md) for the compact evidence baseline.
- Read [references/development-gates.md](references/development-gates.md) for new builds, redesigns, implementation work, or experiments.
- For a bounded audit or repair, load only the relevant surface, flow, and system lenses.

Treat Checklist Design as a third-party reference, not content to reproduce. Paraphrase criteria, link to the original pages, and retrieve the smallest relevant set when current web access is available.

## Workflow

### 1. Establish the design contract

Before code, state:

- the product surface and primary user;
- the task, decision, or outcome the screen must enable;
- what should be understood within five seconds;
- the primary action and one or two supporting actions;
- target viewports and consequential states;
- product, data, brand, accessibility, and technical constraints;
- observable success criteria.

Inspect existing documentation, data contracts, tokens, components, nearby flows, and rendered states. Preserve domain truth and working infrastructure even when replacing the presentation.

### 2. Choose the intervention level

Classify the work explicitly:

- `repair`: fix a bounded usability, state, accessibility, or consistency defect;
- `restructure`: change hierarchy, grouping, responsive behavior, or interaction flow while retaining the visual system;
- `redesign`: establish a new information architecture, composition, interaction model, or visual system because the present approach cannot satisfy the outcome.

Do not default to `repair`. Use `redesign` when the user asks to start over or when structural evidence shows that local fixes cannot create the required outcome. Do not retain legacy layout or styling merely because it already exists.

### 3. Form a falsifiable hypothesis

Write one sentence:

> If we change **[design mechanism]** for **[user/task]**, then **[observable behavior or comprehension]** will improve, evidenced by **[comparison or acceptance check]**.

For a restructure or redesign, establish a concrete visual direction before implementation. Use a selected mock, a source visual, or an explicit system covering hierarchy, layout, typography, color, density, and interaction. Avoid coding from vague adjectives.

For an experiment, require material change across at least three of these axes:

- information architecture;
- page composition and hierarchy;
- primary interaction model;
- narrow-screen behavior;
- visual system and density.

If the proposed delta does not meet that bar, label it a repair or polish pass rather than a redesign experiment.

### 4. Develop through checkpoints

Treat QA as part of development, not a final inspection:

1. **Contract gate:** confirm the screen serves the hypothesis before implementation expands.
2. **First-viewport gate:** render the main task with realistic data; fix hierarchy before secondary details.
3. **Interaction gate:** exercise primary actions plus loading, empty, error, disabled, selected, focus, and success states that matter.
4. **Responsive gate:** verify a representative narrow viewport, content reflow, overflow strategy, touch targets, and zoom resilience.
5. **Release gate:** compare the rendered result against the design contract and run relevant automated checks.

At each gate, record criteria as `pass`, `risk`, `fail`, or `not observed`. Fix failures that invalidate the hypothesis before adding surface polish.

### 5. Implement the chosen system

Keep APIs, authentication, data truth, and working domain behavior stable unless the brief changes them. Reuse existing components and tokens only when they support the selected direction. In redesign mode, replacing presentation components and tokens is allowed; do not let reuse collapse the redesign back into the legacy layout.

Keep controls semantic, preserve visible focus, respect reduced motion, pair status color with text or another cue, and make action feedback specific. Use native interaction patterns unless a custom pattern materially improves the task and remains accessible.

For data-heavy surfaces:

- prioritize decisions and exceptions before aggregate decoration;
- keep column meaning, sort state, provenance, and timestamps explicit;
- place search and filters next to the collection they affect;
- distinguish no data, no results, load failure, and in-progress states;
- choose deliberate narrow behavior: prioritized fields, stacked records, drill-down, or labeled horizontal scroll.

### 6. Run an honest experiment

Keep legacy and experimental interfaces independently credible. Share data and domain logic, but prefer separate presentation trees for a true redesign. A root class that changes spacing, font sizes, and borders is not sufficient evidence of a redesign.

Use the same route, data, viewport, filters, and state for comparisons. Use a segmented control, tabs, or radio group for `Before` and `After`; default to `After`; announce the active view programmatically. Do not weaken the before-state or curate friendlier after-state data.

Apply the materiality test before launch:

- can a viewer identify the changed product idea within five seconds?
- does the primary task or decision become visibly easier?
- can the difference be described in structural terms, not only visual adjectives?
- do mobile and desktop express the same hypothesis appropriately?

If not, mark the experiment failed before release and revise the concept.

### 7. Verify and hand off

Capture matched desktop and narrow views plus consequential states. Compare reference, before, and after together when available. Check focus order, status communication without color, overflow, truncation, tap targets, 200% zoom when practical, console errors, broken links, and relevant automated checks.

Lead the handoff with the hypothesis result. Report the structural changes, preserved constraints, checks completed, unresolved risks, and experiment control location. Do not claim verification that did not run.
