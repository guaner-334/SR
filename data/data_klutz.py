import pandas as pd
from Star_Rail_damage_simulation.character import Character
from Star_Rail_damage_simulation.character import character_move
from Star_Rail_damage_simulation.character import character_exmove
from Star_Rail_damage_simulation.msg import send_action
from Star_Rail_damage_simulation.msg import send_stats
from Star_Rail_damage_simulation.msg import global_msg
from Star_Rail_damage_simulation.dmgCount import dmg_count
from Star_Rail_damage_simulation.dmgCount import dot_count
from Star_Rail_damage_simulation.entity import count_dmg
from Star_Rail_damage_simulation.entity import Entity
from Star_Rail_damage_simulation.entity import make_dmg
from Star_Rail_damage_simulation.buff import Buff
from Star_Rail_damage_simulation.buff import Debuff
from Star_Rail_damage_simulation.effect import Effect


# 创建人物数据
def build_character_data(name: str):
    df = pd.read_excel("data/人物属性.xlsx")
    stats_name = []
    for i in df["属性名"]:
        stats_name.append(i)
    # 获取第一行的数据
    first_row = df.iloc[0]
    stats_list = []
    # 遍历每一列，判断第一行的值是否满足条件
    for column in df.columns:
        if first_row[column] == name:
            for i in (df[column]):
                if pd.isnull(i):  # 判断数据是否为空
                    stats_list.append("")
                else:
                    stats_list.append(i)
            break
    stats_dic = dict(zip(stats_name, stats_list))
    instance = Character()
    for i in stats_dic:
        if stats_dic[i] != "":
            stats = getattr(instance, i)
            if type(stats) is list:
                stats[0] = stats_dic[i]
                setattr(instance, i, stats)
            else:
                setattr(instance, i, stats_dic[i])
    return instance


# 希儿
klutz = build_character_data("木头人")


# 木头人buff
def klutz_talent(a, b):
    pass


def klutz_bonus_ability(a, b):
    pass


def klutz_bonus_stats(a, b):
    pass


# 木头人普通攻击
def klutz_basis_atk(entity_msg: Entity):
    # 创建击杀数
    kill_num = 0
    # 产出1点战技点
    global_msg.recover_skill_point(entity_msg.source)
    # 恢复20点能量
    entity_msg.source.energy_recovery(entity_msg.source, True, 20, 0)
    # 伤害结算
    send_action.send(entity_msg.source, entity_msg.target, "攻击")  # 发送通知
    dmg = dmg_count.solo("ATK", 1, entity_msg.source, entity_msg.target)
    kill_num += make_dmg(entity_msg.source, dmg)  # 伤害结算,如有击杀则统计
    entity_msg.source.temp_temp_stats()  # 清空临时属性
    # 状态更新
    entity_msg.kill_num += kill_num
    return 0  # 返回0,行动结束


# 木头人战技
def klutz_skill(entity_msg: Entity):
    pass
    return 0  # 返回0,行动结束


# 木头人终结技
def klutz_ultimate(entity_msg: Entity):
    pass
    return 0


klutz_basis_atk_entity = Entity(1, "普通攻击:强袭", "希儿", klutz_basis_atk, True, False, klutz)  # 希儿普通攻击实体
klutz_skill_entity = Entity(2, "战技:归刃", "希儿", klutz_skill, True, False, klutz)  # 希儿战技实体
klutz_ultimate_entity = Entity(3, "终结技:乱蝶", "希儿", klutz_ultimate, True, False, klutz)  # 希儿终结技实体
klutz_talent_entity = Effect(klutz, klutz_talent)  # 希儿天赋
klutz_bonus_ability_effect = Effect(klutz, klutz_bonus_ability)  # 希儿额外能力效果
klutz_seele_bonus_stats = Effect(klutz, klutz_bonus_stats)  # 希儿额外能力属性加成效果

# 组装
klutz.basic_atk_entity = klutz_basis_atk_entity
klutz.skill_entity = klutz_skill_entity
klutz.ultimate_entity = klutz_ultimate_entity
klutz.talent_entity = klutz_talent_entity
klutz.bonus_ability = klutz_bonus_ability_effect
klutz.bonus_stats = klutz_seele_bonus_stats
