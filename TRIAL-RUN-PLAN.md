# 试跑计划 - 自动总结机制

_开始时间：2026-03-07 11:47_

---

## 🎯 试跑目标

验证 **每日重置前自动总结机制** 的有效性和可靠性，确保：
1. 每天自动生成总结报告
2. 学习记录不遗漏
3. MEMORY.md 及时更新
4. 会话重置后上下文不丢失

---

## ⚙️ 配置总览

| 项目 | 配置 | 说明 |
|------|------|------|
| **重置时间** | 每天 7:00 AM | `session.reset.atHour: 7` |
| **总结时间** | 每天 6:00 AM | Cron: `0 6 * * *` |
| **Heartbeat** | 每天 8:00-9:00 AM | 用户起床后检查 |
| **时区** | Asia/Shanghai | 与用户所在地一致 |

---

## 📦 已配置组件

### 1. OpenClaw 配置 (`~/.openclaw/openclaw.json`)

```json5
{
  "session": {
    "reset": {
      "mode": "daily",
      "atHour": 7
    }
  },
  "cron": {
    "jobs": [
      {
        "id": "daily-pre-reset-summary",
        "name": "每日重置前总结",
        "schedule": "0 6 * * *",
        "command": "cd /Users/a123456/.openclaw/workspace && ./scripts/auto-daily-summary.sh",
        "enabled": true,
        "timezone": "Asia/Shanghai",
        "timeoutMs": 1800000
      }
    ]
  }
}
```

### 2. 脚本文件

| 脚本 | 用途 | 状态 |
|------|------|------|
| `scripts/auto-daily-summary.sh` | 自动总结（核心） | ✅ 已创建 |
| `scripts/quick-log.sh` | 快速记录学习 | ✅ 已创建 |
| `scripts/daily-summary.sh` | 简易总结 | ✅ 已创建 |

### 3. 文档文件

| 文件 | 用途 | 状态 |
|------|------|------|
| `HEARTBEAT.md` | 每日检查清单 | ✅ 已更新 |
| `IMPLEMENTATION_PLAN.md` | 实施方案 | ✅ 已创建 |
| `TRIAL-RUN-PLAN.md` | 试跑计划（本文件） | ✅ 已创建 |

---

## 📊 试跑周期

### 第一阶段：功能验证（第 1-3 天）

**目标**：确保所有组件正常工作

**检查项**：
- [ ] Cron 任务准时触发（6:00 AM）
- [ ] 总结报告正确生成
- [ ] Git 提交统计准确
- [ ] 学习记录统计正确
- [ ] MEMORY.md 更新日期标记

**操作**：
```bash
# 每天早上检查
ls -la memory/*-daily-summary.md | tail -1
head -3 MEMORY.md | grep "最后更新"
```

### 第二阶段：稳定性测试（第 4-7 天）

**目标**：验证连续运行的稳定性

**检查项**：
- [ ] 连续 7 天无失败
- [ ] 总结报告质量稳定
- [ ] 无重复记录
- [ ] 文件大小合理（<1MB）

**操作**：
```bash
# 查看 cron 运行历史
openclaw cron runs daily-pre-reset-summary | tail -20

# 检查总结文件数量
ls memory/*-daily-summary.md | wc -l
```

### 第三阶段：优化调整（第 8-14 天）

**目标**：根据实际使用情况优化

**检查项**：
- [ ] 总结时间是否合适（6:00 AM）
- [ ] 重置时间是否合适（7:00 AM）
- [ ] 是否需要调整统计指标
- [ ] 是否有遗漏的学习记录

**操作**：
```bash
# 根据反馈调整配置
openclaw config set session.reset.atHour=8
openclaw config set cron.jobs[0].schedule="0 7 * * *"
```

---

## 🔍 每日检查清单

### 早上检查（8:00-9:00）

```bash
# 1. 检查总结是否生成
FILE="memory/$(date -d "yesterday" +%Y-%m-%d)-daily-summary.md"
if [ -f "$FILE" ]; then
    echo "✅ 总结已生成：$FILE"
else
    echo "❌ 总结未生成，手动补跑"
    ./scripts/auto-daily-summary.sh --force
fi

# 2. 检查学习记录
echo "昨日学习：$(grep -c "$(date -d "yesterday" +%Y-%m-%d)" .learnings/LEARNINGS.md 2>/dev/null || echo 0)"

# 3. 检查 MEMORY.md
head -3 MEMORY.md | grep "最后更新"
```

### 晚上检查（可选）

```bash
# 快速记录今天的学习
./scripts/quick-log.sh learning "今天学到的重要内容"
```

---

## 📈 成功指标

| 指标 | 目标值 | 检查频率 |
|------|--------|----------|
| 总结生成率 | 100% | 每日 |
| 学习记录 | ≥1 条/天 | 每日 |
| MEMORY.md 更新 | ≥1 次/周 | 每周 |
| Cron 失败次数 | 0 次 | 每周 |
| 记忆丢失错误 | 0 次 | 持续 |

---

## ⚠️ 异常处理

### 场景 1：总结未生成

**检测**：早上发现没有昨日总结  
**处理**：
```bash
# 1. 检查 cron 状态
openclaw cron list

# 2. 查看运行日志
openclaw cron runs daily-pre-reset-summary | tail -10

# 3. 手动补生成
./scripts/auto-daily-summary.sh --force
```

### 场景 2：学习记录遗漏

**检测**：Git 有提交但无学习记录  
**处理**：
```bash
# 1. 查看 git 变化
git log --since="yesterday" --oneline

# 2. 手动补充
./scripts/quick-log.sh learning "补充：xxx"
```

### 场景 3：总结文件过大

**检测**：文件 >1MB  
**处理**：
```bash
# 1. 检查文件内容
wc -l memory/*-daily-summary.md

# 2. 调整脚本，限制输出长度
# 编辑 auto-daily-summary.sh，减少 head -N 的值
```

---

## 📝 试跑日志

### Day 1 (2026-03-07) - 配置和测试

**完成**：
- ✅ 修改重置时间为 7:00 AM (`session.reset.atHour: 7`)
- ✅ 配置 Cron 任务（6:00 AM 触发，ID: `087fc5cb-be8a-4938-b1fd-beb0db3d41de`）
- ✅ 创建自动总结脚本 (`auto-daily-summary.sh`)
- ✅ 创建快速记录脚本 (`quick-log.sh`)
- ✅ 更新 HEARTBEAT.md
- ✅ 测试脚本运行成功
- ✅ 生成第一份总结报告 (`memory/2026-03-07-daily-summary.md`)

**Cron 任务详情**：
```
ID: 087fc5cb-be8a-4938-b1fd-beb0db3d41de
名称：每日重置前总结
时间：每天 6:00 AM (Asia/Shanghai)
类型：Isolated session
交付：none（内部执行）
下次运行：18 小时后
```

**问题**：无

**备注**：明天早上 6 点后检查 Cron 是否自动触发

---

### Day 2 (2026-03-08) - 待填写

**检查**：
- [ ] Cron 是否自动触发
- [ ] 总结是否生成
- [ ] 学习记录是否完整

**问题**：_待填写_

**备注**：_待填写_

---

## 🎉 试跑完成标准

满足以下条件视为试跑成功：

- [ ] 连续 7 天总结自动生成
- [ ] 无 Cron 任务失败
- [ ] 学习记录 ≥5 条/周
- [ ] MEMORY.md 更新 ≥1 次
- [ ] 无记忆丢失类错误
- [ ] 用户满意度高

**预计完成时间**：2026-03-21

---

**创建时间**: 2026-03-07  
**负责人**: Zero  
**状态**: 🚧 试跑中（Day 1）
