"""Count how many solutions a Sudoku grid has, stopping early once a cap is hit.

A puzzle is only valid if this returns exactly 1 -- finding a second solution
means the puzzle is ambiguous and shouldn't be handed to a player.
"""
import copy

from .generator import EMPTY, SIZE, is_safe


def _find_empty(board: list[list[int]]) -> tuple[int, int] | None:
    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] == EMPTY:
                return row, col
    return None


def count_solutions(board: list[list[int]], limit: int = 2) -> int:
    """Return the number of solutions for `board`, capped at `limit`.

    Stops searching as soon as `limit` solutions are found, so callers that
    only care whether a puzzle is uniquely solvable (limit=2) don't pay for
    an exhaustive search.
    """
    board = copy.deepcopy(board)
    count = 0

    def solve() -> bool:
        nonlocal count
        empty = _find_empty(board)
        if empty is None:
            count += 1
            return count >= limit
        row, col = empty
        for candidate in range(1, SIZE + 1):
            if is_safe(board, row, col, candidate):
                board[row][col] = candidate
                if solve():
                    board[row][col] = EMPTY
                    return True
                board[row][col] = EMPTY
        return False

    solve()
    return count


def has_unique_solution(board: list[list[int]]) -> bool:
    return count_solutions(board, limit=2) == 1
