import pygame
import sys
import math
import random
import time
import copy
import os
import mcts

pygame.init()

#定义参数
MAX_TURNS = 50
NAME=['wW', 'wA', 'wP', 'wC', 'eW', 'eA', 'eP', 'eC']

# 定义颜色
RED = (255, 0, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
LIGHT_GREEN = (144, 238, 144)
ORANGE = (255, 165, 0)

# 设置窗口大小
WIDTH, HEIGHT = 700, 700
ROWS, COLS = 8, 8
SQSIZE = WIDTH // COLS

# 创建窗口
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('王国保卫战')

class Kingdom:
    def __init__(self):
        self.board=[
            ['--', '--', '--', '--', '--', '--', 'eA', 'eC'],
            ['--', '--', '--', '--', '--', '--', 'eP', 'eW'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['wW', 'wP', '--', '--', '--', '--', '--', '--'],
            ['wC', 'wA', '--', '--', '--', '--', '--', '--']
        ]
        type = [Warrior(), Archer(), Protector(), Commander(), Warrior(), Archer(), Protector(), Commander()]
        position = [[0,6],[1,7],[1,6],[0,7]]
        self.chess = {key: value for key, value in zip(NAME, type)}
        self.player='w'
        self.current_winner=None
        self.turns=0

    def print_board(self):
        pass


    def winner(self):
        chess=self.chess
        if self.board[0][7] == '--':
            return 'w'
        if self.board[7][0] == '--':
            return 'e'
        if chess['eW'].hp+chess['eA'].hp+chess['eP'].hp<=0:
            return 'w'
        if chess['wW'].hp+chess['wA'].hp+chess['wP'].hp<=0:
            return 'e'
        # 达到回合上限
        if self.turns == MAX_TURNS:
            # return 'e'
            # print(self.player)
            # print(time.time() - start_time)
            if chess['eC'].hp > chess['wC'].hp:
                return 'e'
            else:
                if chess['eC'].hp < chess['wC'].hp:
                    return 'w'
                # 司令生命值相同
                else:
                    if chess['eC'].hp == chess['wC'].hp:
                        sum = [0, 0]
                        for row in range(ROWS):
                            for col in range(COLS):
                                if self.board[row][col] != '--':
                                    piece = self.board[row][col]
                                    if piece[0] == 'w':
                                        sum[0] += self.chess[piece].hp
                                    else:
                                        sum[1] += self.chess[piece].hp
                                    if sum[1] >= sum[0]:
                                        return 'e'
                                    else:
                                        if sum[1] < sum[0]:
                                            return 'w'
        return None

    def vaild_policy(self):
        policies = []
        for row in range(ROWS):
            for col in range(COLS):
                if self.board[row][col][0] == self.player and self.board[row][col][1] != 'C':
                    piece = self.board[row][col]
                    vaild_moves = self.chess[piece].move_range(self.board, [row, col])
                    # print(len(vaild_moves))
                    for move_to in vaild_moves:
                        new_state = copy.deepcopy(self)
                        new_state.board[row][col] = '--'
                        new_state.board[move_to[0]][move_to[1]] = piece
                        new_state.turns = self.turns + 1
                        new_state.player = 'w' if self.player == 'e' else 'e'
                        erase(new_state)
                        vaild_attacks = self.chess[piece].atk_range(new_state.board, move_to)
                        new_state.current_winner = new_state.winner()
                        if len(vaild_attacks) == 0:
                            policies.append(new_state)
                        else:
                            for attack_to in vaild_attacks:
                                piece_object = new_state.board[attack_to[0]][attack_to[1]]
                                new_state.chess[piece_object].attack(new_state.chess[piece])
                                erase(new_state)
                                new_state.current_winner = new_state.winner()
                                policies.append(new_state)
        return policies


def in_board(position):
    return 0 <= position[0] < 8 and 0 <= position[1] < 8

# 定义棋子抽象基类
class Chess:
    def __init__(self):
        self.atk = self.hp = self.type = self.hpmax = self.move_next = self.atk_next = None

    def attack(self, obj):
        obj.hp -= self.atk

    def heal(self):
        self.hp = self.hpmax if self.hp + 25 > self.hpmax else self.hp + 25

    def information(self):
        return [self.type, 'ATK:' + str(self.atk), 'HP:' + str(self.hp)]

    def move_range(self, board, position):
        # vaild_move = [[0 for _ in range(COLS)] for _ in range(ROWS)]
        vaild_move=[]
        for d in self.move_next:
            destination = (d[0] + position[0], d[1] + position[1])
            if (in_board(destination) == False):
                continue
            if board[destination[0]][destination[1]] == '--':
                vaild_move.append([destination[0],destination[1]])
        return vaild_move

    def atk_range(self, board, position):
        # vaild_atk = [[0 for _ in range(COLS)] for _ in range(ROWS)]
        vaild_atk=[]
        for d in self.atk_next:
            destination = (d[0] + position[0], d[1] + position[1])
            if (in_board(destination) == False):
                continue
            if board[destination[0]][destination[1]] != '--' and board[destination[0]][destination[1]][0] != \
                    board[position[0]][position[1]][0]:
                # vaild_atk[destination[0]][destination[1]] = 1;
                vaild_atk.append([destination[0],destination[1]])
        # print(vaild_atk)
        return vaild_atk

# 定义各棋子类
class Commander(Chess):
    def __init__(self):
        self.type = 'Commander'
        self.atk = 0
        self.hp = self.hpmax = 1600

class Warrior(Chess):
    def __init__(self):
        self.type = 'Warrior'
        self.atk = 200
        self.hp = 1000
        self.hpmax = 1000
        self.atk_next = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    def move_range(self, board, position):
        # vaild_move = [[0 for _ in range(COLS)] for _ in range(ROWS)]
        vaild_move=[]
        move = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for d in move:
            first_move = (position[0] + d[0], position[1] + d[1])
            if (in_board(first_move) == False):
                continue
            if board[first_move[0]][first_move[1]] == '--':
                vaild_move.append([first_move[0],first_move[1]])
                for dd in move:
                    second_move = (first_move[0] + dd[0], first_move[1] + dd[1])
                    if (in_board(second_move) == False):
                        continue
                    if board[second_move[0]][second_move[1]] == '--':
                        vaild_move.append([second_move[0],second_move[1]])
        return vaild_move


class Archer(Chess):
    def __init__(self):
        self.type = 'Archer'
        self.atk = 250
        self.hp = 700
        self.hpmax = 700
        self.move_next = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        self.atk_next = [(-1, 0), (1, 0), (0, -1), (0, 1), (1, 1), (1, -1), (-1, -1), (-1, 1), (2, 0), (-2, 0), (0, 2),
                         (0, -2)]

class Protector(Chess):
    def __init__(self):
        self.type = 'Protector'
        self.atk = 150
        self.hp = self.hpmax = 1400
        self.move_next = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        self.atk_next = [(-1, 0), (1, 0), (0, -1), (0, 1), (1, 1), (1, -1), (-1, -1), (-1, 1)]

# 绘制棋盘
def draw_board():
    screen.fill(WHITE)
    for row in range(3, 5):
        for col in range(3, 5):
            pygame.draw.rect(screen, YELLOW, (col * SQSIZE, row * SQSIZE, SQSIZE, SQSIZE))
    for row in range(ROWS):
        for col in range(COLS):
            pygame.draw.rect(screen, BLACK, (col * SQSIZE, row * SQSIZE, SQSIZE, SQSIZE), 1)

# 绘制棋子信息与血条
def draw_pieces(game):

    for row in range(ROWS):
        for col in range(COLS):
            piece = game.board[row][col]

            if piece != '--':
                pygame.draw.rect(screen, RED if (piece[0] == 'w') else BLUE, (
                col * SQSIZE + 1, row * SQSIZE + 1, (SQSIZE - 2) * game.chess[piece].hp / game.chess[piece].hpmax, SQSIZE // 10))
                font = pygame.font.Font(None, 20)
                text_surface = font.render(game.chess[piece].information()[0], True, RED if (piece[0] == 'w') else BLUE)
                screen.blit(text_surface, (col * SQSIZE + 2, row * SQSIZE + 15))
                font = pygame.font.Font(None, 30)
                text_surface = font.render(game.chess[piece].information()[1], True, RED if (piece[0] == 'w') else BLUE)
                screen.blit(text_surface, (col * SQSIZE + 5, row * SQSIZE + 40))
                text_surface = font.render(game.chess[piece].information()[2], True, RED if (piece[0] == 'w') else BLUE)
                screen.blit(text_surface, (col * SQSIZE + 5, row * SQSIZE + 60))

# 画可移动范围
def draw_move(vaild):
    for position in vaild:
        pygame.draw.rect(screen, LIGHT_GREEN, (position[1] * SQSIZE + 1, position[0] * SQSIZE + 1, SQSIZE - 2, SQSIZE - 2), 4)

# 画可攻击对象
def draw_atk(vaild):
    for position in vaild:
        pygame.draw.rect(screen, ORANGE, (position[1] * SQSIZE + 1, position[0] * SQSIZE + 1, SQSIZE - 2, SQSIZE - 2), 4)

# 治疗区
def recover(game):
    for row in range(3, 5):
        for col in range(3, 5):
            piece = game.board[row][col]
            if piece != '--':
                game.chess[piece].heal()
                if piece[0] == 'w':
                    game.chess['wC'].heal()
                else:
                    game.chess['eC'].heal()


# 移除棋子
def erase(game):
    for row in range(ROWS):
        for col in range(COLS):
            piece = game.board[row][col]
            if piece != '--' and game.chess[piece].hp <= 0:
                game.board[row][col] = '--'



# 主函数
def main():
    game=Kingdom()
    running = True
    selected1 = selected2 = None
    draw_board()
    draw_pieces(game)

    while running:
        if game.current_winner is not None:
            print("有赢家")
            running = False
            sys.exit()
        # print(game.player)
        if game.player=='w':
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = event.pos
                    row = y // SQSIZE
                    col = x // SQSIZE

                    if selected1 and selected2:
                        pieceA = game.board[selected2[0]][selected2[1]]
                        pieceB = game.board[row][col]
                        vaild_atk = game.chess[pieceA].atk_range(game.board, selected2)

                        if [row,col] not in vaild_atk:
                            draw_board()
                            draw_pieces(game)
                            print('请选中')
                        else:
                            game.chess[pieceA].attack(game.chess[pieceB])
                            erase(game)
                            draw_board()
                            draw_pieces(game)
                            print('已攻击或跳过', game.board[row][col])
                            print('请选中')
                        game.player = 'e'
                        selected1 = selected2 = None
                    else:
                        if selected1:
                            draw_board()
                            piece = game.board[selected1[0]][selected1[1]]
                            selected2 = (row, col)
                            if [row,col] not in game.chess[piece].move_range(game.board, selected1):
                                selected1 = selected2 = None
                                print('请选中')
                            else:
                                game.board[row][col] = piece
                                game.board[selected1[0]][selected1[1]] = '--'
                                print('已移动', game.board[row][col])
                                recover(game)
                                vaild_atk = game.chess[piece].atk_range(game.board, selected2)
                                if len(vaild_atk) == 0:
                                    selected1 = selected2 = None
                                    game.player='e'
                                    print('请选中')
                                else:
                                    draw_atk(vaild_atk)
                                    print('请攻击')
                            draw_pieces(game)
                        else:
                            if game.board[row][col] != '--' and game.board[row][col][1] != 'C':
                                selected1 = (row, col)
                                piece = game.board[row][col]
                                draw_move(game.chess[piece].move_range(game.board, selected1))
                                print('已选中', game.board[row][col])
        else:
            tree=mcts.MCTS(game,0.4)
            game=tree.search(game)
            draw_board()
            draw_pieces(game)

        pygame.display.flip()

if __name__ == "__main__":
    main()