"""
Version 1
Created on Fri Aug 2 23:03 2024
Author: Chi Ran
很唐的版本，根本算不上AI，写这个主要是为了交上去能先看看其他人的水平
主要策略是占据治疗区，随后不动，等待敌方的进攻
先列出下一步所有的结果，然后对每个局面算出一个评估值
主要因素有敌方血量，我方控制范围，治疗区的占领
用评估值最高的走法
输出用时发现每一步用时基本在1ms以内

改进计划：
1.占领治疗区时保持队形
2.遭遇战的博弈策略
3.充分利用算力（套上蒙特卡洛搜索树）
"""
import realm
import time

class Evaluation:
    def __init__(self, layout, my_side):
        self.layout = layout
        self.my_side = my_side


    def health_evaluation(self):
        my_side = self.my_side
        enemy_side = 'E' if my_side == 'W' else 'W'
        layout = self.layout
        health_value: dict[realm.ChessType, float] = {realm.ChessType.COMMANDER: 100, realm.ChessType.ARCHER: 18,
                                                      realm.ChessType.PROTECTOR: 22, realm.ChessType.WARRIOR: 30}
        # for chess_id in realm.get_valid_chess_id(board.layout,my_side,include_commander = False):
        total_health = sum(
            health_value[chess_id] * realm.get_chess_details(layout, enemy_side, chess_id, return_details=True)['hp'] /
            realm.get_chess_profile(chess_id)['init_hp']
            for chess_id in realm.get_valid_chess_id(layout, enemy_side, include_commander=True))
        # chess_id = realm.ChessType.COMMANDER
        # total_health += health_value[chess_id] * (
        #             realm.get_chess_details(layout, enemy_side, chess_id, return_details=True)['hp']
        #             / realm.get_chess_profile(chess_id)['init_hp']) ** 0.25
        total_health+=len(realm.get_valid_chess_id(layout, enemy_side, include_commander=False))*50
        return total_health

    def cover_evaluation(self):
        my_side = self.my_side
        layout = self.layout
        enemy_side = 'E' if my_side == 'W' else 'W'
        total_cover = 0
        for chess_id in realm.get_valid_chess_id(layout, my_side, include_commander=True):
            for enemy_id in realm.get_valid_attack(layout, my_side, chess_id):
                # print(pos)
                if enemy_id == realm.ChessType.COMMANDER:
                    total_cover += 5
                else:
                    total_cover += (1000 - realm.get_chess_details(layout, enemy_side, enemy_id, return_details=True)[
                        'hp']) / 200
        return total_cover

    def recover_evaluation(self):
        my_side = self.my_side
        layout = self.layout
        enemy_side = 'E' if my_side == 'W' else 'W'
        value=0
        for chess_id in realm.get_valid_chess_id(layout, my_side, include_commander=False):
            pos=realm.get_chess_details(layout, my_side, chess_id, return_details = True)['pos']
            value+=pos[0]-4 if pos[0]>=4 else 3-pos[0]
            value+=pos[1]-4 if pos[1]>=4 else 3-pos[1]
        return value*0.1

    def aggressive_evaluation(self):
        my_side = self.my_side
        layout = self.layout
        enemy_side = 'E' if my_side == 'W' else 'W'
        enemy_pos = realm.get_chess_details(layout, enemy_side, realm.ChessType.COMMANDER, return_details = True)['pos']
        value=0
        for chess_id in realm.get_valid_chess_id(layout, my_side, include_commander=False):
            pos = realm.get_chess_details(layout, my_side, chess_id, return_details=True)['pos']
            value+=abs(pos[0]-enemy_pos[0])+abs(pos[1]-enemy_pos[1])
        return value*0.5

    def function(self):
        return -self.health_evaluation() + self.cover_evaluation()-self.recover_evaluation()-self.aggressive_evaluation()


@realm.api_decorator
def update(board):
    start_time=time.time()
    my_side = board.my_side
    list_actions = realm.get_valid_actions(board.layout, my_side)
    enemy_side = 'E' if my_side == 'W' else 'W'
    values = []
    for action in list_actions:
        layout = realm.make_turn(board.layout, my_side, action, calculate_points='none')[0]
        if realm.is_terminal(layout) == my_side:
            return action
        # print(Evaluation(layout,my_side).function())
        values.append([Evaluation(layout, my_side).function(), action])
    print(-start_time+time.time())
    print(max(values, key=lambda x: x[0])[0])
    return max(values, key=lambda x: x[0])[1]
