import os

from flask import Flask, jsonify, render_template, request, session

from sudoku.generator import SIZE
from sudoku.puzzle import generate_puzzle

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/new-game", methods=["POST"])
def new_game():
    clues = int((request.json or {}).get("clues", 35))
    puzzle, solution = generate_puzzle(clues)
    session["solution"] = solution
    return jsonify({"puzzle": puzzle})


@app.route("/api/check", methods=["POST"])
def check_solution():
    board = (request.json or {}).get("board")
    solution = session.get("solution")
    if solution is None:
        return jsonify({"error": "No game in progress"}), 400
    incorrect = []
    for i in range(SIZE):
        for j in range(SIZE):
            if board[i][j] != solution[i][j]:
                incorrect.append([i, j])
    return jsonify({"incorrect": incorrect})


if __name__ == "__main__":
    app.run(debug=True)
