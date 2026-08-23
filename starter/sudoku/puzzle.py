"""Carve a playable puzzle out of a fully solved grid."""
import copy
import random

from .generator import EMPTY, SIZE, generate_solved_grid


def remove_cells(board: list[list[int]], clues: int) -> None:
    """Blank out cells in place until only `clues` filled cells remain.

    Note: this does not yet verify the remaining puzzle still has a unique
    solution -- that check lands in sudoku/solver.py in a later pass.
    """
    attempts = SIZE * SIZE - clues
    while attempts > 0:
        row = random.randrange(SIZE)
        col = random.randrange(SIZE)
        if board[row][col] != EMPTY:
            board[row][col] = EMPTY
            attempts -= 1


def generate_puzzle(clues: int = 35) -> tuple[list[list[int]], list[list[int]]]:
    """Return (puzzle, solution) where puzzle has `clues` cells filled in."""
    solution = generate_solved_grid()
    puzzle = copy.deepcopy(solution)
    remove_cells(puzzle, clues)
    return puzzle, solution
