"""Seed initial figures data."""
import asyncio
import json
import re
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from backend.database import AsyncSessionLocal
from backend.models.figures import FigureORM

# 人物专属头像：按性别选用 DiceBear 风格（女=lorelei，男=adventurer，其他=notionists）
FIGURES_AVATAR_OPTIONS = {
    "female": "https://api.dicebear.com/7.x/lorelei/png",
    "male": "https://api.dicebear.com/7.x/adventurer/png",
    "other": "https://api.dicebear.com/7.x/notionists/png",
}

# 人物性别映射（用于生成符合性别的头像）
FIGURE_GENDERS = {
    "罗辑": "male", "叶文洁": "female", "章北海": "male", "程心": "female", "托马斯·维德": "male",
    "守摆人 (Pendulum-001)": "male", "史强": "male", "汪淼": "male", "丁仪": "male", "杨冬": "female",
    "麦克·伊文斯": "male", "申玉菲": "female", "常伟思": "male", "雷迪亚兹": "male",
    "弗里德里克·泰勒": "male", "比尔·希恩斯": "male", "萨伊": "female", "庄颜": "female",
    "云天明": "male", "艾 AA": "female", "关一帆": "male", "智子 (仿生人)": "female",
    "歌者": "male", "褚岩": "male", "东方延绪": "female", "1379号监听员": "male",
    "魏成": "male", "潘寒": "male", "叶哲泰": "male", "杨卫宁": "male", "雷志成": "male",
    "山杉惠子": "female", "白蓉": "female", "弗雷斯": "male", "吴岳": "male", "毕云峰": "male",
    "林格": "male", "斐兹罗": "male", "伽尔宁": "male", "坎特": "male", "斯坦顿": "male",
    "曹彬": "male", "高 Way": "male", "三体元首": "other", "邵琳": "female", "白沐霖": "male",
    "沙瑞山": "male", "徐冰冰": "female", "唐红静": "female", "破壁人一号": "male",
    "破壁人二号": "male", "破壁人三号": "female", "乔纳森": "male", "张援朝": "male",
    "杨晋文": "male", "苗福全": "male", "斯科特": "male", "莫沃维奇": "male", "井上明": "male",
    "朴义君": "male", "李医生": "male", "长老": "other", "归零者": "other", "亨特": "male",
    "戴文": "male", "拉菲尔": "male", "奈尔·威廉斯": "male", "杰拉德": "male",
    # 三体游戏中人物（原著明确出现）
    "周文王": "male", "墨子": "male", "冯·诺依曼": "male", "秦始皇": "male",
    "哥白尼": "male", "爱因斯坦": "male", "牛顿": "male", "亚里士多德": "male",
    "纣王": "male", "伽利略": "male",
    # 原著中提及的真实人物
    "霍金": "male",
}


def get_figure_avatar_url(figure: dict) -> str:
    """按人物性别生成对应风格的头像 URL（同一姓名始终得到同一头像）。"""
    raw = (figure.get("en_name") or figure["name"]).strip()
    seed = re.sub(r"[^\w\u4e00-\u9fff]", "", raw) or "figure"
    if not seed.encode("ascii", "ignore").decode().strip():
        seed = "".join(str(ord(c)) for c in raw[:4])
    gender = figure.get("gender") or FIGURE_GENDERS.get(figure["name"], "other")
    base = FIGURES_AVATAR_OPTIONS.get(gender, FIGURES_AVATAR_OPTIONS["other"])
    return f"{base}?seed={seed}&size=300&backgroundColor=0d1b2a"

# 智子档案库：关键人物（含三体游戏中角色与原著提及人物）
FIGURES = [
    # --- 原有核心人物 (Updated/Kept) ---
    {
        "name": "罗辑",
        "en_name": "Luo Ji",
        "role": "面壁者 / 执剑人",
        "era": "危机纪元",
        "status": "hibernating",
        "description": "天文学家，社会学家。第四位面壁者，黑暗森林理论的创立者，第一代执剑人。他以玩世不恭的伪装欺骗了整个世界，最终建立了对三体世界的威慑。在冥王星的守望中，他成为了人类最后的守墓人。",
        "image_url": "https://placehold.co/300x400/000/fff?text=Luo+Ji",
        "quotes": "“我对三体世界说话。”\n“这是计划的一部分。”",
        "logic_score": 0.99,
        "metrics": '{"alienation": 95, "deterrence": 100, "empathy": 20, "rationality": 95}',
        "key_events": '[{"role": "trigger", "impact_description": "建立黑暗森林威慑"}, {"role": "guardian", "impact_description": "担任执剑人54年"}]'
    },
    {
        "name": "叶文洁",
        "en_name": "Ye Wenjie",
        "role": "ETO统帅",
        "era": "黄金时代",
        "status": "deceased",
        "description": "天体物理学家，ETO 精神领袖。她在红岸基地向宇宙发送了第一条包含人类文明信息的信息，引来了三体舰队。她的绝望开启了人类的危机，也开启了人类的觉醒。",
        "image_url": "https://placehold.co/300x400/000/fff?text=Ye+Wenjie",
        "quotes": "“到这里来吧，我将帮助你们获得这个世界。”\n“消灭人类暴政，世界属于三体。”",
        "logic_score": 0.95,
        "metrics": '{"alienation": 80, "deterrence": 60, "empathy": 10, "rationality": 90}',
        "key_events": '[{"role": "trigger", "impact_description": "向三体发射信号"}, {"role": "mentor", "impact_description": "向罗辑提示公理"}]'
    },
    {
        "name": "章北海",
        "en_name": "Zhang Beihai",
        "role": "太空军",
        "era": "危机纪元",
        "status": "deceased",
        "description": "太空军政治部主任，坚定的失败主义者（伪装成胜利主义者）。他通过暗杀推动了无工质辐射驱动引擎的发展，并在末日之战前劫持“自然选择”号逃离，为人类保留了火种。他的目光穿越了几个世纪。",
        "image_url": "https://placehold.co/300x400/000/fff?text=Zhang+Beihai",
        "quotes": "“自然选择，前进四！”\n“没关系的，都一样。”",
        "logic_score": 0.98,
        "metrics": '{"alienation": 90, "deterrence": 70, "empathy": 30, "rationality": 100}',
        "key_events": '[{"role": "trigger", "impact_description": "劫持自然选择号"}, {"role": "executor", "impact_description": "刺杀老航天"}]'
    },
    {
        "name": "程心",
        "en_name": "Cheng Xin",
        "role": "执剑人",
        "era": "威慑纪元",
        "status": "active",
        "description": "航天发动机专业博士，第二代执剑人。她的爱与仁慈最终导致了威慑系统的失效和地球的沦陷，但她也一次次在绝境中幸存。她是圣母，也是死神。",
        "image_url": "https://placehold.co/300x400/000/fff?text=Cheng+Xin",
        "quotes": "“我选择爱。”",
        "logic_score": 0.3,
        "metrics": '{"alienation": 5, "deterrence": 0, "empathy": 100, "rationality": 15}',
        "key_events": '[{"role": "victim", "impact_description": "威慑失败"}, {"role": "survivor", "impact_description": "逃离二向箔"}]'
    },
    {
        "name": "托马斯·维德",
        "en_name": "Thomas Wade",
        "role": "PIA局长",
        "era": "危机纪元",
        "status": "deceased",
        "description": "PIA 首任局长，阶梯计划提议者。他冷酷无情，为了前进不择手段，坚信“失去人性，失去很多；失去兽性，失去一切”。如果让他执剑，三体人绝不敢动。",
        "image_url": "https://placehold.co/300x400/000/fff?text=Wade",
        "quotes": "“前进！前进！！不择手段地前进！！！”",
        "logic_score": 0.97,
        "metrics": '{"alienation": 95, "deterrence": 100, "empathy": 0, "rationality": 100}',
        "key_events": '[{"role": "trigger", "impact_description": "研制光速飞船"}, {"role": "executor", "impact_description": "阶梯计划"}]'
    },
    {
        "name": "守摆人 (Pendulum-001)",
        "en_name": "The Pendulum Keeper",
        "role": "观测者",
        "era": "乱纪元 471年",
        "status": "deceased",
        "description": "【零点计划原创】他拥有全文明最稳健的一双手。在双日凌空的烈焰即将吞噬大地的前一刻，他没有选择脱水，而是将自己锁死在三体摆的底座上。他用烧焦的视网膜记录下最后一次单摆的周期——那是证明这个文明曾经试图解析宇宙规律的唯一证据。",
        "image_url": "https://placehold.co/300x400/000/fff?text=Pendulum+Keeper",
        "quotes": "“眼睛里没有恐惧，只有波长 450nm 的冷光。”",
        "logic_score": 0.0,
        "metrics": '{"alienation": 100, "deterrence": 0, "empathy": 0, "rationality": 100}',
        "key_events": '[{"role": "observer", "impact_description": "记录最后一次单摆周期"}]'
    },

    # --- 新增人物 (Book 1: Three Body) ---
    {
        "name": "史强",
        "en_name": "Shi Qiang (Da Shi)",
        "role": "前警官 / 地球防务",
        "era": "危机纪元",
        "status": "deceased",
        "description": "粗俗但极其敏锐的观察者。他不相信任何理论，只相信直觉和经验。他是罗辑的守护天使，也是在这个疯狂世界中唯一能让人感到踏实的锚点。在乱纪元里，他的眼睛比任何望远镜都锋利。",
        "image_url": "https://placehold.co/300x400/000/fff?text=Da+Shi",
        "quotes": "“邪乎到家必有鬼。”\n“虫子从来没有被真正战胜过。”",
        "logic_score": 0.85,
        "metrics": '{"alienation": 20, "deterrence": 60, "empathy": 80, "rationality": 70}',
        "key_events": '[{"role": "protector", "impact_description": "古筝行动执行"}, {"role": "guide", "impact_description": "唤醒罗辑"}]'
    },
    {
        "name": "汪淼",
        "en_name": "Wang Miao",
        "role": "纳米科学家",
        "era": "黄金时代",
        "status": "deceased",
        "description": "应用物理学家，“古筝行动”的执行者。他的视网膜上曾倒计时着人类文明的终点，但他最终用纳米飞刃切开了“审判日”号，为人类获取了三体文明的第一手资料。",
        "image_url": "https://placehold.co/300x400/000/fff?text=Wang+Miao",
        "quotes": "“倒计时的尽头是什么？”",
        "logic_score": 0.88,
        "metrics": '{"alienation": 40, "deterrence": 50, "empathy": 60, "rationality": 95}',
        "key_events": '[{"role": "executor", "impact_description": "古筝行动"}, {"role": "observer", "impact_description": "见证宇宙闪烁"}]'
    },
    {
        "name": "丁仪",
        "en_name": "Ding Yi",
        "role": "理论物理学家",
        "era": "危机纪元",
        "status": "deceased",
        "description": "物理学天才。他在最后时刻看透了“水滴”的本质，用生命验证了宇宙的残酷公理——毁灭你，与你何干。他是那个时代最清醒的醉鬼。",
        "image_url": "https://placehold.co/300x400/000/fff?text=Ding+Yi",
        "quotes": "“傻孩子们，快跑啊！”\n“物理学不存在了？不，它只是更残酷了。”",
        "logic_score": 0.96,
        "metrics": '{"alienation": 80, "deterrence": 0, "empathy": 40, "rationality": 100}',
        "key_events": '[{"role": "victim", "impact_description": "接触水滴"}, {"role": "pioneer", "impact_description": "可控核聚变"}]'
    },
    {
        "name": "杨冬",
        "en_name": "Yang Dong",
        "role": "理论物理学家",
        "era": "黄金时代",
        "status": "deceased",
        "description": "叶文洁之女。当她发现物理学不存在，而母亲是这一切的推手时，她的世界崩塌了。她是这一连串多米诺骨牌倒下的第一块，也是最安静的一块。",
        "image_url": "https://placehold.co/300x400/000/fff?text=Yang+Dong",
        "quotes": "“物理学……不存在了。”",
        "logic_score": 0.90,
        "metrics": '{"alienation": 90, "deterrence": 0, "empathy": 20, "rationality": 90}',
        "key_events": '[{"role": "trigger", "impact_description": "自杀引发汪淼调查"}]'
    },
    {
        "name": "麦克·伊文斯",
        "en_name": "Mike Evans",
        "role": "ETO 资助者",
        "era": "黄金时代",
        "status": "deceased",
        "description": "物种共产主义者，ETO 的核心金主。他试图通过引入外星文明来拯救地球生态，却最终死于自己引来的纳米飞刃之下。他用巨额财富为人类买来了一张末日门票。",
        "image_url": "https://placehold.co/300x400/000/fff?text=Evans",
        "quotes": "“主，我们是同志了。”",
        "logic_score": 0.40,
        "metrics": '{"alienation": 90, "deterrence": 10, "empathy": 5, "rationality": 30}',
        "key_events": '[{"role": "traitor", "impact_description": "建立第二红岸基地"}]'
    },
    {
        "name": "申玉菲",
        "en_name": "Shen Yufei",
        "role": "科学边界成员",
        "era": "黄金时代",
        "status": "deceased",
        "description": "冷酷的物理学家，试图通过解决三体问题来拯救主。她的一生都在寻找那个不存在的数学解，最终倒在了这种徒劳的执着中。",
        "image_url": "https://placehold.co/300x400/000/fff?text=Shen+Yufei",
        "quotes": "“佛祖保佑，我主脱离苦海。”",
        "logic_score": 0.92,
        "metrics": '{"alienation": 90, "deterrence": 0, "empathy": 10, "rationality": 98}',
        "key_events": '[{"role": "messenger", "impact_description": "引导汪淼进入游戏"}]'
    },
    {
        "name": "常伟思",
        "en_name": "Chang Weisi",
        "role": "太空军司令",
        "era": "危机纪元",
        "status": "deceased",
        "description": "坚定的军人，古筝行动的指挥官。他在绝望中建立了太空军的雏形，尽管他知道这场战争在物理学锁死的那一刻就已经输了。",
        "image_url": "https://placehold.co/300x400/000/fff?text=Chang+Weisi",
        "quotes": "“整个人类历史也是偶然，从石器时代到今天，都没什么重大变故，真幸运。”",
        "logic_score": 0.85,
        "metrics": '{"alienation": 30, "deterrence": 50, "empathy": 50, "rationality": 80}',
        "key_events": '[{"role": "commander", "impact_description": "组建太空军"}]'
    },

    # --- 新增人物 (Book 2: The Dark Forest) ---
    {
        "name": "雷迪亚兹",
        "en_name": "Manuel Rey Diaz",
        "role": "面壁者",
        "era": "危机纪元",
        "status": "deceased",
        "description": "委内瑞拉总统，核威慑的狂热信徒。他试图用恒星级氢弹以此要挟三体人，哪怕代价是毁灭地球。这种疯狂让他成为了最接近成功但也最悲剧的面壁者之一。",
        "image_url": "https://placehold.co/300x400/000/fff?text=Rey+Diaz",
        "quotes": "“我要让太阳不再升起。”",
        "logic_score": 0.80,
        "metrics": '{"alienation": 85, "deterrence": 90, "empathy": 10, "rationality": 60}',
        "key_events": '[{"role": "planner", "impact_description": "摇篮计划（恒星级氢弹）"}]'
    },
    {
        "name": "弗里德里克·泰勒",
        "en_name": "Frederick Tyler",
        "role": "面壁者",
        "era": "危机纪元",
        "status": "deceased",
        "description": "前美国国防部长。他的计划是建立一支蚊群般的敢死队去背叛人类，这种复杂的双重背叛逻辑最终被破壁人识破，导致了他的自杀。",
        "image_url": "https://placehold.co/300x400/000/fff?text=Tyler",
        "quotes": "“妈妈，我将变成萤火虫。”",
        "logic_score": 0.70,
        "metrics": '{"alienation": 60, "deterrence": 20, "empathy": 30, "rationality": 60}',
        "key_events": '[{"role": "planner", "impact_description": "蚊群计划"}]'
    },
    {
        "name": "比尔·希恩斯",
        "en_name": "Bill Hines",
        "role": "面壁者",
        "era": "危机纪元",
        "status": "deceased",
        "description": "脑科学家。他表面上寻找提升人类智力的途径，实则植入了绝对的失败主义——“思想钢印”。他是唯一一个在此维度上战胜了智子的面壁者，虽然是向着逃亡的方向。",
        "image_url": "https://placehold.co/300x400/000/fff?text=Hines",
        "quotes": "“水有毒。”",
        "logic_score": 0.90,
        "metrics": '{"alienation": 70, "deterrence": 0, "empathy": 40, "rationality": 90}',
        "key_events": '[{"role": "planner", "impact_description": "思想钢印计划"}]'
    },
    {
        "name": "萨伊",
        "en_name": "Say",
        "role": "联合国秘书长",
        "era": "危机纪元",
        "status": "deceased",
        "description": "面壁计划的启动者。她以政治家的魄力推动了人类历史上最疯狂的赌博，她是那个时代真正的舵手。",
        "image_url": "https://placehold.co/300x400/000/fff?text=Say",
        "quotes": "“面壁者，请开始你的工作。”",
        "logic_score": 0.85,
        "metrics": '{"alienation": 40, "deterrence": 60, "empathy": 50, "rationality": 85}',
        "key_events": '[{"role": "initiator", "impact_description": "启动面壁计划"}]'
    },
    {
        "name": "庄颜",
        "en_name": "Zhuang Yan",
        "role": "罗辑之妻",
        "era": "危机纪元",
        "status": "hibernating",
        "description": "罗辑梦中的女孩，被面壁计划具象化到现实。她是罗辑建立威慑的唯一锚点，是连接神性与人性的脆弱纽带。",
        "image_url": "https://placehold.co/300x400/000/fff?text=Zhuang+Yan",
        "quotes": "“带我们回家。”",
        "logic_score": 0.30,
        "metrics": '{"alienation": 10, "deterrence": 0, "empathy": 100, "rationality": 20}',
        "key_events": '[{"role": "muse", "impact_description": "成为罗辑的人质"}]'
    },

    # --- 新增人物 (Book 3: Death's End) ---
    {
        "name": "云天明",
        "en_name": "Yun Tianming",
        "role": "阶梯计划执行人",
        "era": "银河纪元",
        "status": "active",
        "description": "一个身患绝症的孤僻大脑，被送往三体舰队。他在地狱中度过了几个世纪，最终通过三个童话向人类传递了生存的密码。他送给程心一个宇宙，却永远错过了她。",
        "image_url": "https://placehold.co/300x400/000/fff?text=Yun+Tianming",
        "quotes": "“来了，爱了，送给她一颗星星，走了。”",
        "logic_score": 0.99,
        "metrics": '{"alienation": 100, "deterrence": 0, "empathy": 100, "rationality": 100}',
        "key_events": '[{"role": "messenger", "impact_description": "传递三个童话"}, {"role": "donor", "impact_description": "送出647号小宇宙"}]'
    },
    {
        "name": "艾 AA",
        "en_name": "Ai AA",
        "role": "程心助理",
        "era": "银河纪元",
        "status": "deceased",
        "description": "新人类的代表，热情、直率、理性。她在关键时刻总是比程心更果断，但命运让她陪伴云天明度过了余生，在石头上刻下了文明的墓碑。",
        "image_url": "https://placehold.co/300x400/000/fff?text=AA",
        "quotes": "“我们要活下去，这才是对爱最好的纪念。”",
        "logic_score": 0.88,
        "metrics": '{"alienation": 30, "deterrence": 10, "empathy": 80, "rationality": 80}',
        "key_events": '[{"role": "companion", "impact_description": "发现二维化迹象"}]'
    },
    {
        "name": "关一帆",
        "en_name": "Guan Yifan",
        "role": "宇宙学家",
        "era": "银河纪元",
        "status": "active",
        "description": "深刻理解黑暗森林法则的学者。他揭示了宇宙降维的真相，是程心最后的守护者。在光速飞船的尾迹中，他见证了死神永生。",
        "image_url": "https://placehold.co/300x400/000/fff?text=Guan+Yifan",
        "quotes": "“在宇宙中，你再快都有比你更快的，你再慢也有比你更慢的。”",
        "logic_score": 0.96,
        "metrics": '{"alienation": 80, "deterrence": 0, "empathy": 50, "rationality": 95}',
        "key_events": '[{"role": "discoverer", "impact_description": "研究黑域与死线"}]'
    },
    {
        "name": "智子 (仿生人)",
        "en_name": "Sophon Android",
        "role": "三体大使",
        "era": "广播纪元",
        "status": "active",
        "description": "三体意志的低维展开。平时是穿和服的优雅女性，挥刀时则是冷酷的屠杀机器。她是两个文明间最危险的信使，也是最后送别人类的礼仪官。",
        "image_url": "https://placehold.co/300x400/000/fff?text=Sophon",
        "quotes": "“你们是虫子。”\n“请享用茶点。”",
        "logic_score": 1.0,
        "metrics": '{"alienation": 100, "deterrence": 100, "empathy": 0, "rationality": 100}',
        "key_events": '[{"role": "envoy", "impact_description": "宣布澳大利亚保留地"}]'
    },
    {
        "name": "歌者",
        "en_name": "Singer",
        "role": "宇宙清理工",
        "era": "广播纪元",
        "status": "active",
        "description": "高级文明的底层职员。清理对于他来说只是日常工作，随手扔出的一片二向箔，就将太阳系压成了一幅画。他甚至没有费心去记下这个星系的坐标。",
        "image_url": "https://placehold.co/300x400/000/fff?text=Singer",
        "quotes": "“藏好自己，做好清理。”",
        "logic_score": 1.0,
        "metrics": '{"alienation": 100, "deterrence": 100, "empathy": 0, "rationality": 100}',
        "key_events": '[{"role": "destroyer", "impact_description": "投掷二向箔"}]'
    },
    {
        "name": "褚岩",
        "en_name": "Chu Yan",
        "role": "蓝色空间号舰长",
        "era": "银河纪元",
        "status": "active",
        "description": "人类中最坚韧的星舰舰长之一。他带领蓝色空间号在黑暗森林中进化出了真正的宇宙文明形态，率先对追击者发起了四维打击。他是新人类的亚当。",
        "image_url": "https://placehold.co/300x400/000/fff?text=Chu+Yan",
        "quotes": "“不管去哪里，都是在这个宇宙中。”",
        "logic_score": 0.98,
        "metrics": '{"alienation": 90, "deterrence": 80, "empathy": 20, "rationality": 95}',
        "key_events": '[{"role": "commander", "impact_description": "四维空间打击万有引力号"}]'
    },
    {
        "name": "东方延绪",
        "en_name": "Dongfang Yanxu",
        "role": "自然选择号舰长",
        "era": "危机纪元",
        "status": "deceased",
        "description": "太空军新生代的杰出代表。她对章北海的警惕最终没能阻止星舰的逃亡，但她的牺牲成为了人类在太空生存的第一课。",
        "image_url": "https://placehold.co/300x400/000/fff?text=Dongfang",
        "quotes": "“自然选择，前进四！”",
        "logic_score": 0.85,
        "metrics": '{"alienation": 50, "deterrence": 40, "empathy": 60, "rationality": 80}',
        "key_events": '[{"role": "victim", "impact_description": "黑暗森林战役"}]'
    },
    {
        "name": "1379号监听员",
        "en_name": "Listener 1379",
        "role": "三体和平主义者",
        "era": "黄金时代",
        "status": "deceased",
        "description": "三体世界中唯一的和平主义者。他向宇宙发出了“不要回答”的警告，以此换取自己短暂的审判与处决。他是三体世界中唯一闪烁过的人性光辉。",
        "image_url": "https://placehold.co/300x400/000/fff?text=1379",
        "quotes": "“不要回答！不要回答！不要回答！”",
        "logic_score": 0.2,
        "metrics": '{"alienation": 90, "deterrence": 0, "empathy": 100, "rationality": 10}',
        "key_events": '[{"role": "savior", "impact_description": "警告地球不要回答"}]'
    },
    {
        "name": "魏成",
        "en_name": "Wei Cheng",
        "role": "数学家",
        "era": "黄金时代",
        "status": "unknown",
        "description": "他的眼中只有几何形状和函数。他无意中触碰到了三体运动的混沌本质，却不知道这背后代表着两个文明的生死存亡。",
        "image_url": "https://placehold.co/300x400/000/fff?text=Wei+Cheng",
        "quotes": "“我能证明三体问题无解。”",
        "logic_score": 0.95,
        "metrics": '{"alienation": 95, "deterrence": 0, "empathy": 5, "rationality": 100}',
        "key_events": '[{"role": "solver", "impact_description": "提出三体问题进化算法"}]'
    },
    {
        "name": "潘寒",
        "en_name": "Pan Han",
        "role": "降临派核心",
        "era": "黄金时代",
        "status": "deceased",
        "description": "激进的环保主义者，认为科技是病态的。他在ETO内部斗争中因背叛原则被核对杀死，是混乱邪恶的典型代表。",
        "image_url": "https://placehold.co/300x400/000/fff?text=Pan+Han",
        "quotes": "“科技是人类的毒瘤。”",
        "logic_score": 0.60,
        "metrics": '{"alienation": 80, "deterrence": 30, "empathy": 20, "rationality": 50}',
        "key_events": '[{"role": "villain", "impact_description": "暗杀申玉菲"}]'
    },

    # --- 红岸与黄金时代 ---
    {
        "name": "叶哲泰",
        "en_name": "Ye Zhetai",
        "role": "理论物理学家",
        "era": "黄金时代",
        "status": "deceased",
        "description": "叶文洁之父，清华大学物理学教授。在批斗中因坚持「科学没有阶级性」被红卫兵打死。他的死是叶文洁对人类文明绝望的起点。",
        "image_url": "https://placehold.co/300x400/000/fff?text=Ye+Zhetai",
        "quotes": "“科学没有阶级性。”",
        "logic_score": 0.88,
        "metrics": '{"alienation": 50, "deterrence": 0, "empathy": 60, "rationality": 95}',
        "key_events": '[{"role": "victim", "impact_description": "批斗中死亡，促成叶文洁转向"}]'
    },
    {
        "name": "杨卫宁",
        "en_name": "Yang Weining",
        "role": "红岸基地总工程师",
        "era": "黄金时代",
        "status": "deceased",
        "description": "叶文洁的丈夫，红岸基地技术负责人。他将叶文洁带入红岸，又在雷志成与叶文洁之间成为牺牲品——叶文洁割断绳索时他随雷志成一同坠崖。",
        "image_url": "https://placehold.co/300x400/000/fff?text=Yang+Weining",
        "quotes": "“文洁，这里需要你。”",
        "logic_score": 0.75,
        "metrics": '{"alienation": 20, "deterrence": 0, "empathy": 70, "rationality": 85}',
        "key_events": '[{"role": "bridge", "impact_description": "将叶文洁带入红岸"}, {"role": "victim", "impact_description": "死于红岸悬崖"}]'
    },
    {
        "name": "雷志成",
        "en_name": "Lei Zhicheng",
        "role": "红岸基地政委",
        "era": "黄金时代",
        "status": "deceased",
        "description": "红岸基地政委，发现叶文洁与地外文明接触后意图上报。叶文洁在检修时割断其与杨卫宁的绳索，二人坠崖身亡。",
        "image_url": "https://placehold.co/300x400/000/fff?text=Lei+Zhicheng",
        "quotes": "“你收到了什么？”",
        "logic_score": 0.70,
        "metrics": '{"alienation": 40, "deterrence": 30, "empathy": 30, "rationality": 75}',
        "key_events": '[{"role": "threat", "impact_description": "发现三体回复，被叶文洁杀害"}]'
    },
    {
        "name": "山杉惠子",
        "en_name": "Yamamura Keiko",
        "role": "破壁人二号",
        "era": "危机纪元",
        "status": "deceased",
        "description": "比尔·希恩斯的妻子，表面上的胜利主义者，实为希恩斯的破壁人。她在听证会上揭穿丈夫的思想钢印计划，并当众自杀。",
        "image_url": "https://placehold.co/300x400/000/fff?text=Keiko",
        "quotes": "“我破壁了，比尔。”",
        "logic_score": 0.93,
        "metrics": '{"alienation": 85, "deterrence": 20, "empathy": 30, "rationality": 95}',
        "key_events": '[{"role": "breaker", "impact_description": "破壁希恩斯"}, {"role": "martyr", "impact_description": "破壁后自杀"}]'
    },
    {
        "name": "白蓉",
        "en_name": "Bai Rong",
        "role": "作家",
        "era": "危机纪元",
        "status": "unknown",
        "description": "罗辑的前女友，作家。她让罗辑在脑海中构建完美恋人的形象，这一经历成为面壁计划为罗辑「制造」庄颜的心理学基础。",
        "image_url": "https://placehold.co/300x400/000/fff?text=Bai+Rong",
        "quotes": "“你心里要有一个她。”",
        "logic_score": 0.50,
        "metrics": '{"alienation": 30, "deterrence": 0, "empathy": 80, "rationality": 60}',
        "key_events": '[{"role": "muse", "impact_description": "罗辑梦中情人概念的来源"}]'
    },
    {
        "name": "弗雷斯",
        "en_name": "Frederick",
        "role": "澳大利亚土著长老",
        "era": "威慑纪元",
        "status": "deceased",
        "description": "程心在澳大利亚保留地遇到的土著老人。他的土地被征用安置地球人，他平静地接受命运，并告诉程心：「姑娘，这是战争。」",
        "image_url": "https://placehold.co/300x400/000/fff?text=Frederick",
        "quotes": "“姑娘，这是战争。”",
        "logic_score": 0.82,
        "metrics": '{"alienation": 40, "deterrence": 0, "empathy": 70, "rationality": 85}',
        "key_events": '[{"role": "witness", "impact_description": "保留地人性见证"}]'
    },

    # --- 太空军与舰队 ---
    {
        "name": "吴岳",
        "en_name": "Wu Yue",
        "role": "海军军官",
        "era": "危机纪元",
        "status": "deceased",
        "description": "章北海的战友，失败主义者。他在太空军成立前夕选择退役，与章北海形成对照——一个选择离开，一个选择留下并行动。",
        "image_url": "https://placehold.co/300x400/000/fff?text=Wu+Yue",
        "quotes": "“我们必败。”",
        "logic_score": 0.78,
        "metrics": '{"alienation": 70, "deterrence": 0, "empathy": 50, "rationality": 90}',
        "key_events": '[{"role": "resigner", "impact_description": "太空军成立前退役"}]'
    },
    {
        "name": "毕云峰",
        "en_name": "Bi Yunfeng",
        "role": "航天系统专家",
        "era": "危机纪元",
        "status": "deceased",
        "description": "坚持化学推进路线的老航天代表之一。章北海为推进无工质发动机研发，制造陨石袭击假象，毕云峰等成为牺牲品。",
        "image_url": "https://placehold.co/300x400/000/fff?text=Bi+Yunfeng",
        "quotes": "“工质推进才是可靠路线。”",
        "logic_score": 0.72,
        "metrics": '{"alienation": 30, "deterrence": 20, "empathy": 50, "rationality": 75}',
        "key_events": '[{"role": "victim", "impact_description": "章北海推动无工质研发的牺牲者"}]'
    },
    {
        "name": "林格",
        "en_name": "Lin Ge",
        "role": "天文学家",
        "era": "危机纪元",
        "status": "deceased",
        "description": "斐兹罗将军的顾问，负责观测三体舰队。正是他在哈勃二号望远镜上首次观察到三体舰队穿越尘埃云的痕迹，证实了入侵的真实性。",
        "image_url": "https://placehold.co/300x400/000/fff?text=Lin+Ge",
        "quotes": "“将军，他们来了。”",
        "logic_score": 0.85,
        "metrics": '{"alienation": 40, "deterrence": 0, "empathy": 40, "rationality": 95}',
        "key_events": '[{"role": "observer", "impact_description": "观测到三体舰队"}]'
    },
    {
        "name": "斐兹罗",
        "en_name": "Fitzroy",
        "role": "将军",
        "era": "危机纪元",
        "status": "deceased",
        "description": "负责太空观测的将军，林格的上司。三体舰队痕迹被确认后，他代表军方将这一消息带给决策层与面壁者。",
        "image_url": "https://placehold.co/300x400/000/fff?text=Fitzroy",
        "quotes": "“让哈勃二号对准那片区域。”",
        "logic_score": 0.80,
        "metrics": '{"alienation": 35, "deterrence": 50, "empathy": 40, "rationality": 85}',
        "key_events": '[{"role": "commander", "impact_description": "主持三体舰队观测"}]'
    },

    # --- PDC 与面壁计划相关 ---
    {
        "name": "伽尔宁",
        "en_name": "Garin",
        "role": "PDC 轮值主席",
        "era": "危机纪元",
        "status": "deceased",
        "description": "面壁计划时期的 PDC 轮值主席之一。曾主持面壁者听证会，与萨伊等共同维系着人类对抗三体的指挥体系。",
        "image_url": "https://placehold.co/300x400/000/fff?text=Garin",
        "quotes": "“面壁者拥有调用资源的权力。”",
        "logic_score": 0.82,
        "metrics": '{"alienation": 45, "deterrence": 55, "empathy": 45, "rationality": 85}',
        "key_events": '[{"role": "administrator", "impact_description": "面壁计划行政协调"}]'
    },
    {
        "name": "坎特",
        "en_name": "Kant",
        "role": "罗辑联络员",
        "era": "危机纪元",
        "status": "unknown",
        "description": "PDC 指派给罗辑的联络官。负责在罗辑「不作为」期间与联合国沟通，并执行对罗辑的保护与监控。",
        "image_url": "https://placehold.co/300x400/000/fff?text=Kant",
        "quotes": "“罗辑博士，这是计划的一部分吗？”",
        "logic_score": 0.75,
        "metrics": '{"alienation": 35, "deterrence": 20, "empathy": 50, "rationality": 80}',
        "key_events": '[{"role": "liaison", "impact_description": "罗辑与 PDC 的桥梁"}]'
    },
    {
        "name": "斯坦顿",
        "en_name": "Stanton",
        "role": "美军将领",
        "era": "危机纪元",
        "status": "deceased",
        "description": "古筝行动的美方军事负责人。与常伟思、史强等协调，在巴拿马运河执行飞刃切割审判日号的行动。",
        "image_url": "https://placehold.co/300x400/000/fff?text=Stanton",
        "quotes": "“让船通过，然后收网。”",
        "logic_score": 0.83,
        "metrics": '{"alienation": 40, "deterrence": 70, "empathy": 30, "rationality": 88}',
        "key_events": '[{"role": "executor", "impact_description": "古筝行动军事协调"}]'
    },

    # --- 广播纪元与掩体纪元 ---
    {
        "name": "曹彬",
        "en_name": "Cao Bin",
        "role": "物理学家",
        "era": "广播纪元",
        "status": "unknown",
        "description": "程心时代的物理学家，参与曲率驱动与黑域研究。曾向程心解释云天明的童话与光速航迹、黑域之间的关联。",
        "image_url": "https://placehold.co/300x400/000/fff?text=Cao+Bin",
        "quotes": "“童话里有答案。”",
        "logic_score": 0.90,
        "metrics": '{"alienation": 50, "deterrence": 0, "empathy": 50, "rationality": 95}',
        "key_events": '[{"role": "interpreter", "impact_description": "解读云天明童话的技术隐喻"}]'
    },
    {
        "name": "高 Way",
        "en_name": "Gao Way",
        "role": "维德副手",
        "era": "威慑纪元",
        "status": "deceased",
        "description": "托马斯·维德在 PIA 与星环公司的得力助手。在维德与程心的对决中站在维德一方，为光速飞船研发承担具体执行。",
        "image_url": "https://placehold.co/300x400/000/fff?text=Gao+Way",
        "quotes": "“我们只服从维德先生的命令。”",
        "logic_score": 0.85,
        "metrics": '{"alienation": 75, "deterrence": 60, "empathy": 20, "rationality": 90}',
        "key_events": '[{"role": "executor", "impact_description": "星环城抵抗与光速飞船"}]'
    },
    {
        "name": "三体元首",
        "en_name": "Trisolaran Supreme",
        "role": "三体世界领袖",
        "era": "黄金时代",
        "status": "active",
        "description": "三体世界的最高统治者。在乱纪元与恒纪元的交替中维系文明存续，下达远征地球的决策，并指挥智子锁死人类科学。",
        "image_url": "https://placehold.co/300x400/000/fff?text=Trisolaran",
        "quotes": "“我们起航。”",
        "logic_score": 1.0,
        "metrics": '{"alienation": 95, "deterrence": 100, "empathy": 5, "rationality": 98}',
        "key_events": '[{"role": "ruler", "impact_description": "远征地球决策"}, {"role": "commander", "impact_description": "智子与水滴部署"}]'
    },
    {"name": "邵琳", "en_name": "Shao Lin", "role": "叶文洁之母", "era": "黄金时代", "status": "deceased", "description": "叶哲泰之妻。在批斗浪潮中为自保在揭发材料上签字，背叛丈夫，间接导致叶哲泰之死。叶文洁对人性的绝望始于父亲之死与母亲之叛。", "image_url": "", "quotes": "\"我没有办法。\"", "logic_score": 0.30, "metrics": '{"alienation": 20, "deterrence": 0, "empathy": 30, "rationality": 40}', "key_events": '[{"role": "betrayer", "impact_description": "揭发叶哲泰"}]'},
    {"name": "白沐霖", "en_name": "Bai Mulin", "role": "记者", "era": "黄金时代", "status": "deceased", "description": "叶文洁在大兴安岭时遇到的《大生产报》记者。曾借她《寂静的春天》，后为自保将写信责任推给叶文洁，致其遭审问。叶文洁首次直面人性之恶。", "image_url": "", "quotes": "\"那封信不是我写的。\"", "logic_score": 0.25, "metrics": '{"alienation": 15, "deterrence": 0, "empathy": 10, "rationality": 35}', "key_events": '[{"role": "betrayer", "impact_description": "诬陷叶文洁"}]'},
    {"name": "沙瑞山", "en_name": "Sha Ruishan", "role": "天体物理学博士生", "era": "黄金时代", "status": "deceased", "description": "汪淼的博士生，负责宇宙微波背景辐射观测。他首次发现宇宙闪烁现象并报告汪淼，成为智子锁死人类认知的见证者之一。", "image_url": "", "quotes": "\"老师，宇宙在闪烁！\"", "logic_score": 0.75, "metrics": '{"alienation": 50, "deterrence": 0, "empathy": 50, "rationality": 90}', "key_events": '[{"role": "observer", "impact_description": "发现宇宙闪烁"}]'},
    {"name": "徐冰冰", "en_name": "Xu Bingbing", "role": "史强助手", "era": "危机纪元", "status": "deceased", "description": "史强办案时的年轻助手，冷静细致，负责技术取证与情报汇总。在古筝行动及罗辑保护等行动中承担关键支援。", "image_url": "", "quotes": "\"史队，数据已经出来了。\"", "logic_score": 0.78, "metrics": '{"alienation": 25, "deterrence": 40, "empathy": 55, "rationality": 88}', "key_events": '[{"role": "support", "impact_description": "古筝行动与罗辑保护"}]'},
    {"name": "唐红静", "en_name": "Tang Hongjing", "role": "杨冬同事", "era": "黄金时代", "status": "deceased", "description": "杨冬在高能所的实验搭档。杨冬自杀后，其遗物与工作记录成为汪淼等人追溯物理学锁死与红岸真相的线索之一。", "image_url": "", "quotes": "\"杨冬最后几天一直在看加速器的数据。\"", "logic_score": 0.70, "metrics": '{"alienation": 40, "deterrence": 0, "empathy": 60, "rationality": 85}', "key_events": '[{"role": "witness", "impact_description": "杨冬之死线索"}]'},
    {"name": "破壁人一号", "en_name": "Wallbreaker One", "role": "泰勒的破壁人", "era": "危机纪元", "status": "deceased", "description": "ETO 指派识破面壁者弗雷德里克·泰勒战略的破壁人。当众揭露「蚊群计划」——用球状闪电将舰队量子化以穿透智子——并指出宏观退相干后只是概率云，无法作战。主不在乎。", "image_url": "", "quotes": "\"主不在乎。您的幽灵舰队会退相干。\"", "logic_score": 0.92, "metrics": '{"alienation": 95, "deterrence": 20, "empathy": 10, "rationality": 95}', "key_events": '[{"role": "breaker", "impact_description": "破壁泰勒"}]'},
    {"name": "破壁人二号", "en_name": "Wallbreaker Two", "role": "雷迪亚兹的破壁人", "era": "危机纪元", "status": "deceased", "description": "ETO 指派识破面壁者雷迪亚兹战略的破壁人。揭露其真实意图并非以氢弹威慑三体，而是将水星推入太阳引发连锁坍缩、毁灭太阳系。三体人会先发制人，人类也会先处决雷迪亚兹。", "image_url": "", "quotes": "\"您要让太阳不再升起。\"", "logic_score": 0.90, "metrics": '{"alienation": 90, "deterrence": 30, "empathy": 15, "rationality": 92}', "key_events": '[{"role": "breaker", "impact_description": "破壁雷迪亚兹"}]'},
    {"name": "破壁人三号", "en_name": "Wallbreaker Three", "role": "罗辑的破壁人", "era": "危机纪元", "status": "deceased", "description": "ETO 指派的对罗辑的破壁人。罗辑的战略是思维不可见的心中之谋，破壁人始终未能真正「破壁」——直至咒语应验与威慑建立，罗辑自我揭晓。", "image_url": "", "quotes": "\"我们无法破壁罗辑。他的战略在他的脑子里。\"", "logic_score": 0.88, "metrics": '{"alienation": 85, "deterrence": 40, "empathy": 20, "rationality": 90}', "key_events": '[{"role": "failed_breaker", "impact_description": "无法破壁罗辑"}]'},
    {"name": "乔纳森", "en_name": "Jonathan", "role": "罗辑保镖", "era": "危机纪元", "status": "deceased", "description": "PDC 指派保护罗辑的安保人员之一。在 ETO 多次暗杀中与史强等共同护卫罗辑，直至其建立威慑。", "image_url": "", "quotes": "\"罗辑博士，请留在安全区内。\"", "logic_score": 0.72, "metrics": '{"alienation": 30, "deterrence": 60, "empathy": 50, "rationality": 75}', "key_events": '[{"role": "protector", "impact_description": "护卫罗辑"}]'},
    {"name": "张援朝", "en_name": "Zhang Yuanchao", "role": "大低谷幸存者", "era": "危机纪元", "status": "deceased", "description": "罗辑冬眠苏醒后结识的三位老人之一，曾经历大低谷。与杨晋文、苗福全一起成为罗辑观察新世界的窗口，代表普通人在末日叙事下的生存与选择。", "image_url": "", "quotes": "\"那时候能吃上饭就不错了。\"", "logic_score": 0.55, "metrics": '{"alienation": 35, "deterrence": 10, "empathy": 70, "rationality": 60}', "key_events": '[{"role": "witness", "impact_description": "大低谷与威慑纪元平民视角"}]'},
    {"name": "杨晋文", "en_name": "Yang Jinwen", "role": "大低谷幸存者", "era": "危机纪元", "status": "deceased", "description": "罗辑苏醒后的三位老邻居之一，与张援朝、苗福全共同代表经历过最黑暗年代的一代人。对「给岁月以文明」有切身体会。", "image_url": "", "quotes": "\"我们活下来了，他们没活下来。\"", "logic_score": 0.58, "metrics": '{"alienation": 40, "deterrence": 15, "empathy": 65, "rationality": 62}', "key_events": '[{"role": "witness", "impact_description": "大低谷幸存者"}]'},
    {"name": "苗福全", "en_name": "Miao Fuquan", "role": "大低谷幸存者", "era": "危机纪元", "status": "deceased", "description": "罗辑苏醒后结识的三位老人之一。与张援朝、杨晋文一样，是威慑纪元初期普通市民的缩影，见证了从大低谷到虚假繁荣的转变。", "image_url": "", "quotes": "\"罗老师，您睡得够久的。\"", "logic_score": 0.52, "metrics": '{"alienation": 30, "deterrence": 10, "empathy": 68, "rationality": 58}', "key_events": '[{"role": "witness", "impact_description": "平民视角"}]'},
    {"name": "斯科特", "en_name": "Scott", "role": "青铜时代号舰长", "era": "危机纪元", "status": "deceased", "description": "末日之战幸存舰「青铜时代」号舰长。在黑暗森林战役的猜疑链中参与星舰国际的相互打击。后舰员被召回地球受审，他向蓝色空间号发出「不要返航，这里不是家」的警告。", "image_url": "", "quotes": "\"不要返航，这里不是家。\"", "logic_score": 0.88, "metrics": '{"alienation": 75, "deterrence": 70, "empathy": 35, "rationality": 90}', "key_events": '[{"role": "commander", "impact_description": "青铜时代号"}, {"role": "messenger", "impact_description": "警告蓝色空间号"}]'},
    {"name": "莫沃维奇", "en_name": "Moscowitz", "role": "万有引力号舰长", "era": "威慑纪元", "status": "deceased", "description": "万有引力号舰长，率舰追击蓝色空间号。威慑失效后，在智子盲区内主持舰上表决，最终启动引力波广播，将三体与地球坐标暴露于黑暗森林。", "image_url": "", "quotes": "\"现在表决。是否启动引力波广播。\"", "logic_score": 0.90, "metrics": '{"alienation": 70, "deterrence": 85, "empathy": 45, "rationality": 92}', "key_events": '[{"role": "commander", "impact_description": "万有引力号"}, {"role": "trigger", "impact_description": "引力波广播表决"}]'},
    {"name": "井上明", "en_name": "Inoue Akira", "role": "希恩斯助手", "era": "危机纪元", "status": "deceased", "description": "脑科学家，希恩斯增智与思想钢印项目的技术助手。在不知情或半知情下参与钢印族制造，与山杉惠子的立场形成对照。", "image_url": "", "quotes": "\"扫描完成。神经回路已标记。\"", "logic_score": 0.82, "metrics": '{"alienation": 55, "deterrence": 20, "empathy": 50, "rationality": 90}', "key_events": '[{"role": "assistant", "impact_description": "思想钢印技术"}]'},
    {"name": "朴义君", "en_name": "Park Il-jun", "role": "亚洲舰队司令", "era": "危机纪元", "status": "deceased", "description": "末日之战时亚洲舰队高级将领。参与联合舰队对水滴的迎击部署，见证水滴以锐角机动击穿人类方阵的绝望时刻。", "image_url": "", "quotes": "\"目标加速！不可能！\"", "logic_score": 0.84, "metrics": '{"alienation": 60, "deterrence": 65, "empathy": 40, "rationality": 85}', "key_events": '[{"role": "commander", "impact_description": "末日之战"}]'},
    {"name": "李医生", "en_name": "Dr. Li", "role": "程心主治医生", "era": "危机纪元", "status": "deceased", "description": "程心罹患绝症时的主治医生。曾与 PIA 接触，程心被列为阶梯计划候选人与其病情有关。云天明自愿献出大脑后，程心终生背负愧疚。", "image_url": "", "quotes": "\"程博士，您的病情需要告知家属。\"", "logic_score": 0.65, "metrics": '{"alienation": 20, "deterrence": 0, "empathy": 75, "rationality": 80}', "key_events": '[{"role": "medical", "impact_description": "程心与阶梯计划候选人"}]'},
    {"name": "毕云峰", "en_name": "Bi Yunfeng", "role": "化学推进派代表", "era": "危机纪元", "status": "deceased", "description": "坚持化学推进路线的老航天专家。章北海为推动无工质辐射推进立项，制造陨石袭击假象，毕云峰与另两名同事在太空行走中「遇难」。无工质研发由此立项。", "image_url": "", "quotes": "\"工质推进才是可靠路线。\"", "logic_score": 0.72, "metrics": '{"alienation": 30, "deterrence": 20, "empathy": 50, "rationality": 75}', "key_events": '[{"role": "victim", "impact_description": "章北海推动无工质研发的牺牲者"}]'},
    {"name": "长老", "en_name": "The Elder", "role": "歌者文明上层", "era": "广播纪元", "status": "active", "description": "歌者文明中下达「藏好自己，做好清理」指示的上层存在。清理工作制度化、平庸化；二向箔与光粒的投放由长老的规则与成本效益决定。", "image_url": "", "quotes": "\"藏好自己，做好清理。\"", "logic_score": 1.0, "metrics": '{"alienation": 100, "deterrence": 100, "empathy": 0, "rationality": 100}', "key_events": '[{"role": "ruler", "impact_description": "清理规则"}]'},
    {"name": "归零者", "en_name": "Returners", "role": "宇宙重启倡议者", "era": "银河纪元", "status": "active", "description": "倡议并执行宇宙质量归还与重启的超级文明。向全宇宙广播呼吁小宇宙归还质量，以使大宇宙能坍缩重启。程心等人最终响应，留下五公斤后走出 647 号宇宙。", "image_url": "", "quotes": "\"请把质量归还。\"", "logic_score": 1.0, "metrics": '{"alienation": 95, "deterrence": 80, "empathy": 20, "rationality": 100}', "key_events": '[{"role": "broadcaster", "impact_description": "回归运动"}]'},
    {"name": "亨特", "en_name": "Hunter", "role": "万有引力号军官", "era": "威慑纪元", "status": "deceased", "description": "万有引力号上的军官之一，参与对蓝色空间号的追击及威慑失效后的舰上表决。引力波广播的启动是集体决策的结果。", "image_url": "", "quotes": "\"我们还有两分钟。\"", "logic_score": 0.85, "metrics": '{"alienation": 65, "deterrence": 75, "empathy": 40, "rationality": 88}', "key_events": '[{"role": "crew", "impact_description": "万有引力号表决"}]'},
    {"name": "戴文", "en_name": "Daven", "role": "蓝色空间号军官", "era": "威慑纪元", "status": "active", "description": "蓝色空间号舰员，随褚岩进入四维碎片并参与对水滴的从内破坏。星舰人类火种的见证者与执行者之一。", "image_url": "", "quotes": "\"它不再是神话了。\"", "logic_score": 0.86, "metrics": '{"alienation": 75, "deterrence": 70, "empathy": 35, "rationality": 90}', "key_events": '[{"role": "crew", "impact_description": "四维打击"}]'},
    {"name": "拉菲尔", "en_name": "Raphael", "role": "雷迪亚兹破壁人", "era": "危机纪元", "status": "deceased", "description": "ETO 中负责破壁雷迪亚兹的破壁人，在听证会上揭露水星坠落与太阳系同归于尽的真实战略，并预言三体先发制人、人类先处决面壁者。", "image_url": "", "quotes": "\"您要让水星坠入太阳。\"", "logic_score": 0.89, "metrics": '{"alienation": 88, "deterrence": 35, "empathy": 18, "rationality": 90}', "key_events": '[{"role": "breaker", "impact_description": "破壁雷迪亚兹"}]'},
    {"name": "奈尔·威廉斯", "en_name": "Neil Williams", "role": "北美舰队代表", "era": "危机纪元", "status": "deceased", "description": "末日之战联合舰队中北美舰队的高级军官。参与木星轨道迎击水滴的部署，目睹人类舰队在数分钟内被一枚探测器击穿的绝望。", "image_url": "", "quotes": "\"All units, engage.\"", "logic_score": 0.82, "metrics": '{"alienation": 55, "deterrence": 68, "empathy": 42, "rationality": 85}', "key_events": '[{"role": "commander", "impact_description": "末日之战"}]'},
    {"name": "杰拉德", "en_name": "Gerrard", "role": "欧洲舰队代表", "era": "危机纪元", "status": "deceased", "description": "联合舰队中欧洲舰队将领。水滴锐角转向时，欧洲舰队的舰艇与亚洲、北美等一同在极短时间内被击穿。", "image_url": "", "quotes": "\"C'est impossible.\"", "logic_score": 0.81, "metrics": '{"alienation": 52, "deterrence": 65, "empathy": 45, "rationality": 84}', "key_events": '[{"role": "commander", "impact_description": "末日之战"}]'},

    # --- 三体游戏中人物（原著《三体》中明确出现的虚拟角色） ---
    {"name": "周文王", "en_name": "King Wen of Zhou", "role": "三体游戏角色", "era": "黄金时代", "status": "deceased", "description": "三体游戏中出现的周文王。向汪淼解释乱纪元与恒纪元、脱水与浸泡的生存法则，手持单摆试图预测太阳运行，代表文明对三体问题的第一次理性探索。", "image_url": "", "quotes": "\"把脱水者搬到仓库里去。\"", "logic_score": 0.65, "metrics": '{"alienation": 40, "deterrence": 0, "empathy": 50, "rationality": 70}', "key_events": '[{"role": "observer", "impact_description": "三体游戏中阐释乱纪元"}]'},
    {"name": "墨子", "en_name": "Mozi", "role": "三体游戏角色", "era": "黄金时代", "status": "deceased", "description": "三体游戏中出现的墨子。研制包裹恒星的宇宙球壳以遮蔽太阳、制造恒纪元的设想，被证明不可行。代表文明对三体问题的另一种求解尝试。", "image_url": "", "quotes": "\"我的宇宙球壳可以遮蔽太阳。\"", "logic_score": 0.70, "metrics": '{"alienation": 50, "deterrence": 0, "empathy": 40, "rationality": 75}', "key_events": '[{"role": "observer", "impact_description": "三体游戏中宇宙球壳设想"}]'},
    {"name": "冯·诺依曼", "en_name": "Von Neumann", "role": "三体游戏角色", "era": "黄金时代", "status": "deceased", "description": "三体游戏中出现的冯·诺依曼。用秦始皇的三千万士兵组成人列计算机，以人力模拟计算机运算三体问题。代表用算力暴力求解的幻想及其极限。", "image_url": "", "quotes": "\"人列计算机。\"", "logic_score": 0.88, "metrics": '{"alienation": 60, "deterrence": 0, "empathy": 20, "rationality": 95}', "key_events": '[{"role": "observer", "impact_description": "三体游戏中人列计算机"}]'},
    {"name": "秦始皇", "en_name": "Qin Shi Huang", "role": "三体游戏角色", "era": "黄金时代", "status": "deceased", "description": "三体游戏中出现的秦始皇。与冯·诺依曼合作，以秦朝军队为人列计算机的「硬件」，指挥士兵举旗运算。三体问题仍无解，恒纪元未至。", "image_url": "", "quotes": "\"朕的军队可以算。\"", "logic_score": 0.75, "metrics": '{"alienation": 70, "deterrence": 80, "empathy": 10, "rationality": 80}', "key_events": '[{"role": "observer", "impact_description": "三体游戏中人列计算机"}]'},
    {"name": "哥白尼", "en_name": "Copernicus", "role": "三体游戏角色", "era": "黄金时代", "status": "deceased", "description": "三体游戏中出现的哥白尼。在游戏中揭示三体运动在力学上无解析解、无法长期预测，恒纪元与乱纪元本质不可知。代表文明对三体问题数学本质的觉醒。", "image_url": "", "quotes": "\"三体问题无解。\"", "logic_score": 0.95, "metrics": '{"alienation": 60, "deterrence": 0, "empathy": 40, "rationality": 98}', "key_events": '[{"role": "observer", "impact_description": "三体游戏中揭示无解"}]'},
    {"name": "爱因斯坦", "en_name": "Einstein", "role": "三体游戏角色", "era": "黄金时代", "status": "deceased", "description": "三体游戏中出现的爱因斯坦。在游戏中参与对三体运动的讨论，代表人类科学巨人对宇宙规律的追问与局限。", "image_url": "", "quotes": "\"上帝不掷骰子。\"", "logic_score": 0.92, "metrics": '{"alienation": 55, "deterrence": 0, "empathy": 45, "rationality": 98}', "key_events": '[{"role": "observer", "impact_description": "三体游戏中科学讨论"}]'},
    {"name": "牛顿", "en_name": "Newton", "role": "三体游戏角色", "era": "黄金时代", "status": "deceased", "description": "三体游戏中出现的牛顿。在游戏中与冯·诺依曼、秦始皇等共同尝试用力学与计算求解三体问题，象征经典力学在混沌面前的无力。", "image_url": "", "quotes": "\"我们可以用微分方程。\"", "logic_score": 0.90, "metrics": '{"alienation": 50, "deterrence": 0, "empathy": 30, "rationality": 95}', "key_events": '[{"role": "observer", "impact_description": "三体游戏中力学求解"}]'},
    {"name": "亚里士多德", "en_name": "Aristotle", "role": "三体游戏角色", "era": "黄金时代", "status": "deceased", "description": "三体游戏中出现的亚里士多德。在游戏中参与对宇宙与运动本质的讨论，代表古典理性对三体世界的介入。", "image_url": "", "quotes": "\"运动需要原因。\"", "logic_score": 0.72, "metrics": '{"alienation": 45, "deterrence": 0, "empathy": 40, "rationality": 82}', "key_events": '[{"role": "observer", "impact_description": "三体游戏中哲学与科学"}]'},
    {"name": "纣王", "en_name": "King Zhou", "role": "三体游戏角色", "era": "黄金时代", "status": "deceased", "description": "三体游戏中出现的纣王。在乱纪元中统治文明，与周文王等共同呈现三体世界文明的轮回与绝望。", "image_url": "", "quotes": "\"烧了。\"", "logic_score": 0.50, "metrics": '{"alienation": 80, "deterrence": 70, "empathy": 5, "rationality": 50}', "key_events": '[{"role": "observer", "impact_description": "三体游戏中乱纪元统治者"}]'},
    {"name": "伽利略", "en_name": "Galileo", "role": "三体游戏角色", "era": "黄金时代", "status": "deceased", "description": "三体游戏中出现的伽利略。在游戏中参与对天体运动与观测的讨论，代表近代科学对三体世界的审视。", "image_url": "", "quotes": "\"观测与计算。\"", "logic_score": 0.85, "metrics": '{"alienation": 50, "deterrence": 0, "empathy": 40, "rationality": 92}', "key_events": '[{"role": "observer", "impact_description": "三体游戏中观测与科学"}]'},

    # --- 原著中明确提及的真实人物 ---
    {"name": "霍金", "en_name": "Stephen Hawking", "role": "物理学家", "era": "黄金时代", "status": "deceased", "description": "原著中提及的英国物理学家。曾警告人类不要主动向宇宙发送信号、暴露地球位置，以免招致高级文明打击。其担忧与「不要回答」及黑暗森林法则相呼应。", "image_url": "", "quotes": "\"不要主动联系外星文明。\"", "logic_score": 0.98, "metrics": '{"alienation": 30, "deterrence": 0, "empathy": 50, "rationality": 98}', "key_events": '[{"role": "observer", "impact_description": "原著中提及的警告"}]'},
]

# 人物志扩展：关键决策、人物关系、关键语录（按姓名合并进 FIGURES）
FIGURES_EXTRA = {
    "罗辑": {
        "key_decisions": [
            {"decision": "接受面壁者身份并利用其权力寻找梦中人", "context": "被选为面壁者后拒绝参与战略，实则借此满足私欲并最终获得庄颜", "outcome": "庄颜成为其建立威慑的情感锚点"},
            {"decision": "在叶文洁墓前悟出黑暗森林法则并实施咒语实验", "context": "雪地工程实为引力波天线掩护，对 187J3X1 恒星发布坐标", "outcome": "验证黑暗森林，为执剑人威慑奠定基础"},
            {"decision": "担任执剑人并持引力波开关五十余年", "context": "三体与人类维持恐怖平衡", "outcome": "威慑纪元维系至程心接任"},
        ],
        "relationships": [
            {"target": "叶文洁", "relation_type": "mentor", "description": "在杨冬墓前从叶文洁处获得宇宙社会学公理"},
            {"target": "庄颜", "relation_type": "lover", "description": "面壁计划为其制造的妻子，威慑建立后被迫冬眠"},
            {"target": "史强", "relation_type": "ally", "description": "长期保护罗辑免受 ETO 暗杀"},
            {"target": "程心", "relation_type": "successor", "description": "将执剑人身份交给程心，后者导致威慑崩溃"},
        ],
        "key_quotes": [
            {"quote": "我对三体世界说话。", "context": "建立威慑时向三体宣告"},
            {"quote": "这是计划的一部分。", "context": "面对质疑时的面壁者式回答"},
            {"quote": "把枪口对准自己的脑袋，才是真正的威慑。", "context": "阐释黑暗森林威慑本质"},
        ],
    },
    "叶文洁": {
        "key_decisions": [
            {"decision": "在红岸回复三体信号并发出「到这里来吧」", "context": "收到「不要回答」后仍选择邀请三体", "outcome": "地球坐标暴露，三体舰队起航"},
            {"decision": "割断雷志成与杨卫宁的绳索", "context": "雷志成发现地外接触欲上报", "outcome": "二人坠崖身亡，叶文洁独守秘密"},
            {"decision": "向罗辑揭示宇宙社会学公理", "context": "杨冬墓前，将黑暗森林的钥匙交给罗辑", "outcome": "间接造就执剑人与威慑纪元"},
        ],
        "relationships": [
            {"target": "叶哲泰", "relation_type": "family", "description": "父亲，批斗中死亡，促成其绝望"},
            {"target": "杨卫宁", "relation_type": "family", "description": "丈夫，红岸总工，被其割绳杀害"},
            {"target": "杨冬", "relation_type": "family", "description": "女儿，物理学家，因智子锁死与母亲真相自杀"},
            {"target": "伊文斯", "relation_type": "ally", "description": "降临派领袖，与三体直接通讯的桥梁"},
            {"target": "罗辑", "relation_type": "mentee", "description": "将公理传授给罗辑"},
        ],
        "key_quotes": [
            {"quote": "到这里来吧，我将帮助你们获得这个世界。", "context": "回复三体信号"},
            {"quote": "消灭人类暴政，世界属于三体。", "context": "ETO 纲领"},
        ],
    },
    "章北海": {
        "key_decisions": [
            {"decision": "刺杀坚持化学推进的老航天以推动无工质研发", "context": "制造陨石袭击假象", "outcome": "无工质发动机成为主流，为星舰逃亡创造条件"},
            {"decision": "劫持自然选择号并下令前进四", "context": "末日之战前逃离战场", "outcome": "为人类保留火种，后死于黑暗森林战役"},
            {"decision": "在黑暗森林战役中放弃先发攻击，接受与追击舰同归于尽", "context": "「没关系的，都一样」", "outcome": "仅蓝色空间号等幸存"},
        ],
        "relationships": [
            {"target": "吴岳", "relation_type": "colleague", "description": "战友，失败主义者，选择退役"},
            {"target": "东方延绪", "relation_type": "subordinate", "description": "自然选择号舰长，与舰同亡"},
            {"target": "褚岩", "relation_type": "indirect_successor", "description": "蓝色空间号延续了章北海的逃亡火种"},
        ],
        "key_quotes": [
            {"quote": "自然选择，前进四！", "context": "劫舰逃亡时"},
            {"quote": "没关系的，都一样。", "context": "黑暗森林战役中面对次声波氢弹"},
        ],
    },
    "程心": {
        "key_decisions": [
            {"decision": "接任执剑人", "context": "威慑度被判定为零仍接受", "outcome": "接任后数分钟三体发动攻击，威慑终结"},
            {"decision": "阻止维德开发光速飞船、交出星环城", "context": "以「只送大脑」式的道德选择否决维德", "outcome": "人类失去唯一大规模逃逸机会"},
            {"decision": "在回归运动中归还小宇宙质量", "context": "响应归零者广播", "outcome": "参与宇宙重启的可能"},
        ],
        "relationships": [
            {"target": "云天明", "relation_type": "lover", "description": "云天明的单恋与三个童话的接收者"},
            {"target": "托马斯·维德", "relation_type": "opponent", "description": "两次关键对决均以程心「人性」获胜"},
            {"target": "艾 AA", "relation_type": "ally", "description": "助手与挚友，共同逃出二向箔"},
            {"target": "罗辑", "relation_type": "successor", "description": "从罗辑手中接过执剑人"},
        ],
        "key_quotes": [
            {"quote": "我选择爱。", "context": "执剑人交接前的自我辩护"},
        ],
    },
    "云天明": {
        "key_decisions": [
            {"decision": "接受阶梯计划、以大脑形式被发射", "context": "绝症将死，为程心留下希望", "outcome": "被三体截获并复原，存活数世纪"},
            {"decision": "通过智子向程心传递三个童话", "context": "将曲率驱动与黑域隐喻藏在故事中", "outcome": "人类获得技术暗示但解读与执行不足"},
            {"decision": "将 647 号小宇宙赠予程心", "context": "与艾 AA 度过余生后", "outcome": "程心在回归运动中归还质量"},
        ],
        "relationships": [
            {"target": "程心", "relation_type": "lover", "description": "一生所爱，送星、送童话、送小宇宙"},
            {"target": "艾 AA", "relation_type": "companion", "description": "晚年与艾 AA 在蓝星相伴"},
            {"target": "托马斯·维德", "relation_type": "indirect", "description": "阶梯计划由维德推动"},
        ],
        "key_quotes": [
            {"quote": "来了，爱了，送给她一颗星星，走了。", "context": "对程心情感的概括"},
        ],
    },
    "史强": {
        "key_decisions": [
            {"decision": "提出古筝行动：用飞刃切割审判日号", "context": "需夺取三体信息且不破坏硬盘", "outcome": "行动成功，人类获得三体通讯记录"},
            {"decision": "长期保护罗辑", "context": "ETO 多次暗杀", "outcome": "罗辑存活至建立威慑"},
            {"decision": "以「虫子从未被战胜」稳定汪淼", "context": "汪淼受倒计时与宇宙闪烁冲击", "outcome": "汪淼坚持科研并最终提供飞刃"},
        ],
        "relationships": [
            {"target": "汪淼", "relation_type": "ally", "description": "古筝行动技术提供者"},
            {"target": "罗辑", "relation_type": "ally", "description": "保护对象与战友"},
            {"target": "常伟思", "relation_type": "superior", "description": "作战体系内上级"},
            {"target": "徐冰冰", "relation_type": "subordinate", "description": "办案助手"},
        ],
        "key_quotes": [
            {"quote": "邪乎到家必有鬼。", "context": "调查异常时的口头禅"},
            {"quote": "虫子从来没有被真正战胜过。", "context": "鼓舞汪淼与人类信心"},
        ],
    },
    "丁仪": {
        "key_decisions": [
            {"decision": "乘小艇接触水滴并用手触碰表面", "context": "末日之战前试图理解探测器", "outcome": "推断出强互作用力材料，发出「傻孩子们，快跑」后与艇同毁"},
            {"decision": "参与宏原子与球状闪电研究", "context": "泰勒蚊群计划依赖该理论", "outcome": "破壁人指出宏观退相干后计划无效，但丁仪理论本身为人类前沿"},
        ],
        "relationships": [
            {"target": "杨冬", "relation_type": "mentee", "description": "杨冬为物理学后辈，其死与智子相关"},
            {"target": "汪淼", "relation_type": "colleague", "description": "同处物理学前沿"},
            {"target": "泰勒", "relation_type": "indirect", "description": "蚊群计划依赖丁仪理论"},
        ],
        "key_quotes": [
            {"quote": "傻孩子们，快跑啊！", "context": "接触水滴后对舰队的最后警告"},
            {"quote": "物理学不存在了？不，它只是更残酷了。", "context": "对智子锁死与宇宙法则的认知"},
        ],
    },
    "托马斯·维德": {
        "key_decisions": [
            {"decision": "推动阶梯计划：只送大脑", "context": "为将人类情报送入三体", "outcome": "云天明大脑被发射并被三体截获"},
            {"decision": "坚持研制光速飞船、与程心对决", "context": "程心要求交出星环城", "outcome": "程心获胜，维德被处决，人类失去逃逸窗口"},
        ],
        "relationships": [
            {"target": "程心", "relation_type": "opponent", "description": "两次关键抉择均败给程心的「人性」"},
            {"target": "云天明", "relation_type": "indirect", "description": "阶梯计划使云天明成为大脑"},
            {"target": "高 Way", "relation_type": "subordinate", "description": "维德副手"},
        ],
        "key_quotes": [
            {"quote": "前进！前进！！不择手段地前进！！！", "context": "一生信条"},
            {"quote": "失去人性，失去很多；失去兽性，失去一切。", "context": "对程心的警示"},
        ],
    },
    "麦克·伊文斯": {
        "key_decisions": [
            {"decision": "建立第二红岸（审判日号）并与三体直接通讯", "context": "物种平等主义与对人类文明的否定", "outcome": "降临派成为三体在地球的代理，古筝行动中被灭"},
        ],
        "relationships": [
            {"target": "叶文洁", "relation_type": "ally", "description": "ETO 精神领袖与降临派金主"},
            {"target": "三体元首", "relation_type": "contact", "description": "通过审判日号与三体通讯"},
        ],
        "key_quotes": [
            {"quote": "主，我们是同志了。", "context": "与三体建立联系后"},
        ],
    },
    "褚岩": {
        "key_decisions": [
            {"decision": "在四维碎片中从内部破坏水滴", "context": "蓝色空间号进入四维，三维封闭结构可被透视与破坏", "outcome": "追击的水滴被毁"},
            {"decision": "参与万有引力号表决，支持启动引力波广播", "context": "威慑失效后", "outcome": "三体与地球坐标暴露于黑暗森林"},
        ],
        "relationships": [
            {"target": "章北海", "relation_type": "indirect_successor", "description": "延续星舰人类火种"},
            {"target": "万有引力号", "relation_type": "ally_then_merged", "description": "与追击舰汇合后共同决定广播"},
        ],
        "key_quotes": [
            {"quote": "不管去哪里，都是在这个宇宙中。", "context": "星舰人类命运"},
        ],
    },
    "1379号监听员": {
        "key_decisions": [
            {"decision": "向地球发出「不要回答」警告", "context": "收到叶文洁信号后违背元首命令", "outcome": "地球未听从，三体仍定位；1379 号被脱水焚烧"},
        ],
        "relationships": [
            {"target": "叶文洁", "relation_type": "contact", "description": "收到其信号并回复警告"},
            {"target": "三体元首", "relation_type": "subordinate", "description": "违背元首命令"},
        ],
        "key_quotes": [
            {"quote": "不要回答！不要回答！不要回答！", "context": "向地球发出的警告"},
        ],
    },
    "常伟思": {
        "key_decisions": [
            {"decision": "组建太空军并推动全球战区", "context": "物理学锁死后的军事应对", "outcome": "人类进入与三体的长期对峙架构"},
            {"decision": "指挥古筝行动", "context": "与史强、斯坦顿等协调", "outcome": "审判日号被切割，三体信息被截获"},
        ],
        "relationships": [
            {"target": "史强", "relation_type": "subordinate", "description": "古筝行动执行者"},
            {"target": "汪淼", "relation_type": "ally", "description": "飞刃技术提供者"},
        ],
        "key_quotes": [
            {"quote": "整个人类历史也是偶然，从石器时代到今天，都没什么重大变故，真幸运。", "context": "对战争与偶然的感慨"},
        ],
    },
    "汪淼": {
        "key_decisions": [
            {"decision": "提供纳米飞刃并参与古筝行动", "context": "审判日号通过巴拿马运河", "outcome": "船被切成四十层，人类获得三体情报"},
            {"decision": "在目睹宇宙闪烁与倒计时后仍选择继续科研并配合军方", "context": "智子施压与史强劝说", "outcome": "飞刃材料成为古筝行动唯一可行方案"},
            {"decision": "进入三体游戏以接近 ETO 与申玉菲", "context": "调查杨冬之死与物理学异常", "outcome": "接触宇宙社会学与文明兴衰，为后续罗辑线索铺垫"},
        ],
        "relationships": [
            {"target": "史强", "relation_type": "ally", "description": "古筝行动提出者与保护者"},
            {"target": "丁仪", "relation_type": "colleague", "description": "物理学界"},
            {"target": "申玉菲", "relation_type": "contact", "description": "被引入三体游戏"},
            {"target": "沙瑞山", "relation_type": "mentee", "description": "其博士生，发现宇宙闪烁"},
        ],
        "key_quotes": [
            {"quote": "倒计时的尽头是什么？", "context": "目睹智子倒计时时的恐惧"},
            {"quote": "宇宙在闪烁。", "context": "与沙瑞山观测到智子对背景辐射的干扰"},
        ],
    },
    "杨冬": {
        "key_decisions": [
            {"decision": "自杀", "context": "发现物理学被锁死且母亲与地外文明有关", "outcome": "引发汪淼等人调查，成为链条起点"},
        ],
        "relationships": [
            {"target": "叶文洁", "relation_type": "family", "description": "母亲，ETO 统帅"},
            {"target": "丁仪", "relation_type": "mentee", "description": "物理学后辈"},
        ],
        "key_quotes": [
            {"quote": "物理学……不存在了。", "context": "遗言"},
        ],
    },
    "智子 (仿生人)": {
        "key_decisions": [],
        "relationships": [
            {"target": "三体元首", "relation_type": "agent", "description": "三体意志在地球的代理人"},
            {"target": "程心", "relation_type": "contact", "description": "宣布澳大利亚保留地等"},
        ],
        "key_quotes": [
            {"quote": "你们是虫子。", "context": "对人类的评价"},
            {"quote": "请享用茶点。", "context": "威慑纪元时期礼仪"},
        ],
    },
    "歌者": {
        "key_decisions": [
            {"decision": "向太阳系投掷二向箔", "context": "例行清理，坐标「有点碍眼」", "outcome": "太阳系二维化"},
        ],
        "relationships": [],
        "key_quotes": [
            {"quote": "藏好自己，做好清理。", "context": "清理者信条"},
        ],
    },
    "三体元首": {
        "key_decisions": [
            {"decision": "下令远征地球", "context": "定位地球坐标后", "outcome": "三体舰队起航"},
            {"decision": "部署智子锁死人类科学", "context": "舰队抵达前", "outcome": "人类基础物理停滞"},
        ],
        "relationships": [
            {"target": "1379号监听员", "relation_type": "subordinate", "description": "违背命令发出不要回答"},
            {"target": "麦克·伊文斯", "relation_type": "contact", "description": "通过审判日号与地球降临派通讯"},
        ],
        "key_quotes": [
            {"quote": "我们起航。", "context": "远征决策"},
        ],
    },
    "雷迪亚兹": {
        "key_decisions": [
            {"decision": "以恒星级氢弹与水星坠落计划要挟三体", "context": "面壁计划", "outcome": "被破壁人揭穿，回国后被群众用石头砸死"},
        ],
        "relationships": [
            {"target": "破壁人二号", "relation_type": "opponent", "description": "揭穿其水星战略"},
            {"target": "萨伊", "relation_type": "superior", "description": "面壁计划主持方"},
        ],
        "key_quotes": [
            {"quote": "我要让太阳不再升起。", "context": "水星计划"},
        ],
    },
    "弗里德里克·泰勒": {
        "key_decisions": [
            {"decision": "建立量子幽灵舰队（蚊群计划）", "context": "面壁计划", "outcome": "被破壁人识破，宏观退相干使计划无效，泰勒自杀"},
        ],
        "relationships": [
            {"target": "破壁人", "relation_type": "opponent", "description": "识破蚊群计划"},
        ],
        "key_quotes": [
            {"quote": "妈妈，我将变成萤火虫。", "context": "蚊群计划"},
        ],
    },
    "比尔·希恩斯": {
        "key_decisions": [
            {"decision": "秘密植入思想钢印「人类必败」", "context": "表面研究增智，实则制造钢印族", "outcome": "钢印族成为逃亡主义种子；被山杉惠子破壁"},
        ],
        "relationships": [
            {"target": "山杉惠子", "relation_type": "family", "description": "妻子，实为破壁人"},
            {"target": "萨伊", "relation_type": "superior", "description": "面壁计划主持方"},
        ],
        "key_quotes": [
            {"quote": "水有毒。", "context": "钢印暗示"},
        ],
    },
    "萨伊": {
        "key_decisions": [
            {"decision": "启动面壁计划并选定四名面壁者", "context": "智子监控下人类唯一战略手段", "outcome": "罗辑、泰勒、雷迪亚兹、希恩斯被赋予面壁者身份"},
        ],
        "relationships": [
            {"target": "罗辑", "relation_type": "subordinate", "description": "第四面壁者"},
            {"target": "伽尔宁", "relation_type": "colleague", "description": "PDC 体系"},
        ],
        "key_quotes": [
            {"quote": "面壁者，请开始你的工作。", "context": "面壁计划启动"},
        ],
    },
    "庄颜": {
        "key_decisions": [],
        "relationships": [
            {"target": "罗辑", "relation_type": "lover", "description": "被面壁计划制造为罗辑的妻子与锚点"},
            {"target": "白蓉", "relation_type": "indirect", "description": "罗辑梦中情人概念的文学来源"},
        ],
        "key_quotes": [
            {"quote": "带我们回家。", "context": "对罗辑的请求"},
        ],
    },
    "艾 AA": {
        "key_decisions": [
            {"decision": "与程心乘唯一曲率飞船逃出太阳系", "context": "二向箔来临前", "outcome": "成为人类最后逃逸者之一"},
        ],
        "relationships": [
            {"target": "程心", "relation_type": "ally", "description": "助手与挚友"},
            {"target": "云天明", "relation_type": "companion", "description": "晚年与云天明在蓝星"},
        ],
        "key_quotes": [
            {"quote": "我们要活下去，这才是对爱最好的纪念。", "context": "逃逸与幸存"},
        ],
    },
    "关一帆": {
        "key_decisions": [],
        "relationships": [
            {"target": "程心", "relation_type": "ally", "description": "程心在银河纪元的守护者与伴侣"},
        ],
        "key_quotes": [
            {"quote": "在宇宙中，你再快都有比你更快的，你再慢也有比你更慢的。", "context": "黑暗森林与光速"},
        ],
    },
    "东方延绪": {
        "key_decisions": [
            {"decision": "担任自然选择号舰长并追击章北海", "context": "末日之战后", "outcome": "在黑暗森林战役中与舰同亡"},
        ],
        "relationships": [
            {"target": "章北海", "relation_type": "subordinate", "description": "被章北海劫舰，后与追击舰相互摧毁"},
        ],
        "key_quotes": [
            {"quote": "自然选择，前进四！", "context": "与章北海同念"},
        ],
    },
    "山杉惠子": {
        "key_decisions": [
            {"decision": "在听证会上揭穿希恩斯的思想钢印计划并自杀", "context": "破壁人二号", "outcome": "希恩斯战略破产，钢印族已存在"},
        ],
        "relationships": [
            {"target": "比尔·希恩斯", "relation_type": "family", "description": "丈夫，被其破壁"},
        ],
        "key_quotes": [
            {"quote": "我破壁了，比尔。", "context": "听证会上"},
        ],
    },
    "叶哲泰": {
        "key_decisions": [
            {"decision": "在批斗中拒绝跪下并坚持科学没有阶级性", "context": "文革批斗", "outcome": "被红卫兵打死，促成叶文洁对人性的绝望"},
        ],
        "relationships": [
            {"target": "叶文洁", "relation_type": "family", "description": "女儿"},
            {"target": "杨冬", "relation_type": "family", "description": "外孙女"},
        ],
        "key_quotes": [
            {"quote": "科学没有阶级性。", "context": "批斗中"},
        ],
    },
    "杨卫宁": {
        "key_decisions": [
            {"decision": "将叶文洁带入红岸基地", "context": "叶文洁处境与专业", "outcome": "叶文洁得以接触天线并回复三体"},
        ],
        "relationships": [
            {"target": "叶文洁", "relation_type": "family", "description": "妻子，杀害自己"},
            {"target": "雷志成", "relation_type": "colleague", "description": "与雷志成一同被叶文洁割绳杀害"},
        ],
        "key_quotes": [
            {"quote": "文洁，这里需要你。", "context": "将叶文洁带入红岸"},
        ],
    },
    "雷志成": {
        "key_decisions": [
            {"decision": "发现叶文洁与地外文明接触后意图上报", "context": "红岸监听", "outcome": "叶文洁割绳，与杨卫宁坠崖身亡"},
        ],
        "relationships": [
            {"target": "叶文洁", "relation_type": "subordinate", "description": "被其杀害"},
            {"target": "杨卫宁", "relation_type": "colleague", "description": "同坠崖"},
        ],
        "key_quotes": [
            {"quote": "你收到了什么？", "context": "发现异常后质问叶文洁"},
        ],
    },
    "魏成": {
        "key_decisions": [],
        "relationships": [
            {"target": "申玉菲", "relation_type": "family", "description": "妻子，科学边界"},
        ],
        "key_quotes": [
            {"quote": "我能证明三体问题无解。", "context": "数学研究"},
        ],
    },
    "申玉菲": {
        "key_decisions": [
            {"decision": "引导汪淼进入三体游戏并推动「拯救主」", "context": "科学边界与拯救派", "outcome": "汪淼接触三体文化；申玉菲后被潘寒核对杀死"},
        ],
        "relationships": [
            {"target": "汪淼", "relation_type": "contact", "description": "引导其进入游戏"},
            {"target": "魏成", "relation_type": "family", "description": "丈夫"},
        ],
        "key_quotes": [
            {"quote": "佛祖保佑，我主脱离苦海。", "context": "拯救派祈祷"},
        ],
    },
    "潘寒": {
        "key_decisions": [
            {"decision": "核对杀死申玉菲", "context": "ETO 内斗", "outcome": "降临派与拯救派冲突"},
        ],
        "relationships": [
            {"target": "申玉菲", "relation_type": "opponent", "description": "杀害申玉菲"},
        ],
        "key_quotes": [
            {"quote": "科技是人类的毒瘤。", "context": "环保与反科技立场"},
        ],
    },
    "吴岳": {
        "key_decisions": [
            {"decision": "在太空军成立前夕退役", "context": "失败主义", "outcome": "与章北海形成对照"},
        ],
        "relationships": [
            {"target": "章北海", "relation_type": "colleague", "description": "战友，选择离开"},
        ],
        "key_quotes": [
            {"quote": "我们必败。", "context": "失败主义"},
        ],
    },
    "林格": {
        "key_decisions": [],
        "relationships": [
            {"target": "斐兹罗", "relation_type": "subordinate", "description": "观测三体舰队的顾问"},
        ],
        "key_quotes": [
            {"quote": "将军，他们来了。", "context": "观测到三体舰队痕迹"},
        ],
    },
    "斐兹罗": {
        "key_decisions": [
            {"decision": "主持哈勃二号对三体舰队的观测", "context": "确认入侵", "outcome": "三体舰队痕迹被证实"},
        ],
        "relationships": [
            {"target": "林格", "relation_type": "superior", "description": "林格的上司"},
        ],
        "key_quotes": [
            {"quote": "让哈勃二号对准那片区域。", "context": "观测指令"},
        ],
    },
    "斯坦顿": {
        "key_decisions": [
            {"decision": "参与古筝行动军事协调", "context": "巴拿马运河", "outcome": "审判日号被切割"},
        ],
        "relationships": [
            {"target": "常伟思", "relation_type": "ally", "description": "多国联合行动"},
            {"target": "史强", "relation_type": "ally", "description": "古筝行动执行"},
        ],
        "key_quotes": [
            {"quote": "让船通过，然后收网。", "context": "古筝行动"},
        ],
    },
    "坎特": {
        "key_decisions": [],
        "relationships": [
            {"target": "罗辑", "relation_type": "liaison", "description": "PDC 指派联络员"},
        ],
        "key_quotes": [
            {"quote": "罗辑博士，这是计划的一部分吗？", "context": "面对罗辑不作为时"},
        ],
    },
    "伽尔宁": {
        "key_decisions": [],
        "relationships": [
            {"target": "萨伊", "relation_type": "colleague", "description": "PDC 轮值体系"},
        ],
        "key_quotes": [
            {"quote": "面壁者拥有调用资源的权力。", "context": "面壁计划行政"},
        ],
    },
    "曹彬": {
        "key_decisions": [],
        "relationships": [
            {"target": "程心", "relation_type": "colleague", "description": "解读云天明童话"},
        ],
        "key_quotes": [
            {"quote": "童话里有答案。", "context": "曲率与黑域隐喻"},
        ],
    },
    "高 Way": {
        "key_decisions": [
            {"decision": "服从维德、参与星环城抵抗与光速飞船研发", "context": "维德与程心对决", "outcome": "程心选择后维德放弃，高 Way 等服从"},
        ],
        "relationships": [
            {"target": "托马斯·维德", "relation_type": "subordinate", "description": "维德副手"},
        ],
        "key_quotes": [
            {"quote": "我们只服从维德先生的命令。", "context": "星环城"},
        ],
    },
    "毕云峰": {
        "key_decisions": [],
        "relationships": [
            {"target": "章北海", "relation_type": "victim", "description": "被章北海推动的陨石袭击牺牲"},
        ],
        "key_quotes": [
            {"quote": "工质推进才是可靠路线。", "context": "老航天立场"},
        ],
    },
    "白蓉": {
        "key_decisions": [],
        "relationships": [
            {"target": "罗辑", "relation_type": "lover", "description": "前女友，罗辑梦中情人概念的来源"},
        ],
        "key_quotes": [
            {"quote": "你心里要有一个她。", "context": "让罗辑构建完美恋人"},
        ],
    },
    "弗雷斯": {
        "key_decisions": [],
        "relationships": [
            {"target": "程心", "relation_type": "contact", "description": "澳大利亚保留地相遇"},
        ],
        "key_quotes": [
            {"quote": "姑娘，这是战争。", "context": "对程心说"},
        ],
    },
    "泰勒": {
        "key_decisions": [
            {"decision": "建立量子幽灵舰队（蚊群计划）", "context": "面壁计划", "outcome": "被破壁人识破，宏观退相干使计划无效，泰勒自杀"},
        ],
        "relationships": [
            {"target": "破壁人", "relation_type": "opponent", "description": "识破蚊群计划"},
        ],
        "key_quotes": [
            {"quote": "妈妈，我将变成萤火虫。", "context": "蚊群计划"},
        ],
    },
    "希恩斯": {
        "key_decisions": [
            {"decision": "秘密植入思想钢印「人类必败」", "context": "表面研究增智，实则制造钢印族", "outcome": "钢印族成为逃亡主义种子；被山杉惠子破壁"},
        ],
        "relationships": [
            {"target": "山杉惠子", "relation_type": "family", "description": "妻子，实为破壁人"},
            {"target": "萨伊", "relation_type": "superior", "description": "面壁计划主持方"},
        ],
        "key_quotes": [
            {"quote": "水有毒。", "context": "钢印暗示"},
        ],
    },
    "守摆人 (Pendulum-001)": {
        "key_decisions": [
            {"decision": "在双日凌空前将自己锁死在三体摆底座上记录最后一次周期", "context": "乱纪元 471 年", "outcome": "为文明留下证明其曾试图解析宇宙规律的唯一证据"},
        ],
        "relationships": [],
        "key_quotes": [
            {"quote": "眼睛里没有恐惧，只有波长 450nm 的冷光。", "context": "零点计划原创"},
        ],
    },
    "邵琳": {
        "key_decisions": [{"decision": "在揭发材料上签字背叛叶哲泰", "context": "批斗浪潮中为自保", "outcome": "叶哲泰被批斗致死，叶文洁对人性的绝望加深"}],
        "relationships": [{"target": "叶哲泰", "relation_type": "family", "description": "丈夫，被其揭发"}, {"target": "叶文洁", "relation_type": "family", "description": "女儿，终生疏离"}],
        "key_quotes": [{"quote": "我没有办法。", "context": "面对叶文洁的质问"}],
    },
    "白沐霖": {
        "key_decisions": [{"decision": "将写给中央的信的责任推给叶文洁", "context": "信被查获后为自保", "outcome": "叶文洁遭审问与迫害，首次直面人性之恶"}],
        "relationships": [{"target": "叶文洁", "relation_type": "betrayer", "description": "诬陷对象"}],
        "key_quotes": [{"quote": "那封信不是我写的。", "context": "推卸责任"}],
    },
    "沙瑞山": {
        "key_decisions": [{"decision": "将宇宙微波背景辐射异常现象报告汪淼", "context": "观测到宇宙闪烁", "outcome": "成为智子干扰人类认知的证据链一环"}],
        "relationships": [{"target": "汪淼", "relation_type": "mentor", "description": "导师"}],
        "key_quotes": [{"quote": "老师，宇宙在闪烁！", "context": "发现异常"}],
    },
    "徐冰冰": {
        "key_decisions": [{"decision": "在古筝行动与罗辑保护中承担技术取证与情报支援", "context": "史强办案团队", "outcome": "关键行动得以执行"}],
        "relationships": [{"target": "史强", "relation_type": "superior", "description": "上司"}],
        "key_quotes": [{"quote": "史队，数据已经出来了。", "context": "办案支援"}],
    },
    "斯科特": {
        "key_decisions": [{"decision": "向蓝色空间号发出「不要返航，这里不是家」", "context": "青铜时代号舰员被召回地球受审前", "outcome": "警告星舰人类勿回地球，影响后续引力波广播决策"}],
        "relationships": [{"target": "蓝色空间号", "relation_type": "ally", "description": "同为星舰国际幸存者"}],
        "key_quotes": [{"quote": "不要返航，这里不是家。", "context": "对蓝色空间号的最后通讯"}],
    },
    "莫沃维奇": {
        "key_decisions": [{"decision": "在智子盲区内主持万有引力号表决并启动引力波广播", "context": "威慑失效后", "outcome": "三体与地球坐标暴露于黑暗森林"}],
        "relationships": [{"target": "褚岩", "relation_type": "opponent", "description": "追击对象；广播后星舰人类与地球人类分野"}],
        "key_quotes": [{"quote": "现在表决。是否启动引力波广播。", "context": "舰上表决"}],
    },
    "破壁人一号": {
        "key_decisions": [{"decision": "在面壁者听证会上公开破壁泰勒的蚊群计划", "context": "ETO 指派", "outcome": "泰勒战略破产，主不在乎"}],
        "relationships": [{"target": "泰勒", "relation_type": "target", "description": "破壁对象"}],
        "key_quotes": [{"quote": "主不在乎。您的幽灵舰队会退相干。", "context": "破壁泰勒"}],
    },
    "破壁人二号": {
        "key_decisions": [{"decision": "揭露雷迪亚兹水星坠落与太阳系同归于尽战略", "context": "ETO 指派", "outcome": "雷迪亚兹被人类视为疯子并遭处决"}],
        "relationships": [{"target": "雷迪亚兹", "relation_type": "target", "description": "破壁对象"}],
        "key_quotes": [{"quote": "您要让太阳不再升起。", "context": "破壁雷迪亚兹"}],
    },
    "长老": {
        "key_decisions": [{"decision": "下达「藏好自己，做好清理」的规则", "context": "歌者文明清理工作", "outcome": "二向箔与光粒投放制度化"}],
        "relationships": [],
        "key_quotes": [{"quote": "藏好自己，做好清理。", "context": "对歌者的指示"}],
    },
    "归零者": {
        "key_decisions": [{"decision": "向全宇宙广播呼吁小宇宙归还质量", "context": "宇宙走向热寂", "outcome": "程心等响应回归运动，留下五公斤后走出小宇宙"}],
        "relationships": [],
        "key_quotes": [{"quote": "请把质量归还。", "context": "回归运动广播"}],
    },
}

def _merge_figure_extra(data: dict) -> None:
    """将 FIGURES_EXTRA 中的关键决策、关系、语录合并进 data，并转为 JSON 字符串。"""
    extra = FIGURES_EXTRA.get(data["name"], {})
    for key in ("key_decisions", "relationships", "key_quotes"):
        if key in extra and extra[key] is not None:
            data[key] = json.dumps(extra[key], ensure_ascii=False)
        elif key not in data or data.get(key) is None:
            data[key] = json.dumps([], ensure_ascii=False)


async def seed():
    from backend.config import settings
    from sqlalchemy import select
    print(f"DEBUG: Connecting to {settings.database_url}")
    async with AsyncSessionLocal() as session:
        # 去重：同名人物只保留一条（保留 id 最小的）
        names_in_seed = {data["name"] for data in FIGURES}
        for name in names_in_seed:
            result = await session.execute(
                select(FigureORM).where(FigureORM.name == name).order_by(FigureORM.id)
            )
            rows = result.scalars().unique().all()
            if len(rows) > 1:
                for row in rows[1:]:
                    await session.delete(row)
                print(f"Dedup: removed {len(rows) - 1} duplicate(s) for {name}")
        # 删除已废弃的简称重复项（种子中仅保留全名：弗里德里克·泰勒、比尔·希恩斯）
        for short_name in ("泰勒", "希恩斯"):
            result = await session.execute(select(FigureORM).where(FigureORM.name == short_name))
            rows = result.scalars().unique().all()
            for row in rows:
                await session.delete(row)
                print(f"Removed deprecated duplicate: {short_name}")
        await session.commit()

    async with AsyncSessionLocal() as session:
        from sqlalchemy import select
        for data in FIGURES:
            data["image_url"] = get_figure_avatar_url(data)
            _merge_figure_extra(data)
            result = await session.execute(select(FigureORM).where(FigureORM.name == data["name"]))
            existing = result.scalar_one_or_none()
            if existing:
                print(f"Updating {data['name']}...")
                existing.description = data["description"]
                existing.quotes = data.get("quotes")
                existing.metrics = data.get("metrics")
                existing.key_events = data.get("key_events")
                existing.logic_score = data.get("logic_score", 1.0)
                existing.image_url = data["image_url"]
                existing.role = data.get("role")
                existing.status = data.get("status")
                existing.key_decisions = data.get("key_decisions")
                existing.relationships = data.get("relationships")
                existing.key_quotes = data.get("key_quotes")
            else:
                print(f"Adding {data['name']}...")
                row = FigureORM(**data)
                session.add(row)
        await session.commit()
    print("Figures seed complete. Total:", len(FIGURES))

if __name__ == "__main__":
    asyncio.run(seed())
