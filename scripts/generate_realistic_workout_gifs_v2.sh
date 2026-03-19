#!/bin/zsh
set -euo pipefail
cd /Users/a123456/.openclaw/workspace
OUT=video-output/kids-workout-gifs-v2
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
STYLE='Create a realistic 3D sports coaching illustration for children, full body visible, same East Asian boy around 9 years old, slim build, short black hair, blue T-shirt, black shorts, white sneakers, bright fitness studio background, professional movement tutorial style, accurate anatomy, natural joint angles, realistic shading, no text, consistent character design across images.'
make_image() {
  local name="$1"
  local prompt="$2"
  uv run "$GEN" --prompt "$STYLE $prompt" --filename "$OUT/$name.png" --resolution 1K
}
make_image deadbug_1 'Child lying on back on a blue mat in dead bug start position: both hips and knees bent 90 degrees, both arms vertical above shoulders, neutral spine, viewed from slight front angle.'
make_image deadbug_2 'Same child on blue mat during dead bug midpoint: right arm moving backward halfway overhead and left leg extending halfway forward, other limbs still bent, core tight, viewed from slight front angle.'
make_image deadbug_3 'Same child on blue mat at full dead bug extension: right arm fully overhead and left leg extended forward low, lower back pressed down, viewed from slight front angle.'
make_image sideplank_1 'Child side plank setup on right forearm with knees bent and hips slightly lifted, preparing to fully extend, side view in a bright studio.'
make_image sideplank_2 'Same child in standard side plank on right forearm and lower leg support, body forming a straighter line, left hand on hip, side view.'
make_image sideplank_3 'Same child in full side plank on right forearm and feet stacked, hips fully lifted, left arm reaching straight up, side view.'
make_image splitsquat_1 'Child in Bulgarian split squat setup, rear foot on low soft bench, front foot planted, torso upright, starting at top position, 3/4 front view.'
make_image splitsquat_2 'Same child descending through the midpoint of Bulgarian split squat, front knee bending, rear knee moving down, torso upright and controlled, 3/4 front view.'
make_image splitsquat_3 'Same child at the bottom of Bulgarian split squat, front thigh lower, rear knee close to floor, controlled posture, 3/4 front view.'
make_image balance_1 'Child standing on right leg in a stable athletic stance, left knee slightly lifted, hands in front ready for ball catch, front view.'
make_image balance_2 'Same child balancing on right leg while reaching arms slightly left toward a small soft orange ball, support knee softly bent, trunk controlled, front view.'
make_image balance_3 'Same child balancing on right leg after catching the orange ball farther left, slight body lean but stable posture, front view.'
