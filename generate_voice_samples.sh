#!/bin/bash
# Test different voice styles with VoiceDesign model

MODEL="Qwen3-TTS-12Hz-1.7B-VoiceDesign-4bit"
OUTPUT_DIR="/Users/a123456/.openclaw/workspace"

echo "Generating voice samples with VoiceDesign model..."

# 1. 成熟男声 (Uncle_Fu style)
echo "1. Generating mature male voice..."
curl -s http://127.0.0.1:8080/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d "{\"model\":\"$MODEL\",\"input\":\"年轻人，人生路上遇到点挫折很正常。关键是要站起来，继续往前走。\",\"voice\":\"male-deep\",\"instruct\":\"成熟稳重的中年男声，低沉圆润，语速缓慢，充满人生阅历\"}" \
  -o "$OUTPUT_DIR/voice-mature-male.m4a"

# 2. 北京男声 (Dylan style)
echo "2. Generating Beijing male voice..."
curl -s http://127.0.0.1:8080/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d "{\"model\":\"$MODEL\",\"input\":\"哎哟喂，您这是去哪儿啊？我跟您说，前边儿那馆子特地道！\",\"voice\":\"male-beijing\",\"instruct\":\"北京口音的男声，清晰自然，带点京腔，热情健谈\"}" \
  -o "$OUTPUT_DIR/voice-beijing-male.m4a"

# 3. 年轻女声 (Vivian style)
echo "3. Generating young female voice..."
curl -s http://127.0.0.1:8080/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d "{\"model\":\"$MODEL\",\"input\":\"哎呀，你这个人怎么这样嘛！人家只是想和你聊聊天而已啦～\",\"voice\":\"young-female\",\"instruct\":\"年轻活泼的女声，明亮略带撒娇，语调起伏明显\"}" \
  -o "$OUTPUT_DIR/voice-young-female.m4a"

# 4. 温柔女声 (Serena style)
echo "4. Generating gentle female voice..."
curl -s http://127.0.0.1:8080/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d "{\"model\":\"$MODEL\",\"input\":\"没关系的，慢慢来。我相信你一定可以做到的，我会一直陪着你的。\",\"voice\":\"gentle-female\",\"instruct\":\"温柔细腻的女声，温暖治愈，语速缓慢，充满关怀\"}" \
  -o "$OUTPUT_DIR/voice-gentle-female.m4a"

# 5. 深沉男声 (current default)
echo "5. Generating deep male voice..."
curl -s http://127.0.0.1:8080/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d "{\"model\":\"$MODEL\",\"input\":\"我是 Zero，你的本地 AI 助手。这是用深沉男声录制的语音。\",\"voice\":\"male-deep\",\"instruct\":\"深沉男声，低音，酷且自然\"}" \
  -o "$OUTPUT_DIR/voice-deep-male.m4a"

echo ""
echo "Done! Generated files:"
ls -lh "$OUTPUT_DIR"/voice-*.m4a
