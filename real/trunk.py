"""
Version 0.5
Created on Sat, Jul 20, 2024 at 15:26
Author: Chi Ran
用蒙特卡洛搜索树实现
为方便合作，先编写了搜索树中除simulate以外的部分
由于文档中的Board类型应该是只读的，所以写了自己的棋盘类型
后续的主要任务在于完成simulate部分
注意：1.如果后续发现了比蒙特卡洛搜索树更适合的模型，会推翻这个版本
     2.原规则的超时判定值得玩味，在敲定最终版本前请不要忽略时限参数的优化
"""

import realm
import time
import math
import copy

#单回合的时限
#这里用极端保守思想，将单回合弹出warning的期望严格控制在0
TIME_LIMITATION = 0.3999
CI = 1.41#UCB公式的参数

#要进行棋盘类型传递而不是棋局类型的传递
class MyBoard:
    def __init__(self, layout, my_side ,turn_number, action=None):
        self.layout=layout
        self.my_side=my_side
        self.turn_number=turn_number
        self.previous_action=action

    def get_vaild_boards(self):
        list_actions = realm.get_valid_actions(self.layout, self.my_side)
        next_boards = []
        for action in list_actions:
            new_board = copy.deepcopy(self)
            new_board.layout = realm.make_turn(self.layout, self.my_side, action, calculate_points='none')[0]
            new_board.turn_number = self.turn_number + 1;
            new_board.my_side = 'W' if self.my_side == 'E' else 'W'
            new_board.previous_action=action
            next_boards.append(new_board)
        return next_boards

#搜索树的节点类
class Node:
    def __init__(self, board, parent=None):
        self.board=board
        self.parent=parent
        self.children=[]
        self.visits=0
        self.wins=0

    def add_child(self,board):
        child=Node(board,self)
        self.children.append(child)
        return child

    def get_ucb(self, c=CI):
        if self.visits==0:
            return float('inf')
        return self.wins / self.visits + c * math.sqrt(math.log(self.parent.visits) / self.visits)

#蒙特卡洛搜索树类
class MCTS:
    def __init__(self, initial_state, time_limit):
        self.root=Node(initial_state)
        self.time_limit=time_limit

    def search(self):
        start_time=time.time()
        while time.time()-start_time<self.time_limit:
            node=self.select()
            winner=self.simulate(node)
            self.backpropagate(node, winner)
        #返回Action类型
        return self.best_policy()

    def select(self):
        node=self.root
        while node.children:
            node = max(node.children, key=lambda child: child.get_ucb())
        if node.visits > 0:
            self.expand(node)
        return node

    def expand(self, node):
        board=node.board
        for new_board in board.get_vaild_boards():
            node.add_child(new_board)

    def simulate(self, node):
        #返回模拟后的获胜者
        pass

    def backpropagate(self,node,winner):
        while node is not None:
            node.visits+=1
            if node.board.my_side==winner:
                node.wins+=1
            node=node.parent

    def best_policy(self,root):
        #返回Action类型
        return max(root.children, key=lambda child: child.visits).board.previous_action

#上传本回合的最终决策
@realm.api_decorator
def update(board):
    my_board=MyBoard(board.layout, board.my_side, board.turn_number)
    mcts=MCTS(my_board,TIME_LIMITAION)
    return mcts.search() #必须返回Action类型
