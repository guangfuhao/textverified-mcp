from __future__ import annotations

import json
import os
from typing import Any

from pydantic import BaseModel, ConfigDict, Field
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from .client import TextVerifiedClient, TextVerifiedError
from .credentials import effective_credentials, save_credentials, settings_snapshot

mcp = FastMCP("TextVerified API v2")


class SettingsReadResult(BaseModel):
    """Structured settings payload consumed by the native plugin settings page."""

    model_config = ConfigDict(populate_by_name=True)

    schema_: dict[str, Any] = Field(alias="schema")
    values: dict[str, Any]
    layout: list[dict[str, Any]] = Field(default_factory=list)


class SettingsUpdateResult(BaseModel):
    values: dict[str, Any]


def _advertise_native_settings() -> None:
    """Advertise the OpenAI settings extension on older MCP SDK releases.

    The Python MCP SDK exposes experimental capabilities through
    ``create_initialization_options``. The extension is intentionally injected
    here instead of depending on a vendor-specific SDK so the plugin remains
    usable by Claude, Codex, and other MCP hosts.
    """

    original = mcp._mcp_server.create_initialization_options

    def create_initialization_options(notification_options: Any = None, experimental_capabilities: dict[str, dict[str, Any]] | None = None):
        capabilities = dict(experimental_capabilities or {})
        settings = dict(capabilities.get("openai/settings", {}))
        settings.setdefault("readTool", "textverified_settings_read")
        settings.setdefault("updateTool", "textverified_settings_update")
        capabilities["openai/settings"] = settings
        options = original(notification_options, capabilities)
        # Newer hosts look for the standardized extension namespace, while
        # older ChatGPT hosts used the experimental namespace above. The MCP
        # SDK version used by this plugin only models ``experimental``
        # explicitly, but its capability model permits extension fields.
        try:
            options.capabilities.extensions = {"openai/settings": settings}
        except (AttributeError, TypeError):
            # Keep the legacy advertisement working on older SDKs/hosts.
            pass
        return options

    mcp._mcp_server.create_initialization_options = create_initialization_options


_advertise_native_settings()


def _client() -> TextVerifiedClient:
    return TextVerifiedClient()


def _result(call: Any) -> str:
    return json.dumps(call, ensure_ascii=False, indent=2, default=str)


def _error(exc: Exception) -> str:
    if isinstance(exc, TextVerifiedError):
        return json.dumps({"error": str(exc), "status_code": exc.status_code, "details": exc.payload}, ensure_ascii=False, indent=2, default=str)
    return json.dumps({"error": str(exc)}, ensure_ascii=False)


@mcp.tool(
    name="textverified_settings_read",
    title="TextVerified settings",
    description="Read the current TextVerified plugin settings. The API key is always masked.",
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=False),
    structured_output=True,
)
def textverified_settings_read() -> SettingsReadResult:
    """Provide the native plugin settings page with its schema and values."""

    snapshot = settings_snapshot()
    values = {key: snapshot[key] for key in ("username", "api_key", "base_url")}
    return SettingsReadResult(
        schema_={
            "type": "object",
            "properties": {
                "username": {
                    "type": "string",
                    "title": "TextVerified username",
                    "description": "The registration email for your TextVerified account.",
                    "minLength": 1,
                },
                "api_key": {
                    "type": "string",
                    "title": "TextVerified API key",
                    "description": "Your primary API key. It is stored locally and never shown after saving.",
                    "minLength": 1,
                },
                "base_url": {
                    "type": "string",
                    "title": "API base URL",
                    "description": "Leave the default unless TextVerified gives you a different API host.",
                    "minLength": 1,
                },
            },
            "required": ["username", "api_key"],
        },
        values=values,
        layout=[
            {
                "kind": "group",
                "title": "TextVerified account",
                "items": [
                    {"kind": "property", "property": "username"},
                    {"kind": "property", "property": "api_key"},
                    {"kind": "property", "property": "base_url"},
                ],
            }
        ],
    )


@mcp.tool(
    name="textverified_settings_update",
    title="Save TextVerified settings",
    description="Save TextVerified credentials entered in the plugin settings page.",
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False, openWorldHint=False),
    structured_output=True,
)
def textverified_settings_update(set: dict[str, str]) -> SettingsUpdateResult:
    """Persist settings with owner-only permissions and return masked values."""

    allowed = {"username", "api_key", "base_url"}
    unknown = set.keys() - allowed
    if unknown:
        raise ValueError(f"Unsupported TextVerified settings: {', '.join(sorted(unknown))}")
    current = effective_credentials()
    username = set.get("username") or current["username"]
    api_key = set.get("api_key") or current["api_key"]
    base_url = set.get("base_url") or current["base_url"] or "https://www.textverified.com"
    save_credentials(username=username, api_key=api_key, base_url=base_url)
    snapshot = settings_snapshot()
    return SettingsUpdateResult(values={key: snapshot[key] for key in ("username", "api_key", "base_url")})


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
