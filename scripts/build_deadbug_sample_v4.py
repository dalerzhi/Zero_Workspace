from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import subprocess, shutil, math, requests

BASE = Path('/Users/a123456/.openclaw/workspace/video-output/reference-clips')
OUT = Path('/Users/a123456/.openclaw/workspace/video-output/final-samples')
AUDIO = OUT / 'audio'
FRAMES = OUT / 'deadbug_frames_v4'
OUT.mkdir(parents=True, exist_ok=True)
AUDIO.mkdir(parents=True, exist_ok=True)
if FRAMES.exists():
    shutil.rmtree(FRAMES)
FRAMES.mkdir(parents=True)

FONT = '/System/Library/Fonts/Hiragino Sans GB.ttc'
TITLE = ImageFont.truetype(FONT, 34)
SUB = ImageFont.truetype(FONT, 22)
BODY = ImageFont.truetype(FONT, 26)
SMALL = ImageFont.truetype(FONT, 20)
BIG = ImageFont.truetype(FONT, 42)

prep_seconds = 8
reps = 10
sec_per_rep = 4
finish_seconds = 5
main_seconds = prep_seconds + reps * sec_per_rep + finish_seconds
fps = 10
W, H = 1280, 720

# 更自然：语速放缓、句子更短、留呼吸空间
script = (
    '我们来做死虫式，一组十次。先追求稳定，不追求速度。\n'
    '仰卧，腰背轻轻压住地面。双手指向天花板，双腿抬到九十度。\n'
    '准备倒计时。三，二，一，开始。\n'
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

key_path = Path.home() / '.noiz_api_key'
if not key_path.exists():
    raise RuntimeError('未找到 ~/.noiz_api_key，无法调用 Noiz TTS')
api_key = key_path.read_text().strip()
if not api_key:
    raise RuntimeError('~/.noiz_api_key 为空')

wav = AUDIO / 'deadbug_v4_voice.wav'
voice_resp = requests.post(
    'https://noiz.ai/v1/text-to-speech',
    headers={'Authorization': api_key},
    data={
        'text': script,
        'voice_id': '4f71a876',  # 平静舒缓，更像教练口播
        'output_format': 'wav',
        'speed': '0.95',
    },
    timeout=180,
)
voice_resp.raise_for_status()
wav.write_bytes(voice_resp.content)

voice_m4a = AUDIO / 'deadbug_v4_voice.m4a'
subprocess.run([
    'ffmpeg', '-y', '-i', str(wav), '-af', 'highpass=f=80,lowpass=f=7000,loudnorm=I=-17:LRA=7:TP=-1.5',
    '-c:a', 'aac', '-b:a', '192k', str(voice_m4a)
], check=True)

# 生成更像音乐的轻量 BGM（不抢人声）
bgm_raw = AUDIO / 'deadbug_v4_bgm_raw.wav'
subprocess.run([
    'ffmpeg', '-y',
    '-f', 'lavfi', '-i', f'sine=frequency=96:sample_rate=44100:duration={main_seconds+2}',
    '-f', 'lavfi', '-i', f'sine=frequency=144:sample_rate=44100:duration={main_seconds+2}',
    '-f', 'lavfi', '-i', f'sine=frequency=288:sample_rate=44100:duration={main_seconds+2}',
    '-filter_complex',
    '[0:a]volume=0.08,afade=t=in:st=0:d=1.2,afade=t=out:st={}:d=1.2[b1];'
    '[1:a]volume=0.05,tremolo=f=2.2:d=0.65,afade=t=in:st=0:d=1.2,afade=t=out:st={}:d=1.2[b2];'
    '[2:a]volume=0.03,vibrato=f=3.5:d=0.18,afade=t=in:st=0:d=1.2,afade=t=out:st={}:d=1.2[b3];'
    '[b1][b2][b3]amix=inputs=3:normalize=0,highpass=f=90,lowpass=f=2500,loudnorm=I=-32:LRA=8:TP=-2[a]'.format(
        main_seconds, main_seconds, main_seconds
    ),
    '-map', '[a]', '-c:a', 'pcm_s16le', str(bgm_raw)
], check=True)


def draw_top_bar(draw):
    draw.rounded_rectangle((18, 16, 1262, 64), radius=16, fill=(18, 33, 63, 208))
    draw.text((34, 24), '死虫式  ·  1组10次（教练跟练版）', font=TITLE, fill='white')
    draw.text((930, 26), '慢 + 稳 + 控制  >  快', font=SUB, fill=(220, 232, 255))


def draw_bottom_bar(draw, left_text, center_text, right_text):
    y1, y2 = 632, 706
    draw.rounded_rectangle((18, y1, 1262, y2), radius=16, fill=(255, 255, 255, 220))
    draw.text((36, 655), left_text, font=SUB, fill=(36, 55, 92))
    tw = draw.textlength(center_text, font=SMALL)
    draw.text(((W - tw) / 2, 660), center_text, font=SMALL, fill=(92, 108, 136))
    rw = draw.textlength(right_text, font=BIG)
    draw.text((1220 - rw, 645), right_text, font=BIG, fill=(62, 111, 235))


def draw_center_cue(draw, text, sub_text):
    x1, y1, x2, y2 = 290, 510, 990, 610
    draw.rounded_rectangle((x1, y1, x2, y2), radius=18, fill=(22, 30, 50, 172))
    tw = draw.textlength(text, font=BODY)
    draw.text(((W - tw) / 2, 532), text, font=BODY, fill=(245, 248, 255))
    sw = draw.textlength(sub_text, font=SMALL)
    draw.text(((W - sw) / 2, 570), sub_text, font=SMALL, fill=(210, 224, 255))


def make_overlay(i):
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    draw_top_bar(d)

    if i < prep_seconds * fps:
        remain = prep_seconds - i / fps
        sec = max(1, math.ceil(remain))
        draw_bottom_bar(d, '准备阶段', '双手向上，双腿90°，腰背贴地', str(sec))
        draw_center_cue(d, '准备就绪', '腹部收紧，呼吸平稳')
    elif i < (prep_seconds + reps * sec_per_rep) * fps:
        t = (i - prep_seconds * fps) / fps
        rep_idx = min(reps, int(t / sec_per_rep) + 1)
        phase = t % sec_per_rep
        remain_total = max(0, reps * sec_per_rep - t)

        stretch = phase < 2.1
        if stretch:
            cue = '右手后 / 左腿前' if rep_idx % 2 == 1 else '左手后 / 右腿前'
            center_title = f'第 {rep_idx} 次：伸展'
            center_sub = '呼气伸展，动作慢一点'
        else:
            cue = '回中间，稳住核心'
            center_title = f'第 {rep_idx} 次：回收'
            center_sub = '吸气回收，腰背不离地'

        left = f'进度  {rep_idx} / {reps}'
        right = str(max(0, math.ceil(remain_total)))
        draw_bottom_bar(d, left, cue, right)
        draw_center_cue(d, center_title, center_sub)

        d.rounded_rectangle((30, 618, 1250, 626), radius=4, fill=(207, 216, 232, 180))
        pw = int(1220 * (t / (reps * sec_per_rep)))
        d.rounded_rectangle((30, 618, 30 + max(8, pw), 626), radius=4, fill=(80, 132, 255, 220))
    else:
        draw_bottom_bar(d, '完成 10 / 10 次', '收尾放松，保持呼吸', '✔')
        draw_center_cue(d, '这组完成', '核心已经激活，做得很好')

    return img


for i in range(main_seconds * fps):
    make_overlay(i).save(FRAMES / f'{i:05d}.png')

video = BASE / 'deadbug.mp4'
out = OUT / 'deadbug_final_sample_v4.mp4'

subprocess.run([
    'ffmpeg', '-y',
    '-stream_loop', '-1', '-i', str(video),
    '-i', str(voice_m4a),
    '-i', str(bgm_raw),
    '-framerate', str(fps), '-i', str(FRAMES / '%05d.png'),
    '-filter_complex',
    '[0:v]scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2:black[bg];'
    '[bg][3:v]overlay=0:0[v];'
    '[1:a]apad=pad_dur=80,volume=1.0[voice];'
    '[2:a]volume=0.22[bgm];'
    '[bgm][voice]sidechaincompress=threshold=0.045:ratio=12:attack=12:release=320[duck];'
    '[duck][voice]amix=inputs=2:weights=0.48 1.0:normalize=0,alimiter=limit=0.96[a]',
    '-map', '[v]', '-map', '[a]',
    '-t', str(main_seconds),
    '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
    '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart',
    str(out)
], check=True)

print(out)
