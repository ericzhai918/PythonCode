import pygame

from settings import *
from gamedisplay import *


class Piece():
    def __init__(self, shape, screen,gamewall):
        self.x = 4
        self.y = 0
        self.shape = shape
        self.turn_times = 0
        self.screen = screen
        self.at_bottom = False
        self.game_wall = gamewall

    def paint(self):
        shape_template = PIECES[self.shape]
        shape_turn = shape_template[self.turn_times]
        # r是行，c是列，x加的是行r，y加的是列c
        for r in range(len(shape_turn)):
            for c in range(len(shape_turn[0])):
                if shape_turn[r][c] == 'O':
                    self.draw_cell(self.y + r, self.x + c)

    def draw_cell(self, row, column):
        GameDisplay.draw_cell(self.screen, row, column, PIECE_COLORS[self.shape])

    def move_right(self):
        if self.can_move_right():
            self.x += 1

    def move_left(self):
        if self.can_move_left():
            self.x -= 1

    def move_down(self):
        if self.can_move_down():
            self.y += 1
        else:
            self.at_bottom = True

    def fall_down(self):
        while not self.at_bottom:
            self.move_down()

    def turn(self):
        shape_list_len = len(PIECES[self.shape])
        if self.can_turn():
            self.turn_times = (self.turn_times + 1) % shape_list_len

    def can_move_right(self):
        shape_mtx = PIECES[self.shape][0]
        for r in range(len(shape_mtx)):
            for c in range(len(shape_mtx[0])):
                if shape_mtx[r][c] == 'O':
                    # 如果方块在最右侧，该方法返回False，否则返回True
                    if self.x + c >= COLUMN_NUM - 1:
                        return False
        return True

    def can_move_left(self):
        shape_mtx = PIECES[self.shape][0]
        for r in range(len(shape_mtx)):
            for c in range(len(shape_mtx[0])):
                if shape_mtx[r][c] == 'O':
                    if self.x + c <= 0:
                        return False
        return True

    def can_move_down(self):
        shape_mtx = PIECES[self.shape][0]
        for r in range(len(shape_mtx)):
            for c in range(len(shape_mtx[0])):
                if shape_mtx[r][c] == 'O':
                    if self.y + r >= LINE_NUM - 1 or self.game_wall.is_wall(self.y + r + 1, self.x + c):
                        return False
        return True

    def can_turn(self):
        shape_list_len = len(PIECES[self.shape])
        turn_times = (self.turn_times + 1) % shape_list_len
        shape_mtx = PIECES[self.shape][turn_times]
        for r in range(len(shape_mtx)):
            for c in range(len(shape_mtx[0])):
                if shape_mtx[r][c] == 'O':
                    if (self.x + c < 0 or self.x + c >= COLUMN_NUM) or (self.y + r < 0 or self.y + r >= LINE_NUM):
                        return False
        return True
