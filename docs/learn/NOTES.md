# Teaching notes

Last refreshed: 2026-09-07

## Learner and mission

- Maher knows basic programming, Python, C++, and object-oriented programming.
- Treat machine learning, computer vision, and ROS 2 perception workflows as new subjects.
- The course builds foundations first and then applies each concept to the colored-cube project.
- Use English, concrete examples, causal explanations, and current repository evidence.
- Give a practical visual or GUI path before terminal commands when both are reasonable.

## Lesson contract

- Eleven main lessons plus four optional robot lessons after the approved editorial split; core paths target 15–20 minutes, with optional reading taking extra time.
- Required practice runs in the browser. Python tasks are explicitly optional.
- Each lesson defines its technical terms locally, including acronyms, symbols, exercises, and project applications. Earlier lessons and the glossary supplement these definitions, not replace them.
- Each lesson provides worked examples, visuals, and two or three meaningful interactive sections distributed through the material, with explanatory feedback and an explain-back. Interactions should let the learner predict, change something, and see consequences.
- Maher approved the revised Lesson 0001 as the course-wide standard on 2026-09-07; preserve the fun of the archived course interactions without copying them mechanically.
- PDF regeneration is deferred at Maher's request during the interactive revision; focus on HTML. Existing PDFs describe an earlier version.
- Visuals must clearly separate the shared input image from task outputs: classification labels, detection boxes, and segmentation masks should not look interchangeable.
- Begin with the general principle. Put repository-specific material in a clearly labelled “Applied to our cubes” section.
- Distinguish established concepts, observed checkout behavior, measured results, and open questions.
- Do not infer mastery from opening a page or answering a multiple-choice question. Create learning records after Maher explains or applies a concept.

- Readability is the priority; Maher is comfortable with a dark theme. Keep restored shared theme behavior and verify contrast in text, diagrams, controls, and feedback.

## Current project anchor

- The current checkout uses a YOLOv5u-style detector, an ONNX/TensorRT deployment path, RGB and depth inputs, and ROS 2 Humble.
- The current documented model contract is input `[1, 3, 640, 640]`, output `[1, 7, 8400]`, with classes `blue_cube`, `green_cube`, and `red_cube`.
- M5 remains PARTIAL: the runtime path works, but reliable positive detection in the room remains unresolved.
- The current geometry filter contains a reversed ordinary z-depth comparison and is an example of why code behavior and conceptual correctness must be assessed separately.

## Course history

- The previous nine-lesson, project-first course is preserved at `archive/2026-09-07-project-first-course/` with checksums.
- No commits unless Maher explicitly requests one.

- Every exercise must use only terms, symbols, and operations explicitly taught earlier in that same lesson. Expanding an acronym once is not sufficient: explain its meaning and show a worked example before testing it. Review questions against their actual prerequisite explanations, not only against a vocabulary checklist. Maher raised the N-axis question in Lesson 0002 as a failure of this rule.

- 2026-09-08: Each lesson should connect its concepts to actual repository code, especially dataset preparation and model training. Include a short source excerpt, a function/call to locate, an explanation of the concept, and a clear distinction between implemented behavior and a proposed improvement. Read executable code rather than trusting notebook titles, comments, or filenames. Keep code-reading practice browser-based; do not run training merely to teach the mapping.

- 2026-09-08: Maher is a strongly visual learner. Prefer meaningful diagrams and direct manipulation of the concept alongside terminology. Enhance existing controls with coordinated visual feedback where possible; do not add decorative images or repeated generic quizzes. Every visual must explain its colors, axes, symbols, and simplifying assumptions locally. Preserve short lessons and existing code connections.

- 2026-09-08 editorial consolidation approved: expand beyond twelve when a topic needs room. The course now has fourteen lessons: camera geometry, depth reliability, ROS 2 flow, and deployment diagnosis have separate core paths. Preserve local prerequisites while avoiding repeated glossary blocks; keep secondary code audit detail and advanced extensions optional. Fresh challenges require a committed answer and have worked explanations. This is an authoring change, not evidence that Maher has mastered the material.

- Training-focus implementation: main lessons 1–11 target better color-image cube detection and fine-tuning. Optional lessons 12–15 preserve geometry, depth, ROS 2, and deployment. A new browser-only comparison finale uses explicitly fictional counts and independent validation/test roles. Real training remains optional and must not be implied by the teaching results.

## 13 September 2026 · Recover useful archived teaching

User values the original nine lessons' useful explanations and interactions. Recover non-duplicated material into optional current-course workshops while preserving the archive. Two workshops added, linked from lessons 9/15 and the course index; no inference about learner mastery. PDFs remain deferred.
