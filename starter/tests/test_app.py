import json


def test_index_returns_200(client):
    res = client.get("/")
    assert res.status_code == 200


def test_new_game_returns_puzzle(client):
    res = client.post("/api/new-game", json={"difficulty": "easy"})
    assert res.status_code == 200
    data = res.get_json()
    filled = sum(1 for row in data["puzzle"] for cell in row if cell != 0)
    assert 40 <= filled <= 45


def test_new_game_rejects_unknown_difficulty(client):
    res = client.post("/api/new-game", json={"difficulty": "impossible"})
    assert res.status_code == 400
    assert "error" in res.get_json()


def test_check_without_active_game_returns_error(client):
    res = client.post("/api/check", json={"board": [[0] * 9 for _ in range(9)]})
    assert res.status_code == 400
    assert "error" in res.get_json()


def test_check_flags_incorrect_cells(client):
    client.post("/api/new-game", json={"difficulty": "easy"})
    with client.session_transaction() as sess:
        solution = sess["solution"]

    wrong_board = json.loads(json.dumps(solution))
    original = wrong_board[0][0]
    wrong_board[0][0] = original % 9 + 1  # guaranteed different digit 1-9

    res = client.post("/api/check", json={"board": wrong_board})
    assert res.status_code == 200
    incorrect = res.get_json()["incorrect"]
    assert [0, 0] in incorrect


def test_check_passes_on_correct_board(client):
    client.post("/api/new-game", json={"difficulty": "easy"})
    with client.session_transaction() as sess:
        solution = sess["solution"]

    res = client.post("/api/check", json={"board": solution})
    assert res.get_json()["incorrect"] == []


def test_check_does_not_flag_blank_cells(client):
    client.post("/api/new-game", json={"difficulty": "easy"})
    blank_board = [[0] * 9 for _ in range(9)]

    res = client.post("/api/check", json={"board": blank_board})
    assert res.get_json()["incorrect"] == []


def test_hint_without_active_game_returns_error(client):
    res = client.post("/api/hint", json={"board": [[0] * 9 for _ in range(9)]})
    assert res.status_code == 400
    assert "error" in res.get_json()


def test_hint_returns_a_cell_matching_the_solution(client):
    client.post("/api/new-game", json={"difficulty": "easy"})
    with client.session_transaction() as sess:
        solution = sess["solution"]

    blank_board = [[0] * 9 for _ in range(9)]
    res = client.post("/api/hint", json={"board": blank_board})
    assert res.status_code == 200
    data = res.get_json()
    assert data["value"] == solution[data["row"]][data["col"]]


def test_hint_never_picks_an_already_filled_cell(client):
    client.post("/api/new-game", json={"difficulty": "easy"})
    with client.session_transaction() as sess:
        solution = sess["solution"]

    # Everything filled except one cell -- hint must land on that exact cell.
    board = json.loads(json.dumps(solution))
    board[4][4] = 0

    res = client.post("/api/hint", json={"board": board})
    data = res.get_json()
    assert (data["row"], data["col"]) == (4, 4)


def test_hint_errors_when_board_is_already_full(client):
    client.post("/api/new-game", json={"difficulty": "easy"})
    with client.session_transaction() as sess:
        solution = sess["solution"]

    res = client.post("/api/hint", json={"board": solution})
    assert res.status_code == 400
    assert "error" in res.get_json()
