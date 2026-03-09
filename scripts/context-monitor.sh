#!/bin/bash
# Context 监控与记忆整理
# 用法：bash scripts/context-monitor.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="$HOME/.openclaw/workspace"

cd "$WORKSPACE_DIR"

echo "🔍 运行 Context 监控..."
python3 "$SCRIPT_DIR/context-monitor.py"

echo ""
echo "✅ Context 监控完成"
