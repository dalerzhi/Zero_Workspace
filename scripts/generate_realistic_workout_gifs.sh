#!/bin/zsh
set -euo pipefail
cd /Users/a123456/.openclaw/workspace
OUT=video-output/kids-workout-gifs
mkdir -p "$OUT"
export GEMINI_API_KEY=$(python3 - <<'PY'
from pathlib import Path
import re
text=(Path.home()/'.zshrc').read_text(errors='ignore')
m=re.search(r'export GEMINI_API_KEY="([^"]+)"', text)
print(m.group(1) if m else '')
PY
)
GEN='/Users/a123456/.openclaw/workspace/skills/nano-banana-pro/scripts/generate_image.py'
STYLE='Create a realistic 3D fitness coaching illustration for children, full body visible, same East Asian boy around 9 years old, slim build, black short hair, blue T-shirt, black shorts, white sneakers, clean bright studio background, professional sports education style, anatomically believable pose, no text, no extra equipment unless requested, consistent character design.'

make_image() {
  local name="$1"
  local prompt="$2"
  uv run $GEN --prompt "$STYLE $prompt" --filename "$OUT/$name.png" --resolution 1K
}

make_image deadbug_start 'The child is lying on his back on a blue exercise mat, tabletop position: hips and knees bent 90 degrees, both arms pointing straight up to the ceiling, neutral neck, core braced, viewed from a slight front angle.'
make_image deadbug_end 'The same child is lying on his back on a blue exercise mat performing dead bug: right arm extended backward overhead and left leg extended forward low, the other arm and leg remain bent, lower back pressed to the mat, viewed from a slight front angle.'

make_image sideplank_start 'The child is performing a side plank on the floor, supported on the right forearm and the outside of the right foot, body in one straight line, left hand on hip, viewed from the side, no mat needed.'
make_image sideplank_end 'The same child is performing a stronger side plank variation, supported on the right forearm and right foot, body straight, left arm reaching straight upward, hips lifted, viewed from the side.'

make_image splitsquat_start 'The child is setting up a Bulgarian split squat in a bright studio, rear foot placed on a low soft bench behind him, front foot planted, torso upright, hands at chest, viewed from a 3/4 front angle.'
make_image splitsquat_end 'The same child is at the bottom of a Bulgarian split squat, rear foot elevated on a low bench, front knee bent and aligned over foot, torso upright, controlled lowering position, viewed from a 3/4 front angle.'

make_image balance_start 'The child is standing on the right leg in a bright studio, left knee slightly lifted, both hands ready in front of chest to catch a small soft orange ball, athletic posture, viewed from the front.'
make_image balance_end 'The same child is balancing on the right leg while reaching slightly left to catch a small soft orange ball, support knee softly bent, trunk stable, viewed from the front.'
