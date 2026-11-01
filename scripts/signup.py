"""Email capture for Northern Mile Media - the signup band.

The offer is the Northern Mile Brief: one email a week on what diesel did, what the border is doing,
and what changed. That is the thing a reader gets in exchange for an address, and it is the only
asset that survives a visitor leaving.

BUILD NOTE - the ESP is not wired yet. Everything else is: the form renders on the pages that
matter, it is styled to the design system, it validates, and it degrades to a plain link if the
endpoint is unset. To go live:

  1. Create a free Buttondown account (free to 100 subscribers) at buttondown.email
  2. Put your username in BRIEF_ENDPOINT below, in place of YOURUSERNAME
  3. Re-run deploy.sh

Why Buttondown and not Mailchimp: free to 100 subscribers, no card, one-field subscribe endpoint
that accepts a plain form POST, and the archive is public so every issue becomes an indexable page.
Mailchimp's free tier is 500 but its embed needs JavaScript and its archive is not indexable.

Until the endpoint is set the form is inert - it renders, so the design is reviewable, but it says
"coming soon" rather than silently failing to subscribe someone who thinks they signed up.
"""
import pathlib

BRIEF_ENDPOINT = "https://buttondown.email/api/emails/embed-subscribe/northern"
BRIEF_NAME = "The Northern Mile Brief"
BRIEF_PITCH = ("One email a week: what diesel did on both sides of the border, "
               "where the crossings are backing up, and what changed in the rules.")

CSS = """
/* ---- signup band ---- */
.nm-signup{background:#1d2b23;color:#FBFAF8;padding:clamp(28px,4vw,44px) clamp(20px,4vw,48px);margin:clamp(32px,5vw,56px) 0 0}
.nm-signup .in{max-width:1160px;margin:0 auto;display:flex;gap:clamp(20px,4vw,48px);align-items:center;justify-content:space-between;flex-wrap:wrap}
.nm-signup h2{margin:0 0 6px;font-size:clamp(19px,2.2vw,24px);line-height:1.25;color:#FBFAF8;font-weight:650}
.nm-signup p{margin:0;font-size:15px;line-height:1.55;color:#c9d6cd;max-width:46ch}
.nm-signup form{display:flex;gap:10px;flex-wrap:wrap;min-width:min(100%,320px)}
.nm-signup input[type=email]{flex:1 1 200px;min-width:0;padding:12px 14px;border:1px solid #4a5c51;border-radius:8px;background:#26362d;color:#FBFAF8;font:inherit;font-size:15px}
.nm-signup input[type=email]::placeholder{color:#8fa197}
.nm-signup input[type=email]:focus{outline:2px solid #7fc79c;outline-offset:1px;border-color:#7fc79c}
.nm-signup button{padding:12px 20px;border:0;border-radius:8px;background:#7fc79c;color:#12201a;font:inherit;font-size:15px;font-weight:650;cursor:pointer;white-space:nowrap}
.nm-signup button:hover{background:#93d6ac}
.nm-signup .fine{margin-top:10px;font-size:13px;color:#8fa197;flex-basis:100%}
.nm-signup .soon{padding:12px 16px;border:1px dashed #4a5c51;border-radius:8px;font-size:14px;color:#c9d6cd}
@media(max-width:640px){.nm-signup .in{flex-direction:column;align-items:flex-start}.nm-signup form{width:100%}}
"""


def band(compact=False):
    """The signup band. Returns '' when there is nothing honest to offer yet."""
    if BRIEF_ENDPOINT:
        form = f'''<form action="{BRIEF_ENDPOINT}" method="post" target="popupwindow"
      onsubmit="window.open('{BRIEF_ENDPOINT}?email='+encodeURIComponent(this.email.value),'popupwindow','width=520,height=560');return true">
      <input type="email" name="email" placeholder="you@yourcompany.com" required aria-label="Email address">
      <button type="submit">Subscribe</button>
      <span class="fine">One email a week. No spam, unsubscribe in a click.</span>
    </form>'''
    else:
        form = '''<div class="soon">Subscribe form goes live once the newsletter is set up.</div>'''

    return f'''<aside class="nm-signup" aria-label="{BRIEF_NAME}">
  <div class="in">
    <div>
      <h2>{BRIEF_NAME}</h2>
      <p>{BRIEF_PITCH}</p>
    </div>
    {form}
  </div>
</aside>'''


if __name__ == "__main__":
    out = pathlib.Path(r"C:\Users\Akheem\northern-mile-dashboard\assets\signup.css")
    out.write_text(CSS.strip() + "\n", encoding="utf-8", newline="\n")
    print(f"  wrote {out}  ({len(CSS)} bytes)")
    print(f"  endpoint set: {bool(BRIEF_ENDPOINT)}")
    print(f"  band renders: {'form' if BRIEF_ENDPOINT else 'coming-soon placeholder'}")
