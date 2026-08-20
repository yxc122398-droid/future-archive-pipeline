import asyncio, json
from pathlib import Path
import edge_tts
from pydub import AudioSegment

OUT=Path('output_router_restart')
OUT.mkdir(exist_ok=True)
VOICE='zh-CN-YunxiNeural'
RATE='+12%'
PITCH='-2Hz'
segments=[
'路由器到底要不要每天重启？长期不关，真的会越用越慢吗？',
'答案是：没必要每天重启。正常路由器本来就是按长期运行设计的。',
'但如果设备多、缓存堆积、内存泄漏，或者连接异常，重启确实可能让它暂时恢复正常。',
'更实用的做法是：网络明显变慢、掉线频繁时再重启；如果几乎每天都要重启，问题多半不是“重启不够勤”，而是路由器性能、散热或宽带本身有问题。',
'每天一个网络避坑知识。下一期：路由器放哪里，信号才最好？'
]
async def gen_one(i,text):
    p=OUT/f'seg_{i:02d}.mp3'
    await edge_tts.Communicate(text,VOICE,rate=RATE,pitch=PITCH).save(str(p))
    return p
async def main():
    files=[]
    for i,t in enumerate(segments,1): files.append(await gen_one(i,t))
    final=AudioSegment.silent(duration=120)
    timings=[]; cur=120
    for i,(f,text) in enumerate(zip(files,segments),1):
        a=AudioSegment.from_file(f)
        st=cur; final+=a; cur+=len(a)
        gap=120 if i<len(files) else 0
        final+=AudioSegment.silent(duration=gap); cur+=gap
        timings.append({'i':i,'text':text,'start_ms':st,'dur_ms':len(a),'end_ms':st+len(a)})
    final.export(OUT/'路由器要不要每天重启_旁白.mp3',format='mp3',bitrate='192k')
    final.export(OUT/'路由器要不要每天重启_旁白.wav',format='wav')
    (OUT/'timings.json').write_text(json.dumps({'voice':VOICE,'rate':RATE,'pitch':PITCH,'total_ms':len(final),'segments':timings},ensure_ascii=False,indent=2),encoding='utf-8')
    (OUT/'voice.txt').write_text(f'{VOICE} {RATE} {PITCH}',encoding='utf-8')
    print('duration_ms',len(final))
asyncio.run(main())
