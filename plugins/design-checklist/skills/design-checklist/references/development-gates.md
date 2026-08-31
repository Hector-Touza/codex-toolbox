# Development and experiment gates

Use this reference for new builds, redesigns, or implementation work. Keep the record compact and update it as evidence changes.

## Design contract template

```md
Surface:
Primary user:
Primary task or decision:
Five-second takeaway:
Primary action:
Supporting actions:
Viewports:
Consequential states:
Constraints:
Hypothesis:
Success evidence:
Intervention: repair | restructure | redesign
```

## Gate record

| Gate | Question | Evidence | Status |
| --- | --- | --- | --- |
| Contract | Does the concept directly serve the hypothesis? | Brief or selected visual | pass/risk/fail/not observed |
| First viewport | Is the main task clear with realistic data? | Rendered desktop view | pass/risk/fail/not observed |
| Interaction | Do core actions and consequential states work? | Exercised states | pass/risk/fail/not observed |
| Responsive | Is the narrow experience deliberately recomposed? | Matched narrow render | pass/risk/fail/not observed |
| Release | Does the build satisfy the contract without regressions? | Comparison plus checks | pass/risk/fail/not observed |

## Materiality scorecard

For a redesign experiment, mark each changed axis with one concrete sentence:

| Axis | Before | After | Material change? |
| --- | --- | --- | --- |
| Information architecture | | | yes/no |
| Composition and hierarchy | | | yes/no |
| Primary interaction model | | | yes/no |
| Narrow-screen behavior | | | yes/no |
| Visual system and density | | | yes/no |

Require at least three `yes` results. Then run the five-second test: show matched captures without explanation and ask what changed and what the screen is for. If the answer depends on pointing out spacing, borders, shadows, or small type adjustments, the experiment is not material.

## Stop conditions

Pause implementation and revise the direction when:

- the primary task is still unclear after the first viewport renders;
- the new structure cannot be distinguished from the legacy structure;
- realistic data breaks hierarchy or responsive behavior;
- a core state is missing or indistinguishable;
- accessibility or product-truth constraints are being traded for novelty;
- automated checks pass but rendered evidence contradicts the hypothesis.

Passing the release gate requires both functional correctness and visible support for the hypothesis.
