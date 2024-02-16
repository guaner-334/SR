# _id 生成器
class IDGenerator:
    """
    生成id,输入起始id,默认为1,每次运训id+1后返回
    附带方法 get_id,获取最新的id
    """

    def __init__(self, start_id: int = 1) -> None:
        self.id_counter = start_id - 1

    def get_id(self) -> int:
        """
        :return: 更新当前id
        """
        self.id_counter += 1
        return self.id_counter


# 角色行动通知id生成及记录
id_action = IDGenerator(1)
# 角色状态通知id生成及记录
stats_action = IDGenerator(1)


# 通知发送基础类
class SendMsg:
    """
    通知模板,用于统一通知类型的参数
    """

    def __init__(self):
        self.source = None  # 发起人,必填
        self.target = None  # 目标,可以为空
        self.entity = None  # 行动实体
        self.id = 0  # 编号id
        self.get_set = set()


# 行动通知
class SendAction(SendMsg):
    """
    角色发起行动时需要发送一条通知
    """

    def send(self, source, target=None, entity=None):
        """
        对全局角色发起行动类型通知
        :param source: 发起通知的角色
        :param target: 行动生效的目标
        :param entity: 行动实体
        """
        self.source = source  # 发起人,必填
        self.target = target  # 目标,可以为空
        self.entity = entity  # 行动实体
        self.id = id_action.get_id()  # 行动id更新
        for _var in self.get_set:  # 循环通知列表
            _var.get_action_msg(self)
        if isinstance(self.entity, str):
            print(f"Action_No.{self.id}: 【{source.name}】进行了【{entity}】")
        else:
            print(f"Action_No.{self.id}: 【{source.name}】使用了【{entity.name}】")


# 状态变化通知
class SendStats(SendMsg):
    """
    状态变化时发起通知
    """

    def __init__(self):
        super().__init__()
        self.change = None
        self.stats = None

    def send(self,
             source,
             target,
             stats: str,
             change):
        """
        发送通知的方法
        :param source: 发起通知的角色
        :param target: 行动生效的目标
        :param stats: 变化的状态属性
        :param change: 数值类型则为具体变化的值,如果为布尔类型,则为变化以后的值
        :return:
        """
        self.source = source  # 发起人,必填
        self.target = target  # 目标,可以为空
        self.stats = stats  # 变化属性
        self.change = change  # 变化值
        self.id = stats_action.get_id()  # 消息id更新
        for _var in self.get_set:  # 循环通知列表
            _var.get_stats_msg(self)
        if stats == "in_death" and change is True:
            global_msg.death(source)
        print(f"Stats_No.{self.id}: 【{source.name}】【{self.stats}】变更, 变更值{self.change}")


# 实例化
send_action = SendAction()
send_stats = SendStats()


# 全局消息类
class GlobalMsg:
    """
    全局消息,记录全局
    """

    def __init__(self):
        self.person_list = list()  # 人物列表
        self.death_person_list = list()  # 死亡人物列表
        self.monster_list = list()  # 怪物列表
        self.death_monster_list = list()  # 死亡怪物列表
        self.summons_list = list()  # 召唤物列表
        self.death_summons_list = list()  # 死亡召唤物列表
        self.battle_skill_point = 3  # 战斗信息,战技点
        self.battle_round_times = 0  # 战斗信息,轮次
        self.attention_character = None  # 正在行动的角色
        self.is_auto = False

    # 产出技能点
    def recover_skill_point(self, character):
        """
        :param character: 角色
        :return:
        """
        if self.battle_skill_point < 5:
            self.battle_skill_point += 1
            send_stats.send(character, None, "battle_skill_point", 1)

    # 使用技能点
    def ues_skill_point(self, character) -> False | True:
        """
        :param character: 角色
        :return: 扣减失败/成功
        """
        if self.battle_skill_point <= 0:
            return False
        else:
            self.battle_skill_point -= 1
            send_stats.send(character, None, "battle_skill_point", -1)
            return True

    # 接收到死亡信息
    def death(self, source):
        # 从列表中移除目标,同时将目标送入死亡列表
        if source.character_type == "person":
            self.person_list.remove(source)
            self.death_person_list.append(source)
        elif source.character_type == "monster":
            self.monster_list.remove(source)
            self.death_monster_list.append(source)
        elif source.character_type == "summons":
            self.summons_list.remove(source)
            self.death_summons_list.append(source)


global_msg = GlobalMsg()
