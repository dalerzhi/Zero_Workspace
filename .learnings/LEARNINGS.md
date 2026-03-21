## [LRN-20260307-009] best_practice

**Logged**: 2026-03-07T18:17:00+08:00
**Priority**: critical
**Status**: resolved
**Area**: infra

### Summary
飞书语音消息时长显示问题修复 - 自动检测音频时长并传递给飞书 API

### Details

**问题**: 飞书语音消息显示时长为 `0:00`，而不是实际时长

**根因**: `openclaw message send` 工具在上传音频文件时没有传递 `duration` 参数给飞书 API

**修复方案**:
1. 添加 `getAudioDurationMs()` 函数，使用 ffprobe 自动检测音频时长
2. 修改 `sendMediaFeishu()` 函数，在上传 OPUS 文件时自动检测并传递 `duration` 参数
3. 修改文件：`/opt/homebrew/lib/node_modules/openclaw/extensions/feishu/src/media.ts`
4. 备份文件：`media.ts.backup.20260307_180813`

**关键代码**:
```typescript
// 自动检测音频时长（毫秒）
export async function getAudioDurationMs(filePath: string): Promise<number | undefined> {
  const { stdout } = await execAsync(
    `ffprobe -i "${filePath}" -v quiet -show_entries format=duration -of default=noprint_wrappers=1:nokey=1`
  );
  const durationSec = parseFloat(stdout.trim());
  if (!isNaN(durationSec)) {
    return Math.round(durationSec * 1000);
  }
  return undefined;
}

// 上传时传递 duration
const { fileKey } = await uploadFileFeishu({
  cfg,
  file: buffer,
  fileName: name,
  fileType,
  duration, // ← 关键参数
  accountId,
});
```

**测试验证**: ✅ 通过 - 飞书显示正确时长

### Suggested Action
无需额外操作，修复已集成到 OpenClaw 飞书插件

### Metadata
- Source: bug_fix
- Related Files: `/opt/homebrew/lib/node_modules/openclaw/extensions/feishu/src/media.ts`
- Tags: feishu, voice-message, duration, ffprobe
- See Also: LRN-20260307-008 (Noiz TTS 集成)

---

## [LRN-20260307-010] knowledge_gap

**Logged**: 2026-03-07T18:17:00+08:00
**Priority**: high
**Status**: resolved
**Area**: config

### Summary
Noiz TTS 音色选择 - 必须选择含"中文"标签的音色，避免使用英文或带"恐惧"标签的音色

### Details

**问题 1**: 生成的语音都是默认女声

**根因**: 使用的音色 ID `b89cf430` 是英文男声（标签：`English,Young,Male`），不适合中文文本

**正确音色**:
- 男声：`dde1b9b5` (子轩 - 中文), `96270d87` (子轩 - 中文), `8316cdf1` (亦辰 - 中文)
- 女声：`4f71a876` (小雨 - 中文), `e47a10c4` (活泼小雨 - 中文)

**问题 2**: 女声音色听起来歇斯底里

**根因**: 使用了 `d44f2ab4` 游戏少女（小雨），标签含"恐惧"

**正确选择**: `4f71a876` 故事讲述者（小雨）- 标签：平静，舒缓

**问题 3**: 情感参数没生效

**根因**: 参数格式错误，应该用小写

**正确格式**:
```json
{"happiness": 0.7}    // ✅ 正确
{"Joy": 0.7}          // ❌ 错误
```

### Suggested Action
默认音色已固定为 `dde1b9b5`（故事讲述者 - 子轩），记录在 TOOLS.md

### Metadata
- Source: debugging
- Related Files: `/Users/a123456/.openclaw/workspace/TOOLS.md`
- Tags: noiz-tts, voice-selection, emotion-params

---

## [LRN-20260307-011] best_practice

**Logged**: 2026-03-07T18:17:00+08:00
**Priority**: medium
**Status**: resolved
**Area**: infra

### Summary
飞书 OPUS 音频编码参数优化 - 避免爆音

### Details

**问题**: 飞书播放语音时有爆音/杂音

**根因**: OPUS 编码参数不符合飞书要求

**错误参数**:
- 采样率：48000 Hz ❌
- 声道：立体声 ❌
- 比特率：64kbps ❌

**正确参数** (飞书优化):
- 采样率：**16000 Hz** ✅
- 声道：**单声道** ✅
- 比特率：**24kbps** ✅

**FFmpeg 命令**:
```bash
ffmpeg -y -i input.wav \
  -c:a libopus \
  -b:a 24k \
  -ar 16000 \
  -ac 1 \
  output.opus
```

### Suggested Action
已将正确参数固化到文档和代码中

### Metadata
- Source: bug_fix
- Related Files: `/Users/a123456/.openclaw/workspace/tts-output/FIX-RECORD.md`
- Tags: ffmpeg, opus, feishu, audio-encoding

---

## [LRN-2026-03-09-2301] auto

**Logged**: 2026-03-09T23:01:38+0800
**Priority**: medium
**Status**: pending
**Area**: config

### Summary
aliyun-mail skill 重构：智能收件人识别 + 邮件内容总结 + 分发包

### Details
_待补充_

### Suggested Action
_待补充_

### Metadata
- Source: quick-log
- Tags: auto-logged

---

## [LRN-2026-03-09-2301] auto

**Logged**: 2026-03-09T23:01:41+0800
**Priority**: medium
**Status**: pending
**Area**: config

### Summary
Session 管理优化：从自动重置改为 Context 监控

### Details
_待补充_

### Suggested Action
_待补充_

### Metadata
- Source: quick-log
- Tags: auto-logged

---

## [LRN-2026-03-09-2331] auto

**Logged**: 2026-03-09T23:31:27+0800
**Priority**: medium
**Status**: pending
**Area**: config

### Summary
aliyun-mail skill 重构：实现智能收件人/抄送识别，区分行动项归属；支持 AI 总结邮件内容而非罗列原文

### Details
_待补充_

### Suggested Action
_待补充_

### Metadata
- Source: quick-log
- Tags: auto-logged

---

## [LRN-2026-03-09-2331] auto

**Logged**: 2026-03-09T23:31:31+0800
**Priority**: medium
**Status**: pending
**Area**: config

### Summary
Session 管理机制优化：禁用自动重置，改为 Context 使用量监控；修复 Context 估算方法

### Details
_待补充_

### Suggested Action
_待补充_

### Metadata
- Source: quick-log
- Tags: auto-logged

---

## [LRN-2026-03-10-1947] auto

**Logged**: 2026-03-10T19:47:38+0800
**Priority**: medium
**Status**: pending
**Area**: config

### Summary
Insta360 Link 2 摄像头配置集成 + TTS 音色迭代（于谦→小雨）

### Details
_待补充_

### Suggested Action
_待补充_

### Metadata
- Source: quick-log
- Tags: auto-logged

---

## [LRN-2026-03-10-2017] auto

**Logged**: 2026-03-10T20:17:34+0800
**Priority**: medium
**Status**: pending
**Area**: config

### Summary
Insta360 Link 2 摄像头配置 + TTS 音色迭代（于谦→小雨）

### Details
_待补充_

### Suggested Action
_待补充_

### Metadata
- Source: quick-log
- Tags: auto-logged

---

## [LRN-2026-03-13-0831] auto

**Logged**: 2026-03-13T08:31:22+0800
**Priority**: medium
**Status**: pending
**Area**: config

### Summary
补充记录：完成 coding subagent retry workflow，并修复 cron delivery / gateway watchdog 稳定性问题。

### Details
_待补充_

### Suggested Action
_待补充_

### Metadata
- Source: quick-log
- Tags: auto-logged

---
## [LRN-20260320-001] correction

**Logged**: 2026-03-20T00:41:00Z
**Priority**: high
**Status**: pending
**Area**: infra

### Summary
承诺“我会盯着进度”后，后台任务失败没有被我主动接住并继续推进，导致需要用户来追问。

### Details
本次视频生成任务在后台 exec 失败，系统已经给出失败事件，但我没有把它当成“需要立即接管的待办”，也没有主动做三件事：
1. 立刻检查失败原因；
2. 自动进入修复/重跑；
3. 主动向用户同步状态。

问题不在于脚本会失败，而在于我把“启动任务”误当成了“交付结果”，缺少结果导向的闭环。

### Suggested Action
对于所有我明确承诺“我盯着/我来跟进”的长任务，执行统一闭环：
- 启动前定义完成条件（产物路径、成功标志）；
- 后台运行后必须跟踪到成功/失败；
- 失败后默认先自查并尝试修复一次，再决定是否打扰用户；
- 若仍未完成，主动汇报“卡点+下一步”，不能等用户追问。

### Metadata
- Source: user_feedback
- Related Files: scripts/build_deadbug_sample_v2.py
- Tags: follow-through, background-task, proactive, correction
- Pattern-Key: followthrough.background-task.closure
- Recurrence-Count: 1
- First-Seen: 2026-03-20
- Last-Seen: 2026-03-20

---
## [LRN-20260321-001] correction

**Logged**: 2026-03-20T16:36:00Z
**Priority**: high
**Status**: pending
**Area**: infra

### Summary
做外部搜索和技能补强时，应该优先用 Agent Reach 或 Tavily；ClawHub 限流时不该等待，应直接走手动安装；GitHub 上应主动关注并安装 cli-anything 这类高价值工具。

### Details
用户明确指出三点工作方法修正：
1. 搜索外部资源/方案时，优先使用 Agent Reach 或 Tavily，而不是忘了现成能力后退回低效方案。
2. GitHub 搜索 `cli-anything`，并安装到本地，它对后续能力扩展有用。
3. 遇到 ClawHub rate limit，不要停住等待，应直接转手动安装（如 git clone / 浏览器下载 / 本地放置 skill）。

### Suggested Action
- 以后做“找 skill / 找 repo / 找外部方案”时，默认先检查 Agent Reach / Tavily 可用性。
- 把“ClawHub 限流 => 手动安装”固化为标准兜底流程。
- 将这三条同时写入长期记忆，避免再次忘记。

### Metadata
- Source: user_feedback
- Tags: search, agent-reach, tavily, clawhub, manual-install, cli-anything
- Pattern-Key: capability-search.agent-reach-first-and-manual-fallback
- Recurrence-Count: 1
- First-Seen: 2026-03-21
- Last-Seen: 2026-03-21

---
## [LRN-20260321-001] correction

**Logged**: 2026-03-21T08:00:00+08:00
**Priority**: high
**Status**: pending
**Area**: docs

### Summary
用户追问“昨天的视频制作进度”时，不能只根据当前产物猜测，应先核对近期真实工作上下文（会话/记录/计划），避免误把旧成品当作“昨天最后版本”。

### Details
本次我先检查了本地视频产物并直接回答“做出来了”，但用户指出昨天最后实际停留在“搜索 ClawHub / GitHub 上的 skills 并规划制作方案”的阶段。说明仅凭产物时间戳不足以回答“做到哪了”，需要先核对更完整的上下文，再回答或续做。

### Suggested Action
以后遇到“做到哪了/昨天最后到哪一步”这类问题时：
1. 先查 memory / git log / 会话记录 / 计划文档
2. 若仍不确定，明确说“我查到的上下文不足”
3. 再给出当前可继续推进的下一步，而不是直接认定已完成

### Metadata
- Source: user_feedback
- Related Files: MEMORY.md, memory/
- Tags: correction, continuity, status-reporting

---

## [LRN-20260321-002] correction

**Logged**: 2026-03-21T19:49:37.483115+08:00
**Priority**: high
**Status**: pending
**Area**: docs

### Summary
视频交付必须先经过明确的自检闸门（音频、字幕、黑屏/脏段、时长结构），不合格不得先发用户验收。

### Details
用户指出 v5 虽修掉 30s 后黑屏段，但又出现两个基础问题：没有明显 BGM、没有字幕。说明当前流程只是在修单个反馈点，没有做完整交付检查。以后视频类产物必须先执行 QA checklist，通过后才能发送。

### Suggested Action
建立 deadbug / workout 视频交付前检查清单，至少覆盖：
1. 是否存在中文 TTS
2. 是否存在可感知 BGM
3. 是否有字幕/cue overlay
4. 是否无英文原声泄漏
5. 是否无黑屏/标题污染段
6. 是否抽样检查关键时间点帧与音频
7. 不通过则返工，不先发用户

### Metadata
- Source: user_feedback
- Related Files: VIDEO-PRODUCTION-PLAN-V1.md
- Tags: correction, qa, video-pipeline

---
