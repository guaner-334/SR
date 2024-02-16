# 光环模板
class Halo:
    """
    光环通用模板
    """

    def __init__(self, source, function):
        self.msg = None
        self.source = source  # 发起人
        self.target = None  # 目标
        self.turn = 0  # 轮次
        self.leave_turn = 0  # 剩余轮次
        self.times = 0
        self.function = function

    # 添加buff
    def add_buff(self, target):
        """
        添加光环,同时生效
        :param target:
        :return:
        """
        self.target = target
        # 目标halo集合中添加自己
        for target in self.target:
            target.halo_set.add(self)
        # 运行buff函数
        self.function(self, "add")

    # buff回合数减1
    def turn_off(self):
        """
        光环持续回合数-1,同时判断是否过期
        :return:
        """
        self.leave_turn -= 1
        if self.leave_turn <= 0:
            self.function(self, "turn_off")
            self.end()

    # 结束
    def end(self):
        for target in self.target:
            target.halo_set.pop(self)
        self.function(self, "end")

    # 受到通知
    def get_action_msg(self, msg_self):
        """
        收到通知时运行光环关联的函数
        :param msg_self: 输入消息
        :return:
        """
        self.msg = msg_self
        self.function(self, "get_action_msg")