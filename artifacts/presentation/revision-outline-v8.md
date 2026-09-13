# Engineering-tutor review and revised presentation — v8

## Review conclusion

The earlier presentation needed a clearer explanation of the engineering problem, the reasons for its methods, the presenter's contribution, and the limits of the evidence. An unfamiliar viewer should understand what is being built and why before seeing performance figures.

The revised deck has 16 main slides and two optional appendix slides. Results begin on slide 12. Slide 2 has no image, as requested. No new model experiments were performed for this revision.

## Critical gaps addressed

| Gap from a tutor's perspective | Improvement |
|---|---|
| What counts as success, and what is outside scope? | Slide 2 distinguishes detection, changing scenes and physical location. Navigation/picking are outside scope; intended range is not presented as a passed test. |
| What does computer vision output? | Slide 3 distinguishes color class, image box and depth. |
| Why use these methods? | Slide 5 explains color thresholds, pretrained YOLO and supporting geometry; it makes no unmeasured benchmark ranking. |
| What did the presenter actually contribute? | Slide 6 distinguishes personal work, reused components and Codex assistance. |
| What makes the dataset credible? | Slide 7 explains label review, varied examples, arrangement-level separation and limited room/lighting coverage. |
| How do training, validation and deployment differ? | Slides 8–10 show separate workflows and desktop versus Jetson responsibilities. |
| Why is a geometry filter needed? | Slide 11 explains intended physical checking before slide 15 reports its failure. |
| How should results be interpreted? | Slides 13–17 separate visible matches, confidence, automated metrics, internal timing and unfinished full-system validation. |
| Where are the research and experiment sources? | Appendix slide 18 and speaker notes identify the sources and reproducible run. |

## Slide sequence

| Slide | Content |
|---:|---|
| 1 | Project title and conceptual cover |
| 2 | Problem, success criteria and scope |
| 3 | Computer vision fundamentals |
| 4 | Existing system architecture |
| 5 | Method choices and rationale |
| 6 | Personal contribution and reused components |
| 7 | Dataset quality, labels and scene separation |
| 8 | Training workflow and fine-tuning |
| 9 | Validation workflow and types of error |
| 10 | Desktop-to-Jetson deployment workflow |
| 11 | Purpose of the geometry filter |
| 12 | Dataset and training outcomes |
| 13 | Validation results: one missed red cube |
| 14 | Live observations and internal processing time |
| 15 | Geometry-filter limitation |
| 16 | Conclusion and remaining engineering work |
| 17 | Appendix: interpreting validation metrics |
| 18 | Appendix: research and experiment references |

## Checks and remaining limitations

All 18 rendered slides were visually inspected. The presentation package and layout validator passed. English speaker notes and 18 tutor answers accompany the deck. The validation picture is explicitly a saved validation view; the live screenshot shows one red cube, with the separately observed three-cube and empty-scene results described in text.

The architecture figure is intentionally retained at the user's request; its fine detail is best explained selectively rather than read aloud. No comparative method benchmark, broad independent test, measured camera-to-browser latency or proven geometry-filter repair is claimed. This version is ready for user review, not recorded user approval.
