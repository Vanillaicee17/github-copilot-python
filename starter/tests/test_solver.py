from sudoku.generator import EMPTY, generate_solved_grid
from sudoku.solver import count_solutions, has_unique_solution


def test_empty_board_has_more_than_one_solution():
    empty_board = [[EMPTY] * 9 for _ in range(9)]
    assert count_solutions(empty_board, limit=2) == 2


def test_full_solved_grid_has_exactly_one_solution():
    grid = generate_solved_grid()
    assert count_solutions(grid, limit=2) == 1
    assert has_unique_solution(grid) is True


def test_grid_missing_one_cell_is_still_unique():
    grid = generate_solved_grid()
    grid[0][0] = EMPTY
    assert has_unique_solution(grid) is True


def test_does_not_mutate_the_input_board():
    grid = generate_solved_grid()
    original = [row[:] for row in grid]
    count_solutions(grid, limit=2)
    assert grid == original
