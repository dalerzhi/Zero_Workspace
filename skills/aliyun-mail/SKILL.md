# aliyun-mail - 阿里云邮箱技能

_收取邮件、解析附件、生成总结_

## 功能

- ✅ 多邮箱账户支持
- ✅ IMAP 收取邮件（指定日期范围）
- ✅ 附件提取（Word/Excel/PPT/PDF）
- ✅ 附件内容读取
- ✅ 邮件 + 附件智能总结
- ✅ 飞书/微信消息推送

## 依赖

```bash
pip3 install imap-tools python-docx openpyxl python-pptx pypdf2
```

## 配置

凭证文件：`~/.openclaw/workspace/.credentials/aliyun-mail.md`

格式：
```markdown
### 邮箱 1
- email: xxx@company.com
- imap_server: imap.qiye.aliyun.com
- imap_port: 993
- auth_code: xxxxxxxxxxxxxxxx

### 邮箱 2
- email: xxx@aliyun.com
- imap_server: imap.aliyun.com
- imap_port: 993
- auth_code: xxxxxxxxxxxxxxxx
```

## 用法

### 1. 收取昨日邮件并总结

```bash
cd /Users/a123456/.openclaw/workspace
bash skills/aliyun-mail/aliyun-mail.sh summary --days 1
```

### 2. 收取指定日期范围

```bash
bash skills/aliyun-mail/aliyun-mail.sh summary \
  --since "2026-03-07" \
  --until "2026-03-08"
```

### 3. 仅列出邮件（不总结）

```bash
bash skills/aliyun-mail/aliyun-mail.sh list --days 1
```

### 4. 提取附件

```bash
bash skills/aliyun-mail/aliyun-mail.sh attachments \
  --days 1 \
  --output-dir /tmp/email-attachments/
```

### 5. 发送到飞书

```bash
bash skills/aliyun-mail/aliyun-mail.sh summary --days 1 \
  --send-feishu \
  --chat-id ou_xxxxxxxxxxxxx
```

## 参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--days N` | 收取最近 N 天的邮件 | 1 |
| `--since DATE` | 开始日期 (YYYY-MM-DD) | 昨天 |
| `--until DATE` | 结束日期 (YYYY-MM-DD) | 今天 |
| `--output-dir` | 附件保存目录 | ./email-attachments/ |
| `--send-feishu` | 发送到飞书 | false |
| `--chat-id` | 飞书聊天 ID | (必填，如果发送) |
| `--include-attachments` | 是否读取附件内容 | true |
| `--summary-length` | 总结长度 (short/medium/long) | medium |

## 输出示例

```markdown
# 📧 邮件日报 (2026-03-07)

## 概览
- 总邮件数：15
- 重要邮件：3
- 含附件：5

## 重点邮件

### 1. [重要] 项目进度更新 - 张三
**发件人**: zhangsan@company.com  
**时间**: 14:30  
**附件**: 项目计划.xlsx (已读取)

**摘要**: 
- 项目延期 2 天，主要因为...
- 需要下周评审...

**附件要点**:
- Q2 目标：完成 3 个模块
- 预算：50 万

---

### 2. 会议邀请 - 产品评审
**发件人**: product@company.com  
**时间**: 10:00  
**附件**: 无

**摘要**: 下周二下午 2 点，302 会议室...

---

## 其他邮件 (10 封)
- 系统通知 × 5
- 订阅邮件 × 3
- 其他 × 2
```

## 定时任务

配置每日早上 8 点自动运行：

```bash
openclaw cron create email-daily-summary \
  --schedule "0 8 * * *" \
  --command "cd /Users/a123456/.openclaw/workspace && bash skills/aliyun-mail/aliyun-mail.sh summary --days 1 --send-feishu --chat-id ou_xxx"
```

## 文件结构

```
skills/aliyun-mail/
├── SKILL.md              # 技能说明
├── aliyun-mail.sh        # 主脚本
├── lib/
│   ├── fetch_emails.py   # 邮件收取
│   ├── parse_attachments.py  # 附件解析
│   └── generate_summary.py   # 生成总结
└── README-授权码.md      # 授权码指南
```

## 故障排查

### 1. 登录失败
- 检查授权码是否正确
- 确认 IMAP 服务已开启
- 检查防火墙/网络

### 2. 附件读取失败
- 确认依赖已安装：`pip3 list | grep docx`
- 检查附件格式是否支持

### 3. 总结生成慢
- 附件过多时会变慢
- 可以设置 `--include-attachments=false` 跳过

## 安全

- 凭证文件权限：`chmod 600 .credentials/aliyun-mail.md`
- 授权码不在日志中显示
- 敏感内容可配置过滤规则
