"""Disabled legacy publisher. Do not run.

The old publisher changed Project fields using outdated names and could create
an additional Project or duplicate items. Use sync_github_issues.py in dry-run
mode first, then apply only after reviewing its output.
"""
raise SystemExit(
    "This legacy publisher is intentionally disabled. "
    "Use: python scripts/sync_github_issues.py (dry-run), then --apply if correct."
)
