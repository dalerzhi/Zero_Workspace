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

### TTS 音色配置 ⭐

**Noiz Cloud TTS (云端语音 AI) - 默认**
- **默认音色**: `4f71a876` - 故事讲述者（小雨）- 平静舒缓 ← **女声默认**
- 可用中文女声：
  - `4f71a876` - 故事讲述者（小雨）- 平静舒缓 ← **默认**
  - `e47a10c4` - 活泼少女（小雨）- 喜悦活泼
- 可用中文男声：
  - `96270d87` - 故事讲述者（子轩）- 磁性共鸣
  - `dde1b9b5` - 故事讲述者（子轩）- 磁性舒缓
  - `8316cdf1` - 温柔男声（亦辰）- 磁性舒缓
- 可用中文女声：
  - `4f71a876` - 故事讲述者（小雨）- 平静舒缓
  - `e47a10c4` - 活泼少女（小雨）- 喜悦活泼
- API: Noiz Cloud API
- 免费额度：100,000 字符

**Izwi TTS (本地语音 AI) - 备选**
- 默认音色：`male-deep` (深沉男声)
- 模型：`Qwen3-TTS-12Hz-0.6B-Base`
- 服务：`izwi serve` (http://127.0.0.1:8080)

### 飞书语音发送 ⭐

**默认方式**: Python 脚本 (`scripts/feishu-voice.py`)

**快速发送**:
```bash
# 使用默认配置（dde1b9b5 男声）
python3 scripts/feishu-voice.py "要发送的文本"

# 指定接收者
python3 scripts/feishu-voice.py "文本" --chat-id ou_xxxxx

# 指定音色
python3 scripts/feishu-voice.py "文本" --voice-id 8316cdf1
```

**优点**：
- ✅ 完全独立，不依赖插件
- ✅ 自动清理临时文件
- ✅ 可自定义所有参数
- ✅ 在新 Session 中也能用

**配置位置**: `~/.openclaw/preferences.json`

---

Add whatever helps you do your job. This is your cheat sheet.
