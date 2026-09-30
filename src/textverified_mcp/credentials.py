from __future__ import annotations

"""Local credential storage for the TextVerified plugin.

The plugin settings page writes this file with owner-only permissions. Values
are never returned by the MCP tools; the API key is represented by a mask.
Environment variables still take precedence so CI and ephemeral sessions do
not need to write credentials to disk.
"""

import json
import os
from pathlib import Path
from typing import Any


MASKED_API_KEY = "••••••••"


def _config_path() -> Path:
    configured = os.getenv("TEXTVERIFIED_CONFIG_FILE", "").strip()
    if configured:
        return Path(configured).expanduser()
    return Path.home() / ".config" / "textverified-mcp" / "credentials.json"


def load_stored_credentials() -> dict[str, str]:
    path = _config_path()
    try:
        raw: Any = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, ValueError):
        return {}
    if not isinstance(raw, dict):
        return {}
    result: dict[str, str] = {}
    for field in ("username", "api_key", "base_url"):
        value = raw.get(field)
        if isinstance(value, str) and value.strip():
            result[field] = value.strip()
    return result


def save_credentials(*, username: str | None = None, api_key: str | None = None, base_url: str | None = None) -> dict[str, str]:
    """Merge and save settings, returning only non-secret metadata."""

    current = load_stored_credentials()
    for field, value in (("username", username), ("api_key", api_key), ("base_url", base_url)):
        if value is not None and value.strip() and value != MASKED_API_KEY:
            current[field] = value.strip()
    if not current.get("username") or not current.get("api_key"):
        raise ValueError("Both username and api_key are required before saving TextVerified settings")

    path = _config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(current, indent=2) + "\n", encoding="utf-8")
    try:
        path.chmod(0o600)
    except OSError:
        pass
    return {"username": current["username"], "base_url": current.get("base_url", "")}


def effective_credentials() -> dict[str, str]:
    """Return environment-first credentials for the API client."""

    stored = load_stored_credentials()
    return {
        "username": os.getenv("TEXTVERIFIED_USERNAME", "").strip() or stored.get("username", ""),
        "api_key": os.getenv("TEXTVERIFIED_API_KEY", "").strip() or stored.get("api_key", ""),
        "base_url": os.getenv("TEXTVERIFIED_BASE_URL", "").strip() or stored.get("base_url", ""),
    }


def settings_snapshot() -> dict[str, Any]:
    effective = effective_credentials()
    return {
        "username": effective["username"],
        "api_key": MASKED_API_KEY if effective["api_key"] else "",
        "base_url": effective["base_url"] or "https://www.textverified.com",
        "api_key_configured": bool(effective["api_key"]),
    }
