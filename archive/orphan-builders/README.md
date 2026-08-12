# Quarantined builders

These scripts each contain a complete, independent copy of the site's HTML and
design tokens, and each writes directly to docs/. Running any of them replaces
the live site with a different design system.

They are kept for reference only. build_fuel_page.py additionally contains the
171.9 hardcoded fallback and the missing-province-becomes-zero bug that were
removed from the live pipeline in August 2026.

The live pipeline is: collector.py -> normalize.py -> build_templates.py
Nothing else should write to docs/.
