from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import subprocess, shutil, math

BASE = Path('/Users/a123456/.openclaw/workspace/video-output/reference-clips')
OUT = Path('/Users/a123456/.openclaw/workspace/video-output/final-samples')
AUDIO = OUT / 'audio'
FRAMES = OUT / 'deadbug_frames_v2'
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

# 1组10次，左右交替，完整跟练
prep_seconds = 5
reps = 10
sec_per_rep = 4
main_seconds = prep_seconds + reps * sec_per_rep
fps = 10
W, H = 1280, 720

script = (
    '准备开始死虫式，一组十次，左右交替。先仰卧，腰背贴住地面，双手向上，双腿抬起。'
    '听到提示后开始。第一步，右手向头后伸，左腿同时向前伸直。回到中间。'
    '第二步，换另一侧。整个过程肚子收紧，腰不要离地。动作宁可慢，也要稳定。'
    '现在跟着节奏完成这一组。'
)
aiff = AUDIO / 'deadbug_v2.aiff'
m4a = AUDIO / 'deadbug_v2.m4a'
subprocess.run(['say', '-v', 'Tingting', '-r', '165', '-o', str(aiff), script], check=True)
subprocess.run(['ffmpeg', '-y', '-i', str(aiff), '-c:a', 'aac', '-b:a', '128k', str(m4a)], check=True)


def draw_top_bar(draw):
    draw.rounded_rectangle((18, 16, 1262, 64), radius=16, fill=(18, 33, 63, 205))
    draw.text((34, 24), '死虫式  ·  1组10次', font=TITLE, fill='white')
    draw.text((1060, 26), '腰背贴地', font=SUB, fill=(220, 232, 255))


def draw_bottom_bar(draw, left_text, center_text, right_text):
    # thin info bar to avoid blocking
    y1, y2 = 642, 706
    draw.rounded_rectangle((18, y1, 1262, y2), radius=16, fill=(255, 255, 255, 215))
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
        left = '准备姿势：双手向上，双腿90度'
        center = '准备开始，听到提示后动作开始'
        right = str(max(1, math.ceil(remain)))
        draw_bottom_bar(d, left, center, right)
    else:
        t = (i - prep_seconds * fps) / fps
        rep_idx = min(reps, int(t / sec_per_rep) + 1)
        phase = t % sec_per_rep
        remain_total = max(0, reps * sec_per_rep - t)
        if phase < 2:
            cue = '右手后伸 / 左腿前伸' if rep_idx % 2 == 1 else '左手后伸 / 右腿前伸'
        else:
            cue = '回到中间，准备换边'
        left = f'第 {rep_idx} / {reps} 次'
        center = cue
        right = str(max(0, math.ceil(remain_total)))
        draw_bottom_bar(d, left, center, right)
        # tiny progress bar above bottom bar
        d.rounded_rectangle((30, 628, 1250, 636), radius=4, fill=(207, 216, 232, 180))
        pw = int(1220 * (t / (reps * sec_per_rep)))
        d.rounded_rectangle((30, 628, 30 + max(8, pw), 636), radius=4, fill=(80, 132, 255, 220))
    return img

for i in range(main_seconds * fps):
    make_overlay(i).save(FRAMES / f'{i:05d}.png')

video = BASE / 'deadbug.mp4'
out = OUT / 'deadbug_final_sample_v2.mp4'
subprocess.run([
    'ffmpeg', '-y', '-stream_loop', '-1', '-ss', '0', '-t', str(main_seconds), '-i', str(video), '-i', str(m4a), '-framerate', str(fps), '-i', str(FRAMES / '%05d.png'),
    '-filter_complex', '[0:v]scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2:black[bg];[bg][2:v]overlay=0:0[v]',
    '-map', '[v]', '-map', '1:a:0', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-shortest', '-movflags', '+faststart', str(out)
], check=True)
print(out)
