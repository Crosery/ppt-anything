#!/usr/bin/env python3
"""
build-html-ppt-external.py — Build a lightweight HTML slideshow with EXTERNAL
WebP image references.

Unlike build-html-ppt.py (which base64-embeds every image into a single HTML,
ballooning a 5-slide deck to 70+ MB), this script:

  1. Runs cwebp to compress each source PNG into a sibling .webp (visually
     lossless q=95 by default; --lossless for bit-perfect at ~30% savings).
  2. Writes <dir>/index.html that references the .webp files via relative
     paths. Base HTML is ~3 KB.
  3. Removes the source PNGs by default so the folder stays minimal (use
     --keep-png to preserve them).

Result: a 2-slide deck goes from ~30 MB base64 HTML → ~5 MB folder that opens
instantly. Use this for any deck you'll browse locally, drop into GH Pages,
or serve from a static host.

Requires cwebp (libwebp). On macOS: `brew install webp`.

Controls inside the slideshow:
  →  Space  PageDown  Right-edge click      next slide
  ←  PageUp  Left-edge click                previous slide
  Home / End                                first / last slide
  F                                         toggle fullscreen

Usage:
  build-html-ppt-external.py --dir <dir> --pattern '*_s*.png'
  build-html-ppt-external.py --dir <dir> --pattern '*_s*.png' --lossless
  build-html-ppt-external.py --dir <dir> --pattern '*_s*.png' --keep-png
  build-html-ppt-external.py --dir <dir> -t 'My deck' -o custom.html

When --dir is used with a glob pattern, files are sorted lexicographically.
Pad numeric suffixes (s01, s02, ... s10) if you have more than 9 slides —
otherwise s10 sorts before s2.
"""
from __future__ import annotations

import argparse
import html
import json
import shutil
import subprocess
import sys
from pathlib import Path


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  html, body {{
    width: 100%; height: 100%;
    background: #1a1a1a;
    font-family: -apple-system, "PingFang SC", "Helvetica Neue", sans-serif;
    overflow: hidden;
    color: #eee;
  }}
  #stage {{ position: fixed; inset: 0; display: flex; align-items: center; justify-content: center; }}
  .slide {{
    position: absolute;
    max-width: 100vw; max-height: 100vh;
    opacity: 0;
    transition: opacity 240ms ease;
    pointer-events: none;
  }}
  .slide.active {{ opacity: 1; pointer-events: auto; }}
  .slide img {{
    display: block;
    max-width: 100vw; max-height: 100vh;
    width: auto; height: auto;
    object-fit: contain;
    user-select: none;
    -webkit-user-drag: none;
  }}
  .hud {{
    position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%);
    font-size: 13px; color: rgba(255,255,255,0.55);
    letter-spacing: 0.12em; font-variant-numeric: tabular-nums;
    pointer-events: none; user-select: none;
  }}
  .hud .sep {{ margin: 0 8px; opacity: 0.45; }}
  .hint {{
    position: fixed; top: 20px; right: 24px;
    font-size: 12px; color: rgba(255,255,255,0.35);
    letter-spacing: 0.08em; pointer-events: none;
  }}
  .nav-edge {{ position: fixed; top: 0; bottom: 0; width: 18vw; cursor: pointer; z-index: 10; }}
  .nav-edge.left {{ left: 0; }}
  .nav-edge.right {{ right: 0; }}
</style>
</head>
<body>
  <div id="stage"></div>
  <div class="nav-edge left"  id="nav-prev"></div>
  <div class="nav-edge right" id="nav-next"></div>
  <div class="hint">←  →    翻页    ·    F    全屏</div>
  <div class="hud"><span id="cur">01</span><span class="sep">/</span><span id="total">01</span></div>
<script>
  const slides = {slides_json};
  const total  = slides.length;
  const stage  = document.getElementById('stage');
  const curEl  = document.getElementById('cur');
  document.getElementById('total').textContent = String(total).padStart(2, '0');

  slides.forEach((src, i) => {{
    const div = document.createElement('div');
    div.className = 'slide' + (i === 0 ? ' active' : '');
    const img = document.createElement('img');
    img.src = src;
    img.alt = 'slide ' + (i + 1);
    div.appendChild(img);
    stage.appendChild(div);
  }});
  const slideEls = document.querySelectorAll('.slide');
  let idx = 0;

  function go(to) {{
    if (to < 0) to = 0;
    if (to >= total) to = total - 1;
    if (to === idx) return;
    slideEls[idx].classList.remove('active');
    slideEls[to].classList.add('active');
    idx = to;
    curEl.textContent = String(idx + 1).padStart(2, '0');
  }}

  document.addEventListener('keydown', (e) => {{
    if (e.metaKey || e.ctrlKey || e.altKey) return;
    switch (e.key) {{
      case 'ArrowRight': case ' ': case 'PageDown':
        go(idx + 1); e.preventDefault(); break;
      case 'ArrowLeft': case 'PageUp':
        go(idx - 1); e.preventDefault(); break;
      case 'Home': go(0); e.preventDefault(); break;
      case 'End':  go(total - 1); e.preventDefault(); break;
      case 'f': case 'F':
        if (!document.fullscreenElement) document.documentElement.requestFullscreen().catch(() => {{}});
        else document.exitFullscreen();
        e.preventDefault(); break;
    }}
  }});
  document.getElementById('nav-prev').addEventListener('click', () => go(idx - 1));
  document.getElementById('nav-next').addEventListener('click', () => go(idx + 1));
</script>
</body>
</html>
"""


def check_cwebp() -> None:
    if shutil.which("cwebp") is None:
        print(
            "error: cwebp not found. Install with `brew install webp` "
            "(macOS) or `apt install webp` (debian/ubuntu).",
            file=sys.stderr,
        )
        sys.exit(2)


def compress_one(png: Path, quality: int, lossless: bool) -> Path:
    webp = png.with_suffix(".webp")
    cmd = ["cwebp", "-m", "6", "-mt"]
    if lossless:
        cmd += ["-lossless", "-z", "9"]
    else:
        cmd += ["-q", str(quality)]
    cmd += [str(png), "-o", str(webp)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"cwebp failed on {png.name}:\n{result.stderr}", file=sys.stderr)
        sys.exit(1)
    return webp


def main() -> None:
    p = argparse.ArgumentParser(
        description="Build a lightweight HTML slideshow with external WebP image references.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument("--dir", required=True, help="folder containing source images")
    p.add_argument("--pattern", default="*.png", help="glob pattern inside --dir (default: *.png)")
    p.add_argument("-o", "--output", default=None,
                   help="output HTML path (default: <dir>/index.html)")
    p.add_argument("-t", "--title", default="Slideshow", help="HTML <title>")
    p.add_argument("--lossless", action="store_true",
                   help="use lossless WebP (bit-perfect; ~30%% smaller than PNG for illustrations)")
    p.add_argument("--quality", type=int, default=95,
                   help="lossy WebP quality 0-100 (default: 95, visually lossless for watercolor illustrations)")
    p.add_argument("--keep-png", action="store_true",
                   help="keep source PNGs (default: delete after successful compression)")
    args = p.parse_args()

    check_cwebp()

    deck_dir = Path(args.dir).expanduser().resolve()
    if not deck_dir.is_dir():
        print(f"not a directory: {deck_dir}", file=sys.stderr)
        sys.exit(1)
    pngs = sorted(deck_dir.glob(args.pattern))
    if not pngs:
        print(f"no images matched {args.pattern!r} in {deck_dir}", file=sys.stderr)
        sys.exit(1)

    output = Path(args.output).expanduser().resolve() if args.output else deck_dir / "index.html"
    mode = "lossless" if args.lossless else f"q={args.quality}"
    print(f"compressing {len(pngs)} slide(s) → WebP ({mode})")

    total_before = 0
    total_after = 0
    webps: list[Path] = []
    for i, png in enumerate(pngs, 1):
        before = png.stat().st_size
        webp = compress_one(png, args.quality, args.lossless)
        after = webp.stat().st_size
        pct = 100.0 * (1.0 - after / before) if before else 0.0
        print(f"  {i:>2}. {png.name} → {webp.name}  "
              f"{before / 1e6:>6.2f} MB → {after / 1e6:>6.2f} MB  ({pct:>4.0f}% smaller)")
        webps.append(webp)
        total_before += before
        total_after += after
        if not args.keep_png:
            png.unlink()

    # HTML references use relative filenames (same directory as the html file).
    slides_rel = [w.name for w in webps]
    doc = HTML_TEMPLATE.format(
        title=html.escape(args.title),
        slides_json=json.dumps(slides_rel),
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(doc, encoding="utf-8")

    html_size_kb = output.stat().st_size / 1024
    total_deliverable = total_after + output.stat().st_size
    total_pct = 100.0 * (1.0 - total_deliverable / total_before) if total_before else 0.0

    print()
    print(f"built: {output}")
    print(f"  html size:          {html_size_kb:>6.1f} KB")
    print(f"  png total (before): {total_before / 1e6:>6.2f} MB")
    print(f"  webp total (after): {total_after / 1e6:>6.2f} MB")
    print(f"  deliverable total:  {total_deliverable / 1e6:>6.2f} MB  ({total_pct:.0f}% smaller than source PNGs)")
    if not args.keep_png:
        print(f"  removed {len(pngs)} source PNG(s)")
    print()
    print("slides in order:")
    for i, w in enumerate(webps, 1):
        print(f"  {i:>2}. {w.name}")


if __name__ == "__main__":
    main()
