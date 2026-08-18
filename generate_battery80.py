import asyncio, json
from pathlib import Path
import edge_tts
from pydub import AudioSegment

VOICE = "zh-CN-YunxiNeural"
RATE = "+4%"
PITCH = "-3Hz"
VOLUME = "+0%"

segments = [
    "手机充到百分之八十以后突然变慢，很多时候不是充电器坏了。",
    "锂电池充电通常会经历两个主要阶段。前半段，充电器尽量给出较大的电流，电量涨得很快。",
    "可当电池电压接近上限以后，系统会开始主动收电流。",
    "因为这时候如果还保持大电流，电池更容易发热，也会加速老化。",
    "所以你会看到一个很典型的现象：前面几十分钟冲得飞快，到了八十%左右，速度突然慢下来。",
    "这不是浪费时间，而是在用更温和的方式，把最后一段电量一点点塞进去。",
    "再加上手机还会根据温度、电池健康度和你是否正在使用手机动态限功率，所以同一个充电器，不同场景速度也会不一样。",
    "一句话：百分之八十以后变慢，很多时候是电池保护在工作，而不是你的充电器突然摆烂。"
]

async def main():
    out = Path("output_battery80")
    out.mkdir(exist_ok=True)
    combined = AudioSegment.silent(duration=0)
    timing = []
    cursor = 0
    for i, text in enumerate(segments, 1):
        mp3 = out / f"seg_{i:02d}.mp3"
        tts = edge_tts.Communicate(text, VOICE, rate=RATE, pitch=PITCH, volume=VOLUME)
        await tts.save(str(mp3))
        seg = AudioSegment.from_file(mp3)
        start = cursor
        combined += seg
        cursor += len(seg)
        timing.append({"index": i, "start_ms": start, "end_ms": cursor, "text": text})
        if i != len(segments):
            combined += AudioSegment.silent(duration=90)
            cursor += 90
    combined.export(out / "手机充到80以后为什么变慢_旁白.wav", format="wav")
    combined.export(out / "手机充到80以后为什么变慢_旁白.mp3", format="mp3", bitrate="192k")
    (out / "timings.json").write_text(json.dumps(timing, ensure_ascii=False, indent=2), encoding="utf-8")
    (out / "voice.txt").write_text(f"{VOICE}\nrate={RATE}\npitch={PITCH}\n", encoding="utf-8")
    print("duration_ms", cursor)

asyncio.run(main())
