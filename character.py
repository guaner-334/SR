import math
from Star_Rail_damage_simulation.msg import send_action
from Star_Rail_damage_simulation.msg import send_stats
from Star_Rail_damage_simulation.msg import SendAction
from Star_Rail_damage_simulation.msg import SendStats
from Star_Rail_damage_simulation.msg import global_msg


# 角色行动
def character_move(character):
    """
    角色回合行动
    :param character: 行动的角色
    :return:
    """
    print(f"【回合开始】")
    if global_msg.is_auto:  # 若自动战斗开启
        print("未开启战斗")
    elif character.character_type == "person":
        print(f"人物【{character.name}】开始行动")
        while True:
            print("输入[e]使用战技,输入[q]使用普通攻击")
            print(f"当前剩余战技点{global_msg.battle_skill_point}")
            player_input = input()
            if player_input == "e":
                for i in global_msg.monster_list:
                    print(i.name)
                print("输入数字选择对应目标,若超出默认选择最大值")
                n = int(input())
                if n >= len(global_msg.monster_list):
                    n = len(global_msg.monster_list) - 1
                else:
                    n -= 1
                t = global_msg.monster_list[n]
                if character.skill(t) == 0:
                    return
            elif player_input == "q":
                for i in global_msg.monster_list:
                    print(i.name)
                print("输入数字选择对应目标,若超出默认选择最大值")
                n = int(input())
                if n >= len(global_msg.monster_list):
                    n = len(global_msg.monster_list) - 1
                else:
                    n -= 1
                t = global_msg.monster_list[n]
                if character.basic_atk(t) == 0:
                    return
            else:
                print("无效输入")
    elif character.character_type == "monster":
        print(f"怪物【{character.name}】开始行动")
        character.auto_fight()
        return
    elif character.character_type == "summons":
        print(f"召唤物【{character.name}】开始行动")
        character.auto_fight()
        return


# 角色额外行动
def character_exmove(character):
    """
    角色额外回合行动,开始时会将角色exmove参数置为Turn,结束前会将参数置为False
    :param character: 行动的角色
    :return:
    """
    print(f"【{character.name}】开始额外行动")
    character.exmove = True
    if global_msg.is_auto:  # 若自动战斗开启
        character.auto_fight()
        character.exmove = False
        return
    elif character.character_type == "person":
        while True:
            print("输入[e]使用战技,输入[q]使用普通攻击")
            print(f"当前剩余战技点{global_msg.battle_skill_point}")
            player_input = input()
            if player_input == "e":
                if character.skill() == 0:
                    character.exmove = False
                    return
            elif player_input == "q":
                if character.basic_atk() == 0:
                    character.exmove = False
                    return
            else:
                print("无效输入")
    elif character.character_type == "monster":
        character.auto_fight()
        character.exmove = False
        return
    elif character.character_type == "summons":
        character.auto_fight()
        character.exmove = False
        return


# 人物通用模板
class Character:
    """
    人物属性通用模板
    """

    # 人物角色相关参数
    def __init__(self):
        # 所有属性均以列表的形式按[基础值,额外值,临时值],百分比属性保留小数点后3位
        # 基础属性
        self.HP = [100, 0, 0]
        self.toughness = [100, 0, 0]  # 韧性值
        self.ATK = [100, 0, 0]
        self.DEF = [100, 0, 0]
        self.SPD = [100, 0, 0]

        # 进阶属性
        self.CRIT_rate = [0.050, 0.000, 0.000]  # 暴击率
        self.CRIT_DMG = [0.050, 0.000, 0.000]  # 暴击伤害
        self.Break_Effect = [0.050, 0.000, 0.000]  # 击破特攻
        self.Break_rate = [1, 0, 0]  # 击破效率
        self.Outgoing_Healing_Boost = [0.050, 0.000, 0.000]  # 医疗加成
        self.Energy = 100  # 最大能量
        self.Energy_Regeneration_Rate = [1.000, 0.000, 0.000]  # 能量回复效率
        self.Effect_Hit_Rate = [0.050, 0.000, 0.000]  # 效果命中
        self.Effect_RES = [0.050, 0.000, 0.000]  # 效果抵抗
        # 伤害加成
        self.DMG_Boost = [0.000, 0.000, 0.000]
        self.Physical_DMG_Boost = [0.000, 0.000, 0.000]
        self.Fire_DMG_Boost = [0.000, 0.000, 0.000]
        self.Ice_DMG_Boost = [0.000, 0.000, 0.000]
        self.Lightning_DMG_Boost = [0.000, 0.000, 0.000]
        self.Wind_DMG_Boost = [0.000, 0.000, 0.000]
        self.Quantum_DMG_Boost = [0.000, 0.000, 0.000]
        self.Imaginary_DMG_Boost = [0.000, 0.000, 0.000]
        # 伤害抵抗
        self.RES_Boost = [0.000, 0.000, 0.000]
        self.Physical_RES_Boost = [0.000, 0.000, 0.000]
        self.Fire_RES_Boost = [0.000, 0.000, 0.000]
        self.Ice_RES_Boost = [0.000, 0.000, 0.000]
        self.Lightning_RES_Boost = [0.000, 0.000, 0.000]
        self.Wind_RES_Boost = [0.000, 0.000, 0.000]
        self.Quantum_RES_Boost = [0.000, 0.000, 0.000]
        self.Imaginary_RES_Boost = [0.000, 0.000, 0.000]
        # 抵抗穿透
        self.RES_PEN = [0.000, 0.000, 0.000]
        self.Physical_RES_PEN = [0.000, 0.000, 0.000]
        self.Fire_RES_PEN = [0.000, 0.000, 0.000]
        self.Ice_RES_PEN = [0.000, 0.000, 0.000]
        self.Lightning_RES_PEN = [0.000, 0.000, 0.000]
        self.Wind_RES_PEN = [0.000, 0.000, 0.000]
        self.Quantum_RES_PEN = [0.000, 0.000, 0.000]
        self.Imaginary_RES_PEN = [0.000, 0.000, 0.000]
        # 易伤/减伤/减防/无视防御
        self.dmg_up = [0.000, 0.000, 0.000]  # 易伤
        self.dmg_down = [0.100, 0.000, 0.000]  # 默认自带10%减伤,击破后消失
        self.def_up = [0.000, 0.000, 0.000]  # 防御增加
        self.def_down = [0.000, 0.000, 0.000]  # 防御下降
        self.def_PEN = [0.000, 0.000, 0.000]  # 防御穿透
        # 其他属性
        self.name = "木桩1号"
        self.e_name = "test"
        self.id = 0
        self.lv = 80
        self.eidolons = 0  # 星魂
        self.paths = "巡猎"  # 命途
        self.combat_type = "火"  # 属性
        self.weakness = {"火", "物理"}  # 弱点
        self.character_type: str = "person"  # 角色类型,"person\monster\summons"
        self.monster_type: set[0, 1, 2, 3] = {0}  # 怪物类型,只有怪物才会有该属性,默认插入0, 1 普通; 2 精英; 3 首领,支持多个类型
        # 状态属性
        self.buff_set: set = set()
        self.debuff_set: set = set()
        self.halo_set: set = set()  # 光环:不随回合结束消失的buff
        self.effect_set: set = set()  # 效果:满足特定条件触发,不随回合结束消失
        self.dot_set: set = set()  # 持续伤害
        self.in_break: bool = False  # 击破状态
        self.in_death: bool = False  # 死亡状态
        # 实时属性
        self.cur_HP = 100  # 当前生命值
        self.cur_toughness = 100  # 当前韧性
        self.cur_energy = 50  # 当前能量
        self.action_point = 0  # 行动值
        # 技能等级
        self.basic_atk_lv = 6
        self.skill_lv = 10
        self.ultimate_lv = 10
        self.talent_lv = 10
        # 技能实体
        self.basic_atk_entity = None
        self.skill_entity = None
        self.ultimate_entity = None
        self.talent_entity = None
        # 额外能力
        self.bonus_ability = None
        self.bonus_stats = None
        # 秘技
        self.technique = None
        # 参数寄存,根据角色自身需求取用
        self.num_1 = 0
        self.num_2 = 0
        self.num_3 = 0
        self.exmove = False  # 是否处于额外回合

    # 接收行动通知
    def get_action_msg(self, msg_self: SendAction):
        """
        :param msg_self: 行动通知
        :return:
        """
        pass

    # 接收属性变化通知
    def get_stats_msg(self, msg_self: SendStats):
        """
        :param msg_self:  状态通知
        :return:
        """
        pass

    # 修改通用属性
    def change_stats(self, source, stats: str, num: int | float, pct: float):
        """
        修改对象的额外属性
        :param source: 输入产生本次修改的角色
        :param stats: 修改的属性类型
        :param num: 修改数值
        :param pct: 修改百分比,小数形式
        :return:
        """
        if stats not in {"HP", "cur_HP", "cur_energy", "cur_toughness", "action_point", "ATK", "DEF", "SPD"}:
            stats_list = getattr(self, stats, 0)  # 获取对应属性的数值列表
            stats_list[1] += num + stats_list[0] * pct  # 数值列表的额外属性增加数值(为负则减少);不取整
            setattr(self, stats, stats_list)  # 将修改后的属性更新值人物面板中
            send_stats.send(source, self, stats, num + stats_list[0] * pct)  # 发送属性修改通知
        elif stats in {"ATK", "DEF", "SPD"}:  # 若修改类型为最大生命值
            stats_list = getattr(self, stats, 0)  # 获取对应属性的数值列表
            stats_list[1] += math.ceil(num + stats_list[0] * pct)  # 数值列表的额外属性增加数值(为负则减少);取整
            setattr(self, stats, stats_list)  # 将修改后的属性更新值人物面板中
            send_stats.send(source, self, stats, math.ceil(num + stats_list[0] * pct))  # 发送属性修改通知
        elif stats == "HP":  # 若修改类型为最大生命值
            change_num = math.ceil(num + pct * self.HP[0])
            self.HP[1] += change_num
            if sum(self.HP) < self.cur_HP:  # 若生命值上限小于当前生命值
                change_hp = sum(self.HP) - self.cur_HP  # 计算差值
                self.cur_HP = sum(self.HP)  # 修改当前生命值为生命值上限
                send_stats.send(source, self, "cur_HP", change_hp)  # 发送当前生命值变化通知
            send_stats.send(source, self, stats, change_num)  # 发送属性修改通知
        elif stats == "cur_HP":  # 若修改类型为当前生命值
            if num or pct > 0:  # 若修改类型为增加(一般而言num和pct符号是一致的)
                change_num = math.ceil(self.HP[0] * pct + num)
                if change_num + self.cur_HP >= sum(self.HP):  # 医疗溢出
                    self.cur_HP = sum(self.HP)
                    # 发送通知
                    send_stats.send(source, self, "cur_HP", sum(self.HP) - self.cur_HP)
                else:
                    self.cur_HP += change_num
                    # 发送通知
                    send_stats.send(source, self, "cur_HP", change_num)
            else:  # 若增加值为负数
                change_hp = math.ceil(self.cur_HP * pct + num)  # 创建生命值数值修改变量;固定和当前生命值百分比变化;向上取整
                self.cur_HP += change_hp  # 当前生命值修改
                send_stats.send(source, self, "cur_HP", change_hp)  # 发送通知
                if self.cur_HP <= 0:  # 若变更后生命值清空
                    self.death(source)
        elif stats == "cur_energy":  # 若修改类型为当前能量值
            change_ep = math.ceil(num + self.Energy * pct)  # 能量增加数值
            self.cur_energy += change_ep  # 修改能量值
            if self.cur_energy > self.Energy:  # 若能量增加后超出了上限
                change_ep -= self.cur_energy - self.Energy  # 计算能量实际修改值
                self.cur_energy = self.Energy  # 将当前能量重置为能量上限
                send_stats.send(source, self, "cur_energy", change_ep)  # 发送通知能量变化
            else:
                if self.cur_energy < 0:  # 若当前能量小于0
                    change_ep += self.cur_energy
                    self.cur_energy = 0  # 将当前能量重置为0
                send_stats.send(source, self, "cur_energy", change_ep)  # 发送通知能量变化
        elif stats == "cur_toughness":  # 若修改类型为当前韧性条
            var_toughness = self.cur_toughness
            self.cur_toughness -= num
            self.cur_toughness -= math.ceil(self.toughness[0] * pct + self.toughness[1] * pct + self.toughness[2] * pct)
            change_toughness = var_toughness - self.cur_toughness
            if self.cur_toughness <= 0:
                self.cur_toughness = 0
                self.in_break = True
                send_stats.send(source, self, stats, change_toughness)
                send_stats.send(source, self, "in_break", True)
            else:
                send_stats.send(source, self, stats, change_toughness)
        elif stats == "action_point":  # 若修改类型为行动值
            self.action_point += num
            self.action_point += pct * 10000

    # 修改临时属性
    def change_temp_stats(self, source, stats: str, num: int, pct: float):
        """
        修改目标对象的临时属性
        :param source: 来源
        :param stats: 类型
        :param num: 数值
        :param pct: 百分比
        :return:
        """
        stats_list = getattr(self, stats, 0)  # 获取对应属性的数值列表
        stats_list[2] += math.ceil(num + stats_list[0] * pct)  # 数值列表的额外属性增加数值(为负则减少);向上取整
        setattr(self, stats, stats_list)  # 将修改后的属性更新值人物面板中
        send_stats.send(source, self, stats, math.ceil(num + stats_list[0] * pct))  # 发送属性修改通知

    # 战斗开始
    def battle_star(self):
        """
        战斗开始时运行,并且发送通知
        :return:
        """
        # 技能实体
        self.talent_entity.add_effect(self)
        # 天赋
        self.bonus_ability.add_effect(self)
        self.bonus_stats.add_effect(self)

    # 波次开始
    def round_star(self):
        """
        波次开始时运行,并且发送通知
        :return:
        """
        send_action.send(self, None, "round_star")

    # 回合开始
    def turn_star(self):
        """
        回合开始时运行,并且发送通知
        :return:
        """
        send_action.send(self, None, "turn_star")

    # 战斗结束
    def battle_end(self):
        """
        战斗结束时运行,并且发送通知
        :return:
        """
        send_action.send(self, None, "battle_end")

    # 轮次结束
    def round_end(self):
        """
        轮次结束时运行,并且发送通知
        :return:
        """
        send_action.send(self, None, "round_end")

    # 回合结束
    def turn_end(self):
        """
        回合结束时运行,并且发送通知
        :return:
        """
        send_action.send(self, None, "turn_end")

    # 是否被击破判断
    def is_break(self, source, break_num: int):
        """
        输入来源和击破数值,同时判断是否被击破,若被击破则运行击破数值
        :param source: 造成击破的来源
        :param break_num: 击破数值
        :return:
        """
        if self.cur_toughness >= 0:
            self.change_stats(source, "cur_toughness", break_num, 0)
            if self.in_break:
                send_stats.send(self, source, "is_break")
                return True
            else:
                return False

    # 清空临时属性
    def temp_temp_stats(self):
        """
        清空人物身上的临时属性
        :return:
        """
        for key, value in self.__dict__.items():  # 以字典的形式遍历所有属性
            if isinstance(value, list):  # 判断当前值是否为列表
                value[2] = 0  # 将临时属性置空

    # 普通攻击
    def basic_atk(self, target) -> int:
        """
        执行普通攻击
        :return: 返回0或1,0代表行动结束,1代表行动继续
        """
        if self.basic_atk_entity:
            return self.basic_atk_entity.work(target)
        else:
            return 0

    # 战技
    def skill(self, target) -> int:
        """
        执行战技
        :return: 返回0或1,0代表行动结束,1代表行动继续
        """
        if self.skill_entity:
            return self.skill_entity.work(target)
        else:
            return 0

    # 终结技
    def ultimate(self, target):
        if self.ultimate_entity:
            return self.ultimate_entity.work(target)
        else:
            return 0

    # 被添加buff
    def add_buff(self, buff, source):
        if buff not in self.buff_set:
            self.buff_set.add(buff)
            buff.add(self, source)

    # 自动战斗策略
    def auto_fight(self):
        """
        自动战斗策略
        :return:
        """
        pass

    # 死亡
    def death(self, source):
        """
        死亡方法
        :return:
        """
        self.in_death = True  # 变更死亡状态为真
        send_stats.send(self, source, "in_death", True)  # 发送死亡通知

    # 能量恢复
    def energy_recovery(self, source, is_bonus, num, pct):
        if is_bonus:
            rate = sum(self.Energy_Regeneration_Rate)
            self.change_stats(source, "cur_energy", num * rate, pct * rate)
        else:
            self.change_stats(source, "cur_energy", num, pct)
