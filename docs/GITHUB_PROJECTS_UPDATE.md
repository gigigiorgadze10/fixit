# GitHub Projects — Mobile-First Update

არსებული Project #1 უნდა შენარჩუნდეს. ახალი Project არ შექმნა.

Project: https://github.com/users/gigigiorgadze10/projects/1

## 1. არსებული ველების მნიშვნელობები

- `Status` (Single Select): Backlog, Ready, In Progress, In Review, Done.
- `MoSCoW` (Single Select): Must have, Should have, Could have, Won't have.
- `Story Points` (Number): 1, 2, 3, 5, 8, 13.

`Sprint` Iteration ველი საჭირო არ არის. თუ ის ჯერ კიდევ არსებობს, დამალე შესაბამის View-ში; თუ უკვე აღარ გამოიყენება, შეგიძლია მოგვიანებით წაშალო.

## 2. Existing Issue-ების ცვლილება

არ შექმნა US-09, US-16 ან US-18 თავიდან. განაახლე შესაბამისი არსებული Issue:

| Story | მოქმედება | MoSCoW | Points |
|---|---|---|---:|
| US-09 | Body განახლდეს გადანაწილების მკაფიო წესებით | Must have | 3 |
| US-16 | Body დარჩეს მხოლოდ 1–5 შეფასებაზე | Could have | 2 |
| US-18 | Body შეიცვალოს Mobile App foundation-ით; `wont-have` label მოიხსნას და `must-have` დაემატოს | Must have | 8 |
| US-20 | ახალი Issue შეიქმნას | Could have | 3 |

Issue-ების body ტექსტები არის `backlog/issues/US-09.md`, `US-16.md`, `US-18.md`, `US-20.md` ფაილებში. მათი გენერაცია ხდება `python scripts/build_backlog.py`-ით.

## 3. Project-ის ველების განახლება

Project-ის Table View-ში იპოვე Issue ID-ით:

- US-18: MoSCoW → Must have; Story Points → 8; Status → Ready (როგორც პირველი ტექნიკური foundation Story).
- US-16: MoSCoW → Could have; Story Points → 2; Status → Backlog.
- US-09: MoSCoW → Must have; Story Points → 3; Status → Backlog.
- US-20: დაამატე ახალი Issue Project #1-ში; MoSCoW → Could have; Story Points → 3; Status → Backlog.

დანარჩენი 16 Story-ის ველები უცვლელი უნდა დარჩეს. ახალი ჯამი: Must 39, Should 16, Could 16, Won't 3; სულ 74 SP.

## 4. Board-ის საწყისი მდგომარეობა

- მხოლოდ US-18 არის Ready.
- დანარჩენი Story-ები Backlog-ში რჩება.
- In Progress, In Review და Done სვეტები ცარიელი შეიძლება იყოს — ეს ნორმალურია დაგეგმვის ეტაპზე.
- MoSCoW და Status ერთმანეთისგან დამოუკიდებელი ველებია; Must have ავტომატურად Ready არ ნიშნავს.

## 5. Labels (რეკომენდებული)

არსებული priority labels შეინარჩუნე: `must-have`, `should-have`, `could-have`, `wont-have`. დაამატე ტექნიკური labels: `mobile-app`, `web-dashboard`, `backend-api`, `database`, `file-storage`, `security`.

მათ Issue-ზე დამატება შეგიძლია, მაგრამ Project-ის MoSCoW field მაინც უნდა იყოს შევსებული — Label მას არ ანაცვლებს.

## 6. საბოლოო Views

1. **Kanban Board** — Board layout, Group by `Status`.
2. **Product Backlog** — Table layout, Group by `MoSCoW`; აჩვენე Title, Status, MoSCoW, Story Points, Labels, Assignees.
3. **MVP View** — Filter `MoSCoW is Must have`.
4. **Future Scope** — Filter `MoSCoW is Should have OR Could have OR Won't have`.

თუ US-20 Issue უკვე შეიქმნა, Project-ში ჯერ ძებნით გადაამოწმე, რომ არ არსებობს, შემდეგ გამოიყენე `Add item from repository`. დუბლირებული Project item არ შექმნა.
