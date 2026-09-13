# Sunday presentation package

Current draft: **version 8 — 16 main slides and two appendix slides**. Revised after the engineering-tutor review and Maher's authorization to add missing content. Maher considered v8 good enough for now. Earlier versions remain locally as history; v8 and the supporting Markdown records are included in Git.

## Main files

- [PowerPoint v8](colored-cube-detection-presentation-v8.pptx) — editable slides with embedded English notes.
- [PDF v8](colored-cube-detection-presentation-v8.pdf) — static slide copy.
- [Speaker notes v8](speaker-notes-v8.md) — explanations and source references.
- [Review and revised outline](revision-outline-v8.md) — critical gaps and how each was addressed.
- [Tutor questions v8](tutor-questions-v8.md) — 18 questions with suggested answers.
- [Saved-evidence fallback](fallback-demo.md) — demonstration using preserved evidence.

The current aliases speaker-notes.md and tutor-questions.md match v8. The older rehearsal checklist is optional historical material; no rehearsal is requested or claimed.

## Evidence boundary

Results start on slide 12. Slides 2 and 3 contain no images. The architecture is retained; training, validation, deployment, and geometry workflows explain the method before results.

The live observations demonstrate detection with the geometry filter disabled. They do not establish full-range reliability, output FPS, or reliable depth-based localization. The geometry filter rejects genuine cubes; its root cause remains unresolved.

Evidence and exact experiment paths are referenced in the speaker notes and the [Sunday journal](../../docs/development-learning-journal/2026-09-13-sunday.md).

## Portability

The PPTX embeds its slide images and notes; the PDF is a self-contained visual copy. Raw training outputs referenced by the notes remain local and are not included in a fresh clone. The saved live screenshot is tracked with the documentation.
