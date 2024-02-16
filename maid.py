from Star_Rail_damage_simulation.msg import global_msg
from action_point_count import action_point_count
from Star_Rail_damage_simulation.character import character_move
# 导入角色
from data.data_seele import seele
from data.data_klutz import klutz


# 战斗流程
def main():
    """
    战斗核心流程函数
    """
    turn_count = 0  # 当前回合数
    action_point = -5000  # 计算回合数的行动点数
    # 战斗开始,运行各列表的战斗开始方法
    for person in global_msg.person_list:
        person.battle_star()
    for person in global_msg.monster_list:
        person.battle_star()
    for person in global_msg.summons_list:
        person.battle_star()
    # 波次开始,运行各列表的战斗开始方法
    for person in global_msg.person_list:
        person.round_star()
    for person in global_msg.monster_list:
        person.round_star()
    for person in global_msg.summons_list:
        person.round_star()
    # 战斗流程
    while global_msg.monster_list != [] and global_msg.person_list != []:  # 人物或怪物列表不为空
        # 计算下一个行动的人
        action_person = action_point_count(action_point)
        if action_person is None:  # 如果返回空,则代表时对局回合结束了
            turn_count += 1  # 回合数+1
        else:
            action_person.turn_star()
            character_move(action_person)
            action_person.turn_end()
        if turn_count >= 20:
            print("回合数耗尽")
            break
    if not global_msg.monster_list:
        print("消灭全部怪物")
    elif not global_msg.person_list:
        print("角色全部阵亡")


global_msg.person_list.append(seele)
global_msg.monster_list.append(klutz)
main()
