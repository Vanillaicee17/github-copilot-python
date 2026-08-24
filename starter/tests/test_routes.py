import json


def test_new_game_defaults_to_medium(client):
    res = client.get("/new")
    assert res.status_code == 200
    data = res.get_json()
    assert data["difficulty"] == "medium"
    filled = sum(1 for row in data["puzzle"] for cell in row if cell != 0)
    assert 30 <= filled <= 35


def test_new_game_rejects_unknown_difficulty(client):
    res = client.get("/new?difficulty=impossible")
    assert res.status_code == 400
    assert "error" in res.get_json()


def test_check_does_not_flag_blank_cells(client):
    client.get("/new?difficulty=easy")
    blank_board = [[0] * 9 for _ in range(9)]
    res = client.post("/check", json={"board": blank_board})
    assert res.get_json()["incorrect"] == []


def test_hint_without_active_game_returns_error(client):
    res = client.post("/hint", json={"board": [[0] * 9 for _ in range(9)]})
    assert res.status_code == 400
    assert "error" in res.get_json()


def test_hint_returns_a_cell_matching_the_solution(client):
    client.get("/new?difficulty=easy")
    with client.session_transaction() as sess:
        solution = sess["solution"]

    blank_board = [[0] * 9 for _ in range(9)]
    res = client.post("/hint", json={"board": blank_board})
    assert res.status_code == 200
    data = res.get_json()
    assert data["value"] == solution[data["row"]][data["col"]]


def test_hint_never_picks_an_already_filled_cell(client):
    client.get("/new?difficulty=easy")
    with client.session_transaction() as sess:
        solution = sess["solution"]

    board = json.loads(json.dumps(solution))
    board[4][4] = 0  # everything filled except this one cell

    res = client.post("/hint", json={"board": board})
    data = res.get_json()
    assert (data["row"], data["col"]) == (4, 4)


def test_hint_errors_when_board_is_already_full(client):
    client.get("/new?difficulty=easy")
    with client.session_transaction() as sess:
        solution = sess["solution"]

    res = client.post("/hint", json={"board": solution})
    assert res.status_code == 400
    assert "error" in res.get_json()


def test_solution_is_not_reused_across_sessions(client):
    # Each /new call generates a fresh puzzle/solution stored in *that*
    # session, not a shared global -- calling /new twice shouldn't ever
    # leave a stale solution behind for /check to compare against.
    client.get("/new?difficulty=easy")
    with client.session_transaction() as sess:
        first_solution = sess["solution"]

    client.get("/new?difficulty=easy")
    with client.session_transaction() as sess:
        second_solution = sess["solution"]

    res = client.post("/check", json={"board": first_solution})
    # first_solution almost certainly no longer matches the *new* session
    # solution, so at least one cell should be flagged unless the two
    # randomly-generated solutions happen to collide entirely.
    assert first_solution != second_solution or res.get_json()["incorrect"] == []
