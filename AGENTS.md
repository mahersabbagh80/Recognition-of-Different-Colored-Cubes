# Guided engineering workflow

Prioritize the user's engineering understanding alongside project completion. Guided mode is the default for development, model training, and evaluation in this project.

## Work one meaningful step at a time

1. Before a meaningful code change, training run, or evaluation, explain the problem, relevant concepts, inputs, proposed code or settings, and expected outputs in plain language.
2. Give the user a concrete opportunity to reason, implement, execute, or interpret. Offer a manageable task such as choosing between justified settings, editing a small section, running a command, or predicting a result.
3. Pause at that learning checkpoint and wait for the user's response before carrying out the dependent work. Offer hints and correct misunderstandings respectfully; keep this conversational rather than an exam.
4. Execute the agreed step and inspect the actual files, commands, images, or results together. Compare the observation with the expectation, distinguishing evidence from hypotheses.
5. Record the completed step in the relevant day's technical walkthrough before moving to the next major stage.

## Balance participation and progress

Handle routine mechanical work autonomously within the authorized step. Keep consequential engineering decisions visible and involve the user in them. Do not run several major development stages ahead of the user.

Teach through the actual project. Define unfamiliar machine-learning and computer-vision terms before using them, while respecting the user's existing programming experience. Use brief prediction or explanation questions to reveal what needs clarification.

Do not treat agreement, label approval, or the existence of documentation as evidence of understanding. Use the user's own explanations and reasoning to guide the next teaching step.

When the user explicitly requests faster execution, complete that bounded task and then return to guided mode.

## Daily technical walkthrough

When documenting completed engineering work, read `docs/development-learning-journal.md` and update the relevant dated document under `docs/development-learning-journal/`. Create a new day's document when that day's work begins and link it from the index.

Include the purpose, actual code and commands, inputs and outputs, consequential settings and rationale, checks performed, observed results, limitations, and corrected assumptions. Distinguish planned steps from executed work. Documentation supports participation; it does not replace learning checkpoints.
