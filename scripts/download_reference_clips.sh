#!/bin/zsh
set -euo pipefail
cd /Users/a123456/.openclaw/workspace
OUT=video-output/reference-clips
mkdir -p "$OUT"
urls=(
  "greatstretch|https://www.bilibili.com/video/BV1Z64y1k7zx/"
  "inchworm|https://www.bilibili.com/video/BV1Qq4y1w7b2/"
  "deadbug|https://www.bilibili.com/video/BV1js411E73s/"
  "sideplank|https://www.bilibili.com/video/BV1YT421y7Hm/"
  "splitsquat|https://www.bilibili.com/video/BV12Hpez1EVv/"
  "jump|https://www.bilibili.com/video/BV17X4y1A7M4/"
  "balance|https://www.bilibili.com/video/BV1p8w8eQEEs/"
  "calf|https://www.bilibili.com/video/BV1a44y1Z7Qz/"
  "chest|https://www.bilibili.com/video/BV1zQ4y1S7B3/"
)
for item in "${urls[@]}"; do
  name="${item%%|*}"
  url="${item#*|}"
  yt-dlp -f "bv*+ba/b" --merge-output-format mp4 -o "$OUT/${name}.%(ext)s" "$url"
done
