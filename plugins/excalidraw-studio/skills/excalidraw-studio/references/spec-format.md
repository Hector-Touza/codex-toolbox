# Compact scene specification

Pass this structure to `create_excalidraw_diagram` or save it as JSON for the CLI `create` command.
Coordinates use Excalidraw canvas pixels.

```json
{
  "title": "Local delivery workflow",
  "roughness": 1,
  "nodes": [
    {
      "id": "repo",
      "type": "rectangle",
      "x": 80,
      "y": 140,
      "width": 240,
      "height": 96,
      "label": "Git repository",
      "semantic": "primary"
    },
    {
      "id": "review",
      "type": "rectangle",
      "x": 520,
      "y": 140,
      "width": 240,
      "height": 96,
      "label": "Visual review",
      "semantic": "success"
    }
  ],
  "edges": [
    {
      "id": "repo-to-review",
      "from": "repo",
      "to": "review",
      "label": "local file",
      "style": "solid",
      "route": "straight"
    }
  ]
}
```

Supported node types: `rectangle`, `ellipse`, `diamond`, and `text`. Supported semantic names:
`primary`, `success`, `warning`, `error`, `external`, `process`, `trigger`, and `neutral`.
Supported edge styles: `solid`, `dashed`, `dotted`. Supported routes: `straight`, `elbow`.

Use stable, descriptive IDs containing letters, digits, hyphens, or underscores. Insert explicit
newlines in labels when a deliberate line break improves scanning; otherwise the compiler wraps
labels to fit.
