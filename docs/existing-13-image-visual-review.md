# Visual review of the 13 retained training photos

12 September 2026. All 13 original JPGs were opened individually with the image viewer at their native 640 × 360 resolution. These observations come from the pixels, not just filenames. No new inference, annotation approval, or training was performed.

## Limits of what the photos establish

The centimeter numbers in filenames are historical labels, not distances remeasured from the pictures. Apparent size and image position are visually observable; exact physical distance, camera calibration, and controlled lighting changes are not established by this inspection.

## Individual observations

| Photo | Visible contents | Implication for the draft checklist |
|---|---|---|
| [background__background_0001.jpg](../evaluation/results/robot_training_2026-09-09/images/train/background__background_0001.jpg) | No target cubes; wooden floor, chair wheel at left, bags/boxes at upper left and curtain at right. | Already covers the ordinary empty-floor role of T16; a repeat needs changed framing or conditions. |
| [blue_green__blue_green_0001.jpg](../evaluation/results/robot_training_2026-09-09/images/train/blue_green__blue_green_0001.jpg) | Green left of blue; both close to the picture center, separated and fully visible. | Two-color combination already covered; little horizontal position variety. |
| [dist20cm__dist20cm_0001.jpg](../evaluation/results/robot_training_2026-09-09/images/train/dist20cm__dist20cm_0001.jpg) | Three relatively large cubes lower in the picture: red, green, blue from left to right. | Already covers a near-looking, separated three-cube row. |
| [dist40cm__dist40cm_0001.jpg](../evaluation/results/robot_training_2026-09-09/images/train/dist40cm__dist40cm_0001.jpg) | Three smaller cubes in an upper-central row: red, green, blue. | Already covers another apparent-size range and a three-cube row. |
| [dist60cm__dist60cm_0001.jpg](../evaluation/results/robot_training_2026-09-09/images/train/dist60cm__dist60cm_0001.jpg) | Three small upper-central cubes: green, red, blue; curtain folds differ. | Additional apparent-size coverage and a different color order. |
| [dist80cm__dist80cm_0001.jpg](../evaluation/results/robot_training_2026-09-09/images/train/dist80cm__dist80cm_0001.jpg) | Three very small cubes near the top center: red, green, blue. | Already has far-looking/small-object examples; details are limited at this size. |
| [red_blue__red_blue_0001.jpg](../evaluation/results/robot_training_2026-09-09/images/train/red_blue__red_blue_0001.jpg) | Red left of blue, separated in the upper-central floor area. | Red/blue pair already covered. |
| [red_green__red_green_0001.jpg](../evaluation/results/robot_training_2026-09-09/images/train/red_green__red_green_0001.jpg) | Red left of green, separated in the upper-central floor area. | Red/green pair already covered. |
| [red_green_blue__red_green_blue_0001.jpg](../evaluation/results/robot_training_2026-09-09/images/train/red_green_blue__red_green_blue_0001.jpg) | Central triangle: red back-left, green back-right, blue in front; no cube hidden. | Directly covers the blue-nearest triangle concept of T14, though metric distance is unverified. |
| [single_blue__single_blue_0001.jpg](../evaluation/results/robot_training_2026-09-09/images/train/single_blue__single_blue_0001.jpg) | One blue cube near horizontal center, above the picture midpoint. | Central single-blue example exists; prioritize off-center additions over repeating this role. |
| [single_green__single_green_0001.jpg](../evaluation/results/robot_training_2026-09-09/images/train/single_green__single_green_0001.jpg) | One green cube near horizontal center, above the picture midpoint; chair wheel visible left. | Central single-green example exists. |
| [single_red__single_red_0001.jpg](../evaluation/results/robot_training_2026-09-09/images/train/single_red__single_red_0001.jpg) | One red cube near horizontal center, above the picture midpoint. | Central single-red example exists. |
| [spread_out__spread_out_0001.jpg](../evaluation/results/robot_training_2026-09-09/images/train/spread_out__spread_out_0001.jpg) | Red upper-left, green upper-right beside curtain, larger blue lower-right; wide spacing. | Already covers spread-out cubes and varied apparent depth/size. Blue still remains on the right. |

## What was already covered

The original 18-shot proposal repeated several scene categories: central single-color cubes, three-cube rows at multiple apparent sizes (T10/T11), a blue-nearest triangle (T14), spread-out/staggered cubes, and an ordinary empty floor (T16). The new prescribed poses and nominal distances are not necessarily exact duplicates, but repeating a category is lower priority than adding visibly different coverage.

## What is visibly limited

- Most cubes cluster in the upper central region. Each single-color example is near the center.
- In the rows and color pairs, blue is consistently to the right of its partners. The triangle places it near center; the spread-out image puts it far right. There is no clear blue-alone or three-color blue example in the left quarter.
- The scene repeatedly shows the same floor, bags/boxes, curtain, and chair area. There are framing/fold differences but no clearly distinct room viewpoint.
- The empty photo already includes non-cube background objects. We lack a deliberately varied foreground non-cube example and a changed-view empty scene.

These are coverage observations, not proven causes of the earlier confidence failures. RGB color changes, shadows, camera noise, and exact lighting effects have not been isolated.

## Revised proposal

Reduce new training captures from 18 to 10: six off-center singles (each color left and right), two new three-color arrangements with blue positions/depth relations underrepresented here, and two changed-view negative scenes. Keep the nine fresh validation photos: existing training photos cannot substitute for held-out examples. This would produce 23 training and nine validation images after successful annotation review. Counts are a practical budget, not a claim of optimality.

The [capture checklist](indoor-cube-capture-checklist.md) now contains the revised placement instructions. No existing photos need to be recaptured solely to match an arbitrary distance in the original draft.
