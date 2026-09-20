#!/usr/bin/env python3
"""Send The Northern Mile Brief as a Ghost newsletter.

THE THING THAT COST THE MOST TIME

The newsletter link is NOT a body field. Sending `newsletter` (or
`newsletter_id`, or a slug, or an object) in the JSON body is accepted with
HTTP 201 and then silently stored as null. Ghost ignores unknown body fields,
so every shape looks identical to a working one.

It is a QUERY PARAMETER on the publish or schedule request:

    PUT /posts/<id>/?newsletter=<slug>&email_segment=all

Per Ghost's docs: "To send a post by email, the newsletter query parameter
must be passed when publishing or scheduling the post, containing the
newsletter's slug." A post is emailed if and only if an active newsletter is
supplied. It must be supplied at publish time, not at draft creation.

So this script:
  1. creates the post as a DRAFT (nothing is emailed, ever, on a draft)
  2. verifies the body actually stored
  3. publishes with ?newsletter=<slug>, which dispatches the email
  4. reads back the `email` object Ghost attaches and reports delivered_count

Step 3 is opt-in via --send. Sending is irreversible, so the destructive path
is never the default.
"""

import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from ghost_publish import (  # noqa: E402
    api_call, markdown_to_html, slugify, find_post_by_slug, upload_image,
    lint_markdown, _load_dotenv,
)
from weekly_brief import build_brief  # noqa: E402


def resolve_newsletter(default="default-newsletter"):
    """Return the slug of the active newsletter.

    Read from the API rather than hard-coded, so a renamed newsletter does not
    quietly break sending. An env override wins if set.
    """
    _load_dotenv()
    override = os.environ.get("NMM_GHOST_NEWSLETTER_SLUG")
    if override:
        return override.strip()
    try:
        r = api_call("GET", "newsletters/?limit=all&fields=slug,status")
        for n in r.get("newsletters", []):
            if n.get("status") == "active":
                return n.get("slug") or default
    except Exception:
        pass
    return default


def recent_posts(days=7, limit=8, exclude_slug=None):
    """The week's published articles, newest first, for the brief's links.

    Returns [] on any failure. A brief with a missing link list is still worth
    sending; a brief that fails to send because Ghost had a hiccup is not.
    """
    import datetime as _dt

    try:
        r = api_call(
            "GET",
            f"posts/?limit={limit}&filter=status:published"
            "&order=published_at%20desc&fields=title,url,slug,published_at",
        )
    except Exception:
        return []

    cutoff = _dt.datetime.now(_dt.timezone.utc) - _dt.timedelta(days=days)
    out = []
    for p in r.get("posts", []):
        if exclude_slug and p.get("slug") == exclude_slug:
            continue
        # Never link a brief to another brief, including an earlier one sent
        # the same week. The brief points at articles.
        if (p.get("slug") or "").startswith("the-northern-mile-brief"):
            continue
        pa = p.get("published_at") or ""
        try:
            when = _dt.datetime.fromisoformat(pa.replace("Z", "+00:00"))
        except ValueError:
            continue
        if when < cutoff:
            continue
        out.append({"title": p.get("title") or "", "url": p.get("url") or ""})
    return out


def brief_hero():
    """Generate and upload a feature image for the brief.

    The first brief shipped with no feature image, so it rendered as a
    text-only card on the blog beside posts that all had one. Returns None on
    any failure: a brief without a hero is worse than one with, but a brief
    that never sends because image generation broke is worse than both.
    """
    import json

    try:
        import blog_visuals

        with open(ROOT / "data" / "fuel.json", encoding="utf-8") as f:
            fuel = json.load(f)
    except Exception:
        return None

    nat = fuel.get("diesel_national_avg")
    stamp = fuel.get("print_date")
    try:
        img = blog_visuals.hero_card(
            headline="Canada's diesel average this week",
            eyebrow="The Northern Mile Brief",
            stat_value=f"{nat}¢" if nat is not None else None,
            stat_label="/L national average",
            source=(f"NRCan weekly survey, print {stamp}" if stamp
                    else "NRCan weekly survey"),
            variant="paper",
        )
        path = blog_visuals.save_hero(img, "brief-hero")
    except Exception:
        return None

    try:
        res = upload_image(str(path))
        return res.get("url") if isinstance(res, dict) else res
    except Exception:
        return None


def build_payload(title, subtitle, markdown, slug, status, published_at=None):
    """Body only. The newsletter link does NOT belong here."""
    return {
        "title": title,
        "html": markdown_to_html(markdown),
        "slug": slug,
        "status": status,
        "custom_excerpt": subtitle,
        "meta_description": subtitle,
        "email_subject": title,
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description="Send the weekly NMM brief")
    ap.add_argument("--dry-run", action="store_true",
                    help="Print only. No API calls at all.")
    ap.add_argument("--send", action="store_true",
                    help="Publish and dispatch the email (IRREVERSIBLE).")
    ap.add_argument("--schedule", metavar="ISO",
                    help="Schedule instead, e.g. 2026-09-23T06:00:00.000Z")
    args = ap.parse_args(argv)

    title, subtitle, markdown = build_brief(
        recent_posts=None if args.dry_run else recent_posts()
    )
    slug = slugify(title)
    nl_slug = None if args.dry_run else resolve_newsletter()

    if args.dry_run:
        print("=== DRY RUN — no API calls made ===")
        print(f"title:      {title}")
        print(f"slug:       {slug}")
        print(f"subject:    {title}")
        print(f"newsletter: {resolve_newsletter()} (would be sent as a query param)")
        print()
        print(markdown)
        return 0

    try:
        existing = find_post_by_slug(slug)
    except Exception as exc:
        print(f"STOP — could not check whether '{slug}' exists ({exc}).")
        print("Refusing to continue: a second brief for the same week would")
        print("email every subscriber twice.")
        return 1

    if existing:
        print(f"STOP — a brief for this week already exists "
              f"(status={existing.get('status')}). Not sending again.")
        return 1

    print(f"=== {title} ===")
    print(f"  slug:       {slug}")
    print(f"  newsletter: {nl_slug} (query param, applied at publish)")

    # This path creates and publishes the newsletter straight through api_call,
    # so it never reaches the gate inside create_or_update_post and was never
    # linted. The brief publishes to the site as a post, so it is held to the
    # same standard as any article.
    ok, out = lint_markdown(markdown)
    print(f"  voice lint: {out.splitlines()[0] if out else 'no output'}")
    if not ok:
        print("\nREFUSING to publish: the brief failed the voice lint.")
        print(out)
        return 1

    print("\n[1/3] creating draft (a draft can never email anyone)...")
    payload = build_payload(title, subtitle, markdown, slug, "draft")
    hero = brief_hero()
    if hero:
        payload["feature_image"] = hero
        print(f"      hero: {hero.rsplit('/', 1)[-1]}")
    else:
        print("      hero: NONE (image generation unavailable)")
    r = api_call("POST", "posts/?source=html", {"posts": [payload]})
    post = (r.get("posts") or [{}])[0]
    pid = post.get("id")
    print(f"      id: {pid}")

    print("[2/3] verifying the body stored...")
    chk = api_call("GET", f"posts/{pid}/?formats=html&fields=html,status")
    stored = ((chk.get("posts") or [{}])[0]).get("html") or ""
    if not stored.strip():
        print("      FAIL — stored body is empty. Not publishing.")
        return 1
    print(f"      body: {len(stored)} chars  status: draft  OK")

    if not args.send and not args.schedule:
        print("\n[3/3] stopping. Post is a DRAFT and ready.")
        print("      Re-run with --send to publish and email the list.")
        return 0

    # The newsletter MUST ride as a query param on the publish call.
    if args.schedule:
        q = f"posts/{pid}/?source=html&newsletter={nl_slug}&email_segment=all"
        upd = build_payload(title, subtitle, markdown, slug, "scheduled", args.schedule)
        print(f"\n[3/3] scheduling with ?newsletter={nl_slug} ...")
        r2 = api_call("PUT", q, {"posts": [dict(upd, updated_at=post.get("updated_at"))]})
        p2 = (r2.get("posts") or [{}])[0]
        print(f"      status: {p2.get('status')}")
        em = p2.get("email")
        print(f"      email queued: {bool(em)}")
        return 0

    q = f"posts/{pid}/?source=html&newsletter={nl_slug}&email_segment=all"
    upd = build_payload(title, subtitle, markdown, slug, "published")
    print(f"\n[3/3] publishing with ?newsletter={nl_slug} (this dispatches the email)...")
    r2 = api_call("PUT", q, {"posts": [dict(upd, updated_at=post.get("updated_at"))]})
    p2 = (r2.get("posts") or [{}])[0]
    print(f"      status: {p2.get('status')}")
    print(f"      url:    {p2.get('url')}")

    em = p2.get("email") or {}
    if em:
        print("\n      email dispatched:")
        for k in ("status", "email_count", "delivered_count",
                  "opened_count", "failed_count", "recipient_filter"):
            if k in em:
                print(f"        {k}: {em[k]}")
        if em.get("error"):
            print(f"        error: {em['error']}")
    else:
        print("\n      WARNING: no email object came back.")
        print("      The post published but may not have emailed anyone.")
        print("      Check Ghost admin before assuming the list received it.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
