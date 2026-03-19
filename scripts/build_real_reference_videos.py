from pathlib import Path
import subprocess, math, os, textwrap

BASE = Path('/Users/a123456/.openclaw/workspace/video-output/reference-clips')
AUDIO = Path('/Users/a123456/.openclaw/workspace/video-output/reference-audio')
OUT = Path('/Users/a123456/.openclaw/workspace/video-output/reference-followalong-videos')
AUDIO.mkdir(parents=True, exist_ok=True)
OUT.mkdir(parents=True, exist_ok=True)
FONT = '/System/Library/Fonts/Hiragino Sans GB.ttc'
VOICE = 'Tingting'
RATE = '190'

cfgs = [
    dict(name='greatstretch', title='伟大拉伸', subtitle='每侧3次', cue='沉髋 → 转胸口 → 换边', start=0, dur=12,
         text='伟大拉伸。每侧三次。先跨出一大步，双手放在前脚两侧。先把髋部慢慢沉下去，再让手肘向下，最后把同侧手臂转向天花板。动作慢一点，感受髋部和胸口被打开。做完一边，再换另一边。'),
    dict(name='inchworm', title='毛毛虫爬', subtitle='3次', cue='手往前爬 → 到平板 → 脚走回', start=0, dur=10,
         text='毛毛虫爬。做三次。先站直，双手慢慢去找地面，再一步一步向前爬到平板支撑。然后把双脚小步走回到手边，再站起来。注意肚子收紧，不要塌腰。'),
    dict(name='deadbug', title='死虫式', subtitle='3组 × 10次', cue='对侧伸展，腰背贴地', start=0, dur=12,
         text='死虫式。三组，每组十次，左右交替。仰卧，双手向上，双腿抬起。右手向后，左腿向前，慢慢伸出去，再收回来。然后换另一侧。整个过程腰背贴地，动作越慢越好。'),
    dict(name='sideplank', title='侧平板支撑', subtitle='每侧30秒 × 2组', cue='手肘在肩下，身体一条线', start=0, dur=12,
         text='侧平板支撑。每侧保持三十秒。手肘放在肩膀正下方，身体尽量保持一条直线。收紧肚子和屁股，不要塌腰，不要耸肩。先做一边，时间到后换另一边。'),
    dict(name='splitsquat', title='保加利亚分腿蹲', subtitle='每侧8次 × 3组', cue='下去3秒，起身1秒', start=8, dur=14,
         text='保加利亚分腿蹲。每侧八次。前脚踩稳，后脚放高。下去的时候慢三秒，起身的时候快一秒。膝盖方向对准脚尖，身体不要摇晃。这个动作主要练腿和稳定性。做完一边，再换另一边。'),
    dict(name='jump', title='原地纵跳摸高', subtitle='连续8次 × 2组', cue='向上跳高，落地轻一点', start=10, dur=10,
         text='原地纵跳摸高。连续做八次。先微微下蹲，再快速向上跳，手尽量去摸高。落地的时候膝盖弯一点，轻轻缓冲，像小猫落地一样轻。每一次都要稳稳站住。'),
    dict(name='balance', title='单腿站立抛接', subtitle='每腿30秒 × 2组', cue='支撑腿微屈，眼睛看前方', start=0, dur=10,
         text='单腿站立抛接。每条腿三十秒。先单腿站稳，支撑腿微微弯曲，眼睛看前面。双手去接球，身体不要乱晃。如果晃了也没关系，慢慢找回平衡。时间到后换另一条腿。'),
    dict(name='calf', title='靠墙小腿拉伸', subtitle='每侧30秒 × 2组', cue='后腿伸直，脚跟踩实', start=0, dur=10,
         text='靠墙小腿拉伸。每侧三十秒。双手扶墙，一脚在前，一脚在后。后面的腿伸直，脚跟要踩实地面。身体轻轻往前推，感受小腿后侧被拉开。保持呼吸，不要弹。'),
    dict(name='chest', title='靠墙胸部拉伸', subtitle='每侧30秒 × 2组', cue='手扶墙，胸口慢慢打开', start=0, dur=10,
         text='靠墙胸部拉伸。每侧三十秒。一只手扶墙，手臂打开。身体慢慢转开，让胸口和肩膀前侧被拉开。注意肩膀不要耸起来，动作轻一点，慢慢呼吸。'),
]

def run(cmd):
    subprocess.run(cmd, check=True)

for c in cfgs:
    src = BASE / f"{c['name']}.mp4"
    aiff = AUDIO / f"{c['name']}.aiff"
    m4a = AUDIO / f"{c['name']}.m4a"
    if not aiff.exists():
        run(['say','-v',VOICE,'-r',RATE,'-o',str(aiff),c['text']])
    run(['ffmpeg','-y','-i',str(aiff),'-c:a','aac','-b:a','128k',str(m4a)])
    # audio duration
    dur = float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',str(m4a)]).decode().strip())
    target = max(dur + 1.2, c['dur']*2)
    out = OUT / f"{c['name']}.mp4"
    vf = (
        f"scale=768:1024:force_original_aspect_ratio=increase,crop=768:1024,"
        f"drawbox=x=18:y=16:w=732:h=78:color=#16284B@0.88:t=fill,"
        f"drawtext=fontfile='{FONT}':text='{c['title']}':fontcolor=white:fontsize=42:x=(w-text_w)/2:y=28,"
        f"drawbox=x=140:y=96:w=488:h=46:color=white@0.92:t=fill,"
        f"drawtext=fontfile='{FONT}':text='{c['subtitle']}':fontcolor=#4D6488:fontsize=28:x=(w-text_w)/2:y=106,"
        f"drawbox=x=36:y=892:w=696:h=116:color=white@0.9:t=fill,"
        f"drawtext=fontfile='{FONT}':text='{c['cue']}':fontcolor=#20345D:fontsize=30:x=(w-text_w)/2:y=922,"
        f"drawtext=fontfile='{FONT}':text='跟练提示：动作慢一点，做标准':fontcolor=#667A9B:fontsize=22:x=(w-text_w)/2:y=966"
    )
    run([
        'ffmpeg','-y','-stream_loop','-1','-ss',str(c['start']),'-t',str(c['dur']),'-i',str(src),'-i',str(m4a),
        '-vf',vf,'-map','0:v:0','-map','1:a:0','-c:v','libx264','-pix_fmt','yuv420p','-c:a','aac','-shortest','-movflags','+faststart',str(out)
    ])
    print(out)
