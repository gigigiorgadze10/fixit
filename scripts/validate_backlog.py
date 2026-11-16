"""Check backlog/stories.json for structural and planning consistency.

Run from the repository root:
    python scripts/validate_backlog.py
"""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
stories = json.loads((ROOT / "backlog" / "stories.json").read_text(encoding="utf-8"))
by_id = {s["id"]: s for s in stories}
errors: list[str] = []

SPRINTS = ["Sprint 1", "Sprint 2", "Sprint 3", "Sprint 4", "Sprint 5"]
PRIORITIES = {"Must have", "Should have", "Could have", "Won't have"}

if len(by_id) != len(stories):
    errors.append("Duplicate Story IDs.")

for s in stories:
    sid = s["id"]
    if s.get("priority") not in PRIORITIES:
        errors.append(f"{sid}: unknown priority {s.get('priority')!r}.")
    if s.get("points") not in {1, 2, 3, 5, 8, 13}:
        errors.append(f"{sid}: Story Points must be Fibonacci (1, 2, 3, 5, 8, 13).")
    if s.get("points", 0) > 8:
        errors.append(f"{sid}: stories above 8 SP must be split.")
    if not s.get("story", "").startswith("როგორც"):
        errors.append(f"{sid}: story text must follow 'როგორც ... მსურს ... რათა ...'.")
    if not s.get("ac") or any(len(sc) != 3 or not all(str(x).strip() for x in sc) for sc in s["ac"]):
        errors.append(f"{sid}: every scenario needs Given/When/Then.")
    for dep in s.get("dependencies", []):
        if dep not in by_id:
            errors.append(f"{sid}: unknown dependency {dep}.")
    sprint = s.get("sprint")
    if sprint not in SPRINTS + ["Product Backlog"]:
        errors.append(f"{sid}: unknown sprint {sprint!r}.")
    if s["priority"] == "Must have" and sprint not in SPRINTS:
        errors.append(f"{sid}: Must have story is not planned in a sprint.")
    # a planned story may only depend on stories planned in the same or an earlier sprint
    if sprint in SPRINTS:
        for dep in s.get("dependencies", []):
            dep_sprint = by_id.get(dep, {}).get("sprint")
            if dep_sprint not in SPRINTS or SPRINTS.index(dep_sprint) > SPRINTS.index(sprint):
                errors.append(f"{sid} ({sprint}) depends on {dep} ({dep_sprint}).")

text = json.dumps(stories, ensure_ascii=False)
for ch, name in (("—", "em dash"), ("–", "en dash")):
    if ch in text:
        errors.append(f"stories.json contains an {name}.")

points = defaultdict(int)
per_sprint = defaultdict(int)
for s in stories:
    points[s["priority"]] += s["points"]
    per_sprint[s["sprint"]] += s["points"]
for sprint in SPRINTS:
    if not 5 <= per_sprint[sprint] <= 10:
        errors.append(f"{sprint}: {per_sprint[sprint]} SP is outside the planned velocity range 5-10.")

if errors:
    print("BACKLOG VALIDATION FAILED")
    for e in errors:
        print(" -", e)
    raise SystemExit(1)

print("BACKLOG VALIDATION PASSED")
print(f"Stories: {len(stories)} | Total: {sum(points.values())} SP")
for p in ["Must have", "Should have", "Could have", "Won't have"]:
    print(f"  {p}: {points[p]} SP")
for sprint in SPRINTS:
    print(f"  {sprint}: {per_sprint[sprint]} SP")
