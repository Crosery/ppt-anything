#!/usr/bin/env python3
"""Batch-generate multiple images in true parallel.

Reads a JSON manifest (list of slide specs), launches all generate-image.py
processes simultaneously, waits for all to finish, retries failures up to
--retries times, and reports results.

Wall-clock time ~= time of one image (plus retry overhead if any fail).

Input manifest format (JSON array, one object per slide):
[
  {
    "name": "slide_01",
    "prompt": "chibi character holding a scroll ...",
    "ref": ["/path/to/char.png", "/path/to/prev.png"],
    "ratio": "16:9",
    "size": "3840x2160"
  },
  ...
]

Fields: name (required), prompt (required), ref (optional list),
ratio (optional, default 16:9), size (optional), model (optional),
provider (optional).

Usage:
  batch-generate.py manifest.json -o ./slides/
  batch-generate.py manifest.json -o ./slides/ --retries 2
  echo '[{"name":"s1","prompt":"apple"}]' | batch-generate.py - -o /tmp/out
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
GENERATE = SCRIPT_DIR / "generate-image.py"


def build_cmd(spec: dict, out_dir: Path, extra_args: list[str]) -> list[str]:
    cmd = [sys.executable, str(GENERATE)]
    if spec.get("provider"):
        cmd += ["--provider", spec["provider"]]
    if spec.get("model"):
        cmd += ["-m", spec["model"]]
    if spec.get("ratio"):
        cmd += ["-r", spec["ratio"]]
    if spec.get("size"):
        cmd += ["--size", spec["size"]]
    for r in spec.get("ref", []):
        cmd += ["--ref", r]
    cmd += ["-o", str(out_dir)]
    cmd += ["-n", spec["name"]]
    cmd += ["--no-preview"]
    cmd += extra_args
    cmd += [spec["prompt"]]
    return cmd


def run_one(spec: dict, out_dir: Path, extra_args: list[str],
            timeout: int) -> tuple[str, bool, str]:
    """Run generate-image.py for one slide. Returns (name, success, message)."""
    name = spec["name"]
    cmd = build_cmd(spec, out_dir, extra_args)
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout)
        if result.returncode == 0:
            out_file = result.stdout.strip().split("\n")[-1]
            return name, True, out_file
        last = "\n".join(result.stderr.strip().splitlines()[-5:])
        return name, False, f"exit {result.returncode}: {last}"
    except subprocess.TimeoutExpired:
        return name, False, f"timeout after {timeout}s"
    except Exception as e:
        return name, False, str(e)


def main() -> None:
    ap = argparse.ArgumentParser(description="Batch-generate images in parallel")
    ap.add_argument("manifest", help="JSON manifest file (or - for stdin)")
    ap.add_argument("-o", "--output-dir", required=True, help="output directory")
    ap.add_argument("--retries", type=int, default=2,
                    help="max retries per failed slide (default: 2)")
    ap.add_argument("--timeout", type=int, default=300,
                    help="per-image timeout in seconds (default: 300)")
    ap.add_argument("--workers", type=int, default=0,
                    help="max parallel workers (default: slide count, i.e. all at once)")
    args, extra = ap.parse_known_args()

    if args.manifest == "-":
        specs = json.load(sys.stdin)
    else:
        with open(args.manifest) as f:
            specs = json.load(f)

    if not isinstance(specs, list) or not specs:
        sys.exit("error: manifest must be a non-empty JSON array")

    for i, s in enumerate(specs):
        if "name" not in s or "prompt" not in s:
            sys.exit(f"error: manifest[{i}] missing 'name' or 'prompt'")

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    workers = args.workers or len(specs)

    print(f"batch: {len(specs)} slides, {workers} workers, "
          f"retries={args.retries}, timeout={args.timeout}s", file=sys.stderr)

    t0 = time.time()
    results: dict[str, tuple[bool, str]] = {}

    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {
            pool.submit(run_one, s, out_dir, extra, args.timeout): s["name"]
            for s in specs
        }
        for fut in as_completed(futures):
            name, ok, msg = fut.result()
            results[name] = (ok, msg)
            tag = "ok" if ok else "FAIL"
            print(f"  [{tag}] {name}: {msg}", file=sys.stderr)

    failed = {name: msg for name, (ok, msg) in results.items() if not ok}
    retry_round = 0
    while failed and retry_round < args.retries:
        retry_round += 1
        retry_specs = [s for s in specs if s["name"] in failed]
        print(f"retry {retry_round}/{args.retries}: {len(retry_specs)} slides",
              file=sys.stderr)
        with ThreadPoolExecutor(max_workers=min(workers, len(retry_specs))) as pool:
            futures = {
                pool.submit(run_one, s, out_dir, extra, args.timeout): s["name"]
                for s in retry_specs
            }
            for fut in as_completed(futures):
                name, ok, msg = fut.result()
                results[name] = (ok, msg)
                tag = "ok" if ok else "FAIL"
                print(f"  [{tag}] {name}: {msg}", file=sys.stderr)
                if ok:
                    del failed[name]

    elapsed = time.time() - t0
    succeeded = sum(1 for ok, _ in results.values() if ok)
    print(f"\nbatch done: {succeeded}/{len(specs)} succeeded, "
          f"{len(specs)-succeeded} failed, {elapsed:.1f}s total", file=sys.stderr)

    summary = []
    for s in specs:
        ok, msg = results[s["name"]]
        summary.append({"name": s["name"], "ok": ok, "output": msg})
    json.dump(summary, sys.stdout, ensure_ascii=False, indent=2)
    print()

    if len(specs) - succeeded > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
