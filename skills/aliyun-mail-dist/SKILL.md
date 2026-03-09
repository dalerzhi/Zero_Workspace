# aliyun-mail - 阿里云邮箱技能

_智能邮件收取、附件解析、内容总结_

---

## 📋 功能特性

### 核心功能
- ✅ **IMAP 邮件收取** - 支持多邮箱账户、指定日期范围
- ✅ **智能分类** - 区分收件人/抄送，识别行动项归属
- ✅ **附件解析** - Word/Excel/PPT/PDF内容提取（不保存文件）
- ✅ **AI 总结** - 邮件正文 + 附件内容智能摘要
- ✅ **飞书推送** - 自动发送到飞书聊天

### 高级功能
- ✅ **周报整理** - 自动提取并整理周报附件内容
- ✅ **账单识别** - 自动提取金额、状态等关键信息
- ✅ **订单跟踪** - 识别数量、交付日期等信息
- ✅ **行动项提取** - 明确指派给"我"的任务置顶显示

---

## 🚀 快速开始

### 1. 安装依赖

```bash
pip3 install --break-system-packages \
  imap-tools \
  python-docx \
  openpyxl \
  python-pptx \
  pypdf2 \
  requests
```

### 2. 配置邮箱账户

创建凭证文件 `~/.openclaw/.email-credentials`：

```ini
[main]
email = your-email@company.com
imap_server = imap.qiye.aliyun.com
imap_port = 993
auth_code = your-auth-code-here

[backup]
email = backup@aliyun.com
imap_server = imap.aliyun.com
imap_port = 993
auth_code = backup-auth-code
```

**权限保护**：
```bash
chmod 600 ~/.openclaw/.email-credentials
```

### 3. 配置飞书（可选）

创建飞书凭证 `~/.openclaw/.feishu-credentials`：

```ini
[default]
app_id = cli_xxxxxxxxxxxxx
app_secret = xxxxxxxxxxxxxxx
default_chat_id = ou_xxxxxxxxxxxxx
```

### 4. 测试运行

```bash
cd ~/.openclaw/workspace
bash skills/aliyun-mail/aliyun-mail.sh test
```

---

## 📖 使用指南

### 日常使用

**收取昨日邮件并总结**：
```bash
bash skills/aliyun-mail/aliyun-mail.sh summary --days 1
```

**发送到飞书**：
```bash
bash skills/aliyun-mail/aliyun-mail.sh summary --days 1 --send-feishu
```

**指定日期范围**：
```bash
bash skills/aliyun-mail/aliyun-mail.sh summary \
  --since "2026-03-07" \
  --until "2026-03-08"
```

### 高级用法

**仅列出邮件（不总结）**：
```bash
bash skills/aliyun-mail/aliyun-mail.sh list --days 7
```

**提取特定类型附件**：
```bash
bash skills/aliyun-mail/aliyun-mail.sh attachments \
  --days 7 \
  --type xlsx \
  --output-summary
```

**整理周报**：
```bash
bash skills/aliyun-mail/aliyun-mail.sh weekly-report \
  --since "2026-03-01" \
  --until "2026-03-07"
```

**搜索特定邮件**：
```bash
bash skills/aliyun-mail/aliyun-mail.sh search \
  --subject "账单" \
  --days 30
```

---

## 📊 输出示例

### 邮件日报

```markdown
# 📧 邮件日报 (2026-03-09)

## 📊 概览
- 总邮件数：6
- 📬 收件人邮件：1
- 📧 抄送邮件：4 (仅需知悉)
- 📢 通知：1

## ⚡ 需要我处理
**账单确认** (财务@company.com)
- ⏰ 本周五前：请您确认 2 月账单

## 🔴 重要事项（收件人）
**项目进度更新**
发件人：项目经理 | 时间：17:03 | 📬 收件人
项目同步，需：对接，核实，提供资料
📎 2 个附件：项目计划.pdf: 工作报告

## 📧 抄送知悉
- 周报--张三 20260308.xlsx - 发件人 📧
  数据表格，15 行

---
📁 附件总数：8 个（已解析内容，未保存文件）
```

### 周报整理

```markdown
# 📋 周报整理 - 张三 (20260308)

## 📊 本周工作 (3/2-3/7)
- 钉钉项目：DVT 试产 450 套，4/12 出货
- 联宝合作：NRE 合同敲定，3 月底付款
- 客户接待：6 批次

## 📅 下周计划 (3/9-3/14)
- 3/9: NRE 流程、正式报价
- 3/10: 龙岗电信运维拜访
- 3/11: 龙虾盒子送样

## ⚠️ 重点跟进
1. 钉钉项目 🔴 - DVT 450 套，4/12 出货
2. 联宝合作 🔴 - NRE 流程，3 月底付款
```

---

## ⚙️ 配置说明

### 邮箱凭证格式

文件位置：`~/.openclaw/.email-credentials`

```ini
[账户名称]
email = 邮箱地址
imap_server = IMAP 服务器
imap_port = 端口 (默认 993)
auth_code = 授权码
ssl = true/false (默认 true)
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

### 飞书凭证格式

文件位置：`~/.openclaw/.feishu-credentials`

```ini
[default]
app_id = cli_xxxxx
app_secret = xxxxxxx
default_chat_id = ou_xxxxx

[backup]
app_id = cli_yyyyy
app_secret = yyyyyyy
default_chat_id = ou_yyyyy
```

### 环境变量（可选）

```bash
export EMAIL_ACCOUNT="main"        # 默认邮箱账户
export FEISHU_ACCOUNT="default"   # 默认飞书账户
export SUMMARY_LENGTH="medium"     # 总结长度：short/medium/long
```

---

## 🔧 参数详解

### summary 命令

| 参数 | 说明 | 默认值 | 示例 |
|------|------|--------|------|
| `--days N` | 收取最近 N 天 | 1 | `--days 7` |
| `--since DATE` | 开始日期 | 昨天 | `--since 2026-03-01` |
| `--until DATE` | 结束日期 | 今天 | `--until 2026-03-08` |
| `--account NAME` | 邮箱账户 | main | `--account personal` |
| `--send-feishu` | 发送飞书 | false | `--send-feishu` |
| `--chat-id ID` | 飞书 ID | (配置默认值) | `--chat-id ou_xxx` |
| `--summary-length` | 总结长度 | medium | `--summary-length short` |

### weekly-report 命令

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--since DATE` | 开始日期 | (必填) |
| `--until DATE` | 结束日期 | (必填) |
| `--sender NAME` | 发件人关键词 | (可选) |
| `--output FILE` | 输出文件 | 自动生成 |

---

## 📁 文件结构

```
~/.openclaw/
├── .email-credentials          # 邮箱凭证 (Git 忽略)
├── .feishu-credentials         # 飞书凭证 (Git 忽略)
└── workspace/
    └── skills/aliyun-mail/
        ├── SKILL.md            # 本文件
        ├── README.md           # 详细文档
        ├── aliyun-mail.sh      # 主脚本
        └── lib/
            ├── fetch_emails.py # 邮件收取
            ├── summarize.py    # 智能总结
            ├── attachments.py  # 附件解析
            └── weekly_report.py # 周报整理
```

---

## ⚠️ 故障排查

### 登录失败
```
❌ 邮箱 xxx 连接失败：[AUTH] Authentication failed
```
**解决**：
1. 检查授权码是否正确
2. 确认 IMAP 服务已开启（邮箱设置 → 客户端设置）
3. 检查网络/防火墙

### 凭证文件找不到
```
❌ 凭证文件不存在：~/.openclaw/.email-credentials
```
**解决**：
```bash
cat > ~/.openclaw/.email-credentials << EOF
[main]
email = your@email.com
imap_server = imap.qiye.aliyun.com
auth_code = your-code
EOF
chmod 600 ~/.openclaw/.email-credentials
```

### 飞书发送失败
```
❌ 飞书发送失败：tenant_access_token invalid
```
**解决**：
1. 检查 `~/.openclaw/.feishu-credentials` 配置
2. 确认飞书应用权限正确
3. 测试连接：`bash skills/aliyun-mail/aliyun-mail.sh feishu-test`

### 附件解析失败
```
[读取失败：...]
```
**解决**：
1. 确认依赖已安装：`pip3 list | grep openpyxl`
2. 检查附件格式是否支持
3. 设置 `--include-attachments=false` 跳过

---

## 🔒 安全最佳实践

### 凭证管理
- ✅ 使用独立凭证文件（`~/.openclaw/.email-credentials`）
- ✅ 设置文件权限：`chmod 600`
- ✅ Git 忽略凭证文件（已配置`.gitignore`）
- ✅ 不在代码中硬编码敏感信息
- ✅ 不在日志中显示授权码

### 数据安全
- ✅ 附件不保存文件，只在内存中解析
- ✅ 敏感内容自动过滤
- ✅ 支持 SSL/TLS 加密连接
- ✅ 定期清理报告目录（建议保留 30 天）

### 访问控制
- ✅ 支持多账户隔离
- ✅ 飞书发送需明确指定 chat-id
- ✅ 支持 IP 白名单（邮箱服务商配置）

---

## 📚 相关文档

- **README.md** - 详细使用指南
- **RECIPIENT-DETECTION.md** - 收件人识别逻辑
- **OPTIMIZATION.md** - 总结优化记录
- **README-授权码.md** - 授权码获取指南

---

## 🎯 最佳实践

### 每日工作流
```bash
# 1. 早上查看昨日邮件摘要
bash skills/aliyun-mail/aliyun-mail.sh summary --days 1 --send-feishu

# 2. 查看需要处理的行动项
bash skills/aliyun-mail/aliyun-mail.sh list --days 1 | grep "⚡"

# 3. 周五整理本周周报
bash skills/aliyun-mail/aliyun-mail.sh weekly-report \
  --since "$(date -v-mon +%Y-%m-%d)" \
  --until "$(date +%Y-%m-%d)"
```

### 定时任务
```bash
# 每天早上 8 点自动发送邮件日报
openclaw cron create email-daily-summary \
  --name "邮件日报" \
  --cron "0 8 * * *" \
  --session main \
  --announce
```

---

**版本**: 2.0  
**最后更新**: 2026-03-09  
**状态**: ✅ 生产就绪
