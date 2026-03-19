import requests, subprocess, os, json
from pathlib import Path

NOIZ_API_KEY = Path.home().joinpath('.noiz_api_key').read_text().strip()
VOICE_ID = '4f71a876'
OUT = Path('/Users/a123456/.openclaw/workspace/video-output/followalong-audio')
OUT.mkdir(parents=True, exist_ok=True)

scripts = {
'greatstretch': '伟大拉伸。每侧三次。准备，左脚向前跨大一步，双手放地。先沉髋，感受髋部打开。手肘向下，再把手臂慢慢转向上方。保持呼吸。做完换边。',
'inchworm': '毛毛虫爬。做三次。准备，站直。双手去找地面，慢慢向前爬到平板支撑，再把脚一步一步走回到手边。全程核心收紧，不要塌腰。',
'deadbug': '死虫式。三组，每组十次左右交替。准备，腰背贴地，双手向上，双腿抬起。右手向后，左腿向前，慢慢伸。收回。换另一侧。动作越慢越好。',
'sideplank': '侧平板支撑。每侧保持三十秒。准备，手肘在肩膀正下方，身体成一条直线。收紧肚子和屁股。保持呼吸，不要塌腰。时间到后换另一边。',
'splitsquat': '保加利亚分腿蹲。每侧八次。准备，后脚放高，前脚踩稳。下蹲三秒，起身一秒。膝盖方向对准脚尖，身体保持稳定。做完换边。',
'jump': '原地纵跳摸高。连续八次。准备，先微微下蹲，再快速向上跳，手去摸高。落地要轻，膝盖弯一点做缓冲。每次都稳稳落地。',
'balance': '单腿站立抛接。每腿三十秒。准备，单腿站稳，支撑腿微微弯曲。眼睛看前方，双手接球。身体不要乱晃，慢慢控制。时间到后换腿。',
'calf': '靠墙小腿拉伸。每侧三十秒。准备，双手扶墙，一脚在前一脚在后。后腿伸直，脚跟踩实地面。轻轻把身体往前推，感受小腿后侧被拉开。',
'chest': '靠墙胸部拉伸。每侧三十秒。准备，一只手扶墙，手臂打开。身体慢慢转向前方外侧，胸口打开，肩膀放松。不要耸肩，保持自然呼吸。'
}

for name, text in scripts.items():
    wav = OUT / f'{name}.wav'
    url = 'https://noiz.ai/v1/text-to-speech'
    headers = {'Authorization': NOIZ_API_KEY}
    data = {'text': text, 'voice_id': VOICE_ID, 'output_format': 'wav', 'speed': '0.92'}
    r = requests.post(url, headers=headers, data=data, timeout=120)
    r.raise_for_status()
    wav.write_bytes(r.content)
    print(wav)
