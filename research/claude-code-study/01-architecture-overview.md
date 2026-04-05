# Claude Code 架构总览

> 源码版本：npm 泄漏版 (2026-03-31)，TypeScript + Bun 运行时，React/Ink 终端 UI。
> 本文面向正在做 agent orchestration / watchdog 的工程师。

---

## 一、项目全景

Claude Code 是 Anthropic 的官方 CLI agent —— 在终端里跟 Claude 交互，完成代码读写、工具调用、多 agent 协调等任务。核心技术栈：

| 层 | 选型 |
|---|------|
| 运行时 | Bun（利用其 bundle feature flags 做编译期 DCE） |
| 终端 UI | React + Ink（组件化渲染） |
| CLI 解析 | Commander.js |
| Schema 校验 | Zod v4 |
| API | Anthropic Messages API (streaming) |

代码量约 51 万行 TS，`src/main.tsx` 单文件 803K（所有 command 定义内联在同一个 entry point）。

---

## 二、核心模块及职责

### 2.1 `src/bootstrap/` — 启动状态

全局 bootstrap state 管理，包括：
- 当前工作目录、session ID、git 信息
- 累计 cost tracker
- 平台检测结果
- 全局 abort controller

**关键点**：bootstrap state 是一个全局单例，不走 React context，在 `init()` 阶段就绑定好，任何模块都可以 import 直接读。

### 2.2 `src/cli/` — 输出层

- `print.ts`（212K 行）：格式化输出引擎，处理 markdown 渲染、代码高亮、进度条
- `structuredIO.ts`：结构化输出模式（JSON lines），供 IDE bridge 和 SDK 消费

**设计选择**：输出层完全和查询逻辑解耦。`QueryEngine` 只 yield 结构化事件，`print` 层负责把事件变成终端可视内容。

### 2.3 `src/commands/` — Slash 命令注册

约 80+ 个 `/xxx` 命令实现（`/commit`、`/compact`、`/review`、`/doctor`、`/mcp` 等）。

执行流：
```
用户输入 /xxx → dequeue 从消息队列移除 → Command.handler() → 返回 Ink 组件或副作用
```

命令和工具是两套体系：命令是用户主动触发的 UI 动作，工具是模型请求调用的能力。

### 2.4 `src/assistant/` — KAIROS 模式

Feature-flagged 的 assistant 模式（代号 KAIROS）。启用后增加 `SleepTool` 等工具，支持更主动的 agent 行为（proactive task execution）。用 Bun 的编译期 feature gate 做 DCE，未启用时零开销。

### 2.5 `src/bridge/` — IDE 集成桥接

**架构**：IDE Extension ↔ WebSocket ↔ Bridge Server ↔ stdin/stdout ↔ Claude Code 子进程

- `bridgeMain.ts`（115K）：bridge 事件循环、session 生命周期管理
- `bridgeMessaging.ts`：JSON-RPC 协议
- `sessionRunner.ts`：每个 session 对应一个独立进程
- JWT 认证 + token 刷新调度
- 支持 multi-session、multi-environment（feature-gated）

**本质**：Bridge 把 Claude Code 从 "终端交互程序" 变成 "可被 IDE 远程驱动的 agent 服务"。每个 session 是独立进程，bridge 只做消息路由 + 生命周期管理。

---

## 三、查询引擎与工具执行（核心数据流）

### 3.1 QueryEngine（src/QueryEngine.ts, 46K）

这是整个系统的大脑。单次 query 的生命周期：

```
用户输入
  │
  ▼
构建 system prompt + 历史消息 + memory 附件
  │
  ▼
Token 计数 → 超限则触发 auto-compact
  │
  ▼
调用 Anthropic API（streaming）
  │
  ├─ 收到 text chunk → buffer → yield 给 UI
  │
  └─ 收到 tool_use block → StreamingToolExecutor
      │
      ├─ 权限检查（canUseTool → getPermissionFromUser）
      ├─ 分类：concurrent-safe vs non-concurrent
      ├─ 执行工具 → 收集 result
      └─ 把 tool_result 追加到消息历史 → 回到 API 调用（agentic loop）
  │
  ▼
post-sampling hooks → cost tracking → session 持久化
```

**关键设计**：
1. **Agentic loop**：工具调用后自动带着 result 回到 API，不需要用户介入
2. **Streaming tool execution**：工具 block 在流式返回过程中就开始解析和排队
3. **Context compression**：接近 token 上限时自动 compact 历史消息
4. **FileStateCache**：跟踪文件修改状态，避免重复读取

### 3.2 工具并发模型（src/services/tools/）

工具分两类：
- **concurrent-safe**（只读工具）：`FileRead`、`Glob`、`Grep`、`WebFetch` 等 → `Promise.all()` 并行执行
- **non-concurrent**（有副作用）：`Bash`、`FileWrite`、`FileEdit` 等 → 串行执行，持有排他锁

**结果排序**：无论完成顺序如何，结果按 tool_call 顺序 emit，保证消息历史确定性。

```
┌─ Tool 1 (read)  ─┐
├─ Tool 2 (grep)  ─┤ 并行
├─ Tool 3 (glob)  ─┘
│
└─ Tool 4 (bash)  ── 串行（等前面全部完成）
└─ Tool 5 (edit)  ── 串行
```

### 3.3 权限系统（src/hooks/toolPermission/）

权限模式：
| 模式 | 行为 |
|------|------|
| `default` | 每次工具调用都弹窗确认 |
| `auto` | 只读工具自动批准，写操作需确认 |
| `plan` | 全部自动批准（规划模式） |
| `bypassPermissions` | 无限制 |

权限可以 **deferred**：先排队，到真正执行时再检查。拒绝会产生一个 synthetic error result 返回给模型。

---

## 四、多 Agent 协调

### 4.1 AgentTool（内置子 agent 生成器）

`AgentTool` 是模型可以调用的工具 —— 它自己就是一个递归的 QueryEngine 实例：

- 接收 prompt → 创建子 agent（同进程或子进程）
- 子 agent 有独立的工具集（可自定义限制）
- 子 agent 有独立 context window
- 支持 `.claude-code/agents/` 目录下的自定义 agent 定义

### 4.2 Coordinator Mode（src/coordinator/）

Feature-gated 的团队协调模式：
- Coordinator agent 只能用 `TEAM_CREATE`、`SEND_MESSAGE`、`SYNTHETIC_OUTPUT` 等内部工具
- 不能直接 bash/edit —— 只能通过 worker agent 操作
- `SharedMemoryContext` 做 agent 间通信
- 适用于大型任务的分治

### 4.3 Task System（src/tasks/）

统一的任务抽象：
- `LocalAgentTask`：同进程内的 agent
- `RemoteAgentTask`：子进程 agent
- `InProcessTeammateTask`：team 内协作
- `DreamTask`：后台思考
- `LocalShellTask`：shell 命令

生命周期：create → run → (progress) → stop → output

---

## 五、启动流程

```
1. 预取（在 import 之前就启动）
   ├─ startMdmRawRead()      ← MDM 配置子进程（async）
   └─ startKeychainPrefetch() ← OAuth/API key 读取（async）

2. init()
   ├─ enableConfigs()         ← Zod 校验
   ├─ setupGracefulShutdown() ← 信号处理
   ├─ applyExtraCACerts()     ← 企业环境 CA 证书
   ├─ OpenTelemetry           ← 懒加载（~400KB）
   ├─ Policy limits           ← 组织级策略
   └─ Plugin init             ← 非阻塞

3. Context 收集
   ├─ getSystemContext()      ← OS/git/env
   └─ getUserContext()        ← 用户设置/权限

4. 工具装配
   ├─ assembleToolPool()      ← 合并内置 + MCP + 插件工具
   └─ filterToolsByDenyRules()← 策略过滤

5. REPL 启动
   └─ React/Ink render → AppStateProvider → 消息循环
```

**性能优化**：预取让 MDM + keychain 读取和模块加载并行，节省约 100ms 启动时间。

---

## 六、其他重要子系统

| 子系统 | 位置 | 作用 |
|--------|------|------|
| Compact | `src/services/compact/` | 上下文压缩，防止 token 溢出 |
| MCP | `src/services/mcp/` | Model Context Protocol 服务器管理 |
| Skills | `src/skills/` | 可复用工作流（prompt 模板 + 参数） |
| Memory | `src/memdir/` | 持久化记忆目录（跨 session） |
| Plugins | `src/plugins/` | 插件系统 |
| Session | `src/utils/sessionStorage.ts` | 会话持久化与恢复 |
| State | `src/state/` | Zustand-like 全局状态管理 |

---

## 七、模块关系图

```
┌─────────────────────────────────────────────────────┐
│                    main.tsx (entry)                  │
│         Commander.js CLI → init() → REPL            │
└──────────────┬──────────────────────────────────────┘
               │
    ┌──────────▼──────────┐
    │   AppState (React)  │ ← 全局状态容器
    └──────────┬──────────┘
               │
    ┌──────────▼──────────┐        ┌──────────────┐
    │    query.ts          │◄──────│  commands.ts  │
    │  (Query Pipeline)    │       │  (/xxx 命令)   │
    └──────────┬──────────┘        └──────────────┘
               │
    ┌──────────▼──────────┐
    │   QueryEngine.ts    │ ← 核心 agentic loop
    │  (LLM Orchestrator) │
    └──────┬─────┬────────┘
           │     │
     ┌─────▼─┐ ┌─▼─────────────────────┐
     │ API   │ │ StreamingToolExecutor  │
     │Client │ │ (并发调度 + 权限检查)     │
     └───────┘ └───┬───────────────────┘
                   │
        ┌──────────▼──────────────┐
        │      tools.ts           │
        │  (40+ 工具注册表)         │
        │  Bash/Read/Edit/Glob/   │
        │  Grep/Agent/Task/...    │
        └─────────────────────────┘
               ▲
               │ Agent 递归调用
    ┌──────────┴──────────┐
    │   AgentTool          │ → 子 QueryEngine
    │   coordinator/       │ → 团队协调
    │   tasks/             │ → 任务抽象
    └─────────────────────┘

    ┌─────────────────────────────┐
    │        bridge/              │
    │  IDE ↔ WebSocket ↔ Session  │ ← 独立进程，不走 REPL
    └─────────────────────────────┘
```

---

## 八、对 Zero 有直接参考价值的 5 个点

### 1. 工具并发分类是个好模式

Claude Code 把工具分成 concurrent-safe 和 non-concurrent 两类，在一次 turn 中并行执行只读工具、串行执行写操作。这个模式可以直接搬到 Zero 的 watchdog agent：sensor 类工具并行跑，actuator 类工具排队执行，结果按调用顺序 emit 保证 transcript 确定性。

### 2. Agentic loop 的 context compression 策略

QueryEngine 在每次回环前检查 token 用量，接近上限时自动触发 compact（用模型自己总结历史）。Zero 的 watchdog 如果要长时间运行，必须有类似机制 —— 否则 context 会爆。Claude Code 用 `CompactBoundaryMessage` 标记压缩边界，compact 后用 `TombstoneMessage` 替换原消息，这个消息类型设计值得参考。

### 3. 权限的 deferred 模式

权限不是调用时立刻检查，而是可以 deferred 到真正执行时。这对 watchdog 场景很有价值 —— agent 可以先规划一批操作，到执行时再统一审批，而不是每个工具调用都打断流程。denial 产生 synthetic error 让模型自行调整策略也是好设计。

### 4. Task 抽象的统一接口

`LocalAgentTask` / `RemoteAgentTask` / `LocalShellTask` 共用同一套 create → run → stop → output 接口。Zero 的 watchdog child-agent 可以直接抄这个抽象 —— 不管底层是同进程 agent、子进程 agent 还是 shell 命令，上层调度逻辑都一样。

### 5. Bootstrap 预取模式

启动时在 import 之前就 spawn 子进程做 IO 密集操作（keychain、MDM），和模块加载并行。Zero 的 watchdog 启动时可以用同样模式：在加载 agent 定义和工具注册的同时，预取环境信息、检查 API 可用性、加载历史状态，把冷启动时间压到最短。

---

*生成时间：2026-04-05 | 源码：tmp-claude-code-main-src/claude-code-main*
