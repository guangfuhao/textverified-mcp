# TextVerified Plugin

[中文 README](README.md) · [GitHub](https://github.com/guangfuhao/textverified-mcp) · [TextVerified API v2 docs](https://app.textverified.com/docs/api/v2#overview)

`textverified-mcp` is an installable TextVerified plugin for Codex, ChatGPT, and other compatible agents. It covers the complete TextVerified API v2 and provides focused SMS and voice verification workflows.

## Install in one sentence

Send this sentence to an Agent that supports plugins:

> Install the TextVerified plugin from https://github.com/guangfuhao/textverified-mcp, then open its plugin settings page so I can enter my TextVerified username and API key.

Codex CLI users can also install it from a personal or repository marketplace:

```bash
codex plugin marketplace add https://github.com/guangfuhao/textverified-mcp
codex plugin add textverified-mcp
```

Marketplace commands differ between Agent products; the one-sentence request lets the Agent select the installation method it supports.

## First-run configuration

After installation, the `textverified-setup` onboarding skill guides the user through configuring:

- **TextVerified username**: the registration email for the TextVerified account;
- **TextVerified API key**: the primary TextVerified API key;
- **API base URL**: defaults to `https://www.textverified.com`.

After saving, the plugin stores the credentials in the current user's local configuration with owner-only permissions (`0600`). The API key is always masked when settings are read and is never written to GitHub, README files, chat messages, or tool arguments. CI and headless environments without a settings page can use `TEXTVERIFIED_USERNAME` and `TEXTVERIFIED_API_KEY` environment variables.

On hosts that support OpenAI MCP Extensions, the settings page is rendered natively through the `openai/settings` capability. The current Codex local-plugin details page may show skills without rendering that native form; in that case, the onboarding skill calls `textverified_setup_local`, which opens a one-shot localhost form and shuts down after saving. CI/headless environments that cannot open the local form can use environment variables or a secret store.

## Capabilities

- `textverified_request`: call every documented `/api/pub/v2/*` API v2 endpoint;
- create and inspect SMS or voice verifications;
- list and send SMS;
- list calls and create an incoming-call access token;
- create rentals;
- access services, prices, inventory, billing, backorders, wake requests, webhook definitions, and pagination links.

The complete OpenAPI contract is [`docs/api-v2.openapi.json`](docs/api-v2.openapi.json), and the endpoint manifest is [`docs/endpoints.md`](docs/endpoints.md).

## Safety behavior

Purchases, refunds, renewals, replies, SMS sends, extensions, and other write operations can spend credits or change account state. Focused write tools require an explicit confirmation parameter, and the generic API tool should only be used when the request is understood. Prefer the documented `test_*` mock service names for integration tests.

The client caches short-lived bearer tokens, retries temporary network, 429, and 5xx failures with bounded backoff, supports `Idempotency-Key`, and restricts requests to TextVerified API v2 hosts.

## Local development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
pytest -q
```

Tests use a local mock transport and never call TextVerified or purchase a number.

## Project files

- `plugin.json`: portable Agent Plugins manifest;
- `mcp.json`: bundled stdio MCP server configuration;
- `.agents/plugins/marketplace.json`: marketplace catalog for GitHub discovery and installation;
- `skills/setup/SKILL.md`: first-install configuration onboarding;
- `skills/textverified-usage/SKILL.md`: usage and safety rules;
- `docs/api-v2.openapi.json`: official API v2 OpenAPI snapshot;
- `src/textverified_mcp/`: Python client and MCP server.

## License

MIT. This is an independent community client. TextVerified is a trademark of its respective owner and does not endorse this project.
