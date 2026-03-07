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
