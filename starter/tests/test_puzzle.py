import pytest

from sudoku.generator import SIZE
from sudoku.puzzle import DIFFICULTY_CLUES, generate_puzzle
from sudoku.solver import has_unique_solution


@pytest.mark.parametrize("difficulty", ["easy", "medium", "hard"])
def test_generate_puzzle_stays_within_difficulty_clue_range(difficulty):
    puzzle, _ = generate_puzzle(difficulty)
    low, high = DIFFICULTY_CLUES[difficulty]
    filled = sum(1 for row in puzzle for cell in row if cell != 0)
    assert low <= filled <= high


def test_generate_puzzle_matches_solution_on_givens():
    puzzle, solution = generate_puzzle("medium")
    for i in range(SIZE):
        for j in range(SIZE):
            if puzzle[i][j] != 0:
                assert puzzle[i][j] == solution[i][j]


def test_solution_is_a_valid_complete_grid():
    _, solution = generate_puzzle("medium")
    for row in solution:
        assert sorted(row) == list(range(1, SIZE + 1))


def test_generate_puzzle_has_a_unique_solution():
    puzzle, _ = generate_puzzle("medium")
    assert has_unique_solution(puzzle) is True


def test_unknown_difficulty_raises():
    with pytest.raises(ValueError):
        generate_puzzle("impossible")
