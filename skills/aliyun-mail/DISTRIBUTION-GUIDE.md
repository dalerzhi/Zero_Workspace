# 📦 aliyun-mail-skill 分发说明

_给其他 Agent 使用的完整技能包_

---

## 📦 分发包内容

**文件**: `aliyun-mail-skill.tar.gz` (23KB)

**包含**:
```
aliyun-mail-skill/
├── SKILL.md                      # ⭐ 主文档（必读）
├── README.md                     # 详细指南
├── README-DISTRIBUTION.md        # 分发说明
├── INSTALL.md                    # 安装指南
├── aliyun-mail.sh                # 主脚本
├── install.sh                    # 自动安装
├── .email-credentials.example    # 邮箱模板
├── .feishu-credentials.example   # 飞书模板
├── .gitignore
├── VERSION
└── lib/
    ├── fetch_emails.py
    └── analyze_emails.py
```

---

## 🚀 使用方法

### 给其他 Agent 的步骤

**1. 发送分发包**
```
发送文件：aliyun-mail-skill.tar.gz
```

**2. 提供安装指令**
```bash
# 解压
tar -xzf aliyun-mail-skill.tar.gz

# 移动技能
cp -r aliyun-mail-skill ~/.openclaw/workspace/skills/aliyun-mail

# 运行安装
bash ~/.openclaw/workspace/skills/aliyun-mail/install.sh
```

**3. 配置凭证**
```bash
# 编辑邮箱配置
vi ~/.openclaw/.email-credentials

# 配置示例：
[main]
email = your-email@company.com
imap_server = imap.qiye.aliyun.com
imap_port = 993
auth_code = your-auth-code
```

**4. 测试**
```bash
cd ~/.openclaw/workspace
bash skills/aliyun-mail/aliyun-mail.sh test
```

---

## 📋 快速参考卡

### 基本用法
```bash
# 查看昨日邮件
bash skills/aliyun-mail/aliyun-mail.sh summary --days 1

# 发送到飞书
bash skills/aliyun-mail/aliyun-mail.sh summary --days 1 --send-feishu

# 指定日期范围
bash skills/aliyun-mail/aliyun-mail.sh summary \
  --since "2026-03-01" \
  --until "2026-03-08"

# 整理周报
bash skills/aliyun-mail/aliyun-mail.sh weekly-report \
  --since "2026-03-01" \
  --until "2026-03-07"
```

### 输出示例
```markdown
# 📧 邮件日报 (2026-03-09)

## 📊 概览
- 总邮件数：6
- 📬 收件人邮件：1
- 📧 抄送邮件：4 (仅需知悉)

## ⚡ 需要我处理
**账单确认** (财务@company.com)
- ⏰ 本周五前：请您确认 2 月账单

## 🔴 重要事项
**项目进度**
发件人：项目经理 | 时间：17:03
项目同步，需：对接，核实
```

---

## 🔐 安全说明

### 敏感信息处理
- ✅ **无硬编码**: 所有凭证都在独立文件中
- ✅ **Git 忽略**: 凭证文件已加入 .gitignore
- ✅ **权限保护**: 自动设置 600 权限
- ✅ **模板分离**: 提供示例模板，不含真实信息

### 凭证文件位置
- 邮箱：`~/.openclaw/.email-credentials`
- 飞书：`~/.openclaw/.feishu-credentials`

### 数据安全
- ✅ 附件不保存文件
- ✅ 只在内存中解析
- ✅ 定期清理报告（建议 30 天）

---

## 📊 功能清单

### 核心功能
- [x] IMAP 邮件收取
- [x] 多邮箱账户支持
- [x] 收件人/抄送识别
- [x] 行动项提取
- [x] 智能内容总结
- [x] 附件解析（Word/Excel/PPT/PDF）
- [x] 飞书消息推送

### 高级功能
- [x] 周报自动整理
- [x] 账单识别（金额/状态）
- [x] 订单识别（数量/日期）
- [x] 邮件分类（重要/待办/通知）
- [x] 自定义总结长度

---

## ⚠️ 依赖要求

### Python 包
```bash
pip3 install --break-system-packages \
  imap-tools==1.11.1 \
  python-docx==1.2.0 \
  openpyxl==3.1.5 \
  python-pptx==1.0.2 \
  pypdf2==3.0.1 \
  requests
```

### 系统要求
- Python 3.8+
- macOS / Linux
- IMAP 邮箱服务
- （可选）飞书应用

---

## 🆘 常见问题

### Q1: 授权码在哪里获取？
**A**: 登录邮箱网页版 → 设置 → 客户端设置 → 开启 IMAP → 生成授权码

### Q2: 支持哪些邮箱？
**A**: 
- ✅ 阿里云企业邮箱
- ✅ 阿里云个人邮箱
- ✅ Gmail（需应用专用密码）
- ✅ 其他 IMAP 邮箱

### Q3: 飞书推送失败？
**A**: 
1. 检查飞书应用权限
2. 确认 app_id 和 app_secret 正确
3. 测试：`bash skills/aliyun-mail/aliyun-mail.sh feishu-test`

### Q4: 如何配置定时任务？
**A**:
```bash
openclaw cron create email-daily-summary \
  --name "邮件日报" \
  --cron "0 8 * * *" \
  --session main \
  --announce
```

---

## 📚 文档索引

| 文档 | 用途 | 必读 |
|------|------|------|
| SKILL.md | 完整技能文档 | ⭐⭐⭐ |
| README-DISTRIBUTION.md | 分发说明 | ⭐⭐ |
| INSTALL.md | 安装指南 | ⭐⭐ |
| README.md | 详细使用 | ⭐ |

---

## 🎯 典型使用场景

### 场景 1：每日邮件摘要
```bash
# 每天早上 8 点自动运行
bash skills/aliyun-mail/aliyun-mail.sh summary --days 1 --send-feishu
```

**效果**: 15 秒掌握昨日所有邮件重点

### 场景 2：周报整理
```bash
# 每周五整理团队周报
bash skills/aliyun-mail/aliyun-mail.sh weekly-report \
  --since "2026-03-04" \
  --until "2026-03-08" \
  --sender "周书辉"
```

**效果**: 自动提取周报附件，生成结构化总结

### 场景 3：账单跟踪
```bash
# 查找最近 30 天的账单
bash skills/aliyun-mail/aliyun-mail.sh search \
  --subject "账单" \
  --days 30
```

**效果**: 自动提取金额、状态、截止日期

---

## 📞 技术支持

### 文档
- 主文档：`SKILL.md`
- 安装指南：`INSTALL.md`
- 故障排查：`SKILL.md` 故障排查章节

### 验证
```bash
# 检查安装
bash skills/aliyun-mail/aliyun-mail.sh test

# 检查依赖
pip3 list | grep -E "imap-tools|docx|openpyxl|pptx|pypdf"
```

---

## ✅ 验收清单

接收技能的 Agent 应该能够：

- [ ] 成功解压分发包
- [ ] 运行 install.sh 完成安装
- [ ] 配置邮箱凭证
- [ ] 通过 test 测试
- [ ] 收取并总结邮件
- [ ] （可选）发送到飞书
- [ ] （可选）整理周报

---

**版本**: 2.0  
**日期**: 2026-03-09  
**包大小**: 23KB  
**许可**: MIT

---

## 📦 快速复制指令

```bash
# 完整安装流程（接收方）
tar -xzf aliyun-mail-skill.tar.gz
cp -r aliyun-mail-skill ~/.openclaw/workspace/skills/aliyun-mail
bash ~/.openclaw/workspace/skills/aliyun-mail/install.sh
vi ~/.openclaw/.email-credentials
cd ~/.openclaw/workspace
bash skills/aliyun-mail/aliyun-mail.sh test
```
