#从chatgpt上拷贝的蒙特卡洛搜索树代码，用作参考

import math
import random
import time

# 定义井字棋的棋盘和基本操作
class TicTacToe:
    def __init__(self):
        self.board = [' ' for _ in range(9)]  # 初始棋盘为9个空格
        self.current_winner = None  # 当前赢家为空

    def print_board(self):
        for row in [self.board[i * 3:(i + 1) * 3] for i in range(3)]:
            print('| ' + ' | '.join(row) + ' |')

    @staticmethod
    def print_board_nums():
        number_board = [[str(i) for i in range(j * 3, (j + 1) * 3)] for j in range(3)]
        for row in number_board:
            print('| ' + ' | '.join(row) + ' |')

    def available_moves(self):
        return [i for i, spot in enumerate(self.board) if spot == ' ']

    def empty_squares(self):
        return ' ' in self.board

    def num_empty_squares(self):
        return self.board.count(' ')

    def make_move(self, square, letter):
        if self.board[square] == ' ':
            self.board[square] = letter
            if self.winner(square, letter):
                self.current_winner = letter
            return True
        return False

    def winner(self, square, letter):
        # 检查行
        row_ind = square // 3
        row = self.board[row_ind * 3:(row_ind + 1) * 3]
        if all([spot == letter for spot in row]):
            return True
        # 检查列
        col_ind = square % 3
        column = [self.board[col_ind + i * 3] for i in range(3)]
        if all([spot == letter for spot in column]):
            return True
        # 检查对角线
        if square % 2 == 0:
            diagonal1 = [self.board[i] for i in [0, 4, 8]]
            if all([spot == letter for spot in diagonal1]):
                return True
            diagonal2 = [self.board[i] for i in [2, 4, 6]]
            if all([spot == letter for spot in diagonal2]):
                return True
        return False

# 定义蒙特卡洛树搜索节点
class Node:
    def __init__(self, state, parent=None, move=None):
        self.state = state  # 当前状态
        self.parent = parent  # 父节点
        self.move = move  # 导致该状态的动作
        self.children = []  # 子节点
        self.visits = 0  # 访问次数
        self.wins = 0  # 胜利次数

    def add_child(self, child_state, move):
        child = Node(child_state, self, move)
        self.children.append(child)
        return child

    def get_uct(self, c=1.41):
        # 计算UCB1值（上置信界）
        if self.visits == 0:
            return float('inf')
        return self.wins / self.visits + c * math.sqrt(math.log(self.parent.visits) / self.visits)

# 定义蒙特卡洛树搜索算法
class MCTS:
    def __init__(self, game, time_limit):
        self.game = game  # 游戏实例
        self.time_limit = time_limit  # 时间限制（秒）

    def search(self, initial_state):
        root = Node(initial_state)  # 创建根节点
        start_time = time.time()

        while time.time() - start_time < self.time_limit:
            node = self.select(root)  # 选择节点
            winner = self.simulate(node)  # 模拟游戏
            self.backpropagate(node, winner)  # 反向传播结果

        return self.best_move(root)

    def select(self, node):
        while node.children:
            node = max(node.children, key=lambda child: child.get_uct())
        if node.visits > 0:
            self.expand(node)
        return node

    def expand(self, node):
        state = node.state
        available_moves = state.available_moves()
        for move in available_moves:
            new_state = self.make_move(state, move)
            node.add_child(new_state, move)

    def simulate(self, node):
        current_state = node.state
        player = 'X' if current_state.board.count('X') <= current_state.board.count('O') else 'O'

        while current_state.empty_squares():
            move = random.choice(current_state.available_moves())
            current_state.make_move(move, player)
            if current_state.current_winner:
                return current_state.current_winner
            player = 'O' if player == 'X' else 'X'

        return 'Draw'

    def backpropagate(self, node, winner):
        while node is not None:
            node.visits += 1
            if node.state.current_winner == winner:
                node.wins += 1
            node = node.parent

    def best_move(self, root):
        return max(root.children, key=lambda child: child.visits).move

    def make_move(self, state, move):
        new_state = TicTacToe()
        new_state.board = state.board[:]
        new_state.make_move(move, 'X' if state.board.count('X') <= state.board.count('O') else 'O')
        return new_state

# 使用示例
if __name__ == '__main__':
    game = TicTacToe()
    mcts = MCTS(game, 0.4)  # 每次模拟时间限制为0.4秒
    while game.empty_squares():
        game.print_board()
        move = mcts.search(game)
        game.make_move(move, 'X' if game.board.count('X') <= game.board.count('O') else 'O')
        if game.current_winner:
            print(f"Winner: {game.current_winner}")
            break
    game.print_board()
