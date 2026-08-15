import asyncio
import os
import tempfile
from pathlib import Path

import edge_tts
from pydub import AudioSegment
from pydub.effects import normalize, compress_dynamic_range

OUT = Path('output')
OUT.mkdir(exist_ok=True)

# Shorter, faster narration designed to fit a ~75 s Bilibili episode.
SEGMENTS = [
    ('凌晨十一点四十七分。雨还在下。整栋实验楼，只剩林彻一个人。', '-4%', '-2Hz', 650),
    ('又一次仿真失败后，他正准备关掉电脑，文件管理器却突然闪了一下。', '-2%', '-2Hz', 450),
    ('屏幕上，多出了一个从没见过的磁盘。名字只有四个字——未来档案。', '-5%', '-3Hz', 650),
    ('林彻拔掉所有外接设备。可它没有消失。设备管理器里，也没有任何记录。', '-2%', '-2Hz', 520),
    ('磁盘中只有七个文件夹。从二零二六，一直到二零七六。', '-3%', '-2Hz', 500),
    ('他试着打开最后一个。屏幕只留下冰冷的提示：当前时间节点，无权访问。', '-6%', '-3Hz', 700),
    ('紧接着，二零二六年的文件夹，自行亮了起来。', '-4%', '-2Hz', 500),
    ('里面只有一份档案。日期，是两天后的八月十七日。事件等级：一级。', '-6%', '-3Hz', 650),
    ('预计死亡人数，一百三十七。', '-8%', '-4Hz', 750),
    ('林彻继续往下看。下一行，写着第一名确认死亡者——林彻。', '-7%', '-4Hz', 950),
    ('下一秒，屏幕右下角浮出红色倒计时：四十七小时，五十九分，四十一秒。', '-6%', '-3Hz', 600),
    ('从这一刻起，他只剩不到四十八小时，去证明这份来自未来的档案，到底是真是假。', '-3%', '-2Hz', 650),
]

PREFERRED = ['zh-CN-YunxiNeural', 'zh-CN-YunyangNeural', 'zh-CN-YunjianNeural']

async def pick_voice():
    voices = await edge_tts.list_voices()
    names = {v.get('ShortName') for v in voices}
    for voice in PREFERRED:
        if voice in names:
            return voice
    zh_male = [v.get('ShortName') for v in voices if v.get('Locale') == 'zh-CN' and v.get('Gender') == 'Male']
    if not zh_male:
        raise RuntimeError('No zh-CN male voice available')
    return zh_male[0]

async def main():
    voice = await pick_voice()
    print('Using voice:', voice)
    combined = AudioSegment.silent(duration=450)
    with tempfile.TemporaryDirectory() as td:
        for i, (text, rate, pitch, pause_ms) in enumerate(SEGMENTS, 1):
            p = Path(td) / f'{i:02d}.mp3'
            communicate = edge_tts.Communicate(text=text, voice=voice, rate=rate, volume='+0%', pitch=pitch)
            await communicate.save(str(p))
            seg = AudioSegment.from_file(p)
            # Gentle processing only; preserve natural articulation.
            seg = compress_dynamic_range(seg, threshold=-19.0, ratio=2.0, attack=8.0, release=90.0)
            combined += seg + AudioSegment.silent(duration=pause_ms)

    combined = normalize(combined, headroom=1.5)
    # Do not exceed the video duration. Leave room for final title card.
    max_ms = 71500
    if len(combined) > max_ms:
        combined = combined[:max_ms].fade_out(300)
    combined = combined.set_frame_rate(48000).set_channels(2)
    combined.export(OUT / '未来档案_EP01_自然旁白.wav', format='wav')
    combined.export(OUT / '未来档案_EP01_自然旁白.mp3', format='mp3', bitrate='192k')
    (OUT / 'voice.txt').write_text(voice + '\n', encoding='utf-8')
    print('Duration ms:', len(combined))

if __name__ == '__main__':
    asyncio.run(main())
