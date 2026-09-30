---
name: textverified-setup
description: Configure TextVerified credentials after the plugin is installed.
---

# TextVerified setup

Run this onboarding skill immediately after installation, before attempting an
account read or any SMS/voice operation.

1. If the host exposes a **TextVerified plugin settings page**, open it and
   enter the user's TextVerified registration email and primary API key there.
2. If the host only shows the plugin's skills (as current Codex local-plugin
   details may), call `textverified_setup_local` with `open_browser=true`.
   This starts a one-shot localhost form in the user's browser. Tell the user
   to enter the credentials there; after saving, the local service exits by
   itself. Do not claim that a settings page was opened when it was not.
3. Keep the default API base URL unless the user explicitly provides another
   TextVerified v2 host, then save the settings.
4. Confirm setup by performing a read-only account request. Never include the
   username or API key in a prompt, tool argument, log, response, repository,
   or Git commit.

If the host cannot run the local setup tool, tell the user to set
`TEXTVERIFIED_USERNAME` and `TEXTVERIFIED_API_KEY` in the host's secure
environment and retry. Do not ask the user to paste credentials into a normal
conversation message.
