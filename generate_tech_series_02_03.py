import asyncio, json
from pathlib import Path
import edge_tts
from pydub import AudioSegment

VOICE = "zh-CN-YunxiNeural"
RATE = "+3%"
PITCH = "-4Hz"
VOLUME = "+0%"

EPISODES = {
    "ep02_120w": [
        "手机写着一百二十瓦快充，为什么真正充电时，一百二十瓦往往只出现一小段？",
        "因为一百二十瓦通常代表峰值能力，不代表从百分之一到百分之一百都一直维持这个功率。",
        "电量比较低、温度合适、充电器和线材都匹配时，手机才更容易进入高功率区间。",
        "随着电量上升，电池电压越来越接近上限，充电管理系统会主动把电流往下收。",
        "到了高电量区间，功率还会继续下降，避免电芯温度和电压压力过高。",
        "如果手机本身已经很热，或者边玩边充，系统甚至会更早限功率。",
        "所以快充真正追求的，不是全程一百二十瓦，而是把最需要速度的前半段尽可能缩短。",
        "下一期讲一个更直观的问题：手机一热，为什么性能会突然掉下来？"
    ],
    "ep03_thermal": [
        "手机一发热就变卡，很多人以为是处理器不行了，其实大多数时候，是手机自己在踩刹车。",
        "处理器工作越快，功耗通常越高，产生的热量也越多。",
        "当温度接近系统设定的安全范围，手机会通过动态电压频率调节，降低处理器频率和工作电压。",
        "频率降下来，性能自然会下降，所以你会感觉游戏掉帧、应用响应变慢。",
        "同时，屏幕亮度、充电功率，甚至部分网络和相机功能，也可能被一起限制。",
        "这不是故障，而是为了避免持续高温伤害电池、芯片和其他元件。",
        "等温度下降以后，系统通常会逐步恢复性能。",
        "所以散热好的手机，不只是摸起来更凉，它更重要的价值，是能把高性能维持得更久。"
    ]
}

async def make_episode(name, segments):
    out = Path("output_tech_series") / name
    out.mkdir(parents=True, exist_ok=True)
    combined = AudioSegment.silent(duration=0)
    timing = []
    cursor = 0
    for i, text in enumerate(segments, 1):
        mp3 = out / f"seg_{i:02d}.mp3"
        tts = edge_tts.Communicate(text, VOICE, rate=RATE, pitch=PITCH, volume=VOLUME)
        await tts.save(str(mp3))
        seg = AudioSegment.from_file(mp3).apply_gain(-1.0)
        start = cursor
        combined += seg
        cursor += len(seg)
        timing.append({"index": i, "start_ms": start, "end_ms": cursor, "text": text})
        if i != len(segments):
            gap = 110
            combined += AudioSegment.silent(duration=gap)
            cursor += gap
    combined.export(out / "narration.wav", format="wav")
    combined.export(out / "narration.mp3", format="mp3", bitrate="192k")
    (out / "timings.json").write_text(json.dumps(timing, ensure_ascii=False, indent=2), encoding="utf-8")
    (out / "voice.txt").write_text(f"{VOICE}\nrate={RATE}\npitch={PITCH}\n", encoding="utf-8")
    print(name, cursor)

async def main():
    for name, segments in EPISODES.items():
        await make_episode(name, segments)

asyncio.run(main())
