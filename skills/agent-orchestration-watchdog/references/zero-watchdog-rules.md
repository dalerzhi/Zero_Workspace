# Zero Watchdog Rules

## Current local defaults

### Standard launcher
```bash
python3 scripts/run-agent-task.py --kind writing|research|coding --label <label> --task "..."
```

### Low-level launcher
```bash
python3 scripts/agent-watchdog.py --label <label> --binary <bin> --command "..."
```

## Preset thresholds

### writing
- startup: 30s
- idle: 300s
- wall: 1800s
- retries: 1

### research
- startup: 30s
- idle: 300s
- wall: 1800s
- retries: 1

### coding
- startup: 45s
- idle: 600s
- wall: 3600s
- retries: 1

## Runtime facts on this machine

- `claude` is available at `/opt/homebrew/bin/claude`
- `codex` is currently not on PATH
- `.runs/agent-watchdog/` stores status and attempt logs

## Known pitfalls

1. OpenClaw background exec may end the outer tool session and SIGTERM the parent process.
   - For true background local agent work, prefer a detached launcher layer.
2. Some commands buffer stdout when redirected to files.
   - Example: Python may need `-u` for unbuffered output.
3. Treat first stdout as a useful signal, but not the sole definition of "healthy startup".

## Progress signals

Prefer these in order:
1. `status.json`
2. new artifact files
3. fresh logs
4. only then raw process existence
