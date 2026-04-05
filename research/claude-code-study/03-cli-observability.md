# Claude Code CLI 可观测性与输出架构研究

> 源码版本：`tmp-claude-code-main-src/claude-code-main`
> 研究日期：2026-04-05

---

## 一、核心问题：原始运行态事件 → 可消费的状态与输出

Claude Code 面对的挑战：LLM agent 的原始事件流（streaming delta、tool call、permission 请求、内部诊断）必须同时服务于三个消费者——终端用户、SDK 宿主（上层 orchestrator）、以及远程会话管理平面（CCR）。它的解法是一个**三层漏斗**：

```
层1: 原始 API 事件流 (Anthropic API → streaming delta, tool_use, message_stop...)
      ↓ [print.ts: 5594 行的巨型编排器]
层2: 结构化 SDK 消息 (StdoutMessage 联合类型)
      ↓ [StructuredIO / RemoteIO]
层3: 传输层 (WebSocket / SSE+POST / Hybrid) → 消费者
```

### 层1→层2：print.ts 的事件路由

`print.ts:runHeadless()` 是主 REPL 循环，它：

1. **消费 stdin** — 通过 `StructuredIO.read()` 解析 NDJSON 行为 `StdinMessage`
2. **路由 control_request** — 21 种变体（`initialize`、`can_use_tool`、`interrupt`、`mcp_*`、`rewind_files`、`set_model` 等），每种有独立处理逻辑
3. **编排 ask()** — 用户 prompt 入队 → 调用 LLM → 产生 assistant/stream_event/system 消息
4. **输出到 Stream** — `output.enqueue(message)` 推入 `Stream<StdoutMessage>`
5. **生命周期广播** — `notifyCommandLifecycle(uuid, 'started'|'completed')`、`notifySessionStateChanged(idle|running|requires_action)`

关键设计：**print.ts 不直接写 stdout**。它只操作一个 `Stream<StdoutMessage>` 队列，由下游的 IO 层决定序列化和传输方式。这实现了输出格式与业务逻辑的完全解耦。

### 层2：StdoutMessage 类型体系

```typescript
StdoutMessage =
  | SDKMessage              // user/assistant/system 完整消息
  | SDKStreamlinedTextMessage       // 精简文本（streamlined 模式）
  | SDKStreamlinedToolUseSummaryMessage // 工具使用摘要
  | SDKPostTurnSummaryMessage       // 轮次结束摘要
  | SDKPartialAssistantMessage      // stream_event（增量 delta）
  | SDKControlResponse      // 控制响应
  | SDKControlRequest       // 控制请求（双向）
  | SDKControlCancelRequest // 取消请求
  | SDKKeepAliveMessage     // 心跳
```

这个联合类型是**所有输出格式的统一中间表示**。不管下游是 terminal print、JSON stdout、还是远程 WebSocket，都消费同一类型。

### 层2→层3：StructuredIO 与 RemoteIO

**StructuredIO**（860 行）是本地 SDK 模式的双向协议层：
- 解析 stdin NDJSON → `StdinMessage`
- 写 stdout NDJSON（通过 `ndjsonSafeStringify()`）
- 维护 `pendingRequests` Map 做 request-response 配对（UUID 跟踪）
- 去重机制：`MAX_RESOLVED_TOOL_USE_IDS = 1000`，防止重复处理 `control_response`

**RemoteIO**（256 行）继承 StructuredIO，加上远程传输：
- 创建 `PassThrough` stream 桥接 transport 数据到 StructuredIO 解析器
- 根据环境变量选择 transport（SSE / Hybrid / WebSocket）
- 可选创建 `CCRClient` 用于 v2 协议

---

## 二、输出格式分层设计：print / json / stream-json / partial messages

Claude Code 并没有用传统的 `--output-format json` 开关。它的方案更激进——**所有模式都走同一个 StdoutMessage 流**，区别仅在于消费端如何解释：

### 1. Terminal 交互模式
print.ts 中 Ink（React for CLI）渲染组件直接消费 assistant message 的 content blocks，分块显示 text、tool_use、thinking 等。用户看到的是经过格式化的彩色终端输出。

### 2. SDK/JSON 模式（`--print` / headless）
`runHeadless()` 把所有 StdoutMessage 序列化为 NDJSON 行写 stdout。每行一个完整 JSON 对象，消费者按行解析即可。

### 3. Stream JSON（增量流）
`stream_event` 类型的 `SDKPartialAssistantMessage` 承载 Anthropic API 原始流事件：
- `message_start` — 消息开始，含 message ID
- `content_block_start` — 内容块开始
- `content_block_delta` — 增量文本/工具输入
- `content_block_stop` / `message_stop` — 结束标记

SDK 宿主可以选择只消费完整的 `SDKMessage`（轮次粒度），也可以订阅 `stream_event` 获得实时流式输出。

### 4. Streamlined 模式
`SDKStreamlinedTextMessage` 和 `SDKStreamlinedToolUseSummaryMessage` 是精简格式——去掉 API 原始结构，只保留文本内容和工具调用摘要。适合轻量集成场景（如 CI/CD 日志）。

### 5. Partial Messages 与 Coalescing
CCRClient 中的 `accumulateStreamEvents()` 是最精巧的部分：
- **100ms 窗口**内的 text_delta 合并为**全量快照**（不是增量片段）
- 每次 flush 对每个 content block 只发一条事件，内容是从 block 开始到当前的完整文本
- 客户端在任意时刻连入（mid-stream）看到的都是**自包含的完整状态**
- 通过 `StreamAccumulatorState`（`byMessage: Map<msgId, string[][]>`）追踪每个 block 的 chunk 数组

```typescript
// 不是发 "Hel" + "lo" + " World"
// 而是发 "Hello World" — 一个 full-so-far snapshot
```

这个设计解决了远程会话重连后的状态同步问题——不需要回放历史 delta。

---

## 三、Transport 层可观测性

### Transport 选择策略

```
环境变量                            → Transport
CLAUDE_CODE_USE_CCR_V2=true        → SSETransport (GET 读 + POST 写)
CLAUDE_CODE_POST_FOR_SESSION_INGRESS_V2 → HybridTransport (WS 读 + POST 写)
默认                                → WebSocketTransport (全双工)
```

### WebSocketTransport（801 行）

**可靠性设计：**
- **CircularBuffer 消息重放**：所有写出消息带 UUID 存入环形缓冲区。重连时检查服务端 `X-Last-Request-Id`，仅重放未确认的消息
- **指数退避重连**：基础 1s，上限 30s，±25% 抖动
- **10 分钟重连预算**：超时后放弃
- **系统休眠检测**：两次 ping 间隔 > 60s 判定为系统休眠，重置重连预算
- **永久关闭码**：1002、4001、4003 立即放弃（除非 token 已刷新）
- **Ping/Pong**：10s 间隔，keep_alive 帧 5 分钟间隔

### SSETransport（712 行）

**读取流：**
```
fetch(SSE URL + Last-Event-ID) → ReadableStream → parseSSEFrames()
  → event: client_event → 提取 payload → NDJSON → onData()
```

**去重机制：**
- 维护 `lastSequenceNum`（高水位）
- 去重集合（1000 条上限，清理时保留高水位以下 200 条）
- 重连时通过 `Last-Event-ID` 恢复

**活性检测：**45s 无帧 → 触发重连（任何帧包括 `:keepalive` 注释都算活跃）

### HybridTransport（283 行）

WebSocket 读 + HTTP POST 写的混合体：
- **stream_event 延迟 100ms** 后批量发送（减少 POST 次数）
- **非 stream 写立即 flush** 之前缓冲的 stream_event（保证顺序）
- 使用 `SerialBatchEventUploader` 确保严格顺序（最多 1 个在途 POST）

### SerialBatchEventUploader（276 行）

**核心合约：串行、有序、可靠投递**

```
enqueue(events[])
  → pending[] (超过 maxQueueSize 则 backpressure 阻塞)
  → drain() 循环（单实例）
  → takeBatch() (respects maxBatchSize + maxBatchBytes)
  → config.send(batch)
  → 成功 → 释放背压，继续
  → 失败 → 重新入队，指数退避
  → 超过 maxConsecutiveFailures → 丢弃当前 batch，重置计数
```

**设计亮点：**
- `takeBatch()` 同时支持条数限制和字节限制（第一条无论多大都发）
- `flush()` 阻塞直到队列清空
- `droppedBatchCount` 让调用方在 flush 后检测是否有静默丢弃
- `RetryableError` 支持 `retryAfterMs`（429 Retry-After），clamp 到 [base, max] 并加抖动

### WorkerStateUploader（132 行）

**最小化状态同步器：**
- **1 in-flight + 1 pending** 的两槽设计——天然无背压问题
- 顶层 key 覆盖写；`external_metadata` / `internal_metadata` 用 RFC 7396 Merge Patch
- 失败时无限重试 + 指数退避
- retry 期间吸收新 patch（coalescing），保证最终一致

### CCRClient（999 行）

**远程会话的完整生命周期协议：**

四条上传管道：
1. **workerState**（WorkerStateUploader）→ PUT /worker — 状态+元数据
2. **eventUploader**（SerialBatchEventUploader）→ POST /worker/events — 客户端可见事件（max 100 条/10MB per batch）
3. **internalEventUploader** → POST /worker/internal-events — 转录+压缩标记（max 200 队列）
4. **deliveryUploader** → POST /worker/events/delivery — 投递状态更新

**Epoch 管理：**
- 父进程设置 epoch token，防止 zombie worker
- 409 Conflict → `onEpochMismatch()`（默认退出）
- JWT exp 检查：过期 token 直接退出，不浪费重试

**心跳：**20s 间隔 POST /worker/heartbeat，服务端 TTL 60s

**会话恢复：**
- `readInternalEvents()` — 从上次 compaction 读前台事件
- `readSubagentInternalEvents()` — 合并所有子 agent 事件
- `getWorkerState()` — 从 GET /worker 读回 external_metadata

---

## 四、Observability 最值得学的设计点

### 1. 生命周期事件作为一等公民

```typescript
notifyCommandLifecycle(uuid, 'started' | 'completed')
notifySessionStateChanged(state: 'idle' | 'running' | 'requires_action', details?)
notifySessionMetadataChanged(metadata)
```

这不是事后加的日志——它是协议的一部分。上层 orchestrator 靠这些事件驱动 UI 状态机和超时逻辑。

### 2. 双轨日志

- `logForDebugging()` — 开发调试，含敏感信息
- `logForDiagnosticsNoPII()` — 遥测级，无 PII

两个函数签名相似但语义完全不同，从 API 层面防止隐私泄漏。

### 3. 去重是传输层的责任

三种 transport 各有去重方案：
- WebSocket：`X-Last-Request-Id` header
- SSE：序列号 + 去重集合
- StructuredIO：`resolvedToolUseIds` 集合

业务层不需要关心幂等——传输层保证 exactly-once 语义。

### 4. 背压信号是显式的

`SerialBatchEventUploader.enqueue()` 在队列满时 **await 阻塞**，而不是丢弃或无限增长。这迫使上游感知下游瓶颈，防止内存泄漏。

### 5. 状态快照 > 增量 delta

CCRClient 的 stream accumulator 把增量 delta 转成 full-so-far 快照。这是一个重要的架构决策：
- 简化客户端逻辑（不需要维护累积状态）
- 重连后无需回放历史
- 代价是带宽——但 100ms 窗口 + 合并使得开销可控

### 6. 输出格式的"洋葱模型"

```
最内层: SDKMessage (完整消息，轮次粒度)
中间层: stream_event (增量 delta，实时流)
外层:   streamlined text/tool summary (精简摘要)
包装层: control_request/response (协议控制)
```

消费者根据能力选择消费哪一层——rich client 消费所有层，CI 脚本只看 streamlined text，orchestrator 主要关心 control 层。

---

## 五、对 Zero 的主 agent 汇报机制的启发

### 1. 采用统一中间表示（IR），而非多套输出逻辑

Claude Code 用 `StdoutMessage` 联合类型作为所有输出的统一 IR。Zero 的 watchdog-agent 架构应当定义一个类似的 `AgentEvent` 联合类型，所有子 agent 的汇报都转成这个类型。主 agent 只消费 IR，不关心子 agent 的内部实现。这样新增子 agent 类型时不需要修改主 agent 的解析逻辑。

### 2. 状态快照优于增量 delta

Zero 的子 agent 汇报进度时，应该发**当前完整状态**而不是增量变化。Claude Code 的 `accumulateStreamEvents` 证明了这一点——full-so-far snapshot 让任何消费者在任意时刻接入都能看到完整状态，无需回放历史。对 Zero 的场景：子 agent 每次汇报应包含 `{task, status, progress_pct, current_output_summary, errors[]}`，而不是 `{delta: "又完成了一步"}`。

### 3. 三级生命周期事件：command / session / metadata

Zero 可以借鉴：
- **Task 级**：`task_started` / `task_completed` / `task_failed`（对应 `notifyCommandLifecycle`）
- **Agent 级**：`idle` / `running` / `requires_action` / `error`（对应 `notifySessionStateChanged`）
- **元数据级**：token 消耗、模型切换、配置变更（对应 `notifySessionMetadataChanged`）

Watchdog 根据 agent 级事件判断是否需要介入；主 orchestrator 根据 task 级事件驱动工作流；Dashboard 消费元数据级。

### 4. 传输层做去重，业务层假设 at-least-once

Zero 的 agent 间通信如果经过任何网络层（即使是本地 IPC），都应该在传输层加去重（UUID + 高水位标记）。业务逻辑可以安全地重试发送而不担心副作用。`SerialBatchEventUploader` 的"串行有序 + 指数退避 + 可配置丢弃阈值"是一个可以直接复用的模式。

### 5. 背压 + Coalescing 两层防护

当子 agent 产出速度超过主 agent 消费速度时：
- **第一层（coalescing）**：状态更新合并——连续 3 次 status update 只保留最后一次（参考 `WorkerStateUploader` 的两槽设计）
- **第二层（backpressure）**：事件队列满时阻塞子 agent（参考 `SerialBatchEventUploader.enqueue()` 的 await 阻塞）

这避免了两个极端：丢消息（不可接受）和无限内存增长（OOM）。

### 6. Epoch / Heartbeat 防 zombie

Zero 的每个子 agent 实例应该有一个 epoch token（由 watchdog 分配）。子 agent 的所有请求都带 epoch。如果 watchdog 重启了一个子 agent，旧实例的 epoch 失效，其请求返回 409 → 旧实例自杀。心跳间隔可以设为 20s（参考 `DEFAULT_HEARTBEAT_INTERVAL_MS`），TTL 设为 3 倍心跳（60s）。这比简单的 process.kill() 更优雅——允许旧实例清理资源后退出。

### 7. 双轨诊断日志：debug vs telemetry

Zero 应从第一天起区分两种日志：
- `logDebug()` — 开发用，含完整 prompt/response 文本，只写本地文件
- `logTelemetry()` — 运维用，只记结构化指标（latency、token_count、error_code），从 API 层面禁止传入自由文本

这个区分在 Claude Code 中已经被验证有效（`logForDebugging` vs `logForDiagnosticsNoPII`），防止隐私泄漏的成本远低于事后修复。

### 8. 控制消息与数据消息走同一通道，但类型区分

Claude Code 的 `StdinMessage` / `StdoutMessage` 里既有数据（user/assistant message）也有控制（permission prompt, interrupt, set_model）。它们走同一个 NDJSON 流，用 `type` 字段区分。Zero 应该采用同样策略——不要为控制通道单独开 IPC。单通道 + 类型标签比双通道更容易保证顺序性，也更容易调试。

---

## 附：关键文件速查

| 文件 | 行数 | 职责 |
|------|------|------|
| `src/cli/print.ts` | 5594 | 主 REPL 编排器，事件路由，输出队列 |
| `src/cli/structuredIO.ts` | 860 | SDK 协议双向解析，NDJSON，权限配对 |
| `src/cli/remoteIO.ts` | 256 | 远程传输桥接，CCR v2 集成 |
| `src/cli/transports/WebSocketTransport.ts` | 801 | 全双工 WS，消息重放，休眠检测 |
| `src/cli/transports/SSETransport.ts` | 712 | SSE 读 + POST 写，序列号去重 |
| `src/cli/transports/HybridTransport.ts` | 283 | WS 读 + POST 写，stream_event 批量 |
| `src/cli/transports/SerialBatchEventUploader.ts` | 276 | 串行有序批量上传，背压+重试 |
| `src/cli/transports/WorkerStateUploader.ts` | 132 | 两槽 coalescing 状态同步 |
| `src/cli/transports/ccrClient.ts` | 999 | CCR v2 完整生命周期：epoch/心跳/四管道上传 |
| `src/entrypoints/sdk/controlSchemas.ts` | 664 | 消息类型定义（21 种 control_request） |
