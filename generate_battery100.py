import asyncio, json
from pathlib import Path
import edge_tts
from pydub import AudioSegment

VOICE = "zh-CN-YunxiNeural"
RATE = "+5%"
PITCH = "-4Hz"
VOLUME = "+0%"

segments = [
    "手机明明已经显示百分之百，为什么插着充电器，电还会继续往里走？",
    "因为屏幕上的百分之百，并不等于电芯真的到了化学极限。手机会故意留出安全余量，避免电池长期顶在最危险的最高电压附近。",
    "而且最后阶段不是全速猛灌。电池接近充满时，充电管理芯片会进入恒压阶段，电压基本稳定，而充电电流会越来越小。",
    "所以你看到百分之百以后，系统可能还会用很小的电流做最后的补充和电量校准；达到停止条件后，就会暂停充电。",
    "之后如果手机自己耗掉一点电，部分机型还会根据温度、充电策略和电量阈值重新补一点，而不是永远持续充电。",
    "真正需要注意的其实不是百分之百这个数字，而是高温。边充边玩让温度长期偏高，比偶尔充到百分之百更值得警惕。",
    "下一期我直接画给你看，标着一百二十瓦的快充，为什么通常只有前面一小段时间能跑到高功率。"
]

async def main():
    out = Path("output_battery100")
    out.mkdir(exist_ok=True)
    combined = AudioSegment.silent(duration=0)
    timing=[]
    cursor=0
    for i, text in enumerate(segments,1):
        mp3 = out / f"seg_{i:02d}.mp3"
        tts = edge_tts.Communicate(text, VOICE, rate=RATE, pitch=PITCH, volume=VOLUME)
        await tts.save(str(mp3))
        seg = AudioSegment.from_file(mp3).apply_gain(-1.0)
        start = cursor
        combined += seg
        cursor += len(seg)
        timing.append({"index":i,"start_ms":start,"end_ms":cursor,"text":text})
        if i != len(segments):
            gap = 90
            combined += AudioSegment.silent(duration=gap)
            cursor += gap
    combined.export(out/"手机100以后为什么还能充_旁白.wav", format="wav")
    combined.export(out/"手机100以后为什么还能充_旁白.mp3", format="mp3", bitrate="192k")
    (out/"timings.json").write_text(json.dumps(timing, ensure_ascii=False, indent=2), encoding="utf-8")
    (out/"voice.txt").write_text(f"{VOICE}\nrate={RATE}\npitch={PITCH}\n", encoding="utf-8")
    print("duration_ms", cursor)
    for x in timing: print(x)

asyncio.run(main())
