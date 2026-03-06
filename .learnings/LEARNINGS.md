## [LRN-20260306-008] knowledge_gap

**Logged**: 2026-03-06T20:51:00+08:00
**Priority**: critical
**Status**: pending
**Area**: infra

### Summary
Qwen3-TTS VoiceDesign 模型支持通过 `instruct` 参数描述音色（包括性别、年龄、情感等）

### Details
根据官方文档 (github.com/QwenLM/Qwen3-TTS):

**VoiceDesign 模型用法**:
```python
model.generate_voice_design(
    text="你好",
    language="Chinese",
    instruct="体现撒娇稚嫩的萝莉女声，音调偏高且起伏明显"
)
```

**CustomVoice 模型支持的音色**:
- Vivian - 年轻女声 (Chinese)
- Serena - 温柔女声 (Chinese)
- Uncle_Fu - 成熟男声 (Chinese) ⭐
- Dylan - 北京男声 (Chinese) ⭐
- Eric - 成都男声 (Sichuan Dialect) ⭐
- Ryan - 男声 (English) ⭐
- Aiden - 美国男声 (English) ⭐
- Ono_Anna - 日本女声 (Japanese)
- Sohee - 韩国女声 (Korean)

### Suggested Action
1. 测试 Izwi 是否支持 `instruct` 参数
2. 或者直接用官方 Python SDK
3. 云端部署时使用 CustomVoice 模型（有现成男声）

### Metadata
- Source: official_documentation
- Related Files: https://github.com/QwenLM/Qwen3-TTS
- Tags: qwen3-tts, voice-design, male-voice
- Pattern-Key: qwen3-tts-voice-control

---
