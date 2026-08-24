# Refactor a Sudoku Game written in Python Flask

Use this simple Sudoku game as a starting point to practice your skills with GitHub Copilot. The goal is to refactor the code to use modern technologies, while also adding new features and improving the overall user experience.

## Getting Started

Follow these instructions to get a copy of the project up and running on your local machine.

### Dependencies

```
- Modern web browser (Chrome, Firefox, Edge, etc.)
- Python 3
```

### Installation

1. Fork this repository to your GitHub account. (You can use the "Fork" button on the top right corner of the repository page.)

2. Clone your forked repository to your local machine.

3. Open a terminal window and navigate to the "github-copilot-python/starter" directory.

4. Create a Python virtual environment and activate it (optional but highly recommended).

```bash
python3 -m venv .venv
source .venv/bin/activate
```

5. Install required Python packages.

```bash
pip install -r requirements.txt
```

6. Run the Flask app.

```bash
python app.py
```

7. Open http://127.0.0.1:5000 in your browser.

## Running the Tests

Test dependencies (`pytest`) are already listed in `requirements.txt`, so step 5 above installs them. From the `starter/` directory, with the virtual environment active:

```bash
pytest -v
```

## Features

- **Puzzle generation with a guaranteed unique solution** (`sudoku_logic.py`) — a randomized-backtracking full grid is carved down cell by cell, re-verifying after every removal (via a solution counter that branches on the most-constrained cell) that exactly one solution still exists. Generation is bounded to a time budget rather than a fixed retry count, so even the sparsest Hard-difficulty boards can't cause a long hang.
- **Difficulty levels** — Easy (40–45 clues), Medium (30–35), Hard (22–27), selected before starting a new game.
- **Locked givens** — prefilled cells (and hints) are rendered read-only and visually distinct; they can't be edited or flagged.
- **Live conflict highlighting** — every keystroke/blur re-checks the board client-side for row/column/box duplicates and highlights only the specific cell(s) in conflict, distinct in color from the Check button's solution mismatches.
- **Check** — compares filled, non-given cells against the actual stored solution (kept server-side in the Flask session, never sent to the client) and highlights any that are wrong.
- **Hint** — reveals one correct value for a currently-empty cell and locks it like a given; hints used are tracked per game and included in the saved score.
- **Timer** — starts on new game, stops the instant the puzzle is solved.
- **Dark mode** — follows the OS preference automatically, with a manual toggle that overrides it and persists the choice in `localStorage`.
- **Completion message** — a full board with zero conflicts is solved by construction (thanks to the uniqueness guarantee above), so no round trip is needed to detect a win.
- **Top 10 leaderboard** — completing a puzzle prompts for a name and saves `{name, time, difficulty, hints}` to `localStorage`, sorted by fastest time and capped at 10 entries.
