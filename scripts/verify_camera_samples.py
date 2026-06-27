#!/usr/bin/env python3
"""Verify a captured RGB+depth set: SHA-256 against the sidecar JSON.

Same contract as scripts/verify_camera_samples.py but usable inline.

Usage:
  python3 verify_camera_samples.py <dir> --prefix <label>
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
    p.add_argument("dir", type=Path)
    p.add_argument("--prefix", required=True)
    args = p.parse_args()

    sidecar = args.dir / f"{args.prefix}_metadata.json"
    if not sidecar.exists():
        print(f"ERROR: sidecar not found: {sidecar}", file=sys.stderr)
        return 1

    rows = json.loads(sidecar.read_text())
    bad = 0
    for r in rows:
        for k, fname in [("rgb_sha256", r["rgb_filename"]),
                         ("depth_sha256", r["depth_filename"])]:
            fpath = args.dir / fname
            if not fpath.exists():
                print(f"MISSING {fpath}")
                bad += 1
                continue
            actual = sha256(fpath)
            if actual != r[k]:
                print(f"FAIL   {fname}: sidecar={r[k][:12]}... actual={actual[:12]}...")
                bad += 1
    total = len(rows)
    if bad:
        print(f"VERIFY FAIL: {bad} bad rows out of {total}", file=sys.stderr)
        return 1
    print(f"VERIFY OK: {total} pairs sha-256 match sidecar")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())