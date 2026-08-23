# Project conventions for Copilot

This is a Flask + vanilla JS Sudoku game. Follow these rules in every suggestion:

- Python: type hints on all function signatures, PEP 8, f-strings over .format().
- Keep game logic (generator/solver/validator) separate from Flask routes —
  routes only orchestrate, they never contain Sudoku rules directly.
- Never trust the client: solution grids live server-side in the Flask
  session, never sent to the browser in the page HTML or JSON.
- Every new function gets a docstring one sentence long, only when the
  *why* isn't obvious from the name.
- JS: no frameworks, ES6+, one concern per file (game.js, timer.js,
  leaderboard.js).
- CSS: custom properties for all colors, both a light and dark palette,
  no inline styles.
- Add or update a pytest test for every function you touch.
