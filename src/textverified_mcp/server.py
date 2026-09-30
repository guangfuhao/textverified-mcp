from __future__ import annotations

import json
import os
from typing import Any

from mcp.server.fastmcp import FastMCP

from .client import TextVerifiedClient, TextVerifiedError

mcp = FastMCP("TextVerified API v2")


def _client() -> TextVerifiedClient:
    return TextVerifiedClient()


def _result(call: Any) -> str:
    return json.dumps(call, ensure_ascii=False, indent=2, default=str)


def _error(exc: Exception) -> str:
    if isinstance(exc, TextVerifiedError):
        return json.dumps({"error": str(exc), "status_code": exc.status_code, "details": exc.payload}, ensure_ascii=False, indent=2, default=str)
    return json.dumps({"error": str(exc)}, ensure_ascii=False)


@mcp.tool()
def textverified_request(method: str, path: str, query: dict[str, Any] | None = None, body: Any = None, headers: dict[str, str] | None = None) -> str:
    """Call any TextVerified API v2 endpoint.

    Use the exact relative path from docs, such as /api/pub/v2/services.
    This is the complete escape hatch for all current and future v2 endpoints.
    Purchase, refund, renewal, reply, and other state-changing calls spend
    account credits or change account state; use only when explicitly intended.
    """
    client = _client()
    try:
        return _result(client.request(method, path, query=query, body=body, headers=headers))
    except Exception as exc:
        return _error(exc)
    finally:
        client.close()


@mcp.tool()
def textverified_create_verification(service_name: str, capability: str = "sms", max_price: float | None = None, idempotency_key: str | None = None, options: dict[str, Any] | None = None, confirm_purchase: bool = False) -> str:
    """Purchase a single-use verification number for SMS or voice.

    Set confirm_purchase=true only after confirming service, capability, and
    max price. Use test_* service names to exercise the documented mock flow.
    """
    if not confirm_purchase:
        return _error(TextVerifiedError("Purchase not sent: set confirm_purchase=true after reviewing the purchase parameters"))
    client = _client()
    try:
        return _result(client.create_verification(service_name, capability, max_price=max_price, idempotency_key=idempotency_key, **(options or {})))
    except Exception as exc:
        return _error(exc)
    finally:
        client.close()


@mcp.tool()
def textverified_get_verification(verification_id: str) -> str:
    """Read verification status and its follow-up links."""
    client = _client()
    try:
        return _result(client.get_verification(verification_id))
    except Exception as exc:
        return _error(exc)
    finally:
        client.close()


@mcp.tool()
def textverified_list_sms(reservation_id: str | None = None, to: str | None = None, reservation_type: str | None = None, extra_query: dict[str, Any] | None = None) -> str:
    """List received SMS, optionally filtered by reservation or number."""
    client = _client()
    try:
        return _result(client.list_sms(reservation_id=reservation_id, to=to, reservation_type=reservation_type, **(extra_query or {})))
    except Exception as exc:
        return _error(exc)
    finally:
        client.close()


@mcp.tool()
def textverified_send_sms(reservation_id: str, send_to: str, content: str, confirm_send: bool = False) -> str:
    """Send an SMS from a rented number; requires explicit confirmation."""
    if not confirm_send:
        return _error(TextVerifiedError("SMS not sent: set confirm_send=true after reviewing the destination and content"))
    client = _client()
    try:
        return _result(client.send_sms(reservation_id, send_to, content))
    except Exception as exc:
        return _error(exc)
    finally:
        client.close()


@mcp.tool()
def textverified_list_calls(reservation_id: str | None = None, to: str | None = None, reservation_type: str | None = None, extra_query: dict[str, Any] | None = None) -> str:
    """List voice calls associated with the account or reservation."""
    client = _client()
    try:
        return _result(client.list_calls(reservation_id=reservation_id, to=to, reservation_type=reservation_type, **(extra_query or {})))
    except Exception as exc:
        return _error(exc)
    finally:
        client.close()


@mcp.tool()
def textverified_create_call_access_token(reservation_id: str) -> str:
    """Create the incoming-call access token for a reservation."""
    client = _client()
    try:
        return _result(client.create_call_access_token(reservation_id))
    except Exception as exc:
        return _error(exc)
    finally:
        client.close()


@mcp.tool()
def textverified_create_rental(service_name: str, duration: str, capability: str = "sms", is_renewable: bool = False, number_type: str = "mobile", allow_back_order_reservations: bool = False, idempotency_key: str | None = None, options: dict[str, Any] | None = None, confirm_purchase: bool = False) -> str:
    """Purchase a rental number; requires explicit confirmation."""
    if not confirm_purchase:
        return _error(TextVerifiedError("Purchase not sent: set confirm_purchase=true after reviewing the rental parameters"))
    client = _client()
    try:
        return _result(client.create_rental(service_name, duration, capability, is_renewable=is_renewable, number_type=number_type, allow_back_order_reservations=allow_back_order_reservations, idempotency_key=idempotency_key, **(options or {})))
    except Exception as exc:
        return _error(exc)
    finally:
        client.close()


def main() -> None:
    mcp.run(transport=os.getenv("TEXTVERIFIED_MCP_TRANSPORT", "stdio"))


if __name__ == "__main__":
    main()
