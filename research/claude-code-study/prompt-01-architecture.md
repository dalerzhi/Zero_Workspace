你在研究一个本地源码仓库：`tmp-claude-code-main-src/claude-code-main`。

任务：做一份**架构总览笔记**，输出到：
`research/claude-code-study/01-architecture-overview.md`

要求：
1. 先读 README 和源码目录结构。
2. 说明这个项目的大模块分别做什么，尤其关注：`src/bridge`、`src/cli`、`src/commands`、`src/assistant`、`src/bootstrap`。
3. 不要只列目录；要讲清楚模块之间的关系、数据/控制流大概怎么走。
4. 输出要适合给一个正在做 agent orchestration/watchdog 的工程师看。
5. 最后加一节：`对 Zero 有直接参考价值的 5 个点`。
6. 用中文写，信息密度高，少废话。
7. 允许自己读取多个源码文件，但不要大面积抄源码。
