import asyncio, json, os
from pathlib import Path
import edge_tts
from pydub import AudioSegment

VOICE = "zh-CN-YunxiNeural"
RATE = "+2%"
PITCH = "-6Hz"
VOLUME = "+0%"

segments = [
    "一千五百度左右的高温燃气，为什么没有把航空发动机里的涡轮叶片直接烧化？",
    "关键不是叶片硬扛高温，而是工程师想办法让叶片本身的温度，始终低于它能承受的极限。",
    "第一层，是内部冷却。压气机引出一部分高压空气，送进叶片内部弯弯曲曲的冷却通道，把热量从里面带走。",
    "第二层，是气膜冷却。冷空气再从叶片表面密密麻麻的小孔喷出来，在叶片外面铺出一层很薄的冷空气保护膜。",
    "第三层，是热障涂层。叶片表面会覆盖耐高温陶瓷涂层，进一步减少高温燃气向金属内部传热。",
    "所以你看到的不是一块金属在硬抗一千多度，而是内部冷却、表面气膜和热障涂层一起工作。",
    "代价也很明显：抽走的冷却空气会影响发动机效率，所以冷却孔怎么开、开多少，本身就是非常复杂的设计问题。",
    "这就是为什么现代涡轮叶片，看上去只有巴掌大，却是航空发动机里最难做的零件之一。"
]

async def main():
    out = Path("output_engine_pilot")
    out.mkdir(exist_ok=True)
    combined = AudioSegment.silent(duration=0)
    timing=[]
    cursor=0
    for i, text in enumerate(segments,1):
        mp3 = out / f"seg_{i:02d}.mp3"
        tts = edge_tts.Communicate(text, VOICE, rate=RATE, pitch=PITCH, volume=VOLUME)
        await tts.save(str(mp3))
        seg = AudioSegment.from_file(mp3)
        seg = seg.apply_gain(-1.0)
        start = cursor
        combined += seg
        cursor += len(seg)
        timing.append({"index":i,"start_ms":start,"end_ms":cursor,"text":text})
        if i != len(segments):
            gap = 120
            combined += AudioSegment.silent(duration=gap)
            cursor += gap
    combined.export(out/"涡轮叶片为什么不会被烧化_旁白.wav", format="wav")
    combined.export(out/"涡轮叶片为什么不会被烧化_旁白.mp3", format="mp3", bitrate="192k")
    (out/"timings.json").write_text(json.dumps(timing, ensure_ascii=False, indent=2), encoding="utf-8")
    (out/"voice.txt").write_text(f"{VOICE}\nrate={RATE}\npitch={PITCH}\n", encoding="utf-8")
    print("duration_ms", cursor)
    for x in timing: print(x)

asyncio.run(main())
