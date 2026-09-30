from __future__ import annotations

from datetime import datetime, timezone

import httpx
import pytest

from textverified_mcp.client import TextVerifiedClient, TextVerifiedError


def test_token_is_cached_and_sms_request_uses_bearer() -> None:
    calls: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        if request.url.path == "/api/pub/v2/auth":
            assert request.headers["X-API-USERNAME"] == "user@example.com"
            assert request.headers["X-API-KEY"] == "secret"
            return httpx.Response(200, json={"token": "token-1", "expiresIn": 900, "expiresAt": "2099-01-01T00:00:00+00:00"})
        assert request.headers["Authorization"] == "Bearer token-1"
        assert request.url.path == "/api/pub/v2/sms"
        assert request.url.params["reservationId"] == "mock_ver_success"
        return httpx.Response(200, json={"data": [], "count": 0, "hasNext": False, "hasPrevious": False, "links": {}})

    with TextVerifiedClient("user@example.com", "secret", transport=httpx.MockTransport(handler)) as client:
        assert client.list_sms(reservation_id="mock_ver_success")["count"] == 0
        assert client.list_sms(reservation_id="mock_ver_success")["count"] == 0
    assert [request.url.path for request in calls].count("/api/pub/v2/auth") == 1


def test_iso_expiry_and_auth_refresh() -> None:
    token_count = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal token_count
        if request.url.path == "/api/pub/v2/auth":
            token_count += 1
            return httpx.Response(200, json={"token": f"token-{token_count}", "expiresIn": 900, "expiresAt": "2099-01-01T00:00:00+00:00"})
        if request.headers.get("Authorization") == "Bearer token-1":
            return httpx.Response(401)
        return httpx.Response(200, json={"ok": True})

    with TextVerifiedClient("u", "k", transport=httpx.MockTransport(handler)) as client:
        assert client.request("GET", "/api/pub/v2/account/me")["ok"] is True
    assert token_count == 2


def test_blocks_external_paths() -> None:
    with TextVerifiedClient("u", "k", transport=httpx.MockTransport(lambda _: httpx.Response(200))) as client:
        with pytest.raises(TextVerifiedError):
            client.request("GET", "https://evil.example/api/pub/v2/account/me")
