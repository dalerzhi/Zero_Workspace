# 每日重置前自动总结机制

## 🎯 目标

在 OpenClaw 每日会话重置（凌晨 4:00）之前，自动总结当天的工作并记录到学习系统中，确保不丢失任何重要上下文。

## ⏰ 时间安排

| 时间 | 事件 |
|------|------|
| 03:00 | 自动总结任务触发 |
| 03:00-03:30 | 扫描工作、生成报告、记录学习 |
| 04:00 | OpenClaw 会话重置 |

## 📋 总结内容

### 1. 工作扫描
- Git 提交记录（今天 vs 昨天）
- 新增/修改的文件
- 完成的任务清单

### 2. 学习记录检查
- `.learnings/LEARNINGS.md` - 今天的新学习
- `.learnings/ERRORS.md` - 今天的错误记录
- `.learnings/FEATURE_REQUESTS.md` - 新功能请求
- 检查是否有遗漏需要记录的内容

### 3. 记忆更新
- 将重要学习提升到 `MEMORY.md`
- 更新 `AGENTS.md` / `TOOLS.md`（如有通用经验）
- 清理过期的待办事项

### 4. 待办交接
- 未完成的任务整理
- 明日优先事项
- 需要持续关注的问题

## 🔧 实现方式

### 方案 A：OpenClaw Cron（推荐）

使用 OpenClaw 内置的 `cron` 工具，在凌晨 3 点自动触发总结任务。

**配置示例** (`openclaw.json`):

```json5
{
  cron: {
    jobs: [
      {
        id: "daily-pre-reset-summary",
        name: "每日重置前总结",
        schedule: "0 3 * * *",  // 每天凌晨 3 点
        command: "openclaw sessions spawn --task \"执行每日总结任务：1. 扫描今日工作 2. 检查学习记录 3. 更新 MEMORY.md 4. 生成待办清单\" --label daily-summary --runtime subagent --mode run",
        enabled: true,
        timezone: "Asia/Shanghai"
      }
    ]
  }
}
```

**优点**：
- 原生支持，无需外部依赖
- 可以直接调用 OpenClaw 工具
- 有完整的日志和错误处理

### 方案 B：系统 Cron + 脚本

使用 macOS 系统 cron 执行总结脚本。

**Crontab 配置**:
```bash
# 每天凌晨 3 点执行总结
0 3 * * * cd /Users/a123456/.openclaw/workspace && ./scripts/daily-summary.sh >> ~/logs/daily-summary.log 2>&1
```

**优点**：
- 简单直接
- 不依赖 OpenClaw 运行状态
- 可以独立调试

### 方案 C：Heartbeat 检查（补充）

在 `HEARTBEAT.md` 中添加每日检查项，由心跳机制触发。

**HEARTBEAT.md**:
```markdown
# 每日检查（凌晨时段）

- [ ] 检查 .learnings/ 中是否有今天该记录但没记录的
- [ ] 扫描 git log，确认完成的任务已记录
- [ ] 更新 MEMORY.md  dengan 今天的重要学习
- [ ] 整理未完成的任务到 TODO.md
```

**优点**：
- 灵活，可以交互式确认
- 适合需要人工判断的场景

## 📊 输出格式

### 每日总结报告 (`memory/YYYY-MM-DD-daily-summary.md`)

```markdown
# 每日总结 - 2026-03-07

## ✅ 完成的工作

1. 安装了 Self-Improving Agent Skill
2. 配置了 Izwi TTS 男声音色
3. 生成了头像图片 (zero-avatar.png)
4. 设计了"完成即更新"保障机制

## 📚 新增学习

- LRN-20260307-001: OpenClaw 会话重置机制
- LRN-20260307-002: 重置前自动总结方案
- ERR-20260307-001: 记忆丢失问题（已修复）

## 🔄 待办交接

- [ ] 实现 cron 自动总结任务
- [ ] 测试总结报告生成
- [ ] 配置 MEMORY.md 自动更新

## 💡 重要洞察

- 会话重置是上下文丢失的主要原因
- 必须在重置前自动总结，不能依赖人工
- 学习记录要及时，最好"完成即记录"
```

## 🚀 实施步骤

### 阶段 1：手动总结（立即开始）

1. 每天晚上手动运行总结脚本
2. 检查学习记录是否完整
3. 更新 MEMORY.md

### 阶段 2：半自动总结（1 周内）

1. 配置 Heartbeat 每日检查
2. 用 cron 触发总结任务
3. 人工确认总结报告

### 阶段 3：全自动总结（2 周内）

1. 总结任务自动执行
2. 学习自动提升到 MEMORY.md
3. 待办自动整理和交接
4. 异常情况人工介入

## ⚠️ 注意事项

1. **时区问题**：确保 cron 使用 Asia/Shanghai 时区
2. **幂等性**：总结任务可以重复执行，不会重复记录
3. **错误处理**：总结失败不影响正常会话重置
4. **隐私保护**：总结内容不发送到外部

## 📈 成功指标

- [ ] 每天至少有 1 条学习记录
- [ ] MEMORY.md 每周至少更新 1 次
- [ ] 无"记忆丢失"类错误
- [ ] 待办事项有清晰的交接记录

---

**创建时间**: 2026-03-07
**最后更新**: 2026-03-07
