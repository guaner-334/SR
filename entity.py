from Star_Rail_damage_simulation.msg import send_action
from Star_Rail_damage_simulation.msg import global_msg

# 行动实体分类集合
# 攻击实体集合
atk_entity = {None}
# 追加攻击实体集合
append_entity = {None}


# 行动实体模板
class Entity:
    """
    行动实体的模板
    """

    def __init__(self,
                 _id: int,
                 name: str,
                 character_name: str,
                 action_function,
                 is_atk: bool,
                 is_append: bool,
                 source=None):
        """
        行为实体输入关键参数,来源可以为空
        :param _id:实体id,用于记录,没有做去重判断
        :param name:行动名称,打印使用
        :param character_name:人物名称,打印使用
        :param action_function:实际运行函数
        :param is_atk:是否为攻击
        :param is_append:是否为追加攻击
        :param source:来源
        """
        self.id = _id
        self.name = name
        self.character_name = character_name
        self.function = action_function
        self.source = source  # 发起人,必填
        self.target = None  # 目标,可以为空
        self.cache = None  # 数据缓存
        self.combat_type = None  # 属性
        self.type = None  # basic_atk/skill/ultimate/others
        self.is_atk = is_atk  # 是否为攻击动作
        self.is_append = is_append  # 是否为追加攻击
        self.kill_num = 0  # 击杀数
        self.conditions = 1
        self.history_dmg = 0

    # 运行实体前先判断是否可以使用
    def is_allow(self):
        if self.type == "skill":
            if self.conditions <= global_msg.battle_skill_point:
                return True
            else:
                return False
        elif self.type == "ultimate":
            if self.source.cur_energy >= self.conditions:
                return True
            else:
                return False
        elif self.type == "basic_atk":
            return True

    # 运行实体
    def work(self, target) -> int | str:
        self.target = target
        send_action.send(self.source, self.target, self)
        # 运行实体函数,并且返回参数
        return self.function(self)


# 伤害元组结算
def make_dmg(source, var):
    """
    伤害元组结算函数
    :param source: 伤害来源
    :param var: 伤害元组
    :return:死亡数
    """
    if isinstance(var[0], int):
        target = var[2]
        _dmg = var[0]
        target.change_stats(source, "cur_HP", _dmg, 0)
        if target.in_death:
            return 1
        else:
            return 0
    else:
        num = 0
        for t in var:
            if t:
                target = t[2]
                _dmg = t[0]
                target.change_stats(source, "cur_HP", _dmg, 0)
                if target.in_death:
                    num += 1
        return num


# 伤害元组统计
def count_dmg(var):
    """
    伤害元组统计函数,返回伤害总数值
    :param var: 伤害元组
    :return: int
    """
    if isinstance(var[0], int):
        return var[0]
    else:
        _dmg = 0
        for t in var:
            if t:
                _dmg += t[0]
        return _dmg
