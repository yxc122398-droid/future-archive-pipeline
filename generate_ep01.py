import asyncio
import tempfile
from pathlib import Path

import edge_tts
from pydub import AudioSegment
from pydub.effects import normalize, compress_dynamic_range

OUT = Path('output')
OUT.mkdir(exist_ok=True)
VIDEO_MS = 74750

# Each line is anchored to the exact visual beat in the 74.75 s edit.
# (start_ms, text, rate, pitch, maximum speech window in ms)
CUES = [
    (500,  '凌晨十一点四十七分。雨还在下。整栋实验楼，只剩林彻一个人。', '-1%', '-2Hz', 5600),
    (6500, '又一次仿真失败。他正准备关机，屏幕忽然闪了一下。', '+2%', '-2Hz', 6500),
    (13750,'一个从未见过的磁盘，凭空出现。名字只有四个字——未来档案。', '+2%', '-3Hz', 5900),
    (20000,'里面只有七个文件夹。从二零二六，一直到二零七六。', '+3%', '-2Hz', 6200),
    (26600,'他试着打开最后一个。系统提示：当前时间节点，无权访问。只有二零二六仍能打开。', '+7%', '-3Hz', 7000),
    (34100,'两天后的八月十七日。一级事件。预计死亡，一百三十七人。', '+3%', '-3Hz', 7200),
    (41800,'林彻继续往下看。首名确认死亡人员——林彻。', '-1%', '-4Hz', 7600),
    (50000,'他关掉窗口，又重新打开。名字没有变化。倒计时已经开始：四十七小时，五十九分，四十一秒。', '+8%', '-3Hz', 9300),
    (59800,'天气正常，没有灾害预警。可档案中的事件原因，仍然被锁定。', '+4%', '-2Hz', 6200),
    (66300,'距离林彻死亡——还有四十八小时。', '-5%', '-4Hz', 5600),
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


def fit_to_window(seg: AudioSegment, max_ms: int) -> AudioSegment:
    # Never let one sentence drift into the next visual event. Edge-TTS rates above
    # are selected to fit naturally; this is only a final safety trim at a quiet tail.
    if len(seg) <= max_ms:
        return seg
    return seg[:max_ms].fade_out(120)

async def main():
    voice = await pick_voice()
    print('Using voice:', voice)
    timeline = AudioSegment.silent(duration=VIDEO_MS, frame_rate=48000).set_channels(2)

    with tempfile.TemporaryDirectory() as td:
        for i, (start_ms, text, rate, pitch, max_ms) in enumerate(CUES, 1):
            p = Path(td) / f'{i:02d}.mp3'
            communicate = edge_tts.Communicate(
                text=text, voice=voice, rate=rate, volume='+0%', pitch=pitch
            )
            await communicate.save(str(p))
            seg = AudioSegment.from_file(p)
            seg = compress_dynamic_range(seg, threshold=-19.0, ratio=2.0, attack=8.0, release=90.0)
            seg = normalize(seg, headroom=2.0)
            seg = fit_to_window(seg, max_ms)
            seg = seg.set_frame_rate(48000).set_channels(2)
            timeline = timeline.overlay(seg, position=start_ms)
            print(f'cue {i:02d}: start={start_ms/1000:.2f}s len={len(seg)/1000:.2f}s')

    timeline = normalize(timeline, headroom=1.7)
    timeline.export(OUT / '未来档案_EP01_同步旁白.wav', format='wav')
    timeline.export(OUT / '未来档案_EP01_同步旁白.mp3', format='mp3', bitrate='192k')
    (OUT / 'voice.txt').write_text(voice + '\n', encoding='utf-8')
    print('Timeline duration ms:', len(timeline))

if __name__ == '__main__':
    asyncio.run(main())
