"""
Created on Sat Jul 20 17:31 2024
Author: Chi Ran
用赌徒策略进行rollout
主要用于测试蒙特卡洛搜索树在真实环境的效率
"""

def simulate(self, node):
    board=copy.deepcopy(node.board)
    while True:
        my_side = board.my_side
        list_actions = realm.get_valid_actions(board.layout, my_side)
        enemy_side = 'E' if my_side == 'W' else 'W'
        def valuation_func(action):
            delta_points = realm.make_turn(board.layout, my_side, action, calculate_points='hard')[1]
            my_delta_points, enemy_delta_points = delta_points[my_side], delta_points[enemy_side]
            return (my_delta_points[0] - enemy_delta_points[0], my_delta_points[1] - enemy_delta_points[1])
        best_action = max(list_actions, key=valuation_func)
        board.layout=realm.make_turn(board.layout, my_side, action, calculate_points='none')[0]
        board.turn_number = board.turn_number + 1;
        board.my_side = 'W' if board.my_side == 'E' else 'W'
        board.previous_action = best_action
        if is_terminal(board.layout) is not None:
            return is_terminal(board.layout)
        if board.turn_number>=99:
            return who_win(board.layout)
