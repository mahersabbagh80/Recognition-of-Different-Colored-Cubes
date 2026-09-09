// Focused visual aids for lessons 0003–0008.
// Each aid is a small, text-labelled toy model attached to an existing lesson control.
(function () {
  'use strict';

  var SVG_NS = 'http://www.w3.org/2000/svg';

  function byId(id) {
    return document.getElementById(id);
  }

  function svgElement(name, attributes, text) {
    var node = document.createElementNS(SVG_NS, name);
    Object.keys(attributes || {}).forEach(function (key) {
      node.setAttribute(key, attributes[key]);
    });
    if (text !== undefined) node.textContent = text;
    return node;
  }

  function clear(node) {
    while (node && node.firstChild) node.removeChild(node.firstChild);
  }

  function prettyNumber(value, digits) {
    var text = Number(value).toFixed(digits);
    return text.replace(/-/g, '−');
  }

  function kernelProducts() {
    var select = byId('l3-patch');
    var svg = byId('l3-kernel-visual');
    if (!select || !svg) return;

    var patchGroup = byId('l3-patch-cells');
    var kernelGroup = byId('l3-kernel-cells');
    var productsGroup = byId('l3-product-lines');
    var response = byId('l3-response-value');
    var feedback = byId('l3-visual-feedback');
    var patterns = {
      rise: [0, 1, 2],
      flat: [1, 1, 1],
      fall: [2, 1, 0]
    };
    var weights = [-1, 0, 1];
    var patch = patterns[select.value] || patterns.rise;

    function drawGrid(group, values, x, y, cellWidth, cellHeight, rows) {
      clear(group);
      for (var r = 0; r < rows; r += 1) {
        for (var c = 0; c < values.length; c += 1) {
          var value = values[c];
          var cellX = x + c * (cellWidth + 3);
          var cellY = y + r * (cellHeight + 3);
          group.appendChild(svgElement('rect', {
            x: cellX,
            y: cellY,
            width: cellWidth,
            height: cellHeight,
            fill: 'var(--code-bg)',
            stroke: 'currentColor',
            'stroke-opacity': '0.45'
          }));
          group.appendChild(svgElement('text', {
            x: cellX + cellWidth / 2,
            y: cellY + cellHeight / 2 + 6,
            'text-anchor': 'middle',
            fill: 'currentColor',
            'font-family': 'monospace',
            'font-size': '17'
          }, prettyNumber(value, 0)));
        }
      }
    }

    function render() {
      patch = patterns[select.value] || patterns.rise;
      drawGrid(patchGroup, patch, 18, 42, 37, 29, 3);
      drawGrid(kernelGroup, weights, 190, 42, 37, 29, 3);
      clear(productsGroup);
      var rowSum = patch[0] * weights[0] + patch[1] * weights[1] + patch[2] * weights[2];
      var total = rowSum * 3;
      for (var row = 0; row < 3; row += 1) {
        productsGroup.appendChild(svgElement('text', {
          x: 338,
          y: 64 + row * 43,
          fill: 'currentColor',
          'font-family': 'monospace',
          'font-size': '14'
        }, 'row ' + (row + 1) + ': ' + patch[0] + '×−1 + ' + patch[1] + '×0 + ' + patch[2] + '×+1 = ' + rowSum));
      }
      response.textContent = 'R = ' + prettyNumber(total, 0);
      var direction = total > 0
        ? 'The positive-weight side sees the bright side, so the response is positive.'
        : total < 0
          ? 'The transition is reversed, so the response is negative.'
          : 'The patch is flat, so the negative and positive contributions cancel.';
      feedback.textContent = 'Each row sums to ' + prettyNumber(rowSum, 0) + '; three rows give R = ' + prettyNumber(total, 0) + '. ' + direction;
      svg.setAttribute('aria-label', 'Toy patch ' + patch.join(', ') + ' with kernel minus one, zero, plus one. Each row sums to ' + total / 3 + ' and the total response is ' + total + '.');
    }

    select.addEventListener('change', render);
    render();
  }

  function sigmoidGraph() {
    var xInput = byId('l4-x');
    var wInput = byId('l4-w');
    var bInput = byId('l4-b');
    var svg = byId('l4-sigmoid-visual');
    if (!xInput || !wInput || !bInput || !svg) return;

    var path = byId('l4-sigmoid-path');
    var vertical = byId('l4-point-v');
    var horizontal = byId('l4-point-h');
    var point = byId('l4-score-point');
    var label = byId('l4-point-label');
    var feedback = byId('l4-visual-feedback');

    function graphX(z) {
      return 60 + ((Math.max(-12, Math.min(12, z)) + 12) / 24) * 500;
    }

    function graphY(p) {
      return 236 - Math.max(0, Math.min(1, p)) * 212;
    }

    function render() {
      var x = Number(xInput.value);
      var w = Number(wInput.value);
      var b = Number(bInput.value);
      var z = w * x + b;
      var p = 1 / (1 + Math.exp(-z));
      var curve = [];
      for (var i = 0; i <= 48; i += 1) {
        var curveZ = -12 + i * 0.5;
        var curveP = 1 / (1 + Math.exp(-curveZ));
        curve.push((i === 0 ? 'M' : 'L') + graphX(curveZ).toFixed(2) + ' ' + graphY(curveP).toFixed(2));
      }
      path.setAttribute('d', curve.join(' '));
      var px = graphX(z);
      var py = graphY(p);
      vertical.setAttribute('x1', px);
      vertical.setAttribute('x2', px);
      vertical.setAttribute('y2', py);
      horizontal.setAttribute('x2', px);
      horizontal.setAttribute('y1', py);
      horizontal.setAttribute('y2', py);
      point.setAttribute('cx', px);
      point.setAttribute('cy', py);
      label.setAttribute('x', px > 455 ? px - 145 : px + 13);
      label.setAttribute('y', Math.max(py - 9, 35));
      label.textContent = '(z=' + prettyNumber(z, 2) + ', p=' + p.toFixed(3) + ')';
      feedback.textContent = 'Selected point: z = ' + prettyNumber(z, 3) + ' and sigmoid output p = ' + p.toFixed(3) + '. Moving x, w, or b moves the score before the sigmoid maps it.';
      svg.setAttribute('aria-label', 'Sigmoid graph with selected score z ' + z.toFixed(3) + ' and output ' + p.toFixed(3) + '.');
    }

    [xInput, wInput, bInput].forEach(function (input) { input.addEventListener('input', render); });
    render();
  }

  function predictionLoss() {
    var input = byId('l5-lr');
    var svg = byId('l5-prediction-visual');
    if (!input || !svg) return;
    var afterBar = byId('l5-after-bar');
    var afterLabel = byId('l5-after-label');
    var beforeLoss = byId('l5-before-loss');
    var afterLoss = byId('l5-after-loss');
    var feedback = byId('l5-visual-feedback');
    var maxValue = 12;
    var baseline = 180;
    var scale = 150 / maxValue;

    function render() {
      var eta = Number(input.value);
      var beforePrediction = 3;
      var target = 6;
      var afterPrediction = 3 + 30 * eta;
      var lossBefore = Math.pow(beforePrediction - target, 2);
      var lossAfter = Math.pow(afterPrediction - target, 2);
      var boundedPrediction = Math.max(0, Math.min(maxValue, afterPrediction));
      afterBar.setAttribute('y', baseline - boundedPrediction * scale);
      afterBar.setAttribute('height', boundedPrediction * scale);
      afterBar.setAttribute('fill', lossAfter <= lossBefore ? '#0f766e' : '#b42318');
      afterLabel.textContent = 'prediction ' + afterPrediction.toFixed(2);
      beforeLoss.textContent = 'squared loss = ' + lossBefore.toFixed(2);
      afterLoss.textContent = 'squared loss = ' + lossAfter.toFixed(2);
      var result = eta === 0
        ? 'With η = 0, the update does not move: prediction and loss stay at their starting values.'
        : Math.abs(afterPrediction - target) < 1e-9
        ? 'The update lands on the target exactly.'
        : afterPrediction < target
          ? 'The update moves toward the target but remains below it.'
          : 'The update passes the target: this is overshooting in the toy example.';
      feedback.textContent = 'η = ' + eta.toFixed(2) + ': w′ = ' + (1 + 12 * eta).toFixed(2) + ', b′ = ' + (1 + 6 * eta).toFixed(2) + ', prediction ŷ′ = ' + afterPrediction.toFixed(2) + ', squared loss = ' + lossAfter.toFixed(2) + '. ' + result;
      svg.setAttribute('aria-label', 'Before prediction 3 with squared loss 9; after learning rate ' + eta.toFixed(2) + ', prediction ' + afterPrediction.toFixed(2) + ' and squared loss ' + lossAfter.toFixed(2) + '.');
    }

    input.addEventListener('input', render);
    render();
  }

  function sessionSplit() {
    var svg = byId('l6-session-visual');
    var randomPanel = byId('l6-random-panel');
    var sessionPanel = byId('l6-session-panel');
    var randomButton = byId('l6-random-view');
    var sessionButton = byId('l6-session-view');
    var feedback = byId('l6-visual-feedback');
    if (!svg || !randomPanel || !sessionPanel || !randomButton || !sessionButton) return;

    var colors = { train: '#02adf8', validation: '#d69e2e', test: '#9aa9b5' };

    function frame(group, x, y, label, split) {
      group.appendChild(svgElement('rect', {
        x: x,
        y: y,
        width: 83,
        height: 30,
        rx: 2,
        fill: 'var(--code-bg)',
        stroke: colors[split],
        'stroke-width': 3
      }));
      group.appendChild(svgElement('text', {
        x: x + 41.5,
        y: y + 20,
        'text-anchor': 'middle',
        fill: 'currentColor',
        'font-family': 'Arial,sans-serif',
        'font-size': 12
      }, label + ' · ' + split));
    }

    function draw() {
      clear(randomPanel);
      clear(sessionPanel);
      var rows = [
        ['A', 90, ['A1', 'train'], ['A2', 'validation']],
        ['B', 140, ['B1', 'train'], ['B2', 'validation']],
        ['C', 190, ['C1', 'test'], ['C2', 'test']]
      ];
      rows.forEach(function (row) {
        var name = row[0];
        var y = row[1];
        randomPanel.appendChild(svgElement('text', { x: 18, y: y - 7, fill: 'currentColor', 'font-size': 12 }, 'session ' + name));
        frame(randomPanel, 82, y - 25, row[2][0], row[2][1]);
        frame(randomPanel, 177, y - 25, row[3][0], row[3][1]);
        sessionPanel.appendChild(svgElement('text', { x: 335, y: y - 7, fill: 'currentColor', 'font-size': 12 }, 'session ' + name));
        var split = name === 'A' ? 'train' : name === 'B' ? 'validation' : 'test';
        frame(sessionPanel, 399, y - 25, name + '1', split);
        frame(sessionPanel, 494, y - 25, name + '2', split);
      });
      randomPanel.appendChild(svgElement('line', { x1: 166, y1: 65, x2: 166, y2: 201, stroke: '#b42318', 'stroke-width': 2, 'stroke-dasharray': '5 4' }));
      randomPanel.appendChild(svgElement('text', { x: 171, y: 218, fill: '#b42318', 'font-size': 12 }, 'leakage risk'));
      sessionPanel.appendChild(svgElement('text', { x: 420, y: 218, fill: '#0f766e', 'font-size': 12 }, 'C stays untouched test'));
    }

    function focus(mode) {
      var random = mode === 'random';
      randomPanel.setAttribute('opacity', '1');
      sessionPanel.setAttribute('opacity', '1');
      randomButton.setAttribute('aria-pressed', random ? 'true' : 'false');
      sessionButton.setAttribute('aria-pressed', mode === 'session' ? 'true' : 'false');
      if (mode === 'random') {
        feedback.textContent = 'Random frame focus: A1/A2 and B1/B2 share neighboring conditions across train and validation. Validation can look too easy because it includes familiar conditions. Session C remains a separate test session in both diagrams.';
      } else if (mode === 'session') {
        feedback.textContent = 'Whole-session focus: every session stays in one split, and Session C is untouched test evidence. This reduces leakage from neighboring frames; whether the sessions represent future use still needs checking.';
      } else {
        feedback.textContent = 'Initial comparison: randomizing neighboring frames can leak the same visual situation across train and validation; whole-session grouping tests session change directly.';
      }
    }

    draw();
    randomButton.addEventListener('click', function () { focus('random'); });
    sessionButton.addEventListener('click', function () { focus('session'); });
    var splitCheck = byId('l6-split-check');
    if (splitCheck) splitCheck.addEventListener('click', function () {
      var values = ['a', 'b', 'c'].map(function (key) { return (byId('l6-session-' + key) || {}).value; });
      if (values[0] && values[1] && values[2] === 'test' && new Set(values).size === 3) focus('session');
    });
    focus();
  }

  function convolutionTracer() {
    var select = byId('l7-kernel');
    var svg = byId('l7-conv-visual');
    if (!select || !svg) return;
    var inputGroup = byId('l7-input-cells');
    var kernelGroup = byId('l7-kernel-cells');
    var outputGroup = byId('l7-output-cells');
    var equation = byId('l7-conv-equation');
    var feedback = byId('l7-visual-feedback');
    var buttons = Array.prototype.slice.call(document.querySelectorAll('.l7-output-cell'));
    var input = [[1, 2, 0], [0, 1, 3], [2, 1, 1]];
    var kernels = {
      edge: [[1, 0], [-1, 1]],
      sum: [[1, 1], [1, 1]],
      contrast: [[1, -1], [-1, 1]]
    };
    var selected = 0;

    function drawCells(group, values, rows, cols, x, y, size, gap, selectedIndex) {
      clear(group);
      for (var r = 0; r < rows; r += 1) {
        for (var c = 0; c < cols; c += 1) {
          var index = r * cols + c;
          var cellX = x + c * (size + gap);
          var cellY = y + r * (size + gap);
          var active = selectedIndex === index;
          group.appendChild(svgElement('rect', {
            x: cellX,
            y: cellY,
            width: size,
            height: size,
            fill: active ? 'var(--accent-soft)' : 'var(--code-bg)',
            stroke: active ? '#b42318' : 'currentColor',
            'stroke-width': active ? 3 : 1,
            'stroke-opacity': active ? 1 : 0.45
          }));
          group.appendChild(svgElement('text', {
            x: cellX + size / 2,
            y: cellY + size / 2 + 7,
            'text-anchor': 'middle',
            fill: 'currentColor',
            'font-family': 'monospace',
            'font-size': 18
          }, prettyNumber(values[r][c], 0)));
        }
      }
    }

    function render() {
      var kernel = kernels[select.value] || kernels.edge;
      var selectedRow = Math.floor(selected / 2);
      var selectedCol = selected % 2;
      var outputs = [];
      for (var r = 0; r < 2; r += 1) {
        outputs[r] = [];
        for (var c = 0; c < 2; c += 1) {
          outputs[r][c] = input[r][c] * kernel[0][0] + input[r][c + 1] * kernel[0][1] + input[r + 1][c] * kernel[1][0] + input[r + 1][c + 1] * kernel[1][1];
        }
      }
      drawCells(inputGroup, input, 3, 3, 22, 45, 47, 5, -1);
      drawCells(kernelGroup, kernel, 2, 2, 250, 70, 47, 5, -1);
      drawCells(outputGroup, outputs, 2, 2, 470, 70, 47, 5, selected);
      var highlight = byId('l7-patch-highlight');
      if (highlight) highlight.parentNode.removeChild(highlight);
      highlight = svgElement('rect', {
        id: 'l7-patch-highlight',
        x: 19 + selectedCol * 52,
        y: 42 + selectedRow * 52,
        width: 105,
        height: 105,
        fill: 'none',
        stroke: '#b42318',
        'stroke-width': 4,
        'stroke-dasharray': '7 4'
      });
      svg.insertBefore(highlight, inputGroup);
      var patchValues = [input[selectedRow][selectedCol], input[selectedRow][selectedCol + 1], input[selectedRow + 1][selectedCol], input[selectedRow + 1][selectedCol + 1]];
      var kernelValues = [kernel[0][0], kernel[0][1], kernel[1][0], kernel[1][1]];
      var terms = patchValues.map(function (value, index) { return value + '×' + prettyNumber(kernelValues[index], 0); });
      var result = outputs[selectedRow][selectedCol];
      equation.textContent = terms.join(' + ') + ' = ' + result;
      feedback.textContent = 'Output cell ' + (selectedRow === 0 ? 'top' : 'bottom') + ' ' + (selectedCol === 0 ? 'left' : 'right') + ': ' + terms.join(' + ') + ' = ' + result + '. The dashed box marks the matching 2 × 2 input patch.';
      buttons.forEach(function (button, index) { button.setAttribute('aria-pressed', index === selected ? 'true' : 'false'); });
      svg.setAttribute('aria-label', 'Selected output cell ' + (selected + 1) + ' uses the input patch ' + patchValues.join(', ') + ' and kernel products ' + terms.join(', ') + ', giving ' + result + '.');
    }

    buttons.forEach(function (button, index) {
      button.addEventListener('click', function () { selected = index; render(); });
    });
    select.addEventListener('change', render);
    render();
  }

  function transferPlan() {
    var freeze = byId('l8-freeze');
    var target = byId('l8-target');
    var svg = byId('l8-transfer-visual');
    if (!freeze || !target || !svg) return;
    var backboneBox = byId('l8-backbone-box');
    var outputBox = byId('l8-output-box');
    var backboneState = byId('l8-backbone-state');
    var outputState = byId('l8-output-state');
    var note = byId('l8-transfer-note');
    var feedback = byId('l8-visual-feedback');

    function render() {
      var backboneGood = freeze.value === 'backbone';
      var targetGood = target.value === 'cubes';
      var outputFrozen = freeze.value === 'output';
      backboneBox.setAttribute('stroke', freeze.value ? (backboneGood ? '#0f766e' : '#b42318') : '#02adf8');
      outputBox.setAttribute('stroke', outputFrozen ? '#b42318' : (target.value ? (targetGood ? '#0f766e' : '#b42318') : '#02adf8'));
      backboneState.textContent = freeze.value ? (backboneGood ? 'frozen' : 'trainable') : 'candidate: frozen';
      outputState.textContent = outputFrozen ? 'frozen' : (target.value ? (targetGood ? 'trainable: cube data' : 'trainable: source data') : 'candidate: trainable');
      if (!freeze.value || !target.value) {
        note.textContent = 'Choose both controls to test this plan.';
        feedback.textContent = 'Initial graphic: the source backbone is the reusable feature extractor; the new output is the task-specific adaptation point.';
      } else if (backboneGood && targetGood) {
        note.textContent = 'Fixed backbone; train the new output with cube labels and boxes.';
        feedback.textContent = 'Good plan: source features stay fixed while target cube examples adapt the new output. Validation evidence would still be needed.';
      } else {
        note.textContent = 'Reconsider this fixed-feature plan; see the explanation below.';
        feedback.textContent = 'Reconsider the roles: the fixed-feature plan freezes the backbone and adapts a new output using cube classes, boxes, and camera conditions.';
      }
      svg.setAttribute('aria-label', 'Transfer plan: backbone is ' + backboneState.textContent + '; new cube output is ' + outputState.textContent + '.');
    }

    freeze.addEventListener('change', render);
    target.addEventListener('change', render);
    render();
  }

  function init() {
    kernelProducts();
    sigmoidGraph();
    predictionLoss();
    sessionSplit();
    convolutionTracer();
    transferPlan();
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
}());
