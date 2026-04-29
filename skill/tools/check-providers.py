#!/usr/bin/env python3
"""check-providers.py — readiness probe for ~/.ppt-anything/providers/*.toml.

Designed for the agent to call at skill startup BEFORE asking the user any
briefing questions. Tells the agent which providers are configured (have all
required auth fields filled) WITHOUT revealing api_key contents to the agent.

Output (to stdout):
  READY: name1 (verified|filled-but-unverified), name2 (...) ...
  INCOMPLETE: name3 (missing: api_key,base_url), ...    [if any are partial]

Or, if zero providers are ready:
  NEED-CONFIG: ...explanation...

Exit codes:
  0  at least one provider is ready (api_key + base_url filled)
  1  no provider is ready — agent must trigger first-run setup wizard

The script reads toml internals — that's fine, it's a tool. The agent never
sees the file body, only this script's structured stdout.
"""

from __future__ import annotations

import sys
import tomllib
from pathlib import Path

PROVIDER_DIR = Path.home() / ".ppt-anything" / "providers"

PLACEHOLDER_PREFIXES = ("<", "PLACEHOLDER")


def is_filled(v: str) -> bool:
    v = v.strip()
    if not v:
        return False
    return not any(v.startswith(p) for p in PLACEHOLDER_PREFIXES)


def probe_one(toml_path: Path) -> tuple[bool, str]:
    """Return (is_ready, status_phrase). status_phrase NEVER contains the key."""
    try:
        with open(toml_path, "rb") as f:
            data = tomllib.load(f)
    except Exception as e:
        return False, f"{toml_path.stem} (parse error: {type(e).__name__})"

    auth = data.get("auth", {})
    api_key = str(auth.get("api_key", ""))
    base_url = str(auth.get("base_url", ""))

    missing = []
    if not is_filled(api_key):
        missing.append("api_key")
    if not is_filled(base_url):
        missing.append("base_url")
    if missing:
        return False, f"{toml_path.stem} (missing: {','.join(missing)})"

    verified = bool(data.get("provider", {}).get("verified", False))
    tag = "verified" if verified else "filled-but-unverified"
    return True, f"{toml_path.stem} ({tag})"


def main() -> None:
    if not PROVIDER_DIR.exists():
        print(f"NEED-CONFIG: provider directory {PROVIDER_DIR} does not exist; "
              f"run scripts/install.sh first")
        sys.exit(1)

    tomls = sorted(PROVIDER_DIR.glob("*.toml"))
    if not tomls:
        print(f"NEED-CONFIG: no *.toml files in {PROVIDER_DIR}")
        sys.exit(1)

    ready: list[str] = []
    incomplete: list[str] = []
    for p in tomls:
        ok, phrase = probe_one(p)
        (ready if ok else incomplete).append(phrase)

    if ready:
        print(f"READY: {', '.join(ready)}")
        if incomplete:
            print(f"INCOMPLETE: {', '.join(incomplete)}")
        sys.exit(0)

    print(f"NEED-CONFIG: {', '.join(incomplete) if incomplete else 'no provider toml files'}")
    print(f"  Recommended next step (agent → user):")
    print(f"  - Path 1 (推荐, 安全): 用户自己 vim ~/.ppt-anything/providers/google.toml 填 [auth].api_key")
    print(f"  - Path 2 (有风险): 用户给 base_url+key+auth_style, agent 调 tools/register-provider.py")
    sys.exit(1)


if __name__ == "__main__":
    main()
