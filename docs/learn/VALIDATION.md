# Interactive course validation

**Date:** 2026-09-07  
**Scope:** Fifteen active HTML lessons: eleven main training lessons and four optional robot lessons. Earlier sections document preceding editions; the training-track section records the current organization.

## Teaching revision

- Each lesson starts with a fundamental concept, defines its working vocabulary locally, supplies a worked example, and then connects the concept to the colored-cube project.
- Browser practice is distributed through the lessons: task comparisons, pixel/layout exploration, filter arithmetic, model scores, gradient updates, data splits, convolution, augmentation, boxes, evaluation, geometry, and ROS 2 message handling.
- Lessons include explanatory feedback, an explain-back, primary-source links, reference navigation, and a reminder to ask the teaching agent follow-up questions.
- Shared styles, navigation, theme switching, and reusable feedback classes are used across all twelve lessons.
- A separate read-only content review covered all twelve lessons. Corrections clarify inference on labeled evaluation inputs, the model-image box coordinate grid, QoS compatibility, and the distinction between transport and synchronizer queues. Quiz answer lengths are balanced; exploratory control labels retain descriptive wording.

## Browser and structural checks

- Chrome loaded all twelve pages through local HTTP. Every range control was exercised at both endpoints and every select option was exercised. No page JavaScript errors or failed lesson-resource requests were recorded.
- All twelve pages were checked at 390-pixel viewport width without horizontal page overflow.
- Light/dark switching and persistence after reload passed for each lesson. Screenshots were captured in both themes.
- Focused checks covered the filter response sign, a color-rule false positive, sigmoid/checkpoint feedback, exact gradient-update values, loss-marker coordinates, whole-session splits, ReLU, dynamic SVG descriptions, mirrored box coordinates, missing depth, and local-depth failure handling.
- Detection/evaluation checks covered identical/disjoint box overlap, the NMS equality boundary, score filtering, wrong-class matching, undefined precision with no accepted predictions, and performance on a difficult data subset.
- All four forms were exercised with incomplete and correct submissions; reset behavior was checked where provided, and both wrong geometry answers were checked for explanatory feedback.
- Twelve inline scripts and the shared JavaScript passed syntax checks. The lessons have no duplicate IDs or unresolved static label references. Fifty-eight local links from the course home and lessons resolve; HTML fragment targets were checked where present.
- `git diff --check -- docs/learn` passed.

## Visual checks

- Nineteen default SVG diagrams were captured and inspected, alongside representative full-page layouts.
- The classification output uses whole-image labels; detection uses separate labeled boxes; semantic segmentation uses class-colored masks.
- The loss-curve marker follows the stated quadratic exactly. The overfitting plot has unfilled axes. The camera pixel lies on the illustrated viewing ray. The horizontal-flip box preserves its stated scale and dimensions.
- Diagram labels use a light diagram surface in both themes. Exercise labels and controls are separated, and range/select controls have usable width.
- A computed-color check of visible non-SVG lesson text found no contrast ratios below 4.5:1 against the resolved solid background in either theme. This is a targeted readability check, not a comprehensive accessibility certification.

## Evidence and limits

- Toy values, diagrams, and queue models are teaching simulations, not project measurements. Current repository behavior is distinguished from validated scientific or deployment performance.
- No camera/robot experiment, model retraining, deployment-accuracy evaluation, or learner-mastery assessment was performed by this HTML revision.
- The 15–20-minute lesson duration is a design estimate; actual reading and practice time has not been measured.
- PDFs were **not regenerated**. Existing PDF links are explicitly labeled as earlier versions; use the HTML for the current course.

## Review artifacts

Temporary browser checks and screenshots are under `tmp/course-qa/`; they are development review artifacts, not required course assets.

## Follow-up: exercise prerequisites

After Maher identified the N-axis question as insufficiently taught, the course received a separate question-by-question prerequisite review. See [Exercise prerequisite review](EXERCISE-PREREQUISITES.md) for coverage and corrections. Definitions, rules, and worked operations were added before affected exercises; explanation after an answer is no longer treated as adequate prerequisite coverage. The original validation did not catch this teaching gap.

## Training-code connections · 2026-09-08

The project-application sections now connect lesson concepts to executable dataset-preparation, fine-tuning, prediction-reporting, capture, and runtime code. They include selected source lines, function/call links, a plain-language explanation, and code-reading prompts with revealed answers. Current implementation is separated from proposed improvements.

Source inspection established that the training notebook currently has no executable cells; the hard-negative dataset configuration reuses validation images for test; the prediction reporter increments its purported frame-hit counter per detection; and the planned evaluation entry point remains a placeholder. The lessons describe these limitations instead of treating filenames or comments as evidence of completion. The training script writes a checkpoint separately from the robot's deployed engine.

No training, dataset rebuilding, model export, deployment, or production-code modification was performed for these teaching additions.

For these additions, 14 source excerpts were checked against repository source lines. All twelve lessons passed local-link/label checks and the Chrome range/select, theme-persistence, and mobile-overflow checks again. The new code-reading reveals work; the text contrast check remained clear in both themes, and representative code sections were inspected visually.

## Visual learning additions · 2026-09-08

Each lesson received a topic-specific visual addition or an extension of an existing explorer:

1. Semantic versus instance masks, including separate instance identifiers.
2. A batch builder showing N, C, H, and W as visible parts of an image array.
3. Patch/kernel products and their summed filter response.
4. A sigmoid curve with a live score marker across the full control range.
5. Before/after prediction bars with the target and squared losses.
6. Neighboring-frame versus whole-session split diagrams.
7. A selectable convolution output linked to its exact input patch and arithmetic.
8. A transfer-learning diagram showing frozen/trainable component roles.
9. Candidate boxes linked to score filtering and suppression controls.
10. Reference/prediction boxes linked to true-positive, false-positive, and false-negative counts.
11. A camera ray linking pixel position, depth, and lateral position.
12. A timestamp diagram showing whether RGB and depth satisfy the timing tolerance.

The additions extend existing controls where possible. Their local introductions explain symbols, visual encodings, and toy assumptions; project-code connections remain available after the fundamentals.

Checks: all twelve pages passed local-link/ID/label checks, Chrome interaction smoke checks, theme persistence, and 390-pixel page-overflow checks. Visible non-SVG text passed the existing contrast scan in both themes. New SVGs use a constant light drawing surface with dark text in both themes, and were inspected as rendered images. Focused checks covered filter signs, extreme sigmoid scores, zero/overshooting updates, all twelve convolution kernel/cell combinations, transfer-role combinations, semantic/instance differences, batch dimensions, suppression boundaries, matching counts, camera-ray collinearity, and timestamp equality. No new diagram text exceeded its SVG bounds in the default-state scan of lessons 3–8. These checks are not a comprehensive accessibility certification or learner study.

## Editorial consolidation · 2026-09-08 · current fourteen-lesson edition

The core writing now starts from concrete questions, reduces repeated definition blocks, and uses fresh challenges with worked explanations. Detailed code investigations, benchmark conventions, and selected extensions remain available in optional notes. Lesson 2 keeps its resizing explanation and dependent exercise in the same extension. Original source excerpts and the interactive teaching diagrams remain available.

The two overloaded final lessons became four: 11 covers back-projection; 12 covers depth reliability; 13 covers ROS 2 message flow; 14 covers artifact handoff and a final diagnostic case. Course navigation, index, mission constraints, and reference map now reflect fourteen lessons. The last case connects artifact selection, one-to-one matching, and a controlled validation/test comparison.

New teaching material includes a real project training image (an unchanged copy of `data/hardneg/images/train/cubes_m4b_0004.jpg`), a local-slope illustration with a numerical nudge, a two-layer receptive-field diagram, and a precision–recall trace coordinated with the existing score cutoff. The PR trace connects the stated finite operating points; it is explicitly not an AP integration rule.

Completed checks for this edition:

- Fourteen pages pass local HTML/ID/label and active course/reference link/fragment checks; fourteen inline scripts and the edited shared scripts pass syntax checks.
- Chrome loads all fourteen pages with no page errors or missing lesson resources. All range endpoints and select options are exercised, including controls in expanded optional notes. Theme persistence and 390-pixel page width pass.
- Fifteen fresh checks pass unanswered, correct, and incorrect submissions with explanatory feedback.
- Focused numerical checks cover the existing filter, sigmoid, update, convolution, NMS, matching, back-projection, and timing controls. Selected PR marker positions match the reported precision/recall counts.
- Rendered review covers the new slope and receptive-field drawings, PR plot, revised final-lesson openings, and fresh problem layouts. The slope curve and tangent use a consistent coordinate mapping; the receptive-field explanation states stride one and no padding.
- The visible non-SVG text contrast scan reports no findings in either theme. Diagram meaning and readability were inspected separately; these checks are not an accessibility certification.

No production training, export, deployment, or PDF generation was performed. The duration labels describe estimated core paths; optional reading and individual practice may take longer. Learning outcomes still require the learner’s explanation or application, not page completion or a passing UI check.

## Training-focused tracks · current edition

The course contains eleven main lessons and four optional robot lessons. The new main lesson 11 compares a baseline and fine-tuned candidate using fictional validation counts, condition slices, fixed matching rules, and an explicit acceptance requirement. The robot material is retained as lessons 12–15; the main-course navigation labels entry into it as optional.

Practical coverage was strengthened in lessons 4 (annotation and missing-label inspection), 6 (varied capture sessions and split planning), and 8 (the script’s HSV, mosaic, and MixUp settings). A positive image containing a distracting region is distinguished from a verified cube-free hard-negative crop. Repeated arithmetic is optional where it does not add a new training decision.

Validation completed: all fifteen pages load in Chrome without page errors or failed resources; expanded optional controls pass range/select checks, theme persistence, and 390-pixel page-overflow checks. Sixteen fresh checks pass unanswered/correct/incorrect feedback. The comparison chart’s counts and ratios match the supplied data, including undefined recall for an empty reference slice. Course links, fragment targets, the 15-entry index, and the main-to-optional navigation boundary pass. The non-SVG text contrast scan is clear in both themes, and the comparison chart was visually inspected. No model was trained, evaluated on real data, exported, or deployed by this revision; PDFs remain unchanged.

## 13 September 2026 · Archived-material recovery

Seventeen active HTML pages: eleven main lessons, four optional robot lessons and two optional recovered workshops. Existing sequence navigation remains the 15-lesson route; optional workshops are reached through the index and contextual links in lessons 9 and 15.

Checks performed: JavaScript syntax; HTML local-file links, duplicate IDs and label references across all 17 pages; archive SHA256SUMS verification; browser checks of the two new workshops (three candidate grids, three coordinate stages, four evidence choices, all four gate combinations, correct responses to both fresh questions); 390px overflow checks in light/dark modes; no browser page errors. The camera-coordinate graphic was visually inspected. Existing lessons' interactions were not exhaustively rerun because their behavior was unchanged. PDFs were not generated. This verifies the recovered teaching artifacts, not detector performance or learner understanding.

Additional recovery in lesson 13: illustrated selected-subset versus whole-box distinction, extents, aspect ratio and the limits of optical-depth standard deviation. Checked against `geometry_filter.py`, visually inspected the rendered diagram and verified 390px layout. No filter code changed.

The restored lesson-15 geometry-rejection choice was browser-tested for its feedback and mobile layout. Its current-example link points to the dated 13 September live record; the older hard-negative script example is explicitly distinguished from the newer model inventory.
