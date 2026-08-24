import copy
import random

SIZE = 9
EMPTY = 0

# (min, max) clues (filled cells) left in the puzzle for each difficulty.
# 17 is Sudoku's proven floor for a uniquely solvable puzzle, so Hard stays
# comfortably above it.
DIFFICULTY_CLUES = {
    'easy': (40, 45),
    'medium': (30, 35),
    'hard': (22, 27),
}

MAX_GENERATION_ATTEMPTS = 20


class PuzzleGenerationStalled(Exception):
    """Raised when a single carving pass can't reach the target clue count."""


def clue_target_for_difficulty(difficulty):
    if difficulty not in DIFFICULTY_CLUES:
        raise ValueError(f'Unknown difficulty: {difficulty!r}')
    low, high = DIFFICULTY_CLUES[difficulty]
    return random.randint(low, high)

def deep_copy(board):
    return copy.deepcopy(board)

def create_empty_board():
    return [[EMPTY for _ in range(SIZE)] for _ in range(SIZE)]

def is_safe(board, row, col, num):
    # Check row and column
    for x in range(SIZE):
        if board[row][x] == num or board[x][col] == num:
            return False
    # Check 3x3 box
    start_row = row - row % 3
    start_col = col - col % 3
    for i in range(3):
        for j in range(3):
            if board[start_row + i][start_col + j] == num:
                return False
    return True

def fill_board(board):
    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] == EMPTY:
                possible = list(range(1, SIZE + 1))
                random.shuffle(possible)
                for candidate in possible:
                    if is_safe(board, row, col, candidate):
                        board[row][col] = candidate
                        if fill_board(board):
                            return True
                        board[row][col] = EMPTY
                return False
    return True

def count_solutions(board, limit=2):
    # Branch on the emptiest-looking cell (fewest legal candidates) instead
    # of the first one found in row-major order. Without this, proving
    # uniqueness on a sparse board (Hard difficulty) can take 60+ seconds --
    # picking the most-constrained cell first fails dead branches almost
    # immediately instead of discovering them many cells deep.
    empty_cell = None
    best_candidates = None
    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] != EMPTY:
                continue
            candidates = [n for n in range(1, SIZE + 1) if is_safe(board, row, col, n)]
            if not candidates:
                return 0  # dead end: this cell has no legal value at all
            if best_candidates is None or len(candidates) < len(best_candidates):
                empty_cell, best_candidates = (row, col), candidates

    if empty_cell is None:
        return 1  # every cell filled -- exactly one solution along this path

    row, col = empty_cell
    solutions = 0
    for candidate in best_candidates:
        board[row][col] = candidate
        solutions += count_solutions(board, limit - solutions)
        board[row][col] = EMPTY
        if solutions >= limit:
            return solutions
    return solutions

def remove_cells(board, clues):
    if not 0 <= clues <= SIZE * SIZE:
        raise ValueError(f'clues must be between 0 and {SIZE * SIZE}')

    cells = [(row, col) for row in range(SIZE) for col in range(SIZE)]
    random.shuffle(cells)
    remaining = SIZE * SIZE
    for row, col in cells:
        if remaining <= clues:
            break
        value = board[row][col]
        board[row][col] = EMPTY
        if count_solutions(board) == 1:
            remaining -= 1
        else:
            board[row][col] = value

    if remaining != clues:
        raise PuzzleGenerationStalled(f'could not carve down to {clues} clues on this grid')
    return board

def generate_puzzle(clues=35):
    if not 0 <= clues <= SIZE * SIZE:
        raise ValueError(f'clues must be between 0 and {SIZE * SIZE}')

    for _ in range(MAX_GENERATION_ATTEMPTS):
        board = create_empty_board()
        fill_board(board)
        solution = deep_copy(board)
        try:
            remove_cells(board, clues)
        except PuzzleGenerationStalled:
            # This grid's cell layout couldn't carve down that far -- a
            # different solved grid might, so retry from scratch rather
            # than backtracking within the same one.
            continue
        puzzle = deep_copy(board)
        return puzzle, solution

    raise PuzzleGenerationStalled(
        f'failed to generate a puzzle with {clues} clues after {MAX_GENERATION_ATTEMPTS} attempts'
    )
