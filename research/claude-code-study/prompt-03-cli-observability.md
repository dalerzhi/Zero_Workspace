你在研究源码仓库：`tmp-claude-code-main-src/claude-code-main`。

任务：重点研究 **CLI 输出、structured IO、print 模式、transport 可观测性**，输出到：
`research/claude-code-study/03-cli-observability.md`

重点文件优先看：
- `src/cli/print.ts`
- `src/cli/structuredIO.ts`
- `src/cli/remoteIO.ts`
- `src/cli/transports/HybridTransport.ts`
- `src/cli/transports/SSETransport.ts`
- `src/cli/transports/WebSocketTransport.ts`
- `src/cli/transports/SerialBatchEventUploader.ts`
- `src/cli/transports/WorkerStateUploader.ts`
- `src/cli/transports/ccrClient.ts`

要求：
1. 重点回答：一个成熟 CLI agent 如何把“原始运行态事件”转成“可给用户/上层 orchestrator 消费的状态与输出”。
2. 说明它在 print/json/stream-json/partial messages 上的设计思路。
3. 总结它在 observability、状态上报、输出格式分层方面最值得学的点。
4. 最后加一节：`对 Zero 的主 agent 汇报机制有什么启发`，至少 6 条。
5. 用中文写，信息密度高，不要抄文档。
