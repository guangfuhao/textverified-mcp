---
name: textverified-setup
description: Configure TextVerified credentials after the plugin is installed.
---

# TextVerified setup

Run this onboarding skill immediately after installation, before attempting an
account read or any SMS/voice operation.

1. Open the **TextVerified plugin settings page** from the installed plugin's
   details/settings view.
2. Enter the user's TextVerified registration email in **TextVerified
   username**.
3. Enter the user's primary TextVerified API key in **TextVerified API key**.
4. Keep the default API base URL unless the user explicitly provides another
   TextVerified v2 host, then save the settings.
5. Confirm setup by performing a read-only account request. Never include the
   username or API key in a prompt, tool argument, log, response, repository,
   or Git commit.

If the host does not expose a native settings page, tell the user to set
`TEXTVERIFIED_USERNAME` and `TEXTVERIFIED_API_KEY` in the host's secure
environment and retry. Do not ask the user to paste credentials into a normal
conversation message.
