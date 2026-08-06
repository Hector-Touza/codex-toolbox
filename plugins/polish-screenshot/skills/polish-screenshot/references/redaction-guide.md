# Redaction guide

## Scope and iteration

1. Follow the user's explicit instructions about what must remain visible and what must be hidden.
2. When the request is ambiguous, propose the intended regions before editing. Infer all sensitive areas only when the user asks for that broader judgment.
3. Open the source at original resolution and list the exact content to protect.
4. Render `guide` to a temporary working file and use its coordinates to choose rectangles.
5. Include the complete text or control plus 6–12 pixels of context. Prefer a slightly generous region over an exact text baseline.
6. Render `redact` to a new file. Never overwrite the source.
7. Open the result at original resolution. Check every edge and ask whether a viewer can still infer the protected value from visible characters, shape, length, or surrounding context.
8. Increase region size or strength and render again when any protected content remains recognizable.
9. Compose the polished image only after the 1:1 redacted preview passes inspection. Inspect the final composition once more because scaling can change how redaction reads.

## Style choice

- `blur`: Preserve a natural screenshot appearance for names, conversation titles, secondary copy, or contextual details. Start with strength 24, padding 8, and feather 3 on a roughly 1900-pixel-wide capture.
- `pixelate`: Prefer for values that should not be read but may retain a familiar UI texture. Use a strong block size and verify that character shapes are gone.
- `solid`: Prefer for passwords, tokens, account numbers, vehicle identifiers, personal addresses, or regulated information. Use feather 0 for a hard, unambiguous mask.

Blur is visual obfuscation and can leak structure. Do not describe it as secure deletion. When consequences of disclosure are meaningful, choose `solid` or remove the sensitive content before capture.

## Quality checks

- Cover labels, icons, tooltips, reflections, and repeated values that reveal the same information.
- Keep masks aligned with the interface geometry.
- Avoid tiny isolated blur patches when one coherent region looks more intentional.
- Preserve unaffected pixels exactly; do not regenerate, repaint, or reconstruct the interface.
- Keep guide files and rejected previews in temporary work storage, not beside the final deliverable.
