import pytest

import sudoku_logic


def test_generate_solved_grid_has_no_row_conflicts():
    board = sudoku_logic.create_empty_board()
    sudoku_logic.fill_board(board)
    for row in board:
        assert sorted(row) == list(range(1, sudoku_logic.SIZE + 1))


def test_count_solutions_on_a_full_grid_is_one():
    board = sudoku_logic.create_empty_board()
    sudoku_logic.fill_board(board)
    assert sudoku_logic.count_solutions(board) == 1


def test_count_solutions_on_an_empty_grid_hits_the_limit():
    board = sudoku_logic.create_empty_board()
    assert sudoku_logic.count_solutions(board, limit=2) == 2


@pytest.mark.parametrize("difficulty", ["easy", "medium", "hard"])
def test_generate_puzzle_stays_within_difficulty_clue_range(difficulty):
    low, high = sudoku_logic.DIFFICULTY_CLUES[difficulty]
    clues = sudoku_logic.clue_target_for_difficulty(difficulty)
    puzzle, solution = sudoku_logic.generate_puzzle(clues)
    filled = sum(1 for row in puzzle for cell in row if cell != 0)
    assert low <= filled <= high
    assert filled == clues


def test_generate_puzzle_has_a_unique_solution():
    puzzle, _ = sudoku_logic.generate_puzzle(30)
    assert sudoku_logic.count_solutions(puzzle) == 1


def test_generate_puzzle_matches_solution_on_givens():
    puzzle, solution = sudoku_logic.generate_puzzle(35)
    for i in range(sudoku_logic.SIZE):
        for j in range(sudoku_logic.SIZE):
            if puzzle[i][j] != 0:
                assert puzzle[i][j] == solution[i][j]


def test_clue_target_for_unknown_difficulty_raises():
    with pytest.raises(ValueError):
        sudoku_logic.clue_target_for_difficulty("impossible")
