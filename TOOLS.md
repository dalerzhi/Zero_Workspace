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

### Feishu Voice Messages

**Skill location**: `workspace/skills/feishu-voice/`

**Quick send**:
```bash
./skills/feishu-voice/feishu-voice.sh "你好，这是测试语音" ou_7c6c3cdce8475c7a8de63811592c37f9
```

**Preferred voices**:
- `Ting-Ting` - 默认中文女声
- `Mei-Jia` - 较新的中文女声

**File location**: `/Users/a123456/.openclaw/workspace/voice_*.opus`

---

Add whatever helps you do your job. This is your cheat sheet.
