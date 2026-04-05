# Local Debug Checklist

## Useful files
- `.runs/agent-watchdog/<run>/status.json`
- `.runs/agent-watchdog/<run>/attempt-*/agent.log`
- `research/claude-code-study/logs/*.launcher.log`

## Useful commands

### Check binaries
```bash
command -v claude codex openclaw
```

### Check processes
```bash
ps -axo pid=,ppid=,pcpu=,rss=,etime=,state=,comm=,command= | grep -E '(claude|python3|openclaw)' | grep -v grep
```

### Child processes
```bash
pgrep -lP <pid>
```

### Latest watchdog status
```bash
ls -dt .runs/agent-watchdog/* | head
cat .runs/agent-watchdog/<run>/status.json
```

## Common local failure modes
1. `codex` not on PATH
2. OpenClaw background exec ends and parent process receives SIGTERM
3. stdout buffering causes false startup timeout
4. parent process alive but child already gone
