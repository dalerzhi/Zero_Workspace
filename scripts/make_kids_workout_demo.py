from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import math, os, subprocess, textwrap

W, H = 1080, 1920
FPS = 24
OUTDIR = Path('/Users/a123456/.openclaw/workspace/video-output/kids-workout-demo')
FRAMES = OUTDIR / 'frames'
OUTDIR.mkdir(parents=True, exist_ok=True)
FRAMES.mkdir(parents=True, exist_ok=True)

FONT_PATH = '/System/Library/Fonts/Hiragino Sans GB.ttc'
TITLE = ImageFont.truetype(FONT_PATH, 72)
SUB = ImageFont.truetype(FONT_PATH, 42)
BODY = ImageFont.truetype(FONT_PATH, 34)
SMALL = ImageFont.truetype(FONT_PATH, 28)

BG = (245, 247, 250)
NAVY = (32, 45, 78)
BLUE = (67, 120, 255)
GREEN = (69, 176, 123)
ORANGE = (255, 154, 64)
RED = (220, 87, 87)
GRAY = (92, 105, 128)
LIGHT = (230, 235, 244)
WHITE = (255, 255, 255)

frame_idx = 0

def rounded_box(draw, xy, fill, radius=36, outline=None, width=3):
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)

def text(draw, xy, s, font, fill=NAVY, anchor='la', spacing=8, max_width=None):
    if max_width:
        final_lines = []
        for raw_line in str(s).split('\n'):
            if not raw_line:
                final_lines.append('')
                continue
            current = ''
            for ch in raw_line:
                trial = current + ch
                if draw.textlength(trial, font=font) <= max_width:
                    current = trial
                else:
                    if current:
                        final_lines.append(current)
                    current = ch
            if current:
                final_lines.append(current)
        s='\n'.join(final_lines)
    draw.multiline_text(xy, s, font=font, fill=fill, anchor=anchor, spacing=spacing)

def base_canvas():
    img = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(img)
    rounded_box(d, (50, 50, W-50, H-50), WHITE, radius=48)
    return img, d

def draw_header(d, title, subtitle=None, color=BLUE):
    rounded_box(d, (90, 95, W-90, 240), fill=color, radius=38)
    text(d, (120, 125), title, TITLE, fill=WHITE)
    if subtitle:
        text(d, (120, 200), subtitle, SUB, fill=(235,240,255))

def stick(draw, cx, cy, scale=1.0, pose='stand', accent=BLUE, t=0.0):
    # Simple child stick figure
    head_r = 42*scale
    torso = 130*scale
    hip_y = cy + 120*scale
    shoulder_y = cy + 40*scale
    lw = max(8, int(10*scale))
    # pose parameters
    la1=ra1=la2=ra2=ll1=rl1=ll2=rl2=0
    if pose=='jump':
        bounce = math.sin(t*math.pi*2)*28*scale
        cy -= bounce
        shoulder_y -= bounce
        hip_y -= bounce
        la1, ra1 = -65, 65
        la2, ra2 = -30, 30
        ll1, rl1 = -20, 20
        ll2, rl2 = -15, 15
    elif pose=='deadbug':
        la1, ra1 = -155, 35
        la2, ra2 = -155, 25
        ll1, rl1 = 155, -25
        ll2, rl2 = 145, -10
    elif pose=='sideplank':
        # draw separately
        draw.line((cx-180*scale, cy+70*scale, cx+190*scale, cy-40*scale), fill=NAVY, width=lw)
        draw.ellipse((cx+175*scale-head_r, cy-60*scale-head_r, cx+175*scale+head_r, cy-60*scale+head_r), outline=NAVY, width=lw, fill=(255,244,220))
        draw.line((cx-150*scale, cy+60*scale, cx-210*scale, cy+140*scale), fill=NAVY, width=lw)
        draw.line((cx-20*scale, cy+20*scale, cx+35*scale, cy+95*scale), fill=NAVY, width=lw)
        return
    elif pose=='lunge_down':
        la1, ra1 = -25, 25
        la2, ra2 = -10, 10
        ll1, rl1 = 35, -65
        ll2, rl2 = 70, 15
    elif pose=='lunge_up':
        la1, ra1 = -15, 15
        la2, ra2 = -10, 10
        ll1, rl1 = 10, -30
        ll2, rl2 = 20, 10
    elif pose=='balance':
        wobble = math.sin(t*math.pi*2)*10
        la1, ra1 = -70+wobble, 75-wobble
        la2, ra2 = -30, 30
        ll1, rl1 = 0, -70
        ll2, rl2 = 10, -20
    elif pose=='stretch_calf':
        la1, ra1 = -20, 15
        la2, ra2 = -10, 5
        ll1, rl1 = 15, -55
        ll2, rl2 = 25, -5
    elif pose=='stretch_chest':
        la1, ra1 = -90, 85
        la2, ra2 = -5, 5
        ll1, rl1 = 0, 0
        ll2, rl2 = 8, -8
    else:
        la1, ra1 = -35, 35
        la2, ra2 = -10, 10
        ll1, rl1 = 8, -8
        ll2, rl2 = 5, -5

    def endpoint(x, y, length, ang_deg):
        a = math.radians(ang_deg)
        return x + length*math.sin(a), y + length*math.cos(a)

    draw.ellipse((cx-head_r, cy-head_r, cx+head_r, cy+head_r), outline=NAVY, width=lw, fill=(255,244,220))
    draw.line((cx, cy+head_r, cx, hip_y), fill=NAVY, width=lw)
    draw.line((cx-55*scale, shoulder_y, cx+55*scale, shoulder_y), fill=accent, width=lw+6)
    l_el = endpoint(cx-55*scale, shoulder_y, 78*scale, la1)
    l_hand = endpoint(*l_el, 64*scale, la2)
    r_el = endpoint(cx+55*scale, shoulder_y, 78*scale, ra1)
    r_hand = endpoint(*r_el, 64*scale, ra2)
    for p1,p2,p3 in [((cx-55*scale, shoulder_y), l_el, l_hand), ((cx+55*scale, shoulder_y), r_el, r_hand)]:
        draw.line((*p1,*p2), fill=NAVY, width=lw)
        draw.line((*p2,*p3), fill=NAVY, width=lw)
    l_kn = endpoint(cx-35*scale, hip_y, 105*scale, ll1)
    l_ft = endpoint(*l_kn, 92*scale, ll2)
    r_kn = endpoint(cx+35*scale, hip_y, 105*scale, rl1)
    r_ft = endpoint(*r_kn, 92*scale, rl2)
    for p1,p2,p3 in [((cx-35*scale, hip_y), l_kn, l_ft), ((cx+35*scale, hip_y), r_kn, r_ft)]:
        draw.line((*p1,*p2), fill=NAVY, width=lw)
        draw.line((*p2,*p3), fill=NAVY, width=lw)

def slide_intro(sec=2.5):
    global frame_idx
    n = int(sec*FPS)
    for i in range(n):
        img,d=base_canvas()
        draw_header(d, '20分钟儿童体能训练', '居家版 · 增肌 / 协调 / 体态改善', BLUE)
        rounded_box(d, (110, 320, 970, 760), fill=(240,245,255), radius=36)
        text(d, (140, 360), '适用目标', SUB, BLUE)
        bullets = '• 肌肉量偏少\n• 协调性较弱\n• 驼背 / 外八倾向\n• 无需器械，在家可做'
        text(d, (150, 445), bullets, BODY, NAVY, spacing=16)
        rounded_box(d, (110, 810, 970, 1700), fill=(252,250,245), radius=36)
        text(d, (140, 850), '训练结构', SUB, ORANGE)
        items=[('3分钟','热身激活'),('4分钟','核心稳定'),('8分钟','下肢力量与协调'),('5分钟','拉伸放松')]
        y=980
        for idx,(m,lab) in enumerate(items,1):
            rounded_box(d,(150,y-20,930,y+120),fill=WHITE,radius=30,outline=LIGHT)
            text(d,(190,y+10),f'{idx}',TITLE,ORANGE)
            text(d,(300,y+5),lab,SUB,NAVY)
            text(d,(300,y+65),m,BODY,GRAY)
            y += 170
        text(d, (540, 1810), '演示版：每个动作展示关键姿势', SMALL, GRAY, anchor='ma')
        img.save(FRAMES / f'{frame_idx:05d}.png')
        frame_idx += 1

def slide_action(title_cn, duration_label, tips, pose_fn, color=GREEN, sec=3.0):
    global frame_idx
    n=int(sec*FPS)
    for i in range(n):
        t=i/max(1,n-1)
        img,d=base_canvas()
        draw_header(d, title_cn, duration_label, color)
        rounded_box(d,(90,300,990,1160),fill=(246,250,255),radius=42)
        pose_fn(d,t)
        rounded_box(d,(90,1210,990,1740),fill=(250,252,255),radius=42)
        text(d,(130,1260),'动作重点',SUB,color)
        y=1350
        for tip in tips:
            text(d,(140,y),f'• {tip}',BODY,NAVY,max_width=780)
            y += 100
        text(d,(540,1810),'动作演示为示意动画，正式训练以动作标准为先',SMALL,GRAY,anchor='ma')
        img.save(FRAMES / f'{frame_idx:05d}.png')
        frame_idx += 1

def pose_warmup(draw,t):
    # alternate worm and stretch
    text(draw,(540,360),'热身激活',SUB,anchor='ma',fill=GRAY)
    if t < 0.5:
        stick(draw,540,680,1.5,'stretch_chest',accent=ORANGE,t=t*2)
        text(draw,(540,1010),'伟大拉伸',SUB,anchor='ma',fill=ORANGE)
    else:
        stick(draw,540,700,1.45,'lunge_down',accent=ORANGE,t=(t-0.5)*2)
        text(draw,(540,1010),'毛毛虫爬（示意）',SUB,anchor='ma',fill=ORANGE)

def pose_deadbug(draw,t):
    draw.line((250,850,830,850), fill=LIGHT, width=12)
    stick(draw,540,720,1.4,'deadbug',accent=BLUE,t=t)

def pose_sideplank(draw,t):
    draw.line((220,920,860,920), fill=LIGHT, width=12)
    stick(draw,470,770,1.4,'sideplank',accent=BLUE,t=t)

def pose_lunge(draw,t):
    pose='lunge_down' if math.sin(t*math.pi*2) > 0 else 'lunge_up'
    draw.line((270,980,810,980), fill=LIGHT, width=10)
    rounded_box(draw,(720,420,900,520),fill=(255,246,232),radius=20)
    text(draw,(810,470),'3秒下\n1秒起',BODY,ORANGE,anchor='ma')
    stick(draw,540,660,1.55,pose,accent=GREEN,t=t)

def pose_jump(draw,t):
    draw.line((230,990,850,990), fill=LIGHT, width=10)
    stick(draw,540,700,1.5,'jump',accent=RED,t=t)
    for x in [430,540,650]:
        h = 150 + 40*math.sin(t*math.pi*2 + x)
        draw.line((x, 1100, x, 1100-h), fill=(255,210,120), width=8)
        draw.ellipse((x-10, 1090-h-10, x+10, 1090-h+10), fill=ORANGE)

def pose_balance(draw,t):
    draw.line((260,980,820,980), fill=LIGHT, width=10)
    stick(draw,540,680,1.5,'balance',accent=BLUE,t=t)
    ball_x = 720 + 60*math.sin(t*math.pi*2)
    ball_y = 520 + 40*math.cos(t*math.pi*2)
    draw.ellipse((ball_x-30, ball_y-30, ball_x+30, ball_y+30), fill=ORANGE)

def pose_calf(draw,t):
    draw.line((260,980,820,980), fill=LIGHT, width=10)
    draw.line((790,400,790,980), fill=LIGHT, width=12)
    stick(draw,530,700,1.5,'stretch_calf',accent=GREEN,t=t)

def pose_chest(draw,t):
    draw.line((260,360,260,1040), fill=LIGHT, width=12)
    stick(draw,500,690,1.5,'stretch_chest',accent=GREEN,t=t)

def slide_outro(sec=2.5):
    global frame_idx
    n = int(sec*FPS)
    for i in range(n):
        img,d=base_canvas()
        draw_header(d,'执行建议','每周 3-4 次，质量优先',NAVY)
        rounded_box(d,(100,330,980,1550),fill=(244,248,255),radius=42)
        tips='1. 严格按：热身 → 核心 → 力量 → 拉伸\n\n2. 动作标准优先，不追求做太快\n\n3. 分腿蹲和落地缓冲最关键\n\n4. 周末可加骑车、滑步车、跳绳等户外活动'
        text(d,(140,410),tips,BODY,NAVY,spacing=18,max_width=760)
        rounded_box(d,(140,1600,940,1760),fill=(255,244,228),radius=32)
        text(d,(540,1680),'这是一版演示视频，后续还可以升级成真人教练版',SUB,ORANGE,anchor='ma')
        img.save(FRAMES / f'{frame_idx:05d}.png')
        frame_idx += 1

slide_intro()
slide_action('热身激活', '3分钟 · 伟大拉伸 / 毛毛虫爬', ['激活全身肌肉','打开胸椎和髋关节','动作流畅，不要憋气'], pose_warmup, ORANGE, 3.0)
slide_action('死虫式', '3组 × 10次（左右交替）', ['腰部贴地','手脚对侧伸展','动作慢一点，重控制'], pose_deadbug, BLUE, 3.0)
slide_action('侧平板支撑', '每侧30秒 × 2组', ['屁股收紧','身体保持一条直线','肩膀不要塌'], pose_sideplank, BLUE, 3.0)
slide_action('保加利亚分腿蹲', '每侧8次 × 3组', ['下蹲慢 3 秒，站起快 1 秒','膝盖方向对准脚尖','这是增肌 + 平衡核心动作'], pose_lunge, GREEN, 3.5)
slide_action('原地纵跳摸高', '连续8次 × 2组', ['向上充分伸展','落地要轻','膝盖微屈缓冲'], pose_jump, RED, 3.0)
slide_action('单腿站立抛接球', '每腿30秒 × 2组', ['支撑腿微屈','身体不要乱晃','抛接物可用软球或玩具'], pose_balance, BLUE, 3.0)
slide_action('靠墙小腿拉伸', '每侧30秒 × 2组', ['后腿伸直','脚跟踩实地面','缓解外八和跟腱紧张'], pose_calf, GREEN, 3.0)
slide_action('靠墙胸部拉伸', '30秒 × 2组', ['手臂扶墙','身体轻轻前倾','打开肩膀，缓解驼背'], pose_chest, GREEN, 3.0)
slide_outro()

mp4 = OUTDIR / 'kids_workout_demo_v1.mp4'
subprocess.run([
    'ffmpeg','-y','-framerate',str(FPS),'-i',str(FRAMES / '%05d.png'),
    '-vf', 'format=yuv420p', '-c:v','libx264','-pix_fmt','yuv420p', str(mp4)
], check=True)
print(mp4)
