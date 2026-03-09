#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
飞书语音消息发送脚本
使用 Noiz Cloud API 生成 TTS，然后发送到飞书
"""

import requests
import subprocess
import tempfile
import os
import json
import sys
from pathlib import Path

# ============ 配置 ============
WORKSPACE = Path.home() / '.openclaw' / 'workspace'

# Noiz API 配置
NOIZ_API_KEY_FILE = Path.home() / '.noiz_api_key'
DEFAULT_VOICE_ID = 'dde1b9b5'  # 故事讲述者（子轩）- 活力男声

# 飞书配置
FEISHU_APP_ID = 'cli_a909ad9f75fadbb5'
FEISHU_APP_SECRET = 'p1MtN6OZic92OCOpMgxaZdSzAvRfsrys'
DEFAULT_CHAT_ID = 'ou_7c6c3cdce8475c7a8de63811592c37f9'


def get_noiz_api_key():
    """获取 Noiz API Key"""
    if NOIZ_API_KEY_FILE.exists():
        with open(NOIZ_API_KEY_FILE, 'r') as f:
            return f.read().strip()
    print("❌ 未找到 Noiz API Key，请创建 ~/.noiz_api_key 文件")
    sys.exit(1)


def get_tenant_token():
    """获取飞书 tenant_access_token"""
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    resp = requests.post(url, json={"app_id": FEISHU_APP_ID, "app_secret": FEISHU_APP_SECRET})
    data = resp.json()
    
    if data.get('code') != 0:
        print(f"❌ 获取飞书 token 失败：{data.get('msg')}")
        sys.exit(1)
    
    return data['tenant_access_token']


def generate_tts(text, voice_id=DEFAULT_VOICE_ID, output_file=None):
    """使用 Noiz API 生成 TTS"""
    api_key = get_noiz_api_key()
    
    url = "https://noiz.ai/v1/text-to-speech"
    headers = {"Authorization": api_key}
    data = {
        "text": text,
        "voice_id": voice_id,
        "output_format": "wav",
        "speed": "1.0"
    }
    
    print(f"🎤 正在生成 TTS (voice_id: {voice_id})...")
    resp = requests.post(url, headers=headers, data=data)
    
    if resp.status_code != 200:
        print(f"❌ TTS 生成失败：{resp.status_code}")
        print(resp.text)
        sys.exit(1)
    
    # 保存 WAV 文件
    if output_file is None:
        output_file = WORKSPACE / f"voice_{os.getpid()}.wav"
    
    with open(output_file, 'wb') as f:
        f.write(resp.content)
    
    print(f"✅ TTS 生成完成：{output_file}")
    return output_file


def convert_to_opus(wav_file, opus_file=None):
    """将 WAV 转换为 OPUS 格式（飞书优化参数）"""
    if opus_file is None:
        opus_file = str(wav_file).replace('.wav', '.opus')
    
    print(f"🔄 转换为 OPUS 格式...")
    
    # 飞书优化参数：16kHz, 单声道，24kbps
    cmd = [
        'ffmpeg', '-y',
        '-i', str(wav_file),
        '-c:a', 'libopus',
        '-b:a', '24k',
        '-ar', '16000',
        '-ac', '1',
        str(opus_file)
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ 转换失败：{result.stderr}")
        sys.exit(1)
    
    print(f"✅ OPUS 转换完成：{opus_file}")
    return opus_file


def get_audio_duration(opus_file):
    """获取音频时长（毫秒）"""
    cmd = [
        'ffprobe', '-i', str(opus_file),
        '-v', 'quiet',
        '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1'
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"⚠️ 无法获取时长")
        return None
    
    duration_sec = float(result.stdout.strip())
    duration_ms = int(duration_sec * 1000)
    
    print(f"⏱️  音频时长：{duration_ms}ms ({duration_sec:.2f}s)")
    return duration_ms


def upload_to_feishu(token, opus_file, duration_ms):
    """上传音频文件到飞书"""
    url = "https://open.feishu.cn/open-apis/im/v1/files"
    headers = {"Authorization": f"Bearer {token}"}
    
    print(f"📤 上传到飞书...")
    
    with open(opus_file, 'rb') as f:
        files = {"file": (os.path.basename(opus_file), f, "audio/opus")}
        data = {
            "file_type": "opus",
            "duration": duration_ms  # 关键！传递时长
        }
        resp = requests.post(url, headers=headers, files=files, data=data)
    
    result = resp.json()
    
    if result.get('code') != 0:
        print(f"❌ 上传失败：{result.get('msg')}")
        sys.exit(1)
    
    file_key = result['data']['file_key']
    print(f"✅ 上传成功：{file_key}")
    return file_key


def send_voice_message(token, chat_id, file_key, duration_ms):
    """发送语音消息到飞书"""
    url = "https://open.feishu.cn/open-apis/im/v1/messages"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    content = json.dumps({
        "file_key": file_key,
        "duration": duration_ms
    })
    
    payload = {
        "receive_id": chat_id,
        "msg_type": "audio",
        "content": content
    }
    
    params = {"receive_id_type": "open_id"}
    
    print(f"📨 发送语音消息...")
    resp = requests.post(url, headers=headers, params=params, json=payload)
    
    result = resp.json()
    
    if result.get('code') != 0:
        print(f"❌ 发送失败：{result.get('msg')}")
        sys.exit(1)
    
    msg_id = result['data']['message_id']
    print(f"✅ 发送成功：{msg_id}")
    return msg_id


def send_feishu_voice(text, chat_id=None, voice_id=DEFAULT_VOICE_ID, cleanup=True):
    """完整流程：生成 TTS → 转换 OPUS → 发送到飞书"""
    if chat_id is None:
        chat_id = DEFAULT_CHAT_ID
    
    # 1. 生成 TTS
    wav_file = generate_tts(text, voice_id)
    
    # 2. 转换为 OPUS
    opus_file = convert_to_opus(wav_file)
    
    # 3. 获取时长
    duration_ms = get_audio_duration(opus_file)
    if duration_ms is None:
        duration_ms = 15000  # 默认 15 秒
    
    # 4. 获取飞书 token
    token = get_tenant_token()
    
    # 5. 上传到飞书
    file_key = upload_to_feishu(token, opus_file, duration_ms)
    
    # 6. 发送消息
    msg_id = send_voice_message(token, chat_id, file_key, duration_ms)
    
    # 7. 清理临时文件
    if cleanup:
        print(f"🧹 清理临时文件...")
        try:
            os.remove(wav_file)
            os.remove(opus_file)
            print(f"✅ 已清理")
        except:
            pass
    
    print(f"\n🎉 完成！")
    print(f"   消息 ID: {msg_id}")
    print(f"   接收者：{chat_id}")
    print(f"   时长：{duration_ms}ms")
    
    return msg_id


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='飞书语音消息发送工具')
    parser.add_argument('text', help='要发送的文本内容')
    parser.add_argument('--chat-id', '-c', help='飞书聊天 ID（默认：ou_7c6c3cdce8475c7a8de63811592c37f9）')
    parser.add_argument('--voice-id', '-v', default=DEFAULT_VOICE_ID, help=f'音色 ID（默认：{DEFAULT_VOICE_ID}）')
    parser.add_argument('--keep-files', action='store_true', help='保留临时文件')
    
    args = parser.parse_args()
    
    if not args.text:
        parser.print_help()
        sys.exit(1)
    
    print("="*60)
    print("🎤 飞书语音消息发送")
    print("="*60)
    print(f"文本：{args.text[:50]}...")
    print(f"音色：{args.voice_id}")
    print(f"接收者：{args.chat_id or DEFAULT_CHAT_ID}")
    print("="*60)
    print()
    
    try:
        send_feishu_voice(
            text=args.text,
            chat_id=args.chat_id,
            voice_id=args.voice_id,
            cleanup=not args.keep_files
        )
    except Exception as e:
        print(f"\n❌ 发送失败：{e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
