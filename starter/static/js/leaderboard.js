const STORAGE_KEY = 'sudoku-leaderboard';
const MAX_ENTRIES = 10;

function loadScores() {
  try {
    const storedScores = localStorage.getItem(STORAGE_KEY);
    if (!storedScores) {
      return [];
    }

    const scores = JSON.parse(storedScores);
    return Array.isArray(scores) ? scores : [];
  } catch {
    return [];
  }
}

function saveScore(entry) {
  const scores = loadScores();
  scores.push(entry);
  scores.sort((first, second) => first.time - second.time);

  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(scores.slice(0, MAX_ENTRIES)));
  } catch {
    // Storage failures must not interrupt the solved state.
  }
}

function formatTime(totalSeconds) {
  const seconds = Math.max(0, Math.floor(Number(totalSeconds) || 0));
  const minutes = Math.floor(seconds / 60);
  return `${minutes}:${String(seconds % 60).padStart(2, '0')}`;
}

function renderLeaderboard() {
  const table = document.getElementById('leaderboard-table');
  if (!table) {
    return;
  }

  const scores = loadScores();
  table.innerHTML = `
    <thead>
      <tr><th>Rank</th><th>Name</th><th>Time</th><th>Difficulty</th><th>Hints</th></tr>
    </thead>
    <tbody></tbody>
  `;

  const body = table.querySelector('tbody');
  scores.slice(0, MAX_ENTRIES).forEach((score, index) => {
    const row = document.createElement('tr');
    [
      index + 1,
      score.name,
      formatTime(score.time),
      score.difficulty,
      score.hints,
    ].forEach((value) => {
      const cell = document.createElement('td');
      cell.textContent = value ?? '';
      row.appendChild(cell);
    });
    body.appendChild(row);
  });
}

document.addEventListener('sudoku:solved', (event) => {
  const name = window.prompt('Enter your name for the leaderboard:');
  if (name === null) {
    return;
  }

  const {difficulty, hints, elapsedSeconds} = event.detail;
  saveScore({name, time: elapsedSeconds, difficulty, hints});
  renderLeaderboard();
});

window.addEventListener('DOMContentLoaded', renderLeaderboard);
