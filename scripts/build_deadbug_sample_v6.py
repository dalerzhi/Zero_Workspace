from pathlib import Path
import subprocess
import requests
from PIL import Image, ImageDraw, ImageFont

BASE = Path('/Users/a123456/.openclaw/workspace/video-output/reference-clips')
OUT = Path('/Users/a123456/.openclaw/workspace/video-output/final-samples')
AUDIO = OUT / 'audio'
OVERLAY = OUT / 'overlay_v6'
OUT.mkdir(parents=True, exist_ok=True)
AUDIO.mkdir(parents=True, exist_ok=True)
OVERLAY.mkdir(parents=True, exist_ok=True)

video_src = BASE / 'deadbug.mp4'
video_clean = OUT / 'deadbug_clean_loop_source_v6.mp4'
out = OUT / 'deadbug_final_sample_v6.mp4'

# 1) 裁切干净动作段（仅保留动作，去掉黑屏/白字污染），并静音源音轨
subprocess.run([
    'ffmpeg', '-y',
    '-ss', '8.0', '-t', '26.0', '-i', str(video_src),
    '-an',
    '-c:v', 'libx264', '-preset', 'medium', '-crf', '18',
    '-pix_fmt', 'yuv420p', str(video_clean)
], check=True)

# 2) 生成中文 TTS 口播
script = (
    '我们来做死虫式，一组十次。先追求稳定，不追求速度。\n'
    '仰卧，腰背轻轻压住地面。双手向上，双腿抬到九十度。\n'
    '准备，三，二，一，开始。\n'
    '一，右手向后，左腿向前。\n'
    '二，换边。\n'
    '三，保持呼吸。\n'
    '四，慢慢伸，慢慢收。\n'
    '五，核心收紧，腰不要离地。\n'
    '六，动作干净，节奏稳定。\n'
    '七，继续，坚持住。\n'
    '八，保持控制。\n'
    '九，最后两次。\n'
    '十，回到中间。\n'
    '很好，这组完成。'
)

api_key = (Path.home() / '.noiz_api_key').read_text().strip()
voice_wav = AUDIO / 'deadbug_v6_voice.wav'
voice_m4a = AUDIO / 'deadbug_v6_voice.m4a'
resp = requests.post(
    'https://noiz.ai/v1/text-to-speech',
    headers={'Authorization': api_key},
    data={
        'text': script,
        'voice_id': '4f71a876',
        'output_format': 'wav',
        'speed': '0.95',
    },
    timeout=180,
)
resp.raise_for_status()
voice_wav.write_bytes(resp.content)
subprocess.run([
    'ffmpeg', '-y', '-i', str(voice_wav),
    '-af', 'highpass=f=80,lowpass=f=7000,loudnorm=I=-17:LRA=7:TP=-1.5',
    '-c:a', 'aac', '-b:a', '192k', str(voice_m4a)
], check=True)

# 3) 生成可感知 BGM（明显存在，但通过 ducking 不压人声）
main_seconds = 53
bgm_wav = AUDIO / 'deadbug_v6_bgm.wav'
subprocess.run([
    'ffmpeg', '-y',
    '-f', 'lavfi', '-i', f'sine=frequency=92:sample_rate=44100:duration={main_seconds+2}',
    '-f', 'lavfi', '-i', f'sine=frequency=138:sample_rate=44100:duration={main_seconds+2}',
    '-f', 'lavfi', '-i', f'sine=frequency=276:sample_rate=44100:duration={main_seconds+2}',
    '-filter_complex',
    '[0:a]volume=0.18,afade=t=in:st=0:d=1.2,afade=t=out:st=52:d=1.2[a1];'
    '[1:a]volume=0.12,tremolo=f=2.1:d=0.7,afade=t=in:st=0:d=1.2,afade=t=out:st=52:d=1.2[a2];'
    '[2:a]volume=0.08,vibrato=f=3.5:d=0.2,afade=t=in:st=0:d=1.2,afade=t=out:st=52:d=1.2[a3];'
    '[a1][a2][a3]amix=inputs=3:normalize=0,highpass=f=90,lowpass=f=2600,loudnorm=I=-25:LRA=8:TP=-2[a]',
    '-map', '[a]', '-c:a', 'pcm_s16le', str(bgm_wav)
], check=True)

# 4) 生成字幕/cue overlay 素材图（透明 PNG）
font_path = '/System/Library/Fonts/STHeiti Medium.ttc'

def make_overlay(path: Path, text: str, y_top: int, bar_h: int, font_size: int, alpha: int):
    im = Image.new('RGBA', (1280, 720), (0, 0, 0, 0))
    draw = ImageDraw.Draw(im)
    draw.rectangle((0, y_top, 1280, y_top + bar_h), fill=(0, 0, 0, alpha))
    font = ImageFont.truetype(font_path, font_size)
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    x = (1280 - tw) // 2
    y = y_top + (bar_h - th) // 2 - 2
    draw.text((x, y), text, font=font, fill=(255, 255, 255, 255))
    im.save(path)

ov_ready = OVERLAY / 'top_ready.png'
ov_action = OVERLAY / 'top_action.png'
ov_end = OVERLAY / 'top_end.png'
ov_bottom = OVERLAY / 'bottom_cue.png'
make_overlay(ov_ready, '准备阶段', 0, 88, 46, 150)
make_overlay(ov_action, '动作阶段 · 10次交替', 0, 88, 46, 150)
make_overlay(ov_end, '收尾阶段', 0, 88, 46, 150)
make_overlay(ov_bottom, '腰背贴地 · 核心收紧 · 慢慢伸慢慢收', 592, 128, 38, 120)

# 5) 合成：循环动作 + cue overlay + 中文口播 + ducking BGM
subprocess.run([
    'ffmpeg', '-y',
    '-stream_loop', '-1', '-i', str(video_clean),
    '-loop', '1', '-i', str(ov_ready),
    '-loop', '1', '-i', str(ov_action),
    '-loop', '1', '-i', str(ov_end),
    '-loop', '1', '-i', str(ov_bottom),
    '-i', str(voice_m4a),
    '-i', str(bgm_wav),
    '-filter_complex',
    '[0:v]scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2:black[v0];'
    '[v0][1:v]overlay=0:0:enable=between(t\\,0\\,8)[v1];'
    '[v1][2:v]overlay=0:0:enable=between(t\\,8\\,47)[v2];'
    '[v2][3:v]overlay=0:0:enable=between(t\\,47\\,53)[v3];'
    '[v3][4:v]overlay=0:0:enable=between(t\\,0\\,53)[v];'
    '[5:a]apad=pad_dur=80,volume=1.0,asplit=2[voice_sc][voice_mix];'
    '[6:a]volume=0.75[bgm];'
    '[bgm][voice_sc]sidechaincompress=threshold=0.030:ratio=9:attack=10:release=260[ducked];'
    '[ducked][voice_mix]amix=inputs=2:weights=0.90 1.0:normalize=0,alimiter=limit=0.95[a]',
    '-map', '[v]', '-map', '[a]',
    '-t', str(main_seconds),
    '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
    '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart',
    str(out)
], check=True)

print(out)
