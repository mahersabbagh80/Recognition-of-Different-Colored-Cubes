# Documentation completion check — 13 September 2026

## Scope and result

The documentation for work completed through the September live test and presentation v8 is current. This does not mark the full robot project complete.

Updated entry points include README, documentation index, project definition, milestones, architecture, technical stack, model inventory, training/validation workflow, evaluation summary, capture outcome, script index, logbook and journal index. The older definition/architecture/stack/concept pages are preserved as explicitly historical snapshots.

## Corrections

- Actual class mapping: 0 blue, 1 green, 2 red.
- Actual training: 23 images, 8 held-out validation images, 60 epochs, selected epoch 45.
- New model is a dated candidate engine; it did not replace the old default.
- Filter-disabled detections work in the observed scenes; enabled geometry filtering rejects genuine cubes.
- Zsh commands use setup.zsh. Runtime settings are cached; restart for parameter changes.
- The full-range evaluation script is a placeholder, not an implemented evaluator.
- Presentation v8 is the current package; rehearsal was removed from scope.

## Verification

Current entry-point and presentation Markdown links were checked for existing local targets. No missing targets were found. Source checks covered the node's class mapping, startup parameters, launch boundary, package dependencies, and evaluation stub. No training, robot execution or new evaluation was performed. Git whitespace checks passed.

## Version-control scope

The v8 PPTX/PDF, supporting Markdown, saved red-cube screenshot and documentation belong to the saved change. Earlier slide binaries and authoring cache remain local and ignored. Model binaries, raw runs and datasets remain local as already intended; linked local run evidence is not bundled into a fresh clone.

## Remaining engineering work

Geometry-filter diagnosis/repair, independent test scenes, full-range reliability, physical-location verification and end-to-end timing remain open. Desktop rqt discovery is also unresolved; browser preview was the working route. Those require future evidence, not invented completion entries.
