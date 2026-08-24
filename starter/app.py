import os
import random

from flask import Flask, jsonify, render_template, request, session

from sudoku.generator import SIZE
from sudoku.puzzle import DIFFICULTY_CLUES, generate_puzzle

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/new-game", methods=["POST"])
def new_game():
    difficulty = (request.json or {}).get("difficulty", "medium")
    if difficulty not in DIFFICULTY_CLUES:
        return jsonify({"error": f"Unknown difficulty: {difficulty!r}"}), 400
    puzzle, solution = generate_puzzle(difficulty)
    session["solution"] = solution
    return jsonify({"puzzle": puzzle, "difficulty": difficulty})


@app.route("/api/check", methods=["POST"])
def check_solution():
    board = (request.json or {}).get("board")
    solution = session.get("solution")
    if solution is None:
        return jsonify({"error": "No game in progress"}), 400
    incorrect = []
    for i in range(SIZE):
        for j in range(SIZE):
            # Only flag cells the player actually filled in -- an empty
            # cell isn't "wrong", it's just not answered yet.
            if board[i][j] != 0 and board[i][j] != solution[i][j]:
                incorrect.append([i, j])
    return jsonify({"incorrect": incorrect})


@app.route("/api/hint", methods=["POST"])
def hint():
    board = (request.json or {}).get("board")
    solution = session.get("solution")
    if solution is None:
        return jsonify({"error": "No game in progress"}), 400
    if board is None:
        return jsonify({"error": "No board provided"}), 400
    empty_cells = [(i, j) for i in range(SIZE) for j in range(SIZE) if board[i][j] == 0]
    if not empty_cells:
        return jsonify({"error": "No empty cells remain"}), 400
    row, col = random.choice(empty_cells)
    return jsonify({"row": row, "col": col, "value": solution[row][col]})


if __name__ == "__main__":
    app.run(debug=True)
