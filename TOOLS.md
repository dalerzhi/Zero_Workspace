# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

## My Setup

### TTS 音色配置

**Izwi TTS (本地语音 AI) - 默认**
- 默认音色：`male-deep` (深沉男声，酷且自然) ⭐
- 可用男声：
  - `male-narrator` - 男声旁白
  - `male-calm` - 男声平静
  - `male-warm` - 男声温暖
  - `male-deep` - 男声深沉 ← 默认
- 模型：`Qwen3-TTS-12Hz-0.6B-Base`
- 服务：`izwi serve` (http://127.0.0.1:8080)
- CLI: `izwi tts --speaker male-deep "文本"`

**备选：macOS say**
- 中文语音：`Ting-Ting`, `Mei-Jia`
- 英文语音：`Samantha`, `Daniel`

### Feishu Voice Messages

**Skill location**: `workspace/skills/feishu-voice/`

**Quick send**:
```bash
./skills/feishu-voice/feishu-voice.sh "你好，这是测试语音" ou_7c6c3cdce8475c7a8de63811592c37f9
```

**File location**: `/Users/a123456/.openclaw/workspace/voice_*.opus`

---

Add whatever helps you do your job. This is your cheat sheet.
