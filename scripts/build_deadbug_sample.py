from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import subprocess, shutil, math

BASE = Path('/Users/a123456/.openclaw/workspace/video-output/reference-clips')
OUT = Path('/Users/a123456/.openclaw/workspace/video-output/final-samples')
AUDIO = OUT / 'audio'
FRAMES = OUT / 'deadbug_frames'
OUT.mkdir(parents=True, exist_ok=True)
AUDIO.mkdir(parents=True, exist_ok=True)
if FRAMES.exists():
    shutil.rmtree(FRAMES)
FRAMES.mkdir(parents=True)
FONT = '/System/Library/Fonts/Hiragino Sans GB.ttc'
TITLE = ImageFont.truetype(FONT, 44)
SUB = ImageFont.truetype(FONT, 28)
BODY = ImageFont.truetype(FONT, 26)
SMALL = ImageFont.truetype(FONT, 22)
BIG = ImageFont.truetype(FONT, 58)

script = '死虫式。现在做一组十次，左右交替。先仰卧，腰背贴住地面。双手向上，双腿抬起，膝盖大约九十度。开始时，右手慢慢向头后伸，左腿同时向前伸直。注意肚子收紧，腰不要拱起来。回到中间，再换另一侧。动作慢一点，越稳越好。'
aiff = AUDIO / 'deadbug.aiff'
m4a = AUDIO / 'deadbug.m4a'
subprocess.run(['say','-v','Tingting','-r','170','-o',str(aiff),script], check=True)
subprocess.run(['ffmpeg','-y','-i',str(aiff),'-c:a','aac','-b:a','128k',str(m4a)], check=True)

def wrap(draw, text, font, width):
    lines=[]
    cur=''
    for ch in text:
        t=cur+ch
        if draw.textlength(t,font=font)<=width:
            cur=t
        else:
            if cur:
                lines.append(cur)
            cur=ch
    if cur:
        lines.append(cur)
    return lines

# Make info overlay images per frame
W,H = 1280,720
fps=10
reps=10
sec_per_rep=4
prep=6
main_dur=prep+reps*sec_per_rep
for i in range(main_dur*fps):
    img = Image.new('RGBA',(W,H),(0,0,0,0))
    d = ImageDraw.Draw(img)
    # top title bar
    d.rounded_rectangle((20,18,1260,100), radius=22, fill=(19,35,68,220))
    d.text((50,34),'死虫式',font=TITLE,fill='white')
    d.text((180,42),'3组 × 10次（样板先演示1组）',font=SUB,fill=(220,232,255))
    # bottom panel
    d.rounded_rectangle((20,510,1260,700), radius=24, fill=(255,255,255,225))
    if i < prep*fps:
        title='准备动作'
        bullet1='1. 仰卧，腰背贴地'
        bullet2='2. 双手向上，双腿抬起'
        bullet3='3. 膝盖约90度，核心收紧'
        countdown = prep - i/fps
        d.text((50,530),title,font=SUB,fill=(28,45,79))
        y=575
        for b in [bullet1,bullet2,bullet3]:
            d.text((60,y),b,font=BODY,fill=(60,76,105))
            y += 38
        d.text((1110,558),f'{math.ceil(countdown)}',font=BIG,fill=(55,103,220),anchor='mm')
        d.text((1110,618),'准备',font=SUB,fill=(55,103,220),anchor='mm')
    else:
        t=(i-prep*fps)/fps
        rep_idx=min(reps, int(t/sec_per_rep)+1)
        remain_total=max(0, main_dur - i/fps)
        phase=t%sec_per_rep
        if phase < 2:
            cue='向外伸展（对侧手脚）'
        else:
            cue='回到中间，准备换边'
        d.text((50,530),f'第 {rep_idx} / {reps} 次',font=SUB,fill=(28,45,79))
        bullets=['要点：腰背始终贴地','错误：不要耸肩，不要拱腰',f'当前提示：{cue}']
        y=575
        for b in bullets:
            d.text((60,y),b,font=BODY,fill=(60,76,105))
            y += 38
        d.text((1110,558),f'{math.ceil(remain_total)}',font=BIG,fill=(55,103,220),anchor='mm')
        d.text((1110,618),'剩余秒数',font=SUB,fill=(55,103,220),anchor='mm')
        # progress bar
        d.rounded_rectangle((50,665,1010,684), radius=9, fill=(220,228,242))
        pw=int(960*((i-prep*fps)/(reps*sec_per_rep*fps)))
        d.rounded_rectangle((50,665,50+max(8,pw),684), radius=9, fill=(88,133,255))
    img.save(FRAMES / f'{i:05d}.png')

video = BASE / 'deadbug.mp4'
out = OUT / 'deadbug_final_sample.mp4'
subprocess.run([
    'ffmpeg','-y','-ss','0','-t',str(main_dur),'-i',str(video),'-i',str(m4a),'-framerate',str(fps),'-i',str(FRAMES/'%05d.png'),
    '-filter_complex',"[0:v]scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2:black[bg];[bg][2:v]overlay=0:0[v]",
    '-map','[v]','-map','1:a:0','-c:v','libx264','-pix_fmt','yuv420p','-c:a','aac','-shortest','-movflags','+faststart',str(out)
], check=True)
print(out)
