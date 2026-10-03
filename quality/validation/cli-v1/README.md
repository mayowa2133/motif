# Desktop CLI adoption

Motif now prefers the desktop-bundled Codex executable before PATH. On this host it selected:

- `/Applications/ChatGPT.app/Contents/Resources/codex-cli/CodexCLI.app/Contents/MacOS/codex`
- `codex-cli 0.159.0-alpha.12.1`
- Configured model: `gpt-6.1-sol`

`backend_config()` uses that executable for login status and version. `model_call()` uses the recorded executable for execution; it cannot silently return to the older PATH binary if that executable disappears. An explicit `MOTIF_CODEX_CLI` file overrides discovery. Invalid overrides fail. PATH remains a recorded option for hosts without the desktop bundle. Model/provider/authentication configuration is preserved.

## Verification

[results.json](results.json) records the actual path/version/model, live response and invocation hashes, and preservation checks. [verified/](verified/) contains a new authenticated data-only structure review of the existing valid Bot-absent planning fixture. All required structural checks passed through Motif's shared `model_call()` path with the configured GPT-6.1 Sol model. No new film, render, audio or assets were produced.

[77 Python regressions](regression-tests.txt) passed, including five CLI tests covering preference over an older PATH executable, invalid explicit overrides, portable PATH discovery, matching login/version/exec binaries, relative output paths and unavailable recorded binaries.

The initial [relative-project attempt](failed-relative-project/) is preserved. Its CLI invocation accepted the model, but the adapter supplied a relative output path while running in an empty temporary directory; the response file was unavailable after that directory was removed. `model_call()` now resolves the project path before constructing outputs. The new verified call used absolute paths and passed; no saved response was substituted.

All 540 frozen benchmark/canonical files and all 1,940 rejected-rowhouse files remain unchanged. Previous structural validation evidence is historical and unchanged, including its explicit GPT-5.6 selection when the older terminal CLI rejected GPT-6.1.

No provider, authentication, global Codex configuration or dependency update was made. These verification results were recorded before committing the CLI integration.
