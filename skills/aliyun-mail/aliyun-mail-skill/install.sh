#!/bin/bash
# aliyun-mail skill 安装脚本

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OPENCLAW_DIR="$HOME/.openclaw"

echo "🚀 安装 aliyun-mail skill..."

# 1. 创建凭证目录
echo "1️⃣ 创建凭证配置..."
mkdir -p "$OPENCLAW_DIR"

if [ ! -f "$OPENCLAW_DIR/.email-credentials" ]; then
    cp "$SCRIPT_DIR/.email-credentials.example" "$OPENCLAW_DIR/.email-credentials"
    echo "   ✅ 创建邮箱凭证模板：$OPENCLAW_DIR/.email-credentials"
    echo "   ⚠️  请编辑此文件配置你的邮箱信息"
else
    echo "   ✓ 邮箱凭证已存在"
fi

if [ ! -f "$OPENCLAW_DIR/.feishu-credentials" ]; then
    cp "$SCRIPT_DIR/.feishu-credentials.example" "$OPENCLAW_DIR/.feishu-credentials"
    echo "   ✅ 创建飞书凭证模板：$OPENCLAW_DIR/.feishu-credentials"
    echo "   ⚠️  如需飞书推送，请编辑此文件配置"
else
    echo "   ✓ 飞书凭证已存在"
fi

# 2. 设置权限
echo "2️⃣ 设置权限..."
chmod 600 "$OPENCLAW_DIR/.email-credentials"
chmod 600 "$OPENCLAW_DIR/.feishu-credentials" 2>/dev/null || true
echo "   ✅ 凭证文件权限已保护 (600)"

# 3. 安装 Python 依赖
echo "3️⃣ 安装 Python 依赖..."
pip3 install --break-system-packages \
    imap-tools \
    python-docx \
    openpyxl \
    python-pptx \
    pypdf2 \
    requests

echo "   ✅ Python 依赖已安装"

# 4. 验证安装
echo "4️⃣ 验证安装..."
cd "$OPENCLAW_DIR/workspace"
if bash skills/aliyun-mail/aliyun-mail.sh test 2>&1 | grep -q "✅"; then
    echo "   ✅ 技能安装成功！"
else
    echo "   ⚠️  测试失败，请检查凭证配置"
fi

echo ""
echo "📚 下一步："
echo "1. 编辑 ~/.openclaw/.email-credentials 配置邮箱"
echo "2. 运行：bash skills/aliyun-mail/aliyun-mail.sh test"
echo "3. 查看文档：cat skills/aliyun-mail/SKILL.md"
echo ""

