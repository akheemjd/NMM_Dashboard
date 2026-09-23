#!/usr/bin/env python3
"""Ghost Admin API client for Northern Mile Media.

Publishes NMM blog posts to Ghost via the Admin REST API.

AUTH (critical — learned the hard way):
  Ghost Admin API does NOT accept the raw id:secret key directly.
  You must sign a JWT with the secret (HS256), embedding the key id as `kid`,
  and set `aud` to "/admin/". Then send it as `Authorization: Ghost <jwt>`.
  The "Authorization: Bearer <token>" format is REJECTED (401).
  The X-Ghost-Version header is NOT needed and causes 400 on some instances.

Environment variables:
  NMM_GHOST_SITE_URL       e.g. https://northern-mile-media.ghost.io
  NMM_GHOST_ADMIN_API_KEY  The id:secret pair from Ghost Integrations
"""

import base64
import hashlib
import hmac
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


# ── Configuration ──────────────────────────────────────────────

GHOST_SITE = os.environ.get("NMM_GHOST_SITE_URL", "").rstrip("/")
GHOST_ADMIN_KEY = os.environ.get("NMM_GHOST_ADMIN_API_KEY", "")

# Ghost Admin API accepts only these values for ?formats=
# ("text" is NOT valid and returns 422)
VALID_FORMATS = {"html", "plaintext", "mobiledoc", "lexical"}


def _load_dotenv():
    """Load .env from repo root if present (so cron doesn't need exports)."""
    global GHOST_SITE, GHOST_ADMIN_KEY
    env_path = Path(__file__).resolve().parent.parent / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        k, v = k.strip(), v.strip()
        if k == "NMM_GHOST_SITE_URL" and not GHOST_SITE:
            GHOST_SITE = v.rstrip("/")
        elif k == "NMM_GHOST_ADMIN_API_KEY" and not GHOST_ADMIN_KEY:
            GHOST_ADMIN_KEY = v


# ── JWT signing ────────────────────────────────────────────────

def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def make_jwt(ttl_seconds=300):
    """Sign a Ghost Admin API JWT.

    Ghost requires this exact shape:
      header  = {"alg":"HS256","typ":"JWT","kid":"<key-id>"}
      payload = {"iat":<now>,"exp":<now+ttl>,"aud":"/admin/"}
      sig     = HMAC-SHA256(secret_bytes, header_b64 + "." + payload_b64)
    """
    if not GHOST_ADMIN_KEY or ":" not in GHOST_ADMIN_KEY:
        raise EnvironmentError(
            "NMM_GHOST_ADMIN_API_KEY must be in 'id:secret' format"
        )
    kid, secret = GHOST_ADMIN_KEY.split(":", 1)

    now = int(time.time())
    header = {"alg": "HS256", "typ": "JWT", "kid": kid}
    payload = {"iat": now, "exp": now + ttl_seconds, "aud": "/admin/"}

    segments = [
        _b64url(json.dumps(header, separators=(",", ":")).encode()),
        _b64url(json.dumps(payload, separators=(",", ":")).encode()),
    ]
    signing_input = ".".join(segments).encode()
    signature = hmac.new(
        bytes.fromhex(secret), signing_input, hashlib.sha256
    ).digest()
    segments.append(_b64url(signature))
    return ".".join(segments)


# ── HTTP layer ─────────────────────────────────────────────────

def api_call(method, endpoint, payload=None, retries=3):
    """Call the Ghost Admin API with JWT auth and retry on server errors.

    Args:
        method: GET | POST | PUT | DELETE
        endpoint: path after /ghost/api/admin/
        payload: dict for POST/PUT, or raw string for status endpoints
        retries: attempts for retryable failures

    Returns:
        Parsed JSON dict (Ghost wraps responses as {"posts":[...]} etc.)

    Raises:
        EnvironmentError on missing/bad credentials
        RuntimeError on non-retryable API errors
    """
    _load_dotenv()

    if not GHOST_SITE:
        raise EnvironmentError("NMM_GHOST_SITE_URL is not set")
    if not GHOST_ADMIN_KEY:
        raise EnvironmentError("NMM_GHOST_ADMIN_API_KEY is not set")

    url = f"{GHOST_SITE}/ghost/api/admin/{endpoint.lstrip('/')}"

    last_err = None
    for attempt in range(retries):
        # Fresh JWT each attempt — they expire after 5 min
        token = make_jwt()

        headers = {
            "Authorization": f"Ghost {token}",
            "Accept": "application/json",
        }
        data = None
        if isinstance(payload, str):
            headers["Content-Type"] = "text/plain; charset=utf-8"
            data = payload.encode("utf-8")
        elif payload is not None:
            headers["Content-Type"] = "application/json; charset=utf-8"
            data = json.dumps(payload).encode("utf-8")

        req = urllib.request.Request(url, data=data, headers=headers, method=method)

        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                raw = resp.read().decode("utf-8", errors="replace")
                if not raw.strip():
                    return {"_status": resp.status}
                try:
                    return json.loads(raw)
                except json.JSONDecodeError:
                    return {"_raw": raw, "_status": resp.status}

        except urllib.error.HTTPError as e:
            body = ""
            try:
                body = e.read().decode("utf-8", errors="replace")[:600]
            except Exception:
                pass
            last_err = f"HTTP {e.code}: {body}"

            # Auth failures are permanent — surface clearly
            if e.code in (401, 403):
                raise EnvironmentError(
                    f"Ghost auth failed (HTTP {e.code}). Check the Admin API key.\n{body}"
                )
            # Validation / client errors — don't burn retries
            if 400 <= e.code < 500:
                raise RuntimeError(f"Ghost API rejected the request\n{last_err}")
            # 5xx — retry with backoff
            if attempt < retries - 1:
                wait = 2 ** attempt
                print(f"  [{attempt+1}/{retries}] {last_err[:120]} — retrying in {wait}s")
                time.sleep(wait)

        except Exception as e:
            last_err = str(e)
            if attempt < retries - 1:
                wait = 2 ** attempt
                print(f"  [{attempt+1}/{retries}] {last_err[:120]} — retrying in {wait}s")
                time.sleep(wait)

    raise RuntimeError(f"Ghost API failed after {retries} attempts: {last_err}")


# ── Post operations ────────────────────────────────────────────

def slugify(text):
    s = re.sub(r"[^a-z0-9]+", "-", text.lower())
    return s.strip("-")[:180]


def markdown_to_html(md):
    """Convert markdown to HTML for the Ghost Admin API.

    CRITICAL: Ghost's Admin API does NOT accept a `markdown` field. It accepts
    html, mobiledoc, or lexical only. Sending `markdown` does not error — Ghost
    quietly stores an EMPTY body and returns 201, so the post publishes with a
    title and no content. `?source=markdown` is not a valid value either (422).

    So: convert to HTML here and post it as `html` with source=html. Raw HTML
    blocks pass through untouched, which is what lets the figures carry
    responsive srcset markup.
    """
    import markdown as _md
    return _md.markdown(md, extensions=[
        "tables",
        "fenced_code",
        "sane_lists",
        "attr_list",
        "md_in_html",
    ])


def find_post_by_slug(slug):
    """Return an existing post dict for this slug, or None."""
    try:
        result = api_call("GET", f"posts/?filter=slug:{slug}&limit=1")
    except RuntimeError:
        return None
    posts = result.get("posts", [])
    return posts[0] if posts else None


def create_or_update_post(title, markdown, options=None):
    """Create a post, or update the existing one with the same slug.

    options keys: slug, status, tags, primary_tag, visibility,
                  feature_image, meta_title, meta_description,
                  custom_excerpt, published_at
    """
    options = options or {}

    # The killswitch gates here, not in main(), so every caller is covered —
    # refresh_brief.py and send_weekly_brief.py write posts too and neither goes
    # through the CLI. Same reasoning as the lint gate below it.
    import killswitch
    killswitch.check("Ghost publish")

    # Both gates live here rather than in main(), so every caller is covered.
    # send_weekly_brief.py and refresh_brief.py write bodies too, and neither
    # went through the CLI, so neither was ever linted.
    if not options.get("skip_lint"):
        ok, out = lint_markdown(markdown)
        print(f"  voice lint: {out.splitlines()[0] if out else 'no output'}")
        if not ok:
            raise ValueError(f"voice lint refused this draft:\n{out}")

    slug = options.get("slug") or slugify(title)
    status = options.get("status", "published")
    tags = options.get("tags") or ([options["primary_tag"]] if options.get("primary_tag") else [])
    pub_at = options.get("published_at") or datetime.now(timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%S.000Z"
    )

    # Ghost expects tag_list as a list of names (it creates missing tags itself)
    # Ghost takes HTML, not markdown. Convert here, or the body publishes empty.
    html_body = markdown_to_html(markdown)

    body = {
        "title": title,
        "html": html_body,
        "slug": slug,
        "status": status,
        "visibility": options.get("visibility", "public"),
        "featured": False,
        "published_at": pub_at,
        "custom_excerpt": options.get("custom_excerpt", ""),
        "meta_title": options.get("meta_title", title),
        "meta_description": options.get("meta_description", title[:160]),
        "tags": [{"name": t} for t in tags],
    }
    if options.get("feature_image"):
        body["feature_image"] = options["feature_image"]

    existing = find_post_by_slug(slug)

    if existing:
        body["updated_at"] = existing["updated_at"]  # collision guard
        print(f"  Updating existing post: {existing.get('id')} ({existing.get('status')})")
        result = api_call("PUT", f"posts/{existing['id']}/?source=html", {"posts": [body]})
        action = "updated"
    else:
        print(f"  Creating post: slug='{slug}' status={status}")
        result = api_call("POST", "posts/?source=html", {"posts": [body]})
        action = "created"

    posts = result.get("posts") or []
    post = posts[0] if posts else result.get("post", {})

    if not post.get("id"):
        raise RuntimeError(
            f"Ghost returned no post id for '{slug}'. Response: {str(result)[:300]}"
        )

    # Assert the body actually stored. Ghost answers 201 for writes it silently
    # discards: a `markdown` field stores an empty body, and the newsletter
    # relation is dropped from a body field. Checking the HTTP status alone
    # would have called every one of those a success.
    try:
        chk = api_call("GET", f"posts/{post['id']}/?formats=html&fields=html,status")
        stored = ((chk.get("posts") or [{}])[0].get("html") or "").strip()
    except Exception as e:
        raise RuntimeError(f"could not read back post {post['id']}: {e}")

    if not stored:
        raise RuntimeError(
            f"post {post['id']} stored an EMPTY body. Ghost accepted the write "
            f"but kept nothing. Not reporting success."
        )

    return {
        "success": True,
        "action": action,
        "ghost_id": post.get("id"),
        "status": post.get("status"),
        "url": post.get("url"),
        "slug": post.get("slug"),
        "updated_at": post.get("updated_at"),
        "body_chars": len(stored),
    }


def verify_published(ghost_id, attempts=4, interval=4):
    """Poll until the post reports status=published."""
    for i in range(attempts):
        try:
            result = api_call("GET", f"posts/{ghost_id}/")
            post = (result.get("posts") or [{}])[0]
            status = post.get("status")
            if status == "published":
                return {
                    "verified": True,
                    "status": status,
                    "url": post.get("url"),
                    "published_at": post.get("published_at"),
                }
            print(f"    [{i+1}/{attempts}] status='{status}' — waiting")
        except Exception as e:
            print(f"    [{i+1}/{attempts}] verify error: {e}")
        if i < attempts - 1:
            time.sleep(interval)
    return {"verified": False, "reason": f"never reached 'published' after {attempts} polls"}


# ── Draft file handling ────────────────────────────────────────

def parse_frontmatter(content):
    """Return (frontmatter_dict, body_markdown)."""
    if not content.startswith("---"):
        return {}, content
    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}, content

    fm = {}
    for line in parts[1].strip().splitlines():
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        v = v.strip().strip('"').strip("'")
        # Inline YAML list: tags: [a, b, c]
        if v.startswith("[") and v.endswith("]"):
            v = [x.strip().strip('"').strip("'") for x in v[1:-1].split(",") if x.strip()]
        fm[k.strip()] = v
    return fm, parts[2].strip()


def options_from_frontmatter(fm, default_status=None):
    """Build Ghost post options from YAML frontmatter.

    Resolution order for status: the CLI --status flag (passed in as
    default_status) wins, then the file's own `status:` key, then "published".

    This previously took default_status="published" and never looked at
    fm["status"] at all, so a draft file with `status: draft` in its
    frontmatter published LIVE. The docstring claimed the opposite, and the
    blog cron's frontmatter template emits a status key.
    """
    opts = {"status": default_status or fm.get("status") or "published"}
    if opts["status"] not in ("published", "draft", "scheduled"):
        raise ValueError(
            f"frontmatter status {opts['status']!r} is not one of "
            "published/draft/scheduled"
        )

    if fm.get("slug"):
        opts["slug"] = fm["slug"]
    if fm.get("description") or fm.get("meta_description"):
        desc = fm.get("description") or fm.get("meta_description")
        opts["meta_description"] = str(desc)[:160]
        opts["custom_excerpt"] = str(desc)[:200]
    if fm.get("category"):
        opts["tags"] = [fm["category"]]
    if isinstance(fm.get("tags"), list):
        opts["tags"] = fm["tags"]
    if fm.get("date"):
        d = str(fm["date"])
        if len(d) == 10:
            opts["published_at"] = f"{d}T12:00:00.000Z"
    return opts


# ── CLI ────────────────────────────────────────────────────────

def pretty_url(url):
    """Ghost returns absolute URLs in the `url` field. Don't prepend the host.

    Falls back to prefixing the ghost host only if the value is a bare path."""
    if not url:
        return ""
    if url.startswith("http://") or url.startswith("https://"):
        return url
    return f"{GHOST_SITE}{url}"


def upload_image(path, purpose="image"):
    """Upload a local image file to Ghost and return its public URL.

    Ghost stores uploads under /content/images/<year>/<month>/ and returns
    the absolute URL in the response. Requires multipart/form-data, so this
    uses `requests` rather than the JSON `api_call` helper.

    Args:
        path: local file path to the image
        purpose: Ghost's purpose hint — "image", "profile_image", or "icon"

    Returns:
        dict with success, url, and the raw response
    """
    import requests

    _load_dotenv()
    if not GHOST_SITE:
        raise EnvironmentError("NMM_GHOST_SITE_URL is not set")
    if not GHOST_ADMIN_KEY:
        raise EnvironmentError("NMM_GHOST_ADMIN_API_KEY is not set")

    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"No such image: {path}")

    ext = path.suffix.lower().lstrip(".") or "png"
    mime = {
        "png": "image/png",
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "gif": "image/gif",
        "webp": "image/webp",
        "svg": "image/svg+xml",
    }.get(ext, "application/octet-stream")

    url = f"{GHOST_SITE}/ghost/api/admin/images/upload/"
    headers = {"Authorization": f"Ghost {make_jwt()}"}

    last_err = None
    for attempt in range(3):
        headers["Authorization"] = f"Ghost {make_jwt()}"  # fresh token
        try:
            with open(path, "rb") as fh:
                resp = requests.post(
                    url,
                    headers=headers,
                    files={"file": (path.name, fh, mime)},
                    data={"purpose": purpose, "ref": path.stem},
                    timeout=60,
                )
        except Exception as e:
            last_err = str(e)
            time.sleep(2 ** attempt)
            continue

        if resp.status_code in (200, 201):
            try:
                body = resp.json()
            except ValueError:
                return {"success": False, "error": f"non-JSON response: {resp.text[:200]}"}
            images = body.get("images") or []
            if images:
                return {"success": True, "url": images[0].get("url"),
                        "raw": images[0]}
            return {"success": False, "error": f"no images in response: {str(body)[:200]}"}

        if resp.status_code in (401, 403):
            raise EnvironmentError(
                f"Ghost auth failed ({resp.status_code}) on image upload: {resp.text[:200]}"
            )

        last_err = f"HTTP {resp.status_code}: {resp.text[:200]}"
        if resp.status_code >= 500:
            time.sleep(2 ** attempt)

    return {"success": False, "error": last_err}


def run_voice_lint(path):
    """Run the deterministic AI-tell scanner on a draft file.

    Returns (ok, output). An LLM cannot see its own tells reliably, so this
    is a hard gate rather than a suggestion.

    A missing scanner FAILS CLOSED. Returning ok=True when voice_lint.py was
    absent meant the gate silently disappeared — the one failure mode a gate
    must never have.
    """
    import subprocess
    script = Path(__file__).resolve().parent / "voice_lint.py"
    if not script.exists():
        return False, f"voice lint FATAL: {script} not found — refusing to publish"
    try:
        p = subprocess.run(
            [sys.executable, str(script), str(path)],
            capture_output=True, text=True, timeout=60,
        )
    except Exception as e:
        return False, f"voice lint could not run: {e}"
    out = (p.stdout or "") + (p.stderr or "")
    return p.returncode == 0, out.strip()


def lint_markdown(markdown):
    """Lint markdown held in memory, so every writer is gated, not just the CLI.

    Returns (ok, output), failing closed like run_voice_lint.
    """
    import subprocess
    script = Path(__file__).resolve().parent / "voice_lint.py"
    if not script.exists():
        return False, f"voice lint FATAL: {script} not found — refusing to publish"
    try:
        p = subprocess.run(
            [sys.executable, str(script), "-"],
            input=markdown, capture_output=True, text=True, timeout=60,
        )
    except Exception as e:
        return False, f"voice lint could not run: {e}"
    out = (p.stdout or "") + (p.stderr or "")
    return p.returncode == 0, out.strip()


def load_visual_manifest(topic_id):
    """Load visuals/<topic_id>/manifest.json if the composer produced one."""
    mpath = Path(__file__).resolve().parent.parent / "visuals" / topic_id / "manifest.json"
    if not mpath.exists():
        return None
    try:
        with open(mpath, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None




def ghost_variant(url, width=720, fmt="webp"):
    """Point a Ghost asset URL at a resized/transcoded variant.

    Ghost serves /content/images/size/w720/format/webp/<path> for any uploaded
    image, so one master upload covers every display size.

    Why 720px WebP as a single src rather than a srcset:

    - Desktop post content is ~720px, so it renders 1:1.
    - A phone shows it at ~343px, which needs ~686px for a retina screen, so
      720px is still exactly sharp.
    - Ghost does NOT reliably preserve a hand-written srcset on a raw <img>:
      it either strips it or rewrites it by prepending its own transform to an
      already-transformed URL, producing /size/w600/size/w720/format/webp/.
      It does preserve a transformed src untouched.

    So one well-chosen src beats fighting the platform's rewriting.
    """
    marker = "/content/images/"
    if marker not in url:
        return url
    prefix, _, tail = url.partition(marker)
    # Strip any transform the URL already carries so we never double up.
    tail = re.sub(r"^(size/w\d+/)|(format/\w+/)+", "", tail)
    return f"{prefix}{marker}size/w{width}/format/{fmt}/{tail}"


def substitute_figures(markdown, manifest):
    """Replace {{figure:name}} placeholders with image markup.

    Returns (text, unresolved_names).

    Emits a plain <img> whose src already points at a correctly sized WebP
    variant. Ghost wraps it in its own kg-image-card and keeps the transform.
    Unresolved placeholders are stripped rather than shipped literally.
    """
    if not manifest:
        return markdown, []
    figs = {f["name"]: f for f in manifest.get("figures", [])}
    unresolved = []

    def _repl(m):
        name = m.group(1).strip()
        fig = figs.get(name)
        if not fig or not fig.get("url"):
            unresolved.append(name)
            return ""

        caption = fig.get("caption", "")
        alt = (caption or name.replace("-", " ")).replace('"', "'")
        src = ghost_variant(fig["url"], width=720, fmt="webp")
        block = f'<img src="{src}" alt="{alt}">'
        if caption:
            block += f'\n<p class="fig-caption"><em>{caption}</em></p>'
        return block

    return re.sub(r"\{\{figure:([a-zA-Z0-9_-]+)\}\}", _repl, markdown), unresolved


def main():
    import argparse

    ap = argparse.ArgumentParser(description="Publish NMM blog posts to Ghost")
    ap.add_argument("file", nargs="?", help="Markdown file (default: newest in content/blog-posts/)")
    ap.add_argument("--status", choices=["published", "draft", "scheduled"],
                   default=None,
                   help="Post status. Omit to let the file's frontmatter "
                        "decide, falling back to published.")
    ap.add_argument("--dry-run", action="store_true",
                   help="Validate content without sending to Ghost")
    ap.add_argument("--check", action="store_true", help="Test credentials and list recent posts")
    ap.add_argument("--skip-lint", action="store_true",
                   help="Bypass the voice-lint gate (only for re-publishing an already-linted post)")
    ap.add_argument("--allow-missing-visuals", action="store_true",
                   help="Publish even if figure placeholders did not resolve")
    args = ap.parse_args()

    _load_dotenv()

    if args.check:
        if not GHOST_SITE or not GHOST_ADMIN_KEY:
            print("FAIL: credentials not set (env or .env)")
            return 1
        try:
            result = api_call("GET", "posts/?limit=3")
        except Exception as e:
            print(f"FAIL: {e}")
            return 1
        posts = result.get("posts", [])
        total = result.get("meta", {}).get("pagination", {}).get("total", "?")
        print(f"OK — connected to {GHOST_SITE}")
        print(f"     {total} posts on the site")
        for p in posts:
            print(f"     - [{p.get('status')}] {p.get('title')}")
        return 0

    # Resolve target file
    if args.file:
        target = Path(args.file)
    else:
        blog_dir = Path(__file__).resolve().parent.parent / "content" / "blog-posts"
        candidates = sorted(blog_dir.glob("*.md"))
        if not candidates:
            print(f"FAIL: no .md files in {blog_dir}")
            return 1
        target = candidates[-1]

    if not target.exists():
        print(f"FAIL: no such file {target}")
        return 1

    content = target.read_text(encoding="utf-8")
    fm, body = parse_frontmatter(content)

    title = fm.get("title") or target.stem.replace("-", " ").title()
    opts = options_from_frontmatter(fm, default_status=args.status)

    words = len(body.split())
    print(f"=== Ghost Publish ===")
    print(f"  Host:   {GHOST_SITE or '(not set)'}")
    print(f"  File:   {target.name}")
    print(f"  Title:  {title}")
    print(f"  Slug:   {opts.get('slug', slugify(title))}")
    print(f"  Status: {opts['status']}")
    print(f"  Body:   {words} words / {len(body)} chars")

    if words < 200:
        print(f"  WARN: body is only {words} words — looks like a stub")

    # ── GATE 1: voice lint ──────────────────────────────────────
    # Mechanical AI tells are not a style preference here; they are the
    # difference between a blog that reads like a person and one that does not.
    if not args.skip_lint:
        ok, out = run_voice_lint(target)
        if not ok:
            print("  VOICE LINT FAILED — refusing to publish")
            for line in out.splitlines():
                print(f"    {line}")
            return 1
        print(f"  voice lint: PASS{' (' + out.splitlines()[-1] + ')' if out else ''}")
    else:
        print("  voice lint: SKIPPED (--skip-lint)")

    # ── GATE 2: visuals ────────────────────────────────────────
    # A post with unresolved figure placeholders must not ship: the reader
    # would see raw {{figure:...}} markup.
    manifest = load_visual_manifest(target.stem)
    placeholder_count = len(re.findall(r"\{\{figure:[a-zA-Z0-9_-]+\}\}", body))

    if manifest:
        figs = manifest.get("figures", [])
        hero = manifest.get("hero") or {}
        uploaded = sum(1 for f in figs if f.get("url"))
        print(f"  visuals: manifest found — {uploaded}/{len(figs)} figures uploaded")
        if hero.get("url") and not opts.get("feature_image"):
            opts["feature_image"] = hero["url"]
            print(f"  feature image set from hero card")
        body, unresolved = substitute_figures(body, manifest)
        if unresolved:
            print(f"  VISUALS: unresolved placeholders {unresolved} — stripping")
        if placeholder_count and uploaded == 0 and not args.allow_missing_visuals:
            print("  VISUALS FAILED — placeholders present but nothing uploaded")
            return 1
    elif placeholder_count:
        print(f"  VISUALS FAILED — {placeholder_count} placeholder(s) but no manifest at "
              f"visuals/{target.stem}/manifest.json")
        print("  Run scripts/compose_post_visuals.py for this topic first.")
        if not args.allow_missing_visuals:
            return 1
    else:
        print("  visuals: none referenced")

    if args.dry_run:
        print("  DRY RUN — no API call made")
        return 0

    try:
        result = create_or_update_post(title, body, opts)
    except Exception as e:
        print(f"  FAIL: {e}")
        return 1

    print(f"  {result['action'].upper()}: {result.get('ghost_id')}")
    print(f"  Status: {result.get('status')}")
    if result.get("url"):
        print(f"  URL: {pretty_url(result['url'])}")

    if result.get("status") == "published":
        v = verify_published(result["ghost_id"])
        if v.get("verified"):
            print(f"  VERIFIED live: {pretty_url(v.get('url'))}")
        else:
            print(f"  UNVERIFIED: {v.get('reason')}")
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
