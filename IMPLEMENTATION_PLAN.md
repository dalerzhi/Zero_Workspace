# 重置前自动总结 - 实施方案

## 🎯 目标

将 **Self-Improving Agent Skill** 与 **OpenClaw 会话重置机制** 结合，确保在每天凌晨 4 点重置前，自动总结并记录当天的工作和学习。

---

## 📋 三层保障机制

### 第一层：自动化总结（核心）

**时间**: 每天凌晨 3:00（重置前 1 小时）  
**执行**: OpenClaw Cron 自动触发  
**内容**:
- 扫描 Git 提交和文件变化
- 检查 `.learnings/` 中的学习记录
- 生成每日总结报告 (`memory/YYYY-MM-DD-daily-summary.md`)
- 更新 `MEMORY.md` 日期标记
- 整理待办事项交接

**脚本**: `scripts/auto-daily-summary.sh`

---

### 第二层：Heartbeat 检查（补充）

**时间**: 每天早上 8:00（用户起床后）  
**执行**: Heartbeat 机制  
**内容**:
- 检查昨晚的总结是否生成
- 确认学习记录是否完整
- 提醒需要补充的内容

**配置**: `HEARTBEAT.md`

---

### 第三层：完成即记录（习惯）

**时间**: 任务完成后立即  
**执行**: 人工 + 脚本辅助  
**内容**:
- 每完成一个非平凡任务，立即记录到 `.learnings/`
- 使用快速记录脚本或模板
- 避免积压到晚上

**脚本**: `scripts/quick-log.sh` (待创建)

---

## 🚀 实施步骤

### 步骤 1：测试总结脚本（立即）

```bash
cd /Users/a123456/.openclaw/workspace

# Dry Run 测试
./scripts/auto-daily-summary.sh --dry-run

# 实际运行（生成今日总结）
./scripts/auto-daily-summary.sh --force
```

**预期输出**:
- ✅ 生成 `memory/2026-03-07-daily-summary.md`
- ✅ 显示今日统计（Git 提交、学习记录等）
- ✅ 更新 `MEMORY.md` 日期标记

---

### 步骤 2：配置 OpenClaw Cron（今天完成）

使用 OpenClaw 的 `cron` 工具添加每日总结任务。

**方法 A：通过配置命令**
```bash
openclaw cron add --json '{
  "id": "daily-pre-reset-summary",
  "name": "每日重置前总结",
  "schedule": "0 3 * * *",
  "command": "cd /Users/a123456/.openclaw/workspace && ./scripts/auto-daily-summary.sh",
  "enabled": true,
  "timezone": "Asia/Shanghai"
}'
```

**方法 B：直接编辑 openclaw.json**
```json5
// ~/.openclaw/openclaw.json
{
  cron: {
    jobs: [
      {
        id: "daily-pre-reset-summary",
        name: "每日重置前总结",
        schedule: "0 3 * * *",
        command: "cd /Users/a123456/.openclaw/workspace && ./scripts/auto-daily-summary.sh",
        enabled: true,
        timezone: "Asia/Shanghai"
      }
    ]
  }
}
```

**验证**:
```bash
# 查看 cron 任务列表
openclaw cron list

# 手动触发测试
openclaw cron run daily-pre-reset-summary
```

---

### 步骤 3：配置 Heartbeat（可选）

编辑 `HEARTBEAT.md` 添加每日检查：

```markdown
# 每日检查

## 早上检查（8:00-9:00）

- [ ] 检查 `memory/$(date -d yesterday +%Y-%m-%d)-daily-summary.md` 是否生成
- [ ] 检查 `.learnings/` 中是否有昨天该记录但没记录的
- [ ] 更新 `MEMORY.md`  dengan 昨天的重要学习
- [ ] 整理今日待办事项

## 触发条件

- 如果昨天总结未生成 → 手动运行 `./scripts/auto-daily-summary.sh --force`
- 如果有学习记录 >5 条 → 提升到 `MEMORY.md`
- 如果有错误记录 → 检查是否已解决
```

---

### 步骤 4：创建快速记录脚本（本周完成）

创建 `scripts/quick-log.sh` 用于日常快速记录：

```bash
#!/bin/bash
# Quick Log - 快速记录学习/错误/功能请求
# 用法：./quick-log.sh learning|error|feature "描述"

TYPE=$1
MESSAGE=$2
TODAY=$(date +%Y-%m-%d)
TIMESTAMP=$(date "+%Y-%m-%dT%H:%M:%S%z")

case $TYPE in
    learning)
        FILE=".learnings/LEARNINGS.md"
        PREFIX="LRN"
        ;;
    error)
        FILE=".learnings/ERRORS.md"
        PREFIX="ERR"
        ;;
    feature)
        FILE=".learnings/FEATURE_REQUESTS.md"
        PREFIX="FEAT"
        ;;
esac

ID="${PREFIX}-${TODAY}-$(date +%H%M)"

cat >> "$FILE" << EOF

## [$ID] auto

**Logged**: $TIMESTAMP
**Priority**: medium
**Status**: pending

### Summary
$MESSAGE

---
EOF

echo "✅ 已记录：[$ID] $MESSAGE"
```

**用法**:
```bash
# 记录学习
./scripts/quick-log.sh learning "OpenClaw 会话重置机制详解"

# 记录错误
./scripts/quick-log.sh error "Nano Banana 2 安装失败 - 域名被墙"

# 记录功能请求
./scripts/quick-log.sh feature "需要自动总结机制"
```

---

## 📊 监控和验证

### 每日检查清单

```bash
# 1. 检查今日总结是否生成
ls -la /Users/a123456/.openclaw/workspace/memory/*-daily-summary.md | tail -1

# 2. 检查学习记录数量
grep -c "$(date +%Y-%m-%d)" /Users/a123456/.openclaw/workspace/.learnings/*.md

# 3. 检查 cron 任务状态
openclaw cron list

# 4. 检查 MEMORY.md 更新时间
head -3 /Users/a123456/.openclaw/workspace/MEMORY.md | grep "最后更新"
```

### 成功指标

| 指标 | 目标 | 检查频率 |
|------|------|----------|
| 每日总结生成率 | 100% | 每日 |
| 学习记录数量 | ≥1 条/天 | 每日 |
| MEMORY.md 更新 | ≥1 次/周 | 每周 |
| 记忆丢失错误 | 0 次 | 持续 |

---

## ⚠️ 异常处理

### 场景 1：总结任务失败

**检测**: 第二天早上发现没有昨日总结  
**处理**:
```bash
# 手动补生成
./scripts/auto-daily-summary.sh --force

# 检查 cron 日志
openclaw cron runs daily-pre-reset-summary | tail -20
```

### 场景 2：学习记录遗漏

**检测**: Heartbeat 检查发现 Git 有提交但无学习记录  
**处理**:
```bash
# 查看 git 变化
git log --since="yesterday" --oneline

# 手动补充记录
./scripts/quick-log.sh learning "补充记录：xxx"
```

### 场景 3：MEMORY.md 长期未更新

**检测**: 超过 7 天未更新  
**处理**:
```bash
# 扫描最近的学习记录
grep -h "## \[LRN-" .learnings/LEARNINGS.md | head -10

# 手动提升到 MEMORY.md
# (编辑 MEMORY.md，添加重要学习)
```

---

## 🔄 持续改进

### 每周回顾（建议周日晚上）

1. 检查本周总结报告完整性
2. 整理学习记录，提升到 MEMORY.md
3. 清理过期的待办事项
4. 优化总结脚本（如有需要）

### 每月回顾

1. 分析学习记录趋势（哪些类型最多？）
2. 检查"记忆丢失"类错误是否归零
3. 评估自动化程度是否需要提升
4. 更新实施方案文档

---

## 📁 文件清单

| 文件 | 用途 | 状态 |
|------|------|------|
| `scripts/auto-daily-summary.sh` | 自动总结脚本 | ✅ 已创建 |
| `scripts/daily-summary.sh` | 简易总结脚本 | ✅ 已创建 |
| `scripts/quick-log.sh` | 快速记录脚本 | ⏳ 待创建 |
| `scripts/pre-reset-summary.md` | 方案文档 | ✅ 已创建 |
| `IMPLEMENTATION_PLAN.md` | 实施方案（本文件） | ✅ 已创建 |
| `HEARTBEAT.md` | 心跳检查配置 | ⏳ 待更新 |
| `openclaw.json` | Cron 配置 | ⏳ 待更新 |

---

## 🎉 下一步行动

### 今天（2026-03-07）

- [ ] 测试 `auto-daily-summary.sh` 脚本
- [ ] 配置 OpenClaw Cron 任务
- [ ] 验证 cron 任务能正常执行
- [ ] 更新 `HEARTBEAT.md`

### 本周

- [ ] 创建 `quick-log.sh` 快速记录脚本
- [ ] 测试完整流程（总结→记录→提升）
- [ ] 收集使用反馈，优化脚本

### 下周

- [ ] 检查第一周的总结报告质量
- [ ] 根据实际使用情况调整 cron 时间
- [ ] 完善异常处理机制

---

**创建时间**: 2026-03-07  
**负责人**: Zero (AI Assistant)  
**状态**: 🚧 实施中
