import asyncio, json
from pathlib import Path
import edge_tts
from pydub import AudioSegment

VOICE = "zh-CN-YunxiNeural"
RATE = "+4%"
PITCH = "-3Hz"
VOLUME = "+0%"

segments = [
    "手机写着八GB加八GB扩展内存，难道真的就等于十六GB内存？答案是不等于。",
    "前面的八GB，是手机真正焊在主板上的物理内存，也就是LPDDR内存。它专门给处理器高速读写，速度快，延迟也低。",
    "后面的八GB扩展内存，通常是从手机存储空间里划出一部分，用来暂存暂时不用的数据，或者配合系统的交换机制减轻内存压力。",
    "问题是，手机闪存再快，也不是物理内存。它的带宽、延迟和随机访问性能，都不能和真正的LPDDR内存直接画等号。",
    "所以扩展内存最大的作用，不是让游戏帧率突然变高，而是内存紧张时，少杀几个后台应用，切回去时少一点重新加载。",
    "如果你的手机本来就有足够的物理内存，开启很大的扩展内存，体感提升可能非常有限。部分场景甚至还会增加额外的数据搬运。",
    "买手机时，八GB加八GB不能当成真正的十六GB来看。优先看物理内存容量，扩展内存只能算辅助。",
    "下一期讲一个更容易被参数骗到的问题：手机两亿像素，就一定比五千万像素拍得更清楚吗？"
]

async def main():
    out = Path("output_ram_extension")
    out.mkdir(exist_ok=True)
    combined = AudioSegment.silent(duration=0)
    timing=[]
    cursor=0
    for i,text in enumerate(segments,1):
        mp3 = out / f"seg_{i:02d}.mp3"
        await edge_tts.Communicate(text, VOICE, rate=RATE, pitch=PITCH, volume=VOLUME).save(str(mp3))
        seg = AudioSegment.from_file(mp3)
        start=cursor
        combined += seg
        cursor += len(seg)
        timing.append({"index":i,"start_ms":start,"end_ms":cursor,"text":text})
        if i != len(segments):
            combined += AudioSegment.silent(duration=90)
            cursor += 90
    combined.export(out/"8GB加8GB扩展内存_旁白.wav", format="wav")
    combined.export(out/"8GB加8GB扩展内存_旁白.mp3", format="mp3", bitrate="192k")
    (out/"timings.json").write_text(json.dumps(timing,ensure_ascii=False,indent=2),encoding="utf-8")
    (out/"voice.txt").write_text(f"{VOICE}\nrate={RATE}\npitch={PITCH}\n",encoding="utf-8")
    print("duration_ms",cursor)

asyncio.run(main())
