"""Generate a fully solved 9x9 Sudoku grid via randomized backtracking."""
import random

SIZE = 9
EMPTY = 0
BOX_SIZE = 3


def create_empty_board() -> list[list[int]]:
    return [[EMPTY for _ in range(SIZE)] for _ in range(SIZE)]


def is_safe(board: list[list[int]], row: int, col: int, num: int) -> bool:
    for i in range(SIZE):
        if board[row][i] == num or board[i][col] == num:
            return False
    start_row = row - row % BOX_SIZE
    start_col = col - col % BOX_SIZE
    for i in range(BOX_SIZE):
        for j in range(BOX_SIZE):
            if board[start_row + i][start_col + j] == num:
                return False
    return True


def fill_board(board: list[list[int]]) -> bool:
    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] == EMPTY:
                candidates = list(range(1, SIZE + 1))
                random.shuffle(candidates)
                for candidate in candidates:
                    if is_safe(board, row, col, candidate):
                        board[row][col] = candidate
                        if fill_board(board):
                            return True
                        board[row][col] = EMPTY
                return False
    return True


def generate_solved_grid() -> list[list[int]]:
    board = create_empty_board()
    fill_board(board)
    return board
