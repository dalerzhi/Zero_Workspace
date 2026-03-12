#!/bin/zsh
set -euo pipefail

export PATH="/opt/homebrew/opt/node/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"

OPENCLAW_NODE="/opt/homebrew/opt/node/bin/node"
OPENCLAW_ENTRY="/opt/homebrew/lib/node_modules/openclaw/dist/index.js"
LOG_DIR="$HOME/.openclaw/logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/gateway-watchdog.log"

stamp() {
  date '+%Y-%m-%d %H:%M:%S'
}

status_ok() {
  "$OPENCLAW_NODE" "$OPENCLAW_ENTRY" status >/dev/null 2>&1
}

restart_gateway() {
  "$OPENCLAW_NODE" "$OPENCLAW_ENTRY" gateway restart >> "$LOG_FILE" 2>&1
}

if status_ok; then
  echo "[$(stamp)] gateway healthy" >> "$LOG_FILE"
  exit 0
fi

echo "[$(stamp)] gateway unhealthy, restarting" >> "$LOG_FILE"
if restart_gateway; then
  echo "[$(stamp)] restart issued" >> "$LOG_FILE"
  exit 0
else
  echo "[$(stamp)] restart failed" >> "$LOG_FILE"
  exit 1
fi
