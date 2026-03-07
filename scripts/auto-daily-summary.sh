#!/bin/bash
# Auto Daily Summary - 每日重置前自动总结
# 用法：./scripts/auto-daily-summary.sh [--dry-run] [--force]

set -e

# 配置
WORKSPACE="/Users/a123456/.openclaw/workspace"
LEARNINGS_DIR="$WORKSPACE/.learnings"
MEMORY_DIR="$WORKSPACE/memory"
MEMORY_FILE="$WORKSPACE/MEMORY.md"
TODAY=$(date +%Y-%m-%d)
YESTERDAY=$(date -d "yesterday" +%Y-%m-%d 2>/dev/null || date -v-1d +%Y-%m-%d)
SUMMARY_FILE="$MEMORY_DIR/${TODAY}-daily-summary.md"

# 参数解析
DRY_RUN=false
FORCE=false
for arg in "$@"; do
    case $arg in
        --dry-run) DRY_RUN=true ;;
        --force) FORCE=true ;;
    esac
done

echo "🤖 Auto Daily Summary"
echo "日期：$TODAY"
echo "模式：$([ "$DRY_RUN" = true ] && echo 'Dry Run' || echo 'Production')"
echo "================================"

# 检查是否已存在今日总结
if [ -f "$SUMMARY_FILE" ] && [ "$FORCE" = false ]; then
    echo "⚠️  今日总结已存在：$SUMMARY_FILE"
    echo "使用 --force 强制重新生成"
    exit 0
fi

# 1. 扫描 Git 提交
echo ""
echo "📝 扫描 Git 提交..."
cd "$WORKSPACE"
GIT_LOG=$(git log --since="$TODAY 00:00" --oneline 2>/dev/null || echo "")
GIT_FILES=$(git diff --name-only HEAD~1 HEAD 2>/dev/null | wc -l || echo "0")

# 2. 统计学习记录
echo "📚 统计学习记录..."
LEARNINGS_COUNT=0
ERRORS_COUNT=0
FEATURES_COUNT=0

if [ -f "$LEARNINGS_DIR/LEARNINGS.md" ]; then
    LEARNINGS_COUNT=$(grep -c "**Logged**: $TODAY" "$LEARNINGS_DIR/LEARNINGS.md" 2>/dev/null || echo "0")
fi

if [ -f "$LEARNINGS_DIR/ERRORS.md" ]; then
    ERRORS_COUNT=$(grep -c "**Logged**: $TODAY" "$LEARNINGS_DIR/ERRORS.md" 2>/dev/null || echo "0")
fi

if [ -f "$LEARNINGS_DIR/FEATURE_REQUESTS.md" ]; then
    FEATURES_COUNT=$(grep -c "**Logged**: $TODAY" "$LEARNINGS_DIR/FEATURE_REQUESTS.md" 2>/dev/null || echo "0")
fi

# 3. 检查 MEMORY.md 更新
echo "💾 检查 MEMORY.md..."
MEMORY_UPDATED=false
if [ -f "$MEMORY_FILE" ]; then
    LAST_UPDATE=$(grep "最后更新" "$MEMORY_FILE" | head -1 || echo "")
    if echo "$LAST_UPDATE" | grep -q "$TODAY"; then
        MEMORY_UPDATED=true
    fi
fi

# 4. 检查待办事项
echo "⏳ 检查待办事项..."
TODO_FILE="$WORKSPACE/TODO.md"
TODO_PENDING=0
if [ -f "$TODO_FILE" ]; then
    TODO_PENDING=$(grep -cE "^\- \[ \]" "$TODO_FILE" 2>/dev/null || echo "0")
fi

# 5. 生成总结报告
echo ""
echo "📊 生成总结报告..."

if [ "$DRY_RUN" = true ]; then
    echo ""
    echo "=== DRY RUN 模式 - 不会写入文件 ==="
    echo ""
    echo "📈 今日统计:"
    echo "  Git 提交：$(echo "$GIT_LOG" | grep -c . || echo 0) 个"
    echo "  修改文件：$GIT_FILES 个"
    echo "  学习记录：$LEARNINGS_COUNT 条"
    echo "  错误记录：$ERRORS_COUNT 条"
    echo "  功能请求：$FEATURES_COUNT 条"
    echo "  MEMORY.md 已更新：$MEMORY_UPDATED"
    echo "  待办事项：$TODO_PENDING 个"
    echo ""
    echo "✅ Dry Run 完成"
    exit 0
fi

# 创建 memory 目录
mkdir -p "$MEMORY_DIR"

# 生成总结文件
cat > "$SUMMARY_FILE" << EOF
# 每日总结 - $TODAY

_自动生成于 $(date "+%Y-%m-%d %H:%M:%S")_

## 📈 今日统计

| 指标 | 数量 |
|------|------|
| Git 提交 | $(echo "$GIT_LOG" | grep -c . || echo 0) |
| 修改文件 | $GIT_FILES |
| 学习记录 | $LEARNINGS_COUNT |
| 错误记录 | $ERRORS_COUNT |
| 功能请求 | $FEATURES_COUNT |
| MEMORY.md 更新 | $MEMORY_UPDATED |
| 待办事项 | $TODO_PENDING |

## 📝 Git 提交

\`\`\`
$GIT_LOG
\`\`\`

## 📚 学习记录

$(if [ "$LEARNINGS_COUNT" -gt 0 ]; then
    echo "今日新增 $LEARNINGS_COUNT 条学习记录"
    grep "$TODAY" "$LEARNINGS_DIR/LEARNINGS.md" -A 3 | head -20
else
    echo "_今日无新增学习记录_"
fi)

## ⚠️ 错误记录

$(if [ "$ERRORS_COUNT" -gt 0 ]; then
    echo "今日记录 $ERRORS_COUNT 个错误"
    grep "$TODAY" "$LEARNINGS_DIR/ERRORS.md" -A 3 | head -20
else
    echo "_今日无新增错误记录_"
fi)

## 🔄 待办交接

$(if [ "$TODO_PENDING" -gt 0 ] && [ -f "$TODO_FILE" ]; then
    echo "未完成事项："
    grep -E "^\- \[ \]" "$TODO_FILE" | head -10
else
    echo "_无待办事项_"
fi)

## 💡 建议

$(
if [ "$LEARNINGS_COUNT" -eq 0 ] && [ "$GIT_FILES" -gt 0 ]; then
    echo "⚠️ 今天有代码修改但没有学习记录，建议检查是否有需要总结的经验"
elif [ "$LEARNINGS_COUNT" -gt 5 ]; then
    echo "✅ 今天学习记录丰富，建议提升到 MEMORY.md"
else
    echo "✅ 今日工作总结完成"
fi
)

---
**生成时间**: $(date "+%Y-%m-%d %H:%M:%S")
**重置时间**: 次日 04:00 (Asia/Shanghai)
**状态**: ✅ 已完成
EOF

echo "✅ 总结报告已生成：$SUMMARY_FILE"

# 6. 更新 MEMORY.md（如果有重要学习）
if [ "$LEARNINGS_COUNT" -gt 3 ] || [ "$MEMORY_UPDATED" = false ]; then
    echo ""
    echo "📝 更新 MEMORY.md..."
    
    # 检查是否需要更新
    if ! grep -q "$TODAY" "$MEMORY_FILE" 2>/dev/null; then
        # 添加更新日期标记
        sed -i.bak "s/_最后更新：.*/_最后更新：$TODAY $(date "+%H:%M")_/" "$MEMORY_FILE" 2>/dev/null || \
        sed -i '' "s/_最后更新：.*/_最后更新：$TODAY $(date "+%H:%M")_/" "$MEMORY_FILE" 2>/dev/null || true
        
        echo "  ✓ MEMORY.md 更新日期标记"
    fi
fi

# 7. 输出摘要
echo ""
echo "================================"
echo "✅ Auto Daily Summary 完成"
echo ""
echo "📊 今日摘要:"
echo "  Git 提交：$(echo "$GIT_LOG" | grep -c . || echo 0)"
echo "  学习记录：$LEARNINGS_COUNT"
echo "  错误记录：$ERRORS_COUNT"
echo "  待办事项：$TODO_PENDING"
echo ""
echo "📁 输出文件:"
echo "  $SUMMARY_FILE"
echo "  $MEMORY_FILE (如有更新)"
echo ""
