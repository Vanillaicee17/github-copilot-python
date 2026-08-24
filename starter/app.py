import os
import random

from flask import Flask, render_template, jsonify, request, session
import sudoku_logic

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/new')
def new_game():
    difficulty = request.args.get('difficulty', 'medium')
    try:
        clues = sudoku_logic.clue_target_for_difficulty(difficulty)
    except ValueError as exc:
        return jsonify({'error': str(exc)}), 400

    puzzle, solution = sudoku_logic.generate_puzzle(clues)
    # The solution lives server-side in the session -- never sent to the
    # client -- so one player's game state can't leak into another's.
    session['solution'] = solution
    return jsonify({'puzzle': puzzle, 'difficulty': difficulty})

@app.route('/check', methods=['POST'])
def check_solution():
    data = request.json
    board = data.get('board')
    solution = session.get('solution')
    if solution is None:
        return jsonify({'error': 'No game in progress'}), 400
    incorrect = []
    for i in range(sudoku_logic.SIZE):
        for j in range(sudoku_logic.SIZE):
            # Only flag cells the player actually filled in -- a blank
            # cell isn't "wrong", it's just not answered yet.
            if board[i][j] != 0 and board[i][j] != solution[i][j]:
                incorrect.append([i, j])
    return jsonify({'incorrect': incorrect})

@app.route('/hint', methods=['POST'])
def hint():
    data = request.json
    board = data.get('board')
    solution = session.get('solution')
    if solution is None:
        return jsonify({'error': 'No game in progress'}), 400
    if board is None:
        return jsonify({'error': 'No board provided'}), 400

    empty_cells = [
        (i, j)
        for i in range(sudoku_logic.SIZE)
        for j in range(sudoku_logic.SIZE)
        if board[i][j] == 0
    ]
    if not empty_cells:
        return jsonify({'error': 'No empty cells remain'}), 400

    row, col = random.choice(empty_cells)
    return jsonify({'row': row, 'col': col, 'value': solution[row][col]})

if __name__ == '__main__':
    app.run(debug=True)
