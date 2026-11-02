"""Safely sync changed FixIt issue bodies using GitHub CLI.

Default is dry-run. Requires `gh auth login` and repository write access.
Run from repo root:
  python scripts/sync_github_issues.py
  python scripts/sync_github_issues.py --apply
  python scripts/sync_github_issues.py --apply --add-us20-to-project

Updates existing US-09, US-16, US-18 issues by ID; creates US-20 only if absent.
Never creates a new Project and never deletes an Issue.
"""
from __future__ import annotations
import argparse
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = "gigigiorgadze10/fixit"
OWNER = "gigigiorgadze10"
PROJECT_NUMBER = "1"
SYNC_IDS = {"US-09", "US-16", "US-18", "US-20"}


def gh(*args: str, json_output: bool = False):
    result = subprocess.run(["gh", *args], cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or "gh command failed")
    output = result.stdout.strip()
    return json.loads(output) if json_output and output else output


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="actually update/create GitHub Issues")
    parser.add_argument("--add-us20-to-project", action="store_true", help="also add newly found/created US-20 to Project #1")
    args = parser.parse_args()

    issues = gh("issue", "list", "--repo", REPO, "--state", "all", "--limit", "500",
                "--json", "number,title,url,labels", json_output=True)
    by_id = {}
    for issue in issues:
        match = re.match(r"^(US-\d{2})\b", issue.get("title", ""))
        if match:
            by_id.setdefault(match.group(1), []).append(issue)

    for story_id in sorted(SYNC_IDS):
        body_path = ROOT / "backlog" / "issues" / f"{story_id}.md"
        if not body_path.exists():
            raise SystemExit(f"Missing generated Issue body: {body_path.relative_to(ROOT)}. Run build_backlog.py first.")
        matches = by_id.get(story_id, [])
        if len(matches) > 1:
            raise SystemExit(f"Found more than one GitHub Issue for {story_id}; resolve duplicates manually before syncing.")
        story_json = json.loads((ROOT / "backlog" / "stories.json").read_text(encoding="utf-8"))
        story = next(s for s in story_json if s["id"] == story_id)
        title = f"{story_id}: {story['title']}"
        if matches:
            issue = matches[0]
            print(f"UPDATE {issue['url']} -> {title}")
            if args.apply:
                gh("issue", "edit", str(issue["number"]), "--repo", REPO,
                   "--title", title, "--body-file", str(body_path))
                if story_id == "US-18":
                    labels = {label["name"] for label in issue.get("labels", [])}
                    if "wont-have" in labels:
                        gh("issue", "edit", str(issue["number"]), "--repo", REPO, "--remove-label", "wont-have")
                    if "must-have" not in labels:
                        gh("issue", "edit", str(issue["number"]), "--repo", REPO, "--add-label", "must-have")
        else:
            print(f"CREATE {title}")
            if args.apply:
                url = gh("issue", "create", "--repo", REPO, "--title", title,
                         "--body-file", str(body_path), "--label", "user-story", "--label",
                         "could-have" if story["priority"] == "Could have" else "must-have")
                print(f"Created: {url}")
                if story_id == "US-20" and args.add_us20_to_project:
                    gh("project", "item-add", PROJECT_NUMBER, "--owner", OWNER, "--url", url)

    if not args.apply:
        print("DRY RUN complete. No GitHub data changed. Re-run with --apply after checking the plan.")
    else:
        print("Issue sync completed. Review Project #1 fields and add/update Project items if needed.")


if __name__ == "__main__":
    main()
