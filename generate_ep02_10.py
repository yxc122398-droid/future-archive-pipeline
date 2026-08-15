import asyncio
import json
import tempfile
from pathlib import Path

import edge_tts
from pydub import AudioSegment
from pydub.effects import normalize, compress_dynamic_range

OUT = Path('output_ep02_10')
OUT.mkdir(exist_ok=True)

EPISODES = {
2: {
    'title': '未来第一次被验证',
    'segments': [
        '林彻没有立刻报警。他先做了一件更理性的事——验证。',
        '二零二六年的档案里，除了两天后的死亡事件，还有一条不起眼的小记录。今天晚上十点十四分，实验楼四层会突然断电。',
        '他查了学校通知，又打电话问值班室。没有检修，没有停电计划，一切正常。',
        '十点十三分五十秒。林彻盯着墙上的电子钟，心里第一次希望这份档案是假的。',
        '十秒后，整层楼瞬间陷入黑暗。电脑、顶灯、走廊，应声熄灭。',
        '三秒以后，应急灯亮起。和档案记录的时间，一秒不差。',
        '林彻重新打开未来档案。原本灰色的界面，多出了一行新的文字：验证完成。读取权限，百分之一。',
        '而两天后的死亡倒计时，仍在继续。下一集：第一百三十七人。',
    ]},
3: {
    'title': '第一百三十七人',
    'segments': [
        '一百三十七。这个数字开始让林彻不安。因为事故发生的时间，是深夜十一点五十二分。',
        '那个时间，实验楼平时最多只有十几个人。到底为什么会死一百三十七人？',
        '他查遍未来两天的教室预约，终于在一个没有公开的内部页面里找到答案。',
        '八月十七日晚，学校将在实验楼举行智能装备挑战赛的封闭测试。参赛学生、教师和工作人员，一共一百三十六人。',
        '加上林彻，正好一百三十七。',
        '更诡异的是，名单的最后一栏写着：临时安全负责人——林彻。可他根本没有报名。',
        '十分钟后，他的邮箱收到一封新邮件：邀请您担任八月十七日夜间测试安全协助人员。',
        '未来不仅知道谁会出现。它似乎还在把所有人，一步一步推向那栋楼。下一集：死因被删除。',
    ]},
4: {
    'title': '死因被删除',
    'segments': [
        '死亡人数对上了，时间也对上了。可档案里最重要的一项，却被人为抹掉。',
        '事件原因后面，只有四个黑色方块。林彻尝试复制、截图、导出，得到的永远都是同样的遮挡。',
        '他干脆把文件拖进十六进制编辑器。几秒后，一串残缺的文字从数据里闪了出来。',
        '不是事故。',
        '下一秒，屏幕猛地变黑。那四个字像从来没有出现过一样，被彻底覆盖。',
        '未来档案重新启动，事件页面自动刷新。预计死亡人数从一百三十七，短暂跳成了一百三十八。',
        '新增的名字只出现了不到半秒。林彻只来得及看清两个字：苏晚。',
        '就在这时，实验室门外响起敲门声。一个女生的声音问：林彻，你电脑里，是不是也出现了奇怪的东西？下一集：第一百三十八个名字。',
    ]},
5: {
    'title': '第一百三十八个名字',
    'segments': [
        '门外的人叫苏晚，网络安全方向研究生。林彻刚刚在未来档案里，看见了她的名字。',
        '苏晚没有进门，只把手机递了过来。半小时前，她收到了一封没有发件人的邮件。',
        '邮件只有一句话：不要让林彻一个人去实验楼地下二层。',
        '问题是，这栋实验楼的公开建筑图里，根本没有地下二层。',
        '林彻再次打开死亡档案。苏晚的名字已经消失，人数也重新变回一百三十七。',
        '但页面最下面，多出一个从未见过的字段：变量干预记录。',
        '第一条记录的时间，正是苏晚收到邮件的那一分钟。后面只有四个字——目标接触。',
        '他们终于意识到，未来档案并不只是被动记录未来。有人正在利用它，主动改变现在。下一集：监控里的未来。',
    ]},
6: {
    'title': '监控里的未来',
    'segments': [
        '苏晚带来了一段视频。来源不是监控系统，而是她邮箱里一个自动解压的附件。',
        '视频只有十一秒。画面里的走廊，正是实验楼四层。右上角时间：八月十七日，二十三点五十一分。',
        '镜头里，未来的林彻从画面尽头冲过来，手里拿着一块烧焦的硬盘。',
        '他回头看了一眼，像是在躲什么人。下一秒，整条走廊全部断电。',
        '画面黑掉之前，监控玻璃的反光里出现了另一个人。',
        '那个人站得很远，看不清脸。但他的身形、走路姿势，甚至抬手的动作，都和林彻几乎一样。',
        '苏晚把最后一帧放大。那个人的手腕上，有一道很深的旧伤。',
        '林彻低头看向自己的手腕。那里现在什么都没有。下一集：不能离开学校。',
    ]},
7: {
    'title': '不能离开学校',
    'segments': [
        '既然两天后会死在学校，最简单的办法，就是离开。',
        '第二天一早，林彻买了最早一班高铁票。他没有告诉任何人，直接打车去了车站。',
        '车刚开出校门，手机里的未来档案突然弹出警告。事件地点，正在更新。',
        '原本的实验楼四层，变成了东环路高架。距离他的出租车，不到三公里。',
        '林彻让司机立刻停车。几秒后，地址再次改变，变成了他脚下这条辅路。',
        '他往回走，事件地点也跟着往回移动。',
        '这不是一个固定地点的灾难。至少对林彻来说，那个事件像是在追着他。',
        '当他重新踏进校门，档案里多出一行小字：逃离尝试，一次。剩余两次。下一集：第二次验证。',
    ]},
8: {
    'title': '第二次验证',
    'segments': [
        '苏晚不相信所谓命运。她要求再做一次验证，而且这次必须由他们自己选择。',
        '未来档案给出一条新的短期记录：今晚二十二点零六分，苏晚会接到一通电话。',
        '来电号码，是她自己的手机号。',
        '二十二点零五分五十八秒。手机安静得没有任何异常。两秒后，铃声突然响起。',
        '屏幕上的来电号码，真的和苏晚自己的号码完全一样。',
        '她接通电话。里面没有杂音，只有一个很轻的女声：不要让林彻打开地下二层。',
        '通话持续十七秒，然后自动挂断。运营商后台却没有这次呼叫记录。',
        '而未来档案里，第二次验证旁边出现了新的状态：通信链路确认。下一集：地下二层。',
    ]},
9: {
    'title': '地下二层',
    'segments': [
        '实验楼没有地下二层。至少现在的建筑资料里没有。',
        '苏晚翻出了二十五年前的施工存档。旧图纸上，地下停车层下面，还有一层被整块涂黑的区域。',
        '标注只有六个字：数据备份机房。二零零三年封闭。',
        '当晚十一点，他们绕过维修通道，在一面后来加建的墙后找到了旧消防门。',
        '门上没有锁，只有一个早已断电的刷卡器。林彻刚靠近，刷卡器突然自己亮了。',
        '未来档案同时弹出红色警告：进入该区域，将使事件提前十七小时。',
        '两个人站在门前沉默了几秒。然后，苏晚伸手按下门把。',
        '门后不是仓库，而是一整排仍在运行的老旧服务器。最里面那台屏幕上，只有一个文件夹：FUTURE_ARCHIVE。下一集：未来发来的第一句话。',
    ]},
10: {
    'title': '未来发来的第一句话',
    'segments': [
        '地下二层的服务器没有接校园网，也没有外部电源记录。可它们正在运行。',
        '林彻拔掉网线，屏幕没有变化。拔掉电源，风扇停了，可那台显示器依然亮着。',
        'FUTURE_ARCHIVE 文件夹自动打开。里面没有事件档案，只有一段纯文本。',
        '林彻。如果你看到这句话，说明第一次方案已经失败。',
        '这是未来档案里，第一次出现完整的人类语句。不是系统提示，也不是事件记录。',
        '文本最后没有名字，只有两个字母：L，C。',
        '林彻还没来得及继续看，旁边的死亡档案突然自动刷新。第一名确认死亡者仍然是他。第二名，却变成了苏晚。',
        '而倒计时，一口气跳掉了十七个小时。距离事件发生，只剩三十小时。未完待续。',
    ]},
}

PREFERRED = ['zh-CN-YunxiNeural', 'zh-CN-YunjianNeural', 'zh-CN-YunyangNeural']

async def pick_voice():
    voices = await edge_tts.list_voices()
    names = {v.get('ShortName') for v in voices}
    for voice in PREFERRED:
        if voice in names:
            return voice
    males = [v.get('ShortName') for v in voices if v.get('Locale') == 'zh-CN' and v.get('Gender') == 'Male']
    if not males:
        raise RuntimeError('No zh-CN male voice available')
    return males[0]

async def synth(text, voice, out_path, rate='-2%', pitch='-2Hz'):
    c = edge_tts.Communicate(text=text, voice=voice, rate=rate, volume='+0%', pitch=pitch)
    await c.save(str(out_path))

async def main():
    voice = await pick_voice()
    print('Using voice:', voice)
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        for ep, data in EPISODES.items():
            ep_dir = OUT / f'EP{ep:02d}'
            ep_dir.mkdir(parents=True, exist_ok=True)
            timeline = AudioSegment.silent(duration=120)
            timings = []
            current_ms = 120
            for idx, text in enumerate(data['segments'], 1):
                raw = td / f'ep{ep:02d}_{idx:02d}.mp3'
                rate = '-3%'
                pitch = '-3Hz'
                if idx in (4, 6, 7):
                    rate = '-5%'
                await synth(text, voice, raw, rate=rate, pitch=pitch)
                seg = AudioSegment.from_file(raw)
                seg = compress_dynamic_range(seg, threshold=-19.0, ratio=2.0, attack=8.0, release=90.0)
                seg = normalize(seg, headroom=2.0)
                start_ms = current_ms
                timeline += seg
                current_ms += len(seg)
                timings.append({'index': idx, 'text': text, 'start_ms': start_ms, 'duration_ms': len(seg)})
                pause = 140 if idx < len(data['segments']) else 0
                if pause:
                    timeline += AudioSegment.silent(duration=pause)
                    current_ms += pause
            timeline = timeline.set_frame_rate(48000).set_channels(2)
            wav = ep_dir / f'未来档案_EP{ep:02d}_旁白.wav'
            mp3 = ep_dir / f'未来档案_EP{ep:02d}_旁白.mp3'
            timeline.export(wav, format='wav')
            timeline.export(mp3, format='mp3', bitrate='192k')
            info = {'episode': ep, 'title': data['title'], 'voice': voice, 'total_ms': len(timeline), 'segments': timings}
            (ep_dir / 'timings.json').write_text(json.dumps(info, ensure_ascii=False, indent=2), encoding='utf-8')
            print(f'EP{ep:02d}: {len(timeline)/1000:.2f}s')
    (OUT / 'voice.txt').write_text(voice + '\n', encoding='utf-8')

if __name__ == '__main__':
    asyncio.run(main())
