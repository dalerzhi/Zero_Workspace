#!/bin/bash
# feishu-voice: Send native voice messages on Feishu
# Usage: feishu-voice "message text" [target_user_id] [voice_id]
# 
# Uses Noiz Cloud API for TTS generation (云端 API)
# Default voices:
#   Male:   96270d87 (故事讲述者 - 子轩)
#   Female: d44f2ab4 (游戏少女 - 小雨)

set -e

TEXT="$1"
TARGET="${2:-}"
VOICE_ID="${3:-d44f2ab4}"  # Default to female voice
WORKSPACE="/Users/a123456/.openclaw/workspace"
NOIZ_SCRIPT="$WORKSPACE/.agents/skills/tts/scripts/tts.sh"

if [ -z "$TEXT" ]; then
    echo "Usage: feishu-voice \"message text\" [target_user_id] [voice_id]"
    echo ""
    echo "Default voices:"
    echo "  Female (default): d44f2ab4 - 游戏少女（小雨）"
    echo "  Male:             96270d87 - 故事讲述者（子轩）"
    echo ""
    echo "More voices: curl https://noiz.ai/v1/voices"
    exit 1
fi

# Generate unique filename
TIMESTAMP=$(date +%s)
WAV_FILE="$WORKSPACE/voice_${TIMESTAMP}.wav"
OPUS_FILE="$WORKSPACE/voice_${TIMESTAMP}.opus"

echo "🎤 Generating TTS with Noiz Cloud API (voice_id: $VOICE_ID)"
bash "$NOIZ_SCRIPT" speak --voice-id "$VOICE_ID" -t "$TEXT" -o "$WAV_FILE" 2>&1 | tail -1

echo "🔄 Converting to Opus format..."
ffmpeg -i "$WAV_FILE" -c libopus "$OPUS_FILE" -y -loglevel error

echo "📨 Sending to Feishu..."
if [ -n "$TARGET" ]; then
    openclaw message send --channel feishu --target "$TARGET" --media "$OPUS_FILE"
else
    openclaw message send --channel feishu --media "$OPUS_FILE"
fi

# Cleanup intermediate file
rm -f "$WAV_FILE"

echo "✅ Voice message sent!"
echo "   File: $OPUS_FILE"
echo "   (Keep for reuse, or delete manually)"
