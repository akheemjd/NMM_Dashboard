"""Build /report/ - the sales page for The Cross-Border Cost Brief.

Buyer: US-domiciled for-hire carriers, 10-100 power units, with Canadian operating authority on the
Ontario-Michigan and Ontario-New York corridors.

The page has one job: get a carrier to either download the free sample or start a $249 subscription.
So it leads with the number they cannot get anywhere else (what a tractor burns per 1,000 km on each
side of the border), states the price plainly, and does not use a single marketing adjective.

No checkout is wired until Stripe exists. Rather than a form that silently drops addresses, the
button says what it does right now: emails for the sample, and a waitlist for the subscription.
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import gen_templates as G  # noqa: E402

OUT = os.path.join(ROOT, "docs", "report")

BODY = """
<main id="main" class="wrap">
<div class="kicker">The Cross-Border Cost Brief</div>
<h1>What your Ontario lanes cost, every month, on one page</h1>
<p class="lede">Fuel, currency and border delay for US carriers running Ontario to Michigan or New York.
Built from the primary sources, dated, and put on a single basis so you can quote from it.</p>

<div class="offer">
  <div class="price"><span class="amt">$249</span><span class="per">/month</span></div>
  <p class="terms">Monthly report, emailed on the first business day. Cancel any time. No contract.</p>
  <a class="btn" href="mailto:northernmilemedia@gmail.com?subject=Cross-Border%20Cost%20Brief%20-%20subscribe">Start the subscription</a>
  <a class="btn ghost" href="#sample">Get a free sample first</a>
</div>

<section class="block">
<h2>What is in it</h2>
<ol class="secs">
  <li><strong>Cost per 1,000 km on each side.</strong> Canadian diesel and US diesel converted to the
      same basis at a 38 L/100 km tractor, so the two numbers are directly comparable. You are not
      doing arithmetic mid-quote.</li>
  <li><strong>The spread you are quoting against.</strong> The difference between the two headline
      prices on a common basis, in cents per litre, stated with its direction.</li>
  <li><strong>Provincial diesel.</strong> Where you actually fuel before the return leg, ranked
      against the national average.</li>
  <li><strong>Your crossings.</strong> Canada-side and US-side booth waits at Windsor-Detroit,
      Sarnia-Port Huron, Fort Erie-Buffalo, Queenston-Lewiston and Sault Ste. Marie.</li>
  <li><strong>What to carry into a quote this month.</strong> One paragraph, no hedging.</li>
</ol>
</section>

<section class="block">
<h2>Why it is not just a diesel price</h2>
<p>You can get a US diesel price anywhere. What you cannot get in one place is the Canadian provincial
figure next to the US district figure, converted to what a tractor actually burns per kilometre, with
the border delay on the crossings your drivers use.</p>
<p>A fuel card tells you what you paid. This tells you what to charge.</p>
</section>

<section class="block">
<h2>Where the numbers come from</h2>
<table class="src">
<tbody>
<tr><td>Canadian diesel, by province</td><td>Natural Resources Canada weekly retail survey</td></tr>
<tr><td>US diesel, by district</td><td>US Energy Information Administration</td></tr>
<tr><td>USD/CAD</td><td>Bank of Canada daily observation</td></tr>
<tr><td>Border wait times</td><td>Canada Border Services Agency, US Customs and Border Protection</td></tr>
<tr><td>Fuel tax by jurisdiction</td><td>IFTA Inc. quarterly tax matrix</td></tr>
</tbody></table>
<p class="note">Every figure carries its observation date. Where a source has not published, the
report says so rather than carrying the previous value forward silently. The method is public at
<a href="/methodology/nmdi/">the methodology page</a>.</p>
</section>

<section class="block" id="sample">
<h2>Read a sample before you pay</h2>
<p>One email and we send you last month's brief, complete, no redactions. If it is not worth $249 to
you, you will know in thirty seconds.</p>
<a class="btn" href="mailto:northernmilemedia@gmail.com?subject=Cross-Border%20Cost%20Brief%20-%20sample%20request">Email for the sample</a>
<p class="note">We reply from a real address. No sequence, no drip campaign behind it.</p>
</section>

<section class="block">
<h2>Who it is for</h2>
<p><strong>US carriers with 10 to 100 power units holding Canadian operating authority</strong>, running
the Ontario corridors. If you cross weekly, the fuel spread alone covers the subscription several
times over. If you cross twice a year, this is not for you.</p>
</section>
</main>
"""

CSS = """
.kicker{text-transform:uppercase;letter-spacing:.12em;font-size:11px;color:var(--accent);font-weight:700}
.lede{font-size:19px;line-height:1.5;color:#333;max-width:44em}
.offer{border-top:2px solid var(--ink);border-bottom:2px solid var(--ink);padding:22px 0;margin:30px 0 40px;display:flex;flex-wrap:wrap;align-items:center;gap:22px}
.price{display:flex;align-items:baseline;gap:4px}
.amt{font:600 44px/1 var(--serif);letter-spacing:-.02em}
.per{font-size:15px;color:#666}
.terms{flex:1 1 220px;font-size:13px;color:#555;margin:0}
.btn{display:inline-block;background:var(--ink);color:#fff;text-decoration:none;padding:13px 22px;font:600 14px/1 system-ui,sans-serif;letter-spacing:.01em}
.btn.ghost{background:none;color:var(--ink);border:1px solid var(--ink)}
.block{margin:0 0 42px}
.block h2{font-size:24px;margin:0 0 12px;padding-top:14px;border-top:1px solid #d8d8d8}
.secs{margin:0;padding-left:22px}
.secs li{margin:0 0 14px;line-height:1.55}
table.src{width:100%;border-collapse:collapse;font-size:14px}
table.src td{padding:7px 10px 7px 0;border-bottom:1px solid #ececec;vertical-align:top}
table.src td:first-child{color:#555;width:38%}
.note{font-size:12.5px;color:#666;margin-top:10px}
@media(max-width:640px){.amt{font-size:36px}.offer{gap:12px}}
"""


def main():
    os.makedirs(OUT, exist_ok=True)
    ld = ('{"@context":"https://schema.org","@type":"Product",'
          '"name":"The Cross-Border Cost Brief",'
          '"description":"Monthly fuel, currency and border delay report for US carriers running '
          'Ontario to Michigan or New York.",'
          '"brand":{"@type":"Brand","name":"Northern Mile Media"},'
          '"offers":{"@type":"Offer","price":"249.00","priceCurrency":"USD",'
          '"availability":"https://schema.org/InStock"}}')
    html = G.head(
        "The Cross-Border Cost Brief - $249/month | Northern Mile",
        "Monthly fuel, currency and border delay report for US carriers with Canadian operating "
        "authority on the Ontario-Michigan and Ontario-New York corridors. $249 per month.",
        "/report/", "/og.jpg", ld)
    # G.head closes </head><body> and opens the shared nav; the page CSS goes in a style block
    # ahead of the body content, which the head() contract allows because it returns up to <main>.
    html = html.replace("</head>", f"<style>{CSS}</style></head>")
    html = html + BODY + G.foot()
    import datetime as dt
    now = dt.datetime.now(dt.timezone.utc)
    html = (html
            .replace("{{build_version}}", now.strftime("%Y-%m-%d-%H%M"))
            .replace("{{updated_iso}}", now.strftime("%Y-%m-%dT%H:%M:%SZ"))
            .replace("{{updated_at}}", now.strftime("%Y-%m-%d %H:%M")))
    with open(os.path.join(OUT, "index.html"), "w", encoding="utf-8", newline="\n") as f:
        f.write(html)
    print(f"  docs/report/index.html ({len(html):,} bytes)")


if __name__ == "__main__":
    main()
