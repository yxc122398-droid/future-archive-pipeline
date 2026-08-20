import asyncio, json
from pathlib import Path
import edge_tts
from pydub import AudioSegment

VOICE='zh-CN-YunxiNeural'
RATE='+4%'
PITCH='-4Hz'
segments=[
'一万毫安的充电宝，为什么连两次五千毫安的手机都充不满？先别急着说商家虚标。',
'真正的问题，是你不能只拿毫安时直接对比。充电宝内部电芯通常按三点七伏标容量，一万毫安时，大约等于三十七瓦时。',
'但给手机充电时，充电宝要先把电压升到五伏、九伏甚至更高，这一步会有转换损耗。',
'假设整套输出效率是百分之八十五，三十七瓦时最后真正送到线材里的，大概只有三十一点五瓦时。',
'而一块五千毫安时手机电池，标称电压往往接近三点八五伏，一块就接近十九瓦时。两块就是三十八瓦时左右。',
'所以一万毫安时充电宝，本来就很难把两块五千毫安时手机从零充到满。再加上线材损耗、手机自身发热和边充边用，实际次数还会更少。',
'以后买充电宝，别只看毫安时。看额定能量和额定容量，更接近真实可用电量。下一期我讲，WiFi明明满格，为什么网速还能慢得离谱。'
]

async def main():
    out=Path('output_powerbank10000'); out.mkdir(exist_ok=True)
    full=AudioSegment.silent(duration=0); timing=[]; cursor=0
    for i,text in enumerate(segments,1):
        p=out/f'seg_{i:02d}.mp3'
        await edge_tts.Communicate(text,VOICE,rate=RATE,pitch=PITCH).save(str(p))
        seg=AudioSegment.from_file(p)
        start=cursor; full+=seg; cursor+=len(seg)
        timing.append({'index':i,'start_ms':start,'end_ms':cursor,'text':text})
        if i!=len(segments): full+=AudioSegment.silent(duration=110); cursor+=110
    full.export(out/'powerbank10000_narration.mp3',format='mp3',bitrate='192k')
    (out/'timings.json').write_text(json.dumps(timing,ensure_ascii=False,indent=2),encoding='utf-8')
    (out/'voice.txt').write_text(f'{VOICE}\nrate={RATE}\npitch={PITCH}\n',encoding='utf-8')
    print(cursor)

asyncio.run(main())
