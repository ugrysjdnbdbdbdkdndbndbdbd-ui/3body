"""Seed initial chronicle data."""
import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from backend.database import AsyncSessionLocal
from backend.models.chronicle import ChronicleEventORM

CHRONICLES = [
    # --- 黄金时代 (The Golden Age) ---
    {
        "era": "黄金时代",
        "year": 1967,
        "title": "红岸工程立项",
        "content": "在疯狂年代的背景下，寻找外星文明的绝密计划“红岸工程”正式立项，选址大兴安岭雷达峰。叶文洁的父亲叶哲泰在批斗中死去，邵琳在揭发材料上签字。这一事件在叶文洁心中种下了对人类文明彻底绝望的种子，为后来她按下那个毁灭性的按钮埋下了伏笔。",
        "summary": "叶哲泰之死与红岸工程建立；叶文洁人性观的起点。",
        "image_url": "https://picsum.photos/seed/redcoast1967/600/400",
        "event_type": "official",
        "causality_status": "collapsed"
    },
    {
        "era": "黄金时代",
        "year": 1971,
        "title": "第一次红岸发射",
        "content": "叶文洁利用太阳作为信号放大器（太阳增益效应），向宇宙发送了第一条包含人类文明自述的信号。这是人类第一次也是最后一次以恒星级的功率向宇宙发出呐喊。红岸基地的真实目的自此与她的个人命运交织。",
        "summary": "叶文洁利用太阳增益向宇宙发射信号；红岸技术路线确立。",
        "image_url": "https://picsum.photos/seed/sunamplifier/600/400",
        "event_type": "official",
        "causality_status": "collapsed"
    },
    {
        "era": "黄金时代",
        "year": 1979,
        "title": "不要回答",
        "content": "三体世界的和平主义者（1379号监听员）截获了地球信号，并回复了著名的警告：“不要回答！不要回答！不要回答！”若地球不回答，三体将无法精确定位。这是两个文明之间最后一次善意的闪烁。叶文洁收到后未向组织汇报。",
        "summary": "1379号监听员发出警告；叶文洁选择不汇报并准备回复。",
        "image_url": "https://picsum.photos/seed/donotanswer/600/400",
        "event_type": "official",
        "causality_status": "collapsed"
    },
    {
        "era": "黄金时代",
        "year": 1979,
        "title": "审判日的邀请",
        "content": "叶文洁在红岸基地按下发射键，回复：“到这里来吧，我将帮助你们获得这个世界。”雷志成发现地外接触欲上报，叶文洁割断其与杨卫宁的绳索，二人坠崖身亡。这八秒钟的传输彻底锁定了两个文明的命运，三体舰队起航。",
        "summary": "叶文洁回复三体信号、杀害雷志成与杨卫宁；地球坐标暴露。",
        "image_url": "https://picsum.photos/seed/yereplied/600/400",
        "event_type": "official",
        "causality_status": "collapsed"
    },
    {
        "era": "黄金时代",
        "year": 1982,
        "title": "红岸基地撤编与伊文斯接触",
        "content": "红岸基地撤编。叶文洁与伊文斯在大兴安岭相遇，将三体通讯的秘密与“消灭人类暴政”的信念传递给他。伊文斯后来在“审判日”号上建立第二红岸，与三体直接对话，成为降临派核心。",
        "summary": "红岸撤编；叶文洁将秘密交给伊文斯，ETO 雏形形成。",
        "image_url": "https://picsum.photos/seed/yeevans/600/400",
        "event_type": "official",
        "causality_status": "collapsed"
    },
    {
        "era": "黄金时代",
        "year": 2007,
        "title": "杨冬之死与物理学崩塌",
        "content": "杨冬在发现加速器异常与母亲真相后自杀，遗言“物理学从来就没有存在过”。其死引发汪淼介入调查，进而牵出宇宙闪烁、倒计时与 ETO。丁仪等学者陷入绝望，常伟思等军方开始将地外威胁纳入战略。",
        "summary": "杨冬自杀；智子锁死与人性真相成为物理学崩塌的象征。",
        "image_url": "https://picsum.photos/seed/yangdong/600/400",
        "event_type": "official",
        "causality_status": "collapsed"
    },
    {
        "era": "黄金时代",
        "year": 2007,
        "title": "古筝行动",
        "content": "为夺取“审判日”号上的三体信息而不破坏硬盘，史强提出古筝行动。巴拿马运河盖拉德水道，汪淼研制的“飞刃”纳米丝将巨轮切成四十层薄片，伊文斯与降临派核心覆灭。人类获取约 28GB 三体通讯数据，红岸—三体对话与智子计划曝光。",
        "summary": "纳米飞刃切割审判日号；伊文斯死亡，三体情报被人类获取。",
        "image_url": "https://picsum.photos/seed/operationguzheng/600/400",
        "event_type": "official",
        "causality_status": "collapsed"
    },

    # --- 危机纪元 (Crisis Era) ---
    {
        "era": "危机纪元",
        "year": 1,
        "title": "智子工程与物理学锁死",
        "content": "三体人将质子二维展开蚀刻电路，制造出超级计算机“智子”。两颗智子到达地球，锁死人类高能物理实验并实时监控全人类。加速器结果被篡改，基础研究沦为幻觉。丁仪称“物理学不存在了”；汪淼等人目睹宇宙闪烁与倒计时。人类科学进入漫长严冬。",
        "summary": "智子抵达；高能物理被锁死，宇宙闪烁与倒计时出现。",
        "image_url": "https://picsum.photos/seed/sophonblockade/600/400",
        "event_type": "official",
        "causality_status": "collapsed"
    },
    {
        "era": "危机纪元",
        "year": 2,
        "title": "面壁计划启动",
        "content": "为对抗智子的全知全能，PDC 启动“面壁计划”。泰勒、雷迪亚兹、希恩斯、罗辑被选为面壁者，享有极高权力且无需向任何人解释战略。ETO 则派出对应破壁人。罗辑最初拒绝参与，转而利用面壁者资源寻找梦中人庄颜。",
        "summary": "四位面壁者诞生；罗辑表面消极、实为唯一未破壁者。",
        "image_url": "https://picsum.photos/seed/wallfacer/600/400",
        "event_type": "official",
        "causality_status": "collapsed"
    },
    {
        "era": "危机纪元",
        "year": 5,
        "title": "罗辑的咒语：187J3X1",
        "content": "罗辑在叶文洁墓前悟出宇宙社会学公理与黑暗森林法则。他以雪地工程为掩护，通过太阳增益向宇宙广播 187J3X1 恒星坐标，作为“咒语”实验。面壁者无需解释；智子与人类均无法理解其真实意图，直至多年后该恒星被光粒摧毁。",
        "summary": "罗辑悟出黑暗森林并发布咒语；187J3X1 成为威慑验证。",
        "image_url": "https://picsum.photos/seed/spell187j3x1/600/400",
        "event_type": "official",
        "causality_status": "collapsed"
    },
    {
        "era": "危机纪元",
        "year": 8,
        "title": "泰勒与雷迪亚兹破壁",
        "content": "泰勒的“蚊群计划”（球状闪电量子化舰队）被破壁人当众揭穿：宏观退相干后仅为概率云，无法作战——“主不在乎”。雷迪亚兹的水星坠落与太阳系同归于尽战略亦被揭露；破壁人预言三体先发制人、人类将处决面壁者。泰勒自杀，雷迪亚兹回国后被民众处决。",
        "summary": "泰勒、雷迪亚兹被破壁；“主不在乎”成为名场面。",
        "image_url": "https://picsum.photos/seed/wallbreaker/600/400",
        "event_type": "official",
        "causality_status": "collapsed"
    },
    {
        "era": "危机纪元",
        "year": 8,
        "title": "阶梯计划：只送大脑",
        "content": "PIA 局长维德提出阶梯计划：用核脉冲推进将探测器送往三体舰队，因运载极限仅能送约 500 克——一只冷冻大脑。云天明自愿献脑，程心在不知情下促成其入选。探测器偏离航线，后于数世纪后被三体截获；云天明在三体世界存活并传递情报。",
        "summary": "阶梯计划执行；云天明大脑被发射，程心终生愧疚。",
        "image_url": "https://picsum.photos/seed/staircase/600/400",
        "event_type": "official",
        "causality_status": "collapsed"
    },
    {
        "era": "危机纪元",
        "year": 12,
        "title": "章北海刺杀老航天",
        "content": "为推动无工质辐射推进立项、打破化学推进派垄断，章北海以陨石为武器在太空刺杀坚持工质路线的老航天（毕云峰等）。调查被归为意外，无工质研发得以立项，为人类舰队在末日之战后的逃亡奠定技术基础。",
        "summary": "章北海暗杀老航天；无工质推进路线确立。",
        "image_url": "https://picsum.photos/seed/assassination/600/400",
        "event_type": "official",
        "causality_status": "collapsed"
    },
    {
        "era": "危机纪元",
        "year": 205,
        "title": "末日之战",
        "content": "人类集结约 2000 艘恒星级战舰于木星轨道，迎战三体探测器“水滴”。丁仪乘艇接触水滴后发出“傻孩子们，快跑啊”的警告。水滴以强互作用力材料锐角机动撞击，约 30 分钟内摧毁除“自然选择”号与追击编队、“青铜时代”号与“量子”号外全部舰艇。太空化为金属坟场。",
        "summary": "水滴摧毁联合舰队；丁仪牺牲，仅四舰幸存。",
        "image_url": "https://picsum.photos/seed/doomsdaybattle/600/400",
        "event_type": "official",
        "causality_status": "collapsed"
    },
    {
        "era": "危机纪元",
        "year": 205,
        "title": "自然选择号逃亡",
        "content": "章北海劫持“自然选择”号并启动“前进四”，率舰逃离太阳系。追击舰“终极规律”号、“企业”号、“深空”号与“自然选择”号一同陷入燃料与猜疑链死局。",
        "summary": "章北海劫持自然选择号；星舰人类火种启程。",
        "image_url": "https://picsum.photos/seed/naturalselection/600/400",
        "event_type": "official",
        "causality_status": "collapsed"
    },
    {
        "era": "危机纪元",
        "year": 205,
        "title": "黑暗森林战役",
        "content": "幸存四舰陷入猜疑链：燃料与配件有限，无法判断对方是否先发制人。“终极规律”号率先发动次声波氢弹攻击，“自然选择”号全员死亡；随后“青铜时代”号攻击“量子”号。“不要返航，这里不是家”——青铜时代号向蓝色空间号发出警告。人类在太空中完成第一次黑暗森林实践。",
        "summary": "星舰互相攻击；猜疑链与“这里不是家”成为名句。",
        "image_url": "https://picsum.photos/seed/darkforestbattle/600/400",
        "event_type": "official",
        "causality_status": "collapsed"
    },
    {
        "era": "危机纪元",
        "year": 208,
        "title": "威慑建立",
        "content": "罗辑在叶文洁墓前，以雪地工程部署的核弹链为引力波天线，向三体世界发出最后通牒：若不停止入侵则向宇宙广播三体坐标。咒语应验（187J3X1 被摧毁）使三体信服。水滴转向，三体舰队转向。人类凭借黑暗森林威慑赢得暂时和平；罗辑成为执剑人。",
        "summary": "罗辑建立黑暗森林威慑；执剑人时代开启。",
        "image_url": "https://picsum.photos/seed/deterrence/600/400",
        "event_type": "official",
        "causality_status": "collapsed"
    },

    # --- 威慑纪元 (Deterrence Era) ---
    {
        "era": "威慑纪元",
        "year": 5,
        "title": "希恩斯破壁与钢印族",
        "content": "山杉惠子作为希恩斯的破壁人当众揭穿：希恩斯表面研究思想钢印增智，实则秘密植入“人类必败”信念，制造钢印族。钢印族成为逃亡主义种子，渗透进太空军与社会。希恩斯称“水有毒”；破壁后惠子自杀。",
        "summary": "希恩斯被妻子破壁；钢印族与逃亡主义蔓延。",
        "image_url": "https://picsum.photos/seed/steelstamp/600/400",
        "event_type": "official",
        "causality_status": "collapsed"
    },
    {
        "era": "威慑纪元",
        "year": 61,
        "title": "执剑人交接与威慑失败",
        "content": "罗辑执剑 54 年后交出引力波广播开关。程心接任执剑人；三体判定其威慑度极低、不会按下开关。交接后约 15 分钟，埋伏在太阳系边缘的水滴摧毁全部引力波发射台。智子宣布人类迁往澳大利亚保留地。威慑纪元终结。",
        "summary": "程心接任执剑人；水滴摧毁发射台，智子宣布保留地。",
        "image_url": "https://picsum.photos/seed/deterrencefail/600/400",
        "event_type": "official",
        "causality_status": "collapsed"
    },
    {
        "era": "威慑纪元",
        "year": 61,
        "title": "四维碎片与水滴摧毁",
        "content": "追击“蓝色空间”号的“万有引力”号与“蓝色空间”号一同进入四维碎片。在四维空间中三维封闭结构被展开，褚岩率队从内部破坏水滴的强互作用力发生器——“它不再是神话了”。两舰在智子盲区内会合。",
        "summary": "四维碎片中人类从内部摧毁水滴；两舰会师。",
        "image_url": "https://picsum.photos/seed/4dfoil/600/400",
        "event_type": "official",
        "causality_status": "collapsed"
    },
    {
        "era": "威慑纪元",
        "year": 61,
        "title": "万有引力号广播",
        "content": "威慑失效后，万有引力号在智子盲区内举行舰上表决，决定是否启动引力波广播。莫沃维奇主持；最终通过。两舰向宇宙广播三体星系坐标，随后地球坐标亦被暴露。黑暗森林打击进入倒计时。",
        "summary": "万有引力号表决并启动引力波广播；两文明坐标暴露。",
        "image_url": "https://picsum.photos/seed/gravitybroadcast/600/400",
        "event_type": "official",
        "causality_status": "collapsed"
    },

    # --- 广播纪元 (Broadcast Era) ---
    {
        "era": "广播纪元",
        "year": 2,
        "title": "程心与云天明会面",
        "content": "云天明通过智子安排的匿名会面与程心相见，传递三个童话（王国的新画师、饕餮海、深水王子），将曲率驱动、黑域、多维空间等情报隐喻其中。程心未能完全解读；云天明的爱意与人类的生机被编码在故事里。",
        "summary": "云天明三个童话传递曲率与黑域情报；程心与团队解读。",
        "image_url": "https://picsum.photos/seed/threetales/600/400",
        "event_type": "official",
        "causality_status": "collapsed"
    },
    {
        "era": "广播纪元",
        "year": 7,
        "title": "三体星系毁灭",
        "content": "坐标广播后，一颗光粒击中三体星系恒星，引发爆发并吞没三体行星。三体文明失去母星，舰队成为流浪文明。地球观测到三体星系熄灭；两个世界的命运在黑暗森林中再次对称。",
        "summary": "光粒打击三体恒星；三体母星毁灭，文明流浪。",
        "image_url": "https://picsum.photos/seed/trisolaris/600/400",
        "event_type": "official",
        "causality_status": "collapsed"
    },
    {
        "era": "广播纪元",
        "year": 8,
        "title": "智子遣返与茶道谈话",
        "content": "智子撤离地球前邀请罗辑与程心茶道谈话，透露“安全声明”（制造黑域）可避免打击，但会令文明自我封闭。智子解除对地球的封锁后随三体舰队离去。人类在恐惧与希望中进入掩体时代。",
        "summary": "智子茶道谈话透露安全声明；智子离开地球。",
        "image_url": "https://picsum.photos/seed/sophontea/600/400",
        "event_type": "official",
        "causality_status": "collapsed"
    },

    # --- 掩体纪元 (Bunker Era) ---
    {
        "era": "掩体纪元",
        "year": 11,
        "title": "星环城与维德抵抗",
        "content": "维德领导的星环公司秘密研制光速飞船（曲率驱动），与联邦政府对立。程心冬眠前将公司交给维德并约定“只在不伤害人类的前提下继续”。维德率武装抵抗政府军，程心苏醒后要求维德履约交出权力；维德遵守承诺放弃抵抗并被处决，人类失去提前获得光速飞船的窗口。",
        "summary": "维德星环城抵抗；程心要求交权，维德被处决。",
        "image_url": "https://picsum.photos/seed/ringcity/600/400",
        "event_type": "official",
        "causality_status": "collapsed"
    },
    {
        "era": "掩体纪元",
        "year": 67,
        "title": "二向箔清理",
        "content": "人类以光粒为假想敌，在木星等巨行星背后建掩体城。歌者从猎户旋臂外侧投掷二向箔——封装二维空间的薄片。二向箔展开后太阳系开始不可逆地向二维跌落，三维结构在平面中崩解。掩体计划无法防御维度打击。",
        "summary": "歌者投掷二向箔；太阳系开始二维化。",
        "image_url": "https://picsum.photos/seed/dualvector/600/400",
        "event_type": "official",
        "causality_status": "collapsed"
    },
    {
        "era": "掩体纪元",
        "year": 67,
        "title": "冥王星的最后逃亡",
        "content": "程心与艾 AA 乘人类唯一光速飞船“星环”号逃离。罗辑选择留在冥王星地球文明博物馆，与保存人类记忆的墓碑一同二维化。“把字刻在石头上。”太阳系最终化为巨大二维画卷，所有生命与文明凝固其中。",
        "summary": "程心乘星环号逃离；罗辑留守冥王星并二维化。",
        "image_url": "https://picsum.photos/seed/pluto2d/600/400",
        "event_type": "official",
        "causality_status": "collapsed"
    },

    # --- 银河纪元 (Galaxy Era) ---
    {
        "era": "银河纪元",
        "year": 409,
        "title": "小宇宙 No.647",
        "content": "云天明将小宇宙 No.647 赠予程心与关一帆。二人进入后时间几近停滞，在其中度过相当于大宇宙亿万年的岁月。647 号是独立于大宇宙的封闭时空，直至收到归零者的全宇宙广播：“请把质量归还。”",
        "summary": "程心与关一帆进入 647 号小宇宙；收到归零者广播。",
        "image_url": "https://picsum.photos/seed/universe647/600/400",
        "event_type": "official",
        "causality_status": "collapsed"
    },
    {
        "era": "银河纪元",
        "year": 409,
        "title": "回归运动",
        "content": "归零者呼吁所有小宇宙归还质量以使大宇宙能坍缩重启。程心决定响应，留下约五公斤生态球（含鱼与记忆）后，将 647 号小宇宙其余质量归还大宇宙。二人走出小宇宙，无论宇宙是否重启，皆为责任的终点。",
        "summary": "程心归还小宇宙质量；走出 647 号，回归运动完成。",
        "image_url": "https://picsum.photos/seed/returnmass/600/400",
        "event_type": "official",
        "causality_status": "collapsed"
    },

    # --- 乱纪元 (Sector T) ---
    {
        "era": "乱纪元",
        "year": 184,
        "title": "三日连珠与 184 号文明毁灭",
        "content": "三体世界第 184 次轮回中，三颗飞星连珠导致引力叠加，地表撕裂，文明毁灭。该事件被记录为三体问题的典型灾难之一；文明在乱纪元中反复脱水与复活，直至下一次恒纪元或下一次毁灭。",
        "summary": "三日连珠导致 184 号文明毁灭；乱纪元典型灾难。",
        "image_url": "https://picsum.photos/seed/triplesun/600/400",
        "event_type": "official",
        "causality_status": "collapsed"
    },
    {
        "era": "乱纪元",
        "year": 471,
        "title": "双日凌空下的最后一次脱水",
        "content": "三体单摆系统在运行周期 t=2.4×10^5 时捕获第三颗恒星非线性摄动。引力异常致大气剥离 34%，地表温度 120 秒内跃至 400℃。第 191 号文明放弃人列计算机，全员脱水；干纤维在“大撕裂”中被抛入太空，成为第 192 号文明眼中的有机尘埃带。",
        "summary": "双日凌空；191 号文明脱水毁灭，有机尘埃带形成。",
        "image_url": "https://picsum.photos/seed/dehydration/600/400",
        "event_type": "official",
        "causality_status": "collapsed"
    }
]

async def seed():
    async with AsyncSessionLocal() as session:
        from sqlalchemy import select
        for data in CHRONICLES:
            result = await session.execute(select(ChronicleEventORM).where(ChronicleEventORM.title == data["title"]))
            existing = result.scalar_one_or_none()
            if existing:
                print(f"Updating {data['title']}...")
                existing.content = data["content"]
                existing.summary = data["summary"]
                existing.year = data["year"]
                existing.era = data["era"]
                existing.image_url = data["image_url"]
            else:
                print(f"Adding {data['title']}...")
                row = ChronicleEventORM(**data)
                session.add(row)
        await session.commit()
    print("Chronicle seed complete. Total:", len(CHRONICLES))

if __name__ == "__main__":
    asyncio.run(seed())
