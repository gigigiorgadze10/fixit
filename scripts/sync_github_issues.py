"""Sync GitHub Issue titles and bodies with backlog/stories.json.

Dry-run by default; nothing changes on GitHub without --apply.
Requires the GitHub CLI (`gh auth login`) with write access to the repository.

    python scripts/sync_github_issues.py            # show the plan
    python scripts/sync_github_issues.py --apply    # update existing issues, create missing ones

Issues are matched by the "US-XX" prefix of the title. The script never deletes
issues and stops if it finds two issues for the same story. Project fields
(Status, Priority, Story Points, Sprint) are set in GitHub Projects itself.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_backlog import ROOT, load_stories, story_body  # noqa: E402

REPO = "gigigiorgadze10/fixit"
PRIORITY_LABEL = {
    "Must have": "must-have",
    "Should have": "should-have",
    "Could have": "could-have",
    "Won't have": "wont-have",
}


def gh(*args: str) -> str:
    result = subprocess.run(["gh", *args], cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
    if result.returncode != 0:
        raise SystemExit(result.stderr.strip() or "gh command failed")
    return result.stdout.strip()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    issues = json.loads(gh("issue", "list", "--repo", REPO, "--state", "all", "--limit", "500",
                           "--json", "number,title,body"))
    by_id: dict[str, list[dict]] = {}
    for issue in issues:
        m = re.match(r"^(US-\d{2})\b", issue["title"])
        if m:
            by_id.setdefault(m.group(1), []).append(issue)

    for story in load_stories():
        sid = story["id"]
        title = f"{sid}: {story['title']}"
        body = story_body(story)
        found = by_id.get(sid, [])
        if len(found) > 1:
            raise SystemExit(f"{sid}: more than one issue found, resolve manually first.")
        if found:
            issue = found[0]
            if issue["title"] == title and issue["body"].strip() == body.strip():
                print(f"OK      #{issue['number']} {sid}")
                continue
            print(f"UPDATE  #{issue['number']} {sid}")
            if args.apply:
                gh("issue", "edit", str(issue["number"]), "--repo", REPO, "--title", title, "--body", body)
        else:
            print(f"CREATE  {title}")
            if args.apply:
                gh("issue", "create", "--repo", REPO, "--title", title, "--body", body,
                   "--label", "user-story", "--label", PRIORITY_LABEL[story["priority"]])

    print("Done." if args.apply else "Dry run only. Re-run with --apply to change GitHub.")


if __name__ == "__main__":
    main()
