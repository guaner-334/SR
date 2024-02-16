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
            elif type(stats) is int:
                setattr(instance, i, int(stats_dic[i]))
            else:
                setattr(instance, i, stats_dic[i])
    return instance


# 希儿
seele = build_character_data("希儿")


# 希儿buff
# 战技buff
def sheathed_blade(buff: Buff, msg: str):
    max_time = 1
    if buff.source.eidolons >= 2:
        max_time = 2
    # 添加buff
    if msg == "add":
        if not buff.is_working:
            # 状态更新
            send_action.get_set.add(buff)
            buff.is_working = True
        if buff.times < max_time:
            buff.source.change_stats(buff.source, "SPD", 0, 0.25)
            buff.times += 1
            buff.leave_turn = 2
        else:
            buff.leave_turn = 2
    # 移除buff
    elif msg == "end":
        buff.source.change_stats(buff.source, "SPD", 0, -0.25 * buff.times)
        # 状态更新
        buff.times = 0
        send_action.get_set.remove(buff)
        buff.is_working = False
    # 回合结束
    elif msg == "msg":
        if buff.msg.source == buff.source:
            if buff.msg.entity == "turn_star":
                buff.turn_off()


seele_sheathed_blade = Buff(seele, sheathed_blade)


# 希儿增幅buff
def buffed_of_seele(buff: Buff, msg: str):
    lv = buff.source.talent_lv
    if buff.source.eidolons >= 3:
        lv += 2
    # 添加buff
    if msg == "add" and not buff.is_working:
        # 状态更新
        buff.leave_turn = 1
        buff.is_working = True
        send_action.get_set.add(buff)
        # 添加buff
        __list = [0.4, 0.44, 0.48, 0.52, 0.56, 0.6, 0.65, 0.7, 0.75, 0.8, 0.84, 0.88, 0.92, 0.96, 1]
        buff.source.change_stats(buff.source, "DMG_Boost", __list[lv - 1], 0)
    # 移除buff
    elif msg == "end":
        __list = [0.4, 0.44, 0.48, 0.52, 0.56, 0.6, 0.65, 0.7, 0.75, 0.8, 0.84, 0.88, 0.92, 0.96, 1]
        buff.source.change_stats(buff.source, "DMG_Boost", -__list[lv - 1], 0)
        # 状态更新
        buff.is_working = False
        send_action.get_set.remove(buff)
    # 回合结束
    elif msg == "msg":
        if buff.msg.source == buff.source:
            if buff.msg.entity == "turn_star":
                buff.turn_off()


seele_buffed_of_seele = Buff(seele, buffed_of_seele)


# 希儿6星魂buff
def shattering_shambles(buff: Buff, msg: str):
    # 添加buff
    if msg == "add" and not buff.is_working:
        # 状态更新
        buff.leave_turn = 1
        buff.is_working = True
        send_action.get_set.add(buff)
    # 移除buff
    elif msg == "end":
        # 状态更新
        buff.is_working = False
        send_action.get_set.remove(buff)
    # 收到消息
    elif msg == "msg":
        # 目标回合结束
        if buff.msg.target == buff.target:
            if buff.msg.entity == "turn_star":
                buff.turn_off()
            if buff.msg.entity.is_atk:
                lv = buff.source.ultimate_lv + 2
                __list = [2.55, 2.72, 2.89, 3.06, 3.23, 3.40, 3.61, 3.82, 4.03, 4.25, 4.42, 4.59, 4.76, 4.93, 5.10]
                rate = __list[lv - 1]
                # 希儿终结技的buff伤害结算
                send_action.send(buff.source, buff.target, "附加伤害")  # 发送通知
                dmg = dmg_count.solo("ATK", rate, buff.source, buff.target)
                make_dmg(buff.source, dmg)
                buff.source.temp_temp_stats()  # 清空临时属性
                buff.history_dmg += count_dmg(dmg)


seele_shattering_shambles = Debuff(seele, shattering_shambles)


# 希儿普通攻击
def seele_basis_atk(entity_msg: Entity):
    # 创建击杀数
    kill_num = 0
    # 产出1点战技点
    global_msg.recover_skill_point(entity_msg.source)
    # 恢复20点能量
    entity_msg.source.energy_recovery(entity_msg.source, True, 20, 0)
    # 获取技能等级
    lv = entity_msg.source.basic_atk_lv
    if entity_msg.source.eidolons >= 5:
        lv += 1
    rate = lv * 0.1 + 0.4
    # 希儿伤害分为两段 比例为3:7
    for i in 0.3, 0.7:
        send_action.send(entity_msg.source, entity_msg.target, "攻击")  # 发送通知
        dmg = dmg_count.solo("ATK", rate * i, entity_msg.source, entity_msg.target)
        kill_num += make_dmg(entity_msg.source, dmg)  # 伤害结算,如有击杀则统计
        entity_msg.source.temp_temp_stats()  # 清空临时属性
    # 进行击破结算
    if entity_msg.target.is_break(entity_msg.source, 10 * entity_msg.source.Break_rate):
        dmg = dot_count.break_type(entity_msg.source, entity_msg.target, "量子")
        make_dmg(entity_msg.source, dmg)
    # 状态更新
    entity_msg.kill_num += kill_num
    # 击杀大于0,并且不在额外回合触发额外回合
    if kill_num > 0 and entity_msg.source.exmove is False:
        character_exmove(seele)
    return 0  # 返回0,行动结束


# 希儿战技
def seele_skill(entity_msg: Entity):
    # 创建击杀数
    kill_num = 0
    # 消耗1点战技点
    global_msg.ues_skill_point(entity_msg.source)
    # 添加战技buff
    seele_sheathed_blade.add_buff(entity_msg.source)
    # 恢复30点能量
    entity_msg.source.energy_recovery(entity_msg.source, True, 30, 0)
    # 技能主体
    lv = entity_msg.source.skill_lv
    if entity_msg.source.eidolons >= 3:
        lv += 2
    rate = lv * 0.11 + 0.99
    # 希儿战技伤害分为4段 比例为2:1:1:6
    for i in 0.2, 0.1, 0.1, 0.6:
        send_action.send(entity_msg.source, entity_msg.target, "攻击")  # 发送通知
        dmg = dmg_count.solo("ATK", rate * i, entity_msg.source, entity_msg.target)
        kill_num += make_dmg(entity_msg.source, dmg)  # 伤害结算,如有击杀则统计
        entity_msg.source.temp_temp_stats()  # 清空临时属性
    # 进行击破结算
    if entity_msg.target.is_break(entity_msg.source, 10 * entity_msg.source.Break_rate):
        dmg = dot_count.break_type(entity_msg.source, entity_msg.target, "量子")
        make_dmg(entity_msg.source, dmg)
    # 状态更新
    entity_msg.kill_num += kill_num
    # 击杀大于0,并且不在额外回合触发额外回合
    if kill_num > 0 and entity_msg.source.exmove is False:
        character_exmove(seele)
    return 0  # 返回0,行动结束


# 希儿终结技
def seele_ultimate(entity_msg: Entity):
    # 创建击杀数
    kill_num = 0
    # 添加buff
    seele_buffed_of_seele.add_buff(entity_msg.source)
    # 恢复5点能量
    entity_msg.source.energy_recovery(entity_msg.source, True, 5, 0)
    # 技能主体
    lv = entity_msg.source.ultimate_lv
    if entity_msg.source.eidolons >= 5:
        lv += 2
    __list = [2.55, 2.72, 2.89, 3.06, 3.23, 3.40, 3.61, 3.82, 4.03, 4.25, 4.42, 4.59, 4.76, 4.93, 5.10]
    rate = __list[lv - 1]
    # 希儿终结技伤害分为1段
    # 第一段攻击
    send_action.send(entity_msg.source, entity_msg.target, "攻击")  # 发送通知
    dmg = dmg_count.solo("ATK", rate, entity_msg.source, entity_msg.target)
    kill_num += make_dmg(entity_msg.source, dmg)  # 伤害结算,如有击杀则统计
    entity_msg.source.temp_temp_stats()  # 清空临时属性
    # 进行击破结算
    if entity_msg.target.is_break(entity_msg.source, 10 * entity_msg.source.Break_rate):
        dmg = dot_count.break_type(entity_msg.source, entity_msg.target, "量子")
        make_dmg(entity_msg.source, dmg)
    # 6星魂效果
    if entity_msg.source.eidolons >= 6:
        seele_shattering_shambles.add_buff(entity_msg.target)
    # 状态更新
    entity_msg.kill_num += kill_num
    # 击杀触发再现,终结技不需要判断是否为已再现
    if kill_num > 0:
        character_move(seele)
    return 0


# 希儿天赋
def seele_talent(self: Effect, msg):
    if msg == "add":
        send_stats.get_set.add(self)
    if msg == "get_msg":
        if self.msg.target == self.source:
            if self.msg.stats == "in_death" and self.msg.change is True:  # 希儿消灭敌方时，进入增幅状态。
                seele_buffed_of_seele.add_buff(self.source)


# 希儿额外能力
def seele_bonus_ability(self: Effect, msg):
    if msg == "add":
        send_stats.get_set.add(self)
        send_action.get_set.add(self)
    if msg == "get_msg":
        if self.msg.entity == seele_basis_atk_entity:  # 释放普通攻击后行动提前20%
            self.source.change_stats(self.source, "action_point", 0, 0.2)
        if seele_buffed_of_seele.is_working:  # 增幅状态下希儿的量子属性抗性穿透提高20%
            self.source.change_temp_stats(self.source, "Quantum_RES_PEN", 0.2, 0)
        if self.source.eidolons >= 4:
            if self.msg.stats == "in_death" and self.msg.change is True:  # 希儿消灭敌方目标时，自身恢复15点能量。
                self.source.energy_recovery(self.source, True, 15, 0)


# 希儿额外能力属性
def seele_bonus_stats(self, msg):
    if msg == "add":
        self.target.change_stats(self.target, "ATK", 0, 0.28)
        self.target.change_stats(self.target, "CRIT_DMG", 0.24, 0)
        self.target.change_stats(self.target, "DEF", 0, 0.125)


seele_basis_atk_entity = Entity(1, "普通攻击:强袭", "希儿", seele_basis_atk, True, False, seele)  # 希儿普通攻击实体
seele_basis_atk_entity.type = "basic_atk"
seele_skill_entity = Entity(2, "战技:归刃", "希儿", seele_skill, True, False, seele)  # 希儿战技实体
seele_basis_atk_entity.type = "skill"
seele_ultimate_entity = Entity(3, "终结技:乱蝶", "希儿", seele_ultimate, True, False, seele)  # 希儿终结技实体
seele_basis_atk_entity.type = "ultimate"
seele_talent_entity = Effect(seele, seele_talent)  # 希儿天赋
seele_bonus_ability_effect = Effect(seele, seele_bonus_ability)  # 希儿额外能力效果
seele_seele_bonus_stats = Effect(seele, seele_bonus_stats)  # 希儿额外能力属性加成效果

# 组装
seele.basic_atk_entity = seele_basis_atk_entity
seele.skill_entity = seele_skill_entity
seele.ultimate_entity = seele_ultimate_entity
seele.talent_entity = seele_talent_entity
seele.bonus_ability = seele_bonus_ability_effect
seele.bonus_stats = seele_seele_bonus_stats
