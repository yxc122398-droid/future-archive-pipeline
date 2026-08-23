import asyncio, json
from pathlib import Path
import edge_tts
from pydub import AudioSegment

OUT=Path('output_speedtest_download')
OUT.mkdir(exist_ok=True)
voice='zh-CN-YunxiNeural'
rate='+8%'
segments=[
'测速明明五百兆，为什么下载只有几十兆？先别急着怪宽带。',
'因为测速里的五百兆，单位其实是兆比特每秒，也就是Mbps。',
'而下载软件常显示的是MB每秒。一个字母大小写，差了八倍。',
'所以五百Mbps的宽带，理论下载上限大约只有六十二点五MB每秒。',
'再扣掉协议开销、WiFi干扰和服务器限速，实际四十到六十MB每秒都很常见。',
'记住：Mbps除以八，才大致等于你熟悉的MB每秒。每天一个网络避坑知识。'
]

async def main():
    meta=[]
    combined=AudioSegment.silent(duration=0)
    cur=0
    for i,text in enumerate(segments,1):
        mp3=OUT/f'seg_{i:02d}.mp3'
        await edge_tts.Communicate(text=text, voice=voice, rate=rate).save(str(mp3))
        a=AudioSegment.from_file(mp3)
        meta.append({'i':i,'text':text,'start_ms':cur,'dur_ms':len(a)})
        combined += a
        cur += len(a)
    combined.export(OUT/'测速500Mbps为什么下载只有几十MB每秒_旁白.mp3', format='mp3', bitrate='192k')
    combined.export(OUT/'测速500Mbps为什么下载只有几十MB每秒_旁白.wav', format='wav')
    (OUT/'timings.json').write_text(json.dumps({'total_ms':cur,'segments':meta},ensure_ascii=False,indent=2),encoding='utf-8')
    (OUT/'voice.txt').write_text(f'{voice} {rate}',encoding='utf-8')

asyncio.run(main())
