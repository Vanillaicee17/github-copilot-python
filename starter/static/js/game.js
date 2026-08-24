// Board rendering, live move validation, and win detection.
import { createTimer } from './timer.js';

const SIZE = 9;
const BOX_SIZE = 3;

let puzzle = [];
let solved = false;
let hintsUsed = 0;
let currentDifficulty = 'medium';
const timer = createTimer(document.getElementById('timer'));

function createBoardElement() {
  const boardDiv = document.getElementById('sudoku-board');
  boardDiv.innerHTML = '';
  for (let i = 0; i < SIZE; i++) {
    const rowDiv = document.createElement('div');
    rowDiv.className = 'sudoku-row';
    for (let j = 0; j < SIZE; j++) {
      const input = document.createElement('input');
      input.type = 'text';
      input.inputMode = 'numeric';
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
// box. This is a plain sibling-conflict check (independent of the actual
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

function freezeBoard(inputs) {
  for (const inp of inputs) {
    inp.disabled = true;
  }
}

function handleCellChange() {
  if (solved) return;

  const boardDiv = document.getElementById('sudoku-board');
  const inputs = Array.from(boardDiv.getElementsByTagName('input'));
  const board = readBoard(inputs);
  const conflicts = findConflicts(board);

  for (const inp of inputs) {
    if (inp.disabled) continue; // givens are never wrong
    const key = `${inp.dataset.row},${inp.dataset.col}`;
    inp.classList.toggle('conflict', conflicts.has(key));
  }

  const msg = document.getElementById('message');
  if (conflicts.size > 0) {
    msg.classList.remove('success');
    msg.textContent = '';
    return;
  }

  if (isBoardFull(board)) {
    solved = true;
    freezeBoard(inputs);
    timer.stop();
    msg.classList.add('success');
    msg.textContent = 'Congratulations! You solved it!';
    // Phase 13 (leaderboard) listens for this to prompt for a name and save the score.
    document.dispatchEvent(new CustomEvent('sudoku:solved', {
      detail: {
        difficulty: currentDifficulty,
        hints: hintsUsed,
        elapsedSeconds: timer.getElapsedSeconds(),
      },
    }));
  } else {
    msg.classList.remove('success');
    msg.textContent = '';
  }
}

async function newGame() {
  const difficulty = document.getElementById('difficulty').value;
  const res = await fetch('/api/new-game', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({difficulty})
  });
  const data = await res.json();
  currentDifficulty = data.difficulty;
  hintsUsed = 0;
  renderPuzzle(data.puzzle);
  timer.start();
  const msg = document.getElementById('message');
  msg.classList.remove('success');
  msg.textContent = '';
}

async function useHint() {
  if (solved) return;

  const boardDiv = document.getElementById('sudoku-board');
  const inputs = Array.from(boardDiv.getElementsByTagName('input'));
  const board = readBoard(inputs);

  const res = await fetch('/api/hint', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({board})
  });
  const data = await res.json();
  const msg = document.getElementById('message');
  if (data.error) {
    msg.classList.remove('success');
    msg.textContent = data.error;
    return;
  }

  const inp = inputs[data.row * SIZE + data.col];
  inp.value = data.value;
  inp.disabled = true; // same locked treatment as a given -- can't be edited or re-flagged
  inp.classList.remove('conflict', 'incorrect');
  inp.classList.add('prefilled');
  hintsUsed += 1;

  handleCellChange();
}

async function checkSolution() {
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = Array.from(boardDiv.getElementsByTagName('input'));
  const board = readBoard(inputs);

  const res = await fetch('/api/check', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({board})
  });
  const data = await res.json();
  const msg = document.getElementById('message');
  if (data.error) {
    msg.classList.remove('success');
    msg.textContent = data.error;
    return;
  }

  const incorrect = new Set(data.incorrect.map(([r, c]) => `${r},${c}`));
  for (const inp of inputs) {
    if (inp.disabled) continue;
    const key = `${inp.dataset.row},${inp.dataset.col}`;
    inp.classList.toggle('incorrect', incorrect.has(key));
  }

  if (incorrect.size === 0) {
    msg.classList.add('success');
    msg.textContent = 'Congratulations! You solved it!';
  } else {
    msg.classList.remove('success');
    msg.textContent = 'Some cells are incorrect.';
  }
}

// Wire buttons
window.addEventListener('load', () => {
  document.getElementById('new-game').addEventListener('click', newGame);
  document.getElementById('check-solution').addEventListener('click', checkSolution);
  document.getElementById('hint').addEventListener('click', useHint);
  newGame();
});
