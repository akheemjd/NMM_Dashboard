#!/usr/bin/env python3
"""Audit what the NMM Ghost Admin API key can access. READ-ONLY PROBES ONLY.

Every request in here is a GET. Nothing is created, modified, or deleted.
The goal is to enumerate the real blast radius of the stored credential.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ghost_publish import api_call, GHOST_SITE, _load_dotenv

_load_dotenv()

# resource -> (endpoint, how to summarise the response)
PROBES = [
    ("posts",      "posts/?limit=1",                     lambda d: f"{d.get('meta',{}).get('pagination',{}).get('total','?')} posts"),
    ("pages",      "pages/?limit=1",                     lambda d: f"{d.get('meta',{}).get('pagination',{}).get('total','?')} pages"),
    ("tags",       "tags/?limit=1",                      lambda d: f"{d.get('meta',{}).get('pagination',{}).get('total','?')} tags"),
    ("users",      "users/?limit=1",                     lambda d: f"{d.get('meta',{}).get('pagination',{}).get('total','?')} staff users"),
    ("members",    "members/?limit=1",                   lambda d: f"{d.get('meta',{}).get('pagination',{}).get('total','?')} subscribers"),
    ("newsletters","newsletters/?limit=1",               lambda d: f"{len(d.get('newsletters',[]))} newsletters"),
    ("tiers",      "tiers/?limit=1",                     lambda d: f"{len(d.get('tiers',[]))} subscription tiers"),
    ("offers",     "offers/?limit=1",                    lambda d: f"{len(d.get('offers',[]))} offers"),
    ("settings",   "settings/?group=site",               lambda d: f"{len(d.get('settings',[]))} site settings readable"),
    ("themes",     "themes/",                            lambda d: f"{len(d.get('themes',[]))} themes installed"),
    ("webhooks",   "webhooks/?limit=1",                  lambda d: f"{len(d.get('webhooks',[]))} webhooks"),
    ("integrations","integrations/?limit=1",             lambda d: f"{len(d.get('integrations',[]))} integrations (API keys!)"),
    ("roles",      "roles/?limit=1",                     lambda d: f"{len(d.get('roles',[]))} roles"),
    ("labels",     "labels/?limit=1",                    lambda d: f"{len(d.get('labels',[]))} member labels"),
    ("redirects",  "redirects/download/",                lambda d: f"{str(d)[:60]}"),
    ("db/backup",  "db/",                                lambda d: f"{str(d)[:60]}"),
]

print(f"Auditing Ghost Admin API key scope")
print(f"Host: {GHOST_SITE}")
print("=" * 62)

readable = []
blocked = []

for name, endpoint, summary in PROBES:
    try:
        result = api_call("GET", endpoint, retries=1)
        try:
            desc = summary(result)
        except Exception:
            desc = f"{len(str(result))} bytes"
        print(f"  READ  [{name:13}] {desc}")
        readable.append(name)
    except Exception as e:
        msg = str(e).split("\n")[0][:60]
        print(f"  DENY  [{name:13}] {msg}")
        blocked.append(name)

print()
print("=" * 62)
print(f"READABLE: {len(readable)}")
print(f"DENIED:   {len(blocked)}")
