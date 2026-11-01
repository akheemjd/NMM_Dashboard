#!/usr/bin/env python3
"""Buttondown list status - subscriber count, recent signups, and send readiness.

Reads the API key from ~/.hermes/buttondown.env so it never lives in the repo. Kept small on
purpose: the useful question is "is the list growing and can it receive mail", not a dashboard.

    python scripts/newsletter_status.py
"""
import json
import os
import pathlib
import urllib.error
import urllib.request

ENV = pathlib.Path.home() / ".hermes" / "buttondown.env"
API = "https://api.buttondown.email/v1"


def key():
    if not ENV.exists():
        raise SystemExit(f"  no key at {ENV}")
    for line in ENV.read_text(encoding="utf-8").splitlines():
        if line.startswith("BUTTONDOWN_API_KEY="):
            return line.split("=", 1)[1].strip()
    raise SystemExit("  BUTTONDOWN_API_KEY missing from the env file")


def call(path, k):
    req = urllib.request.Request(f"{API}{path}", headers={"Authorization": f"Token {k}"})
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        return {"error": e.code, "body": e.read().decode("utf-8", "replace")[:200]}


def main():
    k = key()
    subs = call("/subscribers?page=1", k)
    if "error" in subs:
        raise SystemExit(f"  API error {subs['error']}: {subs['body']}")

    rows = subs.get("results", [])
    confirmed = [s for s in rows if s.get("confirmed") or s.get("status") == "regular"]
    pending = [s for s in rows if s.get("status") == "unactivated"]

    print(f"SUBSCRIBERS   {subs.get('count', len(rows))}")
    print(f"  active      {len(confirmed)}")
    print(f"  pending     {len(pending)}  (double opt-in not yet confirmed)")

    if rows:
        print("\nMOST RECENT:")
        for s in sorted(rows, key=lambda x: x.get("creation_date") or "")[-8:]:
            print(f"  {s.get('creation_date','?')[:10]}  {s.get('source','?'):16} "
                  f"{s.get('status','?'):12} {s.get('email_address','?')}")

    emails = call("/emails?page=1", k)
    if "error" not in emails:
        sent = emails.get("results", [])
        print(f"\nEMAILS SENT   {len(sent)}")
        for e in sent[:3]:
            print(f"  {e.get('publish_date','draft')[:10]}  {e.get('subject','(no subject)')[:60]}")

    n = subs.get("count", len(rows))
    print("\nREADINESS")
    print(f"  {'OK  ' if n else 'WAIT'}  capture wired and receiving")
    print(f"  {'OK  ' if n else 'WAIT'}  {'list has someone to send to' if n else 'no subscribers yet, nothing to send'}")
    print("  ---  first issue goes out once there is a confirmed subscriber")


if __name__ == "__main__":
    main()
