# buff通用模板
class Buff:
    """
    通用BUFF模板,支持方法:
    add_buff:buff生效
    turn_off:回合数减1, 为零时判断是否过期
    get_action_msg:收到通知
    :return None
    """

    def __init__(self, source, function):
        """
        :param source:产生这个buff角色
        :param function: 对应的buff函数
        """
        self.msg = None
        self.source = source  # 发起人
        self.target = None  # 目标
        self.leave_turn = 0  # 剩余轮次
        self.is_working = False
        self.times = 0
        self.function = function
        self.history_dmg = 0

    # 添加buff
    def add_buff(self, target):
        """
        :param target:buff生效的对象
        :return:
        """
        self.target = target
        # 目标buff集合中添加自己
        self.target.buff_set.add(self)
        # 运行buff函数
        self.function(self, "add")

    # buff回合数减1
    def turn_off(self):
        """
        调用该方法会使得该buff的回合数减一,若归零则运行buff函数的"end"状态
        :return:
        """
        self.leave_turn -= 1
        self.function(self, "turn_off")
        if self.leave_turn <= 0:
            self.end()

    # buff结束
    def end(self):
        self.target.buff_set.pop(self)
        self.function(self, "end")

    # 受到通知
    def get_action_msg(self, msg_self):
        """
        :return:
        """
        self.msg = msg_self
        self.function(self, "msg")


class Debuff(Buff):
    # 添加buff
    def add_buff(self, target):
        """
        :param target:debuff生效的对象
        :return:
        """
        self.target = target
        # 目标buff集合中添加自己
        self.target.debuff_set.add(self)
        # 运行buff函数
        self.function(self, "add")
