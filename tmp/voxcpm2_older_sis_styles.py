from pathlib import Path
import subprocess

WORK = Path('/Users/a123456/.openclaw/workspace')
VOX = WORK / 'tmp' / 'VoxCPM' / '.venv' / 'bin' / 'voxcpm'
styles = [
    (
        'flirty_boss',
        '(御姐音，成熟妩媚，带一点挑逗感和掌控感，语速从容，尾音轻轻上扬)'
        '晚上好呀，别急，先把注意力给我。你现在听到的，是一条偏风骚御姐风格的 VoxCPM2 试听。'
        '我说话不会太快，但会让你忍不住继续听下去。要是你喜欢这种又稳、又撩、还带点压迫感的感觉，那我们可以继续往这个方向细调。'
    ),
    (
        'lazy_charm',
        '(御姐音，慵懒性感，气声略多，像深夜贴着耳边说话，语气自信又松弛)'
        '这么晚了，还在听声音测试啊。那这条我就故意说得更近一点，也更暧昧一点。'
        '这种感觉不是那种用力过猛的撒娇，而是很自然地把氛围拉下来，让人觉得放松，又有点被拿捏。'
        '如果你想要那种深夜电台里，很会撩人的御姐感，这条应该会比较接近。'
    ),
    (
        'sharp_tease',
        '(御姐音，性感利落，带一点坏笑和轻微攻击性，像聪明又危险的都市姐姐)'
        '好，现在换一种。这个版本会更锋利一点，不是温柔挂的，是那种一开口就知道她很会掌控节奏的人。'
        '她不会一直哄你，但会用很轻的语气，把你的注意力一点点勾过去。'
        '如果你喜欢更有张力、更有侵略性的御姐风，那我们就沿着这条继续往前推。'
    ),
]

for name, text in styles:
    wav = WORK / 'tmp' / f'voxcpm2-{name}.wav'
    cmd = [str(VOX), 'design', '--text', text, '--output', str(wav), '--no-denoiser']
    print('RUN', name, flush=True)
    subprocess.run(cmd, check=True)
    print('DONE', wav, flush=True)
