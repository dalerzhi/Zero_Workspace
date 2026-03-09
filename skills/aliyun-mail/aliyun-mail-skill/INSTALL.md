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
