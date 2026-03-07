#!/bin/bash
# Daily Summary Script - 在每日重置前自动总结工作
# 用法：./scripts/daily-summary.sh

set -e

WORKSPACE="/Users/a123456/.openclaw/workspace"
LEARNINGS_DIR="$WORKSPACE/.learnings"
MEMORY_FILE="$WORKSPACE/MEMORY.md"
TODAY=$(date +%Y-%m-%d)
YESTERDAY=$(date -d "yesterday" +%Y-%m-%d)

echo "📅 生成每日总结：$TODAY"
echo "================================"

# 1. 扫描今天的 git 提交
echo ""
echo "📝 今日 git 提交："
cd "$WORKSPACE"
git log --since="$TODAY 00:00" --until="$TODAY 23:59" --oneline 2>/dev/null || echo "  无提交"

# 2. 检查今天的学习记录
echo ""
echo "📚 今日学习记录："
if [ -f "$LEARNINGS_DIR/LEARNINGS.md" ]; then
    grep -c "$TODAY" "$LEARNINGS_DIR/LEARNINGS.md" 2>/dev/null || echo "  0 条"
else
    echo "  无 LEARNINGS.md"
fi

if [ -f "$LEARNINGS_DIR/ERRORS.md" ]; then
    grep -c "$TODAY" "$LEARNINGS_DIR/ERRORS.md" 2>/dev/null || echo "  0 条"
else
    echo "  无 ERRORS.md"
fi

# 3. 检查 MEMORY.md 最后更新时间
echo ""
echo "💾 MEMORY.md 最后更新："
if [ -f "$MEMORY_FILE" ]; then
    head -3 "$MEMORY_FILE" | grep "最后更新" || echo "  无更新时间"
else
    echo "  文件不存在"
fi

# 4. 输出待办事项（如有）
echo ""
echo "⏳ 待办事项检查："
if [ -f "$WORKSPACE/TODO.md" ]; then
    grep -E "^\- \[ \]" "$WORKSPACE/TODO.md" | head -5 || echo "  无待办"
else
    echo "  无 TODO.md"
fi

echo ""
echo "================================"
echo "✅ 总结完成"
