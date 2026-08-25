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

## How this file shapes Copilot's output

Copilot (Chat, inline completions, and code review) reads every
`.github/copilot-instructions.md` file in the repo automatically and folds it
into the context for *every* request in this workspace — you don't re-paste
it into each prompt. That means:

- Completions match project conventions by default. E.g. asking for "a
  function to validate a row" here produces a type-hinted, PEP 8 function
  with a docstring only if the *why* isn't obvious — not whatever style
  Copilot would guess from training data alone.
- It resolves ambiguity Copilot can't infer from the code around the cursor.
  The instruction "solution grids live server-side, never sent to the
  client" is why Copilot won't suggest returning `solution` from `/new` even
  though that would be the simplest way to satisfy a naive "check the
  answer" request.
- It's advisory, not enforced. Copilot can still get it wrong, especially on
  rules that require reasoning across files (like "routes never contain
  Sudoku rules directly"). Treat this file as raising the odds of a
  good-first-suggestion, not a guarantee — review generated code against
  these rules the same as you would a teammate's PR.
- Specific and falsifiable beats vague. "Add or update a pytest test for
  every function you touch" is something Copilot can act on directly. A
  rule like "write good tests" gives it nothing concrete to match against.

### What a good instructions file looks like

Effective instruction files tend to state, concretely:

1. **Code style** — naming conventions, formatting, patterns (e.g. "type
   hints on all function signatures, f-strings over `.format()`" above).
2. **Project-specific constraints** — frameworks/libraries in play and the
   architecture boundaries between them (e.g. "game logic stays separate
   from Flask routes").
3. **Non-obvious invariants** — things Copilot can't infer just by reading
   the code, like a security/privacy boundary (e.g. "the solution never
   reaches the client").
4. **Example prompts or interaction patterns**, when the team wants Copilot
   used a particular way — e.g. "when asked to add a new game rule, first
   propose the function signature and a test before implementing the body."

Keep it short and scannable (a bullet list, not prose) — Copilot weighs
every rule in the file on every request, so vague or redundant entries
dilute the specific ones.

### References

- [GitHub Docs: Configuring GitHub Copilot](https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions)
- [GitHub Copilot: Best practices for prompts and instructions](https://docs.github.com/en/copilot/using-github-copilot/best-practices-for-using-github-copilot)
- [GitHub Blog: custom instructions for GitHub Copilot](https://github.blog/ai-and-ml/github-copilot/)
- [GitHub Copilot — Responsible Use Guidelines](https://resources.github.com/copilot-trust-center/responsible-use/)
- [W3C WCAG Color and Contrast Guidelines](https://www.w3.org/WAI/WCAG21/Understanding/use-of-color.html)
