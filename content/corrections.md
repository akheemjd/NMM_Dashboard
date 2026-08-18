# NMM Corrections Log

Newest first. Each `##` block is one correction. `status: pending` means it has
not yet been corrected in a published issue; flip it to `corrected` (and note
the issue date) once it ships. `build_brief.py` auto-injects pending entries
into the next data brief, and the writer corrects them in the next issue.

## 2026-08-12
status: corrected
what: USD/CAD rate published six weeks stale (collector read the Bank of Canada API observations oldest-first)
before: 1.4206 (dated 2026-06-29)
after: 1.3927 (dated 2026-08-11)
scope: dashboard exchange-rate module only; diesel and provincial figures unaffected
