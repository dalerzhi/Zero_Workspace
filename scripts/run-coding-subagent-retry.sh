#!/usr/bin/env bash
set -euo pipefail

# Wrapper: run an OpenClaw coding subagent task with limited retry on transient backend failures.
# Default: 1 retry (total up to 2 attempts).

usage() {
  cat <<'EOF'
用法:
  scripts/run-coding-subagent-retry.sh --task "任务描述" [选项]
  scripts/run-coding-subagent-retry.sh --task-file path/to/task.txt [选项]

选项:
  --task <text>           子 agent 任务文本
  --task-file <path>      从文件读取任务文本
  --label <name>          子任务 label（默认: coding-task）
  --retries <n>           最大重试次数（默认: 1；建议 1-2）
  --backoff <sec>         重试前等待秒数（默认: 8）
  --model <model>         模型名（默认: openai-codex/gpt-5.3-codex）
  --dry-run               仅打印将执行的命令，不真正执行
  -h, --help              显示帮助

说明:
  - 仅对“疑似瞬时错误”自动重试（如 server_error/5xx/timeout 等）。
  - 非瞬时错误（参数错误、权限错误、任务逻辑错误）会立即失败。
EOF
}

TASK=""
TASK_FILE=""
LABEL="coding-task"
RETRIES=1
BACKOFF=8
MODEL="openai-codex/gpt-5.3-codex"
DRY_RUN=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --task)
      TASK="${2:-}"; shift 2 ;;
    --task-file)
      TASK_FILE="${2:-}"; shift 2 ;;
    --label)
      LABEL="${2:-}"; shift 2 ;;
    --retries)
      RETRIES="${2:-}"; shift 2 ;;
    --backoff)
      BACKOFF="${2:-}"; shift 2 ;;
    --model)
      MODEL="${2:-}"; shift 2 ;;
    --dry-run)
      DRY_RUN=1; shift ;;
    -h|--help)
      usage; exit 0 ;;
    *)
      echo "[ERROR] 未知参数: $1" >&2
      usage
      exit 2 ;;
  esac
done

if [[ -n "$TASK_FILE" ]]; then
  if [[ ! -f "$TASK_FILE" ]]; then
    echo "[ERROR] task 文件不存在: $TASK_FILE" >&2
    exit 2
  fi
  TASK="$(cat "$TASK_FILE")"
fi

if [[ -z "$TASK" ]]; then
  echo "[ERROR] 必须提供 --task 或 --task-file" >&2
  usage
  exit 2
fi

if ! [[ "$RETRIES" =~ ^[0-9]+$ ]]; then
  echo "[ERROR] --retries 必须是非负整数" >&2
  exit 2
fi

if ! [[ "$BACKOFF" =~ ^[0-9]+$ ]]; then
  echo "[ERROR] --backoff 必须是非负整数" >&2
  exit 2
fi

if ! command -v openclaw >/dev/null 2>&1; then
  echo "[ERROR] 未找到 openclaw 命令" >&2
  exit 127
fi

# Heuristic: errors worth retrying.
is_retryable_output() {
  local text="$1"
  echo "$text" | grep -Eqi "server_error|internal server error|bad gateway|gateway timeout|service unavailable|temporar|timed out|timeout|econnreset|connection reset|overloaded|try again|rate limit|429|502|503|504"
}

MAX_ATTEMPTS=$((RETRIES + 1))
ATTEMPT=1
USE_MODEL_FLAG=1

while [[ $ATTEMPT -le $MAX_ATTEMPTS ]]; do
  ATTEMPT_LABEL="${LABEL}-a${ATTEMPT}"
  CMD=(openclaw sessions spawn --task "$TASK" --label "$ATTEMPT_LABEL" --runtime subagent --mode run)
  if [[ $USE_MODEL_FLAG -eq 1 ]]; then
    CMD+=(--model "$MODEL")
  fi

  echo "[INFO] 启动 coding 子 agent (attempt ${ATTEMPT}/${MAX_ATTEMPTS}, label=${ATTEMPT_LABEL}, model=${MODEL})"

  if [[ $DRY_RUN -eq 1 ]]; then
    printf '[DRY-RUN] %q ' "${CMD[@]}"; echo
    exit 0
  fi

  set +e
  OUTPUT="$(${CMD[@]} 2>&1)"
  STATUS=$?
  set -e

  echo "$OUTPUT"

  if [[ $STATUS -ne 0 ]] && echo "$OUTPUT" | grep -Eqi "unknown option.*--model|unknown flag.*--model|unrecognized option.*--model"; then
    if [[ $USE_MODEL_FLAG -eq 1 ]]; then
      echo "[WARN] 当前 openclaw 版本不支持 --model，自动回退为不带 --model 重试同一次尝试。"
      USE_MODEL_FLAG=0
      continue
    fi
  fi

  if [[ $STATUS -eq 0 ]]; then
    echo "[OK] 子任务执行完成（attempt ${ATTEMPT}）"
    exit 0
  fi

  if [[ $ATTEMPT -lt $MAX_ATTEMPTS ]] && is_retryable_output "$OUTPUT"; then
    SLEEP_SEC=$((BACKOFF * ATTEMPT))
    echo "[WARN] 检测到疑似瞬时错误，${SLEEP_SEC}s 后重试..."
    sleep "$SLEEP_SEC"
    ATTEMPT=$((ATTEMPT + 1))
    continue
  fi

  if [[ $ATTEMPT -lt $MAX_ATTEMPTS ]]; then
    echo "[ERROR] 失败且非可重试错误，不再重试。"
  else
    echo "[ERROR] 已达到最大尝试次数（${MAX_ATTEMPTS}），任务失败。"
  fi
  exit "$STATUS"
done
