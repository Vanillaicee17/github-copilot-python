// Dark-mode toggle: flips a data-theme attribute on <html> that styles.css
// keys off (in addition to following the OS preference automatically),
// and remembers the choice.
const STORAGE_KEY = 'sudoku-theme';

function getStoredTheme() {
  try {
    return localStorage.getItem(STORAGE_KEY);
  } catch {
    return null;
  }
}

function storeTheme(theme) {
  try {
    localStorage.setItem(STORAGE_KEY, theme);
  } catch {
    // Storage unavailable (private browsing, quota) -- theme just won't persist.
  }
}

function applyTheme(theme, button) {
  if (theme) {
    document.documentElement.dataset.theme = theme;
  } else {
    delete document.documentElement.dataset.theme;
  }
  if (button) {
    button.textContent = theme === 'dark' ? 'Light Mode' : 'Dark Mode';
  }
}

const toggleButton = document.getElementById('dark-mode-toggle');
applyTheme(getStoredTheme(), toggleButton);

if (toggleButton) {
  toggleButton.addEventListener('click', () => {
    const isDark = document.documentElement.dataset.theme === 'dark'
      || (!document.documentElement.dataset.theme
          && window.matchMedia('(prefers-color-scheme: dark)').matches);
    const next = isDark ? 'light' : 'dark';
    applyTheme(next, toggleButton);
    storeTheme(next);
  });
}
