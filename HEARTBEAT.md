# HEARTBEAT.md - 每日检查清单

_最后更新：2026-03-07_

---

## 📅 每日检查（早上 8:00-9:00）

### 1. 检查昨晚总结是否生成

```bash
# 检查昨日总结文件
ls -la /Users/a123456/.openclaw/workspace/memory/$(date -d "yesterday" +%Y-%m-%d)-daily-summary.md 2>/dev/null || echo "❌ 总结未生成"
```

**如果未生成**：
```bash
# 手动补生成
cd /Users/a123456/.openclaw/workspace
./scripts/auto-daily-summary.sh --force
```

---

### 2. 检查学习记录

```bash
# 检查昨日学习数量
echo "昨日学习记录："
grep -c "$(date -d "yesterday" +%Y-%m-%d)" .learnings/LEARNINGS.md 2>/dev/null || echo "0"

echo "昨日错误记录："
grep -c "$(date -d "yesterday" +%Y-%m-%d)" .learnings/ERRORS.md 2>/dev/null || echo "0"
```

**如果有 Git 提交但无学习记录**：
```bash
# 查看昨日 git 变化
git log --since="yesterday" --until="today" --oneline

# 手动补充记录
./scripts/quick-log.sh learning "补充记录：xxx"
```

---

### 3. 检查 MEMORY.md 更新

```bash
# 检查最后更新时间
head -3 MEMORY.md | grep "最后更新"
```

**如果超过 3 天未更新**：
- 检查 `.learnings/` 中是否有需要提升的学习
- 手动整理重要学习到 `MEMORY.md`

---

### 4. 整理今日待办

```bash
# 查看待办事项
cat TODO.md 2>/dev/null || echo "无待办文件"
```

**更新待办**：
- 完成的事项标记为 `[x]`
- 添加新的待办事项
- 删除过期事项

---

## 📊 每周检查（周日晚上）

### 周回顾

- [ ] 检查本周总结报告完整性
- [ ] 整理学习记录，提升到 `MEMORY.md`
- [ ] 清理过期的待办事项
- [ ] 检查 cron 任务运行日志

```bash
# 查看 cron 运行历史
openclaw cron runs daily-pre-reset-summary | tail -20
```

---

## ⚠️ 异常情况处理

### 总结任务失败

**检测**：连续 2 天无总结文件  
**处理**：
1. 检查 cron 状态：`openclaw cron list`
2. 手动运行：`./scripts/auto-daily-summary.sh --force`
3. 查看日志：`openclaw cron runs daily-pre-reset-summary`

### 学习记录遗漏

**检测**：Git 有提交但 `.learnings/` 无记录  
**处理**：
1. 查看 git 变化：`git log --since="3 days ago" --oneline`
2. 手动补充：`./scripts/quick-log.sh learning "xxx"`

### MEMORY.md 长期未更新

**检测**：超过 7 天未更新  
**处理**：
1. 扫描最近学习：`grep -h "## \[LRN-" .learnings/LEARNINGS.md | head -10`
2. 手动提升到 `MEMORY.md`

---

## 📈 成功指标

| 指标 | 目标 | 检查频率 |
|------|------|----------|
| 每日总结生成率 | 100% | 每日 |
| 学习记录数量 | ≥1 条/天 | 每日 |
| MEMORY.md 更新 | ≥1 次/周 | 每周 |
| 记忆丢失错误 | 0 次 | 持续 |

---

**配置说明**：
- Session 重置：**已禁用**（永不自动重置）
- Context 监控：每 2 小时自动检查，超过 70% 时自动整理记忆
- Heartbeat 检查：每天 8:00-9:00 AM（用户起床后）

**更新**：2026-03-09 - 禁用自动重置，改为 Context 监控
