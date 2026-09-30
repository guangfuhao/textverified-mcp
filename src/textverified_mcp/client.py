from __future__ import annotations

import json
import os
import random
import time
from datetime import datetime
from dataclasses import dataclass
from typing import Any, Mapping
from urllib.parse import urljoin, urlparse

import httpx

from .credentials import effective_credentials


class TextVerifiedError(RuntimeError):
    """An error returned by TextVerified or by the client configuration."""

    def __init__(self, message: str, *, status_code: int | None = None, payload: Any = None):
        super().__init__(message)
        self.status_code = status_code
        self.payload = payload


@dataclass
class _Token:
    value: str
    expires_at: float


class TextVerifiedClient:
    """Small, defensive TextVerified API v2 client.

    TextVerified requires both the API username and primary API key to mint a
    bearer token. The key is only read from the constructor/environment and is
    never included in returned tool data or logs.
    """

    def __init__(
        self,
        username: str | None = None,
        api_key: str | None = None,
        *,
        base_url: str | None = None,
        timeout: float = 30.0,
        max_retries: int = 3,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        stored = effective_credentials()
        self.username = (username or stored["username"]).strip()
        self.api_key = (api_key or stored["api_key"]).strip()
        self.base_url = (base_url or stored["base_url"] or "https://www.textverified.com").rstrip("/")
        self.timeout = timeout
        self.max_retries = max(0, max_retries)
        self._token: _Token | None = None
        self._http = httpx.Client(base_url=self.base_url, timeout=timeout, transport=transport)

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> "TextVerifiedClient":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def _require_credentials(self) -> None:
        missing = [name for name, value in (("TEXTVERIFIED_USERNAME", self.username), ("TEXTVERIFIED_API_KEY", self.api_key)) if not value]
        if missing:
            raise TextVerifiedError(f"Missing required configuration: {', '.join(missing)}")

    def _get_token(self, *, force: bool = False) -> str:
        self._require_credentials()
        now = time.time()
        if not force and self._token and self._token.expires_at - now > 60:
            return self._token.value
        response = self._http.post(
            "/api/pub/v2/auth",
            headers={"X-API-USERNAME": self.username, "X-API-KEY": self.api_key, "Accept": "application/json"},
        )
        if response.status_code >= 400:
            raise self._error(response, "Unable to create bearer token")
        try:
            data = response.json()
            token = str(data["token"])
            expires_in = float(data.get("expiresIn", 900))
            raw_expires_at = data.get("expiresAt")
            if isinstance(raw_expires_at, (int, float)):
                expires_at = float(raw_expires_at)
            elif isinstance(raw_expires_at, str):
                try:
                    expires_at = datetime.fromisoformat(raw_expires_at.replace("Z", "+00:00")).timestamp()
                except ValueError:
                    expires_at = now + expires_in
            else:
                expires_at = now + expires_in
        except (ValueError, KeyError, TypeError) as exc:
            raise TextVerifiedError("TextVerified returned an invalid bearer token response") from exc
        self._token = _Token(token, min(expires_at, now + max(60.0, expires_in)))
        return token

    @staticmethod
    def _error(response: httpx.Response, prefix: str = "TextVerified request failed") -> TextVerifiedError:
        try:
            payload: Any = response.json()
        except ValueError:
            payload = response.text[:2000]
        detail = payload.get("errorDescription") if isinstance(payload, dict) else None
        suffix = f": {detail}" if detail else ""
        return TextVerifiedError(f"{prefix} ({response.status_code}){suffix}", status_code=response.status_code, payload=payload)

    @staticmethod
    def _safe_path(path: str) -> str:
        if path.startswith("http://") or path.startswith("https://"):
            parsed = urlparse(path)
            if parsed.netloc not in {"www.textverified.com", "backend.textverified.com"}:
                raise TextVerifiedError("Only TextVerified API v2 URLs are allowed")
            path = parsed.path + (("?" + parsed.query) if parsed.query else "")
        if not path.startswith("/"):
            path = "/" + path
        parsed = urlparse(path)
        if parsed.scheme or parsed.netloc or not parsed.path.startswith("/api/pub/v2/") and parsed.path != "/api/pub/v2":
            raise TextVerifiedError("Only relative TextVerified API v2 paths are allowed")
        return parsed.path + (("?" + parsed.query) if parsed.query else "")

    def request(
        self,
        method: str,
        path: str,
        *,
        query: Mapping[str, Any] | None = None,
        body: Any = None,
        headers: Mapping[str, str] | None = None,
        retry_auth: bool = True,
    ) -> Any:
        """Call any documented `/api/pub/v2/*` endpoint.

        Returned links from TextVerified are accepted as-is only when they
        point back to the configured TextVerified host and API v2 path.
        """
        safe_path = self._safe_path(path)
        token = self._get_token()
        request_headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
        if headers:
            for key, value in headers.items():
                if key.lower() not in {"authorization", "x-api-key", "x-api-username"}:
                    request_headers[key] = value
        method = method.upper()
        if body is not None:
            request_headers.setdefault("Content-Type", "application/json")
        for attempt in range(self.max_retries + 1):
            try:
                response = self._http.request(method, safe_path, params=query, json=body, headers=request_headers)
            except httpx.HTTPError as exc:
                if attempt >= self.max_retries:
                    raise TextVerifiedError(f"Network error calling TextVerified: {exc}") from exc
                time.sleep(min(8.0, 0.5 * (2**attempt)) + random.random() / 10)
                continue
            if response.status_code == 401 and retry_auth:
                token = self._get_token(force=True)
                request_headers["Authorization"] = f"Bearer {token}"
                return self.request(method, safe_path, query=query, body=body, headers=headers, retry_auth=False)
            if response.status_code == 429 or 500 <= response.status_code <= 599:
                if attempt < self.max_retries:
                    retry_after = response.headers.get("Retry-After")
                    delay = float(retry_after) if retry_after and retry_after.isdigit() else min(8.0, 0.5 * (2**attempt))
                    time.sleep(delay + random.random() / 10)
                    continue
            if response.status_code >= 400:
                raise self._error(response)
            if not response.content:
                return {"status_code": response.status_code, "headers": dict(response.headers)}
            try:
                return response.json()
            except ValueError:
                return {"status_code": response.status_code, "text": response.text, "headers": dict(response.headers)}
        raise TextVerifiedError("TextVerified request failed after retries")

    # Convenience methods for the high-frequency SMS/voice flows.
    def create_verification(self, service_name: str, capability: str = "sms", *, max_price: float | None = None, idempotency_key: str | None = None, **options: Any) -> Any:
        body: dict[str, Any] = {"serviceName": service_name, "capability": capability, **options}
        if max_price is not None:
            body["maxPrice"] = max_price
        headers = {"Idempotency-Key": idempotency_key} if idempotency_key else None
        return self.request("POST", "/api/pub/v2/verifications", body=body, headers=headers)

    def get_verification(self, verification_id: str) -> Any:
        return self.request("GET", f"/api/pub/v2/verifications/{verification_id}")

    def list_sms(self, *, reservation_id: str | None = None, to: str | None = None, reservation_type: str | None = None, **query: Any) -> Any:
        params = {"reservationId": reservation_id, "to": to, "reservationType": reservation_type, **query}
        return self.request("GET", "/api/pub/v2/sms", query={k: v for k, v in params.items() if v is not None})

    def send_sms(self, reservation_id: str, send_to: str, content: str) -> Any:
        return self.request("POST", "/api/pub/v2/sms/send", body={"reservationId": reservation_id, "sendTo": send_to, "content": content})

    def list_calls(self, *, reservation_id: str | None = None, to: str | None = None, reservation_type: str | None = None, **query: Any) -> Any:
        params = {"reservationId": reservation_id, "to": to, "reservationType": reservation_type, **query}
        return self.request("GET", "/api/pub/v2/calls", query={k: v for k, v in params.items() if v is not None})

    def create_call_access_token(self, reservation_id: str) -> Any:
        return self.request("POST", "/api/pub/v2/calls/access-token", body={"reservationId": reservation_id})

    def create_rental(self, service_name: str, duration: str, capability: str = "sms", *, is_renewable: bool = False, number_type: str = "mobile", allow_back_order_reservations: bool = False, idempotency_key: str | None = None, **options: Any) -> Any:
        body: dict[str, Any] = {"serviceName": service_name, "duration": duration, "capability": capability, "isRenewable": is_renewable, "numberType": number_type, "allowBackOrderReservations": allow_back_order_reservations, **options}
        headers = {"Idempotency-Key": idempotency_key} if idempotency_key else None
        return self.request("POST", "/api/pub/v2/reservations/rental", body=body, headers=headers)
