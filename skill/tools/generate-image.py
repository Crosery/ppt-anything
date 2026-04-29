#!/usr/bin/env python3
"""Generate images via Google Gemini Image API, Seedream 5.0 (Ark), a generic
Gemini-shape bridge, or a generic OpenAI-image-compatible bridge.

Reads credentials from `~/.anything-ppt/providers/<provider>.toml` first (the
canonical store), falling back to `.env` in this script's directory and finally
process env. Calls the selected provider, saves the PNG locally, and previews
inline with `kitten icat` when running in a kitty terminal.

Providers:
  google (default)     -> Google Gemini Image API. Native auth via
                          X-Goog-Api-Key header. Models supported:
                          gemini-3-pro-image-preview (Pro, 1K/2K/4K),
                          gemini-2.5-flash-image (Flash, cheap),
                          gemini-3.1-flash-image-preview, etc.
                          Refs are base64-inlined.
  nanobanana           -> Same Gemini wire shape, OpenAI-compatible bearer
                          auth. Use for any third-party Gemini bridge — you
                          provide base_url + api_key + auth_style in your
                          toml. Refs are base64-inlined.
  seedream             -> Ark Doubao Seedream 5.0. Supports image-to-image;
                          local ref files auto-uploaded via the company
                          Qiniu bridge.
  xais                 -> Generic OpenAI-image-compatible endpoint. You
                          provide base_url + api_key in your toml. Keeps
                          --list-models support.

The toml field [auth].auth_style controls the auth header used:
  "google" -> X-Goog-Api-Key: <key>            (Google official native)
  "bearer" -> Authorization: Bearer <key>      (OpenAI-style; bridge default)
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
import uuid
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent

# --- Seedream / Ark -----------------------------------------------------------
ARK_ENDPOINT_DEFAULT = "https://ark.cn-beijing.volces.com/api/v3/images/generations"
ARK_ENDPOINT = ARK_ENDPOINT_DEFAULT  # overridable via toml at call time
ARK_MODEL = "doubao-seedream-5-0-260128"
# -r <ratio> maps to these pixel sizes (~2k, multiples of 16). Users who want
# 3k or exact dimensions should pass --size explicitly.
ARK_RATIO_TO_SIZE = {
    "1:1": "2048x2048",
    "16:9": "2560x1440",
    "9:16": "1440x2560",
    "3:2": "2304x1536",
    "2:3": "1536x2304",
    "4:3": "2304x1728",
    "3:4": "1728x2304",
    "21:9": "2688x1152",
    "4:5": "1792x2240",
    "5:4": "2240x1792",
}

# --- Xais (generic OpenAI-image bridge) --------------------------------------
# No hardcoded base_url — must come from ~/.anything-ppt/providers/xais.toml.
XAIS_DEFAULT_MODEL = "Nano_Banana_Pro_2K_0"

# --- Gemini-shape providers (google, nanobanana) -----------------------------
# google     = Google Gemini Image API official endpoint.
# nanobanana = same wire shape via a third-party bridge (you provide base_url).
# No hardcoded base_url — must come from the corresponding toml.
NANOBANANA_DEFAULT_MODEL = "gemini-3-pro-image-preview"
NANOBANANA_MODELS = {
    "gemini-3-pro-image-preview",       # nano-banana pro: best quality, 1K/2K/4K
    "gemini-3-pro-image-preview-stable",  # pro stable variant, 1K/2K/4K
    "gemini-2.5-flash-image",           # flash image variant, no imageSize
    "gemini-2.5-flash-image-preview",   # nano-banana: cheap, fast, no imageSize
    "gemini-3.1-flash-image-preview",   # latest flash variant
    "gpt-image-2",                      # OpenAI image model exposed via some bridges
}
# Models that accept generationConfig.imageConfig.imageSize (1K / 2K / 4K).
NANOBANANA_PRO_MODELS = {
    "gemini-3-pro-image-preview",
    "gemini-3-pro-image-preview-stable",
}
NANOBANANA_VALID_IMAGE_SIZES = {"1K", "2K", "4K"}
# Default imageSize for pro models when --size not given. 2K and 4K cost the
# same on Google's official Pro tier, so the default goes to 4K — but 4K has a
# higher transient failure rate, so we auto-fallback to 2K once on retryable
# failures.
NANOBANANA_DEFAULT_IMAGE_SIZE = "4K"
NANOBANANA_FALLBACK_IMAGE_SIZE = "2K"

VALID_RATIOS = set(ARK_RATIO_TO_SIZE.keys())
DEFAULT_RATIO = "16:9"
DEFAULT_PROVIDER = "google"

# --- Qiniu (company bridge for local-file -> remote URL) ----------------------
# These are baked-in company defaults; no user config required. Confirmed
# publicly reachable: the token endpoint is unauthenticated.
QINIU_UPLOAD_URLS = [
    "https://up-z1.qiniup.com",
    "https://up.qiniup.com",
    "https://up-z2.qiniup.com",
]
QINIU_CDN_DOMAIN = "https://qncweb.ktvsky.com"
QINIU_BASE = "https://m.ktvsky.com"
QINIU_TOKEN_API = "/c/qiniu/get_upload_token"
QINIU_CHECK_API = "/vadd/facechange/mv/qiniu/check"
QINIU_DIRECTORY = "seedream"


# --- credentials: ~/.anything-ppt/providers/*.toml -> .env -> env -------------

# Maps env var name -> provider toml stem in ~/.anything-ppt/providers/.
# Lookup order: 1) toml [auth].api_key  2) ~/.claude/skills/.../.env (legacy)
#               3) os.environ
ENV_TO_PROVIDER = {
    "GOOGLE_API_KEY":     "google",
    "NANOBANANA_API_KEY": "nanobanana",   # legacy alias for Gemini bridges
    "ARK_API_KEY":        "seedream",
    "XAIS_API_KEY":       "xais",
}

PROVIDER_LIB_DIR = Path.home() / ".anything-ppt" / "providers"


def _toml_field(provider: str, field: str) -> str:
    """Read [auth].<field> from ~/.anything-ppt/providers/<provider>.toml.
    Returns '' if file missing, tomllib unavailable, or value is placeholder."""
    cfg = PROVIDER_LIB_DIR / f"{provider}.toml"
    if not cfg.exists():
        return ""
    try:
        import tomllib  # Python 3.11+
    except ImportError:
        return ""
    try:
        with open(cfg, "rb") as f:
            data = tomllib.load(f)
    except Exception:
        return ""
    val = str(data.get("auth", {}).get(field, "")).strip()
    if not val or val.startswith("<") or val.startswith("PLACEHOLDER"):
        return ""
    return val


def _load_dotenv() -> None:
    env_path = SCRIPT_DIR / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        v = v.strip().strip('"').strip("'")
        os.environ.setdefault(k.strip(), v)


def require_key(name: str) -> str:
    # 1) ~/.anything-ppt/providers/<provider>.toml [auth].api_key (preferred)
    provider = ENV_TO_PROVIDER.get(name)
    if provider:
        val = _toml_field(provider, "api_key")
        if val:
            return val
    # 2) .env in script dir (legacy fallback)
    _load_dotenv()
    key = os.environ.get(name, "").strip()
    if key:
        return key
    sys.exit(
        f"error: {name} not configured.\n"
        f"  Preferred: edit ~/.anything-ppt/providers/{provider or '<provider>'}.toml\n"
        f"             and set [auth].api_key + [auth].base_url + [auth].docs_url.\n"
        f"  Legacy:   export {name}=... in env or add to {SCRIPT_DIR / '.env'}."
    )


def resolve_base_url(provider: str, default: str = "") -> str:
    """Provider base_url: toml is the source of truth. `default` is kept as a
    legacy fallback for callers that pass one, but new providers (google,
    nanobanana, xais) must supply base_url via toml — no brand URLs are
    hardcoded in this script.
    """
    val = _toml_field(provider, "base_url")
    if val:
        return val
    if default:
        return default
    sys.exit(
        f"error: provider {provider!r} has no base_url configured.\n"
        f"  Edit ~/.anything-ppt/providers/{provider}.toml and set "
        f"[auth].base_url to the API gateway URL."
    )


def resolve_auth_style(provider: str) -> str:
    """Provider auth_style: toml [auth].auth_style. Defaults if missing:
      - google     -> "google" (X-Goog-Api-Key)
      - everyone   -> "bearer" (Authorization: Bearer <key>; OpenAI-compatible)
    """
    val = _toml_field(provider, "auth_style")
    if val in ("google", "bearer"):
        return val
    return "google" if provider == "google" else "bearer"


def auth_headers(provider: str, key: str) -> dict[str, str]:
    """Return the auth header(s) to send for this provider."""
    style = resolve_auth_style(provider)
    if style == "google":
        return {"X-Goog-Api-Key": key}
    return {"Authorization": f"Bearer {key}"}


def _http(method: str, url: str, *, headers: dict | None = None,
          body: bytes | None = None, timeout: int = 120) -> bytes:
    req = urllib.request.Request(
        url,
        data=body,
        headers=headers or {"User-Agent": "curl/8.4.0"},
        method=method,
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read()
    except urllib.error.HTTPError as e:
        sys.exit(f"error: HTTP {e.code} from {url}: {e.read().decode('utf-8', 'replace')[:500]}")
    except urllib.error.URLError as e:
        sys.exit(f"error: network failure contacting {url}: {e.reason}")
    except TimeoutError as e:
        # Python 3.14+: socket SSL-read timeouts surface as a bare TimeoutError
        # that does NOT wrap into URLError. Handle it explicitly.
        sys.exit(f"error: timeout after {timeout}s contacting {url}: {e}")


def http_get_json(url: str, headers: dict | None = None, timeout: int = 30) -> dict:
    return json.loads(_http("GET", url, headers=headers, timeout=timeout).decode("utf-8"))


def http_post_json(url: str, body: dict, headers: dict, timeout: int = 300) -> dict:
    payload = json.dumps(body).encode("utf-8")
    merged = {**headers, "Content-Type": "application/json"}
    return json.loads(_http("POST", url, headers=merged, body=payload, timeout=timeout).decode("utf-8"))


# --- Qiniu upload -------------------------------------------------------------

def _multipart_encode(fields: dict[str, str], file_path: Path,
                      file_field: str = "file") -> tuple[bytes, str]:
    boundary = f"----claude-{uuid.uuid4().hex}"
    crlf = b"\r\n"
    chunks: list[bytes] = []
    for k, v in fields.items():
        chunks += [
            f"--{boundary}".encode(),
            f'Content-Disposition: form-data; name="{k}"'.encode(),
            b"",
            v.encode("utf-8"),
        ]
    suffix = file_path.suffix.lower() or ".png"
    ctype = "image/png" if suffix == ".png" else "application/octet-stream"
    chunks += [
        f"--{boundary}".encode(),
        f'Content-Disposition: form-data; name="{file_field}"; filename="{file_path.name}"'.encode(),
        f"Content-Type: {ctype}".encode(),
        b"",
        file_path.read_bytes(),
        f"--{boundary}--".encode(),
        b"",
    ]
    return crlf.join(chunks), f"multipart/form-data; boundary={boundary}"


def qiniu_upload(local_path: Path) -> str:
    """Upload a local file through the company Qiniu bridge; return CDN URL."""
    suffix = local_path.suffix.lower() or ".png"
    key_name = f"{QINIU_DIRECTORY}/{int(time.time() * 1000)}{suffix}"

    token_resp = http_get_json(
        f"{QINIU_BASE}{QINIU_TOKEN_API}?filename={key_name}", timeout=30,
    )
    if token_resp.get("errcode") != 200 or not token_resp.get("token"):
        sys.exit(f"error: Qiniu token fetch failed: {token_resp.get('errmsg')!r}")
    token = token_resp["token"]

    body, ctype = _multipart_encode({"key": key_name, "token": token}, local_path)
    last_err: Exception | None = None
    for url in QINIU_UPLOAD_URLS:
        try:
            raw = _http(
                "POST", url,
                headers={"Content-Type": ctype, "User-Agent": "curl/8.4.0"},
                body=body, timeout=300,
            )
            payload = json.loads(raw.decode("utf-8"))
            if not payload.get("key"):
                sys.exit(f"error: Qiniu upload response missing 'key': {payload}")
            cdn_url = f"{QINIU_CDN_DOMAIN}/{payload['key']}"
            # Best-effort post-upload integrity check (matches company flow).
            check = http_get_json(
                f"{QINIU_BASE}{QINIU_CHECK_API}?k={cdn_url}&is_record=0", timeout=30,
            )
            if check.get("errcode") != 200:
                sys.exit(f"error: Qiniu image check failed: {check.get('errmsg')!r}")
            return cdn_url
        except urllib.error.URLError as e:
            last_err = e
            continue
    sys.exit(f"error: Qiniu upload failed on all endpoints: {last_err}")


def normalize_ref(ref: str) -> str:
    """URL passes through; local path is uploaded to Qiniu."""
    if ref.startswith(("http://", "https://")):
        return ref
    path = Path(ref).expanduser()
    if not path.is_file():
        sys.exit(f"error: --ref file not found: {ref}")
    print(f"→ uploading {path.name} via Qiniu …", file=sys.stderr)
    return qiniu_upload(path)


# --- Seedream provider --------------------------------------------------------

def seedream_generate(prompt: str, ratio: str, size_override: str | None,
                      ref_urls: list[str], key: str, timeout: int,
                      ) -> tuple[str | None, bytes | None]:
    """Return (remote_url, raw_png). Exactly one is non-None."""
    size = size_override or ARK_RATIO_TO_SIZE.get(ratio, "2048x2048")
    body: dict = {
        "model": ARK_MODEL,
        "prompt": prompt,
        "size": size,
        "response_format": "b64_json",
        "output_format": "png",
        "watermark": False,
    }
    if ref_urls:
        body["image"] = ref_urls[0] if len(ref_urls) == 1 else ref_urls
    resp = http_post_json(
        ARK_ENDPOINT, body,
        headers={"Authorization": f"Bearer {key}"},
        timeout=timeout,
    )
    data = resp.get("data") or []
    if not data:
        sys.exit(f"error: Seedream returned no data: {resp}")
    item = data[0]
    if item.get("b64_json"):
        return None, base64.b64decode(item["b64_json"])
    if item.get("url"):
        return item["url"], None
    sys.exit(f"error: Seedream item has neither b64_json nor url: {item}")


# --- Gemini-shape provider (google, nanobanana, custom) ---------------------

def _ref_to_inline_data(ref: str, timeout: int = 120) -> dict:
    """Turn a URL or local path into a Gemini inlineData part (base64)."""
    if ref.startswith(("http://", "https://")):
        raw = _http("GET", ref, timeout=timeout)
        ext = ref.split("?", 1)[0].rsplit(".", 1)[-1].lower()
    else:
        path = Path(ref).expanduser()
        if not path.is_file():
            sys.exit(f"error: --ref file not found: {ref}")
        raw = path.read_bytes()
        ext = path.suffix.lstrip(".").lower()
    mime_map = {
        "png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg",
        "webp": "image/webp", "gif": "image/gif",
    }
    mime = mime_map.get(ext, "image/png")
    # Gemini Image API: max 10MB per uploaded image (docs: ai.google.dev).
    if len(raw) > 10 * 1024 * 1024:
        sys.exit(f"error: ref image {ref} exceeds 10MB cap (got {len(raw)/1024/1024:.1f}MB)")
    return {"inlineData": {"mimeType": mime, "data": base64.b64encode(raw).decode("ascii")}}


class NanobananaError(Exception):
    """Failure from nanobanana_call_once. .retryable says if size-fallback may help."""
    def __init__(self, msg: str, *, retryable: bool):
        super().__init__(msg)
        self.retryable = retryable


# finishReason values that mean "model refused the prompt" — same prompt at 2K
# will also be refused, so don't fallback (it would just bill twice for nothing).
_NANOBANANA_NON_RETRYABLE_FINISH = {
    "PROHIBITED_CONTENT", "SAFETY", "BLOCKED", "RECITATION",
}


def _gemini_call_once(provider: str, prompt: str, model: str, ratio: str,
                      image_size: str | None, parts_prefix: list[dict],
                      key: str, timeout: int) -> bytes:
    """Single POST attempt against a Gemini-shape image endpoint.

    Works for any provider whose toml supplies base_url + auth_style:
      - google     -> X-Goog-Api-Key header (official)
      - nanobanana -> Authorization: Bearer (third-party bridge default)
      - any custom name with auth_style set in its toml
    """
    parts = list(parts_prefix) + [{"text": prompt}]
    image_config: dict = {"aspectRatio": ratio}
    if image_size and model in NANOBANANA_PRO_MODELS:
        image_config["imageSize"] = image_size
    body = {
        "contents": [{"role": "user", "parts": parts}],
        "generationConfig": {
            "responseModalities": ["IMAGE"],
            "imageConfig": image_config,
        },
    }
    base = resolve_base_url(provider)
    url = f"{base}/v1beta/models/{model}:generateContent"
    payload = json.dumps(body).encode("utf-8")
    headers = {
        **auth_headers(provider, key),
        "Content-Type": "application/json",
        "User-Agent": "curl/8.4.0",
    }
    req = urllib.request.Request(url, data=payload, method="POST", headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
    except urllib.error.HTTPError as e:
        body_text = e.read().decode("utf-8", "replace")[:500]
        # Auth + safety/quota = same outcome at any size → not retryable.
        non_retryable = (
            e.code in (401, 403)
            or (e.code == 400 and any(k in body_text.lower()
                                      for k in ("safety", "policy", "blocked")))
        )
        raise NanobananaError(f"HTTP {e.code}: {body_text}",
                              retryable=not non_retryable)
    except urllib.error.URLError as e:
        raise NanobananaError(f"network: {e.reason}", retryable=True)
    except TimeoutError as e:
        raise NanobananaError(f"timeout after {timeout}s: {e}", retryable=True)

    try:
        resp_json = json.loads(raw.decode("utf-8"))
    except json.JSONDecodeError:
        raise NanobananaError(f"non-JSON response: {raw[:200]!r}", retryable=True)

    if "error" in resp_json:
        err = json.dumps(resp_json["error"], ensure_ascii=False)[:300]
        # API-level error → fallback may not help, but cheap to try once.
        raise NanobananaError(f"api error: {err}", retryable=True)

    candidates = resp_json.get("candidates") or []
    if not candidates:
        raise NanobananaError(f"no candidates: {json.dumps(resp_json)[:300]}",
                              retryable=True)

    cand0 = candidates[0]
    finish = cand0.get("finishReason", "")
    for p in cand0.get("content", {}).get("parts", []):
        if "inlineData" in p:
            return base64.b64decode(p["inlineData"]["data"])
        # Some bridges return the image as markdown text:
        # ![image](data:image/png;base64,....) or ![image](https://...)
        text = p.get("text")
        if isinstance(text, str) and text:
            m_data = re.search(
                r"!\[[^\]]*\]\(data:image/[^;]+;base64,([A-Za-z0-9+/=]+)\)",
                text,
            )
            if m_data:
                try:
                    return base64.b64decode(m_data.group(1))
                except Exception:
                    pass
            m_url = re.search(r"!\[[^\]]*\]\((https?://[^)]+)\)", text)
            if m_url:
                return _http("GET", m_url.group(1), timeout=timeout)

    # No image part. If the model refused for content reasons, don't retry.
    retryable = finish.upper() not in _NANOBANANA_NON_RETRYABLE_FINISH
    raise NanobananaError(f"no image part (finishReason={finish!r})",
                          retryable=retryable)


def gemini_generate(provider: str, prompt: str, model: str, ratio: str,
                    image_size: str | None, refs: list[str],
                    key: str, timeout: int,
                    *, allow_size_fallback: bool = True) -> tuple[bytes, str | None]:
    """Generate via a Gemini-shape provider with one-shot 4K→2K fallback.

    `provider` selects the toml whose [auth] supplies base_url + auth_style.

    Returns (image_bytes, effective_image_size). effective_image_size is the
    size that actually produced the bytes — caller can log if it differs.
    Calls sys.exit() on terminal failure.
    """
    # Resolve refs to inlineData parts ONCE — re-uploading on retry would just
    # waste time (the same bytes go up regardless of imageSize).
    parts_prefix = [_ref_to_inline_data(r, timeout=timeout) for r in refs]

    try:
        img = _gemini_call_once(provider, prompt, model, ratio, image_size,
                                parts_prefix, key, timeout)
        return img, image_size
    except NanobananaError as e:
        will_fallback = (
            allow_size_fallback
            and e.retryable
            and model in NANOBANANA_PRO_MODELS
            and image_size == "4K"
        )
        if not will_fallback:
            sys.exit(f"error: {provider} failed: {e}")
        print(f"→ warning:  4K attempt failed ({str(e)[:200]})", file=sys.stderr)
        print(f"→ retry:    falling back to {NANOBANANA_FALLBACK_IMAGE_SIZE} "
              f"(note: failed 4K call still billed)", file=sys.stderr)

    try:
        img = _gemini_call_once(provider, prompt, model, ratio,
                                NANOBANANA_FALLBACK_IMAGE_SIZE,
                                parts_prefix, key, timeout)
        return img, NANOBANANA_FALLBACK_IMAGE_SIZE
    except NanobananaError as e:
        sys.exit(f"error: {provider} {NANOBANANA_FALLBACK_IMAGE_SIZE} "
                 f"fallback also failed: {e}")


# --- Xais provider ------------------------------------------------------------

def xais_build_content(prompt: str, ratio: str, ref_url: str | None):
    text = prompt.rstrip()
    if ratio:
        text = f"{text}\n长宽比:{ratio}"
    if not ref_url:
        return text
    return [
        {"type": "text", "text": text},
        {"type": "image_url", "image_url": {"url": ref_url}},
    ]


def xais_generate(prompt: str, model: str, ratio: str, ref_url: str | None,
                  key: str, timeout: int) -> str:
    body = {
        "model": model,
        "messages": [{"role": "user", "content": xais_build_content(prompt, ratio, ref_url)}],
    }
    resp = http_post_json(
        f"{resolve_base_url("xais")}/v1/chat/completions", body,
        headers={"Authorization": f"Bearer {key}", "User-Agent": "curl/8.4.0", "Accept": "*/*"},
        timeout=timeout,
    )
    content = resp["choices"][0]["message"]["content"]
    m = re.search(r"!\[[^\]]*\]\(([^)]+)\)", content)
    if not m:
        sys.exit(f"error: no image URL in Xais response.\nRaw content: {content!r}")
    return m.group(1).replace(r"\u0026", "&")


def xais_list_models(key: str) -> None:
    # Xais /v1/models is historically slow (~10-15s); use a generous timeout.
    resp = http_get_json(
        f"{resolve_base_url("xais")}/v1/models",
        headers={"Authorization": f"Bearer {key}", "User-Agent": "curl/8.4.0", "Accept": "*/*"},
        timeout=60,
    )
    for m in resp.get("data", []):
        print(m.get("id"))


# --- shared -------------------------------------------------------------------

def download_to(url: str, path: Path, timeout: int = 120) -> None:
    path.write_bytes(_http("GET", url, timeout=timeout))


def in_kitty() -> bool:
    return "kitty" in os.environ.get("TERM", "") or bool(os.environ.get("KITTY_WINDOW_ID"))


def kitty_preview(path: Path) -> bool:
    """Render image inline with kitten icat. Silently no-op off-tty or off-kitty.

    icat emits escape sequences that require a real TTY; if stdout is piped
    (e.g. running inside Claude Code's Bash tool), skip instead of spamming.
    """
    if not in_kitty() or not sys.stdout.isatty():
        return False
    kitten = shutil.which("kitten") or shutil.which("kitty")
    if not kitten:
        return False
    cmd = [kitten, "icat", "--align", "left", str(path)] if kitten.endswith("kitten") \
        else [kitten, "+kitten", "icat", "--align", "left", str(path)]
    try:
        subprocess.run(cmd, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


# --- cli ----------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        description="Generate an image via Google Gemini (default), Seedream 5.0 (Ark), "
                    "or any third-party Gemini- / OpenAI-image-compatible bridge configured "
                    "in ~/.anything-ppt/providers/<name>.toml.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  generate.py '夕阳下的金门大桥，油画风格'                # google pro, 16:9\n"
            "  generate.py -r 9:16 --size 4K '海边灯塔, 4K'              # google pro 4K\n"
            "  generate.py -m gemini-2.5-flash-image 'cheap draft'\n"
            "  generate.py --ref /tmp/face.png '换成梵高风格'           # base64-inlined\n"
            "  generate.py --provider seedream --size 3k '4K wallpaper'\n"
            "  generate.py --provider nanobanana '...'                  # third-party Gemini bridge\n"
            "  generate.py --provider xais --list-models                # OpenAI-compat bridge\n"
        ),
    )
    ap.add_argument("prompt", nargs="?", help="prompt text (omit to read from stdin)")
    ap.add_argument("--provider", choices=["google", "nanobanana", "seedream", "xais"],
                    default=DEFAULT_PROVIDER,
                    help=f"image provider (default: {DEFAULT_PROVIDER}). "
                         f"google + nanobanana are both Gemini-shape; nanobanana is "
                         f"kept as a name for third-party Gemini bridges.")
    ap.add_argument("-m", "--model",
                    help=f"model id. Gemini-shape default: {NANOBANANA_DEFAULT_MODEL}. "
                         f"Xais default: {XAIS_DEFAULT_MODEL}. "
                         f"Seedream: ignored (single model {ARK_MODEL}).")
    ap.add_argument("-r", "--ratio", default=DEFAULT_RATIO,
                    help=f"aspect ratio (default: {DEFAULT_RATIO}); one of {sorted(VALID_RATIOS)}")
    ap.add_argument("--size",
                    help="[google/nanobanana pro] '1K' | '2K' | '4K'  ·  "
                         "[seedream] '2k' | '3k' | 'WxH' (overrides --ratio)  ·  "
                         "[xais / Gemini flash] ignored.")
    ap.add_argument("--ref", action="append",
                    help="reference image URL or local path. Repeat for multiple "
                         "(google / nanobanana / seedream support N refs; "
                         "xais uses only the first).")
    ap.add_argument("-o", "--output-dir",
                    help="output directory (default: ~/Pictures/<provider>/)")
    ap.add_argument("-n", "--name", help="output filename stem (default: timestamp)")
    ap.add_argument("--timeout", type=int, default=300,
                    help="request timeout in seconds (default: 300)")
    ap.add_argument("--no-preview", action="store_true",
                    help="skip kitty inline preview even if in kitty")
    ap.add_argument("--list-models", action="store_true",
                    help="list available models and exit (xais only; no cost)")
    return ap.parse_args()


def main() -> None:
    args = parse_args()

    if args.list_models:
        if args.provider != "xais":
            sys.exit("error: --list-models is Xais-only (Seedream exposes one fixed model).")
        xais_list_models(require_key("XAIS_API_KEY"))
        return

    prompt = args.prompt if args.prompt else sys.stdin.read().strip()
    if not prompt:
        sys.exit("error: empty prompt (pass as arg or pipe via stdin)")

    if args.ratio not in VALID_RATIOS:
        sys.exit(f"error: invalid ratio {args.ratio!r}; choose from {sorted(VALID_RATIOS)}")

    out_dir = Path(args.output_dir).expanduser() if args.output_dir \
        else Path.home() / "Pictures" / args.provider
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = args.name or f"{args.provider}_{datetime.now():%Y%m%d_%H%M%S}"
    out_path = out_dir / f"{stem.removesuffix('.png')}.png"

    # Banner
    print(f"→ provider: {args.provider}", file=sys.stderr)
    if args.provider == "seedream":
        if args.model:
            print(f"→ warning:  -m ignored on seedream (fixed model {ARK_MODEL})", file=sys.stderr)
        effective_size = args.size or ARK_RATIO_TO_SIZE[args.ratio]
        tag = "" if args.size else f" (from -r {args.ratio})"
        print(f"→ model:    {ARK_MODEL}", file=sys.stderr)
        print(f"→ size:     {effective_size}{tag}", file=sys.stderr)
    elif args.provider in ("google", "nanobanana"):
        model = args.model or NANOBANANA_DEFAULT_MODEL
        if model not in NANOBANANA_MODELS:
            print(f"→ warning:  unknown {args.provider} model {model!r}; "
                  f"known: {sorted(NANOBANANA_MODELS)} — sending anyway",
                  file=sys.stderr)
        print(f"→ model:    {model}", file=sys.stderr)
        print(f"→ ratio:    {args.ratio}", file=sys.stderr)
        if model in NANOBANANA_PRO_MODELS:
            if args.size is None:
                print(f"→ size:     {NANOBANANA_DEFAULT_IMAGE_SIZE} (default; "
                      f"auto-fallback to {NANOBANANA_FALLBACK_IMAGE_SIZE} on failure)",
                      file=sys.stderr)
            elif args.size in NANOBANANA_VALID_IMAGE_SIZES:
                tag = f" (auto-fallback to {NANOBANANA_FALLBACK_IMAGE_SIZE} on failure)" \
                    if args.size == "4K" else ""
                print(f"→ size:     {args.size}{tag}", file=sys.stderr)
            else:
                print(f"→ warning:  --size {args.size} not in "
                      f"{sorted(NANOBANANA_VALID_IMAGE_SIZES)}; sending anyway",
                      file=sys.stderr)
        elif args.size:
            print(f"→ warning:  --size {args.size} ignored "
                  f"(only pro model accepts imageSize)", file=sys.stderr)
    else:  # xais
        print(f"→ model:    {args.model or XAIS_DEFAULT_MODEL}", file=sys.stderr)
        print(f"→ ratio:    {args.ratio}", file=sys.stderr)
        if args.size:
            print("→ warning:  --size ignored on xais provider", file=sys.stderr)

    # Refs: seedream/xais want URLs (local -> Qiniu upload); Gemini-shape
    # providers (google, nanobanana) base64-inline; Qiniu URLs would just add
    # a network hop.
    ref_inputs: list[str] = args.ref or []
    ref_urls: list[str] = []
    if args.provider in ("seedream", "xais") and ref_inputs:
        for r in ref_inputs:
            u = normalize_ref(r)
            ref_urls.append(u)
            shown = u[:100] + ("…" if len(u) > 100 else "")
            print(f"→ ref:      {shown}", file=sys.stderr)
        if args.provider == "xais" and len(ref_urls) > 1:
            print("→ warning:  xais uses only the first --ref; rest ignored", file=sys.stderr)
    elif args.provider in ("google", "nanobanana") and ref_inputs:
        for r in ref_inputs:
            if r.startswith(("http://", "https://")):
                shown = r[:100] + ("…" if len(r) > 100 else "")
                print(f"→ ref:      {shown}  (download → base64)", file=sys.stderr)
            else:
                p = Path(r).expanduser()
                if not p.is_file():
                    sys.exit(f"error: --ref file not found: {r}")
                kb = p.stat().st_size // 1024
                print(f"→ ref:      {p}  ({kb}KB → base64)", file=sys.stderr)

    preview = prompt[:120] + ("…" if len(prompt) > 120 else "")
    print(f"→ prompt:   {preview}", file=sys.stderr)

    t0 = time.time()
    if args.provider == "seedream":
        key = require_key("ARK_API_KEY")
        url, raw = seedream_generate(
            prompt, args.ratio, args.size, ref_urls, key, args.timeout,
        )
        if raw is not None:
            out_path.write_bytes(raw)
        else:
            download_to(url, out_path)
    elif args.provider in ("google", "nanobanana"):
        env_var = "GOOGLE_API_KEY" if args.provider == "google" else "NANOBANANA_API_KEY"
        key = require_key(env_var)
        model = args.model or NANOBANANA_DEFAULT_MODEL
        requested_size = args.size
        if requested_size is None and model in NANOBANANA_PRO_MODELS:
            requested_size = NANOBANANA_DEFAULT_IMAGE_SIZE
        raw, effective_size = gemini_generate(
            args.provider, prompt, model, args.ratio, requested_size,
            ref_inputs, key, args.timeout,
        )
        out_path.write_bytes(raw)
        if requested_size and effective_size != requested_size:
            print(f"→ note:     served at {effective_size} "
                  f"(requested {requested_size}, fell back)", file=sys.stderr)
    else:
        key = require_key("XAIS_API_KEY")
        ref_url = ref_urls[0] if ref_urls else None
        url = xais_generate(
            prompt, args.model or XAIS_DEFAULT_MODEL, args.ratio, ref_url, key, args.timeout,
        )
        download_to(url, out_path)

    gen_t = time.time() - t0
    print(f"✓ generated in {gen_t:.1f}s, saved to {out_path}", file=sys.stderr)

    if not args.no_preview:
        kitty_preview(out_path)

    # Clean stdout for piping.
    print(out_path)


if __name__ == "__main__":
    main()
