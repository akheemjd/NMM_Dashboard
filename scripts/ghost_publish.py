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

    slug = options.get("slug") or slugify(title)
    status = options.get("status", "published")
    tags = options.get("tags") or ([options["primary_tag"]] if options.get("primary_tag") else [])
    pub_at = options.get("published_at") or datetime.now(timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%S.000Z"
    )

    # Ghost expects tag_list as a list of names (it creates missing tags itself)
    body = {
        "title": title,
        "markdown": markdown,
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

    return {
        "success": bool(post.get("id")),
        "action": action,
        "ghost_id": post.get("id"),
        "status": post.get("status"),
        "url": post.get("url"),
        "slug": post.get("slug"),
        "updated_at": post.get("updated_at"),
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


def options_from_frontmatter(fm, default_status="published"):
    """Build Ghost post options from YAML frontmatter.

    NOTE: `status` from frontmatter is only used when the caller did not
    explicitly pass a status. The CLI --status flag always wins — an explicit
    operator instruction must not be silently overridden by file contents.
    """
    opts = {"status": default_status}

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


def main():
    import argparse

    ap = argparse.ArgumentParser(description="Publish NMM blog posts to Ghost")
    ap.add_argument("file", nargs="?", help="Markdown file (default: newest in content/blog-posts/)")
    ap.add_argument("--status", choices=["published", "draft", "scheduled"], default="published")
    ap.add_argument("--dry-run", action="store_true", help="Validate only, no API write")
    ap.add_argument("--check", action="store_true", help="Test credentials and list recent posts")
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
