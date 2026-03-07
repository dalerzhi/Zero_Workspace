# TTS 方案对比

_评估时间：2026-03-07_

---

## 📊 方案对比

| 特性 | **NoizAI TTS** (新) | **Izwi TTS** (现有) |
|------|-------------------|-------------------|
| **后端** | Noiz Cloud / Kokoro Local | Qwen3-TTS (本地) |
| **音质** | ⭐⭐⭐⭐⭐ 生产级 | ⭐⭐⭐⭐ 良好 |
| **速度** | ⭐⭐⭐⭐ 快 (云端) | ⭐⭐ 慢 (本地 1.7B) |
| **情感控制** | ✅ 支持 (Joy, Sadness 等) | ❌ 不支持 |
| **音色克隆** | ✅ 支持 (参考音频) | ⚠️ 有限 (VoiceDesign) |
| **多语言** | ✅ 中英文混合 | ✅ 中英文 |
| **时长控制** | ✅ 精确 (SRT 时间轴) | ❌ 不支持 |
| **飞书发送** | ✅ 内置 (`speak_and_send_feishu`) | ✅ 手动脚本 |
| **Telegram** | ✅ 内置 | ❌ 不支持 |
| **Discord** | ✅ 内置 | ❌ 不支持 |
| **成本** | 💰 云端 API (免费额度？) | 💰 免费 (本地) |
| **依赖** | `ffmpeg` | `ffmpeg`, `say` |
| **配置** | API Key 或本地 Kokoro | 模型下载 |

---

## 🎯 NoizAI TTS 优势

### 1. 多平台原生发送

```bash
# 飞书 - 直接发送语音消息
bash skills/tts/scripts/tts.sh speak_and_send_feishu \
  -t "你好" \
  --chat-id oc_xxx \
  --app-id cli_xxx \
  --app-secret xxx

# Telegram - 直接发送语音
bash skills/tts/scripts/tts.sh speak_and_send_telegram \
  -t "Hello" \
  --chat-id 123456 \
  --bot-token BOT_TOKEN

# Discord - 直接发送语音
bash skills/tts/scripts/tts.sh speak_and_send_discord \
  -t "Hello" \
  --channel-id 123456 \
  --bot-token BOT_TOKEN
```

**对比 Izwi**：需要手动写脚本转 opus + message 发送

---

### 2. 情感控制

```json
{
  "default": { "voice_id": "voice_123", "target_lang": "zh" },
  "segments": {
    "1": { "voice_id": "voice_host", "emo": { "Joy": 0.6 } },
    "2-4": { "voice_id": "voice_guest", "emo": { "Sadness": 0.3 } }
  }
}
```

**对比 Izwi**：只有 VoiceDesign 的 `instruct` 参数，不支持细粒度情感

---

### 3. 时间轴精确控制（SRT 模式）

```bash
# 1. 生成 SRT
bash skills/tts/scripts/tts.sh to-srt \
  -i article.txt \
  -o article.srt \
  --cps 15

# 2. 创建语音映射
cat > vm.json <<'EOF'
{
  "default": { "voice": "zf_xiaoni", "lang": "cmn" },
  "segments": {
    "1": { "voice": "zm_yunxi" },
    "5-8": { "voice": "af_sarah", "lang": "en-us", "speed": 0.9 }
  }
}
EOF

# 3. 渲染时间轴音频
bash skills/tts/scripts/tts.sh render \
  --srt input.srt \
  --voice-map vm.json \
  -o output.wav
```

**对比 Izwi**：不支持时间轴控制

---

### 4. 音色克隆

```bash
# 用参考音频克隆音色
bash skills/tts/scripts/tts.sh speak \
  -t "Hello world" \
  --ref-audio ./my_voice.wav \
  -o cloned.wav

# 或用 URL
bash skills/tts/scripts/tts.sh speak \
  -t "Hello" \
  --ref-audio https://example.com/voice.wav \
  -o cloned.wav
```

**对比 Izwi**：VoiceDesign 需要指定模型，不支持自定义参考音频

---

### 5. 多平台技能集成

NoizAI 技能已集成到：
- ✅ OpenClaw
- ✅ Gemini CLI
- ✅ Amp
- ✅ Cline
- ✅ Cursor
- ✅ Codex

**对比 Izwi**：只有 OpenClaw 飞书技能

---

## ⚠️ NoizAI TTS 劣势

### 1. 需要 API Key（推荐模式）

**Noiz Cloud**：
- 需要注册 https://developers.noiz.ai/api-keys
- 可能有免费额度（待确认）
- 云端处理，速度快

**Izwi**：
- 完全本地，无需 API
- 但模型大（1.7B-4bit = 2.15GB）
- 速度慢（5 秒语音≈40 秒生成）

---

### 2. 本地 Kokoro 需要安装

```bash
uv tool install kokoro-tts
```

**安装时间**：可能需要 5-10 分钟（下载模型）
**模型大小**：Kokoro 约 1-2GB

**对比 Izwi**：已经安装完成

---

### 3. 飞书配置需要权限

NoizAI 的 `speak_and_send_feishu` 需要：
- `FEISHU_APP_ID`
- `FEISHU_APP_SECRET`
- `FEISHU_CHAT_ID`
- `FEISHU_TENANT_ACCESS_TOKEN`

**对比 Izwi**：同样需要这些，但我们的飞书技能已经配置好了

---

## 🎯 推荐方案

### 方案 A：Noiz Cloud（推荐用于生产）

**适合场景**：
- ✅ 需要高质量语音
- ✅ 需要情感控制
- ✅ 需要多平台发送（飞书 + Telegram + Discord）
- ✅ 需要音色克隆
- ✅ 可以接受 API 成本

**配置**：
```bash
# 1. 获取 API Key
# 访问 https://developers.noiz.ai/api-keys

# 2. 配置
bash skills/tts/scripts/tts.sh config \
  --set-api-key YOUR_KEY

# 3. 测试
bash skills/tts/scripts/tts.sh speak \
  -t "你好，这是 NoizAI TTS 测试" \
  -o /tmp/test.wav
```

---

### 方案 B：Kokoro Local（推荐用于开发/测试）

**适合场景**：
- ✅ 完全本地，无 API 成本
- ✅ 隐私敏感内容
- ✅ 可以接受安装时间
- ✅ 音质要求中等

**配置**：
```bash
# 1. 安装 Kokoro
uv tool install kokoro-tts

# 2. 测试（自动检测本地后端）
bash skills/tts/scripts/tts.sh speak \
  -t "Hello world" \
  -o /tmp/test.wav
```

---

### 方案 C：混合模式（最佳）

**日常开发**：Kokoro Local（免费，快速迭代）
**生产环境**：Noiz Cloud（高质量，情感控制）
**特殊场景**：Izwi（已有配置，飞书专用）

**配置**：
```bash
# 默认用 Kokoro
bash skills/tts/scripts/tts.sh speak -t "Hello" -o out.wav

# 需要情感时用 Noiz
bash skills/tts/scripts/tts.sh speak \
  -t "Hello" \
  --backend noiz \
  --emotion happy \
  -o out.wav

# 飞书专用（已有技能）
./skills/feishu-voice/feishu-voice.sh "你好" ou_xxx
```

---

## 📋 测试清单

### Noiz Cloud

- [ ] 获取 API Key
- [ ] 配置 `~/.noiz_api_key`
- [ ] 测试基础 TTS
- [ ] 测试情感控制
- [ ] 测试音色克隆
- [ ] 测试飞书发送
- [ ] 测试 Telegram 发送
- [ ] 测试 Discord 发送

### Kokoro Local

- [ ] 安装 `kokoro-tts`
- [ ] 测试基础 TTS
- [ ] 测试多语言
- [ ] 测试飞书发送（需要集成）

### Izwi（现有）

- [ ] 保持现有飞书技能
- [ ] 作为备选方案

---

## 💡 建议

**短期（本周）**：
1. 安装 Kokoro Local（正在安装）
2. 测试基础功能
3. 对比音质和速度

**中期（下周）**：
1. 申请 Noiz API Key
2. 测试情感控制和音色克隆
3. 评估成本

**长期**：
1. 生产用 Noiz Cloud
2. 开发用 Kokoro Local
3. Izwi 作为备选

---

**下一步**：等待 Kokoro 安装完成，然后测试对比。
