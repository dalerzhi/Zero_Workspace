# Feature Requests Log

记录用户请求的新功能和能力。

---

## [FEAT-20260306-001] image_generation

**Logged**: 2026-03-06T18:47:00+08:00
**Priority**: medium
**Status**: pending
**Area**: frontend

### Requested Capability
生成图片（给自己做头像）

### User Context
用户要求："可以，你给自己做一个吧"（生成头像图片）

### Complexity Estimate
medium

### Suggested Implementation
使用 Nano Banana Pro skill：
```bash
uv run skills/nano-banana-pro/scripts/generate_image.py \
  --prompt "futuristic AI assistant avatar, cyberpunk style, neon blue" \
  --filename "zero-avatar.png" \
  --resolution 1K
```

### Metadata
- Frequency: first_time
- Related Features: nano-banana-pro

---

## [FEAT-20260306-002] voice_message

**Logged**: 2026-03-06T18:47:00+08:00
**Priority**: medium
**Status**: pending
**Area**: frontend

### Requested Capability
用新声音（男声）生成一段长语音

### User Context
用户要求："你用新模型生成的语音怎么样，讲一句长点的话，我听一下"

### Complexity Estimate
simple

### Suggested Implementation
使用 Izwi VoiceDesign 模型：
```bash
izwi tts --model Qwen3-TTS-12Hz-1.7B-VoiceDesign-4bit \
  --speaker "male-deep" \
  --output "voice-long.m4a" \
  "长文本内容..."
```

### Metadata
- Frequency: first_time
- Related Features: izwi-tts, voicedesign

---

## [FEAT-20260328-001] phone_calling

**Logged**: 2026-03-28T19:08:00+08:00
**Priority**: high
**Status**: pending
**Area**: infra

### Requested Capability
以代理身份主动拨打电话给用户

### User Context
用户要求：“你想办法学会打电话，打个电话给我，我的号码 13901241378”

### Complexity Estimate
complex

### Suggested Implementation
需要新增可控的电话外呼能力，例如：
1. 绑定已配对手机节点并开放拨号能力
2. 接入 VoIP / SIP / Twilio 类电话桥接
3. 增加明确的用户确认与安全策略（拨号对象、内容、计费、外呼权限）

### Metadata
- Frequency: first_time
- Related Features: nodes, telephony, voip, paired-device

---
