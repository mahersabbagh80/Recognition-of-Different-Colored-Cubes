#!/usr/bin/env python3
"""Build a read-only HTML gallery from provisional cube annotations."""

import argparse
import base64
import html
import json
from pathlib import Path


COLORS = {
    "blue_cube": "#00a8ff",
    "green_cube": "#00d26a",
    "red_cube": "#ff4d4d",
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("annotations", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[1]
    payload = json.loads(args.annotations.read_text())
    articles = []
    for item in payload["images"]:
        image_path = project_root / item["source_file"]
        encoded = base64.b64encode(image_path.read_bytes()).decode("ascii")
        overlays = []
        legend = []
        for index, obj in enumerate(item["objects"], 1):
            class_name = obj["class_name"]
            x1, y1, x2, y2 = obj["bbox_xyxy"]
            color = COLORS[class_name]
            overlays.append(
                f'<rect x="{x1}" y="{y1}" width="{x2-x1}" height="{y2-y1}" '
                f'fill="none" stroke="{color}" stroke-width="3" />'
                f'<circle cx="{x1+8}" cy="{y1+8}" r="8" fill="{color}" />'
                f'<text x="{x1+8}" y="{y1+11}" text-anchor="middle">{index}</text>'
            )
            legend.append(f"{index}: {html.escape(class_name)} [{x1}, {y1}, {x2}, {y2}]")
        summary = "; ".join(legend) if legend else "No target cubes; expected empty label file."
        articles.append(
            f'<article><h2>{html.escape(item["image_id"])} '
            f'<span>{html.escape(item["split"])}</span></h2>'
            f'<svg viewBox="0 0 {item["width"]} {item["height"]}" role="img" '
            f'aria-label="Provisional cube annotation overlay">'
            f'<image width="100%" height="100%" href="data:image/jpeg;base64,{encoded}" />'
            f'{"".join(overlays)}</svg><p>{summary}</p></article>'
        )

    document = f"""<!doctype html>
<html lang="en"><meta charset="utf-8">
<title>12 September cube annotation review</title>
<style>
body {{ font: 17px system-ui; max-width: 1120px; margin: 24px auto; padding: 16px; background: #eee; color: #222; }}
article {{ background: white; padding: 14px; margin: 18px 0; }}
h2 {{ margin: 0 0 10px; }} h2 span {{ float: right; font-size: .8em; color: #555; }}
svg {{ width: 100%; height: auto; background: #222; }}
text {{ fill: #111; font: bold 10px system-ui; }} p {{ overflow-wrap: anywhere; }}
</style>
<h1>Provisional cube annotations — 12 September 2026</h1>
<p>This page is a read-only review aid. Boxes are proposals, not approved labels.
Check that every complete cube has exactly one box, the color name is correct,
and shadows or unrelated objects are excluded. Original JPGs are unchanged.</p>
{''.join(articles)}
</html>
"""
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(document)
    print(f"wrote {args.output} with {len(articles)} images")


if __name__ == "__main__":
    main()
