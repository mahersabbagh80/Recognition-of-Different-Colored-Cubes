# Exercise prerequisite review

**Reviewed:** 2026-09-07, after the N-axis question exposed an inadequate explanation.

## Review rule

For each exercise, inspect the material that appears **before** it in the same lesson. Identify the terms, symbols, assumptions, and operations needed to answer. A vocabulary mention, answer revealed afterward, or explanation in another lesson does not substitute for teaching the prerequisite. A worked example must make a required calculation usable. Exploratory controls can teach consequences, but their labels and rules must already be understandable.

The earlier browser and content checks did not adequately enforce this requirement. This review specifically checks the teaching sequence; browser checks alone cannot establish it.

## Coverage and corrections

| Lesson | Prerequisites checked | Result |
| --- | --- | --- |
| 01 · Vision task | Image-level labels, boxes, masks, task requirements, acceptance contract | Existing explanation and examples precede the questions. |
| 02 · Images are data | RGB/BGR, normalization, scaling/padding, NCHW, batch size | Added an explicit N-axis explanation, letter-by-letter axis meanings, a two-image worked example, and the distinction between size and index. Linked the question back to that explanation. |
| 03 · Visual features | Kernel products and sums, response sign, RGB order, threshold comparisons | Existing rules and worked arithmetic precede the explorations. |
| 04 · How models learn | Feature, weight, bias, sigmoid, target type, threshold decision | Added a negative-weight example, zero-weight behavior, and an explicit accept/reject rule including equality before the controls. |
| 05 · Loss and optimization | Prediction/error/loss, gradient update, learning rate, metric selection | Added zero-rate behavior and a numerical overshooting example before the first control. |
| 06 · Generalization | Train/validation/test, session assignment, curves, hard negatives | Clarified development and the exact allowed session assignments before the checker. |
| 07 · Neural networks | Weighted unit, activation, ReLU, kernel arithmetic, channel meanings | Defined weight/bias by their operations and added a worked unit-to-ReLU calculation before practice. |
| 08 · Transfer learning | Source/target, freezing, selection, box flip, label preservation | Defined overfitting, training loss, and validation rule locally; made the fixed-feature strategy an explicit exercise assumption. The box transform already has a preceding numeric example. |
| 09 · Detection | Box coordinates, overlap area, IoU, score cutoff, NMS | Added worked shared-width/area arithmetic and a worked two-cutoff decision before the controls. |
| 10 · Evaluation | Matching, TP/FP/FN, precision/recall, subsets | Added a complete matching example and a combined-count recall example before the related exercises. |
| 11 · Geometry | Back-projection, units, median/p90, missing values, depth comparison | Added the even-count median rule, one-based rank and ceiling calculation, empty-sample case, and a worked margin/predicate comparison before practice. |
| 12 · ROS 2 | Nodes/processes, timestamps/slop, queues/rates, failure boundaries | Added time-unit conversion and pairing examples, plus queue-growth/fill/drain calculations before the controls. Final questions follow the relevant system explanations. |

## Limits

This is a review of prerequisites and instructional order, not proof that every reader will understand every explanation. Learner questions remain evidence for further revision. No new learner-mastery claim is recorded. PDFs remain deferred.

### Visual additions, 2026-09-08

New graphics reuse the locally taught calculations and controls. Their introductions explain image-axis selection, graph axes, component states, and patch highlighting before asking the learner to interpret changes. Session colors also have text labels; instance masks have identifiers; timing and matching outcomes are written out. These additions do not require running project code or introduce new assessed prerequisites.

## Editorial consolidation · fourteen-lesson edition

The former combined geometry lesson is now 11 (back-projection) and 12 (depth reliability); the former system lesson is now 13 (ROS 2 flow) and 14 (deployment diagnosis). Earlier rows describe the preceding edition.

- Lesson 2 keeps resizing and its dependent combined-input exercise together in an optional extension. The required fresh batch problem uses N/C/H/W definitions and examples on the core path.
- Lessons 3–8 replace end-of-page vocabulary recitals with new situations and worked rubrics. The optimization challenge uses the locally worked parameter-update rule; receptive-field reasoning states stride-one/no-padding assumptions.
- Lesson 9's fresh suppression case states the class, score qualification, overlap, and strict suppression rule before asking for an outcome.
- Lesson 10 introduces precision and recall before the linked plot; optional AP material is not required for the empty-scene challenge.
- Lesson 11 provides calibration numbers and optical-depth meaning before the new distance problem.
- Lesson 12 explains valid samples and fallback policy before asking what a kept candidate establishes.
- Lesson 13 teaches time conversion and pairing before the fresh timestamp question.
- Lesson 14 locally restates artifact roles and one-to-one TP/FP/FN matching before the final case. Its comparison-plan rubric separates validation choices from untouched test assessment.

Feedback appears after a committed choice. Worked reveals remain available for self-checking; the course does not treat a correct multiple-choice response as sufficient evidence of mastery.

## Training-focused tracks

Main lessons are now 1–11; optional robot lessons are 12–15. The new lesson 11 locally defines checkpoints, validation/test roles, one-to-one matching, TP/FP/FN, precision, recall, slices, and fixed requirements before its comparison question. Its data are explicitly fictional; the real experiment remains optional. The independent-test requirement is not satisfied by the repository's current validation/test alias.
