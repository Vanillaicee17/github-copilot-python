// Elapsed-time tracking for one game, displayed in an element and readable
// by anything that needs the final time (the leaderboard, on completion).

function formatSeconds(totalSeconds) {
  const minutes = Math.floor(totalSeconds / 60);
  const seconds = totalSeconds % 60;
  return `${minutes}:${String(seconds).padStart(2, '0')}`;
}

export function createTimer(displayEl) {
  let startedAt = null;
  let elapsedSeconds = 0;
  let intervalId = null;

  function render() {
    if (displayEl) displayEl.textContent = formatSeconds(elapsedSeconds);
  }

  function stop() {
    if (intervalId !== null) {
      clearInterval(intervalId);
      intervalId = null;
    }
  }

  function start() {
    stop();
    startedAt = Date.now();
    elapsedSeconds = 0;
    render();
    intervalId = setInterval(() => {
      elapsedSeconds = Math.floor((Date.now() - startedAt) / 1000);
      render();
    }, 1000);
  }

  return {
    start,
    stop,
    getElapsedSeconds: () => elapsedSeconds,
  };
}
