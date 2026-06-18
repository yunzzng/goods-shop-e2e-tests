#!/bin/zsh

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_PYTHON="$ROOT_DIR/.venv/bin/python3"
DASHBOARD_PATH="$ROOT_DIR/artifacts/dashboard.html"

if [ ! -x "$VENV_PYTHON" ]; then
  echo "Virtual environment Python not found: $VENV_PYTHON"
  echo "Create it first with: python3 -m venv .venv"
  exit 1
fi

"$VENV_PYTHON" -m pytest "$@"

if [ -f "$DASHBOARD_PATH" ]; then
  echo
  echo "Dashboard: $DASHBOARD_PATH"
  if command -v open >/dev/null 2>&1; then
    open "$DASHBOARD_PATH"
  fi
fi
