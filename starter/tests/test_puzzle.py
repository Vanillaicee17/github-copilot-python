from sudoku.generator import SIZE
from sudoku.puzzle import generate_puzzle


def test_generate_puzzle_has_requested_clue_count():
    puzzle, _ = generate_puzzle(clues=35)
    filled = sum(1 for row in puzzle for cell in row if cell != 0)
    assert filled == 35


def test_generate_puzzle_matches_solution_on_givens():
    puzzle, solution = generate_puzzle(clues=40)
    for i in range(SIZE):
        for j in range(SIZE):
            if puzzle[i][j] != 0:
                assert puzzle[i][j] == solution[i][j]


def test_solution_is_a_valid_complete_grid():
    _, solution = generate_puzzle(clues=30)
    for row in solution:
        assert sorted(row) == list(range(1, SIZE + 1))
