#!/usr/bin/env python3
"""Verify captured frames: counts + SHA-256 against sidecar JSON.

Matches capture_frames.py's sidecar format (single-image, key='sha256'
and 'filename'), NOT the rgb+depth pair format that
verify_camera_samples.py expects.

Usage:
  python3 scripts/_verify_positives.py --input-dir <dir>
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--input-dir", required=True, type=Path)
    args = p.parse_args()

    if not args.input_dir.is_dir():
        print(f"ERROR: not a directory: {args.input_dir}", file=sys.stderr)
        return 1

    sidecars = sorted(args.input_dir.glob("*_metadata.json"))
    if not sidecars:
        print(f"ERROR: no sidecars in {args.input_dir}", file=sys.stderr)
        return 1

    total_frames = 0
    bad_buckets = 0

    for sidecar in sidecars:
        prefix = sidecar.name.removesuffix("_metadata.json")
        rows = json.loads(sidecar.read_text())

        disk_jpgs = sorted(args.input_dir.glob(f"{prefix}_*.jpg"))
        disk_count = len(disk_jpgs)

        sidecar_count = len(rows)
        sha_fail = 0
        missing = 0

        for row in rows:
            jpg = args.input_dir / row["filename"]
            if not jpg.exists():
                missing += 1
                continue
            actual = sha256(jpg)
            if actual != row["sha256"]:
                sha_fail += 1
                print(f"  FAIL {prefix}/{row['filename']}: sidecar={row['sha256'][:12]}.. actual={actual[:12]}..")

        status = "OK" if (missing == 0 and sha_fail == 0 and disk_count == sidecar_count) else "FAIL"
        print(f"[{status}] {prefix}: disk={disk_count}, sidecar={sidecar_count}, sha_mismatch={sha_fail}, missing={missing}")
        total_frames += sidecar_count
        if status == "FAIL":
            bad_buckets += 1

    print(f"\n=== Total: {len(sidecars)} buckets, {total_frames} frames ===")
    if bad_buckets:
        print(f"  {bad_buckets} bucket(s) FAIL — re-run rsync or check files")
        return 1
    print("  All buckets OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())