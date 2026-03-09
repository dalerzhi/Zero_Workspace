# aliyun-mail-skill 分发打包脚本

cd "$(dirname "$0")"

DIST_DIR="aliyun-mail-skill"
rm -rf "$DIST_DIR"
mkdir -p "$DIST_DIR"

echo "📦 正在打包 aliyun-mail skill..."

# 复制核心文件
cp SKILL.md "$DIST_DIR/"
cp README.md "$DIST_DIR/"
cp aliyun-mail.sh "$DIST_DIR/"
cp -r lib "$DIST_DIR/"

# 复制模板文件
cp ../../.email-credentials.template "$DIST_DIR/.email-credentials.example"
cp ../../.feishu-credentials.template "$DIST_DIR/.feishu-credentials.example"

# 创建安装脚本
cat > "$DIST_DIR/install.sh" << 'INSTALL_SCRIPT'
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

INSTALL_SCRIPT

chmod +x "$DIST_DIR/install.sh"

# 创建使用说明
cat > "$DIST_DIR/INSTALL.md" << 'INSTALL_DOC'
# aliyun-mail Skill 安装指南

## 📦 快速安装

```bash
# 1. 运行安装脚本
bash install.sh

# 2. 配置邮箱凭证
vi ~/.openclaw/.email-credentials

# 3. 测试
cd ~/.openclaw/workspace
bash skills/aliyun-mail/aliyun-mail.sh test
```

## 🔧 手动安装

### 1. 复制 Skill

```bash
cp -r aliyun-mail-skill ~/.openclaw/workspace/skills/aliyun-mail
```

### 2. 创建凭证

**邮箱凭证** `~/.openclaw/.email-credentials`:
```ini
[main]
email = your-email@company.com
imap_server = imap.qiye.aliyun.com
imap_port = 993
auth_code = your-auth-code
```

**飞书凭证** (可选) `~/.openclaw/.feishu-credentials`:
```ini
[default]
app_id = cli_xxxxxxxxxxxxx
app_secret = xxxxxxxxxxxxxxx
default_chat_id = ou_xxxxxxxxxxxxx
```

### 3. 安装依赖

```bash
pip3 install --break-system-packages \
  imap-tools \
  python-docx \
  openpyxl \
  python-pptx \
  pypdf2 \
  requests
```

### 4. 测试

```bash
cd ~/.openclaw/workspace
bash skills/aliyun-mail/aliyun-mail.sh test
```

## 📖 使用文档

完整文档：`skills/aliyun-mail/SKILL.md`

### 基本用法

```bash
# 查看昨日邮件
bash skills/aliyun-mail/aliyun-mail.sh summary --days 1

# 发送到飞书
bash skills/aliyun-mail/aliyun-mail.sh summary --days 1 --send-feishu

# 整理周报
bash skills/aliyun-mail/aliyun-mail.sh weekly-report \
  --since "2026-03-01" \
  --until "2026-03-07"
```

## ⚠️ 注意事项

1. **凭证安全**: 凭证文件权限自动设置为 600
2. **Git 忽略**: 凭证文件已加入 .gitignore
3. **多账户**: 支持配置多个邮箱账户
4. **附件处理**: 默认不保存附件文件，只解析内容

## 🆘 故障排查

### 登录失败
```
❌ 邮箱 xxx 连接失败：[AUTH] Authentication failed
```
**解决**: 检查授权码是否正确，确认 IMAP 服务已开启

### 依赖缺失
```
❌ 缺少 imap-tools
```
**解决**: `pip3 install imap-tools`

### 飞书发送失败
```
❌ 飞书凭证未配置
```
**解决**: 创建 `~/.openclaw/.feishu-credentials`

## 📞 支持

文档：`skills/aliyun-mail/SKILL.md`
INSTALL_DOC

# 创建 .gitignore
cat > "$DIST_DIR/.gitignore" << 'GITIGNORE'
# 敏感信息
.email-credentials
.feishu-credentials

# Python
__pycache__/
*.pyc
*.pyo

# 报告文件
email-reports/

# 临时文件
*.tmp
*.log
GITIGNORE

# 创建版本信息
cat > "$DIST_DIR/VERSION" << VERSION
aliyun-mail-skill
版本：2.0
日期：$(date +%Y-%m-%d)
包含文件:
- SKILL.md (主文档)
- README.md (详细指南)
- aliyun-mail.sh (主脚本)
- lib/ (Python 库)
- install.sh (安装脚本)
- .email-credentials.example (邮箱模板)
- .feishu-credentials.example (飞书模板)
VERSION

# 设置权限
chmod +x "$DIST_DIR/aliyun-mail.sh"
chmod +x "$DIST_DIR/install.sh"

echo "✅ 打包完成！"
echo ""
echo "📦 分发包位置：$DIST_DIR/"
echo ""
echo "📋 包含文件:"
find "$DIST_DIR" -type f | sort
echo ""
echo "🚀 安装方法:"
echo "  1. 复制 $DIST_DIR 到目标位置"
echo "  2. 运行：bash $DIST_DIR/install.sh"
echo "  3. 配置凭证：vi ~/.openclaw/.email-credentials"
echo ""
