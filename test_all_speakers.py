#!/usr/bin/env python3
"""
Test all CustomVoice speakers from Qwen3-TTS
"""

import torch
import soundfile as sf
from qwen_tts import Qwen3TTSModel

# Speaker definitions with sample texts
SPEAKERS = {
    "Vivian": {
        "desc": "年轻女声，明亮略带锋芒",
        "text": "哎呀，你这个人怎么这样嘛！人家只是想和你聊聊天而已啦～",
        "lang": "Chinese"
    },
    "Serena": {
        "desc": "温柔女声，温暖细腻",
        "text": "没关系的，慢慢来。我相信你一定可以做到的，我会一直陪着你的。",
        "lang": "Chinese"
    },
    "Uncle_Fu": {
        "desc": "成熟男声，低沉圆润",
        "text": "年轻人，人生路上遇到点挫折很正常。关键是要站起来，继续往前走。",
        "lang": "Chinese"
    },
    "Dylan": {
        "desc": "北京男声，清晰自然",
        "text": "哎哟喂，您这是去哪儿啊？我跟您说，前边儿那馆子特地道！",
        "lang": "Chinese"
    },
    "Eric": {
        "desc": "成都男声，四川方言",
        "text": "哎呀，你个瓜娃子！走嘛，我请你吃火锅噻，巴适得很！",
        "lang": "Chinese"
    },
    "Ryan": {
        "desc": "男声，英文",
        "text": "Hey mate! Ready to take on the world? Let's make this happen together!",
        "lang": "English"
    },
    "Aiden": {
        "desc": "美国男声",
        "text": "What's up, dude! This is gonna be awesome. Let's rock and roll!",
        "lang": "English"
    },
    "Ono_Anna": {
        "desc": "日本女声",
        "text": "こんにちは！今日は一緒に楽しい時間を過ごしましょうね！",
        "lang": "Japanese"
    },
    "Sohee": {
        "desc": "韩国女声",
        "text": "안녕하세요! 오늘 하루도 화이팅하세요!",
        "lang": "Korean"
    }
}

def main():
    print("Loading CustomVoice model...")
    model = Qwen3TTSModel.from_pretrained(
        "Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice",
        device_map="mps",  # Apple Silicon
        dtype=torch.float32,  # MPS doesn't support bfloat16
    )
    
    print(f"\nSupported speakers: {model.get_supported_speakers()}")
    print(f"Supported languages: {model.get_supported_languages()}\n")
    
    for speaker_name, speaker_info in SPEAKERS.items():
        print(f"\n{'='*60}")
        print(f"Testing: {speaker_name} - {speaker_info['desc']}")
        print(f"Text: {speaker_info['text']}")
        print(f"{'='*60}")
        
        try:
            wavs, sr = model.generate_custom_voice(
                text=speaker_info['text'],
                language=speaker_info['lang'],
                speaker=speaker_name,
            )
            
            output_file = f"/Users/a123456/.openclaw/workspace/voice-{speaker_name}.wav"
            sf.write(output_file, wavs[0], sr)
            print(f"✓ Saved: {output_file}")
            
        except Exception as e:
            print(f"✗ Error: {e}")
    
    print("\n\nAll tests completed!")

if __name__ == "__main__":
    main()
