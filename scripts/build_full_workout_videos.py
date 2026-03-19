from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import subprocess, math, shutil

BASE = Path('/Users/a123456/.openclaw/workspace/video-output/full-workout-assets')
OUT = Path('/Users/a123456/.openclaw/workspace/video-output/full-workout-videos')
OUT.mkdir(parents=True, exist_ok=True)
FONT = '/System/Library/Fonts/Hiragino Sans GB.ttc'
TITLE = ImageFont.truetype(FONT, 46)
SUB = ImageFont.truetype(FONT, 30)
BODY = ImageFont.truetype(FONT, 26)
BIG = ImageFont.truetype(FONT, 70)

ACTIONS = [
    dict(stem='greatstretch', title='伟大拉伸', subtitle='每侧 3 次', mode='reps', reps=6, seconds_per_rep=6, tips=['前脚踩稳，后腿伸展','先沉髋，再转胸口向上']),
    dict(stem='inchworm', title='毛毛虫爬', subtitle='3 次', mode='reps', reps=3, seconds_per_rep=10, tips=['手一步步向前爬','核心收紧，不要塌腰']),
    dict(stem='deadbug', title='死虫式', subtitle='3 组 × 10 次（左右交替）', mode='reps', reps=10, seconds_per_rep=4, tips=['腰背贴地','动作慢，重控制']),
    dict(stem='sideplank', title='侧平板支撑', subtitle='每侧 30 秒 × 2 组', mode='hold', hold_seconds=30, tips=['屁股收紧','身体保持一条直线']),
    dict(stem='splitsquat', title='保加利亚分腿蹲', subtitle='每侧 8 次 × 3 组', mode='reps', reps=8, seconds_per_rep=4, tips=['下蹲 3 秒，起身 1 秒','膝盖方向对准脚尖']),
    dict(stem='jump', title='原地纵跳摸高', subtitle='连续 8 次 × 2 组', mode='reps', reps=8, seconds_per_rep=3, tips=['向上充分伸展','落地轻，膝盖缓冲']),
    dict(stem='balance', title='单腿站立抛接', subtitle='每腿 30 秒 × 2 组', mode='hold', hold_seconds=30, tips=['支撑腿微屈','身体不要乱晃']),
    dict(stem='calf', title='靠墙小腿拉伸', subtitle='每侧 30 秒 × 2 组', mode='hold', hold_seconds=30, tips=['后腿伸直','脚跟踩实地面']),
    dict(stem='chest', title='靠墙胸部拉伸', subtitle='30 秒 × 2 组', mode='hold', hold_seconds=30, tips=['手臂扶墙','身体轻轻前倾'])
]

W,H = 768,1024
FPS = 10

def fit(im):
    bg = Image.new('RGB', (W,H), (244,247,251))
    im = im.convert('RGB')
    im.thumbnail((W-40, H-260))
    x=(W-im.width)//2
    y=96+(H-280-im.height)//2
    bg.paste(im,(x,y))
    return bg

def make_frame(base_img, title, subtitle, bottom_main, bottom_sub, progress=None):
    fr = base_img.copy()
    d = ImageDraw.Draw(fr)
    d.rounded_rectangle((20,16,W-20,78), radius=24, fill=(25,41,76))
    d.text((W//2,47), title, font=TITLE, fill='white', anchor='mm')
    d.rounded_rectangle((150,86,618,128), radius=18, fill=(255,255,255))
    d.text((W//2,107), subtitle, font=SUB, fill=(80,98,138), anchor='mm')
    d.rounded_rectangle((30,H-180,W-30,H-28), radius=28, fill=(255,255,255))
    d.text((W//2,H-138), bottom_main, font=BIG, fill=(33,53,95), anchor='mm')
    d.text((W//2,H-76), bottom_sub, font=BODY, fill=(93,108,132), anchor='mm')
    if progress is not None:
        d.rounded_rectangle((70,H-212,W-70,H-196), radius=8, fill=(224,230,240))
        d.rounded_rectangle((70,H-212,70+int((W-140)*progress),H-196), radius=8, fill=(77,121,255))
    return fr

def load_triplet(stem):
    return [fit(Image.open(BASE / f'{stem}_{i}.png')) for i in [1,2,3]]

def interp(imgs, t):
    # t in [0,1]
    if t <= 0.5:
        local = t/0.5
        return Image.blend(imgs[0], imgs[1], local)
    local = (t-0.5)/0.5
    return Image.blend(imgs[1], imgs[2], local)

for cfg in ACTIONS:
    imgs = load_triplet(cfg['stem'])
    frames_dir = OUT / f"{cfg['stem']}_frames"
    if frames_dir.exists():
        shutil.rmtree(frames_dir)
    frames_dir.mkdir(parents=True)
    frame_idx = 0
    if cfg['mode']=='reps':
        reps = cfg['reps']
        spr = cfg['seconds_per_rep']
        total = reps * spr
        for rep in range(1, reps+1):
            for f in range(spr*FPS):
                t = f/max(1,spr*FPS-1)
                cyc = interp(imgs, t if t<=0.5 else 1-t) if cfg['stem'] in ['greatstretch','inchworm'] else interp(imgs, t)
                # for cyclical reps return to start on next rep by bouncing
                if cfg['stem'] not in ['greatstretch','inchworm']:
                    phase = t*2 if t < 0.5 else (1-(t-0.5)*2)
                    cyc = interp(imgs, max(0,min(1,phase)))
                remain = total - ((rep-1)*spr + f/FPS)
                fr = make_frame(cyc, cfg['title'], cfg['subtitle'], f'第 {rep} / {reps} 次', f'剩余 {math.ceil(remain)} 秒', progress=((rep-1)*spr + f/FPS)/total)
                fr.save(frames_dir / f'{frame_idx:05d}.png')
                frame_idx += 1
    else:
        hold = cfg['hold_seconds']
        total = hold
        # settle into best pose then hold with gentle drift between mid/end
        for f in range(hold*FPS):
            sec_elapsed = f/FPS
            drift = (math.sin(sec_elapsed*0.8)+1)/2
            cyc = Image.blend(imgs[1], imgs[2], drift*0.35)
            remain = total - sec_elapsed
            fr = make_frame(cyc, cfg['title'], cfg['subtitle'], f'保持 {math.ceil(remain)} 秒', '匀速呼吸，保持动作标准', progress=sec_elapsed/total)
            fr.save(frames_dir / f'{frame_idx:05d}.png')
            frame_idx += 1
    outmp4 = OUT / f"{cfg['stem']}.mp4"
    subprocess.run(['ffmpeg','-y','-framerate',str(FPS),'-i',str(frames_dir/'%05d.png'),'-vf','format=yuv420p','-c:v','libx264','-movflags','+faststart',str(outmp4)], check=True)
    print(outmp4)
