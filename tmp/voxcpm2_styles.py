from pathlib import Path
import subprocess

WORK = Path('/Users/a123456/.openclaw/workspace')
VOX = WORK / 'tmp' / 'VoxCPM' / '.venv' / 'bin' / 'voxcpm'
BASE = '你好，我是 Zero，下面这条是 VoxCPM2 的风格试听。'
styles = [
    ('warm_female', '(年轻女性，声音温柔温暖，像朋友轻声聊天)' + BASE),
    ('calm_male', '(成熟男声，平静克制，低沉自然，有一点科技感)' + BASE),
    ('bright_girl', '(活泼少女音，轻快明亮，带一点笑意)' + BASE),
    ('narrator', '(旁白感男声，清晰稳重，像纪录片解说)' + BASE),
]

for name, text in styles:
    wav = WORK / 'tmp' / f'voxcpm2-{name}.wav'
    cmd = [str(VOX), 'design', '--text', text, '--output', str(wav), '--no-denoiser']
    print('RUN', name, flush=True)
    subprocess.run(cmd, check=True)
    print('DONE', wav, flush=True)
