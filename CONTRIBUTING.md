# Contributing

Keep every plugin self-contained under `plugins/<plugin-name>/`.

A plugin must include:

- `.codex-plugin/plugin.json`;
- a nested `README.md`;
- its required skills, MCP configuration, scripts, assets, and examples;
- a license file;
- one matching entry in `.agents/plugins/marketplace.json`.

Use relative paths inside plugin manifests and documentation. Do not make one plugin depend on files from another plugin.

Before publication:

1. Validate the plugin manifest and each skill.
2. Run focused checks for executable code.
3. Test the plugin from a clean clone.
4. Confirm that the marketplace source path resolves to the plugin directory.
5. Update the root catalog and the plugin README.

Use short documentation. State requirements and limitations. Do not claim checks that you did not run.
