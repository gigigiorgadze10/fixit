"""Validate the expected FixIt Mobile-First Story count, MoSCoW totals and AC."""
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
path = ROOT / "backlog" / "stories.json"
stories = json.loads(path.read_text(encoding="utf-8"))
errors = []
ids = [s.get("id") for s in stories]
if len(ids) != len(set(ids)):
    errors.append("Duplicate Story IDs found.")
if len(stories) != 20:
    errors.append(f"Expected 20 stories, found {len(stories)}.")

count = Counter(s.get("priority") for s in stories)
points = defaultdict(int)
for s in stories:
    points[s.get("priority")] += int(s.get("points", 0))
    if not s.get("story"):
        errors.append(f"{s.get('id')}: missing User Story text.")
    ac = s.get("ac")
    if not isinstance(ac, list) or not ac:
        errors.append(f"{s.get('id')}: missing Acceptance Criteria.")
    else:
        for idx, item in enumerate(ac, 1):
            if not isinstance(item, list) or len(item) != 3 or not all(str(v).strip() for v in item):
                errors.append(f"{s.get('id')}: invalid Given/When/Then scenario {idx}.")
    if int(s.get("points", 0)) not in {1, 2, 3, 5, 8, 13}:
        errors.append(f"{s.get('id')}: Story Points not in Fibonacci scale.")

expected = {
    "Must have": (10, 39),
    "Should have": (5, 16),
    "Could have": (4, 16),
    "Won't have": (1, 3),
}
for priority, (expected_count, expected_points) in expected.items():
    actual = (count[priority], points[priority])
    if actual != (expected_count, expected_points):
        errors.append(f"{priority}: expected {(expected_count, expected_points)}, found {actual}.")

if errors:
    print("BACKLOG VALIDATION FAILED:")
    for error in errors:
        print(f"- {error}")
    raise SystemExit(1)

print("BACKLOG VALIDATION PASSED")
print(f"Stories: {len(stories)} | Total: {sum(int(s['points']) for s in stories)} SP")
print(f"MVP: {count['Must have']} stories / {points['Must have']} SP")
for priority in expected:
    print(f"{priority}: {count[priority]} stories / {points[priority]} SP")
