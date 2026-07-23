# Design system

## Layout first

Choose the visual metaphor from the relationship:

- Input to transform to output: left-to-right pipeline.
- One to many: fan-out from a clear source.
- Many to one: convergence into the result.
- Parent and children: tree with free-standing labels.
- Repeating feedback: cycle with a distinct return path.
- Comparison: two aligned columns with shared baselines.
- Phases: whitespace or a restrained dashed divider.

Use a 24 px base grid. Leave 100-120 px between unlabeled connected components and 150-200 px
when an arrow carries a label. Reserve at least 48 px inside zones.

## Hierarchy

- Diagram title: 28 px.
- Section header: 24 px.
- Component label: 20 px.
- Description: 16 px.
- Note: 14 px.

Keep roughly 60% whitespace, 30% primary structure, and 10% highlight. Aim for fewer than one
third of text elements inside boxes. Use boxes for real components, decisions, start/end states,
or meaningful zones.

## Semantic palette

| Meaning | Fill | Stroke |
| --- | --- | --- |
| Primary/input | `#dbeafe` | `#1e40af` |
| Data/success | `#dcfce7` | `#166534` |
| Decision/warning | `#fef9c3` | `#854d0e` |
| Critical/error | `#fee2e2` | `#991b1b` |
| External/storage | `#f3e8ff` | `#6b21a8` |
| Process | `#e0f2fe` | `#0369a1` |
| Trigger/start | `#fed7aa` | `#c2410c` |
| Neutral/zone | `#f1f5f9` | `#475569` |

Use solid arrows for the main flow, dashed arrows for responses or asynchronous work, and dotted
arrows for optional or weak dependencies. Label only when the relationship is not obvious.

## Review checklist

- One obvious reading direction.
- No clipped labels or overlapping nodes.
- Arrows terminate at component edges and do not cross unrelated components.
- Title and primary path remain legible at fit-to-screen scale.
- Color conveys meaning rather than decoration.
- No large uniform card grid unless the subject truly is a grid.
- Preview and editable source both exist inside the repository.
