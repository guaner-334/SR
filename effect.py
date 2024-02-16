class Effect:
    def __init__(self, source, function):
        self.msg = None
        self.source = source  # 发起人
        self.target = None  # 目标
        self.function = function
        self.times = 0

    # 添加effect
    def add_effect(self, target):
        self.target = target
        # 运行effect函数
        self.function(self, "add")

    # 收到通知
    def get_action_msg(self, msg_self):
        self.msg = msg_self
        self.function(self, "get_msg")

    # 收到通知
    def get_stats_msg(self, msg_self):
        self.msg = msg_self
        self.function(self, "get_msg")