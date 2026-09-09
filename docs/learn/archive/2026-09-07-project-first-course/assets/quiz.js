// learn_cube_recognition — shared lesson widgets
// 1. Quiz checker: toggles .shown on .quiz when the button is clicked.
// 2. Theme toggle: respects prefers-color-scheme by default, remembers the
//    user's manual choice in localStorage, and adds a small button in the
//    top-right corner of the page to flip light/dark.
// 3. Course navigation and spaced-retrieval warm-ups for lesson pages.
// 4. Local self-rating summaries for the course dashboard. Self-ratings are
//    practice signals only; demonstrated mastery belongs in learning-records/.

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

  // --- Course structure and spaced retrieval ---

  var COURSE = {
    '0001-what-yolo-outputs.html': {
      title: 'What YOLO outputs', ref: 'image-and-tensor-contracts.html',
      prev: null, next: '0002-how-yolo-produces-predictions.html'
    },
    '0002-how-yolo-produces-predictions.html': {
      title: 'How YOLO produces predictions', ref: 'yolo-output-and-decoding.html',
      prev: '0001-what-yolo-outputs.html', next: '0003-pytorch-and-model-training.html',
      prompts: [
        ['Without looking back, how is object detection different from image classification?', 'Detection answers both what and where; classification answers what is present without locating each object.'],
        ['Why is a confidence score evidence rather than a guarantee?', 'It is a model score shaped by training data and can be wrong, especially under domain shift.']
      ]
    },
    '0003-pytorch-and-model-training.html': {
      title: 'PyTorch and model training', ref: 'training-and-evaluation.html',
      prev: '0002-how-yolo-produces-predictions.html', next: '0004-why-the-model-fails-on-the-robot.html',
      prompts: [
        ['Interpret the three axes of the current output `[1, 7, 8400]`.', 'One batch item; seven fields per candidate; 8,400 candidate positions.'],
        ['Why does the decoder transpose `[7,8400]` to `[8400,7]`?', 'It reorganizes the same values so each row contains one candidate. It does not create or sort predictions.']
      ]
    },
    '0004-why-the-model-fails-on-the-robot.html': {
      title: 'Why the model fails on the robot', ref: 'training-and-evaluation.html',
      prev: '0003-pytorch-and-model-training.html', next: '0005-onnx-and-tensorrt.html',
      prompts: [
        ['What different jobs do the training, validation, and test sets perform?', 'Training updates parameters; validation guides choices and checkpoint selection; an untouched test measures final generalization.'],
        ['What does “best checkpoint” mean—and what does it not prove?', 'It is best under the recorded validation rule. It does not prove performance in every deployment domain.']
      ]
    },
    '0005-onnx-and-tensorrt.html': {
      title: 'ONNX and TensorRT', ref: 'onnx-and-tensorrt.html',
      prev: '0004-why-the-model-fails-on-the-robot.html', next: '0006-ros-2-perception-wiring.html',
      prompts: [
        ['Give two reasons high validation mAP can coexist with live robot failure.', 'Examples: different scale, viewpoint, lighting, background, camera processing, or a small unrepresentative validation sample.'],
        ['Why can the geometry filter not recover a cube when YOLO proposes no box?', 'Geometry is a post-filter. Without a decoded candidate box, it has no region to inspect.']
      ]
    },
    '0006-ros-2-perception-wiring.html': {
      title: 'ROS 2 perception wiring', ref: 'ros2-and-depth.html',
      prev: '0005-onnx-and-tensorrt.html', next: '0007-depth-and-geometry-filtering.html',
      prompts: [
        ['State the different purpose of `best.pt`, `best.onnx`, and `best.engine`.', 'Checkpoint for framework loading or training; portable graph boundary; target-optimized TensorRT runtime plan.'],
        ['Why must each export boundary be verified separately?', 'Graph conversion, precision, operators, and target compatibility can change or break behavior even when the intended detector is the same.']
      ]
    },
    '0007-depth-and-geometry-filtering.html': {
      title: 'Depth and geometry filtering', ref: 'ros2-and-depth.html',
      prev: '0006-ros-2-perception-wiring.html', next: '0008-evaluation-and-fine-tuning.html',
      prompts: [
        ['Trace one synchronized RGB/depth pair to the three published outputs.', 'Sync → conversion and depth guard → inference → decode → geometry decision → standard detections, vendor objects, and debug image.'],
        ['How does an invalid whole depth frame differ from sparse depth in one box?', 'An invalid frame makes the callback return early; sparse per-box depth follows the geometry fail-open policy and keeps the candidate with a quality reason.']
      ]
    },
    '0008-evaluation-and-fine-tuning.html': {
      title: 'Evaluation and fine-tuning', ref: 'training-and-evaluation.html',
      prev: '0007-depth-and-geometry-filtering.html', next: '0009-project-walkthrough-and-interview-practice.html',
      prompts: [
        ['For z-depth, should a raised cube top normally be nearer or farther than the floor behind it?', 'Nearer, so it normally has a smaller z-depth value.'],
        ['What can the geometry filter check, and what can it never create?', 'It can check depth statistics for an existing candidate box; it cannot create a missing YOLO candidate.']
      ]
    },
    '0009-project-walkthrough-and-interview-practice.html': {
      title: 'Project walkthrough and interview practice', ref: 'index.html',
      prev: '0008-evaluation-and-fine-tuning.html', next: null,
      prompts: [
        ['Why is 100% per-class frame-hit coverage not 100% accuracy?', 'Class IDs appeared in every frame, but there was no ground-truth matching by class and IoU; extra or incorrect detections may still exist.'],
        ['State the artifact chain and one verification question at each boundary.', 'best.pt → best.onnx → best.engine; verify checkpoint behavior, ONNX contract and inference, then target-engine loading, numerical behavior, and latency.'],
        ['What does M5 PARTIAL mean in one evidence-backed sentence?', 'The runtime path and empty-scene behavior work, but reliable positive detection of the room cubes at the production threshold has not passed its gate.']
      ]
    }
  };

  function currentFile() {
    var bits = window.location.pathname.split('/');
    return bits[bits.length - 1] || 'index.html';
  }

  function makeLink(href, label) {
    var link = document.createElement('a');
    link.href = href;
    link.textContent = label;
    return link;
  }

  function initLessonNavigation(file, item) {
    var main = document.querySelector('main');
    if (!main || document.querySelector('.lesson-nav')) return;
    var nav = document.createElement('nav');
    nav.className = 'course-nav lesson-nav';
    nav.setAttribute('aria-label', 'Course navigation');
    if (item.prev) nav.appendChild(makeLink(item.prev, '← Previous lesson'));
    nav.appendChild(makeLink('../index.html', 'Course home'));
    nav.appendChild(makeLink('../reference/' + item.ref, 'Quick reference'));
    nav.appendChild(makeLink('../MISSION.md', 'Mission'));
    if (item.next) nav.appendChild(makeLink(item.next, 'Next lesson →'));
    var footer = main.querySelector('footer');
    main.insertBefore(nav, footer || null);
  }

  function initTeacherPrompt() {
    var main = document.querySelector('main');
    if (!main || document.querySelector('.teacher-prompt')) return;
    var prompt = document.createElement('section');
    prompt.className = 'callout teacher-prompt';
    var title = document.createElement('p');
    title.className = 'callout-title';
    title.textContent = 'Continue with the teaching agent';
    var text = document.createElement('p');
    text.textContent = 'Ask the agent to clarify anything uncertain, challenge your explanation with a counterexample, or assess your explain-back. A learning record should be created only after you demonstrate the idea in your own words.';
    prompt.appendChild(title);
    prompt.appendChild(text);
    var anchor = main.querySelector('.lesson-nav') || main.querySelector('footer');
    main.insertBefore(prompt, anchor || null);
  }

  function storeRetrieval(file, status) {
    try {
      localStorage.setItem('lcr.retrieval.' + file, JSON.stringify({
        status: status,
        updatedAt: new Date().toISOString()
      }));
    } catch (e) { /* localStorage blocked — the exercise still works */ }
  }

  function initRetrieval(file, prompts) {
    if (!prompts || !prompts.length || document.querySelector('[data-retrieval-block]')) return;
    var main = document.querySelector('main');
    var anchor = main && main.querySelector('.concept-art');
    if (!main || !anchor) return;

    var section = document.createElement('section');
    section.className = 'retrieval-practice';
    section.setAttribute('data-retrieval-block', '');
    var heading = document.createElement('h2');
    heading.textContent = 'Retrieval warm-up';
    section.appendChild(heading);
    var intro = document.createElement('p');
    intro.className = 'retrieval-intro';
    intro.textContent = 'Answer from memory before revealing the cues. Difficulty here is useful: it strengthens retrieval and shows what deserves review.';
    section.appendChild(intro);

    prompts.forEach(function (entry, idx) {
      var card = document.createElement('div');
      card.className = 'retrieval-card';
      var label = document.createElement('label');
      label.setAttribute('for', 'retrieval-' + (idx + 1));
      label.textContent = (idx + 1) + '. ' + entry[0];
      var textarea = document.createElement('textarea');
      textarea.id = 'retrieval-' + (idx + 1);
      textarea.placeholder = 'Write or say your answer before revealing the cues…';
      var details = document.createElement('details');
      var summary = document.createElement('summary');
      summary.textContent = 'Reveal recall cues';
      var cue = document.createElement('p');
      cue.textContent = entry[1];
      details.appendChild(summary);
      details.appendChild(cue);
      card.appendChild(label);
      card.appendChild(textarea);
      card.appendChild(details);
      section.appendChild(card);
    });

    var rate = document.createElement('div');
    rate.className = 'self-rate';
    var recalled = document.createElement('button');
    recalled.type = 'button';
    recalled.textContent = 'I recalled the core idea';
    var review = document.createElement('button');
    review.type = 'button';
    review.textContent = 'I need to revisit it';
    var status = document.createElement('p');
    status.className = 'retrieval-status';
    status.textContent = 'Self-rating is saved in this browser as a practice signal, not proof of mastery.';
    recalled.addEventListener('click', function () {
      storeRetrieval(file, 'recalled');
      status.textContent = 'Saved: recalled. Explain it to the agent when you want this assessed as demonstrated learning.';
    });
    review.addEventListener('click', function () {
      storeRetrieval(file, 'review');
      status.textContent = 'Saved: revisit. Use the quick reference, then try the prompt again later without looking.';
    });
    rate.appendChild(recalled);
    rate.appendChild(review);
    rate.appendChild(status);
    section.appendChild(rate);
    anchor.insertAdjacentElement('afterend', section);
  }

  function initDashboard() {
    var dashboard = document.querySelector('[data-course-dashboard]');
    if (!dashboard) return;
    var completed = 0;
    var review = 0;
    Object.keys(COURSE).forEach(function (file) {
      if (!COURSE[file].prompts) return;
      try {
        var raw = localStorage.getItem('lcr.retrieval.' + file);
        if (!raw) return;
        completed += 1;
        if (JSON.parse(raw).status === 'review') review += 1;
      } catch (e) { /* ignore unavailable or malformed local state */ }
    });
    if (!completed) return;
    var state = document.getElementById('learning-state');
    var detail = document.getElementById('learning-detail');
    if (state) state.textContent = completed + ' retrieval check-in' + (completed === 1 ? '' : 's');
    if (detail) detail.textContent = review
      ? review + ' marked for review. These are self-ratings; mastery still requires an assessed explain-back.'
      : 'All completed warm-ups were self-rated as recalled; mastery still requires an assessed explain-back.';
  }

  // --- Bootstrap ---

  function init() {
    var btn = makeToggleButton();
    if (body) body.appendChild(btn);
    // Create the control before applying the initial theme so applyTheme()
    // can set its visible sun/moon label as well as the body class.
    applyTheme(effectiveTheme());
    initQuizzes();
    var file = currentFile();
    if (COURSE[file]) {
      initLessonNavigation(file, COURSE[file]);
      initRetrieval(file, COURSE[file].prompts);
      initTeacherPrompt();
    }
    initDashboard();

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
