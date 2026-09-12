# First-frame selection — 12 September 2026

Corrected scope: apply the first-frame rule only to images currently in images/train. The four images in images/val are pending a separate selection decision. Earlier interpretation applying this to all setups was too broad. Exclude the later selected frame; preserve all source images, labels, and historical results. This supersedes the proposed all-26 selection.

This is a representative-frame selection rule, not a claim that all pairs are byte-identical. The blue/green pair was visually inspected this session; other pairs were not individually rechecked during this decision.

| Setup | Keep | Exclude from next run |
|---|---|---|
| background | images/train/background__background_0001.jpg | images/train/background__background_0012.jpg |
| blue_green | images/train/blue_green__blue_green_0001.jpg | images/train/blue_green__blue_green_0004.jpg |
| dist20cm | images/train/dist20cm__dist20cm_0001.jpg | images/train/dist20cm__dist20cm_0012.jpg |
| dist40cm (pending; not approved by this decision) | images/val/dist40cm__dist40cm_0001.jpg | images/val/dist40cm__dist40cm_0012.jpg |
| dist60cm | images/train/dist60cm__dist60cm_0001.jpg | images/train/dist60cm__dist60cm_0012.jpg |
| dist80cm | images/train/dist80cm__dist80cm_0001.jpg | images/train/dist80cm__dist80cm_0012.jpg |
| red_blue | images/train/red_blue__red_blue_0001.jpg | images/train/red_blue__red_blue_0004.jpg |
| red_green | images/train/red_green__red_green_0001.jpg | images/train/red_green__red_green_0004.jpg |
| red_green_blue | images/train/red_green_blue__red_green_blue_0001.jpg | images/train/red_green_blue__red_green_blue_0004.jpg |
| single_blue | images/train/single_blue__single_blue_0001.jpg | images/train/single_blue__single_blue_0003.jpg |
| single_green | images/train/single_green__single_green_0001.jpg | images/train/single_green__single_green_0003.jpg |
| single_red | images/train/single_red__single_red_0001.jpg | images/train/single_red__single_red_0012.jpg |
| spread_out (pending; not approved by this decision) | images/val/spread_out__spread_out_0001.jpg | images/val/spread_out__spread_out_0004.jpg |

Confirmed selection from images/train: 11 first-frame images, 21 annotated cubes, and one empty background image. Exclude its 11 later frames. The four validation-folder images remain unchanged and their selection is pending; their table rows above are not approved exclusions.

Reason for exclusions: retain one representative per capture setup, avoiding repeated near-identical examples. No new training configuration or training run was executed by this recording step.
