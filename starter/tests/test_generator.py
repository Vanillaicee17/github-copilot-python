from sudoku.generator import SIZE, generate_solved_grid, is_safe


def test_generate_solved_grid_is_fully_filled():
    grid = generate_solved_grid()
    assert all(cell != 0 for row in grid for cell in row)


def test_generate_solved_grid_has_no_row_conflicts():
    grid = generate_solved_grid()
    for row in grid:
        assert sorted(row) == list(range(1, SIZE + 1))


def test_generate_solved_grid_has_no_column_conflicts():
    grid = generate_solved_grid()
    for col in range(SIZE):
        column = [grid[row][col] for row in range(SIZE)]
        assert sorted(column) == list(range(1, SIZE + 1))


def test_is_safe_rejects_row_duplicate():
    grid = [[0] * SIZE for _ in range(SIZE)]
    grid[0][0] = 5
    assert is_safe(grid, 0, 1, 5) is False
    assert is_safe(grid, 0, 1, 6) is True
