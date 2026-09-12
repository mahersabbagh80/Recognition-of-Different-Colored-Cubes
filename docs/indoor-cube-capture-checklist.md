# Indoor cube capture checklist

Prepared 12 September 2026. Planned captures, not completed work.

## Target

Keep the existing 13 approved images for training. Add **10 new training photos** and collect **9 separate validation photos**. After annotation review, that would give 23 training images and 9 validation images. This is a manageable first collection, not a statistically sufficient sample or a guarantee of detection quality.

Both sets should represent the intended demonstration: the same robot camera, room, floor, cube colors, and ordinary indoor conditions. Validation gets newly constructed scenes, not copies or adjacent frames from training scenes. A later live test remains separate.

## Prepare the room and camera

1. Use the JetRover's camera in its normal mounted position. Keep the robot stationary for each photo. Do not use phone photos for this batch.
2. Clear a floor patch large enough to place cubes roughly 40–80 cm in front of the camera. A wall, curtain, furniture leg, or part of the bed can remain in the background. The whole room need not be visually empty.
3. Use the normal lighting you expect during the demonstration. Avoid a strong reflection that hides a cube's color. Keep the camera height and tilt consistent with live operation.
4. Identify two robot positions in the room: **A**, facing one portion of the floor; **B**, shifted roughly 20–30 cm sideways and turned slightly so the background framing changes. Adjust those amounts to the available space. They are practical starting points, not calibrated requirements.
5. All left/right instructions below refer to the **camera preview**, not your position behind or beside the rover. Left/center/right mean roughly the left quarter, center, and right quarter of the picture. Keep complete cubes inside the frame.
6. Distances below are approximate horizontal floor distances from beneath the camera to the cube. If a placement is outside the view, move it until the whole cube is visible and note the actual distance. Do not change the camera mounting just to satisfy a number.
7. Save the original color image without prediction boxes or labels painted onto it. We will annotate it afterward. Wait until your hand is out of view and the image is sharp.

## Batch T — 10 targeted new training photos

Revised after [viewing all 13 existing images individually](existing-13-image-visual-review.md). The earlier 18-shot list is superseded. We already have central single cubes, three-cube rows, size variation, a blue-nearest triangle, a spread-out layout, and an empty floor. Do not recapture those just to complete a checklist.

Use position A for T01–T06 and position B for T07–T10. Left and right mean roughly the left and right quarters of the preview, not the far edges. Capture one sharp representative per row. A burst stays entirely within this training batch.

| ID | Cubes and placement | What this adds |
|---|---|---|
| T01 | Blue alone, left, about 40 cm | Blue away from its repeatedly central/right placement. |
| T02 | Blue alone, right, about 75 cm | Off-center single blue at a different apparent size. |
| T03 | Green alone, left, about 75 cm | Off-center single green. |
| T04 | Green alone, right, about 40 cm | Green at another location and size. |
| T05 | Red alone, left, about 40 cm | Off-center single red. |
| T06 | Red alone, right, about 75 cm | Red at another location and size. |
| T07 | Blue left at about 45 cm, red center at 65 cm, green right at 75 cm | Position B; blue on the left, different relative depths and background framing. Keep outlines separate. |
| T08 | Green left at about 45 cm, blue center at 75 cm, red right at 60 cm | Blue farther back between its partners. Use a second ordinary demo lighting condition if practical; keep colors visible. |
| T09 | No cubes; one ordinary non-cube object such as a shoe clearly on the floor | Position B with different framing; adds a deliberate foreground negative example. |
| T10 | No cubes; remove that foreground object | Another slightly shifted framing under the second normal lighting condition. |

If a placement falls outside the camera view, adjust until the whole cube is visible and note the approximate actual distance. New positions and appearance matter more than matching the nominal centimeter values. These additions target observed coverage gaps; improvement remains to be measured.

## Reset before validation

Stop the training capture batch and remove the cubes. Create a separate validation batch before taking another photo. Choose **position C**, a fresh camera viewpoint within the same usable floor area, different from A and B: move and turn the robot enough to change the framing. Rebuild every arrangement below rather than leaving a training scene in place.

This is a practical separation by capture setup, not proof of independence across rooms or days. We are evaluating new arrangements in this room.

## Batch V — 9 validation photos

Do not train on these photos or nearby frames from their setups. They will be labeled and used to inspect progress and select the checkpoint. They should not be deliberately much harder or easier than the training situations.

| ID | Cubes and placement | Background / detail |
|---|---|---|
| V01 | All three at about 45 cm: green left, blue center, red right | Position C; gaps between cubes. |
| V02 | All three at about 65 cm: blue left, red center, green right | Newly arrange and rotate cubes. |
| V03 | All three at about 75 cm: red left, green center, blue right | Spread across view without clipping. |
| V04 | Red left at 45 cm, blue center at 65 cm, green right at 75 cm | Stagger depths; no cube hidden. |
| V05 | Green left at 75 cm, red center at 65 cm, blue right at 45 cm | Shift camera framing slightly and rebuild the scene. |
| V06 | All three in a loose triangle around 55 cm; green nearest | Use the second normal lighting condition from training, but a fresh arrangement. |
| V07 | No cubes | Position C, normal lighting. |
| V08 | No cubes; an ordinary non-cube object in a new position | Different framing from T09. |
| V09 | No cubes | Second normal lighting condition and another framing. |

Each color appears in six validation photos. That is still a small sample: one missed cube changes that color's recall by about 17 percentage points. Report counts and examples with the percentages.

## Save, review, then train

- Keep raw captures in two clearly named batches, for example `new_training` and `new_validation`, with the row IDs in filenames or a capture note. These are proposed batch names; no directories or captures have been created by this document.
- Record the ID, actual filename, robot position, approximate distance, and lighting. Assign the split before capture, rather than moving difficult examples to training after seeing scores.
- Review blur, cube visibility, and accidental duplicates before training. Retake an unusable image within its assigned batch. Do not pick validation images because the model already detects them well.
- We will prepare and review box/color annotations for both batches. Empty photos receive empty label files after confirming there are no target cubes.
- Only after review will we import training pairs into images/train and labels/train, and validation pairs into images/val and labels/val. Then update the YAML, approval records, and preflight checks. New images will not automatically pass the current historical approval lookup.
- Later, evaluate the chosen deployed model on additional freshly arranged live scenes. If those scenes drive a model or threshold change, treat them as development evidence and reserve another untouched check for the final claim.

## First action when ready

### How to save one photo

Use the existing `scripts/capture_frames.py` on the robot, with its camera bringup running and ROS environment loaded. The robot checkout path below is documented in `docs/m3d-revived-plan.md`; verify it and the camera connection when starting the session. The robot was not contacted during preparation of these instructions.

Once the scene is ready and hands are out of view, run this in the **robot terminal**:

```bash
python3 /home/ubuntu/jetson_ws/src/Recognition-of-Different-Colored-Cubes/scripts/capture_frames.py \
  --topic /depth_cam/rgb/image_raw \
  --out-dir /home/ubuntu/cube_camera_samples/new_training \
  --max-frames 1 \
  --timeout-s 15 \
  --prefix T01_take1
```

Pressing Enter starts the subscriber. It saves the first successfully converted camera frame and exits; there is no countdown or second shutter key. Confirm the terminal reports one saved frame, then open the JPG to check it. A timeout with zero frames is not a captured photo.

The output is under `new_training/<robot-date>/T01_take1/`, containing `T01_take1_0001.jpg` and a metadata JSON file. Change the prefix for each scene. For a retake, use a new take suffix, such as `T01_take2`, because reusing the same prefix and date can overwrite the previous capture. Validation uses `--out-dir /home/ubuntu/cube_camera_samples/new_validation` and prefixes such as `V01_take1`. Images are saved on the robot first; transfer and annotation follow later.

This command is a prepared example, not an executed capture. Before the first photo, we will establish the robot terminal, verify the script and camera topic, and review the preview together.

Set up the robot at A and arrange **T01: one blue cube on the left of the preview, roughly 40 cm away, fully visible**. Check framing together before capturing the whole batch. Then proceed row by row.

This checklist applies the [methodology review](training-validation-methodology-review.md). The particular counts, distances, and layouts are project-specific proposals based on the existing 40–80 cm examples, not values prescribed by the references.
