// Fundamentals-first course: shared theme, quiz, navigation, retrieval, and mini-labs.
(function () {
  var THEME_KEY = 'lcr.theme';
  var COURSE = [
    ['0001-choose-the-vision-task.html', 'Choose the vision task', '0002-images-are-data.html'],
    ['0002-images-are-data.html', 'Images are data', '0003-visual-features.html'],
    ['0003-visual-features.html', 'Visual features', '0004-how-models-learn.html'],
    ['0004-how-models-learn.html', 'How models learn', '0005-loss-and-optimization.html'],
    ['0005-loss-and-optimization.html', 'Loss and optimization', '0006-generalization-and-data-splits.html'],
    ['0006-generalization-and-data-splits.html', 'Generalization and data splits', '0007-neural-networks-and-convolutions.html'],
    ['0007-neural-networks-and-convolutions.html', 'Neural networks and convolutions', '0008-transfer-learning-and-augmentation.html'],
    ['0008-transfer-learning-and-augmentation.html', 'Transfer learning and augmentation', '0009-object-detection.html'],
    ['0009-object-detection.html', 'Object detection', '0010-evaluate-a-detector.html'],
    ['0010-evaluate-a-detector.html', 'Evaluate a detector', '0011-compare-a-fine-tune.html'],
    ['0011-compare-a-fine-tune.html', 'Did fine-tuning help?', '0012-depth-and-camera-geometry.html'],
    ['0012-depth-and-camera-geometry.html', 'From pixels to 3-D points', '0013-check-depth-evidence.html'],
    ['0013-check-depth-evidence.html', 'Can we trust this depth?', '0014-ros2-message-flow.html'],
    ['0014-ros2-message-flow.html', 'How ROS 2 carries a frame', '0015-deploy-and-diagnose.html'],
    ['0015-deploy-and-diagnose.html', 'Deploy the model and diagnose a result', null]
  ];

  function storedTheme() {
    try { return localStorage.getItem(THEME_KEY); } catch (_) { return null; }
  }
  function effectiveTheme() {
    return storedTheme() || (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
  }
  function applyTheme(theme) {
    document.body.classList.remove('dark', 'light');
    document.body.classList.add(theme);
    document.documentElement.style.colorScheme = theme;
    document.documentElement.style.backgroundColor = theme === 'dark' ? '#000916' : '#dfe9f3';
    var button = document.querySelector('.theme-toggle');
    if (button) {
      button.textContent = theme === 'dark' ? '☀' : '☾';
      button.setAttribute('aria-label', theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode');
      button.setAttribute('title', theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode');
    }
  }
  function initTheme() {
    var button = document.createElement('button');
    button.type = 'button';
    button.className = 'theme-toggle';
    button.setAttribute('aria-label', 'Toggle light and dark theme');
    button.addEventListener('click', function () {
      var next = effectiveTheme() === 'dark' ? 'light' : 'dark';
      try { localStorage.setItem(THEME_KEY, next); } catch (_) {}
      applyTheme(next);
    });
    document.body.appendChild(button);
    applyTheme(effectiveTheme());
  }

  function initQuizzes() {
    document.querySelectorAll('.quiz').forEach(function (quiz) {
      var button = quiz.querySelector('.check-btn');
      if (!button) return;
      button.addEventListener('click', function () {
        var chosen = quiz.querySelector('input[type="radio"]:checked');
        var answer = quiz.querySelector('.answer');
        if (!chosen || !answer) {
          if (answer) { answer.textContent = 'Choose an answer first.'; quiz.classList.add('shown'); }
          return;
        }
        var right = Number(chosen.value) === Number(quiz.dataset.correct);
        answer.className = 'answer ' + (right ? 'correct' : 'wrong');
        answer.textContent = (right ? 'Correct. ' : 'Try again. ') + (quiz.dataset.correctText || '');
        quiz.classList.add('shown');
      });
    });
  }

  function currentFile() {
    return window.location.pathname.split('/').pop() || '';
  }
  function link(href, label) {
    var a = document.createElement('a'); a.href = href; a.textContent = label; return a;
  }
  function initNavigation() {
    var file = currentFile();
    var index = COURSE.findIndex(function (entry) { return entry[0] === file; });
    if (index < 0) return;
    var main = document.querySelector('main');
    var nav = document.createElement('nav');
    nav.className = 'course-nav lesson-nav';
    nav.setAttribute('aria-label', 'Course navigation');
    if (index > 0) nav.appendChild(link(COURSE[index - 1][0], index === 11 ? '← Main course finale' : '← Previous'));
    nav.appendChild(link('../index.html', 'Course home'));
    nav.appendChild(link('../reference/fundamentals-map.html', 'Course map'));
    nav.appendChild(link('../reference/GLOSSARY.md', 'Glossary'));
    if (COURSE[index][2]) nav.appendChild(link(COURSE[index][2], index === 10 ? 'Optional: robot track →' : 'Next →'));
    var footer = main.querySelector('footer');
    main.insertBefore(nav, footer || null);

    var teacher = document.createElement('section');
    teacher.className = 'callout teacher-prompt';
    teacher.innerHTML = '<p class="callout-title">Continue with your teaching agent</p><p>Ask about anything unclear, then explain the central idea in your own words. The agent records demonstrated understanding—not page completion—as learning evidence.</p>';
    main.insertBefore(teacher, nav);
  }

  function initRanges() {
    document.querySelectorAll('[data-range-output]').forEach(function (input) {
      var output = document.getElementById(input.dataset.rangeOutput);
      var formula = input.dataset.formula || 'value';
      function update() {
        var v = Number(input.value);
        var result = v;
        if (formula === 'normalize255') result = (v / 255).toFixed(3);
        if (formula === 'squareError') result = Math.pow(v - Number(input.dataset.target || 0), 2).toFixed(2);
        if (formula === 'sigmoid') result = (1 / (1 + Math.exp(-v))).toFixed(3);
        if (output) output.textContent = result;
      }
      input.addEventListener('input', update); update();
    });
  }

  function initDashboard() {
    var el = document.getElementById('learning-state');
    if (!el) return;
    var count = 0;
    try {
      COURSE.forEach(function (entry) {
        if (localStorage.getItem('lcr.visited.' + entry[0])) count += 1;
      });
    } catch (_) {}
    el.textContent = count ? count + ' lesson page' + (count === 1 ? '' : 's') + ' opened' : 'Not yet measured';
    var detail = document.getElementById('learning-detail');
    if (detail && count) detail.textContent = 'Opening pages tracks navigation only. Explain-backs are the evidence of learning.';
  }
  function recordVisit() {
    var file = currentFile();
    if (!COURSE.some(function (entry) { return entry[0] === file; })) return;
    try { localStorage.setItem('lcr.visited.' + file, new Date().toISOString()); } catch (_) {}
  }

  function init() {
    initTheme();
    initQuizzes();
    initRanges();
    recordVisit();
    initNavigation();
    initDashboard();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
