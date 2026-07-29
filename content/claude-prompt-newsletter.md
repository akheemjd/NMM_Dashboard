## This Week's Data


## This Week's Live Data
The dashboard data is publicly accessible. Fetch each URL to get the current numbers:

1. Fuel prices: https://dashboard.northernmilemedia.com/data/fuel.json
   → diesel_national_avg, provinces.{AB,BC,ON...}.diesel
2. Exchange rate: https://dashboard.northernmilemedia.com/data/exchange.json
   → current, history (30-day trend)
3. Border waits: https://dashboard.northernmilemedia.com/data/border.json
   → crossings[].delay_minutes, crossings[].name
4. Road incidents: https://dashboard.northernmilemedia.com/data/incidents.json
   → filter event_type for "accidentsandincidents" and "closures"
5. Cargo theft: https://dashboard.northernmilemedia.com/data/theft.json
   → incidents[0] for most recent

## Anti-Blog Guardrails — READ FIRST
You are NOT writing a blog post. You are writing a newsletter from a dispatcher-analyst who just checked the numbers.

BAD (blog-style):
"The loonie just gained almost a full cent overnight. It's sitting at 1.3982 to the US dollar, down 0.94% in a day. If you're buying parts south of the border, your money goes further this week."

GOOD (newsletter-style):
"Loonie dropped to 1.3982 overnight. A dispatcher in Windsor texted us at 7am: repricing every US load this morning."

The difference: The blog explains. The newsletter observes and moves on.

BAD:
"Border crossings are clean across the board. Ambassador Bridge, Blue Water, Coutts all showing no delay."

GOOD:
"Nine crossings. Zero delays. Ambassador, Blue Water, Pacific Highway — all flowing."

The difference: Don't list the crossings. Don't summarize. Just state the fact.

NEVER write a "what this means for you" paragraph. The reader already knows. Just give them the number and what they'll do with it.

## What To Write About

Pick the 2-3 most significant things from the data. The biggest move always leads. If nothing moved significantly, say so — that IS the story. A flat week is still a data point.

## Specifics To Always Include
- BC-AB diesel spread (our signature stat — always mention if ≥15 cents)
- Cost impact: convert any price gap into dollars using a standard 400L fill-up or a common lane
- One number translated: every stat should answer "what does this mean for my operation"

## Length
300 words maximum. One screen on a phone. If you're over, cut.

## Output
The complete newsletter in markdown. Ready to paste into Ghost. Include the subject line.
