# Agent Task Runner

在 `agent-watchdog.py` 之上，再包一层**人类可直接调用**的启动器：

- `scripts/run-agent-task.py`

目的：少手拼参数，默认带上合理的超时与重试策略。

## 支持的任务类型

### writing
适合：写作、改稿、总结、长文生成

默认：
- startup: 30s
- idle: 300s
- wall: 1800s
- retries: 1

### research
适合：调研、材料整理、方案对比

默认：
- startup: 30s
- idle: 300s
- wall: 1800s
- retries: 1

### coding
适合：编码、测试、改文件、跑命令

默认：
- startup: 45s
- idle: 600s
- wall: 3600s
- retries: 1

## 当前 backend

目前只接了本机已验证可用的：

- `claude` (`/opt/homebrew/bin/claude`)

`codex` 当前不在 PATH，所以**没有默认接进去**。等本机 codex 可用后，再接第二后端。

## 用法

### 1. 直接写作任务

```bash
python3 scripts/run-agent-task.py \
  --kind writing \
  --label article-draft \
  --task "写一篇关于组织奖励可见忙碌而不是效率的中文文章，1500字左右。"
```

### 2. 从文件读取长任务

```bash
python3 scripts/run-agent-task.py \
  --kind research \
  --label ai-topic-research \
  --task-file /tmp/task.txt
```

### 3. 编码任务 + 指定产物

```bash
python3 scripts/run-agent-task.py \
  --kind coding \
  --label watchdog-refactor \
  --task "重构 scripts/agent-watchdog.py，并把结果写到 reports/refactor-note.md" \
  --expect-file 'reports/*.md'
```

### 4. 先看最终命令，不执行

```bash
python3 scripts/run-agent-task.py \
  --kind writing \
  --label dry-run-demo \
  --task "写一段测试文字" \
  --dry-run
```

## 设计原则

1. 日常任务优先走 `run-agent-task.py`
2. 底层仍然统一落到 `agent-watchdog.py`
3. 复杂场景再直接调用 `agent-watchdog.py`
4. 没有 watchdog 的 agent 任务，不算合格编排

## 什么时候直接用 watchdog

以下情况可绕过 runner，直接用 `agent-watchdog.py`：

- 你要自定义 retry regex
- 你要接非 claude backend
- 你要精细控制 shell command
- 你要做特殊产物监控

## 当前建议

主会话默认这样分层：

- **简单/标准任务** → `run-agent-task.py`
- **复杂/特殊任务** → `agent-watchdog.py`

这样既不丢控制力，也不会每次手搓参数。
