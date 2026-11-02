# FixIt - მუნიციპალური პრობლემების შეტყობინებისა და მართვის სისტემა

**საგანი:** DevOps and Software Engineering  
**ავტორი:** გიგი გიორგაძე  
**პროექტის ტიპი:** ინდივიდუალური Product Backlog და არქიტექტურის პროექტი

[GitHub Repository](https://github.com/gigigiorgadze10/fixit) · [GitHub Projects](https://github.com/users/gigigiorgadze10/projects/1) · [Issues](https://github.com/gigigiorgadze10/fixit/issues)

## 1. პროექტის მოკლე აღწერა

ქალაქში დაზიანებული ქუჩის განათების, გზის ორმოს ან გადავსებული ნაგვის ურნის შესახებ მოქალაქეს ხშირად არ აქვს მარტივი და გამჭვირვალე გზა მუნიციპალიტეტისთვის ინფორმაციის მისაწოდებლად. **FixIt** არის მობილური აპლიკაცია, რომლითაც მოქალაქე იღებს/ირჩევს ფოტოს, უთითებს პრობლემის კატეგორიასა და GPS-ით ან რუკაზე მონიშნულ მდებარეობას და აგზავნის განაცხადს. მუნიციპალიტეტის დისპეჩერი ვებ-პანელიდან ამოწმებს განაცხადს და ანაწილებს პასუხისმგებელ თანამშრომელზე, ხოლო საველე თანამშრომელი მობილური აპლიკაციით ხედავს დავალებას, იწყებს სამუშაოს და დასრულებას ფოტოთი ადასტურებს. მოქალაქე აპლიკაციაში აკონტროლებს საკუთარი განაცხადის სტატუსსა და ისტორიას, მუნიციპალიტეტი კი იღებს პროცესის ერთიან აღრიცხვას.

## 2. პროდუქტის არხები და მომხმარებლები

FixIt იყენებს ორ კლიენტს და ერთ საერთო Backend-ს:

| კლიენტი | მომხმარებლები | ძირითადი დანიშნულება |
|---|---|---|
| Native Mobile App (Android/iOS) — React Native + Expo | Citizen, Field Worker | განაცხადის შექმნა, კამერა, GPS, რუკა, დავალებების მიღება და შესრულების ფოტოთი დადასტურება |
| Web Dashboard — Next.js | Dispatcher/Manager, Admin | განაცხადების ცხრილი/ფილტრები, გადამოწმება, მინიჭება, მომხმარებლებისა და კატეგორიების მართვა |
| Shared Backend — ASP.NET Core Web API | ორივე კლიენტი | ბიზნესლოგიკა, ავტორიზაცია, უფლებები, მონაცემთა დამუშავება და API |

**Stakeholder-ები:** მოქალაქე, დისპეჩერი, საველე თანამშრომელი, სისტემის ადმინისტრატორი, მუნიციპალიტეტი (დამკვეთი/გადამხდელი), იურიდიული ან მონაცემთა დაცვის პასუხისმგებელი პირი (შესაბამისობის საკითხებზე შეჩერების უფლებით).

**სისტემის როლები:** `Citizen`, `Manager`, `Worker`, `Admin`. მოქალაქე საჯარო რეგისტრაციით იღებს მხოლოდ `Citizen` როლს. თანამშრომელთა როლებს ანიჭებს უფლებამოსილი Admin.

## 3. MVP-ის მიზანი და საზღვრები

MVP უზრუნველყოფს ერთ მუნიციპალურ არეალში პრობლემის სრულ ძირითად ციკლს:

1. Citizen ქმნის ანგარიშს და შედის მობილურ აპლიკაციაში.
2. Citizen ქმნის განაცხადს კატეგორიით, აღწერით, 1–3 ფოტოთი და მდებარეობით.
3. Citizen ხედავს მხოლოდ საკუთარ განაცხადებს, დეტალებსა და სტატუსის ისტორიას.
4. Manager ვებ-პანელიდან ხედავს საკუთარი უწყების განაცხადებს და ანაწილებს პასუხისმგებელ Worker-ზე.
5. Worker მობილური აპლიკაციით ხედავს საკუთარ დავალებას, იწყებს სამუშაოს და ტვირთავს დასრულების ფოტოს.
6. Citizen ხედავს `Resolved` სტატუსსა და დასრულების მტკიცებულებას.

### MVP-ის მოცულობა

| პრიორიტეტი | Story-ები | რაოდენობა | ქულა |
|---|---|---:|---:|
| Must Have | US-01, US-02, US-03, US-04, US-08, US-09, US-11, US-12, US-13, US-18 | 10 | **39 SP** |
| Should Have | US-05, US-06, US-10, US-14, US-19 | 5 | 16 SP |
| Could Have | US-07, US-15, US-16, US-20 | 4 | 16 SP |
| Won't Have (this time) | US-17 | 1 | 3 SP |
| **სრული Backlog** | **US-01…US-20** | **20** | **74 SP** |

აქტიური Backlog (Won't Have-ის გამოკლებით): 19 Story / 71 SP. MVP: 10 Must Have Story / 39 SP.

**MVP-ში არ შედის:** Push შეტყობინებები, ანონიმური შეტყობინება, საჯარო რუკა, მოქალაქეების მხარდაჭერის ხმები, სტატისტიკური Dashboard, პრობლემის ხელახლა გახსნა, კატეგორიების თვითმართვა Admin-ის მიერ და ელფოსტით პაროლის აღდგენა. ეს ფუნქციები ცალკე პრიორიტეტებით რჩება Backlog-ში.

## 4. არაფუნქციური მოთხოვნები (NFR)

| ID | მოთხოვნა | გაზომვადი კრიტერიუმი |
|---|---|---|
| NFR-01 | API performance | 100 ვირტუალური მომხმარებლის k6 ტესტში ძირითადი API GET მოთხოვნების p95 პასუხის დრო ≤ 2 წამი. არ მოიცავს გარე რუკის ფილებსა და ფაილის ატვირთვის დროს. |
| NFR-02 | Reliability under load | იმავე 100 VU ტესტში ძირითადი API მოთხოვნების შეცდომების წილი < 1%. |
| NFR-03 | Photo upload | განაცხადზე 1–3 JPEG/PNG ფოტო; თითოეული მაქსიმუმ 10 MB. ზედმეტი ზომა → 413; დაუშვებელი ფორმატი → 415. |
| NFR-04 | Mobile usability | Citizen და Worker-ის ძირითადი ეკრანები უნდა იყოს გამოსაყენებელი მინიმუმ 360 dp სიგანის ტელეფონზე. |
| NFR-05 | Web usability | Dispatcher/Admin-ის ძირითადი სამუშაო ხედები უნდა მუშაობდეს მინიმუმ 1024 CSS px სიგანის ეკრანზე ჰორიზონტალური გადახვევის გარეშე. |
| NFR-06 | Access control | ყველა დაცული endpoint ამოწმებს ავტორიზაციას, როლსა და რესურსზე წვდომას; დაცული endpoint-ების 100%-ზე უნდა არსებობდეს 401/403/უცხო რესურსის უარყოფის ტესტები. |
| NFR-07 | Privacy | ატვირთული ფოტოების EXIF მეტამონაცემები იშლება შენახვამდე; პირადი საკონტაქტო მონაცემები არ ბრუნდება საჯარო API-დან და არ იწერება ჩვეულებრივ აპლიკაციის ლოგში. |

ეს მოთხოვნები სამიზნე კრიტერიუმებია; შესრულებულად ჩაითვლება მხოლოდ შესაბამისი ტესტის შედეგის არსებობისას.

## 5. Definition of Done

Story დასრულებულია მხოლოდ მაშინ, როდესაც ყველა Acceptance Criteria დაკმაყოფილებულია; შესაბამისი Unit/Integration/UI ტესტები გადის; ავტორიზაცია და რესურსზე წვდომა შემოწმებულია; კოდი გაიარა review/self-review; დოკუმენტაცია და API/DB ცვლილების შემთხვევაში migration განახლებულია; build/CI წარმატებულია; ფუნქცია სატესტო გარემოში შემოწმებულია; GitHub Issue განახლებულია.

დეტალები: [`docs/DEFINITION_OF_DONE.md`](docs/DEFINITION_OF_DONE.md).

## 6. სამუშაო პროცესის მართვა

პროექტი იმართება Agile მიდგომით და Kanban workflow-ით. GitHub Projects-ში გამოიყენება `Backlog`, `Ready`, `In Progress`, `In Review`, `Done` სტატუსები. MoSCoW პრიორიტეტი და Story Points დამოუკიდებელი ველებია: პრიორიტეტი ფუნქციის მნიშვნელობას აღწერს, Status კი მიმდინარე სამუშაო მდგომარეობას.

დეტალები: [`KANBAN_WORKFLOW.md`](KANBAN_WORKFLOW.md).

## 7. არქიტექტურა და ტექნოლოგიური სტეკი

**Overall style:** Client–Server Architecture.  
**Backend style:** Layered Modular Monolith.

| ფენა | ტექნოლოგია | დანიშნულება |
|---|---|---|
| Mobile | React Native + Expo + TypeScript | Android/iOS აპლიკაცია Citizen-ისა და Worker-ისთვის |
| Mobile navigation/device APIs | Expo Router, ImagePicker, Location, SecureStore | ნავიგაცია, კამერა/გალერეა, GPS და სესიის უსაფრთხო შენახვა |
| Web | Next.js App Router + TypeScript | Dispatcher/Admin Dashboard |
| Backend | ASP.NET Core 10 Web API | საერთო REST API და ბიზნესლოგიკა |
| Authentication | ASP.NET Core Identity API | Mobile Bearer token და Web Cookie რეჟიმები |
| ORM/DB | EF Core 10 + PostgreSQL | რელაციური მონაცემები და ტრანზაქციები |
| Spatial | PostGIS + NetTopologySuite | მუნიციპალური საზღვრისა და რუკის გეოგრაფიული მოთხოვნები |
| File storage | Private S3-compatible Object Storage | ფოტოების ბინარული ფაილები; DB ინახავს მხოლოდ მეტამონაცემებს |
| Maps | react-native-maps (Mobile), Leaflet (Web) | რუკა და მდებარეობის მონიშვნა |
| Testing | xUnit, WebApplicationFactory, React Native Testing Library, Playwright, k6 | Backend, UI და დატვირთვის ტესტები |
| DevOps | Docker Compose, GitHub Actions | განმეორებადი ლოკალური გარემო და CI |

მნიშვნელოვანი ავტორიზაციის დაზუსტება: ASP.NET Core Identity API-ის ჩაშენებული Bearer token proprietary token-ია და არა სტანდარტული JWT. MVP-ში ეს მისაღებია ერთი პირველი მხარის Mobile კლიენტისთვის; Web Dashboard იყენებს უსაფრთხო Cookie რეჟიმს. სტანდარტული OAuth2/OIDC/JWT ინტეგრაცია განიხილება მხოლოდ მაშინ, თუ ამას მომავალი გარე ინტეგრაცია მოითხოვს.

დეტალები: [`ARCHITECTURE.md`](ARCHITECTURE.md), [`API_CONTRACT.md`](API_CONTRACT.md), [`DATA_MODEL.md`](DATA_MODEL.md), [`docs/adr/ADR-002-mobile-first-architecture.md`](docs/adr/ADR-002-mobile-first-architecture.md).

## 8. ძირითადი რისკები

| რისკი | გავლენა | შემცირების გზა |
|---|---|---|
| Mobile OS / მოწყობილობების განსხვავება | კამერა, GPS ან რუკა სხვადასხვა მოწყობილობაზე განსხვავებულად იქცევა | Expo SDK-ის თავსებადი ვერსიების დაფიქსირება, Android/iOS რეალურ მოწყობილობაზე smoke test, ხელით მდებარეობის fallback |
| მდებარეობის სიზუსტე და მუნიციპალური საზღვარი | არასწორი კოორდინატი ან საზღვარს გარეთ განაცხადი | რუკაზე წერტილის ხელით გასწორება და PostGIS geofence შემოწმება სერვერზე |
| ფოტოები და პირადი მონაცემები | EXIF/ფაილის ბმულის გაჟონვა | EXIF stripping, private bucket, authorization check, დროებითი ბმულები და ლოგების მინიმიზაცია |
| Storage/DB თანმიმდევრულობა | ფაილი აიტვირთა, მაგრამ DB ჩანაწერი ვერ შეიქმნა | ორსაფეხურიანი პროცესი: ატვირთვა → DB transaction; DB წარუმატებლობისას კომპენსატორული წაშლა და orphan cleanup |

## 9. Repository-ის დოკუმენტაცია

- [Product Backlog](BACKLOG.md)
- [Architecture](ARCHITECTURE.md)
- [REST API Contract](API_CONTRACT.md)
- [Database Model](DATA_MODEL.md)
- [Kanban Workflow](KANBAN_WORKFLOW.md)
- [Definition of Done](docs/DEFINITION_OF_DONE.md)
- [Architecture Decision Record](docs/adr/ADR-002-mobile-first-architecture.md)
- [GitHub Projects Update](docs/GITHUB_PROJECTS_UPDATE.md)
- [Migration Guide](docs/MIGRATION_GUIDE.md)
- [Tech Stack](docs/TECH_STACK.md)
- [References](docs/REFERENCES.md)
- [Assignment Checklist](docs/RELEASE_CHECKLIST.md)
- [Architecture Presentation](docs/FixIt-Architecture.pptx)
- [GitHub Project Board](https://github.com/users/gigigiorgadze10/projects/1)
