import asyncio, json
from pathlib import Path
import edge_tts
from pydub import AudioSegment

VOICE = "zh-CN-YunxiNeural"
RATE = "+4%"
PITCH = "-4Hz"
VOLUME = "+0%"

segments = [
    "WiFi明明满格，网速却慢得离谱？先别急着怪手机。",
    "那个WiFi图标，主要表示手机和路由器之间的无线信号强不强。它并不等于你到互联网的整条链路都很快。",
    "比如路由器就在你旁边，所以信号满格。但如果家里的宽带出口本身拥堵，或者运营商线路此时很忙，网速照样上不去。",
    "第二个常见原因是频段和干扰。二点四G穿墙更好，但附近路由器、蓝牙设备和各种无线设备都可能挤在一起；五G通常更快，但隔墙之后衰减也更明显。",
    "第三个原因是共享。家里电视在看四K视频、电脑在下载、手机在备份，所有设备都在分同一条宽带。你这里显示满格，也不代表带宽全归你。",
    "还有一种情况，测速很快但某个应用特别慢，那问题可能根本不在WiFi，而在对方服务器、线路路由或者应用本身。",
    "所以遇到满格但卡，最有效的排查顺序是：先测速，再分别试二点四G和五G，再看看是不是其他设备正在占带宽。",
    "记住一句话：WiFi满格，只能证明你离路由器这段连接不错，不代表整个互联网都快。下一期讲，八G加八G扩展内存，真的等于十六G吗？"
]

async def main():
    out = Path("output_wifi_fullbars")
    out.mkdir(exist_ok=True)
    combined = AudioSegment.silent(duration=0)
    timing = []
    cursor = 0
    for i, text in enumerate(segments, 1):
        mp3 = out / f"seg_{i:02d}.mp3"
        tts = edge_tts.Communicate(text, VOICE, rate=RATE, pitch=PITCH, volume=VOLUME)
        await tts.save(str(mp3))
        seg = AudioSegment.from_file(mp3)
        seg = seg.apply_gain(-0.5)
        start = cursor
        combined += seg
        cursor += len(seg)
        timing.append({"index": i, "start_ms": start, "end_ms": cursor, "text": text})
        if i != len(segments):
            gap = 90
            combined += AudioSegment.silent(duration=gap)
            cursor += gap
    combined.export(out / "wifi_fullbars_narration.wav", format="wav")
    combined.export(out / "wifi_fullbars_narration.mp3", format="mp3", bitrate="192k")
    (out / "timings.json").write_text(json.dumps(timing, ensure_ascii=False, indent=2), encoding="utf-8")
    (out / "voice.txt").write_text(f"{VOICE}\nrate={RATE}\npitch={PITCH}\n", encoding="utf-8")
    print("duration_ms", cursor)

asyncio.run(main())
