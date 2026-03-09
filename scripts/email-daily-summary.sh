#!/bin/bash
# 邮件日报 - 每天早上 8 点自动运行
# 用法：bash scripts/email-daily-summary.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="$HOME/.openclaw/workspace"

cd "$WORKSPACE_DIR"

echo "📬 开始收取昨日邮件..."
bash skills/aliyun-mail/aliyun-mail.sh summary --days 1 --send-feishu --chat-id ou_7c6c3cdce8475c7a8de63811592c37f9

echo ""
echo "✅ 邮件日报完成"
