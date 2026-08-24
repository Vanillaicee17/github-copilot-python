// Dark-mode toggle: flips a data-theme attribute on <html> that every CSS
// custom property in styles.css keys off, and remembers the choice.
const STORAGE_KEY = 'sudoku-theme';

function getStoredTheme() {
  try {
    return localStorage.getItem(STORAGE_KEY);
  } catch (e) {
    return null;
  }
}

function storeTheme(theme) {
  try {
    localStorage.setItem(STORAGE_KEY, theme);
  } catch (e) {
    // Storage unavailable (private browsing, quota) -- theme just won't persist.
  }
}

function applyTheme(theme, button) {
  document.documentElement.dataset.theme = theme;
  if (button) {
    button.textContent = theme === 'dark' ? 'Light Mode' : 'Dark Mode';
  }
}

// Module scripts run after the DOM is parsed, so this can apply the saved
// theme immediately rather than waiting for the `load` event (which would
// also wait on images/stylesheets and cause a visible flash).
const toggleButton = document.getElementById('dark-mode-toggle');
applyTheme(getStoredTheme() === 'dark' ? 'dark' : 'light', toggleButton);

if (toggleButton) {
  toggleButton.addEventListener('click', () => {
    const next = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
    applyTheme(next, toggleButton);
    storeTheme(next);
  });
}
