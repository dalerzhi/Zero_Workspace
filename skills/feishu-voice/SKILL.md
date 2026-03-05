---
name: feishu-voice
description: "Send native voice messages on Feishu (飞书). Generate TTS audio, convert to Opus format, and send as native voice messages."
metadata:
  {
    "openclaw":
      {
        "emoji": "🎤",
        "requires": { "bins": ["ffmpeg", "say"] },
        "install":
          [
            {
              "id": "ffmpeg",
              "kind": "brew",
              "formula": "ffmpeg",
              "bins": ["ffmpeg"],
              "label": "Install ffmpeg for audio conversion",
            },
          ],
      },
  }
---

# Feishu Voice Message Skill

Send **native voice messages** (原生语音消息) on Feishu. This skill handles the complete workflow: TTS generation → Opus conversion → Feishu upload → Send as voice message type.

## Why This Skill?

Feishu distinguishes between:
- **Audio file** (音频文件) - Sent as `.m4a`, `.mp3`, etc. Shows as a file attachment
- **Voice message** (语音消息) - Sent as `.opus`/`.ogg`. Shows as a native voice bubble with play button

This skill ensures you send **native voice messages** that users can tap to play.

## Quick Start

### Send a voice message (one-liner)

```bash
# Generate TTS, convert to opus, send in one command
say -v Ting-Ting "你好，这是测试语音" | ffmpeg -f wav -i pipe:0 -c libopus /Users/a123456/.openclaw/workspace/voice.opus -y 2>/dev/null && \
openclaw message send --channel feishu --target <user_id> --media /Users/a123456/.openclaw/workspace/voice.opus
```

### Step by step

```bash
# 1. Generate TTS audio (macOS built-in)
say -v Ting-Ting "你好，这是测试语音" -o /Users/a123456/.openclaw/workspace/voice.m4a

# 2. Convert to Opus format (required for native voice messages)
ffmpeg -i /Users/a123456/.openclaw/workspace/voice.m4a -c libopus /Users/a123456/.openclaw/workspace/voice.opus -y

# 3. Send via Feishu (auto-detected as voice message type)
openclaw message send --channel feishu --target <user_id> --media /Users/a123456/.openclaw/workspace/voice.opus
```

## Available Voices (macOS)

List all available voices:
```bash
say -v '?'
```

Common Chinese voices:
- `Ting-Ting` - Female, Mandarin (default for Chinese)
- `Sin-Ji` - Female, Cantonese
- `Mei-Jia` - Female, Mandarin (newer)

English voices:
- `Samantha` - Female, US English
- `Daniel` - Male, UK English
- `Fred` - Male, US English

## Using in Agent Code

When you want to send a voice message in response to user requests:

```bash
# Example: User asks "给我读一下这句话"
TEXT="这是要读的内容"
OUTPUT="/Users/a123456/.openclaw/workspace/voice_$(date +%s).opus"

# Generate and convert
say -v Ting-Ting "$TEXT" -o "${OUTPUT%.opus}.m4a"
ffmpeg -i "${OUTPUT%.opus}.m4a" -c libopus "$OUTPUT" -y 2>/dev/null

# Send
openclaw message send --channel feishu --target <user_id> --media "$OUTPUT"
```

## Key Requirements

| Requirement | Why |
|-------------|-----|
| `.opus` or `.ogg` format | Feishu only recognizes these as voice messages |
| File in workspace directory | `/tmp/` is blocked for security |
| ffmpeg installed | Required for audio conversion |

## Troubleshooting

### "Local media path is not under an allowed directory"

**Problem**: File is in `/tmp/` or other non-allowed directory

**Solution**: Move file to workspace:
```bash
cp /tmp/voice.opus /Users/a123456/.openclaw/workspace/voice.opus
```

### Still shows as file, not voice message

**Problem**: File extension is not `.opus` or `.ogg`

**Solution**: Convert to opus:
```bash
ffmpeg -i voice.m4a -c libopus voice.opus -y
```

### TTS sounds robotic

**Try different voices**:
```bash
say -v Mei-Jia "试试这个声音" -o test.m4a
```

### Need longer audio

macOS `say` has no practical limit, but for very long text:
- Split into multiple files
- Or use cloud TTS services (Azure, Google, AWS Polly)

## Advanced: Custom Voice Pipeline

For production use, you might want:

1. **Better TTS**: Use Azure TTS, Google TTS, or ElevenLabs
2. **Audio cleanup**: Add noise reduction, normalize volume
3. **Caching**: Cache frequently used phrases

Example with Azure TTS:
```bash
# Install Azure CLI and extension
az extension add --name speech

# Generate with Azure TTS
az cognitiveservices speech synthesize \
  --file /Users/a123456/.openclaw/workspace/voice.wav \
  --text "你好" \
  --locale zh-CN \
  --voice zh-CN-XiaoxiaoNeural

# Convert to opus
ffmpeg -i voice.wav -c libopus voice.opus -y
```

## Related

- [Feishu Message API Docs](https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/reference/im-v1/message/create)
- [Feishu File Upload API](https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/reference/im-v1/file/create)
- [macOS say command](https://ss64.com/osx/say.html)
- [ffmpeg Opus encoding](https://trac.ffmpeg.org/wiki/Encode/Opus)
