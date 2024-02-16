from math import ceil
from Star_Rail_damage_simulation.msg import global_msg


# 获取全局角色对应的速度值
def get_speed():
    """
    获取当前全局角色的列表及其速度
    :return:{人物:速度}的字典
    """
    person_dic: dict = {}
    for person in global_msg.person_list:
        person_dic.update({person: sum(person.SPD)})
    for person in global_msg.monster_list:
        person_dic.update({person: sum(person.SPD)})
    for person in global_msg.summons_list:
        person_dic.update({person: sum(person.SPD)})
    return person_dic


# 行动值计算
def action_point_count(action_point: int):
    """
    :param action_point: 输入当前全局行动的行动值
    :return: 返回Character或None
    """
    # 获取全局角色速度信息
    speed_msg = get_speed()
    action_character = []
    while not action_character:
        # 对全局角色进行一次行动判断
        for key in speed_msg:
            if key.action_point >= 10000:  # 若当前角色行动值大于10000,将其加入行动角色列表
                action_character.append(key)
        # 若出现行动值大于10000则中断循环
        if action_character:
            break
        # 对全局角色增加等同于速度的行动值
        for key in speed_msg:
            action_point += 100
            key.action_point += speed_msg[key]
            if key.action_point >= 10000:  # 若当前角色行动值大于10000,将其加入行动角色列表
                action_character.append(key)
            # 若出现行动值大于10000则中断循环
        if action_character:
            break
        if action_point >= 10000:
            break
    # 找出行动值最大的角色
    max_c = 0  # 最大行动值
    if action_character:
        c = None  # 对应角色
        for __character in action_character:
            if sum(__character.SPD) > max_c:
                max_c = sum(__character.SPD)
                c = __character
    else:
        c = None
    if c:
        over_time = (max_c - 10000) / sum(c.SPD)  # 计算超出行动点数的比例
        # 对所有超过10000行动值的角色扣减固定比例的行动值
        for key in action_character:
            key.action_point -= ceil(over_time * sum(key.SPD))
    return c
