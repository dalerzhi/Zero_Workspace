你在研究源码仓库：`tmp-claude-code-main-src/claude-code-main`。

任务：重点研究 **session / bridge / transport / polling / remote runtime** 相关实现，输出到：
`research/claude-code-study/02-session-bridge-transport.md`

重点文件优先看：
- `src/bridge/sessionRunner.ts`
- `src/bridge/createSession.ts`
- `src/bridge/replBridge.ts`
- `src/bridge/replBridgeTransport.ts`
- `src/bridge/remoteBridgeCore.ts`
- `src/bridge/bridgeMessaging.ts`
- `src/bridge/pollConfig.ts`
- `src/bridge/pollConfigDefaults.ts`
- `src/bridge/flushGate.ts`
- `src/bridge/capacityWake.ts`

要求：
1. 讲清楚 session 生命周期：创建、运行、通信、轮询、恢复、完成/失败。
2. 讲清楚它是如何避免“以为还在跑，其实已经挂了”这类问题的；如果源码没有直接做，也要指出缺口。
3. 总结它在 transport、polling、状态同步方面最值得借鉴的机制。
4. 最后单独列一节：`对 Zero 的 watchdog / orchestrator 可直接移植的设计`，至少 8 条。
5. 用中文写，偏工程设计说明，不要写成流水账。
