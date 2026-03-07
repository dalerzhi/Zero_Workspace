# Noiz TTS 快速使用指南

_默认音色：`dde1b9b5` - 故事讲述者（子轩）- 活力男声_

---

## 🎤 快速发送语音（飞书）

```bash
python3 << 'EOF'
import requests
import json
import subprocess
import os

# 配置
APP_ID = "cli_a909ad9f75fadbb5"
APP_SECRET = "p1MtN6OZic92OCOpMgxaZdSzAvRfsrys"
CHAT_ID = "ou_7c6c3cdce8475c7a8de63811592c37f9"
API_KEY = "NjU2MDVjYjQtOGMzZC00OTc5LWE0YjgtODM4ZWY3NzYzYWQ1JDY4NzU0NDdAcXEuY29t"

# 默认音色
VOICE_ID = "dde1b9b5"  # 故事讲述者（子轩）

def get_tenant_token():
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    resp = requests.post(url, json={"app_id": APP_ID, "app_secret": APP_SECRET})
    return resp.json()["tenant_access_token"]

def generate_and_send(text, voice_id=VOICE_ID, emo='{"happiness":0.5}', speed="1.0"):
    # 1. 生成 TTS
    resp = requests.post(
        "https://noiz.ai/v1/text-to-speech",
        headers={"Authorization": API_KEY},
        data={
            "text": text,
            "voice_id": voice_id,
            "output_format": "wav",
            "speed": speed,
            "emo": emo
        }
    )
    
    wav_file = "/tmp/voice.wav"
    opus_file = "/tmp/voice.opus"
    
    with open(wav_file, "wb") as f:
        f.write(resp.content)
    
    # 2. 转 OPUS (飞书优化参数)
    subprocess.run([
        "ffmpeg", "-y", "-i", wav_file,
        "-c:a", "libopus", "-b:a", "24k", "-ar", "16000", "-ac", "1",
        opus_file
    ], capture_output=True)
    
    # 3. 获取时长
    result = subprocess.run(
        ["ffprobe", "-i", opus_file, "-v", "quiet", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1"],
        capture_output=True, text=True
    )
    duration_ms = int(float(result.stdout.strip()) * 1000)
    
    # 4. 上传飞书
    token = get_tenant_token()
    url = "https://open.feishu.cn/open-apis/im/v1/files"
    
    with open(opus_file, "rb") as f:
        files = {"file": ("voice.opus", f, "audio/opus")}
        data = {"file_type": "opus", "duration": duration_ms}
        resp = requests.post(url, headers={"Authorization": f"Bearer {token}"}, files=files, data=data)
    
    file_key = resp.json()["data"]["file_key"]
    
    # 5. 发送消息
    url = "https://open.feishu.cn/open-apis/im/v1/messages"
    content = json.dumps({"file_key": file_key, "duration": duration_ms})
    
    resp = requests.post(
        url,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        params={"receive_id_type": "open_id"},
        json={"receive_id": CHAT_ID, "msg_type": "audio", "content": content}
    )
    
    msg_id = resp.json()["data"]["message_id"]
    print(f"✅ 发送成功：{msg_id} (时长：{duration_ms/1000:.2f}s)")

# 使用示例
generate_and_send("你好，这是默认男声测试")
EOF
```

---

## 🎭 情感参数

| 情感 | 参数格式 | 效果 |
|------|---------|------|
| 开心 | `{"happiness":0.7}` | 愉悦、轻快 |
| 温柔 | `{"tenderness":0.6}` | 温暖、关怀 |
| 平静 | `{"calm":0.7}` | 沉稳、专业 |
| 惊讶 | `{"surprise":0.5}` | 兴奋、活力 |
| 关怀 | `{"care":0.5}` | 体贴、温暖 |

---

## ⚡ 语速参数

| 语速 | 参数 | 效果 |
|------|------|------|
| 慢速 | `0.85` | 沉稳、正式 |
| 正常 | `1.0` | 自然对话 |
| 快速 | `1.15` | 活力、兴奋 |

---

## 📁 文件管理

**输出目录**: `/Users/a123456/.openclaw/workspace/tts-output/final/`

**命名规范**:
```
{序号}-{性别}-{情感}.opus
例：01-male-warm.opus
```

---

## 🔧 常用命令

```bash
# 查看音频时长
ffprobe -i file.opus -v quiet -show_entries format=duration -of default=noprint_wrappers=1:nokey=1

# 转换 OPUS（飞书优化）
ffmpeg -y -i input.wav -c:a libopus -b:a 24k -ar 16000 -ac 1 output.opus

# 查看 API 余额
curl -s "https://noiz.ai/v1/usage" -H "Authorization: YOUR_API_KEY"
```

---

**最后更新**: 2026-03-07  
**默认音色**: `dde1b9b5` (故事讲述者 - 子轩)
