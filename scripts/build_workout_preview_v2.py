from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import subprocess, os

BASE = Path('/Users/a123456/.openclaw/workspace/video-output/kids-workout-gifs-v2')
OUT = BASE
FONT = '/System/Library/Fonts/Hiragino Sans GB.ttc'
TITLE = ImageFont.truetype(FONT, 34)
SUB = ImageFont.truetype(FONT, 22)

seqs = [
    ('deadbug', '死虫式', ['deadbug_1.png','deadbug_2.png','deadbug_3.png']),
    ('sideplank', '侧平板支撑', ['sideplank_1.png','sideplank_2.png','sideplank_3.png']),
    ('splitsquat', '保加利亚分腿蹲', ['splitsquat_1.png','splitsquat_2.png','splitsquat_3.png']),
    ('balance', '单腿平衡抛接', ['balance_1.png','balance_2.png','balance_3.png']),
]

frames_dir = OUT / 'preview_frames'
frames_dir.mkdir(parents=True, exist_ok=True)

def fit(im, size=(768,1024)):
    bg = Image.new('RGB', size, (243,246,250))
    im = im.convert('RGB')
    im.thumbnail((size[0]-50, size[1]-170))
    x = (size[0]-im.width)//2
    y = 90 + (size[1]-170-im.height)//2
    bg.paste(im, (x,y))
    return bg

idx = 0
all_frames = []
for stem, title, files in seqs:
    imgs = [fit(Image.open(BASE / f)) for f in files]
    # hold on each key pose + smooth blends
    expanded = []
    for j in range(len(imgs)-1):
        a, b = imgs[j], imgs[j+1]
        for _ in range(6):
            expanded.append(a.copy())
        for k in range(1,9):
            expanded.append(Image.blend(a,b,k/9))
    for _ in range(8):
        expanded.append(imgs[-1].copy())
    for frame in expanded + list(reversed(expanded[6:-6])):
        d = ImageDraw.Draw(frame)
        d.rounded_rectangle((24, 18, 744, 72), radius=22, fill=(25,41,76))
        d.text((384,45), title, font=TITLE, fill='white', anchor='mm')
        d.rounded_rectangle((250, 930, 518, 976), radius=18, fill=(255,255,255))
        d.text((384,954), '慢动作分解演示', font=SUB, fill=(75,96,136), anchor='mm')
        path = frames_dir / f'{idx:05d}.png'
        frame.save(path)
        all_frames.append(path)
        idx += 1

mp4 = OUT / 'kids_workout_preview_v2.mp4'
subprocess.run([
    'ffmpeg','-y','-framerate','10','-i', str(frames_dir / '%05d.png'),
    '-vf','format=yuv420p','-c:v','libx264','-movflags','+faststart', str(mp4)
], check=True)
print(mp4)
