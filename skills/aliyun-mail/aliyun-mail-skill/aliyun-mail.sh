#!/bin/bash
# aliyun-mail.sh - 阿里云邮箱技能主脚本
# 用法：bash aliyun-mail.sh <command> [options]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="$HOME/.openclaw/workspace"
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
    
    # 检查 Python 包（使用正确的导入名）
    python3 -c "from imap_tools import MailBox" 2>/dev/null || missing+=("imap-tools")
    python3 -c "import docx" 2>/dev/null || missing+=("python-docx")
    python3 -c "import openpyxl" 2>/dev/null || missing+=("openpyxl")
    python3 -c "import pptx" 2>/dev/null || missing+=("python-pptx")
    python3 -c "from pypdf import PdfReader" 2>/dev/null || missing+=("pypdf")
    
    if [ ${#missing[@]} -gt 0 ]; then
        log_warn "缺少 Python 依赖：${missing[*]}"
        log_info "运行以下命令安装："
        echo "  pip3 install --break-system-packages ${missing[*]}"
        return 1
    fi
}

# 检查凭证
check_credentials() {
    local cred_file="$HOME/.openclaw/.email-credentials"
    
    if [ ! -f "$cred_file" ]; then
        log_error "凭证文件不存在：$cred_file"
        log_info "请创建邮箱凭证文件，格式如下："
        echo ""
        echo "  [main]"
        echo "  email = your-email@company.com"
        echo "  imap_server = imap.qiye.aliyun.com"
        echo "  imap_port = 993"
        echo "  auth_code = your-auth-code"
        echo ""
        log_info "参考文档：$SCRIPT_DIR/README.md"
        return 1
    fi
    
    # 检查权限
    local perms=$(stat -f "%Lp" "$cred_file" 2>/dev/null || stat -c "%a" "$cred_file" 2>/dev/null)
    if [ "$perms" != "600" ]; then
        log_warn "凭证文件权限不安全：$perms (建议：600)"
        log_info "运行：chmod 600 $cred_file"
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
