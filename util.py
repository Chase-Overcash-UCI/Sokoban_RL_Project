import numpy as np
from enum import Enum


# Value is change in coordinate
class Action(Enum):
    UP = (-1, 0)
    DOWN = (1, 0)
    LEFT = (0, -1)
    RIGHT = (0, 1)


class CellState(Enum):
    EMPTY = ' '
    WALL = '#'
    GOAL = '.'
    PLAYER = '@'
    PLAYER_ON_GOAL = '%'
    BOX = '$'
    BOX_ON_GOAL = 'X'


def convert_text_to_board(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()
        n_row, n_col = map(int, lines[0].split())
        # Read wall, box, goal and player pos from text. Convert box, goal, and player to tuples of coord
        # Also convert box, goal, and player to 0-index instead of 1-index
        wall_cells = list(map(int, lines[1].split()))[1:]
        box_cells = list(map(int, lines[2].split()))[1:]
        box_cells = [(box_cells[idx] - 1, box_cells[idx + 1] - 1) for idx in range(0, len(box_cells), 2)]
        goal_cells = list(map(int, lines[3].split()))[1:]
        goal_cells = [(goal_cells[idx] - 1, goal_cells[idx + 1] - 1) for idx in range(0, len(goal_cells), 2)]
        player_pos = tuple(map(int, lines[4].split()))
        player_pos = (player_pos[0] - 1, player_pos[1] - 1)

    board = np.full((n_row, n_col), CellState.EMPTY, dtype=CellState)
    # init wall, box, and goal cells. Somehow index starts at 1
    for r, c in zip(wall_cells[::2], wall_cells[1::2]):
        board[r - 1, c - 1] = CellState.WALL

    # Box, goal, and player are already converted to 0-index
    for r, c in goal_cells:
        board[r, c] = CellState.GOAL

    for r, c in box_cells:
        board[r, c] = CellState.BOX if board[r, c] == CellState.EMPTY else CellState.BOX_ON_GOAL

    # init player, player pos already converted to 0-index
    board[player_pos[0], player_pos[1]] = CellState.PLAYER if \
        board[player_pos[0], player_pos[1]] == CellState.EMPTY else CellState.PLAYER_ON_GOAL

    return board, box_cells, goal_cells, player_pos


def get_new_pos(pos, action):
    return pos[0] + action.value[0], pos[1] + action.value[1]


# accepts a numpy 2d array as board
def print_board(board):
    print("=" * 40)
    print("  " + "".join(list(map(str, range(board.shape[1])))))
    for r in range(board.shape[0]):
        print(r, end=" ")
        for c in range(board.shape[1]):
            print(board[r, c].value, end="")
        print()

    print("=" * 40)
