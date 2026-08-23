"""Carve a uniquely-solvable puzzle out of a fully solved grid, by difficulty."""
import copy
import random

from .generator import EMPTY, SIZE, generate_solved_grid
from .solver import count_solutions

# (min, max) clues (filled cells) left in the puzzle for each difficulty.
# 17 is Sudoku's proven floor for a uniquely solvable puzzle, so Hard stays
# comfortably above it.
DIFFICULTY_CLUES = {
    "easy": (40, 45),
    "medium": (30, 35),
    "hard": (22, 27),
}

MAX_GENERATION_ATTEMPTS = 20


def clue_target_for_difficulty(difficulty: str) -> int:
    if difficulty not in DIFFICULTY_CLUES:
        raise ValueError(f"Unknown difficulty: {difficulty!r}")
    low, high = DIFFICULTY_CLUES[difficulty]
    return random.randint(low, high)


def _carve_unique_puzzle(solution: list[list[int]], clue_target: int) -> list[list[int]] | None:
    """Try one randomized carving pass toward `clue_target` clues.

    Walks the 81 cells in random order, blanking each one only if the board
    still has exactly one solution afterward. Returns None if the pass
    stalls before reaching the target -- some cells can't be removed
    without breaking uniqueness, and a single pass doesn't revisit them.
    """
    board = copy.deepcopy(solution)
    filled = SIZE * SIZE
    cells = [(row, col) for row in range(SIZE) for col in range(SIZE)]
    random.shuffle(cells)

    for row, col in cells:
        if filled <= clue_target:
            return board
        removed_value = board[row][col]
        board[row][col] = EMPTY
        if count_solutions(board, limit=2) == 1:
            filled -= 1
        else:
            board[row][col] = removed_value

    return board if filled <= clue_target else None


def generate_puzzle(difficulty: str = "medium") -> tuple[list[list[int]], list[list[int]]]:
    """Return (puzzle, solution) for the given difficulty.

    Each attempt starts from a fresh solved grid: if carving stalls above
    the clue target on one grid, a different grid's cell layout may carve
    down further, so retrying from scratch is cheaper than the alternative
    of backtracking within a single carve.
    """
    for _ in range(MAX_GENERATION_ATTEMPTS):
        solution = generate_solved_grid()
        clue_target = clue_target_for_difficulty(difficulty)
        puzzle = _carve_unique_puzzle(solution, clue_target)
        if puzzle is not None:
            return puzzle, solution
    raise RuntimeError(
        f"Failed to generate a '{difficulty}' puzzle after {MAX_GENERATION_ATTEMPTS} attempts"
    )
