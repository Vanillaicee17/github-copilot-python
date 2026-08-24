// Client-side rendering and interaction for the Flask-backed Sudoku
const SIZE = 9;
const BOX_SIZE = 3;

let puzzle = [];
let solved = false;
let hintsUsed = 0;
let currentDifficulty = 'medium';

// --- Timer -----------------------------------------------------------
let timerStartedAt = null;
let timerElapsedSeconds = 0;
let timerIntervalId = null;

function formatSeconds(totalSeconds) {
  const minutes = Math.floor(totalSeconds / 60);
  const seconds = totalSeconds % 60;
  return `${minutes}:${String(seconds).padStart(2, '0')}`;
}

function renderTimer() {
  const el = document.getElementById('timer');
  if (el) el.textContent = formatSeconds(timerElapsedSeconds);
}

function stopTimer() {
  if (timerIntervalId !== null) {
    clearInterval(timerIntervalId);
    timerIntervalId = null;
  }
}

function startTimer() {
  stopTimer();
  timerStartedAt = Date.now();
  timerElapsedSeconds = 0;
  renderTimer();
  timerIntervalId = setInterval(() => {
    timerElapsedSeconds = Math.floor((Date.now() - timerStartedAt) / 1000);
    renderTimer();
  }, 1000);
}

// --- Board -------------------------------------------------------------
function createBoardElement() {
  const boardDiv = document.getElementById('sudoku-board');
  boardDiv.innerHTML = '';
  for (let i = 0; i < SIZE; i++) {
    const rowDiv = document.createElement('div');
    rowDiv.className = 'sudoku-row';
    for (let j = 0; j < SIZE; j++) {
      const input = document.createElement('input');
      input.type = 'text';
      input.maxLength = 1;
      input.className = 'sudoku-cell';
      input.dataset.row = i;
      input.dataset.col = j;
      input.dataset.boxParity = (Math.floor(i / 3) + Math.floor(j / 3)) % 2;
      input.addEventListener('input', (e) => {
        e.target.value = e.target.value.replace(/[^1-9]/g, '');
        handleCellChange();
      });
      input.addEventListener('blur', handleCellChange);
      rowDiv.appendChild(input);
    }
    boardDiv.appendChild(rowDiv);
  }
}

function renderPuzzle(puz) {
  puzzle = puz;
  solved = false;
  hintsUsed = 0;
  createBoardElement();
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  for (let i = 0; i < SIZE; i++) {
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const val = puzzle[i][j];
      const inp = inputs[idx];
      if (val !== 0) {
        inp.value = val;
        inp.disabled = true;
        inp.classList.add('prefilled');
      } else {
        inp.value = '';
        inp.disabled = false;
      }
    }
  }
}

function readBoard(inputs) {
  const board = [];
  for (let i = 0; i < SIZE; i++) {
    board[i] = [];
    for (let j = 0; j < SIZE; j++) {
      const val = inputs[i * SIZE + j].value;
      board[i][j] = val ? parseInt(val, 10) : 0;
    }
  }
  return board;
}

// Cells that share a value with another cell in the same row, column, or
// box -- a plain sibling-conflict check (independent of the actual
// solution), so it can run instantly on every keystroke with no round trip.
function findConflicts(board) {
  const conflicts = new Set();

  const flagDuplicates = (cells) => {
    const seenAt = new Map();
    for (const [r, c] of cells) {
      const val = board[r][c];
      if (val === 0) continue;
      if (seenAt.has(val)) {
        conflicts.add(`${r},${c}`);
        conflicts.add(seenAt.get(val));
      } else {
        seenAt.set(val, `${r},${c}`);
      }
    }
  };

  for (let r = 0; r < SIZE; r++) {
    flagDuplicates(Array.from({length: SIZE}, (_, c) => [r, c]));
  }
  for (let c = 0; c < SIZE; c++) {
    flagDuplicates(Array.from({length: SIZE}, (_, r) => [r, c]));
  }
  for (let boxRow = 0; boxRow < SIZE; boxRow += BOX_SIZE) {
    for (let boxCol = 0; boxCol < SIZE; boxCol += BOX_SIZE) {
      const cells = [];
      for (let i = 0; i < BOX_SIZE; i++) {
        for (let j = 0; j < BOX_SIZE; j++) {
          cells.push([boxRow + i, boxCol + j]);
        }
      }
      flagDuplicates(cells);
    }
  }

  return conflicts;
}

function isBoardFull(board) {
  return board.every((row) => row.every((cell) => cell !== 0));
}

function handleCellChange() {
  if (solved) return;

  const boardDiv = document.getElementById('sudoku-board');
  const inputs = Array.from(boardDiv.getElementsByTagName('input'));
  const board = readBoard(inputs);
  const conflicts = findConflicts(board);

  for (const inp of inputs) {
    if (inp.disabled) continue; // givens/hints are never wrong
    const key = `${inp.dataset.row},${inp.dataset.col}`;
    inp.classList.toggle('conflict', conflicts.has(key));
  }

  const msg = document.getElementById('message');
  if (conflicts.size > 0) {
    msg.innerText = '';
    return;
  }

  if (isBoardFull(board)) {
    solved = true;
    stopTimer();
    for (const inp of inputs) inp.disabled = true;
    msg.classList.add('success');
    msg.innerText = 'Congratulations! You solved it!';
    // leaderboard.js listens for this to prompt for a name and save the score.
    document.dispatchEvent(new CustomEvent('sudoku:solved', {
      detail: {
        difficulty: currentDifficulty,
        hints: hintsUsed,
        elapsedSeconds: timerElapsedSeconds,
      },
    }));
  } else {
    msg.innerText = '';
  }
}

async function newGame() {
  const difficultySelect = document.getElementById('difficulty');
  const difficulty = difficultySelect ? difficultySelect.value : 'medium';
  const res = await fetch(`/new?difficulty=${encodeURIComponent(difficulty)}`);
  const data = await res.json();
  const msg = document.getElementById('message');
  if (data.error) {
    msg.classList.remove('success');
    msg.innerText = data.error;
    return;
  }
  currentDifficulty = data.difficulty;
  renderPuzzle(data.puzzle);
  startTimer();
  msg.classList.remove('success');
  msg.innerText = '';
}

async function checkSolution() {
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  const board = readBoard(Array.from(inputs));
  const res = await fetch('/check', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({board})
  });
  const data = await res.json();
  const msg = document.getElementById('message');
  if (data.error) {
    msg.classList.remove('success');
    msg.innerText = data.error;
    return;
  }
  const incorrect = new Set(data.incorrect.map(x => x[0]*SIZE + x[1]));
  for (let idx = 0; idx < inputs.length; idx++) {
    const inp = inputs[idx];
    if (inp.disabled) continue;
    inp.classList.toggle('incorrect', incorrect.has(idx));
  }
  if (incorrect.size === 0) {
    msg.classList.add('success');
    msg.innerText = 'Congratulations! You solved it!';
  } else {
    msg.classList.remove('success');
    msg.innerText = 'Some cells are incorrect.';
  }
}

async function useHint() {
  if (solved) return;
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = Array.from(boardDiv.getElementsByTagName('input'));
  const board = readBoard(inputs);

  const res = await fetch('/hint', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({board})
  });
  const data = await res.json();
  const msg = document.getElementById('message');
  if (data.error) {
    msg.classList.remove('success');
    msg.innerText = data.error;
    return;
  }

  const inp = inputs[data.row * SIZE + data.col];
  inp.value = data.value;
  inp.disabled = true; // same locked treatment as a given
  inp.classList.remove('conflict', 'incorrect');
  inp.classList.add('prefilled');
  hintsUsed += 1;

  handleCellChange();
}

// Wire buttons
window.addEventListener('load', () => {
  document.getElementById('new-game').addEventListener('click', newGame);
  document.getElementById('check-solution').addEventListener('click', checkSolution);
  const hintButton = document.getElementById('hint');
  if (hintButton) hintButton.addEventListener('click', useHint);
  // initialize
  newGame();
});
