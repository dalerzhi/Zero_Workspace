# Claude Code Lessons Worth Stealing

## 1. Separate runtime events from user-facing output
Do not let low-level process logs become the reporting API. Normalize them into a structured event/state layer first.

## 2. Treat lifecycle as a real state machine
Session creation, running, reconnect, archive, and recovery should be explicit states, not implicit side effects.

## 3. Hide protocol differences behind a transport interface
WebSocket, SSE, and hybrid transports should look identical to the orchestration layer.

## 4. Make lifecycle events first-class
Started, running, requires_action, completed, failed, archived: emit these explicitly.

## 5. Prefer state snapshots over tiny deltas
For dashboards, restarts, and fan-in summaries, "current full state" is often more valuable than raw deltas.

## 6. Put dedupe and retry semantics in the transport layer
Upper layers should not need to reason about duplicate deliveries or replay.

## 7. Use coalescing and backpressure together
Merge frequent state updates, but block when the downstream truly cannot keep up.

## 8. Use fencing/epoch ideas to kill zombies
If a worker is replaced, old workers should detect they are stale and stop talking.

## 9. Separate control messages from content, but keep them on one typed channel
A single ordered channel with message types is easier to reason about than split control/data pipes.

## 10. Build observability into the protocol, not as an afterthought
If progress, status, and lifecycle are part of the protocol, the orchestrator can supervise instead of guess.
