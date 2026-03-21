from pathlib import Path
import subprocess
import requests

BASE = Path('/Users/a123456/.openclaw/workspace/video-output/reference-clips')
OUT = Path('/Users/a123456/.openclaw/workspace/video-output/final-samples')
AUDIO = OUT / 'audio'
OUT.mkdir(parents=True, exist_ok=True)
AUDIO.mkdir(parents=True, exist_ok=True)

video_src = BASE / 'deadbug.mp4'
video_clean = OUT / 'deadbug_clean_loop_source_v5.mp4'
out = OUT / 'deadbug_final_sample_v5.mp4'

# 1) 裁干净动作段（去掉黑屏白字段），并强制去掉源音轨
subprocess.run([
    'ffmpeg', '-y',
    '-ss', '8.0', '-t', '26.0', '-i', str(video_src),
    '-an',
    '-c:v', 'libx264', '-preset', 'medium', '-crf', '18',
    '-pix_fmt', 'yuv420p', str(video_clean)
], check=True)

# 2) 重新生成中文口播
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
voice_wav = AUDIO / 'deadbug_v5_voice.wav'
voice_m4a = AUDIO / 'deadbug_v5_voice.m4a'
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

# 3) 生成可感知但不抢口播的 BGM
main_seconds = 53
bgm_wav = AUDIO / 'deadbug_v5_bgm.wav'
subprocess.run([
    'ffmpeg', '-y',
    '-f', 'lavfi', '-i', f'sine=frequency=92:sample_rate=44100:duration={main_seconds+2}',
    '-f', 'lavfi', '-i', f'sine=frequency=138:sample_rate=44100:duration={main_seconds+2}',
    '-f', 'lavfi', '-i', f'sine=frequency=276:sample_rate=44100:duration={main_seconds+2}',
    '-filter_complex',
    '[0:a]volume=0.14,afade=t=in:st=0:d=1.2,afade=t=out:st=52:d=1.2[a1];'
    '[1:a]volume=0.10,tremolo=f=2.1:d=0.7,afade=t=in:st=0:d=1.2,afade=t=out:st=52:d=1.2[a2];'
    '[2:a]volume=0.06,vibrato=f=3.5:d=0.2,afade=t=in:st=0:d=1.2,afade=t=out:st=52:d=1.2[a3];'
    '[a1][a2][a3]amix=inputs=3:normalize=0,highpass=f=90,lowpass=f=2600,loudnorm=I=-27:LRA=9:TP=-2[a]',
    '-map', '[a]', '-c:a', 'pcm_s16le', str(bgm_wav)
], check=True)

# 4) 合成：循环干净动作画面 + 中文口播 + ducking BGM
subprocess.run([
    'ffmpeg', '-y',
    '-stream_loop', '-1', '-i', str(video_clean),
    '-i', str(voice_m4a),
    '-i', str(bgm_wav),
    '-filter_complex',
    '[0:v]scale=1280:720:force_original_aspect_ratio=decrease,'
    'pad=1280:720:(ow-iw)/2:(oh-ih)/2:black[v];'
    '[1:a]apad=pad_dur=80,volume=1.0,asplit=2[voice_sc][voice_mix];'
    '[2:a]volume=0.60[bgm];'
    '[bgm][voice_sc]sidechaincompress=threshold=0.035:ratio=10:attack=10:release=260[ducked];'
    '[ducked][voice_mix]amix=inputs=2:weights=0.85 1.0:normalize=0,alimiter=limit=0.95[a]',
    '-map', '[v]', '-map', '[a]',
    '-t', str(main_seconds),
    '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
    '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart',
    str(out)
], check=True)

print(out)
