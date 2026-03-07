#!/bin/bash
# Quick Log - 快速记录学习/错误/功能请求
# 用法：./quick-log.sh learning|error|feature "描述"

set -e

WORKSPACE="/Users/a123456/.openclaw/workspace"
LEARNINGS_DIR="$WORKSPACE/.learnings"
TODAY=$(date +%Y-%m-%d)
TIMESTAMP=$(date "+%Y-%m-%dT%H:%M:%S%z")

TYPE=${1:-learning}
MESSAGE=${2:-"无描述"}

# 检查参数
if [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    echo "用法：$0 learning|error|feature \"描述\""
    echo ""
    echo "示例:"
    echo "  $0 learning \"OpenClaw 会话重置机制详解\""
    echo "  $0 error \"Nano Banana 2 安装失败 - 域名被墙\""
    echo "  $0 feature \"需要自动总结机制\""
    exit 0
fi

# 确保目录存在
mkdir -p "$LEARNINGS_DIR"

case $TYPE in
    learning|l)
        FILE="$LEARNINGS_DIR/LEARNINGS.md"
        PREFIX="LRN"
        AREA="config"
        ;;
    error|e)
        FILE="$LEARNINGS_DIR/ERRORS.md"
        PREFIX="ERR"
        AREA="infra"
        ;;
    feature|f)
        FILE="$LEARNINGS_DIR/FEATURE_REQUESTS.md"
        PREFIX="FEAT"
        AREA="frontend"
        ;;
    *)
        echo "❌ 未知类型：$TYPE"
        echo "支持：learning(l), error(e), feature(f)"
        exit 1
        ;;
esac

# 生成 ID
ID="${PREFIX}-${TODAY}-$(date +%H%M)"

# 确保文件有标题
if [ ! -f "$FILE" ]; then
    case $TYPE in
        learning|l)
            echo "# Learnings Log" > "$FILE"
            echo "" >> "$FILE"
            echo "记录纠正、知识缺口、最佳实践。" >> "$FILE"
            ;;
        error|e)
            echo "# Errors Log" > "$FILE"
            echo "" >> "$FILE"
            echo "记录命令失败、异常和集成问题。" >> "$FILE"
            ;;
        feature|f)
            echo "# Feature Requests Log" > "$FILE"
            echo "" >> "$FILE"
            echo "记录用户请求的新功能和能力。" >> "$FILE"
            ;;
    esac
    echo "" >> "$FILE"
    echo "---" >> "$FILE"
    echo "" >> "$FILE"
fi

# 追加记录
cat >> "$FILE" << EOF

## [$ID] auto

**Logged**: $TIMESTAMP
**Priority**: medium
**Status**: pending
**Area**: $AREA

### Summary
$MESSAGE

### Details
_待补充_

### Suggested Action
_待补充_

### Metadata
- Source: quick-log
- Tags: auto-logged

---
EOF

echo "✅ 已记录：[$ID]"
echo "   类型：$TYPE"
echo "   内容：$MESSAGE"
echo "   文件：$FILE"
