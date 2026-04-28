#!/usr/bin/env python3
"""
build-html-ppt.py — Build a self-contained HTML slideshow from a set of images.

Output is a single .html file: no server, no external assets (images embedded as
base64). Opens as plain file:// in any browser.

Controls inside the slideshow:
  →  Space  PageDown  Click          next slide
  ←  PageUp  Right-click             previous slide
  Home                               first slide
  End                                last slide
  F   Double-click                   toggle fullscreen
  Esc                                exit fullscreen

Usage:
  build-html-ppt.py img1.png img2.png ...            -o deck.html
  build-html-ppt.py --dir <dir>                      -o deck.html
  build-html-ppt.py --dir <dir> --pattern '*_s*.png' -o deck.html
  build-html-ppt.py --dir <dir> -t 'My deck'         -o deck.html

When --dir is used, files are sorted lexicographically. Pad numeric suffixes
(s01, s02, ... s10) if you have more than 9 slides — otherwise s10 sorts
before s2.
"""
from __future__ import annotations

import argparse
import base64
import html
import json
import mimetypes
import sys
from pathlib import Path


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  html, body {{
    width: 100vw;
    height: 100vh;
    background: #000;
    overflow: hidden;
  }}
  #stage {{
    width: 100vw;
    height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    user-select: none;
    -webkit-user-select: none;
  }}
  #slide {{
    max-width: 100vw;
    max-height: 100vh;
    width: auto;
    height: auto;
    object-fit: contain;
    display: block;
    -webkit-user-drag: none;
    user-drag: none;
  }}
</style>
</head>
<body>
  <div id="stage"><img id="slide" alt=""></div>
<script>
  const slides = {slides_json};
  const total = slides.length;
  let idx = 0;
  const img = document.getElementById('slide');
  const stage = document.getElementById('stage');

  // Preload all slides so navigation is instant.
  const preloaded = slides.map((src) => {{ const i = new Image(); i.src = src; return i; }});

  function render() {{ img.src = slides[idx]; }}
  function next() {{ if (idx < total - 1) {{ idx++; render(); }} }}
  function prev() {{ if (idx > 0) {{ idx--; render(); }} }}

  function toggleFullscreen() {{
    if (!document.fullscreenElement) {{
      document.documentElement.requestFullscreen().catch(() => {{}});
    }} else {{
      document.exitFullscreen();
    }}
  }}

  document.addEventListener('keydown', (e) => {{
    if (e.metaKey || e.ctrlKey || e.altKey) return;
    switch (e.key) {{
      case 'ArrowRight':
      case ' ':
      case 'PageDown':
        next(); e.preventDefault(); break;
      case 'ArrowLeft':
      case 'PageUp':
        prev(); e.preventDefault(); break;
      case 'Home':
        idx = 0; render(); e.preventDefault(); break;
      case 'End':
        idx = total - 1; render(); e.preventDefault(); break;
      case 'f':
      case 'F':
        toggleFullscreen(); e.preventDefault(); break;
    }}
  }});

  stage.addEventListener('click', next);
  stage.addEventListener('contextmenu', (e) => {{ prev(); e.preventDefault(); }});
  stage.addEventListener('dblclick', (e) => {{ toggleFullscreen(); e.preventDefault(); }});

  render();
</script>
</body>
</html>
"""


def encode_image(path: Path) -> str:
    mime, _ = mimetypes.guess_type(str(path))
    if mime is None:
        mime = "image/png"
    data = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{data}"


def collect(args: argparse.Namespace) -> list[Path]:
    if args.dir:
        paths = sorted(Path(args.dir).expanduser().glob(args.pattern))
    else:
        paths = [Path(p).expanduser() for p in args.images]
    missing = [p for p in paths if not p.is_file()]
    if missing:
        for p in missing:
            print(f"missing: {p}", file=sys.stderr)
        sys.exit(1)
    if not paths:
        print("no images found", file=sys.stderr)
        sys.exit(1)
    return paths


def main() -> None:
    p = argparse.ArgumentParser(
        description="Build a self-contained HTML slideshow from images.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument("images", nargs="*", help="image files in slide order")
    p.add_argument("--dir", help="directory to read images from (sorted by name)")
    p.add_argument("--pattern", default="*.png", help="glob pattern when using --dir (default: *.png)")
    p.add_argument("-o", "--output", required=True, help="output HTML path")
    p.add_argument("-t", "--title", default="Slideshow", help="HTML <title>")
    args = p.parse_args()

    paths = collect(args)
    slides = [encode_image(pth) for pth in paths]
    doc = HTML_TEMPLATE.format(
        title=html.escape(args.title),
        slides_json=json.dumps(slides),
    )
    out = Path(args.output).expanduser()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(doc, encoding="utf-8")
    size_mb = out.stat().st_size / (1024 * 1024)
    print(f"built: {out.resolve()}  ({len(paths)} slides, {size_mb:.1f} MB)")
    print("slides in order:")
    for i, pth in enumerate(paths, 1):
        print(f"  {i:>2}. {pth}")


if __name__ == "__main__":
    main()
