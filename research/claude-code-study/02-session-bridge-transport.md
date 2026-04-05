# Claude Code: Session / Bridge / Transport 深度分析

> 源码版本：`tmp-claude-code-main-src/claude-code-main`
> 重点目录：`src/bridge/`
> 撰写日期：2026-04-05

---

## 目录

1. [整体架构概览](#1-整体架构概览)
2. [Session 生命周期](#2-session-生命周期)
3. [Transport 抽象层](#3-transport-抽象层)
4. [轮询与容量管理](#4-轮询与容量管理)
5. [消息去重与排序保证](#5-消息去重与排序保证)
6. [Token 刷新与鉴权恢复](#6-token-刷新与鉴权恢复)
7. [故障检测与恢复机制](#7-故障检测与恢复机制)
8. [设计缺口分析](#8-设计缺口分析)
9. [值得借鉴的核心机制](#9-值得借鉴的核心机制)
10. [对 Zero 的 watchdog / orchestrator 可直接移植的设计](#10-对-zero-的-watchdog--orchestrator-可直接移植的设计)

---

## 1. 整体架构概览

Bridge 系统存在两条并行路径：

| 路径 | 入口 | 核心文件 | 适用场景 |
|------|------|---------|---------|
| **Env-based (环境层)** | `replBridge.ts` | bridgeApi → pollForWork → transport | 标准远程运行，有 Environments API |
| **Env-less (直连)** | `remoteBridgeCore.ts` | POST /sessions → /bridge → transport | 无环境层的轻量接入 |

两条路径共享：
- **Transport 适配器** (`replBridgeTransport.ts`)：统一 v1 (WebSocket) 与 v2 (SSE + HTTP POST) 差异
- **消息处理** (`bridgeMessaging.ts`)：类型守卫、去重、路由
- **FlushGate** (`flushGate.ts`)：初始历史刷写时的写入排队
- **JWT 刷新** (`jwtUtils.ts`)：过期前 5 分钟主动续签

**协议版本选择**：由服务端 WorkSecret 中的 `use_code_sessions` 字段驱动，客户端不做协议猜测。

```
┌─────────────┐        ┌───────────────┐
│ replBridge   │        │remoteBridgeCore│
│ (env-based)  │        │  (env-less)    │
└──────┬───────┘        └──────┬─────────┘
       │                       │
       ▼                       ▼
  ┌─────────────────────────────────┐
  │    replBridgeTransport.ts       │
  │  ┌─────────┐   ┌─────────────┐ │
  │  │ v1: WS  │   │ v2: SSE+CCR │ │
  │  └─────────┘   └─────────────┘ │
  └─────────────────────────────────┘
       │                       │
       ▼                       ▼
  ┌──────────────────────────────────┐
  │  bridgeMessaging / flushGate /   │
  │  jwtUtils / capacityWake         │
  └──────────────────────────────────┘
```

---

## 2. Session 生命周期

### 2.1 创建阶段

**Env-based 路径** (`replBridge.ts`)：
1. `registerBridgeEnvironment()` → POST `/v1/environments/bridge` → 获取 `environment_id`
2. 进入 poll 循环 → `pollForWork()` → 拿到 WorkResponse
3. `createBridgeSession()` → POST `/v1/sessions` → 返回 `session_id`
4. 解码 `WorkSecret`（base64url → JSON），内含 `session_ingress_token`、`api_base_url`、协议版本标记

**Env-less 路径** (`remoteBridgeCore.ts`)：
1. 直接 POST `/v1/code/sessions` → 获取 `session_id`
2. POST `/v1/code/sessions/{id}/bridge` → 获取 `worker_jwt`、`expires_in`、`api_base_url`、`worker_epoch`
3. 跳过环境注册和轮询，直连 transport

**关键设计**：
- **Crash-recovery 指针**（`bridgePointer`）：session 创建后立即持久化，包含 session_id + environment_id。用于 perpetual 模式下重启恢复，避免孤儿 session。
- **Git 上下文注入**：创建时自动检测 git repo、branch，注入 session 元数据，支持按仓库维度管理。

### 2.2 运行阶段（通信）

Session 进入运行态后的消息流：

```
Server → [SSE/WS] → handleIngressMessage() → dedup → route
                                                  ├─ onInboundMessage (用户消息)
                                                  ├─ onPermissionResponse (权限回复)
                                                  └─ onControlRequest (服务端指令)

Client → flushGate.check() → transport.write() → Server
```

**消息类型过滤**（`isEligibleBridgeMessage`）：只有 `user`、`assistant`、`local_command` 三类消息走 transport，tool_result 等内部消息不上传。

**FlushGate 状态机**：

| 状态 | enqueue() 行为 | 用途 |
|------|---------------|------|
| `start()` | 入队，返回 true | 初始历史刷写期间 |
| `end()` | 返回已排队项，后续 enqueue 返回 false | 刷写完成，放行 |
| `drop()` | 丢弃队列 | transport 重建时清理旧队列 |
| `deactivate()` | 清除 active 标记 | 新 transport 排空旧队列 |

### 2.3 轮询阶段

详见 [第4节](#4-轮询与容量管理)。

### 2.4 恢复阶段

**Env-based 重连策略**（`replBridge.ts`）：
- **策略 1（就地重连）**：用相同 environment_id 重新注册，尝试恢复已有 session
- **策略 2（全新 session）**：如果 TTL 已过期或 session 不可恢复，在新注册的 env 上创建新 session
- **防护**：环境重建次数上限 = 3，防止无限重建循环

**Env-less 重连**（`remoteBridgeCore.ts`）：
- 401 触发 → 重新请求 `/bridge` → 获取新 JWT + epoch → 重建 transport
- `authRecoveryInFlight` 标记串行化并发刷新请求
- FlushGate 在重建期间激活，保证消息不丢失

### 2.5 完成/失败

**正常完成**（`teardown()`）：
1. FlushGate drop（丢弃未发消息）
2. 发送 `makeResultMessage()`（state = 'idle'）
3. `archiveBridgeSession()` → POST `/v1/sessions/{id}/archive`（幂等，409 = 已归档）
4. 清除 crash-recovery 指针（非 perpetual 模式）
5. transport.close()（最后关闭，确保 uploader 排空）
6. Archive 失败时 401 重试，总预算 1.5 秒

**异常终止**：
- 子进程退出 → `sessionRunner.ts` 检测 done Promise resolve
- 强制杀进程 → `forceKill()` → SIGKILL
- 未归档的 session 靠 crash-recovery 指针在下次启动时回收

---

## 3. Transport 抽象层

### 3.1 统一接口 (`ReplBridgeTransport`)

```typescript
interface ReplBridgeTransport {
  write(message): Promise<void>
  writeBatch(messages): Promise<void>
  close(): void
  isConnectedStatus(): boolean
  getStateLabel(): string
  connect(): void
  getLastSequenceNum(): number     // SSE 续传位点
  reportState(state): void          // v2: PUT /worker
  reportMetadata(metadata): void    // v2: 外部元数据
  reportDelivery(eventId, status): void  // v2: ACK
  flush(): Promise<void>            // v2: 排空上传缓冲
  setOnData / setOnClose / setOnConnect(callback): void
}
```

### 3.2 v1 适配器（WebSocket）

`createV1ReplTransport()`：
- 直接包装 HybridTransport（WebSocket 读 + POST 写）
- `getLastSequenceNum()` 始终返回 0（WS 有自己的重放语义）
- state/delivery/flush 全是 no-op

### 3.3 v2 适配器（SSE + CCR HTTP）

`createV2ReplTransport()`：
- **读**：SSETransport，支持 `lastSequenceNum` 续传
- **写**：CCRClient（HTTP POST to `/worker/*` 端点）
- **注册**：`registerWorker()` → POST `/sessions/{id}/worker/register` → 获取 `worker_epoch`
- **心跳**：20 秒间隔，服务端 TTL 60 秒（3× 安全余量）
- **Epoch 冲突**：409 响应 → `onClose(4090)` → replBridge 触发重连
- **初始化失败**：PUT /worker 失败 → `onClose(4091)`
- **SSE 401**：映射为 `onClose(401)` → 鉴权恢复流程

### 3.4 关键细节：Epoch 管理

CCR v2 引入 `worker_epoch` 概念：
- 服务端在 `registerWorker()` 时签发
- 所有 `/worker/*` 请求必须携带
- 服务端用于检测"同一 session 被多个 worker 同时处理"的脑裂问题
- 409 = epoch 不匹配 → 当前 worker 必须立即让出

这是一个**分布式锁的轻量替代**：不需要显式加锁/解锁，靠递增的 epoch 实现 fencing。

---

## 4. 轮询与容量管理

### 4.1 双速率轮询

| 状态 | 间隔 | 含义 |
|------|------|------|
| Not-at-capacity | 2000ms | 积极寻找新任务 |
| At-capacity | 600,000ms (10min) | 维持存活信号 |

**设计原则**：空闲时快速响应，忙碌时减少服务端负载。

### 4.2 心跳机制

- `non_exclusive_heartbeat_interval_ms`：独立于 poll 的心跳循环（默认 0 = 关闭）
- 心跳与 poll 互相补充：至少要有一个存活机制启用
- 验证规则：心跳 = 0（关闭）或 ≥100ms（拒绝 1-99ms 的无意义值）

### 4.3 CapacityWake（`capacityWake.ts`）

**问题**：at-capacity 状态下 poll 间隔 10 分钟，但 transport 断开后需要立即恢复。

**解决方案**：
```typescript
signal(): { signal: AbortSignal, cleanup: () => void }
wake(): void  // 中断当前 sleep，重置 controller
```

Transport 关闭时调用 `wake()`，poll 循环的 `sleep()` 被 abort → 立即进入下一轮 poll。

### 4.4 GrowthBook 动态调参

`pollConfig.ts` 通过 GrowthBook feature flag `tengu_bridge_poll_interval_config` 支持线上动态调整：
- Zod schema 校验 + refinement 规则
- 5 分钟缓存刷新
- 无效配置自动降级到 defaults
- **运维价值**：无需发版即可全局调节 poll 频率，应对突发负载

---

## 5. 消息去重与排序保证

### 5.1 BoundedUUIDSet（环形去重缓冲）

```typescript
class BoundedUUIDSet {
  constructor(capacity: number)
  add(uuid: string): void   // O(1)，容量满时淘汰最老条目
  has(uuid: string): boolean // O(1)
}
```

用于两个场景：
- **回声过滤**（`recentPostedUUIDs`）：客户端发出的消息被服务端回传时过滤
- **重投递去重**（`recentInboundUUIDs`）：SSE 重连后服务端可能重放已处理消息

### 5.2 FlushGate 排序保证

初始历史刷写（最多 200 条）期间，新消息被排队而非直接发送。避免：
- 历史消息和实时消息交叉
- 服务端因乱序而产生不一致状态

### 5.3 Sequence Number 续传

v2 transport 的 SSE 流支持 `lastSequenceNum`：
- Transport 重建时携带上一个连接的最后序列号
- 服务端从该位点之后开始推送，避免重放整个流

---

## 6. Token 刷新与鉴权恢复

### 6.1 主动刷新调度器 (`createTokenRefreshScheduler`)

```
过期前 5min → 触发刷新
├─ 成功 → 更新 token，设下一个定时器
├─ 失败 → 重试（最多 3 次连续失败）
└─ 长期运行 → 30min 兜底定时器
```

**Generation Counter**：每次刷新操作携带 generation 标记。如果在刷新进行中 token 已被其他路径更新（比如 401 恢复），旧的刷新结果会被丢弃。防止 ABA 问题。

### 6.2 401 恢复链

```
请求返回 401
  → onAuth401 回调
  → OAuth refresh
  → 更新 transport token
  → 重试原请求（仅重试一次）
```

**Env-less 路径额外逻辑**：
- `authRecoveryInFlight` 标记防止并发 401 重试
- 重新请求 `/bridge` 端点获取新 JWT + epoch
- 需要重建整个 transport（新 epoch = 新 worker 注册）

### 6.3 子进程 Token 传递

`sessionRunner.ts` 通过 stdin 向子进程发送 token 更新：
```
子进程 stdin ← JSON(token_update)
```
无需重启子进程即可刷新认证。

---

## 7. 故障检测与恢复机制

### 7.1 已实现的故障检测

| 检测手段 | 检测的故障 | 响应动作 |
|---------|----------|---------|
| Transport onClose 回调 | 连接断开 | capacityWake → 重新 poll |
| Epoch 409 | 脑裂/重复 worker | 关闭 transport，让出 session |
| 401 响应 | Token 过期 | 刷新 + 重试 |
| 子进程 done Promise | 子进程崩溃 | 记录 stderr，session 标记完成 |
| 心跳 (v2) | Worker 无响应 | 服务端侧超时回收 |
| Poll 空结果 | 无工作/环境失效 | 持续 poll 直到有工作 |
| SSE 断开 | 读流中断 | 映射为 onClose → 重连 |

### 7.2 Generation Counter 防过期异步

`replBridge.ts` 使用 generation counter 来处理"异步操作完成时状态已变"的问题：
- 每次状态变迁递增 generation
- 异步回调检查当前 generation 是否与启动时一致
- 不一致则丢弃结果（状态已过期）

这是一个轻量级的"取消令牌"模式，比 AbortController 更适合状态机场景。

### 7.3 环境重建限制

Env-based 路径最多重建环境 3 次。防止：
- 服务端持续拒绝注册时的无限循环
- 网络抖动导致的资源浪费

---

## 8. 设计缺口分析

尽管整体健壮性很高，以下几个方面值得注意：

### 8.1 客户端侧缺少主动健康探测

**现状**：故障检测主要依赖被动信号（连接断开、请求失败）。心跳是 worker → server 方向的，服务端可以检测 worker 死亡，但 **worker 无法主动检测服务端是否还在处理自己的 session**。

**风险**：如果服务端已将 session 标记为 abandoned 但 transport 连接仍在（半开连接），worker 可能继续处理已被回收的 session。

**建议**：增加客户端侧的"反向心跳"或定期 GET session 状态。

### 8.2 Perpetual 模式的 crash-recovery 指针可能过期

**现状**：`bridgePointer` 仅存储 session_id + environment_id。如果 worker 长时间宕机：
- 服务端可能已回收该 session/environment
- 重启后尝试恢复会失败（但有 fallback 到全新 session）

**缺口**：没有记录指针的创建时间或 TTL，无法在恢复前快速判断是否值得尝试。

### 8.3 多 worker 脑裂窗口

**现状**：Epoch 机制能检测脑裂，但检测是**写时检测**（409 在 POST 时返回）。在 409 之前，两个 worker 可能同时读取 SSE 流。

**实际影响有限**：SSE 是只读的，真正的冲突发生在写入侧。但如果两个 worker 同时处理同一条消息的不同部分，可能产生不一致的副作用。

### 8.4 缺少结构化的 circuit breaker

**现状**：重试策略是 ad-hoc 的（每个 API 调用自带重试逻辑）。没有全局的 circuit breaker 来在服务端整体不可用时快速失败。

**影响**：在服务端大面积故障时，大量客户端会持续重试，加重服务端恢复负担。

---

## 9. 值得借鉴的核心机制

### 9.1 Transport 协议抽象

将 WebSocket 和 SSE+HTTP 统一到 `ReplBridgeTransport` 接口下，上层代码完全不关心底层协议。新增协议只需实现适配器。

### 9.2 Epoch Fencing

用递增 epoch 替代分布式锁，解决"谁是当前合法 worker"的问题。成本极低（一个整数比较），效果等同于 fencing token。

### 9.3 FlushGate 有限状态机

4 个状态 + 严格的转换规则，解决了历史回放与实时消息的排序问题。状态机的好处是所有边界情况都有明确处理。

### 9.4 双速率 Poll + CapacityWake

空闲时积极、繁忙时克制、断连时立即唤醒。三种频率无缝切换，兼顾响应性和效率。

### 9.5 Generation Counter 模式

比 AbortController 更轻量的异步取消方案。特别适合"状态机 + 异步操作"的组合，避免 stale callback 造成状态混乱。

### 9.6 BoundedUUIDSet 环形去重

O(1) 操作 + 固定内存开销。适合任何需要"最近 N 条去重"的场景。

### 9.7 GrowthBook 动态调参

运行时可调的 poll 参数 + Zod schema 校验 + 安全降级到默认值。做到了"可远程调参但不会因为错误配置而崩溃"。

### 9.8 主动 Token 刷新 + Generation 防护

不等 401 才刷新，而是提前 5 分钟。加上 generation counter 防止 ABA，确保 token 更新的原子性。

---

## 10. 对 Zero 的 watchdog / orchestrator 可直接移植的设计

以下是从 Claude Code bridge 实现中可以直接应用到 Zero 的 watchdog 和 orchestrator 系统的设计：

### 10.1 Epoch Fencing 机制

**原理**：每次 worker 注册时获取递增的 epoch，所有写操作必须携带。服务端比对 epoch，不匹配则拒绝（409）。

**移植方式**：Zero 的每个 agent task 分配一个 epoch。watchdog 接管任务时获取新 epoch，旧 worker 的所有后续操作自动失效。解决"以为还在跑，其实已经被接管"的问题。

### 10.2 Generation Counter 异步取消

**原理**：状态变迁递增 generation，异步回调检查 generation 一致性。

**移植方式**：orchestrator 的每个决策周期递增 generation。如果在等待子 agent 回复期间状态已变（比如用户取消），回调自动作废。避免 stale 操作覆盖新状态。

### 10.3 双速率 Poll + CapacityWake

**原理**：空闲时快速 poll（2s），满载时慢速 poll（10min），transport 断开时立即唤醒。

**移植方式**：watchdog 对活跃任务每 2 秒检查一次，无任务时每 10 分钟心跳。任务异常结束时通过 `wake()` 立即触发检查，无需等待下一个 poll 周期。

### 10.4 FlushGate 状态机

**原理**：在状态转换期间排队消息，转换完成后按序释放。

**移植方式**：orchestrator 在重新分配任务时激活 FlushGate。期间子 agent 的输出被缓冲，重新分配完成后按序投递给新 handler。防止消息丢失或乱序。

### 10.5 Crash-Recovery 指针

**原理**：session 创建后立即持久化 `{session_id, environment_id}` 到本地文件。重启时读取指针尝试恢复。

**移植方式**：watchdog 启动任务后立即写入 `{task_id, agent_id, started_at, last_heartbeat}` 到持久化存储。watchdog 自身重启后可以立即恢复对所有活跃任务的监控，而不是从零开始。增加 `started_at` 字段解决原实现中缺少 TTL 判断的问题。

### 10.6 BoundedUUIDSet 去重

**原理**：O(1) 环形缓冲，固定容量，FIFO 淘汰。

**移植方式**：orchestrator 用于去重重复的 webhook/event 通知。比如同一个子 agent 的完成通知可能被投递多次（网络重试），环形缓冲确保只处理一次。内存固定，无需定期清理。

### 10.7 主动健康探测 + 宽限期

**原理**：v2 心跳间隔 20s，服务端 TTL 60s（3× 安全余量）。不是"一次没收到就判死"。

**移植方式**：watchdog 对 agent 的健康检查采用类似设计——心跳间隔 T，判死阈值 3T。这个 3× 倍率在网络抖动和 GC 暂停下都能提供足够容错。建议 Zero 的 agent 心跳间隔 10s，判死 30s。

### 10.8 GrowthBook 式动态调参

**原理**：通过远程 feature flag 动态调整 poll 间隔，Zod 校验 + 默认值降级。

**移植方式**：watchdog 的关键参数（心跳间隔、判死阈值、最大重试次数、并发任务上限）都通过远程配置下发。每次读取时做 schema 校验，无效值降级到编译时默认值。这样在生产环境发现问题时可以秒级调整，而不需要发版重启。

### 10.9 结构化 Teardown 顺序

**原理**：`teardown()` 严格按顺序执行——先发结果消息、再归档、再清指针、最后关 transport（排空上传缓冲后再关）。

**移植方式**：orchestrator 的任务结束流程应同样有严格顺序——先通知依赖方、再持久化结果、再更新状态、最后释放资源。特别是"transport 最后关闭"这个原则：确保所有未发出的数据都已排空，避免数据丢失。

### 10.10 401/409 分级处理

**原理**：401 = token 过期，可刷新重试；409 = epoch 冲突，必须让出。不同错误码触发不同恢复路径，而不是统一重试。

**移植方式**：watchdog 的错误处理应区分"可恢复错误"（网络抖动、token 过期 → 重试）和"不可恢复错误"（任务已被接管、资源已释放 → 立即停止）。避免对不可恢复错误做无意义重试。

### 10.11 串行化鉴权恢复

**原理**：`authRecoveryInFlight` 标记确保同一时刻只有一个 401 恢复流程在进行。多个并发 401 不会触发多次 OAuth refresh。

**移植方式**：watchdog 与多个外部服务交互时，token 刷新应全局串行化。避免 N 个并发请求同时 401 导致 N 次刷新请求打到 auth 服务。

### 10.12 子进程 NDJSON 活动流

**原理**：`sessionRunner.ts` 通过 stdout NDJSON 从子进程提取结构化活动（tool_use、text、result、error），存入环形缓冲（最多 10 条）。

**移植方式**：watchdog 监控的每个 agent 子进程通过 NDJSON 协议上报活动。watchdog 维护每个 agent 的最近 N 条活动快照，用于：
- 健康判断（最近有活动 = 还在工作）
- 故障诊断（最后几条活动 = 崩溃现场）
- 状态展示（给 orchestrator 提供各 agent 的当前进度）

---

## 附录：核心文件清单

| 文件 | 行数 | 职责 |
|------|------|------|
| `replBridge.ts` | ~2400 | Env-based 主控逻辑 |
| `remoteBridgeCore.ts` | ~1000 | Env-less 主控逻辑 |
| `replBridgeTransport.ts` | ~370 | v1/v2 transport 适配器 |
| `bridgeMessaging.ts` | ~460 | 消息类型守卫、去重、路由 |
| `sessionRunner.ts` | ~550 | 子进程生命周期管理 |
| `createSession.ts` | ~385 | Session CRUD API 客户端 |
| `bridgeApi.ts` | ~300 | Environments API 客户端 |
| `jwtUtils.ts` | ~257 | Token 刷新调度器 |
| `pollConfig.ts` | ~111 | GrowthBook 动态 poll 配置 |
| `pollConfigDefaults.ts` | ~83 | Poll 默认值 |
| `flushGate.ts` | ~72 | 历史刷写排队状态机 |
| `capacityWake.ts` | ~57 | 容量变化唤醒原语 |
| `workSecret.ts` | ~128 | Work 密钥解码 + URL 构建 |
| `ccrClient.ts` | ~300+ | CCR v2 worker 生命周期协议 |
| `types.ts` | ~263 | 类型定义 |
