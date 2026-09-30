from __future__ import annotations

import json

from textverified_mcp.server import textverified_settings_read, textverified_settings_update


def test_settings_round_trip_masks_api_key_and_restricts_file(monkeypatch, tmp_path):
    config_file = tmp_path / "credentials.json"
    monkeypatch.setenv("TEXTVERIFIED_CONFIG_FILE", str(config_file))
    monkeypatch.delenv("TEXTVERIFIED_USERNAME", raising=False)
    monkeypatch.delenv("TEXTVERIFIED_API_KEY", raising=False)
    monkeypatch.delenv("TEXTVERIFIED_BASE_URL", raising=False)

    updated = textverified_settings_update({"username": "demo@example.com", "api_key": "local-test-key"})
    assert updated.values["username"] == "demo@example.com"
    assert updated.values["api_key"] == "••••••••"

    read = textverified_settings_read()
    assert read.values["api_key"] == "••••••••"
    assert "local-test-key" not in json.dumps(read.model_dump(by_alias=True))
    assert config_file.stat().st_mode & 0o777 == 0o600

