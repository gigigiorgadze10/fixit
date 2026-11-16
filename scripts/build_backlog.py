"""Generate BACKLOG.md from backlog/stories.json (the single source of truth).

Run from the repository root:
    python scripts/build_backlog.py
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STORIES_PATH = ROOT / "backlog" / "stories.json"
PRIORITY_ORDER = ["Must have", "Should have", "Could have", "Won't have"]
SPRINT_ORDER = ["Sprint 1", "Sprint 2", "Sprint 3", "Sprint 4", "Sprint 5", "Product Backlog"]


def load_stories() -> list[dict]:
    return json.loads(STORIES_PATH.read_text(encoding="utf-8"))


def story_body(story: dict) -> str:
    """Markdown body used both in BACKLOG.md and as the GitHub Issue body."""
    lines = [f"### User Story\n\n{story['story']}\n", "### Acceptance Criteria\n"]
    for index, (given, when, then) in enumerate(story["ac"], start=1):
        lines += [
            f"**სცენარი {index}**",
            f"- **Given** {given}",
            f"- **When** {when}",
            f"- **Then** {then}\n",
        ]
    lines += [
        "### შეფასება და დაგეგმვა\n",
        f"- **როლი:** {story['role']}",
        f"- **MoSCoW:** {story['priority']}",
        f"- **Story Points:** {story['points']}",
        f"- **Sprint:** {story['sprint']}",
        f"- **პლატფორმა:** {', '.join(story.get('platform', [])) or 'არ არის'}",
        f"- **დამოკიდებულება:** {', '.join(story.get('dependencies', [])) or 'არ არის'}",
    ]
    if story.get("split_from"):
        lines.append(f"- **დაშლილია:** {story['split_from']}")
    if story.get("note"):
        lines += ["", f"> {story['note']}"]
    lines += ["", "Definition of Done: იხ. README, ნაწილი 5.5."]
    return "\n".join(lines).strip() + "\n"


def main() -> None:
    stories = load_stories()
    total = sum(s["points"] for s in stories)

    out = [
        "# FixIt: Product Backlog\n",
        "წყარო: `backlog/stories.json`. ფაილი გენერირდება ბრძანებით `python scripts/build_backlog.py`, ამიტომ ხელით არ სწორდება.\n",
        "## 1. MoSCoW შეჯამება\n",
        "| პრიორიტეტი | Story-ები | რაოდენობა | ქულა |",
        "|---|---|---:|---:|",
    ]
    for priority in PRIORITY_ORDER:
        group = [s for s in stories if s["priority"] == priority]
        ids = ", ".join(s["id"] for s in group) or "არ არის"
        out.append(f"| {priority} | {ids} | {len(group)} | {sum(s['points'] for s in group)} |")
    out.append(f"| **სულ** | | **{len(stories)}** | **{total}** |\n")

    out += [
        "## 2. სპრინტების მიხედვით\n",
        "| Sprint | Story-ები | ქულა |",
        "|---|---|---:|",
    ]
    for sprint in SPRINT_ORDER:
        group = [s for s in stories if s["sprint"] == sprint]
        if group:
            out.append(f"| {sprint} | {', '.join(s['id'] for s in group)} | {sum(s['points'] for s in group)} |")
    out.append("")

    out += [
        "## 3. ყველა Story\n",
        "| ID | სათაური | როლი | MoSCoW | SP | Sprint |",
        "|---|---|---|---|---:|---|",
    ]
    for s in stories:
        out.append(f"| {s['id']} | {s['title']} | {s['role']} | {s['priority']} | {s['points']} | {s['sprint']} |")
    out.append("")

    out.append("## 4. Story-ების დეტალები\n")
    for s in stories:
        out.append(f"### {s['id']}: {s['title']}\n")
        out.append(story_body(s).replace("### ", "#### "))

    (ROOT / "BACKLOG.md").write_text("\n".join(out), encoding="utf-8")
    print(f"BACKLOG.md generated: {len(stories)} stories, {total} SP.")


if __name__ == "__main__":
    main()
