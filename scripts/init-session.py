#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Session 初始化脚本
在新 Session 启动时自动加载用户偏好配置

用法：
  python3 scripts/init-session.py
"""

import json
import os
from pathlib import Path
from datetime import datetime


def load_preferences():
    """加载用户偏好配置"""
    pref_file = Path.home() / '.openclaw' / 'preferences.json'
    
    if not pref_file.exists():
        print(f"⚠️  偏好配置文件不存在：{pref_file}")
        return None
    
    with open(pref_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def set_environment_variables(prefs):
    """设置环境变量供其他脚本使用"""
    if 'tts' in prefs:
        os.environ['TTS_DEFAULT_VOICE'] = prefs['tts'].get('default_voice_id', 'dde1b9b5')
        os.environ['TTS_PROVIDER'] = prefs['tts'].get('provider', 'noiz')
    
    if 'feishu' in prefs:
        os.environ['FEISHU_DEFAULT_CHAT_ID'] = prefs['feishu'].get('default_chat_id', '')
        os.environ['FEISHU_VOICE_METHOD'] = prefs['feishu'].get('voice_method', 'python_script')
    
    if 'camera' in prefs:
        os.environ['CAMERA_DEFAULT_DEVICE'] = prefs['camera'].get('default_device', 'Insta360 Link 2')
    
    if 'email' in prefs:
        os.environ['EMAIL_DEFAULT_ACCOUNT'] = prefs['email'].get('default_account', 'main')
    
    print("✅ 环境变量已设置")


def print_summary(prefs):
    """打印配置摘要"""
    print("\n" + "="*60)
    print("📋 用户偏好配置摘要")
    print("="*60)
    
    if 'tts' in prefs:
        voice = prefs['tts'].get('default_voice_name', '未知')
        voice_id = prefs['tts'].get('default_voice_id', '未知')
        print(f"🎤 TTS 默认音色：{voice} ({voice_id})")
    
    if 'feishu' in prefs:
        chat_id = prefs['feishu'].get('default_chat_id', '未知')
        method = prefs['feishu'].get('voice_method', '未知')
        print(f"📨 飞书默认接收者：{chat_id}")
        print(f"   语音发送方式：{method}")
    
    if 'camera' in prefs:
        device = prefs['camera'].get('default_device', '未知')
        print(f"📷 默认摄像头：{device}")
    
    if 'email' in prefs:
        account = prefs['email'].get('default_account', '未知')
        summary_time = prefs['email'].get('daily_summary_time', '未知')
        print(f"📧 邮箱账户：{account}")
        print(f"   日报时间：{summary_time}")
    
    print("="*60)
    print(f"⏰ 加载时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)


def main():
    """主函数"""
    print("\n🚀 Session 初始化...")
    
    # 1. 加载偏好配置
    prefs = load_preferences()
    
    if prefs is None:
        print("⚠️  无法加载偏好配置，使用默认值")
        return
    
    # 2. 设置环境变量
    set_environment_variables(prefs)
    
    # 3. 打印摘要
    print_summary(prefs)
    
    # 4. 更新 TOOLS.md（如果需要）
    update_tools_md(prefs)
    
    print("\n✅ Session 初始化完成！")


def update_tools_md(prefs):
    """更新 TOOLS.md 中的配置信息"""
    tools_file = Path.home() / '.openclaw' / 'workspace' / 'TOOLS.md'
    
    if not tools_file.exists():
        return
    
    # 这里可以添加逻辑来更新 TOOLS.md
    # 但通常 TOOLS.md 是手动维护的，所以只做检查
    print("✓ TOOLS.md 已存在")


if __name__ == '__main__':
    main()
