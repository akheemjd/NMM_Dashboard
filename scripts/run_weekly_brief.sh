#!/usr/bin/env bash
# Send The Northern Mile Brief. Silent on success.
#
# The subscribe page promises "Every Wednesday, 6am". This is what keeps that
# promise. It stays quiet when it works and only speaks up when it does not,
# matching how the deploy cron behaves.
#
# Exit 0 with no output  -> job succeeded, nothing to report
# Non-zero with output   -> something broke, and you will see why

set -uo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO" || { echo "NMM brief: cannot cd to $REPO"; exit 1; }

PY="${PYTHON:-python}"

OUT="$("$PY" scripts/send_weekly_brief.py --send 2>&1)"
CODE=$?

# The double-send guard firing is the system working, not failing. It exits
# non-zero to stop the pipeline, so without this branch a correctly-refused
# second send would raise a false alarm every time the cron ran twice.
if echo "$OUT" | grep -q "already exists"; then
  exit 0
fi

if [ $CODE -ne 0 ]; then
  echo "NMM BRIEF FAILED (exit $CODE)"
  echo "$OUT" | tail -30
  exit 1
fi

# A successful run should have actually dispatched an email. If the script
# published but no email went out, that is the dangerous silent failure this
# whole two-step design exists to catch, so treat it as a failure here too.
if ! echo "$OUT" | grep -q "email dispatched"; then
  echo "NMM BRIEF: published but NO EMAIL WAS DISPATCHED"
  echo "$OUT" | tail -20
  exit 1
fi

# Success. Stay silent.
exit 0
