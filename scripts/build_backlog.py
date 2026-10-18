"""stories.json-დან აგენერირებს BACKLOG.md-ს და GitHub Issue-ების ტექსტებს."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STORIES = json.loads((ROOT / "backlog" / "stories.json").read_text(encoding="utf-8"))

EPICS = {
    "EPIC-1": "პრობლემის შეტყობინება და თვალყურის დევნება (თავდაპირველი შეფასება: 13 ქულა)",
    "EPIC-2": "ბრიგადის სამუშაო პროცესი ადგილზე (თავდაპირველი შეფასება: 8 ქულა)",
}


def body(s):
    lines = [f"### User Story\n\n{s['story']}\n", "### Acceptance Criteria\n"]
    for i, (given, when, then) in enumerate(s["ac"], 1):
        lines.append(f"**სცენარი {i}**")
        lines.append(f"- **Given** {given}")
        lines.append(f"- **When** {when}")
        lines.append(f"- **Then** {then}\n")
    lines.append("### შეფასება\n")
    lines.append(f"- **როლი:** {s['role']}")
    lines.append(f"- **MoSCoW:** {s['priority']}")
    lines.append(f"- **Story Points:** {s['points']}")
    if s.get("split_from"):
        lines.append(f"- **დაშლილია:** {s['split_from']} ({EPICS[s['split_from']]})")
    if s.get("note"):
        lines.append(f"\n> {s['note']}")
    return "\n".join(lines) + "\n"


def main():
    out_dir = ROOT / "backlog" / "issues"
    out_dir.mkdir(parents=True, exist_ok=True)
    doc = ["# FixIt: სრული Product Backlog\n",
           "ფაილი დაგენერირებულია `scripts/build_backlog.py`-ით `backlog/stories.json`-დან.\n"]
    for s in STORIES:
        text = body(s)
        (out_dir / f"{s['id']}.md").write_text(text, encoding="utf-8")
        doc.append(f"## {s['id']}: {s['title']}\n\n" + text.replace("### ", "#### "))
    (ROOT / "BACKLOG.md").write_text("\n".join(doc), encoding="utf-8")


if __name__ == "__main__":
    main()
