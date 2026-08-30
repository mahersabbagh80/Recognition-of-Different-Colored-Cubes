// learn_cube_recognition — shared lesson widgets
// 1. Quiz checker: toggles .shown on .quiz when the button is clicked.
// 2. Theme toggle: respects prefers-color-scheme by default, remembers the
//    user's manual choice in localStorage, and adds a small button in the
//    top-right corner of the page to flip light/dark.

(function () {
  // --- Theme handling ---

  var STORAGE_KEY = 'lcr.theme';  // 'light' | 'dark' | absent (follow OS)
  var root = document.documentElement;
  var body = document.body;

  function getStoredChoice() {
    try { return localStorage.getItem(STORAGE_KEY); } catch (e) { return null; }
  }
  function setStoredChoice(choice) {
    try {
      if (choice) localStorage.setItem(STORAGE_KEY, choice);
      else        localStorage.removeItem(STORAGE_KEY);
    } catch (e) { /* localStorage blocked — fine, just don't persist */ }
  }

  function effectiveTheme() {
    var stored = getStoredChoice();
    if (stored === 'light' || stored === 'dark') return stored;
    return window.matchMedia &&
           window.matchMedia('(prefers-color-scheme: dark)').matches
           ? 'dark' : 'light';
  }

  function applyTheme(theme) {
    if (!body) return;
    body.classList.remove('dark', 'light');
    if (theme === 'dark')       body.classList.add('dark');
    else if (theme === 'light') body.classList.add('light');
    // else: no class, let @media (prefers-color-scheme) decide
    var btn = document.querySelector('.theme-toggle');
    if (btn) {
      btn.textContent = theme === 'dark' ? '☀' : '☾';
      btn.title = theme === 'dark'
        ? 'Switch to light theme'
        : 'Switch to dark theme';
    }
  }

  function makeToggleButton() {
    var btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'theme-toggle';
    btn.setAttribute('aria-label', 'Toggle theme');
    btn.addEventListener('click', function () {
      var current = effectiveTheme();
      var next = current === 'dark' ? 'light' : 'dark';
      setStoredChoice(next);
      applyTheme(next);
    });
    return btn;
  }

  // --- Quiz handling ---

  function initQuizzes() {
    document.querySelectorAll('.quiz').forEach(function (quiz) {
      var btn = quiz.querySelector('.check-btn');
      if (!btn) return;

      btn.addEventListener('click', function () {
        var picked = quiz.querySelector('input[type="radio"]:checked');
        var answerEl = quiz.querySelector('.answer');
        if (!picked || !answerEl) return;

        var chosenIdx = parseInt(picked.value, 10);
        var correctIdx = parseInt(quiz.dataset.correct, 10);
        var correctText = quiz.dataset.correctText || '';

        answerEl.classList.remove('correct', 'wrong');
        if (chosenIdx === correctIdx) {
          answerEl.classList.add('correct');
          answerEl.textContent = 'Correct. ' + correctText;
        } else {
          answerEl.classList.add('wrong');
          answerEl.textContent = 'Not quite. ' + correctText;
        }
        quiz.classList.add('shown');
      });
    });
  }

  // --- Bootstrap ---

  function init() {
    var btn = makeToggleButton();
    if (body) body.appendChild(btn);
    // Create the control before applying the initial theme so applyTheme()
    // can set its visible sun/moon label as well as the body class.
    applyTheme(effectiveTheme());
    initQuizzes();

    // React to OS-level theme changes, but only if the user hasn't chosen.
    if (window.matchMedia) {
      var mq = window.matchMedia('(prefers-color-scheme: dark)');
      mq.addEventListener('change', function () {
        if (!getStoredChoice()) applyTheme(effectiveTheme());
      });
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
