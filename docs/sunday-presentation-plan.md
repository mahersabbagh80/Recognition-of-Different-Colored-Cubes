# Sunday presentation plan — 9–13 September 2026

Prepared on 8 September; revised on 9 September after Maher clarified his instructor’s dataset requirement. Technical execution has not started.

**Presentation:** Sunday, 13 September, 18:00 Europe/Berlin (CEST).
**Time budget:** three hours daily Wednesday–Sunday: 12 preparation hours before Sunday, plus three Sunday hours. Optional extra hours are contingency, not required capacity. No work session is planned for Tuesday.
**Delivery deadline:** Saturday evening. Prepare 30 minutes of material, leaving up to 15 minutes for questions. Sunday is for checks and rehearsal.

## 1. What we are trying to deliver

A repeatable demonstration of red, green, and blue cube recognition on the JetRover, an honest evaluation, and an explanation Maher can give confidently.

The presentation package should contain:

- A working demonstration in explicitly documented conditions, if technically achievable.
- A short local backup video showing the actual tested behavior.
- A results table with correct detections, misses, false detections, and live processing rate.
- A simple architecture diagram, before/after examples, and limitations.
- Approximately 10–12 slides, speaker notes, and a rehearsed demonstration sequence.
- The exact model, configuration, startup procedure, and evidence locations.

Keep the existing YOLO → ONNX → TensorRT → ROS 2 approach. Navigation, manipulation, new model architectures, and expanding the learning course are outside this week's scope.

### Completion and presentation are different checkpoints

**Technical target proposed for Wednesday confirmation:** at least 80% precision and recall for each color on the frozen test, and at least 5 processed frames per second on the Jetson. Precision means the fraction of reported cubes that are correct; recall means the fraction of actual cubes found. Use the reviewed evaluator's matching rules and report sample counts. This proposal makes detection quality explicit; it does not silently replace the original project's color-accuracy criterion.

Test the intended 20–80 cm range and report results by distance. Success in a narrower range is a scoped demonstration, not completion of the original full-range goal. Record non-cube distractor results separately: an empty room alone does not prove shape discrimination. Small-sample results are evidence for these tested conditions, not broad reliability claims.

**Presentation fallback:** if these targets are missed, present the implemented pipeline, measured behavior, diagnosed failures, and remaining work as a progress report. Do not mark incomplete milestones finished.

## 2. How to work with Codex each day

Use **this existing task in the Codex desktop app** as the main conversation all week. Open the same project and return here; no new daily task is needed. Keep technical decisions, robot testing, results, and presentation preparation together.

Use a separate ChatGPT conversation only if useful for practising explanations. Give it the current presentation notes and verified results; bring useful edits back here. Do not rely on another conversation knowing the current repository or this week's decisions.

Separate development tasks are optional for independent work, not a daily ritual. A separate checkout can contain changes absent from this project, so completion elsewhere must be followed by review and integration. The existing evaluation checkout is the first example to resolve. Background subagents, when useful, follow the user's standing cost-conscious delegation instructions; Maher does not need to manage them.

**Daily routine:**

1. Send the day's start message below, filling in robot access and available time.
2. Codex reads this plan and `docs/sunday-progress.md`, checks actual files, and names the first checkpoint.
3. Codex performs available software work and gives Maher one physical action at a time. Prefer the image viewer and annotation gallery for visual work. Give terminal steps only where needed.
4. Maher positions objects, operates hardware, confirms labels, and reports observations. For errors, share the exact output or a saved log, not only “it failed.”
5. Before stopping, use the end-of-session message. Codex records results, paths, blockers, and the next action.

Keep all three hours inclusive of explanations and wrap-up. If a step overruns, trim optional work and record the blocked checkpoint; do not silently spend tomorrow's rehearsal time.

### Messages you can use at any time

**When confused:** “Pause the implementation. Explain this step from first principles, define the terms, and ask me one question to check my understanding.”

**When time is running out:** “I have 30 minutes left. Prioritize today's checkpoint and save a clear handoff. Tell me what we should defer.”

**End of session:** “End today's session. Update docs/sunday-progress.md with verified results, evidence paths, changed files, exact model/settings, remaining blockers, any running job and how to check it, and the first action next time. Explain the result to me in plain English.”

**If a new task becomes necessary:** “Continue the Sunday presentation preparation in this project. Read docs/sunday-presentation-plan.md and docs/sunday-progress.md first. Verify the current checkout and artifacts before acting. My available time is [time], and robot access is [status]. Resume from the recorded next action.”

Training can exceed a session only after a job is explicitly launched and its logging, power requirements, and recovery/check procedure are recorded. The plan does not schedule automatic work or reminders. Do not assume Codex continues after a conversation ends.

## 3. Wednesday, 9 September — prepare our own dataset and new training run

**Revised direction:** Maher collected 98 robot-camera images following his instructor’s request to use his own dataset. Use reviewed self-captured images for this project’s new training and validation data; do not mix in the external cube dataset or initialize from the old cube-specific model. Start from a compatible general pretrained YOLO checkpoint, whose identity and provenance must be verified before training. This is transfer learning, not training from random weights. General pretraining still uses external knowledge; disclose that in the presentation. The instructor has not been reported to prohibit general pretraining.

Maher explicitly requested removal of the old cube-trained model on 9 September. Its local deployment artifacts and M2/M3c training checkpoints were removed; historical reports remain. Copies outside this checkout, including the robot, have not been changed. Compare the new model with recorded historical results only with their dataset limitations made explicit. New training is the intended path, rather than conditional on whether the old cube model can be rescued.

**Session start:** Return to this task with available time and robot-access status. Begin with the image inventory and annotation gallery, then follow the schedule below.

| Elapsed time | Maher | Codex | Checkpoint/output |
|---|---|---|---|
| 0:00–0:20 | Explain how the 98 images were captured and whether any have previously been used in training. | Verify image inventory and existing evaluation/annotation work; preserve unrelated edits. | Known image provenance and one working checkout. |
| 0:20–0:35 | Provide a simple camera view if the robot is accessible. | Briefly check class mapping, input handling, and training/export compatibility. Record depth-filter checks still required before deployment. | Identify an obvious pipeline blocker without spending the session trying to rescue the old model. |
| 0:35–1:45 | Review and correct boxes and colors in the gallery. | Prepare labels for useful self-captured images and verify each selected frame has complete annotations, including empty backgrounds. | Reviewed candidate training images and remaining gaps. |
| 1:45–2:15 | Confirm capture-session grouping; capture missing validation examples if needed and feasible. | Allocate training and validation by session; check class coverage, near-duplicates, and label format. Reserve fresh final-test captures separately. | A defensible data split, or a clearly recorded capture blocker. |
| 2:15–2:40 | Inspect training examples with labels overlaid. | Verify a compatible general pretrained checkpoint, run a training smoke check, and launch the bounded new training run only if data is ready. Save to a separate candidate location. | Training started with logs, or exact preparation remaining. |
| 2:40–2:55 | Explain the difference between general pretraining, our cube training, and evaluation. | Correct misunderstandings and save speaker notes. | Clear explanation in Maher’s words. |
| 2:55–3:00 | Confirm next session availability. | Save progress, any running-job details, and Thursday’s first action. | Reliable handoff. |

The existing September 7 report is at `/home/maher/.codex/worktrees/67ee/Recognition-of-Different-Colored-Cubes/evaluation/robot_dataset_2026-09-07/report.md`. It reports 13 provisionally annotated images; the remaining images must not be treated as labeled. Review and integrate useful evaluator/annotation work rather than recreate it.

Use image quality, variety, and class coverage to select useful images; 98 is not a guaranteed sufficient training set. Keep related frames from the same capture session together. If the existing collection cannot provide distinct training and validation sessions, capture additional self-collected validation images rather than randomly splitting near-identical frames. Keep the final test separate from both.

**Pass:** reviewed self-captured data, a defensible split, and a verified training setup. Starting training today is desirable, but accurate annotation takes priority. Historical diagnostic images used for new training can no longer serve as independent proof of improvement; evaluate the new candidate on held-out validation data instead.

**Fallback:** if annotation or capture takes longer, finish a coherent reviewed subset and record the remaining work. Thursday begins by completing that preparation. Robot unavailability does not prevent reviewing existing images; synchronized RGB/depth validation remains required before trusting the deployed filter.

**Optional extra hour:** complete annotations or capture a distinct validation session. No new architecture. Old model cleanup is recorded separately in the progress record.

## 4. Thursday, 10 September — improve and choose a candidate

**Start message:** “Start Thursday's three-hour session. Read yesterday's progress, resolve its highest-priority blocker, and evaluate the new candidate on held-out validation data. Explain whether the evidence supports deploying it.”

| Elapsed time | Maher | Codex | Checkpoint/output |
|---|---|---|---|
| 0:00–0:20 | Review Wednesday's findings. | Check job status and baseline evidence. | Check readiness of the new run using our own data and general pretrained initialization; address diagnosed blockers. |
| 0:20–1:20 | Correct remaining labels or capture a specific missing development condition. | Complete or run the new training on reviewed self-captured data; verify any needed bounded fix and evaluate the new candidate on held-out validation images. | Results for each color, misses, and false detections. |
| 1:20–2:00 | Inspect examples where the candidate succeeds and fails. | Verify candidate export if ready; investigate one concrete cause if not. | Candidate decision with evidence. |
| 2:00–2:30 | Describe project motivation and initial challenges. | Draft the presentation outline and select existing figures. | Slide structure started before Saturday. |
| 2:30–2:50 | Explain training versus validation versus final test. | Check understanding and refine speaker notes. | Clear explanation of how improvement is measured. |
| 2:50–3:00 | Confirm the demonstrated conditions. | Save progress and Friday priorities. | Candidate or explicit recovery branch. |

**Pass:** all three colors produce useful detections in simple validation scenes, with measured precision and recall reported. Historical baseline comparisons must name differences in the evaluated data. A visually appealing single image is insufficient. The old local model was removed at Maher’s request; preserve new candidate versions as they are produced.

**Fallback:** if the candidate misses a color in simple scenes, spend the remaining technical time diagnosing that failure. Do not launch an open-ended hyperparameter search. If training is still running, record how it will be checked; do not call an unmeasured candidate successful.

**Optional extra hour:** one evidence-driven correction or completing a candidate comparison.

## 5. Friday, 11 September — deploy, verify, and freeze scope

**Updated handoff agreed Thursday evening:** Wednesday's core preparation, training and explanation are complete. Friday starts with the deferred candidate-improvement work below. The original deployment timetable is conditional on readiness and remaining time; do not assume two full daily plans fit into three hours.

**Start message:** “Start Friday's session by reading the latest progress and confirming our available time. Guide me through a small batch of additional robot-camera photos inside my room. First show a numbered checklist describing exactly where to put the robot and cubes, the background and distances, and why each scene is useful. Work one setup at a time. Then review the labels and agree on the next training/evaluation step before executing it. Reassess deployment and presentation priorities against the time remaining.”

**Capture instructions to prepare before taking photos:**

- Use Maher's apartment, probably the same room. Outdoor captures are outside this agreed scope. Work with the actual floor, furniture and available indoor space.
- For every numbered setup, specify the robot's location and camera-facing direction; cube colors and count; cube distance from the camera and left/center/right placement in its view; cube orientation; and the visible background/scenery and lighting.
- State what remains fixed and what changes between shots, how many photos to take, and what to check in the camera preview. If room dimensions or camera framing are needed to make instructions concrete, establish them first rather than inventing measurements.
- Prioritize the weak blue-cube cases while including green/red combinations and empty-room backgrounds. Explain each setup's purpose; do not assume more images guarantee better performance.
- Assign whole arrangements to training additions or held-out development validation before retraining. Keep the later independent final test separate. Avoid repetitive frames being split across these groups.
- Lead the sequence and give Maher the physical capture steps. Pause for each setup's result and adapt to what the camera actually sees. A detailed scene checklist has been requested but has not yet been produced or executed.

**Original deployment sequence below — use only after the capture/improvement checkpoint and time review:**

| Elapsed time | Maher | Codex | Checkpoint/output |
|---|---|---|---|
| 0:00–0:20 | Ready the robot and viewing setup. | Confirm candidate identity, configuration, and deployment procedure. | Known version to test. |
| 0:20–1:15 | Run single-color, combined, empty, and distractor scenes. | Export/deploy; verify synchronized depth and filter behavior on real cubes and distractors; compare raw and final detections with saved-image behavior; measure processed-frame rate and ROS outputs. | Live evidence, or a specific deployment blocker. |
| 1:15–1:45 | Repeat agreed demo sequence and capture a short provisional video. | Fix only a diagnosed issue, recheck affected behavior, then freeze model/settings and scope. | Written freeze decision. |
| 1:45–2:30 | Review slide wording and explain design choices. | Draft slides/notes and prepare Saturday's capture checklist and annotation workflow. | Presentation draft; test procedure ready. |
| 2:30–2:50 | Explain why TensorRT and ROS 2 are used. | Ask likely tutor questions. | Two more practised explanations. |
| 2:50–3:00 | Confirm Saturday setup. | Record frozen artifacts and exact startup steps. | Saturday can begin with testing. |

**Pass:** repeatable live output, documented operating conditions, and frozen candidate/configuration. Detection rate must be measured from processed frames, not inferred solely from camera rate or publishing frequency.

**Fallback:** if live deployment fails, present recorded/offline evidence with its limitations. If only a narrower distance range works, document it before the final test. If depth filtering is not validated, disclose any RGB-only demonstration and do not claim validated depth-based shape rejection.

**Optional extra hour:** resolve a known deployment issue or finish slide notes. No new features.

## 6. Saturday, 12 September — measure and finish the presentation

**Start message:** “Start Saturday's three-hour session. Keep Friday's model and settings frozen. Guide me through the fresh test, report failures honestly, and finish the backup video and presentation package within today's budget.”

| Elapsed time | Maher | Codex | Checkpoint/output |
|---|---|---|---|
| 0:00–0:15 | Set up the frozen demonstration. | Verify exact artifacts and capture procedure. | No accidental configuration drift. |
| 0:15–1:00 | Capture 50 fresh layouts across two distinct test-only sessions, resetting/rearranging between them. | Guide the prepared checklist, save metadata and outputs. | Test captures separate from development data. |
| 1:00–1:45 | Review actual boxes and colors in the annotation gallery. | Prepare annotations, run matching, report per-color and distance results and background errors. | Reviewed test report, or precisely marked unfinished coverage. |
| 1:45–2:05 | Record the final short demo and one representative limitation. | Save/play back the video locally and check files. | Usable backup, including sound if needed. |
| 2:05–2:30 | Approve wording and results. | Finish slides, PDF backup, speaker notes, and startup checklist. | Presentation package. |
| 2:30–2:50 | Practise demo transitions and difficult explanations. | Check timing and factual claims. | Rehearsal feedback. |
| 2:50–3:00 | Confirm Sunday logistics. | Save final status and Sunday checklist. | Saturday delivery complete. |

Use the prepared 50-layout checklist as the starting point: 40 positive layouts covering 20/40/60/80 cm and 10 negative layouts, including distractors. Fifty adjacent video frames are not 50 independent layouts. Keep the final test out of training and threshold selection.

**Timing risk:** capture plus annotation may take longer than 90 minutes. At 1:45, preserve presentation time. If necessary, report the fully reviewed subset with its exact size and mark the planned 50-layout evaluation incomplete. Do not rush labels or invent coverage. An optional extra hour is best spent completing this test.

**No tuning on Saturday's test.** If results motivate a later change, retain the original result; that changed candidate needs new independent evidence. If the test fails, update the presentation's claims, not the threshold to make the same test pass.

## 7. Sunday, 13 September — rehearse and present

Suggested schedule, all Berlin time. The three preparation hours exclude the presentation itself.

**Start message:** “Start Sunday's final preparation. The presentation is at 18:00 Berlin time. Use the frozen Saturday package, help me rehearse for 30 minutes, question me like my tutor, and check the live and backup demonstration. Prioritize presentation readiness.”

| Time | Activity |
|---|---|
| 14:00–14:30 | Verify startup, camera view, robot power, local video, slides/PDF, and display or screen sharing. |
| 14:30–15:00 | Give the entire 30-minute presentation aloud, including the demo. |
| 15:00–15:30 | Practise tutor questions; identify unclear answers. |
| 15:30–16:00 | Trim wording and correct slide/notes errors. Keep the technical version frozen. |
| 16:00–16:30 | Rehearse the weakest section and the switch to backup video. |
| 16:30–17:00 | Final equipment check; arrange files and rest the setup. |
| 17:00–18:00 | Buffer and break; join the meeting early enough to check audio/display. |
| 18:00 | Presentation. |

If the live demonstration fails, make one brief restart attempt (about one minute), then play the backup. If no successful live version was achieved, introduce the recorded/offline material accurately from the outset.

### Suggested 30-minute presentation

| Minutes | Content |
|---|---|
| 0–3 | Problem, robot, and intended behavior. |
| 3–7 | Pipeline diagram and what each component contributes. |
| 7–12 | Initial failure and the evidence used to investigate it. |
| 12–17 | Dataset, correction/fine-tune, and evaluation design. |
| 17–23 | Live or recorded demonstration: each color, combined scene, empty/distractor, limitation. |
| 23–27 | Results, operating conditions, and what remains unproven. |
| 27–30 | What Maher learned and the next technical step. |
| 30–45 | Questions if time allows. |

Practise: Why YOLO? Why not color alone? Why did source-image performance fail to transfer? How do you count misses? Why separate capture sessions? What does TensorRT change? What does ROS 2 publish? What evidence supports the depth filter? What did Codex help produce, and what did you personally verify and understand?

## 8. Stop rules and records

### Saturday revision: new indoor training and validation captures

Maher chose to collect new photos after cleaning the usable room area. Follow the [numbered indoor capture checklist](indoor-cube-capture-checklist.md): keep the 13 existing examples for training, propose 10 targeted new training and 9 separately arranged validation photos after the individual-image review, annotate and review both batches, then configure a disjoint training/validation run before deployment and fresh live evaluation. This supersedes today's same-image-only evaluation proposal. Capture counts and layouts are planned, not completed. Keep the guided workflow and preserve time for deployment and presentation preparation.

- Thursday: lack of useful three-color detection triggers a narrower commitment and focused diagnosis.
- Friday: freeze scope and implementation; retain recoverable versions of the new candidate.
- Saturday: preserve evaluation integrity and presentation time even if targets fail.
- Sunday: use the frozen package and fallback media.

Record progress in [sunday-progress.md](sunday-progress.md). Record the reasoning and worked examples after meaningful completed steps in [the development learning journal](development-learning-journal.md). Use exact artifact paths and separate observed results from pending work. This plan creates no scheduled automation and makes no claim that the robot has been retested today.

Background reading on separate checkouts: [official OpenAI worktree documentation](https://learn.chatgpt.com/docs/environments/git-worktrees). The single-main-task workflow above is our project recommendation.
