// Mini-practice for the image, coordinate, and batch-size data contracts.
(function () {
  'use strict';

  var EXPECTED = {
    red: 1,
    y: 80,
    batch: 1
  };

  var MESSAGES = {
    red: {
      correct: 'Correct: BGR [0, 0, 255] puts 255 in the red channel, and 255 / 255 = 1.',
      incorrect: 'Try again: read the red channel from BGR [0, 0, 255], then normalize it with 255 / 255.'
    },
    y: {
      correct: "Correct: resize first, then add padding: 40 × 0.5 + 60 = 80.",
      incorrect: 'Try again: apply the scale to the original y value, then add the padding: 40 × 0.5 + 60.'
    },
    batch: {
      correct: 'Correct: this batch contains one image, so its batch size is 1.',
      incorrect: 'Try again: count the images in this batch. There is one image, so the batch size is 1.'
    }
  };

  function setFeedback(element, message, correct) {
    element.textContent = message;
    element.className = correct ? 'feedback correct' : 'feedback wrong';
  }

  function init() {
    var form = document.getElementById('image-practice');
    if (!form) return;

    var fields = {
      red: {
        input: document.getElementById('answer-red'),
        feedback: document.getElementById('feedback-red'),
        label: 'the normalized red-channel answer'
      },
      y: {
        input: document.getElementById('answer-y'),
        feedback: document.getElementById('feedback-y'),
        label: 'the transformed y-coordinate answer'
      },
      batch: {
        input: document.getElementById('answer-batch'),
        feedback: document.getElementById('feedback-batch'),
        label: 'the batch-size answer'
      }
    };
    var result = document.getElementById('practice-result');

    form.addEventListener('submit', function (event) {
      event.preventDefault();
      var correctCount = 0;

      Object.keys(fields).forEach(function (key) {
        var field = fields[key];
        var raw = field.input ? field.input.value.trim() : '';
        if (raw === '') {
          setFeedback(field.feedback, 'Please enter ' + field.label + '.', false);
          return;
        }

        var value = Number(raw);
        if (!Number.isFinite(value)) {
          setFeedback(field.feedback, 'Please enter a finite number for ' + field.label + '.', false);
          return;
        }

        var isCorrect = value === EXPECTED[key];
        setFeedback(field.feedback, isCorrect ? MESSAGES[key].correct : MESSAGES[key].incorrect, isCorrect);
        if (isCorrect) correctCount += 1;
      });

      if (result) {
        result.textContent = correctCount === 3
          ? 'All three answers are correct. Now explain why each value has that meaning without looking at the feedback.'
          : correctCount + ' of 3 answers are correct. Use the feedback above and try again.';
      }
    });

    form.addEventListener('reset', function () {
      Object.keys(fields).forEach(function (key) {
        if (fields[key].feedback) {
          fields[key].feedback.textContent = '';
          fields[key].feedback.className = 'feedback';
        }
      });
      if (result) result.textContent = '';
    });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
