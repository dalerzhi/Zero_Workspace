from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import subprocess, shutil, math, requests, os

BASE = Path('/Users/a123456/.openclaw/workspace/video-output/reference-clips')
OUT = Path('/Users/a123456/.openclaw/workspace/video-output/final-samples')
AUDIO = OUT / 'audio'
FRAMES = OUT / 'deadbug_frames_v3'
OUT.mkdir(parents=True, exist_ok=True)
AUDIO.mkdir(parents=True, exist_ok=True)
if FRAMES.exists():
    shutil.rmtree(FRAMES)
FRAMES.mkdir(parents=True)

FONT = '/System/Library/Fonts/Hiragino Sans GB.ttc'
TITLE = ImageFont.truetype(FONT, 34)
SUB = ImageFont.truetype(FONT, 22)
BODY = ImageFont.truetype(FONT, 20)
BIG = ImageFont.truetype(FONT, 38)

prep_seconds = 6
reps = 10
sec_per_rep = 4
finish_seconds = 4
main_seconds = prep_seconds + reps * sec_per_rep + finish_seconds
fps = 10
W, H = 1280, 720

# 更有激情的中文教练口播，确保完整带完10次并收尾
script = (
    '来，死虫式跟我练，一组十次，今天这组要稳、要狠、要控制！'
    '先准备，仰卧，腰背压紧地面，双手指向天花板，双腿抬到九十度。'
    '三、二、一，开始！'
    '第一下，右手向后，左腿向前，慢慢伸直，回中间。'
    '第二下，换边，左手向后，右腿向前，回中间。'
    '继续，第三下，第四下，节奏稳住。'
    '第五下，核心收紧，腰千万别离地。'
    '第六下，呼气伸展，吸气回收。'
    '第七下，控制住，不要抢速度。'
    '第八下，很棒，动作依然要干净。'
    '第九下，再坚持一下。'
    '最后一下，第十下，做完回中间！'
    '漂亮！十次完整结束，这组完成，核心已经点燃！'
)

# Noiz Cloud TTS（更接近真人）
key_path = Path.home() / '.noiz_api_key'
if not key_path.exists():
    raise RuntimeError('未找到 ~/.noiz_api_key，无法调用 Noiz TTS')
api_key = key_path.read_text().strip()
if not api_key:
    raise RuntimeError('~/.noiz_api_key 为空')

wav = AUDIO / 'deadbug_v3_voice.wav'
voice_resp = requests.post(
    'https://noiz.ai/v1/text-to-speech',
    headers={'Authorization': api_key},
    data={
        'text': script,
        'voice_id': 'e47a10c4',  # 活泼少女，感染力更强
        'output_format': 'wav',
        'speed': '1.03',
    },
    timeout=180,
)
voice_resp.raise_for_status()
wav.write_bytes(voice_resp.content)

voice_m4a = AUDIO / 'deadbug_v3_voice.m4a'
subprocess.run(['ffmpeg', '-y', '-i', str(wav), '-c:a', 'aac', '-b:a', '192k', str(voice_m4a)], check=True)

# 合成占位 BGM（免版权，程序生成），并做轻微律动
bgm_raw = AUDIO / 'deadbug_v3_bgm_raw.wav'
subprocess.run([
    'ffmpeg', '-y',
    '-f', 'lavfi', '-i', f'sine=frequency=110:sample_rate=44100:duration={main_seconds+2}',
    '-f', 'lavfi', '-i', f'sine=frequency=220:sample_rate=44100:duration={main_seconds+2}',
    '-filter_complex',
    '[0:a]volume=0.08,afade=t=in:st=0:d=1,afade=t=out:st={}:d=1[b1];'
    '[1:a]volume=0.05,tremolo=f=3:d=0.55,afade=t=in:st=0:d=1,afade=t=out:st={}:d=1[b2];'
    '[b1][b2]amix=inputs=2:normalize=0,highpass=f=70,lowpass=f=2800[a]'.format(main_seconds, main_seconds),
    '-map', '[a]', '-c:a', 'pcm_s16le', str(bgm_raw)
], check=True)


def draw_top_bar(draw):
    draw.rounded_rectangle((18, 16, 1262, 64), radius=16, fill=(18, 33, 63, 205))
    draw.text((34, 24), '死虫式  ·  1组10次（完整版）', font=TITLE, fill='white')
    draw.text((1010, 26), '核心收紧 · 腰背贴地', font=SUB, fill=(220, 232, 255))


def draw_bottom_bar(draw, left_text, center_text, right_text):
    y1, y2 = 642, 706
    draw.rounded_rectangle((18, y1, 1262, y2), radius=16, fill=(255, 255, 255, 218))
    draw.text((36, 660), left_text, font=SUB, fill=(36, 55, 92))
    tw = draw.textlength(center_text, font=BODY)
    draw.text(((W - tw) / 2, 664), center_text, font=BODY, fill=(92, 108, 136))
    rw = draw.textlength(right_text, font=BIG)
    draw.text((1220 - rw, 650), right_text, font=BIG, fill=(62, 111, 235))


def make_overlay(i):
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    draw_top_bar(d)

    if i < prep_seconds * fps:
        remain = prep_seconds - i / fps
        draw_bottom_bar(d, '准备姿势：双手向上，双腿90度', '倒计时后开始完整10次', str(max(1, math.ceil(remain))))
    elif i < (prep_seconds + reps * sec_per_rep) * fps:
        t = (i - prep_seconds * fps) / fps
        rep_idx = min(reps, int(t / sec_per_rep) + 1)
        phase = t % sec_per_rep
        remain_total = max(0, reps * sec_per_rep - t)

        if phase < 2:
            cue = '右手后伸 / 左腿前伸' if rep_idx % 2 == 1 else '左手后伸 / 右腿前伸'
        else:
            cue = '回到中间，稳住核心，准备换边'

        left = f'第 {rep_idx} / {reps} 次'
        right = str(max(0, math.ceil(remain_total)))
        draw_bottom_bar(d, left, cue, right)
        d.rounded_rectangle((30, 628, 1250, 636), radius=4, fill=(207, 216, 232, 180))
        pw = int(1220 * (t / (reps * sec_per_rep)))
        d.rounded_rectangle((30, 628, 30 + max(8, pw), 636), radius=4, fill=(80, 132, 255, 220))
    else:
        draw_bottom_bar(d, '完成 10 / 10 次', '太棒了！这一组完整结束', '✔')

    return img


for i in range(main_seconds * fps):
    make_overlay(i).save(FRAMES / f'{i:05d}.png')

video = BASE / 'deadbug.mp4'
out = OUT / 'deadbug_final_sample_v3.mp4'

# 语音+bgm 混音（语音优先 + ducking）
subprocess.run([
    'ffmpeg', '-y', '-stream_loop', '-1', '-i', str(video), '-i', str(voice_m4a), '-i', str(bgm_raw),
    '-framerate', str(fps), '-i', str(FRAMES / '%05d.png'),
    '-filter_complex',
    '[0:v]scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2:black[bg];'
    '[bg][3:v]overlay=0:0[v];'
    '[1:a]apad=pad_dur=70[voice];'
    '[2:a]volume=0.18[bgm];'
    '[bgm][voice]sidechaincompress=threshold=0.05:ratio=10:attack=8:release=250[duck];'
    '[duck][voice]amix=inputs=2:weights=0.55 1.0:normalize=0[a]'
    ,
    '-map', '[v]', '-map', '[a]',
    '-t', str(main_seconds),
    '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
    '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart',
    str(out)
], check=True)

print(out)
