# ADR-002 — Mobile-First Client–Server Architecture

- **Status:** Proposed / for lecturer approval
- **Date:** 2026-11-03
- **Decision owners:** FixIt project author/team

## Context

FixIt-ის ორი მთავარი ოპერაციული მომხმარებელი ადგილზე მუშაობს: Citizen იღებს ფოტოს და უთითებს GPS მდებარეობას; Field Worker იღებს დავალებას, მიდის მისამართზე, იწყებს სამუშაოს და ატვირთავს დასრულების ფოტოს. Dispatcher და Admin კი ბევრ განაცხადს მართავენ ცხრილებით, ფილტრებითა და ადმინისტრაციული ფორმებით.

არსებული არქიტექტურა იყენებდა ASP.NET Core MVC + Razor Views + Bootstrap-ს და მხოლოდ responsive web UI-ს აღწერდა. ეს ვერ გამოხატავდა პროდუქტის ნამდვილ Mobile App მიზანს.

## Decision

გამოვიყენოთ:

- React Native + Expo + TypeScript Mobile App — Citizen და Field Worker.
- Next.js App Router + TypeScript Web Dashboard — Dispatcher/Manager და Admin.
- ASP.NET Core 10 Web API — საერთო Backend.
- Layered Modular Monolith — Backend-ის შიდა არქიტექტურა.
- PostgreSQL + PostGIS — რელაციური და სივრცითი მონაცემები.
- Private S3-compatible Object Storage — ფოტოების ფაილები.

## Rationale

1. Native mobile capabilities (camera, location, secure storage) პირველადი მომხმარებლის სამუშაოსთან პირდაპირ კავშირშია.
2. Dispatcher/Admin სამუშაოს უფრო ფართო Web Dashboard ამარტივებს.
3. ერთი API და მონაცემთა ბაზა უზრუნველყოფს წესების ერთიანობას, ხოლო ერთი Backend deployable სემესტრის მასშტაბისთვის მართვადია.

## Authentication decision

MVP-ში Mobile client იყენებს ASP.NET Core Identity API-ის Bearer token რეჟიმს, ხოლო Web Dashboard — Cookie რეჟიმს. ჩაშენებული Identity bearer token proprietary token-ია და **არ არის JWT**. ეს არჩევანი მისაღებია ერთ პირველ მხარის მობილურ კლიენტთან. თუ მომავალში საჭიროა სტანდარტული OAuth2/OIDC/JWT, უნდა დაემატოს ცალკე Identity Provider; ეს არ არის MVP-ის მოთხოვნა.

## Alternatives considered

| Alternative | Why not selected now |
|---|---|
| Responsive MVC Website only | არ იძლევა ჩვენს მიერ მოთხოვნილ Native Mobile App პროდუქტს; კამერა/GPS-ის ინტეგრაცია შესაძლებელია, მაგრამ native app-ის UX/Distribution არ მიიღება. |
| Flutter + Web Dashboard | ტექნიკურად კარგი ალტერნატივაა, მაგრამ გუნდის არსებული TypeScript/React კომპეტენცია React Native-ს ამ ეტაპზე უფრო პრაქტიკულს ხდის. |
| Microservices | ზრდის deployment, service-to-service და distributed transaction სირთულეს MVP-ის შესაბამისი ღირებულების გარეშე. |
| MongoDB | ძირითადი მონაცემები რელაციურია და მოითხოვს FK/ტრანზაქციებს; PostgreSQL უფრო შესაფერისია. |
| JWT implemented manually | საკუთარი token issuer-ის შექმნა უსაფრთხოების პასუხისმგებლობას ზრდის; MVP-ში გამოიყენება Identity-ის ჩაშენებული token რეჟიმი და არ ვაცხადებთ მას JWT-დ. |

## Consequences

**Positive:** მომხმარებლის როლზე მორგებული UX; საერთო Backend; Native camera/GPS/secure storage; ერთი ბიზნესლოგიკის წყარო.

**Trade-offs:** ორი Frontend codebase-ის მოვლა; Android/iOS release/testing; authentication scheme-ების მკაფიო გაყოფა; API contract-ის სტაბილურობის საჭიროება.

## Follow-up

- Backlog-ში US-18 გადადის Must Have-ში (8 SP).
- US-16 რჩება მხოლოდ Rating ფუნქციად.
- US-20 ცალკე ReopenRequest ფუნქციად ემატება Could Have-ში.
- API Contract იყენებს Mobile Bearer და Web Cookie auth რეჟიმებს.
- Data Model ამატებს Assignment history-ს და PostGIS ServiceArea-ს.
