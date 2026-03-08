#!/bin/bash
# aliyun-mail.sh - 阿里云邮箱技能主脚本
# 用法：bash aliyun-mail.sh <command> [options]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"
CREDENTIALS_FILE="$WORKSPACE_DIR/.credentials/aliyun-mail.md"
PYTHON_LIB="$SCRIPT_DIR/lib"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# 检查依赖
check_dependencies() {
    local missing=()
    
    for pkg in imap-tools python-docx openpyxl python-pptx pypdf2; do
        if ! python3 -c "import $(echo $pkg | tr - _)" 2>/dev/null; then
            missing+=("$pkg")
        fi
    done
    
    if [ ${#missing[@]} -gt 0 ]; then
        log_warn "缺少 Python 依赖：${missing[*]}"
        log_info "运行以下命令安装："
        echo "  pip3 install ${missing[*]}"
        return 1
    fi
}

# 检查凭证
check_credentials() {
    if [ ! -f "$CREDENTIALS_FILE" ]; then
        log_error "凭证文件不存在：$CREDENTIALS_FILE"
        log_info "请先配置邮箱信息，参考：$SCRIPT_DIR/README-授权码.md"
        return 1
    fi
}

# 主命令
case "$1" in
    summary)
        check_dependencies || exit 1
        check_credentials || exit 1
        python3 "$PYTHON_LIB/fetch_emails.py" --action summary "${@:2}"
        ;;
    
    list)
        check_dependencies || exit 1
        check_credentials || exit 1
        python3 "$PYTHON_LIB/fetch_emails.py" --action list "${@:2}"
        ;;
    
    attachments)
        check_dependencies || exit 1
        check_credentials || exit 1
        python3 "$PYTHON_LIB/fetch_emails.py" --action attachments "${@:2}"
        ;;
    
    test)
        check_dependencies || exit 1
        check_credentials || exit 1
        log_info "测试邮箱连接..."
        python3 "$PYTHON_LIB/fetch_emails.py" --action test "${@:2}"
        ;;
    
    install)
        log_info "安装 Python 依赖..."
        pip3 install imap-tools python-docx openpyxl python-pptx pypdf2
        log_info "安装完成"
        ;;
    
    *)
        echo "用法：$0 <command> [options]"
        echo ""
        echo "命令:"
        echo "  summary      收取邮件并生成总结"
        echo "  list         列出邮件（不总结）"
        echo "  attachments  提取附件"
        echo "  test         测试邮箱连接"
        echo "  install      安装依赖"
        echo ""
        echo "选项:"
        echo "  --days N           收取最近 N 天的邮件"
        echo "  --since DATE       开始日期 (YYYY-MM-DD)"
        echo "  --until DATE       结束日期 (YYYY-MM-DD)"
        echo "  --output-dir DIR   附件保存目录"
        echo "  --send-feishu      发送到飞书"
        echo "  --chat-id ID       飞书聊天 ID"
        echo ""
        echo "示例:"
        echo "  $0 summary --days 1"
        echo "  $0 summary --since 2026-03-07 --until 2026-03-08"
        echo "  $0 attachments --days 1 --output-dir /tmp/attachments/"
        exit 1
        ;;
esac
