# Distilled review lenses

Use these lenses to structure evidence. They are an original synthesis, not a copy of Checklist Design.

## Product and decision clarity

- Is the primary user, task, current state, and next decision obvious?
- Does the first viewport prioritize what needs attention over descriptive decoration?
- Can the user tell what changed, what is running, what failed, and what requires action?
- Are auditability, provenance, freshness, and permission boundaries visible where they affect trust?

## Information architecture

- Are groups based on user decisions and workflow rather than data-source shape?
- Are overview, exception, investigation, and action layers distinct?
- Does navigation expose the important path without advertising every feature?
- Does the narrow layout preserve task priority rather than merely stack desktop sections?

## Hierarchy and composition

- Do typography, placement, scale, and whitespace establish a clear reading order?
- Are headings, labels, body copy, metadata, and numeric emphasis visibly distinct?
- Is density intentional for the task, with decoration subordinate to signal?
- Does hierarchy survive narrow screens and 200% zoom?

## Interaction model

- Does action copy predict its result?
- Are primary and supporting actions proportionate and placed near their consequences?
- Are hover, focus, pressed, loading, disabled, selected, success, and error states distinct where relevant?
- Are empty, no-results, load-error, permission-denied, and in-progress states recoverable?

## Visual system

- Do spacing, type, color, radius, border, and elevation roles form a coherent system?
- Are colors semantic and every status understandable without color alone?
- Are components reused because they serve the direction, not because they already exist?
- Does the result retain product character without relying on generic dashboard conventions?

## Tables and collections

- Do headers preserve context during scroll?
- Are search, filters, sort, counts, and row actions discoverable and keyboard-safe?
- Are applied filters and reset paths clear?
- Is narrow behavior deliberate: prioritized fields, stacked records, drill-down, or labeled overflow?

## Implementation fidelity

- Does the rendered first viewport still express the design hypothesis?
- Did technical reuse dilute the selected information architecture or composition?
- Do realistic data and long labels preserve the intended layout?
- Are responsive and interaction states designed rather than patched after the happy path?

## Experiment integrity

- Do before and after use the same route, data, viewport, filters, and state?
- Is the active version programmatically identifiable?
- Does the experiment change at least three structural axes?
- Is the improvement understandable in five seconds and describable without CSS adjectives?
