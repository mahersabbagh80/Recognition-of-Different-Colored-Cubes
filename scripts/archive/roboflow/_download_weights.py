#!/usr/bin/env python3
"""Download pretrained YOLOv5 weights from Roboflow Universe.

Model ID: red-green-blue-cube-detection/1
Source URL: https://universe.roboflow.com/jakub-slof/red-green-blue-cube-detection
Classes: bluecube, green cube, red cube
mAP@50: 86.1%, Precision: 80.3%, Recall: 72.5%

Requires ROBOFLOW_API_KEY environment variable (free at https://app.roboflow.com/).
"""
import os
import sys
import hashlib
from pathlib import Path

from roboflow import Roboflow

MODEL_URL = "https://universe.roboflow.com/jakub-slof/red-green-blue-cube-detection"
REPO = Path(__file__).resolve().parents[3]
OUTPUT_DIR = str(REPO / "models")
OUTPUT_FILE = str(REPO / "models" / "best.pt")


def sha256_hex(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    api_key = os.environ.get("ROBOFLOW_API_KEY", "")
    if not api_key:
        print("ERROR: ROBOFLOW_API_KEY environment variable not set.", file=sys.stderr)
        print("", file=sys.stderr)
        print("To fix:", file=sys.stderr)
        print("  1. Go to https://app.roboflow.com/ and sign up (free)", file=sys.stderr)
        print("  2. Go to Settings → Roboflow API → copy your Private API Key", file=sys.stderr)
        print("  3. Run: export ROBOFLOW_API_KEY=<your-key>", file=sys.stderr)
        sys.exit(1)

    rf = Roboflow(api_key=api_key)
    project = rf.workspace().project("red-green-blue-cube-detection")
    version = project.version(1)
    model = version.model

    print(f"Project: {project.name}")
    print(f"Version: {version.version}")
    print(f"Model type: Roboflow 3.0 Object Detection (Fast)")
    print(f"Downloading weights...")

    out_path = model.download()
    if out_path is None:
        print("ERROR: download() returned None", file=sys.stderr)
        sys.exit(1)

    print(f"Downloaded to: {out_path}")

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    new_path = out_path
    if os.path.basename(out_path) != "best.pt":
        new_path = os.path.join(OUTPUT_DIR, "best.pt")
        os.rename(out_path, new_path)
        print(f"Renamed to: {new_path}")
    elif os.path.dirname(out_path) != OUTPUT_DIR:
        import shutil
        shutil.move(out_path, OUTPUT_FILE)
        new_path = OUTPUT_FILE
        print(f"Moved to: {new_path}")

    checksum = sha256_hex(new_path)
    size_mb = os.path.getsize(new_path) / (1024 * 1024)

    print(f"\n--- SUCCESS ---")
    print(f"File:   {new_path}")
    print(f"Size:   {size_mb:.1f} MB")
    print(f"SHA256: {checksum}")
    print(f"Source: {MODEL_URL}")
    print(f"Classes: bluecube, green cube, red cube")


if __name__ == "__main__":
    main()
