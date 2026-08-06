# Codex Toolbox

[![License: MIT](https://img.shields.io/badge/License-MIT-0f766e.svg)](LICENSE)
[![Codex plugins](https://img.shields.io/badge/Codex-plugins-2563eb.svg)](.agents/plugins/marketplace.json)

Codex Toolbox is a public collection of small Codex plugins, skills, and local tools.

Each plugin is self-contained. It has its own manifest, documentation, assets, examples, and license.

## Plugins

| Plugin | What it does | Package |
| --- | --- | --- |
| [Excalidraw Studio](plugins/excalidraw-studio/README.md) | Creates editable `.excalidraw` files, validates them, renders local SVG and PNG previews, and inspects the output before refinement. | Skill + local MCP server + Python CLI |
| [App QA](plugins/app-qa/README.md) | Reviews an app with three independent critics, consolidates findings, guides rework, and records the result in `app-qa-findings.md`. | Skill |
| [Polish Screenshot](plugins/polish-screenshot/README.md) | Redacts selected regions without image generation, visually verifies the result, and turns raw window captures into publication-ready compositions. | Skill + Python CLI |

## Install

Add this repository as a Codex plugin marketplace:

```bash
codex plugin marketplace add Hector-Touza/codex-toolbox --ref main
```

Then install the plugins you need:

```bash
codex plugin add excalidraw-studio@codex-toolbox
codex plugin add app-qa@codex-toolbox
codex plugin add polish-screenshot@codex-toolbox
```

You can also ask Codex to do this for you:

```text
Add https://github.com/Hector-Touza/codex-toolbox as a Codex plugin marketplace.
Install the plugins I select. Preserve my existing marketplaces. Verify each
installed plugin in a fresh task when required.
```

The plugins are not in the official OpenAI Plugins Directory. Review third-party plugin code before installation.

## Repository layout

```text
.agents/plugins/marketplace.json  Marketplace catalog
plugins/excalidraw-studio/        Excalidraw Studio plugin
plugins/app-qa/                   App QA plugin
plugins/polish-screenshot/        Polish Screenshot plugin
```

The repository can later include more self-contained plugins under `plugins/`. Standalone skills or MCP servers can use top-level folders when they are not part of a plugin.

## Contribute

See [CONTRIBUTING.md](CONTRIBUTING.md) for the package layout and validation requirements.

## License

[MIT](LICENSE) © 2026 Hector Touza.
