#!/bin/sh
set -eu
PLUGIN_ROOT="${PLUGIN_ROOT:-$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)}"
if [ -x "$PLUGIN_ROOT/.venv/bin/textverified-mcp" ]; then
  exec "$PLUGIN_ROOT/.venv/bin/textverified-mcp" "$@"
fi
if command -v uv >/dev/null 2>&1; then
  exec uv run --project "$PLUGIN_ROOT" textverified-mcp "$@"
fi
exec python3 -m textverified_mcp.server "$@"
