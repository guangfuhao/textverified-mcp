from __future__ import annotations

"""Ephemeral localhost setup page for hosts without native plugin settings."""

import argparse
import html
import os
import secrets
import subprocess
import sys
import threading
import time
import urllib.parse
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from .credentials import save_credentials


_MAX_BODY = 16 * 1024
_DEFAULT_BASE_URL = "https://www.textverified.com"
_PAGE_STYLE = """
body{font:16px -apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;max-width:560px;margin:48px auto;padding:0 20px;color:#172033;background:#f7f9fc}
main{background:#fff;border:1px solid #e3e8f0;border-radius:16px;padding:28px;box-shadow:0 8px 28px #17203312}
h1{font-size:24px;margin:0 0 8px}p{line-height:1.5;color:#566176}label{display:block;font-weight:600;margin:18px 0 7px}input{box-sizing:border-box;width:100%;padding:11px 12px;border:1px solid #c9d2df;border-radius:9px;font-size:16px}button{margin-top:24px;padding:11px 16px;border:0;border-radius:9px;background:#1769e0;color:#fff;font-size:16px;font-weight:600;cursor:pointer}.hint{font-size:13px;color:#6b7585;margin-top:16px}
"""


def _page(*, message: str = "", success: bool = False) -> bytes:
    alert = f'<p style="color:{"#18794e" if success else "#b42318"}">{html.escape(message)}</p>' if message else ""
    if success:
        content = f"<h1>TextVerified is configured</h1>{alert}<p>You can close this tab. The temporary local setup service has stopped.</p>"
    else:
        content = f"""
<h1>TextVerified setup</h1>
<p>Enter your credentials locally. This page is served only from this computer and the temporary service closes after saving.</p>
{alert}
<form method="post">
  <label for="username">TextVerified username</label>
  <input id="username" name="username" type="email" autocomplete="username" required>
  <label for="api_key">TextVerified API key</label>
  <input id="api_key" name="api_key" type="password" autocomplete="current-password" required>
  <label for="base_url">API base URL</label>
  <input id="base_url" name="base_url" value="{_DEFAULT_BASE_URL}" autocomplete="url">
  <button type="submit">Save securely</button>
</form>
<p class="hint">The API key is written to the local TextVerified configuration with owner-only permissions. It is never displayed back to the page.</p>
"""
    return f"<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>TextVerified setup</title><style>{_PAGE_STYLE}</style></head><body><main>{content}</main></body></html>".encode("utf-8")


class _SetupServer(ThreadingHTTPServer):
    allow_reuse_address = False
    daemon_threads = True

    def __init__(self, address: tuple[str, int], token: str, timeout: int):
        super().__init__(address, _SetupHandler)
        self.token = token
        self.started_at = time.monotonic()
        self.timeout = timeout
        self.completed = False


class _SetupHandler(BaseHTTPRequestHandler):
    server: _SetupServer

    def log_message(self, _format: str, *_args: Any) -> None:
        # Never log request URLs or form values because the one-time URL is a
        # credential to access this local setup page.
        return

    def _authorized(self) -> bool:
        query = urllib.parse.parse_qs(urllib.parse.urlsplit(self.path).query)
        return secrets.compare_digest(query.get("token", [""])[0], self.server.token)

    def _send(self, body: bytes, status: int = 200) -> None:
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Security-Policy", "default-src 'none'; style-src 'unsafe-inline'; form-action 'self'")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        if not self._authorized():
            self._send(_page(message="This setup link is invalid or expired."), 404)
            return
        self._send(_page())

    def do_POST(self) -> None:  # noqa: N802
        if not self._authorized():
            self._send(_page(message="This setup link is invalid or expired."), 404)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            length = 0
        if length <= 0 or length > _MAX_BODY:
            self._send(_page(message="The submitted form is too large."), 413)
            return
        raw = self.rfile.read(length)
        fields = urllib.parse.parse_qs(raw.decode("utf-8", errors="strict"), keep_blank_values=True)
        username = fields.get("username", [""])[0].strip()
        api_key = fields.get("api_key", [""])[0].strip()
        base_url = fields.get("base_url", [_DEFAULT_BASE_URL])[0].strip() or _DEFAULT_BASE_URL
        if not username or not api_key:
            self._send(_page(message="Username and API key are required."), 400)
            return
        try:
            save_credentials(username=username, api_key=api_key, base_url=base_url)
        except (OSError, ValueError):
            self._send(_page(message="The credentials could not be saved locally."), 500)
            return
        self.server.completed = True
        self._send(_page(message="Credentials saved locally.", success=True))
        threading.Thread(target=self.server.shutdown, daemon=True).start()


def _serve_cli(timeout: int, open_browser: bool) -> int:
    """Run the one-shot server in a detached child process."""
    token = secrets.token_urlsafe(32)
    server = _SetupServer(("127.0.0.1", 0), token, timeout)
    url = f"http://127.0.0.1:{server.server_port}/?token={urllib.parse.quote(token)}"
    rendezvous = Path(f"/tmp/textverified-setup-{os.getpid()}.url")
    rendezvous.write_text(url + "\n", encoding="utf-8")
    try:
        rendezvous.chmod(0o600)
    except OSError:
        pass
    if open_browser:
        try:
            webbrowser.open(url, new=2)
        except Exception:
            pass

    def stop_on_timeout() -> None:
        time.sleep(timeout)
        if not server.completed:
            server.shutdown()

    threading.Thread(target=stop_on_timeout, daemon=True).start()
    try:
        server.serve_forever(poll_interval=0.2)
    finally:
        server.server_close()
        try:
            rendezvous.unlink()
        except OSError:
            pass
    return 0


def launch_setup_service(*, open_browser: bool = True, timeout: int = 600) -> dict[str, Any]:
    """Launch the setup page as a detached one-shot local process."""
    process = subprocess.Popen(
        [sys.executable, "-m", "textverified_mcp.setup_server", "--serve", "--timeout", str(timeout), *(["--no-open"] if not open_browser else [])],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
        close_fds=True,
    )
    rendezvous = Path(f"/tmp/textverified-setup-{process.pid}.url")
    deadline = time.monotonic() + 3
    while time.monotonic() < deadline and not rendezvous.exists():
        time.sleep(0.03)
    if not rendezvous.exists():
        return {"started": False, "error": "The local setup service did not start."}
    url = rendezvous.read_text(encoding="utf-8").strip()
    try:
        rendezvous.unlink()
    except OSError:
        pass
    return {"started": True, "pid": process.pid, "url": url, "expires_in_seconds": timeout, "message": "Complete the local form; the service exits after saving."}


def main() -> int:
    parser = argparse.ArgumentParser(description="Open a one-shot localhost TextVerified setup form")
    parser.add_argument("--serve", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--timeout", type=int, default=600)
    parser.add_argument("--no-open", action="store_true")
    args = parser.parse_args()
    if not args.serve:
        result = launch_setup_service(open_browser=not args.no_open, timeout=args.timeout)
        print(result.get("url", result.get("error", "")))
        return 0 if result.get("started") else 1
    return _serve_cli(max(30, min(args.timeout, 3600)), not args.no_open)


if __name__ == "__main__":
    raise SystemExit(main())
