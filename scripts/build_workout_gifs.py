from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

BASE = Path('/Users/a123456/.openclaw/workspace/video-output/kids-workout-gifs')
FONT = '/System/Library/Fonts/Hiragino Sans GB.ttc'

pairs = [
    ('deadbug', '死虫式'),
    ('sideplank', '侧平板支撑'),
    ('splitsquat', '保加利亚分腿蹲'),
    ('balance', '单腿平衡抛接'),
]

def fit(im, size=(720, 960)):
    bg = Image.new('RGB', size, (246,248,252))
    im = im.convert('RGB')
    im.thumbnail((size[0]-40, size[1]-140))
    x = (size[0]-im.width)//2
    y = 90 + (size[1]-140-im.height)//2
    bg.paste(im, (x,y))
    return bg

for stem, title in pairs:
    a = fit(Image.open(BASE / f'{stem}_start.png'))
    b = fit(Image.open(BASE / f'{stem}_end.png'))
    frames = []
    font = ImageFont.truetype(FONT, 34)
    sub = ImageFont.truetype(FONT, 24)
    for seq in [list(range(0,11)), list(range(10,-1,-1))]:
        for i in seq:
            alpha = i/10
            frame = Image.blend(a, b, alpha)
            d = ImageDraw.Draw(frame)
            d.rounded_rectangle((24, 18, 696, 72), radius=22, fill=(24,40,74))
            d.text((360, 46), title, font=font, fill='white', anchor='mm')
            d.text((360, 915), '示意动图 · 动作标准请以教练指导为准', font=sub, fill=(90,104,128), anchor='mm')
            frames.append(frame)
    out = BASE / f'{stem}.gif'
    frames[0].save(out, save_all=True, append_images=frames[1:], duration=80, loop=0, disposal=2)
    print(out)

# combined preview gif
preview_frames = []
font = ImageFont.truetype(FONT, 28)
for stem, title in pairs:
    gif = Image.open(BASE / f'{stem}.gif')
    for idx in range(gif.n_frames):
        gif.seek(idx)
        fr = gif.convert('RGB')
        canvas = Image.new('RGB', (768, 1024), (242,245,250))
        canvas.paste(fr, (24,40))
        d = ImageDraw.Draw(canvas)
        d.text((384, 990), title, font=font, fill=(36,52,88), anchor='mm')
        preview_frames.append(canvas)
out = BASE / 'kids_workout_preview.gif'
preview_frames[0].save(out, save_all=True, append_images=preview_frames[1:], duration=80, loop=0, disposal=2)
print(out)
