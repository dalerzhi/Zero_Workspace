# Noiz TTS 调试总结

_调试日期：2026-03-07_  
_调试人：Zero_

---

## 📋 调试目标

实现飞书原生语音消息发送，使用云端 TTS 生成不同音色和情感的语音。

---

## 🔧 技术方案

### 最终方案

| 组件 | 选择 | 原因 |
|------|------|------|
| **TTS 服务** | Noiz Cloud API | 音质好、速度快、支持情感控制 |
| **音色** | `dde1b9b5` 故事讲述者（子轩） | 中文男声、磁性舒缓 |
| **音频格式** | OPUS | 飞书原生语音消息要求 |
| **OPUS 参数** | 16kHz, 单声道，24kbps | 飞书优化参数 |
| **发送方式** | 飞书 API 直接调用 | 支持传递 duration 参数 |

---

## ⚠️ 遇到的问题及解决方案

### 问题 1：语音都是默认女声

**现象**: 发送的 6 段语音听起来都是女声

**根因**: 
- 使用的音色 ID `b89cf430` 是 **英文男声**（标签：`English,Young,Male`）
- 不适合中文文本，API 可能自动切换到默认女声

**解决**:
```python
# 正确的中文男声音色 ID
VOICE_ID = "dde1b9b5"  # 故事讲述者（子轩）- 中文，青年，男，磁性，舒缓
```

**经验**: 
- ✅ 必须选择标签含 `中文` 的音色
- ✅ 通过 API 获取音色列表：`GET /v1/voices?voice_type=built-in`

---

### 问题 2：情感参数没生效

**现象**: 不同情感的语音听起来一样

**根因**: 情感参数格式错误
```python
# ❌ 错误格式（大写）
{"Joy": 0.7, "Calm": 0.5}

# ✅ 正确格式（小写，参考 API 文档）
{"happiness": 0.7, "calm": 0.5}
```

**支持的情感参数**:
```json
{"happiness": 0.7}    // 开心/活力
{"tenderness": 0.6}   // 温柔
{"calm": 0.8}         // 平静
{"surprise": 0.5}     // 惊讶
{"care": 0.5}         // 关怀
```

**验证方法**:
```python
# 测试 API 是否真的接受 emo 参数
resp1 = api(text="测试", emo=None)  # 110636 bytes
resp2 = api(text="测试", emo='{"happiness":0.9}')  # 128556 bytes
# 文件大小不同 → 参数生效
```

---

### 问题 3：语音有爆音瑕疵

**现象**: 飞书播放时有爆音/杂音

**根因**: OPUS 编码参数不符合飞书要求

| 参数 | 错误值 ❌ | 正确值 ✅ |
|------|----------|----------|
| 采样率 | 48000 Hz | **16000 Hz** |
| 声道 | 立体声 | **单声道** |
| 比特率 | 64kbps | **24kbps** |

**修复代码**:
```python
subprocess.run([
    "ffmpeg", "-y", "-i", input_wav,
    "-c:a", "libopus",
    "-b:a", "24k",      # 24kbps（飞书推荐 16-32kbps）
    "-ar", "16000",     # 16kHz（飞书要求）
    "-ac", "1",         # 单声道
    output_opus
])
```

---

### 问题 4：飞书语音显示时长 0:00

**现象**: 语音消息显示 `0:00` 时长

**根因**: `openclaw message send` 工具上传音频时**没有传递 `duration` 参数**

**飞书 API 要求**:
```python
# 上传文件时必须传递 duration（毫秒）
data = {
    "file_type": "opus",
    "duration": 3826  # ← 关键参数！
}
```

**完整发送流程**:
```python
# 1. 获取音频时长（毫秒）
duration_ms = int(ffprobe_duration_sec * 1000)

# 2. 上传文件（带 duration）
file_key = upload_audio(file_path, duration_ms)

# 3. 发送消息（content 中也要带 duration）
content = json.dumps({"file_key": file_key, "duration": duration_ms})
send_audio_message(content)
```

---

### 问题 5：技能脚本调用本地 TTS

**现象**: `feishu-voice.sh` 技能使用 macOS `say` 命令，不是云端 API

**根因**: 技能创建时使用了本地 TTS 方案

**修复**:
```bash
# ❌ 原代码（本地 say）
say -v "$VOICE" "$TEXT" -o "$M4A_FILE"

# ✅ 修复后（Noiz API）
bash "$NOIZ_SCRIPT" speak --voice-id "$VOICE_ID" -t "$TEXT" -o "$WAV_FILE"
```

---

### 问题 6：文件路径权限问题

**现象**: `Local media path is not under an allowed directory`

**根因**: OpenClaw 不允许访问 `/tmp/` 目录

**解决**:
```python
# 复制到 workspace 目录
cp /tmp/voice.opus /Users/a123456/.openclaw/workspace/tts-output/final/
```

**最佳实践**:
```python
# 创建分类目录
mkdir -p /Users/a123456/.openclaw/workspace/tts-output/{male,female,final}

# 输出到子目录，保持 workspace 整洁
output_dir = "/Users/a123456/.openclaw/workspace/tts-output/final"
```

---

## 🎯 推荐音色列表

### 中文男声（推荐）

| voice_id | 名称 | 标签 | 适用场景 |
|----------|------|------|----------|
| `dde1b9b5` ⭐ | 故事讲述者（子轩） | 中文，青年，男，磁性，舒缓 | **默认**，日常对话 |
| `96270d87` | 故事讲述者（子轩） | 中文，青年，男，磁性，共鸣 | 正式场合 |
| `8316cdf1` | 温柔男声（亦辰） | 中文，青年，男，磁性，舒缓 | 温柔场景 |

### 中文女声（备选）

| voice_id | 名称 | 标签 | 适用场景 |
|----------|------|------|----------|
| `4f71a876` ⭐ | 故事讲述者（小雨） | 中文，青年，女，磁性，舒缓 | 日常对话 |
| `e47a10c4` | 活泼少女（小雨） | 中文，青年，女，喜悦，活泼 | 活力场景 |

### 避免使用的音色

| voice_id | 名称 | 问题 |
|----------|------|------|
| `d44f2ab4` ❌ | 游戏少女（小雨） | 标签含"恐惧"，听起来歇斯底里 |
| `b89cf430` ❌ | 故事讲述者（子轩） | 英文男声，不适合中文 |

---

## 📝 标准操作流程

### 1. 生成 TTS 音频

```python
import requests

API_KEY = "NjU2MDVjYjQtOGMzZC00OTc5LWE0YjgtODM4ZWY3NzYzYWQ1JDY4NzU0NDdAcXEuY29t"
VOICE_ID = "dde1b9b5"  # 默认音色

resp = requests.post(
    "https://noiz.ai/v1/text-to-speech",
    headers={"Authorization": API_KEY},
    data={
        "text": "你好，这是测试",
        "voice_id": VOICE_ID,
        "output_format": "wav",
        "speed": "1.0",
        "emo": '{"happiness":0.5}'  # 可选
    }
)

with open("/tmp/voice.wav", "wb") as f:
    f.write(resp.content)
```

### 2. 转换为 OPUS（飞书优化）

```python
import subprocess

subprocess.run([
    "ffmpeg", "-y",
    "-i", "/tmp/voice.wav",
    "-c:a", "libopus",
    "-b:a", "24k",      # 24kbps
    "-ar", "16000",     # 16kHz
    "-ac", "1",         # 单声道
    "/tmp/voice.opus"
], capture_output=True)
```

### 3. 获取时长

```python
result = subprocess.run(
    ["ffprobe", "-i", "/tmp/voice.opus",
     "-v", "quiet",
     "-show_entries", "format=duration",
     "-of", "default=noprint_wrappers=1:nokey=1"],
    capture_output=True, text=True
)
duration_ms = int(float(result.stdout.strip()) * 1000)
```

### 4. 上传飞书（带 duration）

```python
import requests

def get_tenant_token():
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    resp = requests.post(url, json={"app_id": APP_ID, "app_secret": APP_SECRET})
    return resp.json()["tenant_access_token"]

def upload_audio(file_path, duration_ms):
    token = get_tenant_token()
    url = "https://open.feishu.cn/open-apis/im/v1/files"
    
    with open(file_path, "rb") as f:
        files = {"file": ("voice.opus", f, "audio/opus")}
        data = {"file_type": "opus", "duration": duration_ms}  # ← 关键！
        resp = requests.post(url, headers={"Authorization": f"Bearer {token}"}, files=files, data=data)
    
    return resp.json()["data"]["file_key"]

file_key = upload_audio("/tmp/voice.opus", duration_ms)
```

### 5. 发送语音消息

```python
def send_audio_message(file_key, duration_ms, chat_id):
    token = get_tenant_token()
    url = "https://open.feishu.cn/open-apis/im/v1/messages"
    
    content = json.dumps({"file_key": file_key, "duration": duration_ms})
    
    resp = requests.post(
        url,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        params={"receive_id_type": "open_id"},
        json={"receive_id": chat_id, "msg_type": "audio", "content": content}
    )
    
    return resp.json()["data"]["message_id"]

msg_id = send_audio_message(file_key, duration_ms, CHAT_ID)
```

---

## 📁 文件管理规范

### 目录结构

```
workspace/
└── tts-output/
    ├── male/      # 男声音色样本
    ├── female/    # 女声音色样本
    └── final/     # 最终发送版本
        ├── 01-male-warm.opus
        ├── 02-male-energetic.opus
        └── ...
```

### 命名规范

```
{序号}-{性别}-{情感}.opus
例：01-male-warm.opus
```

### 清理策略

- 临时文件：`/tmp/voice*.wav` `rm -f` 及时清理
- 最终文件：保留在 `tts-output/final/`
- 中间文件：OPUS 转换后可删除 WAV

---

## 🔑 配置信息

### API Key

```bash
# 存储在 ~/.noiz_api_key
NjU2MDVjYjQtOGMzZC00OTc5LWE0YjgtODM4ZWY3NzYzYWQ1JDY4NzU0NDdAcXEuY29t
```

### 飞书凭证

```python
APP_ID = "cli_a909ad9f75fadbb5"
APP_SECRET = "p1MtN6OZic92OCOpMgxaZdSzAvRfsrys"
CHAT_ID = "ou_7c6c3cdce8475c7a8de63811592c37f9"
```

### 默认音色

```python
VOICE_ID = "dde1b9b5"  # 故事讲述者（子轩）
```

---

## 💡 经验总结

### ✅ 正确做法

1. **音色选择**: 必须选择标签含 `中文` 的音色
2. **情感参数**: 使用小写格式 `{"happiness":0.7}`
3. **OPUS 参数**: 16kHz, 单声道，24kbps
4. **上传 API**: 必须传递 `duration` 参数（毫秒）
5. **文件管理**: 使用子目录分类，不放在 workspace 根目录

### ❌ 错误做法

1. ❌ 使用英文音色 ID 处理中文文本
2. ❌ 情感参数用大写 `{"Joy":0.7}`
3. ❌ OPUS 用 48kHz 立体声 64kbps
4. ❌ 上传时不传递 `duration`
5. ❌ 文件直接放在 `/tmp/` 或 workspace 根目录

### 🎯 关键发现

1. **API 验证**: 通过比较返回文件大小验证参数是否生效
2. **飞书要求**: OPUS 必须 16kHz 单声道，否则有爆音
3. **时长显示**: 必须同时在上一步和发送时传递 `duration`
4. **音色标签**: 避免"恐惧"、"游戏"等标签的音色

---

## 📚 参考文档

- Noiz API 文档：https://docs.noiz.ai/api-documentation
- 飞书文件上传 API：https://open.feishu.cn/document/server-docs/im-v1/file/create
- 飞书消息发送 API：https://open.feishu.cn/document/server-docs/im-v1/message/create
- FFmpeg OPUS 编码：https://trac.ffmpeg.org/wiki/Encode/Opus

---

**最后更新**: 2026-03-07  
**状态**: ✅ 调试完成，可投入生产使用
