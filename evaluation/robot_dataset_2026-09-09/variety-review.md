# Image variety review — 9 September 2026

Inspected contact sheets containing all 98 source JPGs. This is a scene-variety inspection, not precise box adjudication of the remaining 85 images. The original 13 human confirmations remain unchanged.

## Observations

- 13 named capture groups: background (12), blue/green (4), 20 cm (12), 40 cm (12), 60 cm (12), 80 cm (12), red/blue (4), red/green (4), three colors (4), single blue (3), single green (3), single red (12), spread out (4).
- Useful changes in cube size, position, color combination, and spacing. Distance names are capture labels, not independently measured distances.
- Within each group, most frames show essentially the same arrangement with small appearance variations. These are repeated observations, not 98 substantially different scenes.
- Background and lighting are broadly shared across groups. Some camera/background composition changes are visible, especially among farther-distance and spread-out views.
- No conclusion about training sufficiency is possible before training and evaluation. The collection is useful for an initial model.

## Split recommendation

One continuous session does not automatically make a dataset unusable or forbid a development split. Whole visibly distinct arrangement groups could be held out for a limited same-session development check, after checking cross-group similarity and class coverage. Do not randomly scatter neighboring frames across training and validation, and do not claim such a same-session check establishes independent robot reliability.

For this small collection, holding out entire arrangements also removes much of that condition from training and leaves few distinct validation examples. A fresh, rearranged validation capture is therefore recommended on the observed evidence, not solely because all images share a session ID. This recommendation does not discard the existing images or block starting annotation/training preparation. The final test remains separate from all model-selection data.

## Evidence

Contact sheets: `evaluation/results/wednesday-variety/sheet-1.jpg` through `sheet-4.jpg`. No images deleted, split assigned, new boxes approved, or model trained during this inspection.
