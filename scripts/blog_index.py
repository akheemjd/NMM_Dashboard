"""Rebuild the blog index as an editorial page instead of a card grid.

What was wrong: twenty identical white rounded cards in two columns. Nothing was more important than
anything else, no data was visible, no type contrast, no brand colour. It read as a Material settings
screen, which is exactly the "Think Android" reaction.

What this does instead:

  * MASTHEAD    serif display type at real scale, with a rule. Sets a publication tone immediately.
  * HERO        the newest piece runs full width at 40px serif, with its key number pulled out as a
                figure. One story is allowed to dominate.
  * THE LIST    everything else is a ruled list, not cards. Date column, category, headline. Hairline
                separators, no boxes, no rounded corners. Denser, faster to scan, and it stops
                pretending every post is equally important.
  * ACCENT      one green used deliberately: the rule under the masthead, the category labels, the
                hero figure. Not decoration, a wayfinding signal.

Same markup contract, so the nav, footer, signup band and canonical logic are untouched.
"""
import pathlib

CSS = """
/* ============ editorial blog index ============ */

.nm-mast{padding:clamp(28px,5vw,56px) 0 clamp(18px,2.5vw,28px);border-bottom:3px solid #1d2b23}
.nm-mast h1{font-family:'Source Serif 4',Georgia,serif;font-size:clamp(40px,7vw,76px);line-height:0.98;
  letter-spacing:-0.02em;margin:0 0 14px;font-weight:600;color:#12201a}
.nm-mast .dek{font-size:clamp(15px,1.6vw,18px);line-height:1.5;color:#4a5c51;max-width:62ch;margin:0}
.nm-mast .dek b{color:#1d2b23;font-weight:600}

/* hero */
.nm-hero{display:block;text-decoration:none;color:inherit;padding:clamp(26px,4vw,44px) 0;
  border-bottom:1px solid #d8ded9;transition:background .15s}
.nm-hero:hover{background:#F5F8F4}
.nm-kicker{display:flex;gap:10px;align-items:center;font-family:'Overpass',system-ui,sans-serif;
  font-size:11px;font-weight:700;letter-spacing:.14em;text-transform:uppercase;color:#25663f;margin-bottom:14px}
.nm-kicker i{font-style:normal;color:#8fa197;font-weight:500;letter-spacing:.08em}
.nm-hero h2{font-family:'Source Serif 4',Georgia,serif;font-size:clamp(26px,3.6vw,42px);line-height:1.1;
  letter-spacing:-0.015em;margin:0 0 14px;font-weight:600;color:#12201a;max-width:26ch}
.nm-hero p{margin:0;font-size:clamp(15px,1.5vw,17px);line-height:1.55;color:#4a5c51;max-width:58ch}
.nm-hero .go{display:inline-block;margin-top:16px;font-family:'Overpass',system-ui,sans-serif;
  font-size:13px;font-weight:700;letter-spacing:.04em;color:#25663f}

/* the ruled list */
.nm-list{margin:0;padding:0;list-style:none}
.nm-list li{border-bottom:1px solid #e2e7e3}
.nm-list a{display:grid;grid-template-columns:132px 1fr;gap:clamp(12px,2vw,28px);
  padding:clamp(16px,2.2vw,24px) 0;text-decoration:none;color:inherit}
.nm-list a:hover .hl{color:#25663f}
.nm-list .when{font-family:'Overpass',system-ui,sans-serif;font-size:12px;letter-spacing:.05em;
  color:#7c8f84;padding-top:4px;text-transform:uppercase}
.nm-list .cat{display:block;color:#25663f;font-weight:700;font-size:10.5px;letter-spacing:.12em;margin-bottom:5px}
.nm-list .hl{font-family:'Source Serif 4',Georgia,serif;font-size:clamp(18px,2.1vw,22px);line-height:1.25;
  font-weight:600;color:#12201a;margin:0 0 7px;transition:color .12s;letter-spacing:-0.01em}
.nm-list .blurb{margin:0;font-size:14.5px;line-height:1.5;color:#5d6f64;max-width:70ch}
.nm-secttl{font-family:'Overpass',system-ui,sans-serif;font-size:11px;font-weight:700;letter-spacing:.16em;
  text-transform:uppercase;color:#7c8f84;padding:clamp(22px,3vw,34px) 0 0}

@media(max-width:680px){
  .nm-list a{grid-template-columns:1fr;gap:6px}
  .nm-list .when{padding-top:0}
  .nm-hero h2{max-width:none}
}
"""


def build_index_markup(posts, clean, human_date, escape):
    """Return the inner body HTML for /blog/."""
    lead, rest = posts[0], posts[1:]

    hero = f"""    <a class="nm-hero" href="/blog/{escape(lead['slug'])}/">
      <div class="nm-kicker">{escape(lead['category'])} <i>{human_date(lead['date'])}</i></div>
      <h2>{escape(lead['title'])}</h2>
      <p>{escape(clean(lead))}</p>
      <span class="go">Read the piece &rarr;</span>
    </a>"""

    rows = []
    for p in rest:
        rows.append(f"""      <li><a href="/blog/{escape(p['slug'])}/">
        <span class="when">{human_date(p['date'])}</span>
        <span><span class="cat">{escape(p['category'])}</span>
        <span class="hl">{escape(p['title'])}</span>
        <p class="blurb">{escape(clean(p))}</p></span>
      </a></li>""")

    return f"""
  <section class="sec">
    <div class="nm-mast">
      <h1>Writing</h1>
      <p class="dek"><b>{len(posts)} pieces</b> on cross-border trucking, built from published figures.
      Every number names its source at the foot of the page. No press releases, no sponsored copy.</p>
    </div>
{hero}
    <div class="nm-secttl">Also this month</div>
    <ul class="nm-list">
{chr(10).join(rows)}
    </ul>
  </section>
"""


if __name__ == "__main__":
    out = pathlib.Path(r"C:\Users\Akheem\northern-mile-dashboard\assets\blog.css")
    t = out.read_text(encoding="utf-8")
    if ".nm-mast" not in t:
        out.write_text(t.rstrip() + "\n\n" + CSS.strip() + "\n", encoding="utf-8", newline="\n")
        print(f"  appended editorial index CSS to blog.css ({len(CSS)} bytes)")
    else:
        print("  CSS already present")
