from settings import *


class GameWall():
    def __init__(self, screen):
        self.screen = screen
        self.area = []
        line = [WALL_BLANK_LABEL] * COLUMN_NUM
        for i in range(LINE_NUM):
            self.area.append(line[:])

    def add_to_wall(self, piece):
        shape_turn = PIECES[piece.shape][piece.turn_times]
        for row in range(len(shape_turn)):
            for column in range(len(shape_turn[0])):
                if shape_turn[row][column] == 'O':
                    self.set_cell(piece.y + row, piece.x + column, piece.shape)

    def set_cell(self, row, column, shape_label):
        self.area[row][column] = shape_label

    def is_wall(self, row, column):
        return self.area[row][column] != WALL_BLANK_LABEL

    def eliminate_lines(self):
        '''消行。如果一行没有空白单元格，就消掉该行。返回得分。'''
        '''计分规则：消掉0行：0分/消掉1行：100分/消掉2行：200分/消掉3行：400分/消掉4行：800分'''
        # 需要消哪几行
        lines_eliminated = []
        for row in range(LINE_NUM):
            if self.is_full(row):
                lines_eliminated.append(row)

        # 消行，更新墙体矩阵
        for row in lines_eliminated:
            self.copy_down(row)  # 消掉行r，上面的各行依次下沉一行
            for column in range(COLUMN_NUM):
                self.area[0][column] = WALL_BLANK_LABEL

        # 根据消掉的行数，计算得分
        elimimated_num = len(lines_eliminated)
        assert (elimimated_num <= 4 and elimimated_num >= 0)
        if elimimated_num < 3:
            score = elimimated_num * 100
        elif elimimated_num == 3:
            score = 400
        else:
            score = 800
        return score

    def is_full(self, row):
        '''下标为row的一行满了吗'''
        for column in range(COLUMN_NUM):
            if self.area[row][column] == WALL_BLANK_LABEL:
                return False
        return True

    def copy_down(self, row):
        '''把row号行上面各行依次下沉一行'''
        for r in range(row, 0, -1):
            for c in range(COLUMN_NUM):
                self.area[r][c] = self.area[r - 1][c]

    def clear(self):
        for r in range(LINE_NUM):
            for c in range(COLUMN_NUM):
                self.area[r][c] = WALL_BLANK_LABEL
