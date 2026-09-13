# Documentation index

Updated 13 September 2026. Start with the current summary; dated journals and archived plans preserve the sequence of earlier decisions.

## Current state

The new fine-tuned model has been converted and demonstrated live on Jetson with the geometry filter disabled. Enabling the filter rejected real cubes. The filter diagnosis and full reliability/localization evaluation remain open. See [evaluation](evaluation.md).

[Documentation completion check](documentation-status-2026-09-13.md) records the scope, checks and remaining engineering work.

## Reading order

| Document | Purpose |
|---|---|
| [Project README](../README.md) | Current result and tested start command |
| [Project definition](project-definition.md) | Goal, class mapping, scope and proposed acceptance |
| [Concept and approach](Concept-and-Approach.md) | Why these methods were chosen |
| [Architecture](architecture.md) | Current camera-to-output pipeline |
| [Technical stack](technical-stack.md) | Runtime, dependencies and artifact identity |
| [Training and validation workflow](training-and-validation-workflow.md) | Actual dataset and reproducible stages |
| [Methodology research](training-validation-methodology-review.md) | Sources behind held-out validation |
| [Capture checklist](indoor-cube-capture-checklist.md) | Indoor scene instructions |
| [Milestones](milestones.md) | Completed stages and remaining acceptance work |
| [Evaluation](evaluation.md) | Measured results and unperformed tests |
| [Daily journal](development-learning-journal.md) | Detailed commands, settings and checks |
| [Logbook](LOGBOOK.md) | Historical overview and September handoff |
| [Sunday progress](sunday-progress.md) | Presentation preparation and revision history |
| [Presentation package](../artifacts/presentation/README.md) | Current v8 slides, notes and tutor answers |
| [Model inventory](../models/README.md) | Local model paths and fingerprints |

## Evidence and history

- [Validation image review](validation-prediction-review-2026-09-13.md)
- [Saturday training record](development-learning-journal/2026-09-12-saturday.md)
- [Sunday deployment and live record](development-learning-journal/2026-09-13-sunday.md)
- [June M5 report](../evaluation/m5_live/report.md): historical model and tests.
- [Archive](archive/README.md): superseded research and plans.
- [Earlier fine-tune proposal](m3d-revived-plan.md): historical plan, superseded by September's own-data run.
- [Learning materials](learn/index.html): supporting course, not a completion checklist.

Large datasets, run outputs and model binaries remain local. Tracked reports summarize them; their presence in a Markdown link does not mean a fresh clone contains those artifacts.
