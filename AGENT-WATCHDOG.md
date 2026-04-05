# Agent Watchdog

目标：**不要再把“任务已提交”误判成“agent 已经真正启动并在推进”。**

这套方案是面向终局目标写的，不继承旧脚本设计。

## 解决的问题

常见翻车方式：

1. 子 agent 命令根本不存在，但主 agent 以为已经起跑
2. 子 agent 启动后没有任何首条日志，主 agent 继续傻等
3. 子 agent 卡住无产物、无新日志，主 agent 没有超时机制
4. 子 agent 非瞬时失败后，主 agent 继续等待而不是降级

`script/agent-watchdog.py`（实际文件路径见下）就是为这几个问题准备的。

## 文件

- `scripts/agent-watchdog.py`

## 核心机制

### 1. Preflight（二进制预检）

启动前先检查 agent CLI 是否真的在 PATH 上：

- 有 `claude` 才能跑 Claude Code
- 有 `codex` 才能跑 Codex
- 有 `openclaw` 才能跑 OpenClaw CLI

如果二进制不存在，**立即失败**，不进入等待态。

### 2. Startup Timeout（启动超时）

如果进程启动后，在设定时间内没有出现**第一条输出**，判定启动失败：

- 默认 30 秒
- 适合抓“命令没跑起来”“被卡在初始化”“静默挂死”
- 注意：某些命令在 stdout 重定向到文件时会缓冲输出（例如 Python 默认缓冲）。这类命令请改成非缓冲模式，例如 `python3 -u ...`，否则 watchdog 会把它当作“无首条日志”处理

### 3. Idle Timeout（空转超时）

如果长时间没有：

- 新日志
- 新产物（可选 expect-file glob）

就判定为卡住，自动结束该尝试并按策略重试。

### 4. Wall Timeout（总时长上限）

单次尝试不允许无限跑。

### 5. Bounded Retries（有界重试）

只对这些情况重试：

- timeout / timed out
- 429 / 502 / 503 / 504
- server_error
- internal server error
- connection reset / ECONNRESET
- overloaded / try again
- idle_timeout / wall_timeout

对这些情况**不重试**：

- command not found
- No such file or directory
- 非瞬时业务错误
- 明确权限/提示词/路径问题

### 6. Status Output（状态可追）

每次运行都会落盘：

```text
.runs/agent-watchdog/<timestamp>-<label>/
  status.json
  attempt-01/
    agent.log
    meta.json
    result.json
  attempt-02/
    ...
```

这样主 agent 不是靠猜，而是靠状态文件判断：

- 是否成功启动
- 卡在哪一轮
- 为什么重试
- 最终失败原因是什么

## 推荐用法

### Claude Code（当前机器可用）

```bash
python3 scripts/agent-watchdog.py \
  --label article-writer \
  --binary claude \
  --command "claude --permission-mode bypassPermissions --print '写一篇关于组织奖励可见忙碌的中文长文'" \
  --cwd /Users/a123456/.openclaw/workspace \
  --startup-timeout 30 \
  --idle-timeout 300 \
  --wall-timeout 1800 \
  --retries 1
```

### Codex（只有安装后才能用）

```bash
python3 scripts/agent-watchdog.py \
  --label codex-test \
  --binary codex \
  --command "codex exec --full-auto 'your task here'" \
  --cwd /path/to/repo \
  --retries 1
```

### 带产物检测

```bash
python3 scripts/agent-watchdog.py \
  --label writer-with-artifact \
  --binary claude \
  --command "claude --permission-mode bypassPermissions --print '生成文章并保存到 out/article.md'" \
  --cwd /Users/a123456/.openclaw/workspace \
  --expect-file 'out/*.md' \
  --idle-timeout 180
```

## 主 agent 编排规则（以后默认）

### 必须做

1. **所有长任务 agent** 必须走 watchdog，不允许裸跑
2. **复杂 shell 命令** 必须显式传 `--binary`
3. 必须设置：
   - `--startup-timeout`
   - `--idle-timeout`
   - `--wall-timeout`
   - `--retries`
4. 任务若有明确交付物，必须加 `--expect-file`
5. 主 agent 的汇报基于：
   - 日志更新
   - 产物出现
   - status.json

### 不允许做

1. `nohup codex ... &` 之后直接默认它已经开始工作
2. 没首条日志还继续等
3. 无产物长时间卡住却不超时
4. 重试没有边界
5. 把“还在跑”当成真实进度

## 建议阈值

### 写作 / 研究类 agent
- startup: 30s
- idle: 300s
- wall: 1800s
- retries: 1

### 编码 / 测试类 agent
- startup: 45s
- idle: 600s
- wall: 3600s
- retries: 1-2

### 渲染 / 长构建类任务
- startup: 60s
- idle: 900s
- wall: 7200s
- retries: 0-1（避免重复耗资源）

## 当前已知事实

在这台机器上：

- `claude` 可用：`/opt/homebrew/bin/claude`
- `codex` 当前 **不在 PATH**

所以如果还想直接起 Codex，必须先安装/配置；否则 watchdog 会立刻 preflight fail，而不是进入傻等。

## 这套方案的意义

它不是“让子 agent 更聪明”。

它的价值是：

**把 agent 任务从“玄学等待”变成“可验证、可超时、可重试、可回收”的工程流程。**
