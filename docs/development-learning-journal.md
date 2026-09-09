# Development learning journal

This journal connects the work we actually perform to the machine-learning and computer-vision ideas behind it. Read it alongside the [daily plan](sunday-presentation-plan.md), [progress record](sunday-progress.md), and [learning course](learn/index.html).

The plan describes intended work. The progress record tracks completed actions and evidence. This journal explains the reasoning, tradeoffs, and lessons. Completing an engineering step does not by itself establish that Maher can explain the underlying concept.

Keep one dated document per day, with a section after each meaningful completed step: the question, concepts, actual action, reason for the decision, evidence and limitations, and one or two explain-back questions. Record changed assumptions as well as successful decisions. Keep future work explicitly marked as planned.

## Purpose clarified: engineering understanding

Maher wants enough technical detail to understand, reproduce, and defend the development decisions to his tutor. The journal should bridge the concepts and the executable implementation. A summary of activities alone is insufficient.

For each meaningful engineering step, document:

1. **Purpose and prerequisite:** the problem being solved and what must already be true.
2. **Inputs:** the actual data, configuration, model, and their provenance.
3. **Implementation:** the relevant script/function/library, exact executed command or a short source excerpt, and what the library performs internally.
4. **Settings and rationale:** explain every consequential option before using it, including alternatives and why this choice fits the experiment.
5. **Outputs:** exact artifact locations and what each contains.
6. **Verification:** checks performed, observed results, limitations, and failures. Distinguish a software check from evidence of model quality.
7. **Engineering explanation:** a question Maher should be able to answer, with enough preceding explanation to reason about it.

Explain a new operation briefly before executing it; then record the exact implementation and observed result afterward. Define technical terms without reteaching basic programming. Use compact code examples and links to full scripts rather than dumping terminal transcripts. Mark proposed commands as unexecuted. Record corrections openly. Never infer conceptual mastery solely from agreement or label approval.

## Daily documents

| Day | Technical work documented | Status |
|---|---|---|
| [Wednesday, 9 September](development-learning-journal/2026-09-09-wednesday.md) | Annotation review, image selection, box conversion, development split, training-environment checks, smoke training, and the 60-epoch experiment with fixed-confidence evaluation | In progress; initial substantive training completed |

Thursday through Sunday will be added as work occurs. The [daily plan](sunday-presentation-plan.md) describes intended future activities; they are not recorded here as completed work.

Each daily document follows the actual engineering steps, explains the code and configuration, links to evidence, and separates results from hypotheses. This index remains the stable entry point for the journal.
