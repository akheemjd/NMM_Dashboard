#!/usr/bin/env python3
"""Render content/blog-posts/*.md as static pages on the dashboard.

WHY THIS EXISTS

The blog was Ghost. Ghost(Pro) was cancelled on 2026-10-15 and its domain went to 404, which took
14 finished posts and the newsletter with it. But the posts were never the problem - the hosting
was. They are markdown files in this repo with frontmatter, and the dashboard is already a static
site on GitHub Pages that rebuilds hourly.

So they render here instead: /blog/ and /blog/<slug>/, on the same domain, at no cost. Nothing to
renew, no service to cancel, no third party to go down. build_sitemap.py walks docs/ looking for
index.html, so these pages are submitted to Google with no extra wiring.

Writes:
    docs/blog/index.html            the post list, newest first
    docs/blog/<slug>/index.html     one page per published post

MUST RUN AFTER gen_templates.py: importing it executes its module body, which rewrites
templates/*.template.html. Those are inputs to the other builders and are already consumed by this
point in the chain, so the rebuild is harmless - but running this first would race them.
"""
import datetime
import html
import os
import re
import sys

import markdown

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import gen_templates as G  # noqa: E402  (imported for head()/foot(); see module docstring)

POSTS_DIR = os.path.join(HERE, "..", "content", "blog-posts")
OUT_DIR = os.path.join(HERE, "..", "docs", "blog")
BASE = "https://dashboard.northernmilemedia.com"

FRONTMATTER = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.S)


def parse_post(path):
    """Frontmatter + body. The frontmatter here is flat key: value with a few [lists]."""
    raw = open(path, encoding="utf-8").read()
    m = FRONTMATTER.match(raw)
    if not m:
        return None
    meta = {}
    for line in m.group(1).splitlines():
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        v = v.strip().strip('"').strip("'")
        if v.startswith("[") and v.endswith("]"):
            v = ", ".join(x.strip() for x in v[1:-1].split(",") if x.strip())
        meta[k.strip()] = v
    body = raw[m.end():].strip()
    if not meta.get("slug") or not body:
        return None
    return meta, body


def load_posts():
    posts = []
    if not os.path.isdir(POSTS_DIR):
        return posts
    for name in sorted(os.listdir(POSTS_DIR)):
        if not name.endswith(".md"):
            continue
        parsed = parse_post(os.path.join(POSTS_DIR, name))
        if not parsed:
            continue
        meta, body = parsed
        if meta.get("status", "published") != "published":
            continue
        meta["body"] = body
        meta.setdefault("category", "Trucking")
        meta.setdefault("date", "1970-01-01")
        posts.append(meta)
    posts.sort(key=lambda p: p["date"], reverse=True)
    return posts


def page(head_html, body_html, tail):
    """Fill the tokens head() and foot() leave behind.

    head() carries {{build_version}} and {{updated_iso}}; foot() carries {{build_version}} again
    plus {{updated_at}} in its "Updated ... UTC" line. The rest of the site resolves these through
    the fill engine, which needs a per-page data dict this builder does not have - so they are
    substituted directly. Any token left over fails loudly below rather than shipping braces to a
    reader.
    """
    now = datetime.datetime.now(datetime.timezone.utc)
    stamp_iso = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    stamp_human = now.strftime("%Y-%m-%d %H:%M")

    out = (head_html + body_html + tail)
    out = out.replace("{{build_version}}", stamp_human.replace(" ", "-").replace(":", ""))
    out = out.replace("{{updated_iso}}", stamp_iso)
    out = out.replace("{{updated_at}}", stamp_human)

    leftover = re.findall(r"\{\{[^}]*\}\}", out)
    if leftover:
        raise SystemExit(f"blog: unresolved template tokens {sorted(set(leftover))}")
    return out


def render_index(posts):
    rows = []
    for p in posts:
        when = p["date"]
        rows.append(
            f'      <a class="r" href="/blog/{html.escape(p["slug"])}/">'
            f'<span class="k">{html.escape(p["category"])}</span>'
            f'<span class="t">{html.escape(p["title"])}</span>'
            f'<span class="d">{html.escape(p.get("description", "")[:150])}</span>'
            f'<span class="m">{when}</span></a>'
        )
    count = len(posts)
    body = f"""
  <section class="sec">
    <div class="lead"><h1>Writing</h1><p>{count} pieces on cross-border trucking, from the data.</p></div>
    <div class="reading">
      <p>Every piece here starts from a published figure and names where it came from. No press
      releases, no sponsored copy. When a number is in a sentence, the source is at the bottom of
      the page.</p>
    </div>
  </section>

  <section class="sec">
    <div class="lead"><h2>Latest</h2></div>
    <div class="rows">
{chr(10).join(rows) if rows else '      <p class="note">Nothing published yet.</p>'}
    </div>
  </section>
"""
    ld = ('{"@type":"Blog","@id":"' + BASE + '/blog/#blog","name":"Northern Mile Media writing",'
          '"url":"' + BASE + '/blog/","publisher":{"@type":"Organization","name":"Northern Mile Media",'
          '"url":"' + BASE + '/"},"inLanguage":"en-CA"}')
    title = "Writing — cross-border trucking, from the data | Northern Mile"
    desc = (f"{count} pieces on Canadian and US diesel prices, border wait times and cross-border "
            "trucking costs, each one built from a published source.")
    return page(G.head(title, desc, BASE + "/blog/", "/og.jpg", ld),
                body, G.foot())


def render_post(p):
    slug = html.escape(p["slug"])
    canon = f"{BASE}/blog/{slug}/"

    # Ghost-era figure macros, e.g. {{figure:provincial-spread}}. The images they pointed at were
    # uploaded to Ghost and went with the cancelled account, so there is nothing to resolve them to
    # and they would print as literal braces. Dropped rather than left dangling; the prose around
    # them still reads, and the charts themselves live on the dashboard. Alternates ("figure-x" /
    # "alt-x") and anything on their own line or inside a paragraph both go.
    body_md = re.sub(r"\{\{figure:[^}]*\}\}", "", p["body"])
    body_md = re.sub(r"\n{3,}", "\n\n", body_md)

    body_html = markdown.markdown(body_md, extensions=["extra", "sane_lists"])
    # The writer's copy often opens with its own H1; the page supplies one.
    body_html = re.sub(r"^\s*<h1[^>]*>.*?</h1>\s*", "", body_html, count=1, flags=re.S)

    meta_line = " · ".join(x for x in (html.escape(p["date"]), html.escape(p["category"])) if x)
    tags = p.get("tags", "")
    tag_line = (f'      <p class="note">Filed under {html.escape(tags)}.</p>' if tags else "")

    ld = ('{"@type":"BlogPosting","@id":"' + canon + '#post",'
          '"headline":' + _json(p["title"]) + ','
          '"description":' + _json(p.get("description", "")) + ','
          '"datePublished":"' + p["date"] + '",'
          '"author":{"@type":"Organization","name":"Northern Mile Media"},'
          '"publisher":{"@type":"Organization","name":"Northern Mile Media","url":"' + BASE + '/"},'
          '"mainEntityOfPage":"' + canon + '","inLanguage":"en-CA"}')

    body = f"""
  <section class="sec">
    <div class="lead"><h1>{html.escape(p["title"])}</h1><p>{meta_line}</p></div>
    <div class="reading">
{_indent(body_html)}
    </div>
{tag_line}  </section>

  <section class="sec">
    <p class="note"><a href="/blog/">All writing</a> · <a href="/methodology/">How the numbers are made</a></p>
  </section>
"""
    return page(G.head(p.get("seo_title") or p["title"], p.get("description", ""), canon, "/og.jpg", ld, og_type="article"),
                body, G.foot())


def _json(s):
    return '"' + str(s).replace("\\", "\\\\").replace('"', '\\"') + '"'


def _indent(block, pad="      "):
    return "\n".join(pad + ln if ln.strip() else ln for ln in block.splitlines())


def main():
    posts = load_posts()
    if not posts:
        print("  blog: no published posts, nothing to build")
        return

    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, "index.html"), "w", encoding="utf-8", newline="\n") as f:
        f.write(render_index(posts))

    for p in posts:
        d = os.path.join(OUT_DIR, p["slug"])
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "index.html"), "w", encoding="utf-8", newline="\n") as f:
            f.write(render_post(p))

    print(f"  blog: {len(posts)} posts + index")


if __name__ == "__main__":
    main()
