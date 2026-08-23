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
