# 📦 aliyun-mail-skill 分发包

_智能邮件收取、附件解析、内容总结技能_

---

## 📋 包含内容

```
aliyun-mail-skill/
├── SKILL.md                      # 技能主文档（必读）
├── README.md                     # 详细使用指南
├── INSTALL.md                    # 安装指南
├── aliyun-mail.sh                # 主脚本
├── install.sh                    # 自动安装脚本
├── .email-credentials.example    # 邮箱凭证模板
├── .feishu-credentials.example   # 飞书凭证模板
├── .gitignore                    # Git 忽略配置
├── VERSION                       # 版本信息
└── lib/                          # Python 库
    ├── fetch_emails.py           # 邮件收取与总结
    ├── analyze_emails.py         # 邮件分析
    └── __pycache__/              # Python 缓存
```

---

## 🚀 快速开始

### 方法 1：自动安装（推荐）

```bash
# 1. 运行安装脚本
bash aliyun-mail-skill/install.sh

# 2. 编辑凭证配置
vi ~/.openclaw/.email-credentials

# 3. 测试
cd ~/.openclaw/workspace
bash skills/aliyun-mail/aliyun-mail.sh test
```

### 方法 2：手动安装

```bash
# 1. 复制 skill
cp -r aliyun-mail-skill ~/.openclaw/workspace/skills/aliyun-mail

# 2. 创建凭证
cat > ~/.openclaw/.email-credentials << EOF
[main]
email = your-email@company.com
imap_server = imap.qiye.aliyun.com
imap_port = 993
auth_code = your-auth-code
EOF

chmod 600 ~/.openclaw/.email-credentials

# 3. 安装依赖
pip3 install --break-system-packages \
  imap-tools python-docx openpyxl \
  python-pptx pypdf2 requests

# 4. 测试
cd ~/.openclaw/workspace
bash skills/aliyun-mail/aliyun-mail.sh test
```

---

## 📖 基本用法

### 查看昨日邮件

```bash
bash skills/aliyun-mail/aliyun-mail.sh summary --days 1
```

### 发送到飞书

```bash
bash skills/aliyun-mail/aliyun-mail.sh summary --days 1 --send-feishu
```

### 整理周报

```bash
bash skills/aliyun-mail/aliyun-mail.sh weekly-report \
  --since "2026-03-01" \
  --until "2026-03-07"
```

---

## 🔧 配置说明

### 邮箱凭证

文件：`~/.openclaw/.email-credentials`

```ini
[main]
email = your-email@company.com
imap_server = imap.qiye.aliyun.com
imap_port = 993
auth_code = your-auth-code
ssl = true
```

**支持多账户**：
```ini
[main]
email = work@company.com
imap_server = imap.qiye.aliyun.com
auth_code = xxx

[personal]
email = personal@gmail.com
imap_server = imap.gmail.com
auth_code = xxx
```

### 飞书凭证（可选）

文件：`~/.openclaw/.feishu-credentials`

```ini
[default]
app_id = cli_xxxxxxxxxxxxx
app_secret = xxxxxxxxxxxxxxx
default_chat_id = ou_xxxxxxxxxxxxx
```

---

## 📊 功能特性

### 核心功能
- ✅ IMAP 邮件收取（支持多账户）
- ✅ 智能分类（收件人/抄送识别）
- ✅ 附件解析（Word/Excel/PPT/PDF）
- ✅ AI 内容总结（不保存附件）
- ✅ 飞书消息推送

### 高级功能
- ✅ 周报自动整理
- ✅ 账单/订单识别
- ✅ 行动项提取
- ✅ 多邮箱账户支持

---

## ⚠️ 重要说明

### 安全
1. **凭证保护**: 凭证文件权限自动设置为 600
2. **Git 忽略**: 凭证文件已加入 .gitignore
3. **不保存附件**: 附件只在内存中解析，不保存文件
4. **敏感信息**: 所有敏感信息都在独立凭证文件中

### 依赖
- Python 3.8+
- imap-tools
- python-docx
- openpyxl
- python-pptx
- pypdf2
- requests

### 系统要求
- macOS / Linux
- 需要 pip3 权限（或使用 virtualenv）

---

## 🆘 故障排查

### 登录失败
```
❌ 邮箱 xxx 连接失败：[AUTH] Authentication failed
```
**解决**:
1. 检查授权码是否正确
2. 确认邮箱 IMAP 服务已开启
3. 检查网络连接

### 依赖缺失
```
❌ 缺少 imap-tools
```
**解决**:
```bash
pip3 install --break-system-packages imap-tools
```

### 飞书发送失败
```
❌ 飞书凭证未配置
```
**解决**:
创建 `~/.openclaw/.feishu-credentials` 并配置

---

## 📚 文档

- **SKILL.md** - 完整技能文档（必读）
- **README.md** - 详细使用指南
- **INSTALL.md** - 安装指南

---

## 📞 支持

如有问题，请查看 SKILL.md 中的故障排查章节。

---

**版本**: 2.0  
**日期**: 2026-03-09  
**许可**: MIT
