#蒙特卡洛搜索树的代码
#用随机走子实现的stimulation

import time
import random
import copy
import math

# 定义搜索树节点类
class Node:
    def __init__(self, state, parent=None, move=None):
        self.state = state
        self.parent = parent
        self.move = move
        self.children = []
        self.visits = 0
        self.wins = 0

    def add_child(self, next_children):
        child = Node(next_children, self)
        self.children.append(child)
        return child

    def get_ucb(self, c=1.41):
        if self.visits == 0:
            return float('inf')
        return self.wins / self.visits + c * math.sqrt(math.log(self.parent.visits) / self.visits)

start_time = time.time()
# 定义蒙特卡洛搜索树类
class MCTS:
    def __init__(self, game, time_limit):
        self.game = game
        self.time_limit = time_limit

    def search(self, initial_state):
        root = Node(initial_state)
        start_time = time.time()
        while time.time() - start_time < self.time_limit:
            node = self.select(root)
            # print(node.state.turns,node==root)
            # print(time.time() - start_time)
            winner = self.simulate(node)
            # print(time.time() - start_time)
            self.backpropagate(node, winner)
            # print(len(root.children))
            # print(time.time() - start_time)

        # print(self.best_policy(root).current_winner)
        # print(root.visits)
        # print(root.visits)
        return self.best_policy(root)

    def select(self, node):
        # node=copy.deepcopy(nodee)
        while node.children:
            node = max(node.children, key=lambda child: child.get_ucb())
        if node.visits > 0:
            self.expand(node)
        return node

    def expand(self, node):
        state=node.state
        policies=state.vaild_policy()
        for new_state in policies:
            node.add_child(new_state)

    def simulate(self,node):
        current_state=copy.deepcopy(node.state)
        while current_state.current_winner==None:
            # print(current_state.turns)
            # start_time = time.time()
            policies=current_state.vaild_policy()
            # print(time.time() - start_time)
            # if len(policies)==0:
            #     print(current_state.player)
            #     print(current_state.current_winner)
            #     for row in current_state.board:
            #         print(row)
            current_state=random.choice(policies)
        return current_state.current_winner

    def backpropagate(self,node,winner):
        while node is not None:
            node.visits+=1
            if node.state.player==winner:
                node.wins+=1
            node=node.parent

    def best_policy(self,root):
        # print(len(root.children))
        return max(root.children, key=lambda child: child.visits).state
