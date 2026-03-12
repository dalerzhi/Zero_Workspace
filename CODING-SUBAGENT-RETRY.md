# Coding 子 agent 自动重试（最小可用方案）

目标：当 `openai-codex/gpt-5.3-codex` 偶发 `server_error` 时，统一用一条命令触发「最多重试 1-2 次」的 coding 子任务，减少主会话手工重跑。

## 1) 推荐命令

```bash
# 默认重试 1 次（总共最多 2 次尝试）
./scripts/run-coding-subagent-retry.sh \
  --label fix-auth-bug \
  --retries 1 \
  --task "在当前仓库修复 auth token 刷新逻辑，补测试并运行测试。输出修改文件和测试结果。"
```

## 2) 常用参数

- `--retries 1`：最多重试 1 次（建议默认）
- `--retries 2`：最多重试 2 次（网络波动更大时用）
- `--task-file path/to/task.txt`：任务较长时从文件读取
- `--model openai-codex/gpt-5.3-codex`：默认已是这个模型（若本机 openclaw 不支持 `--model` 参数，脚本会自动回退）
- `--dry-run`：先看最终命令，不执行

## 3) 建议工作流（主会话）

1. 先整理好任务描述（尽量含验收标准、测试要求）。
2. 通过该脚本触发子 agent（统一 label + 重试策略）。
3. 成功后审改动；失败时看脚本输出判断是：
   - **瞬时后端问题**（脚本已自动重试）；
   - **非瞬时问题**（需求不清、权限、命令错误等，需人工修正任务再跑）。

## 4) 判定“可重试错误”

脚本仅对以下关键词触发自动重试：

- `server_error`
- `internal server error`
- `429/502/503/504`
- `timeout/timed out`
- `connection reset / ECONNRESET`
- `overloaded / try again`

## 5) 限制

- 这是 **本地包装器**，不修改 OpenClaw 核心逻辑。
- 重试基于输出文本关键字匹配（启发式），不是官方错误码协议。
- 仅覆盖 `openclaw sessions spawn --mode run` 这类同步执行路径；不自动恢复已经部分完成的上下文。
- 如果是任务本身错误（提示词、权限、仓库状态），不会盲目重试。
