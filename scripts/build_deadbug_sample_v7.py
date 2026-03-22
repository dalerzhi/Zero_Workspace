from pathlib import Path
import math
import subprocess
import wave
import struct

BASE = Path('/Users/a123456/.openclaw/workspace/video-output/reference-clips')
OUT = Path('/Users/a123456/.openclaw/workspace/video-output/final-samples')
AUDIO = OUT / 'audio'
OVERLAY = OUT / 'overlay_v6'  # 复用 v6 overlay
OUT.mkdir(parents=True, exist_ok=True)
AUDIO.mkdir(parents=True, exist_ok=True)

video_src = BASE / 'deadbug.mp4'
video_clean = OUT / 'deadbug_clean_loop_source_v7.mp4'
voice_m4a = AUDIO / 'deadbug_v6_voice.m4a'  # 直接复用已验证中文口播
bgm_wav = AUDIO / 'deadbug_v7_bgm_musiclike.wav'
out = OUT / 'deadbug_final_sample_v7.mp4'
preview = OUT / 'deadbug_final_sample_v7_preview12s.mp4'

main_seconds = 53
sr = 44100


def ensure_video_clean():
    if video_clean.exists():
        return
    subprocess.run([
        'ffmpeg', '-y',
        '-ss', '8.0', '-t', '26.0', '-i', str(video_src),
        '-an',
        '-c:v', 'libx264', '-preset', 'medium', '-crf', '18',
        '-pix_fmt', 'yuv420p', str(video_clean)
    ], check=True)


def smoothstep(x: float) -> float:
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    return x * x * (3 - 2 * x)


def make_musiclike_bgm(path: Path, duration: float):
    n = int(sr * duration)
    beat = 60.0 / 112.0
    bar = beat * 4

    # C - G - Am - F（轻快常见流行和声）
    prog = [
        (261.63, 329.63, 392.00),
        (196.00, 246.94, 293.66),
        (220.00, 261.63, 329.63),
        (174.61, 220.00, 261.63),
    ]

    frames = bytearray()
    for i in range(n):
        t = i / sr
        bar_idx = int(t / bar) % len(prog)
        chord = prog[bar_idx]

        # 和弦 pad：慢起慢落，避免机械感
        in_bar = (t % bar) / bar
        env = 0.45 + 0.55 * math.sin(math.pi * in_bar) ** 2
        pad = env * (
            0.12 * math.sin(2 * math.pi * chord[0] * t)
            + 0.10 * math.sin(2 * math.pi * chord[1] * t)
            + 0.08 * math.sin(2 * math.pi * chord[2] * t)
        )

        # 低频根音（每拍轻推一下）
        beat_phase = (t % beat) / beat
        bass_env = math.exp(-5.5 * beat_phase)
        bass = 0.20 * bass_env * math.sin(2 * math.pi * (chord[0] / 2) * t)

        # 轻鼓组
        kick_phase = t % beat
        kick = 0.0
        if kick_phase < 0.11:
            f0 = 110 - 45 * (kick_phase / 0.11)
            kick = 0.35 * math.exp(-20 * kick_phase) * math.sin(2 * math.pi * f0 * t)

        snare = 0.0
        snare_phase = (t - beat) % (2 * beat)
        if snare_phase < 0.08:
            noise = math.sin(2 * math.pi * 7000 * t) * math.sin(2 * math.pi * 9973 * t)
            snare = 0.12 * math.exp(-32 * snare_phase) * noise

        # hi-hat：每半拍短噪点
        hh_phase = t % (beat / 2)
        hihat = 0.0
        if hh_phase < 0.028:
            noise = math.sin(2 * math.pi * 12000 * t) * math.sin(2 * math.pi * 8431 * t)
            hihat = 0.06 * math.exp(-80 * hh_phase) * noise

        # 总线 + 慢速起落淡入淡出
        fade_in = smoothstep(min(1.0, t / 1.2))
        fade_out = smoothstep(min(1.0, max(0.0, (duration - t) / 1.5)))
        y = (pad + bass + kick + snare + hihat) * fade_in * fade_out

        # 软限幅
        y = math.tanh(1.7 * y) * 0.75
        s = int(max(-1.0, min(1.0, y)) * 32767)
        frames += struct.pack('<h', s)

    with wave.open(str(path), 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(frames)

    # 后期：立体声 + EQ + 轻压缩，得到更“正常”BGM质感
    polished = path.with_name(path.stem + '_stereo.wav')
    subprocess.run([
        'ffmpeg', '-y', '-i', str(path),
        '-af',
        'aformat=sample_rates=44100:channel_layouts=stereo,'
        'highpass=f=55,lowpass=f=12000,'
        'equalizer=f=220:width_type=h:width=120:g=1.8,'
        'equalizer=f=3200:width_type=h:width=1800:g=1.2,'
        'acompressor=threshold=-20dB:ratio=2.5:attack=15:release=180,'
        'loudnorm=I=-24:LRA=8:TP=-2',
        '-c:a', 'pcm_s16le', str(polished)
    ], check=True)
    polished.replace(path)


def render(target: Path, seconds: int):
    subprocess.run([
        'ffmpeg', '-y',
        '-stream_loop', '-1', '-i', str(video_clean),
        '-loop', '1', '-i', str(OVERLAY / 'top_ready.png'),
        '-loop', '1', '-i', str(OVERLAY / 'top_action.png'),
        '-loop', '1', '-i', str(OVERLAY / 'top_end.png'),
        '-loop', '1', '-i', str(OVERLAY / 'bottom_cue.png'),
        '-i', str(voice_m4a),
        '-i', str(bgm_wav),
        '-filter_complex',
        '[0:v]scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2:black[v0];'
        '[v0][1:v]overlay=0:0:enable=between(t\\,0\\,8)[v1];'
        '[v1][2:v]overlay=0:0:enable=between(t\\,8\\,47)[v2];'
        '[v2][3:v]overlay=0:0:enable=between(t\\,47\\,53)[v3];'
        '[v3][4:v]overlay=0:0:enable=between(t\\,0\\,53)[v];'
        '[5:a]apad=pad_dur=80,volume=1.0,asplit=2[voice_sc][voice_mix];'
        '[6:a]volume=0.72[bgm];'
        '[bgm][voice_sc]sidechaincompress=threshold=0.028:ratio=9:attack=8:release=240[ducked];'
        '[ducked][voice_mix]amix=inputs=2:weights=0.95 1.0:normalize=0,alimiter=limit=0.95[a]',
        '-map', '[v]', '-map', '[a]',
        '-t', str(seconds),
        '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
        '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart',
        str(target)
    ], check=True)


def main():
    if not voice_m4a.exists():
        raise FileNotFoundError(f'缺少中文口播文件: {voice_m4a}')

    ensure_video_clean()
    make_musiclike_bgm(bgm_wav, main_seconds + 2)

    # 先出 12s 小样
    render(preview, 12)

    # 再出整片
    render(out, main_seconds)

    print(f'preview={preview}')
    print(f'final={out}')


if __name__ == '__main__':
    main()
