#!/bin/bash
# Zero Workspace 自动备份脚本

set -e

WORKSPACE="/Users/a123456/.openclaw/workspace"
cd "$WORKSPACE"

# 检查是否有改动
if git status --porcelain | grep -q .; then
    git add -A
    git commit -m "Auto backup: $(date '+%Y-%m-%d %H:%M')"
    git push origin main
    echo "Backup completed at $(date)"
else
    echo "No changes to backup at $(date)"
fi
