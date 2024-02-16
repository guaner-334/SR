import math
from random import randint
from Star_Rail_damage_simulation.msg import global_msg


# 获取目标对象指定属性的抗性/穿透/伤害加成

def get_boost(source, stats_type, combat):
    """
    :param source: 输入来源的实例化对象
    :param stats_type: 支持输入DMG,RES_PEN,RES字符串
    :param combat: 支持输入物理,火,冰,雷,风,量子,虚数字符串
    :return: 返回输入对象的对应属性的抗性/穿透/伤害总加成
    """
    combat_dic = {
        "物理": "Physical",
        "火": "Fire",
        "冰": "Ice",
        "雷": "Lightning",
        "风": "Wind",
        "量子": "Quantum",
        "虚数": "Imaginary"
    }
    combat = combat_dic[combat]
    stats = stats_type
    stats_sum = 0
    if stats == "DMG":  # 若为增伤类型
        stats = combat + "_DMG_Boost"
        stats_sum = sum(getattr(source, stats)) + sum(getattr(source, "DMG_Boost"))
    if stats == "RES":  # 若为抗性
        stats = combat + "_RES_Boost"
        stats_sum = sum(getattr(source, stats)) + sum(getattr(source, "RES_Boost"))
    if stats == "RES_PEN":  # 若为抵抗穿透类型
        stats = combat + "_RES_PEN"
        stats_sum = sum(getattr(source, stats)) + sum(getattr(source, "RES_PEN"))
    if stats == "Outgoing_Healing_Boost":  # 若为医疗加成
        stats_sum = sum(getattr(source, stats)) + sum(getattr(source, "Outgoing_Healing_Boost"))
    return stats_sum


class Count:
    """
    计算器通用模板
    """

    def __init__(self):
        self.combat = None
        self.type = "break"


# 常规伤害计算器
class DMGCount(Count):
    # 攻击伤害计算
    @staticmethod
    def atk(stats: str, atk: int, source, target):
        """
        计算伤害函数
        :param stats: 参与计算的属性:ATK/DEF/HP
        :param atk: 基础倍率
        :param source: 造成伤害的角色
        :param target: 被攻击的角色
        :return: 返回(伤害 是否暴击 目标)的元组
        """
        is_crit = False
        # 各个伤害乘区计算
        # 更新基础属性
        stats = sum(getattr(source, stats))
        # 计算基础伤害乘区,公式:属性*技能倍率
        dmg_base = stats * atk
        # 计算增伤,公式:1 + 对应属性的百分比增伤 + 全属性增伤
        dmg_boost = 1 + get_boost(source, "DMG", source.combat_type)
        # 计算暴击伤害伤害乘区
        crit_range = 1  # 暴击伤害倍率,初始默认为1
        crit_roll = randint(1, 10000)  # 创建随机数
        crit_nub = sum(source.CRIT_rate) * 10000  # 将爆率*10000
        if crit_roll <= crit_nub:  # 若暴击
            is_crit = True  # 是否暴击变更为True
            crit_range = 1 + sum(source.CRIT_DMG)  # 暴击后,暴击伤害加成生效
        # 计算抗性伤害乘区,公式:1 - 敌方抗性 + 我方穿透
        target_res = get_boost(target, "RES", source.combat_type)  # 目标抗性
        source_res_pen = get_boost(source, "RES_PEN", source.combat_type)  # 自身穿透
        res_range = 1 - target_res + source_res_pen  # 最终抗性效果
        # 易伤区间,公式:1 + 敌方易伤
        dmg_up = 1 + sum(target.dmg_up)
        # 减伤区间,公式:1 - 敌方减伤
        dmg_down = 1 - sum(target.dmg_down)
        # 防御区间,公式:（（200+10*己方角色等级）/（（200+10*敌方等级）*（1-减防率）+（200+10*己方角色等级）））
        def_down = sum(source.def_PEN) + sum(target.def_down) - sum(target.def_up)  # 减防率
        if def_down > 1:  # 减防率不可大于1
            def_down = 1
        source_lv = source.lv
        target_lv = target.lv
        def_range_part1 = (200 + 10 * source_lv)  # 计算公式分子部分
        def_range_part2 = (200 + 10 * target_lv) * (1 - def_down) + (200 + 10 * source_lv)  # 分母部分
        def_down = def_range_part1 / def_range_part2
        # 基础伤害*增伤*暴击伤害*抗性*易伤*减伤*防御
        dmg = math.ceil(dmg_base * dmg_boost * crit_range * res_range * dmg_up * dmg_down * def_down)
        # 计算伤害结束后结算击破;击破生效
        return dmg, is_crit, target

    # 单体攻击结算
    def solo(self, stats, atk: int, source, target):
        """
        计算单体伤害函数
        :param stats: 参与计算的属性
        :param atk: 基础倍率
        :param source: 造成伤害的角色
        :param target: 被攻击的角色
        :return: 返回(伤害 是否暴击 目标)的元组
        """
        # 返回伤害值
        return tuple(self.atk(stats, atk, source, target))

    # 范围攻击伤害计算器
    def range(self, source, target, stats, atk, atk_l, atk_r) -> tuple[tuple, tuple | None, tuple | None]:
        """
        计算范围伤害函数
        :param stats: 参与计算的属性
        :param atk: 基础倍率
        :param source: 造成伤害的角色
        :param target: 被攻击的角色
        :param atk_l: 范围伤害左侧倍率
        :param atk_r: 范围伤害右侧倍率
        :return: 返回最多三组(伤害 是否暴击 目标)的元组
        """
        target_left = None
        target_right = None
        l_dmg = None
        r_dmg = None
        # 获取范围伤害的目标
        # 目标元素在怪物列表中
        if target in global_msg.monster_list:
            # 获取元素在列表中的索引
            index = global_msg.monster_list.index(target)
            # 如果元素在头部
            if index == 0:
                target_right = global_msg.monster_list[index + 1]
            # 如果元素在尾部
            elif index == len(global_msg.monster_list) - 1:
                target_left = global_msg.monster_list[index - 1]
            # 元素在中间
            else:
                target_left = global_msg.monster_list[index - 1]
                target_right = global_msg.monster_list[index + 1]
        # 目标元素在人物列表中
        else:
            # 获取元素在列表中的索引
            index = global_msg.person_list.index(target)
            # 如果元素在头部
            if index == 0:
                target_right = global_msg.person_list[index + 1]
            # 如果元素在尾部
            elif index == len(global_msg.person_list) - 1:
                target_left = global_msg.person_list[index - 1]
            # 元素在中间
            else:
                target_left = global_msg.person_list[index - 1]
                target_right = global_msg.person_list[index + 1]
        dmg = self.atk(stats, atk, source, target)
        if target_left:
            l_dmg = self.atk(stats, atk_l, source, target_left)
        if target_right:
            r_dmg = self.atk(stats, atk_r, source, target_right)
        # 返回
        return dmg, l_dmg, r_dmg

    # 全体攻击伤害计算器
    def all(self, source, target, stats, atk, all_atk) -> tuple:
        """
        计算范围伤害函数
        :param stats: 参与计算的属性
        :param atk: 基础倍率
        :param source: 造成伤害的角色
        :param target: 被攻击的角色
        :param all_atk: 全体伤害倍率
        :return: 返回多组(伤害 是否暴击 目标)的元组
        """
        # 创建返回值的列表
        out_list = set()
        # 获取范围伤害的目标
        # 目前元素在怪物
        if target in global_msg.monster_list:
            target_list = global_msg.monster_list
        # 目标元素在人物中
        else:
            target_list = global_msg.person_list
        # 循环
        for target_var in target_list:
            if target_var is not target:
                dmg = self.atk(stats, all_atk, source, target_var)
                out_list.add(dmg)
            else:
                dmg = self.atk(stats, atk, source, target_var)
                out_list.add(dmg)
        return tuple(out_list)

    # 随机攻击伤害计算器
    def random(self, stats, atk: int, source, target):
        # 目前元素在怪物
        if target in global_msg.monster_list:
            target_list = global_msg.monster_list
        # 目标元素在人物中
        else:
            target_list = global_msg.person_list
        # 将目标修改为敌人列表中的随机一个目标
        target = target_list[randint(0, len(target_list))]
        msg = self.atk(stats, atk, source, target)
        return msg


# DoT伤害计算器
class DotCount(Count):
    def dot_type(self, source, target, stats: str, atk_rate, layers=1):
        # 初始化
        self.type = "dot"
        # 各个伤害乘区计算
        # 计算基础伤害乘区,公式:属性*技能倍率
        # 获取基础属性
        stats = sum(getattr(source, stats))
        dmg_base = stats * atk_rate * layers  # 基础伤害等于基础属性 * 攻击倍率 * dot层数
        # 计算增伤,公式:1 + 对应属性的百分比增伤 + 全属性增伤
        dmg_boost = 1 + get_boost(source, "DMG", source.combat_type)
        # 计算抗性伤害乘区,公式:1 - 敌方抗性 + 我方穿透
        target_res = get_boost(target, "RES", source.combat_type)  # 目标抗性
        source_res_pen = get_boost(source, "RES_PEN", source.combat_type)  # 自身穿透
        res_range = 1 - target_res + source_res_pen  # 最终抗性效果
        # 易伤区间,公式:1 + 敌方易伤
        dmg_up = 1 + sum(target.dmg_up)
        # 减伤区间,公式:1 - 敌方减伤
        dmg_down = 1 - sum(target.dmg_down)
        # 防御区间,公式:（（200+10*己方角色等级）/（（200+10*敌方等级）*（1-减防率）+（200+10*己方角色等级）））
        def_down = sum(source.def_PEN) + sum(target.def_down) - sum(target.def_up)  # 减防率
        if def_down > 1:  # 减防率不可大于1
            def_down = 1
        source_lv = source.lv
        target_lv = target.lv
        def_range_part1 = (200 + 10 * source_lv)  # 计算公式分子部分
        def_range_part2 = (200 + 10 * target_lv) * (1 - def_down) + (200 + 10 * source_lv)  # 分母部分
        def_down = def_range_part1 / def_range_part2
        # 基础伤害*增伤*暴击伤害*抗性*易伤*减伤*防御
        dmg = math.ceil(dmg_base * dmg_boost * res_range * dmg_up * dmg_down * def_down)
        return dmg

    # 击破触发伤害计算公式：击破触发伤害=基础伤害（基于角色等级）*属性伤害系数*（(敌方韧度数+2)/4）*（1+击破特攻%）*防御*抗性*易伤*减伤
    # 击破伤害计算
    def break_type(self, source, target, combat):
        # 初始化
        self.combat = combat
        self.type = "break"
        # 各个伤害乘区计算
        # 计算基础伤害乘区,公式:属性*技能倍率
        # 获取基础属性
        dmg_base = break_base_dmg[source.lv] * break_base_rate[combat]
        # 计算抗性伤害乘区,公式:1 - 敌方抗性 + 我方穿透
        target_res = get_boost(target, "RES", source.combat_type)  # 目标抗性
        source_res_pen = get_boost(source, "RES_PEN", source.combat_type)  # 自身穿透
        res_range = 1 - target_res + source_res_pen  # 最终抗性效果
        # 易伤区间,公式:1 + 敌方易伤
        dmg_up = 1 + sum(target.dmg_up)
        # 减伤区间,公式:1 - 敌方减伤
        dmg_down = 1 - sum(target.dmg_down)
        # 防御区间,公式:（（200+10*己方角色等级）/（（200+10*敌方等级）*（1-减防率）+（200+10*己方角色等级）））
        def_down = sum(source.def_PEN) + sum(target.def_down) - sum(target.def_up)  # 减防率
        if def_down > 1:  # 减防率不可大于1
            def_down = 1
        source_lv = source.lv
        target_lv = target.lv
        def_range_part1 = (200 + 10 * source_lv)  # 计算公式分子部分
        def_range_part2 = (200 + 10 * target_lv) * (1 - def_down) + (200 + 10 * source_lv)  # 分母部分
        def_down = def_range_part1 / def_range_part2
        # 韧性条乘区
        toughness_range = (sum(target.toughness) + 20) / 40  # 以正常普通攻击削减韧性值=10为标准计算
        # 击破特效
        break_effect = sum(source.Break_Effect)
        # 基础伤害*韧性条系数*抗性*易伤*减伤*防御*击破特效
        dmg = math.ceil(dmg_base * toughness_range * res_range * dmg_up * dmg_down * def_down * break_effect)
        return dmg

    # 击破dot伤害计算
    # 击破持续伤害=基础伤害（基于角色等级）*属性持续伤害系数*（1+击破特攻%）*防御*抗性*易伤*减伤
    def break_dot_type(self, source, target, combat, layers=1):
        # 初始化
        self.combat = combat
        self.type = "break_dot"
        # 更新全局角色的buff,效果等状态
        # 各个伤害乘区计算
        # 计算基础伤害乘区,公式:属性*技能倍率
        # 获取基础属性
        if combat == "物理":
            if 2 in target.monster_type or 3 in target.monster_type:  # 若为精英怪或boss
                dmg_base = sum(target.HP) * 0.16 * break_dot_rate[combat]  # 基础伤害为最大生命值0.16
            else:
                dmg_base = sum(target.HP) * 0.07 * break_dot_rate[combat]  # 基础伤害为最大生命值0.07
        else:
            dmg_base = break_base_dmg[source.lv] * break_dot_rate[combat] * layers  # 基础伤害 * 倍率 * 层数

        # 计算抗性伤害乘区,公式:1 - 敌方抗性 + 我方穿透(不确定是否吃这个穿透)
        target_res = get_boost(target, "RES", source.combat_type)  # 目标抗性
        source_res_pen = get_boost(source, "RES_PEN", source.combat_type)  # 自身穿透
        res_range = 1 - target_res + source_res_pen  # 最终抗性效果
        # 易伤区间,公式:1 + 敌方易伤
        dmg_up = 1 + sum(target.dmg_up)
        # 减伤区间,公式:1 - 敌方减伤
        dmg_down = 1 - sum(target.dmg_down)
        # 防御区间,公式:（（200+10*己方角色等级）/（（200+10*敌方等级）*（1-减防率）+（200+10*己方角色等级）））
        def_down = sum(source.def_PEN) + sum(target.def_down) - sum(target.def_up)  # 减防率
        if def_down > 1:  # 减防率不可大于1
            def_down = 1
        source_lv = source.lv
        target_lv = target.lv
        def_range_part1 = (200 + 10 * source_lv)  # 计算公式分子部分
        def_range_part2 = (200 + 10 * target_lv) * (1 - def_down) + (200 + 10 * source_lv)  # 分母部分
        def_down = def_range_part1 / def_range_part2
        # 击破特效
        break_effect = sum(source.Break_Effect)
        # 基础伤害*抗性*易伤*减伤*防御*击破特效
        dmg = math.ceil(dmg_base * res_range * dmg_up * dmg_down * def_down * break_effect)
        return dmg


# 击破基础伤害表
break_base_dmg = {
    1: 54,
    2: 58,
    3: 62,
    4: 67.53,
    5: 70.51,
    6: 73.52,
    7: 76.57,
    8: 79.64,
    9: 82.74,
    10: 85.87,
    11: 91.49,
    12: 97.07,
    13: 102.59,
    14: 108.06,
    15: 113.47,
    16: 118.84,
    17: 124.15,
    18: 129.41,
    19: 134.62,
    20: 139.77,
    21: 149.33,
    22: 158.80,
    23: 168.18,
    24: 177.46,
    25: 186.65,
    26: 195.75,
    27: 204.75,
    28: 213.66,
    29: 222.48,
    30: 231.20,
    31: 246.43,
    32: 261.18,
    33: 275.47,
    34: 289.32,
    35: 302.73,
    36: 315.71,
    37: 328.29,
    38: 340.47,
    39: 352.26,
    40: 363.67,
    41: 408.12,
    42: 451.79,
    43: 494.68,
    44: 536.82,
    45: 578.22,
    46: 618.92,
    47: 658.91,
    48: 698.23,
    49: 736.89,
    50: 774.90,
    51: 871.06,
    52: 964.87,
    53: 1056.42,
    54: 1145.79,
    55: 1233.06,
    56: 1318.30,
    57: 1401.58,
    58: 1482.96,
    59: 1562.52,
    60: 1640.31,
    61: 1752.32,
    62: 1861.90,
    63: 1969.90,
    64: 2074.07,
    65: 2176.80,
    66: 2288.39,
    67: 2375.91,
    68: 2472.42,
    69: 2566.97,
    70: 2659.64,
    71: 2780.30,
    72: 2898.60,
    73: 3014.60,
    74: 3128.37,
    75: 3239.98,
    76: 3349.98,
    77: 3456.92,
    78: 3562.38,
    79: 3665.91,
    80: 3767.55
}
# 击破属性倍率
break_base_rate = {
    "冰": 1,
    "物理": 2,
    "火": 2,
    "雷": 1,
    "风": 1.5,
    "量子": 0.5,
    "虚数": 0.5

}
# 击破属性dot倍率
break_dot_rate = {
    "冰": 1,
    "物理": 0,
    "火": 1,
    "雷": 2,
    "风": 1,
    "量子": 0.6,
    "虚数": 0

}
# 实例化
# 常规伤害
dmg_count = DMGCount()
# dot伤害
dot_count = DotCount()
