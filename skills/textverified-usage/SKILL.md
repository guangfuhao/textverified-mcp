---
name: textverified-usage
description: Use the TextVerified plugin for account reads, service discovery, SMS and voice verification, rentals, and other documented API v2 operations.
---

Use the TextVerified MCP tools when the user explicitly asks to inspect or operate their TextVerified account.

Authentication is configured from the installed plugin's **TextVerified settings page**. The page stores the username and API key locally with owner-only permissions. Environment variables `TEXTVERIFIED_USERNAME` and `TEXTVERIFIED_API_KEY` are supported as a secure CI/headless fallback. Never ask the user to paste credentials into a normal conversation or tool argument, never print credentials, and never place credentials in repository files.

Prefer read-only account, service, pricing, inventory, verification status, SMS, and call tools for inspection. Before purchases, rentals, sending SMS, refunds, renewals, extensions, replies, or other state changes, explain the operation and use the tool's explicit confirmation parameter. Prefer documented `test_*` mock service names for integration testing.
