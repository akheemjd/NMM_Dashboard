"""Build the www blog repo from the dashboard output.

This ran from C:	mp as scratch for most of a session, which meant the site at
www.northernmilemedia.com was produced by a file that was not in version control. Moving
it here makes it reviewable, revertible and guardable.

The www host carries the blog ONLY, but the blog pages come from the dashboard repo where every
nav and body link is root-relative: /fuel-prices/, /border-trends/, /advertise/. On www those
resolve to nothing - 18 links across the site returned 404.

Three transforms, applied to a fresh copy so nothing compounds:

  1. canonical  https://dashboard.northernmilemedia.com/blog/x/  ->  https://www.northernmilemedia.com/blog/x/
     The www copy must be canonical to itself, or Google treats it as a duplicate of the dashboard.

  2. root-relative /blog/... and /assets/...   -> unchanged (these exist on www)

  3. root-relative anything else (/fuel-prices/, /border-trends/, ...)  -> absolute dashboard URL
     Those pages live on the dashboard. Linking to them across hosts is correct; linking to a
     non-existent local path is not.

A previous attempt did the global dashboard->www replace FIRST, which destroyed the very host
distinction this needs. Order matters: absolute-ise the dashboard links, and only touch canonicals
for the www substitution.
"""
import pathlib
import re
import shutil

SRC = pathlib.Path(r"C:\Users\Akheem\northern-mile-dashboard\docs")
DST = pathlib.Path(r"C:\tmp\nmmblog")
WWW = "https://www.northernmilemedia.com"
DASH = "https://dashboard.northernmilemedia.com"

OLD = [
    "trucking-cost-per-kilometre-canada",
    "cra-psb-owner-operator-audit-canada",
    "what-diesel-costs-across-canada-province-by-province",
    "what-diesel-costs-across-canada-right-now-province-by-province-2",
    "ifta-filing-deadlines-for-canadian-carriers-in-2026-and-the-mistakes-that-trigger-audits",
]

# 1. fresh copy
# Keep .git (the repo) AND CNAME (GitHub Pages records the custom domain there - deleting it
# silently unroutes www.northernmilemedia.com and the host starts serving "Site not found").
for item in list(DST.iterdir()):
    if item.name in (".git", "CNAME", ".nojekyll"):
        continue
    shutil.rmtree(item) if item.is_dir() else item.unlink()
shutil.copytree(SRC / "blog", DST / "blog")
shutil.copytree(SRC / "assets", DST / "assets", dirs_exist_ok=True)
# og.jpg lives at the docs root, not in assets/, so the asset copy missed it and every blog post
# offered a social card image that 404ed on this host.
if (SRC / "og.jpg").exists():
    shutil.copy2(SRC / "og.jpg", DST / "og.jpg")
for s in OLD:
    if (SRC / s / "index.html").exists():
        (DST / s).mkdir(parents=True, exist_ok=True)
        shutil.copy2(SRC / s / "index.html", DST / s / "index.html")

CANON = re.compile(r'(<link rel="canonical" href=")' + re.escape(DASH) + r'([^"]*)"')
ROOTLINK = re.compile(r'(href|src)="(/(?!/)[^"]*)"')


def relink(m):
    attr, path = m.group(1), m.group(2)
    if path.startswith(("/blog/", "/assets/")):
        return f'{attr}="{path}"'
    return f'{attr}="{DASH}{path}"'


changed = 0
for f in DST.rglob("*.html"):
    t = f.read_text(encoding="utf-8")
    before = t
    t = CANON.sub(lambda m: m.group(1) + WWW + m.group(2) + '"', t)
    t = ROOTLINK.sub(relink, t)
    if t != before:
        f.write_text(t, encoding="utf-8", newline="\n")
        changed += 1
print(f"  pages rewritten: {changed}")

# The masthead anchors must NOT leave the blog. The generic rule above sends every non-blog path to
# the dashboard, which is right for section links (/fuel-prices/) and wrong for the logo: a reader on
# the blog who clicks the brand expects the blog front page, not a different site.
LOGO = re.compile(r'<(a)[^>]*class="(?:mark|name)"[^>]*href="[^"]*"')
for f in DST.rglob("*.html"):
    t = f.read_text(encoding="utf-8")
    fixed = LOGO.sub(lambda m: m.group(0).replace(
        re.search(r'href="[^"]*"', m.group(0)).group(0), 'href="/blog/"'), t)
    if fixed != t:
        f.write_text(fixed, encoding="utf-8", newline="\n")
print("  masthead anchors point at /blog/")


# root redirect
(DST / "index.html").write_text(
    '<!DOCTYPE html><html lang="en-CA"><head><meta charset="UTF-8">'
    '<title>Northern Mile Media</title>'
    f'<link rel="canonical" href="{WWW}/blog/">'
    '<meta http-equiv="refresh" content="0; url=/blog/">'
    '</head><body><p><a href="/blog/">Writing</a></p></body></html>\n',
    encoding="utf-8", newline="\n")

# sitemap + robots
urls = [f"{WWW}/blog/"] + [f"{WWW}/blog/{d.name}/" for d in sorted((DST / "blog").iterdir()) if d.is_dir()]
urls += [f"{WWW}/{s}/" for s in OLD if (DST / s).is_dir()]
sm = ['<?xml version="1.0" encoding="UTF-8"?>',
      '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'] + \
     [f"  <url><loc>{u}</loc></url>" for u in urls] + ["</urlset>"]
(DST / "sitemap.xml").write_text("\n".join(sm) + "\n", encoding="utf-8", newline="\n")
(DST / "robots.txt").write_text("User-agent: *\nAllow: /\n\nSitemap: " + WWW + "/sitemap.xml\n",
                                encoding="utf-8", newline="\n")

# verification
sample = (DST / "blog" / "index.html").read_text(encoding="utf-8")
_m = re.search('canonical" href="([^"]+)', sample)
print("  canonical   :", _m.group(1) if _m else "MISSING")
print(f"  dashboard nav links: {len(re.findall(re.escape(DASH), sample))}")
print(f"  sitemap urls: {len(urls)}")
