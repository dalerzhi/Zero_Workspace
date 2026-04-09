from pathlib import Path
import subprocess, json, requests

APP_ID='cli_a909ad9f75fadbb5'
APP_SECRET='p1MtN6OZic92OCOpMgxaZdSzAvRfsrys'
CHAT_ID='ou_7c6c3cdce8475c7a8de63811592c37f9'
WORK = Path('/Users/a123456/.openclaw/workspace/tmp')
styles = [
    ('warm_female', 'VoxCPM2 风格 1，温柔女声'),
    ('calm_male', 'VoxCPM2 风格 2，冷静男声'),
    ('bright_girl', 'VoxCPM2 风格 3，活泼少女'),
    ('narrator', 'VoxCPM2 风格 4，旁白解说'),
]

def duration_ms(path: Path) -> int:
    r = subprocess.run([
        'ffprobe','-i',str(path),'-v','quiet','-show_entries','format=duration','-of','default=noprint_wrappers=1:nokey=1'
    ], capture_output=True, text=True, check=True)
    return int(float(r.stdout.strip()) * 1000)

def to_opus(src: Path, dst: Path):
    subprocess.run([
        'ffmpeg','-y','-i',str(src),'-c:a','libopus','-b:a','24k','-ar','16000','-ac','1',str(dst)
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

token_resp=requests.post('https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal',json={'app_id':APP_ID,'app_secret':APP_SECRET}).json()
assert token_resp.get('code') == 0, token_resp
token = token_resp['tenant_access_token']
headers = {'Authorization': f'Bearer {token}'}

for name, label in styles:
    wav = WORK / f'voxcpm2-{name}.wav'
    opus = WORK / f'voxcpm2-{name}.opus'
    to_opus(wav, opus)
    dur = duration_ms(opus)
    with open(opus,'rb') as f:
        up = requests.post('https://open.feishu.cn/open-apis/im/v1/files', headers=headers, files={'file':(opus.name, f, 'audio/opus')}, data={'file_type':'opus','duration':dur}).json()
    assert up.get('code') == 0, up
    file_key = up['data']['file_key']
    payload = {
        'receive_id': CHAT_ID,
        'msg_type': 'audio',
        'content': json.dumps({'file_key': file_key, 'duration': dur}, ensure_ascii=False)
    }
    send = requests.post('https://open.feishu.cn/open-apis/im/v1/messages', headers={**headers, 'Content-Type':'application/json'}, params={'receive_id_type':'open_id'}, json=payload).json()
    assert send.get('code') == 0, send
    print(label, send['data']['message_id'], dur, flush=True)
