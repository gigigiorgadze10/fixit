# FixIt — Mobile-First Migration Guide

ეს განახლება განკუთვნილია არსებული `gigigiorgadze10/fixit` Repository-სთვის. მიზანი არის არქიტექტურის შეცვლა ისე, რომ უკვე არსებული 19 Issue, მათი ნომრები და უცვლელი Story-ები არ დაიკარგოს.

## 1. რა იცვლება

| Item | Before | After |
|---|---|---|
| Product client | Responsive Razor web app | React Native Mobile + Next.js Web Dashboard |
| Backend | ASP.NET Core MVC + API | ASP.NET Core 10 Web API |
| Auth | Cookie-only აღწერა | Mobile Bearer token; Web secure Cookie |
| US-18 | Won't Have, 13 SP | Must Have, 8 SP — Mobile App foundation |
| US-16 | Rating + reopen ერთ Story-ში | მხოლოდ Rating, 2 SP |
| US-20 | არ არსებობდა | Reopen request, Could Have, 3 SP |
| US-09 | Reassign სცენარის არასაკმარისი წესები | მხოლოდ Accepted-მდე გადანაწილება; InProgress-ზე აკრძალულია |

## 2. განახლებული ქულები

- Must Have: 10 Story / 39 SP.
- Should Have: 5 Story / 16 SP.
- Could Have: 4 Story / 16 SP.
- Won't Have: 1 Story / 3 SP.
- Total: 20 Story / 74 SP.
- MVP: 39 SP.

## 3. უსაფრთხო განახლების რიგი

1. GitHub Repository-ის ლოკალური clone გააკეთე და დარწმუნდი, რომ `main` განახლებულია.
2. შექმენი ახალი branch: `feature/mobile-first-architecture`.
3. დააკოპირე განახლებული `README.md`, `BACKLOG.md`, `ARCHITECTURE.md`, `API_CONTRACT.md`, `DATA_MODEL.md`, `KANBAN_WORKFLOW.md` და `docs/` ფაილები.
4. ჯერ არ გაუშვა ძველი `scripts/publish_github.py` — ის ძველ `Priority` და `Ready (MVP)` ველებს ეძებს და შესაძლოა Project-ის არსებული კონფიგურაცია შეცვალოს.
5. გაუშვი `python scripts/migrate_mobile_first_backlog.py --apply` — ეს ქმნის backup-ს და ცვლის მხოლოდ US-09, US-16, US-18-ს, ამატებს US-20-ს; დანარჩენ Story-ებს არ შლის.
6. გაუშვი `python scripts/build_backlog.py` და შემდეგ `python scripts/validate_backlog.py`.
7. გადახედე Git diff-ს. თუ ყველაფერი სწორია, commit გააკეთე და push.
8. GitHub Issues-ში update script-ის dry-run ნახე, შემდეგ `--apply` არგუმენტით გამოიყენე. Existing Issue-ები title-ის US-ID-ით იძებნება; US-20 მხოლოდ байхгүй үед იქმნება.
9. Project #1-ში განაახლე US-18-ის MoSCoW/Points, US-16-ის MoSCoW/Points, დაამატე US-20; Project item-ების დუბლიკატები არ შექმნა.

## 4. არსებული Story-ების შენარჩუნება

Migration script backup-ს ქმნის `backlog/stories.pre-mobile-first.json` სახელით. თუ ფაილი უკვე არსებობს, სკრიპტი მას overwrite-ს არ უკეთებს. ცვლილებები მხოლოდ `--apply` არგუმენტით იწერება; მის გარეშე dry-run რეჟიმში მუშაობს.

`BACKLOG.md` და `backlog/issues/*.md` გენერირებული ფაილებია. ცვლილების წყარო არის `backlog/stories.json`. გენერირებულ Markdown-ში ხელით შეტანილი ტექსტი შემდეგ გენერაციაზე დაიკარგება.

## 5. GitHub Issues / Project განახლება

`sync_github_issues.py` პირველ გაშვებაზე მხოლოდ dry-run აჩვენებს. `--apply` რეჟიმი განაახლებს US-09, US-16, US-18 Issue-ებს და შექმნის US-20-ს, თუ შესაბამისი ID-ით Issue არ არსებობს. Project Board-ზე US-20-ის დამატება და MoSCoW/Story Points განახლება ბოლოს ხელით გადაამოწმე.

**არ წაშალო** არსებული Issues, Project #1 ან Issue history.
