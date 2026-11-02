"""Safely migrates an existing FixIt stories.json to the Mobile-First scope.

Run from repository root:
  python scripts/migrate_mobile_first_backlog.py          # dry-run
  python scripts/migrate_mobile_first_backlog.py --apply  # write changes

Only US-09, US-16, US-18 are updated; US-20 is added if missing.
All other Story records and their Acceptance Criteria are preserved.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
STORIES_FILE = ROOT / "backlog" / "stories.json"
BACKUP_FILE = ROOT / "backlog" / "stories.pre-mobile-first.json"

PLATFORMS = {
    "US-01": ["mobile-app", "backend-api"],
    "US-02": ["mobile-app", "backend-api", "file-storage"],
    "US-03": ["mobile-app", "backend-api", "database"],
    "US-04": ["mobile-app", "backend-api"],
    "US-05": ["mobile-app", "backend-api"],
    "US-06": ["mobile-app", "web-dashboard", "backend-api"],
    "US-07": ["mobile-app", "web-dashboard", "backend-api"],
    "US-08": ["web-dashboard", "backend-api"],
    "US-09": ["web-dashboard", "backend-api", "database"],
    "US-10": ["web-dashboard", "backend-api"],
    "US-11": ["mobile-app", "backend-api"],
    "US-12": ["mobile-app", "backend-api", "file-storage"],
    "US-13": ["web-dashboard", "backend-api"],
    "US-14": ["web-dashboard", "backend-api"],
    "US-15": ["web-dashboard", "backend-api", "database"],
    "US-16": ["mobile-app", "web-dashboard", "backend-api"],
    "US-17": ["mobile-app", "backend-api"],
    "US-18": ["mobile-app"],
    "US-19": ["mobile-app", "backend-api"],
    "US-20": ["mobile-app", "web-dashboard", "backend-api"],
}

DEPENDENCIES = {
    "US-01": ["US-18"],
    "US-02": ["US-01", "US-18"],
    "US-03": ["US-02"],
    "US-04": ["US-01", "US-02"],
    "US-05": ["US-04"],
    "US-06": ["US-02"],
    "US-07": ["US-06"],
    "US-08": [],
    "US-09": ["US-08", "US-13"],
    "US-10": ["US-08"],
    "US-11": ["US-09", "US-18"],
    "US-12": ["US-11"],
    "US-13": [],
    "US-14": ["US-13"],
    "US-15": ["US-08", "US-09"],
    "US-16": ["US-04", "US-12"],
    "US-17": [],
    "US-18": [],
    "US-19": ["US-01"],
    "US-20": ["US-04", "US-08", "US-12"],
}

UPDATES = {
    "US-09": {
        "title": "შეტყობინების მიღება და თანამშრომელზე მინიჭება/გადანაწილება",
        "role": "უწყების მენეჯერი (დისპეჩერი)",
        "story": "როგორც **უწყების მენეჯერი**, მსურს ახალი განაცხადის პასუხისმგებელ თანამშრომელზე მინიჭება და სამუშაოს დაწყებამდე საჭიროების შემთხვევაში სხვა თანამშრომელზე გადანაწილება, რათა თითოეულ განაცხადს ჰყავდეს პასუხისმგებელი პირი და მინიჭებების ისტორია შენარჩუნდეს.",
        "ac": [
            ["განაცხადი სტატუსით New არის და Manager უფლებამოსილია შესაბამის უწყებაზე", "Manager აირჩევს იმავე უწყების აქტიურ Worker-ს და მიუთითებს ვადას", "იქმნება Assignment, სტატუსი იცვლება Accepted-ით და StatusHistory აფიქსირებს მოქმედებას"],
            ["განაცხადი Accepted სტატუსშია და სამუშაო ჯერ არ დაწყებულა", "Manager მიუთითებს ახალ აქტიურ Worker-ს და გადანაწილების მიზეზს", "ძველი Assignment იკეტება EndedAt-ით, იქმნება ახალი Assignment და ისტორია ინახავს ვინ/როდის/რატომ გადაანაწილა"],
            ["განაცხადი InProgress ან Resolved სტატუსშია", "Manager ცდილობს სხვა Worker-ზე გადანაწილებას", "ოპერაცია უარყოფილია 409 Conflict-ით და არსებული Assignment უცვლელი რჩება"],
        ],
        "priority": "Must have",
        "points": 3,
        "note": "MVP-ში გადანაწილება შესაძლებელია მხოლოდ Accepted სტატუსში, სამუშაოს დაწყებამდე. InProgress/Resolved დავალების გადანაწილება მომავალი ცვლილების მოთხოვნაა.",
    },
    "US-16": {
        "title": "გადაჭრის შეფასება მოქალაქის მიერ",
        "role": "მოქალაქე",
        "story": "როგორც **მოქალაქე**, მსურს ჩემი დასრულებული განაცხადის მოგვარების ხარისხი 1-დან 5-მდე შევაფასო, რათა მუნიციპალიტეტმა მომსახურების ხარისხზე უკუკავშირი მიიღოს.",
        "ac": [
            ["მოქალაქის საკუთარი განაცხადი Resolved სტატუსშია", "მოქალაქე ირჩევს 1-დან 5-მდე შეფასებას", "შეფასება ინახება შესაბამის Report-ზე და ხელმისაწვდომია უფლებამოსილი Manager-ისთვის"],
            ["მოქალაქემ უკვე შეაფასა საკუთარი განაცხადი", "მეორედ ცდილობს ახალი შეფასების გაგზავნას", "სისტემა არ ქმნის დუბლიკატ შეფასებას; განახლება შესაძლებელია მხოლოდ განსაზღვრული ბიზნესწესით"],
        ],
        "priority": "Could have",
        "points": 2,
        "note": "ხელახლა გახსნა გამოყოფილია US-20-ში და ამ Story-ის ფარგლებს არ წარმოადგენს.",
    },
    "US-18": {
        "title": "Native Mobile App-ის საწყისი სტრუქტურა (Android/iOS)",
        "role": "მოქალაქე და საველე თანამშრომელი",
        "story": "როგორც **მოქალაქე ან საველე თანამშრომელი**, მსურს FixIt-ის ინსტალირებადი Android/iOS აპლიკაციის გამოყენება, რათა ჩემი როლის შესაბამისი მუნიციპალური მოქმედებები ტელეფონიდან შევასრულო.",
        "ac": [
            ["მხარდაჭერილ Android ან iOS მოწყობილობაზე აპლიკაცია დაყენებულია", "მომხმარებელი პირველად ხსნის აპლიკაციას", "ჩნდება საწყისი ეკრანი და როლის შესაბამისი ნავიგაციის სტრუქტურა; აპლიკაცია არ ითხოვს არასაჭირო permission-ებს"],
            ["მომხმარებელი წარმატებით არის ავტორიზებული", "აპლიკაცია იღებს მიმდინარე მომხმარებლის პროფილს", "აჩვენებს მხოლოდ შესაბამის როლზე განკუთვნილ ნავიგაციას; Backend მაინც ამოწმებს ყველა დაცულ მოთხოვნას"],
            ["მობილურ აპს აქვს მოქმედი Bearer session", "აპლიკაცია აგზავნის დაცულ API მოთხოვნას ან ახორციელებს logout-ს", "წვდომის ტოკენი ინახება SecureStore-ში და იგზავნება Authorization header-ში; logout-ისას ლოკალური ტოკენები იშლება"],
        ],
        "priority": "Must have",
        "points": 8,
        "note": "ეს Story ქმნის Mobile App-ის ტექნიკურ საძირკველს: Expo project, navigation, typed API client და secure token storage. Citizen/Worker-ის ბიზნესფუნქციები აღწერილია US-01…US-12-ში. Push Notifications MVP-ში არ შედის.",
    },
}

NEW_STORY = {
    "id": "US-20",
    "title": "პრობლემის ხელახლა გახსნის მოთხოვნა",
    "role": "მოქალაქე",
    "story": "როგორც **მოქალაქე**, მსურს ახლახან დასრულებულ განაცხადზე ხელახლა გახსნის მოთხოვნა მიზეზის მითითებით, თუ პრობლემა რეალურად არ მოგვარებულა, რათა მუნიციპალიტეტმა განმეორებით გადაამოწმოს შედეგი.",
    "ac": [
        ["მოქალაქის საკუთარი Report Resolved სტატუსშია და დასრულებიდან 7 დღე არ გასულა", "მოქალაქე უთითებს მიზეზს და აგზავნის reopen request-ს", "იქმნება Pending ReopenRequest; Report რჩება Resolved სტატუსში, სანამ Manager არ განიხილავს"],
        ["არსებობს Pending ReopenRequest", "Manager ამტკიცებს მოთხოვნას", "მოთხოვნა ხდება Approved, Report ბრუნდება Accepted სტატუსში და Manager-ს შეუძლია ახალი Assignment-ის შექმნა"],
        ["არსებობს Pending ReopenRequest", "Manager უარყოფს მოთხოვნას მიზეზის მითითებით", "მოთხოვნა ხდება Rejected, Report რჩება Resolved სტატუსში და უარყოფის მიზეზი მოქალაქისთვის ხელმისაწვდომია"],
    ],
    "priority": "Could have",
    "points": 3,
    "note": "Future scope. Pending მოთხოვნის შექმნა Report-ის სტატუსს დაუყოვნებლივ არ ცვლის; მოთხოვნის განხილვა Manager-ის უფლებამოსილებაა.",
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write the migration; without this flag only previews")
    args = parser.parse_args()

    if not STORIES_FILE.exists():
        print(f"ERROR: {STORIES_FILE} not found. Run this script inside your existing FixIt repository.", file=sys.stderr)
        return 2

    stories = json.loads(STORIES_FILE.read_text(encoding="utf-8"))
    if not isinstance(stories, list):
        print("ERROR: stories.json must contain a JSON array.", file=sys.stderr)
        return 2

    by_id = {story.get("id"): story for story in stories}
    missing = sorted({"US-09", "US-16", "US-18"} - set(by_id))
    if missing:
        print(f"ERROR: expected existing Story IDs missing: {missing}", file=sys.stderr)
        return 2

    updated = []
    for story_id, changes in UPDATES.items():
        by_id[story_id].update(changes)
        updated.append(story_id)

    if "US-20" not in by_id:
        stories.append(NEW_STORY.copy())
        by_id["US-20"] = stories[-1]
        updated.append("US-20 (new)")
    else:
        by_id["US-20"].update(NEW_STORY)
        updated.append("US-20 (updated)")

    for story in stories:
        sid = story["id"]
        story["platform"] = PLATFORMS.get(sid, [])
        story["dependencies"] = DEPENDENCIES.get(sid, [])

    print("Mobile-First migration preview:")
    print("  Updated: " + ", ".join(updated))
    print(f"  Stories after migration: {len(stories)}")
    if not args.apply:
        print("DRY RUN ONLY — no file was changed. Re-run with --apply to write the migration.")
        return 0

    if not BACKUP_FILE.exists():
        shutil.copy2(STORIES_FILE, BACKUP_FILE)
        print(f"Backup created: {BACKUP_FILE.relative_to(ROOT)}")
    else:
        print(f"Existing backup preserved: {BACKUP_FILE.relative_to(ROOT)}")

    STORIES_FILE.write_text(json.dumps(stories, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Migration written to backlog/stories.json")
    print("Next: python scripts/build_backlog.py && python scripts/validate_backlog.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
