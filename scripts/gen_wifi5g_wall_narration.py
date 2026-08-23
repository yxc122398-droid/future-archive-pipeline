import asyncio
import edge_tts
from pathlib import Path

TEXT = '''为什么5GHz WiFi测速更快，却一隔墙就明显掉速？因为快和穿墙，本来就是两回事。5GHz频段通常更干净，也更容易用上更宽的信道，所以近距离速度更高；但频率更高，信号穿过墙体时衰减也更明显。2.4GHz虽然速度通常低一些，却更适合隔墙和远距离连接。所以离路由器近，优先用5GHz；隔了几堵墙或者距离很远，2.4GHz反而可能更稳。别只看满格，稳定和速度要一起看。每天一个网络避坑知识。'''

async def main():
    out = Path('output')
    out.mkdir(exist_ok=True)
    communicate = edge_tts.Communicate(TEXT, voice='zh-CN-YunxiNeural', rate='+10%', pitch='+0Hz')
    await communicate.save(str(out / 'wifi5g_wall_narration.mp3'))
    (out / 'script.txt').write_text(TEXT, encoding='utf-8')

asyncio.run(main())
