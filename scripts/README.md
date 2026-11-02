# FixIt Scripts

Run commands from the repository root (the folder containing README.md).

## 1. Requirements

- Python 3.10+ (standard library only for these scripts).
- For GitHub Issue sync only: GitHub CLI (`gh`) installed and authenticated with repository write access.

## 2. Safe migration

Preview first; no file is changed:

```powershell
py scripts/migrate_mobile_first_backlog.py
```

Apply after reviewing preview:

```powershell
py scripts/migrate_mobile_first_backlog.py --apply
```

The script backs up `backlog/stories.json` to `backlog/stories.pre-mobile-first.json` (if that backup does not already exist), preserves all other Story records/Acceptance Criteria, updates US-09/US-16/US-18 and adds US-20.

## 3. Regenerate Markdown and validate

```powershell
py scripts/build_backlog.py
py scripts/validate_backlog.py
```

Expected result: 20 Stories / 74 SP; MVP 10 Stories / 39 SP.

## 4. Sync existing GitHub Issues

First ensure `gh auth status` succeeds and that the generated `backlog/issues/US-09.md`, `US-16.md`, `US-18.md`, `US-20.md` exist.

Dry-run (no changes):

```powershell
py scripts/sync_github_issues.py
```

Apply only after checking output:

```powershell
py scripts/sync_github_issues.py --apply
```

To also add a newly created US-20 to the already existing Project #1:

```powershell
py scripts/sync_github_issues.py --apply --add-us20-to-project
```

The script never creates a Project and refuses to update if it finds duplicate Issue IDs. Afterward, manually verify Project field values and the US-20 card.

## 5. Legacy publisher warning

The old `publish_github.py` is not safe for this migration; the supplied replacement is a disabled guard. Do not run the historical publisher because it uses outdated field names and could duplicate items.
