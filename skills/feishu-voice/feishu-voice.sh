#!/bin/bash
# feishu-voice: Send native voice messages on Feishu
# Usage: feishu-voice "message text" [target_user_id] [voice_name]

set -e

TEXT="$1"
TARGET="${2:-}"
VOICE="${3:-Ting-Ting}"
WORKSPACE="/Users/a123456/.openclaw/workspace"

if [ -z "$TEXT" ]; then
    echo "Usage: feishu-voice \"message text\" [target_user_id] [voice_name]"
    echo "  message_text: The text to convert to speech"
    echo "  target_user_id: Feishu user ID (optional, uses default channel if omitted)"
    echo "  voice_name: macOS voice name (default: Ting-Ting)"
    echo ""
    echo "Available voices: say -v '?'"
    exit 1
fi

# Generate unique filename
TIMESTAMP=$(date +%s)
M4A_FILE="$WORKSPACE/voice_${TIMESTAMP}.m4a"
OPUS_FILE="$WORKSPACE/voice_${TIMESTAMP}.opus"

echo "🎤 Generating TTS with voice: $VOICE"
say -v "$VOICE" "$TEXT" -o "$M4A_FILE"

echo "🔄 Converting to Opus format..."
ffmpeg -i "$M4A_FILE" -c libopus "$OPUS_FILE" -y -loglevel error

echo "📨 Sending to Feishu..."
if [ -n "$TARGET" ]; then
    openclaw message send --channel feishu --target "$TARGET" --media "$OPUS_FILE"
else
    openclaw message send --channel feishu --media "$OPUS_FILE"
fi

# Cleanup intermediate file
rm -f "$M4A_FILE"

echo "✅ Voice message sent!"
echo "   File: $OPUS_FILE"
echo "   (Keep for reuse, or delete manually)"
