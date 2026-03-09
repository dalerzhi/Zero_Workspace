# 📧 阿里云邮箱自动日报系统

_类似 `gog gmail` 的阿里云邮箱技能，支持自动收取、分析、总结_

---

## ✅ 功能清单

- ✅ **IMAP 收取邮件** - 支持指定日期范围
- ✅ **附件解析** - Word/Excel/PPT/PDF 自动读取内容
- ✅ **智能总结** - 自动生成邮件摘要
- ✅ **飞书推送** - 自动发送到飞书聊天
- ✅ **定时任务** - 每天早上 8 点自动运行

---

## 📁 文件结构

```
workspace/
├── skills/aliyun-mail/
│   ├── SKILL.md              # 技能说明
│   ├── aliyun-mail.sh        # 主脚本
│   ├── lib/
│   │   └── fetch_emails.py   # 邮件收取与总结
│   └── README-授权码.md      # 授权码指南
├── scripts/
│   └── email-daily-summary.sh  # 每日自动脚本
├── .credentials/
│   └── aliyun-mail.md        # 邮箱凭证（加密存储）
└── email-reports/
    └── YYYY-MM-DD/           # 每日报告目录
        └── YYYY-MM-DD-邮件日报.md
```

---

## 🔧 配置

### 1. 邮箱配置

凭证文件：`~/.openclaw/workspace/.credentials/aliyun-mail.md`

```markdown
### 主邮箱
- email: zhibin@cheersucloud.com
- imap_server: imap.qiye.aliyun.com
- imap_port: 993
- auth_code: Nf8JracDzQP4u4uu
```

**权限保护**：
```bash
chmod 600 .credentials/aliyun-mail.md
```

### 2. 飞书配置

环境变量（可选，默认已配置）：
```bash
export FEISHU_APP_ID="cli_a909ad9f75fadbb5"
export FEISHU_APP_SECRET="p1MtN6OZic92OCOpMgxaZdSzAvRfsrys"
```

---

## 📖 用法

### 快速开始

**收取昨日邮件并发送到飞书**：
```bash
cd /Users/a123456/.openclaw/workspace
bash scripts/email-daily-summary.sh
```

### 手动命令

**1. 收取最近 N 天邮件**：
```bash
bash skills/aliyun-mail/aliyun-mail.sh summary --days 3
```

**2. 指定日期范围**：
```bash
bash skills/aliyun-mail/aliyun-mail.sh summary \
  --since "2026-03-07" \
  --until "2026-03-08"
```

**3. 仅列出邮件（不总结）**：
```bash
bash skills/aliyun-mail/aliyun-mail.sh list --days 1
```

**4. 提取附件**：
```bash
bash skills/aliyun-mail/aliyun-mail.sh attachments \
  --days 1 \
  --output-dir /tmp/attachments/
```

**5. 发送到飞书**：
```bash
bash skills/aliyun-mail/aliyun-mail.sh summary --days 1 \
  --send-feishu \
  --chat-id ou_xxxxxxxxxxxxx
```

---

## ⏰ 定时任务

### 方案 1：OpenClaw Cron（推荐）

每天早上 8 点自动运行：

```bash
# 任务已配置，ID: email-daily-summary
#  schedule: 0 8 * * *
#  command: bash scripts/email-daily-summary.sh
```

**查看任务状态**：
```bash
openclaw cron list
openclaw cron runs email-daily-summary | tail -10
```

**手动触发**：
```bash
openclaw cron run email-daily-summary
```

### 方案 2：系统 Cron

```bash
crontab -e

# 添加：
0 8 * * * cd /Users/a123456/.openclaw/workspace && bash scripts/email-daily-summary.sh >> /tmp/email-summary.log 2>&1
```

---

## 📊 输出示例

### 终端输出

```
📬 找到 1 个邮箱账户

📂 附件保存目录：/Users/a123456/.openclaw/workspace/email-reports/2026-03-09

正在收取 zhibin@cheersucloud.com 的邮件...
  ✓ 收取 3 封邮件

总计：3 封邮件

============================================================
# 📧 邮件日报 (2026-03-09)

## 概览
- 总邮件数：3
- 含附件邮件：3
- 附件总数：27

## 重点邮件

### 1. 回复：关于导入新防火墙品牌说明
**发件人**: junyi.cheng@cheersucloud.com
**时间**: 2026-03-08 17:03

**正文摘要**:
开凤你好：
感谢及时反馈。我们同步推进以下两项工作：
- 你提到有替代型号性价比更高，请于 3 月 9 日（周一）上午提供对方联系方式...
- 针对本次邮件中的疑问，我们将核实信息真实性，周一上午同步反馈结果。

**附件详情**:
  **1. 17553_InsertPic_FF70.png** (17.1KB)

---

### 2. 回复：X86 云服务结算单 to 蔚领~2026 年 2 月账单核对
**发件人**: chenkun.zhu@cheersucloud.com
**时间**: 2026-03-08 10:48

**正文摘要**:
Hi 丽珍，
 账单确认无误，可发与客户确认账单，谢谢~

---
============================================================

💾 总结已保存：/Users/a123456/.openclaw/workspace/email-reports/2026-03-09/2026-03-09-邮件日报.md

📤 发送到飞书：ou_7c6c3cdce8475c7a8de63811592c37f9
✅ 飞书发送成功：om_x100b55d5d6ad88a4b21992152417f15
```

### 飞书消息

自动发送到飞书聊天，格式与终端输出相同。

---

## 🔍 参数说明

| 参数 | 说明 | 默认值 | 示例 |
|------|------|--------|------|
| `--days N` | 收取最近 N 天的邮件 | 1 | `--days 7` |
| `--since DATE` | 开始日期 (YYYY-MM-DD) | 昨天 | `--since 2026-03-01` |
| `--until DATE` | 结束日期 (YYYY-MM-DD) | 今天 | `--until 2026-03-08` |
| `--output-dir` | 附件保存目录 | `./email-reports/日期/` | `--output-dir /tmp/` |
| `--send-feishu` | 发送到飞书 | false | `--send-feishu` |
| `--chat-id` | 飞书聊天 ID | (必填) | `--chat-id ou_xxx` |
| `--include-attachments` | 是否读取附件内容 | true | `--include-attachments=false` |

---

## 📝 支持的附件格式

| 格式 | 扩展名 | 提取内容 |
|------|--------|----------|
| **Word** | `.docx`, `.doc` | 全文段落文本 |
| **Excel** | `.xlsx`, `.xls` | 前 5 行数据（前 2 个工作表） |
| **PPT** | `.pptx`, `.ppt` | 前 5 页文本 |
| **PDF** | `.pdf` | 前 5 页文本 |
| **图片** | `.png`, `.jpg`, `.gif` | 保存文件（不提取文字） |

---

## ⚠️ 故障排查

### 1. 登录失败
```
❌ 邮箱 zhibin@cheersucloud.com 连接失败：[AUTH] Authentication failed
```
**解决**：
- 检查授权码是否正确
- 确认 IMAP 服务已开启（阿里云邮箱设置 → 客户端设置）
- 检查网络/防火墙

### 2. 缺少依赖
```
❌ 缺少 imap-tools，运行：pip3 install imap-tools
```
**解决**：
```bash
pip3 install --break-system-packages imap-tools python-docx openpyxl python-pptx pypdf2
```

### 3. 飞书发送失败
```
❌ 飞书发送失败：tenant_access_token invalid
```
**解决**：
- 检查 `FEISHU_APP_ID` 和 `FEISHU_APP_SECRET` 环境变量
- 确认飞书应用权限正确

### 4. 附件读取失败
```
[Word 读取失败：...]
```
**解决**：
- 确认依赖已安装：`pip3 list | grep docx`
- 检查附件格式是否支持

---

## 🔒 安全

- ✅ 凭证文件权限：`chmod 600 .credentials/aliyun-mail.md`
- ✅ 授权码不在日志中显示
- ✅ 支持多邮箱账户配置
- ✅ 敏感内容可配置过滤规则

---

## 📈 优化建议

### 性能优化
- 大量附件时设置 `--include-attachments=false` 跳过内容提取
- 定期清理 `email-reports/` 目录（保留最近 30 天）

### 功能扩展
- 添加邮件分类（重要/普通/订阅）
- 支持 Gmail/Outlook 等其他邮箱
- 添加邮件搜索功能

---

**最后更新**: 2026-03-09  
**状态**: ✅ 已部署并测试通过  
**定时任务**: 每天 8:00 AM 自动运行
