"""ქმნის ლეიბლებს, Issue-ებს და GitHub Projects დაფას stories.json-დან.

გამოყენება: python scripts/publish_github.py <owner/repo>
საჭიროა gh CLI, ავტორიზებული `project` scope-ით.
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STORIES = json.loads((ROOT / "backlog" / "stories.json").read_text(encoding="utf-8"))
REPO = sys.argv[1]
OWNER = REPO.split("/")[0]
PROJECT_TITLE = "FixIt Backlog"

PRIORITIES = {
    "Must have": ("must-have", "B60205", "RED"),
    "Should have": ("should-have", "D93F0B", "ORANGE"),
    "Could have": ("could-have", "FBCA04", "YELLOW"),
    "Won't have": ("wont-have", "BFBFBF", "GRAY"),
}
ROLES = {
    "მოქალაქე": "role: მოქალაქე",
    "უწყების მენეჯერი (დისპეჩერი)": "role: მენეჯერი",
    "მუნიციპალიტეტის თანამშრომელი (ბრიგადა)": "role: თანამშრომელი",
    "სისტემის ადმინისტრატორი": "role: ადმინი",
    "მერიის ხელმძღვანელობა": "role: მერია",
}
STATUSES = [
    ("Backlog", "GRAY", "ჯერ არ დაგეგმილა"),
    ("Ready (MVP)", "BLUE", "MVP-ში შემავალი, დასაწყებად მზად"),
    ("In Progress", "YELLOW", "მიმდინარეობს"),
    ("In Review", "PURPLE", "Code review და ტესტირება"),
    ("Done", "GREEN", "აკმაყოფილებს Definition of Done-ს"),
]


def gh(*args, parse=False):
    out = subprocess.run(["gh", *args], check=True, capture_output=True,
                         text=True, encoding="utf-8").stdout
    return json.loads(out) if parse else out.strip()


def graphql(query, **variables):
    args = ["api", "graphql", "-f", f"query={query}"]
    for k, v in variables.items():
        args += ["-F" if isinstance(v, int) else "-f", f"{k}={v}"]
    return gh(*args, parse=True)["data"]


def labels():
    gh("label", "create", "user-story", "-R", REPO, "-c", "0E8A16", "-d", "User Story", "--force")
    for name, color, _ in PRIORITIES.values():
        gh("label", "create", name, "-R", REPO, "-c", color, "-d", "MoSCoW", "--force")
    for name in ROLES.values():
        gh("label", "create", name, "-R", REPO, "-c", "C5DEF5", "--force")


def issues():
    existing = {i["title"]: i["url"] for i in
                gh("issue", "list", "-R", REPO, "--state", "all", "-L", "200",
                   "--json", "title,url", parse=True)}
    urls = {}
    for s in STORIES:
        title = f"{s['id']}: {s['title']}"
        if title in existing:
            urls[s["id"]] = existing[title]
            continue
        body = ROOT / "backlog" / "issues" / f"{s['id']}.md"
        urls[s["id"]] = gh("issue", "create", "-R", REPO, "-t", title, "-F", str(body),
                           "-l", "user-story", "-l", PRIORITIES[s["priority"]][0],
                           "-l", ROLES[s["role"]])
        print("issue", title)
    return urls


def project():
    found = [p for p in gh("project", "list", "--owner", OWNER, "--format", "json",
                           parse=True)["projects"] if p["title"] == PROJECT_TITLE]
    proj = found[0] if found else gh("project", "create", "--owner", OWNER, "--title",
                                      PROJECT_TITLE, "--format", "json", parse=True)
    num, pid = str(proj["number"]), proj["id"]
    subprocess.run(["gh", "project", "link", num, "--owner", OWNER, "--repo", REPO],
                   capture_output=True)
    gh("project", "edit", num, "--owner", OWNER, "--visibility", "PUBLIC",
       "--description", "FixIt: User Story-ები MoSCoW პრიორიტეტით და Story Points-ით",
       "--readme", "სრული აღწერა, Definition of Done და MVP: "
                   f"https://github.com/{REPO}#readme")

    fields = {f["name"]: f for f in gh("project", "field-list", num, "--owner", OWNER,
                                        "--format", "json", parse=True)["fields"]}
    if "Priority" not in fields:
        gh("project", "field-create", num, "--owner", OWNER, "--name", "Priority",
           "--data-type", "SINGLE_SELECT", "--single-select-options",
           ",".join(PRIORITIES))
    if "Story Points" not in fields:
        gh("project", "field-create", num, "--owner", OWNER, "--name", "Story Points",
           "--data-type", "NUMBER")

    # Status სვეტების გადარქმევა დაფისთვის
    status_id = fields["Status"]["id"]
    opts = ", ".join(f'{{name: "{n}", color: {c}, description: "{d}"}}' for n, c, d in STATUSES)
    graphql(f"mutation($id: ID!) {{ updateProjectV2Field(input: {{fieldId: $id, "
            f"singleSelectOptions: [{opts}]}}) {{ clientMutationId }} }}", id=status_id)

    # Priority-ს ფერები
    prio_id = {f["name"]: f for f in gh("project", "field-list", num, "--owner", OWNER,
                                          "--format", "json", parse=True)["fields"]}["Priority"]["id"]
    popts = ", ".join(f'{{name: "{n}", color: {c[2]}, description: ""}}' for n, c in PRIORITIES.items())
    graphql(f"mutation($id: ID!) {{ updateProjectV2Field(input: {{fieldId: $id, "
            f"singleSelectOptions: [{popts}]}}) {{ clientMutationId }} }}", id=prio_id)

    fields = {f["name"]: f for f in gh("project", "field-list", num, "--owner", OWNER,
                                        "--format", "json", parse=True)["fields"]}
    return num, pid, fields


def add_items(num, pid, fields, urls):
    opt = lambda field, name: next(o["id"] for o in fields[field]["options"] if o["name"] == name)
    for s in STORIES:
        item = gh("project", "item-add", num, "--owner", OWNER, "--url", urls[s["id"]],
                  "--format", "json", parse=True)["id"]
        status = "Ready (MVP)" if s["priority"] == "Must have" else "Backlog"
        base = ["project", "item-edit", "--id", item, "--project-id", pid]
        gh(*base, "--field-id", fields["Status"]["id"],
           "--single-select-option-id", opt("Status", status))
        gh(*base, "--field-id", fields["Priority"]["id"],
           "--single-select-option-id", opt("Priority", s["priority"]))
        gh(*base, "--field-id", fields["Story Points"]["id"], "--number", str(s["points"]))
        print("item", s["id"], status)


if __name__ == "__main__":
    labels()
    urls = issues()
    num, pid, fields = project()
    add_items(num, pid, fields, urls)
    print(f"https://github.com/users/{OWNER}/projects/{num}")
