# FixIt: არქიტექტურის არჩევა

**პრაქტიკული 2** · სცენარი **D: საკუთარი იდეა**: FixIt, კომუნალური პრობლემების შეტყობინების სისტემა (იხ. [README.md](README.md) და [BACKLOG.md](BACKLOG.md)).
**პრეზენტაცია:** [docs/FixIt-Architecture.pptx](docs/FixIt-Architecture.pptx)

მოთხოვნები, რომლებიც არქიტექტურას განსაზღვრავს:
- 4 როლი: მოქალაქე, უწყების მენეჯერი, ბრიგადის თანამშრომელი, ადმინი
- ფოტოების ატვირთვა (10 MB-მდე, NFR-3) და რუკა/გეოლოკაცია (US-03, US-06)
- სია და რუკა იტვირთება 2 წამში, 500 ერთდროული მომხმარებელი (NFR-1, NFR-2)
- ინდივიდუალური პროექტი, MVP ≈ 2 თვეში (31 ქულა), სრული გეგმა ≈ 3 თვე ([SCRUM_PLAN.md](SCRUM_PLAN.md))

## 0. MVP-ის რეალისტური ვერსია (2–3 თვე, Scrum)

ქვემოთ აღწერილი არქიტექტურა არის **სამიზნე სურათი**. ერთ სემესტრში ერთი ადამიანი ყველაფერს ვერ ააწყობს, ამიტომ MVP-სთვის (იხ. [SCRUM_PLAN.md](SCRUM_PLAN.md)) ვტოვებთ იმავე სტილს და pattern-ების ძირითად ნაწილს, ხოლო რთულ ნაწილებს ვანაცვლებთ მარტივით. შეცვლა არ არის დრასტიკული: ყველა გამარტივება მოგვიანებით უკან იცვლება კოდის მცირე ცვლილებით, რადგან ინტერფეისები (`IFileStorage`, `INotificationService`) უკვე არსებობს.

| ნაწილი | სამიზნე არქიტექტურა (ქვემოთ) | MVP-ში (რასაც რეალურად ვაკეთებთ) | რატომ |
|--------|------------------------------|-----------------------------------|-------|
| გეო-მონაცემები | PostGIS + NetTopologySuite, GiST ინდექსი | ორი სვეტი `Latitude`, `Longitude` (`double`) + ჩვეულებრივი ინდექსი. მუნიციპალიტეტის საზღვარი (US-03, სცენარი 3) = მართკუთხა არე (bounding box) კონფიგურაციაში, ზუსტი პოლიგონი მოგვიანებით. მისამართი და უბანი კოორდინატებიდან Nominatim-ით (OSM), ≤ 1 მოთხოვნა წამში | რუკაზე ნიშნულების ჩვენებას და ფილტრს საკმარისად ეყოფა; „50 მეტრის რადიუსი" (დუბლიკატები) ხელით ირჩევა მენეჯერი |
| ფონური ამოცანები | Hangfire | ფოტოს შეკუმშვა ატვირთვისას სინქრონულად (ImageSharp, ≤ 10 MB ფოტო ეტევა 5 წამში); ელფოსტა ჩაშენებული `BackgroundService` + `Channel` | Hangfire ცალკე კონფიგურაცია და dashboard-ია, სემესტრისთვის ზედმეტი |
| Domain Events | MediatR, Observer | `AssignmentService` პირდაპირ იძახებს `INotificationService.StatusChanged(...)` | ერთი გამომძახებელი და ერთი მიმღები გვაქვს, ბიბლიოთეკა არ სჭირდება |
| სტატუსის წესები | State pattern (კლასი თითო სტატუსზე) | ერთი `ReportStatusRules` კლასი: დაშვებული გადასვლების `Dictionary<ReportStatus, ReportStatus[]>` | იგივე წესები, 20 ხაზი კოდი, იგივე unit ტესტები |
| ფოტოების საცავი | S3-თავსებადი საცავი | ლოკალური დისკი (`LocalFileStorage`) ან Cloudinary free tier | `IFileStorage` ინტერფეისი ტოვებს გადასვლის შესაძლებლობას |
| ჰოსტინგი | Nginx + Docker Compose საკუთარ სერვერზე | PaaS: Azure App Service (**Basic ან ზევით**) + მართვადი PostgreSQL ავტომატური ბექაპით. დემონსტრაციისთვის უფასო plan-ებიც შეიძლება, მაგრამ მათზე ხელმისაწვდომობა გარანტირებული არ არის | Azure-ის SLA Basic-დან ზევით 99.95%, ხოლო Free/Shared-ზე SLA არ არის; NFR-4-ის (99.9%) შესასრულებლად Basic საკმარისია. HTTPS და deploy ავტომატურია |
| ტესტირება | xUnit + Moq + WebApplicationFactory + Playwright + k6 | xUnit + Moq (სერვისები) და `WebApplicationFactory` (2–3 ძირითადი ნაკადი); k6 Sprint 6-ში NFR-1/2-ისთვის: 500 ვირტუალური მომხმარებელი 5–10 წმ პაუზებით, p95 ≤ 500 ms, შეცდომები < 1% | DoD: დაფარვა ≥ 70% ახალ კოდზე სრულდება unit ტესტებით |
| NFR-ების დონე | 99.9% ხელმისაწვდომობა (NFR-4), 500 ერთდროული მომხმარებელი (NFR-2) | იგივე: NFR-ები არ მცირდება. დატვირთვის ტესტი ტარდება staging-ზე Basic plan-ით Sprint 6-ში | უფასო plan-ზე SLA არ არის, ამიტომ ჩაბარებამდე staging და production Basic-ზეა |

**რჩება უცვლელად** (ეს MVC-ს არსია და იაფი): ASP.NET Core 8 MVC, Razor + Bootstrap 5, Leaflet + OpenStreetMap, EF Core + PostgreSQL, ASP.NET Identity (4 როლი), Repository + DI, ViewModel-ები, Service ფენა, GitHub Actions CI.

### აუდიტის შემდეგ დაზუსტებული ბაზა და წესები

| ცვლილება | რატომ |
|----------|-------|
| `Reports.District` (text) | US-08 ფილტრი „უბნით"; ივსება მისამართიდან |
| `Users.NotifyByEmail` (boolean, ნაგულისხმევად true) | US-05, სცენარი 2: მოქალაქეს შეუძლია შეტყობინების გამორთვა |
| `Latitude`/`Longitude` Sprint 1-ში nullable, Sprint 2-ში (US-03) NOT NULL მიგრაციით | US-02 უსწრებს US-03-ს, ამიტომ ლოკაცია ჯერ არ არის სავალდებულო |
| ინდექსი `Reports(AuthorId, CreatedAt)` | US-04 „ჩემი შეტყობინებები" |
| `Reports.Number` გენერირდება PostgreSQL SEQUENCE-ით | ნომერი უნიკალური რჩება პარალელურ მოთხოვნებზეც |
| `xmin` concurrency token `Reports`-ზე | ორი მენეჯერი ერთსა და იმავე შეტყობინებას ერთდროულად ვერ მიანიჭებს (409 Conflict) |
| `Status` ინახება ტექსტად + CHECK შეზღუდვა | ბაზაში არავალიდური სტატუსი ვერ მოხვდება |
| FK-ები `ON DELETE RESTRICT`; მომხმარებელი არ იშლება, ითიშება (`IsActive`) | US-13, სცენარი 2: სამუშაოების ისტორია ინახება |

**საჯარო ხილვადობის წესი (US-06, იურიდიული ვეტო):** საჯარო რუკაზე ჩანს მხოლოდ სტატუსებით `Accepted`, `InProgress`, `Resolved`; `New` და `Rejected` არა. ფოტოები საჯაროდ ჩანს მხოლოდ მიღებულ შეტყობინებებზე, ანუ მენეჯერი მათ ხედავს გამოქვეყნებამდე.

**სტანდარტები და ოპერაციები (ყველა ერთი ადამიანისთვის შესასრულებელია):**

| სფერო | რას ვაკეთებთ | NFR / DoD |
|-------|--------------|-----------|
| უსაფრთხოება | HSTS, `Secure`/`HttpOnly`/`SameSite` cookie, CSP (მხოლოდ საკუთარი რესურსები და OSM ფილები), ჩაშენებული ASP.NET Core Rate Limiting, Anti-Forgery ტოკენები | NFR-5, NFR-9 |
| ლოგირება | Serilog; პერსონალური მონაცემები ლოგში არ იწერება | Sprint 0 |
| მონიტორინგი | `/health` endpoint და გარე შემოწმება ყოველ წუთში (UptimeRobot ან Azure availability test) | NFR-4 |
| საიდუმლოები | კონფიგურაცია გარემოს ცვლადებით/User Secrets, რეპოში გასაღები არასოდეს | Sprint 0 |
| დამოკიდებულებები | Dependabot და `dotnet list package --vulnerable` CI-ში | DoD |
| ბექაპი | მართვადი PostgreSQL-ის ყოველდღიური ბექაპი, აღდგენის გამოცდა | NFR-7 |
| წვდომადობა | Lighthouse/axe, ლეიბლები, კონტრასტი | NFR-8 |
| პერსონალური მონაცემები | EXIF-ის წაშლა, ანონიმიზაციის პროცედურა, 3-წლიანი ვადა | NFR-10 |

**ღია კითხვა (გადაწყვიტე Sprint 1-მდე):** US-02 ითვალისწინებს HEIC ფოტოს, მაგრამ ImageSharp HEIC-ს არ კითხულობს (გადაამოწმე ბიბლიოთეკის დოკუმენტაციაში). MVP-ში უსაფრთხოა JPG/PNG; iPhone-ის ბრაუზერი ხშირად ფოტოს ატვირთვისას JPEG-ად გარდაქმნის, ამიტომ ეს Sprint 0-ის prototype-ზე სცადე და, თუ საჭიროა, HEIC ცალკე story-დ გააკეთე.

**რას რომელი Sprint-ი ააგებს:**

| ნაწილი | Sprint | Story-ები |
|--------|--------|-----------|
| პროექტი, ბაზა, Identity, CI | 0 | — |
| `AccountController`, `ReportsController.Create` + ფოტო | 1 | US-01, US-02 |
| რუკა (Leaflet), „ჩემი შეტყობინებები", `AdminController` | 2 | US-03, US-04, US-13 |
| `ManageController`: სია, ფილტრები, მინიჭება | 3 | US-08, US-09 |
| `TasksController`: ამოცანები, დასრულება ფოტოთი | 4 | US-11, US-12, US-10 |
| ელფოსტის შეტყობინებები, კატეგორიების მართვა, პაროლის აღდგენა | 5 | US-05, US-14, US-19 |
| საჯარო რუკა (`MapApiController`), k6, გაპრიალება | 6 | US-06 |

**Stakeholder-ები → კომპონენტები:**

| Stakeholder | რას იყენებს | კომპონენტები |
|-------------|-------------|--------------|
| მოქალაქე | ფორმა, რუკა, ჩემი სია | `AccountController`, `ReportsController`, Razor View-ები, `MapApiController` |
| მენეჯერი (დისპეჩერი) | სია ფილტრებით, მინიჭება, უარყოფა | `ManageController`, `AssignmentService` |
| ბრიგადა | ამოცანები და დასრულება ფოტოთი | `TasksController`, `IFileStorage` |
| ადმინი | მომხმარებლები, როლები, კატეგორიები | `AdminController`, Identity |
| მერია (იხდის) | დაბალი ხარჯი, სტატისტიკა (Could, მოგვიანებით) | PaaS უფასო plan, `StatsController` (US-15, გადადებული) |
| იურიდიული / პმდ ოფიცერი (ვეტო) | მონაცემთა დაცვა | EXIF-ის წაშლა (US-02), ViewModel-ები კონტაქტის დასამალად, Privacy Check #1 და #2 ([SCRUM_PLAN.md](SCRUM_PLAN.md)) |

ქვემოთ მოცემული ნაწილები (1–8) რჩება როგორც სრული დიზაინი; MVP-ში მათი ის ნაწილი ვრცელდება, რაც ზემოთ ცხრილში „რჩება უცვლელად"-შია.

## 1. არქიტექტურული სტილი: MVC + ფენოვანი (Layered) მონოლითი

FixIt არის ერთი **ASP.NET Core MVC** აპლიკაცია, სადაც სერვერი თავად აგენერირებს HTML გვერდებს (server-side rendering). კოდი დაყოფილია სამ MVC როლად და მათ უკან ორ დამატებით ფენად:

| ფენა | რას აკეთებს | FixIt-ში |
|------|-------------|----------|
| **Model** | მონაცემები და ბიზნეს-წესები | `Report`, `User`, `Category`, სტატუსების წესები (State pattern), ViewModel-ები |
| **View** | რას ხედავს მომხმარებელი | Razor გვერდები (`.cshtml`): ფორმა, სია, რუკა, მენეჯერის პანელი |
| **Controller** | იღებს მოთხოვნას, იძახებს სერვისს, ირჩევს View-ს | `ReportsController`, `ManageController`, `TasksController`, `AdminController` |
| Service | ბიზნეს-ლოგიკა, რომ Controller-ები „მსუქანი" არ გახდეს | `ReportService`, `AssignmentService`, `NotificationService` |
| Repository / Data | ბაზასთან მუშაობა | Entity Framework Core, `FixItDbContext` |

მძიმე და ნელი სამუშაოები (ფოტოს შეკუმშვა, ელფოსტა) გადადის ფონურ ამოცანებში (**Hangfire**), რომ მომხმარებელს პასუხის ლოდინი არ მოუწიოს.

**არგუმენტები:**

1. **სწრაფი დეველოპმენტი მცირე პროექტისთვის.** MVC-ში ერთ პროექტში ერთად არის UI და backend: არ გვჭირდება ცალკე SPA (React), ცალკე API-ის ვერსიონირება და ორი deploy. ASP.NET Core MVC-ს მზად აქვს ავტორიზაცია და როლები (Identity), ფორმების ვალიდაცია, CSRF დაცვა და EF Core მიგრაციები. ერთი დეველოპერისთვის ეს ნიშნავს, რომ დრო MVP-ის 9 story-ზე იხარჯება და არა ინფრასტრუქტურაზე.
2. **ჩვენი ინტერფეისი ძირითადად ფორმები და სიებია.** შეტყობინების ფორმა, მენეჯერის სია ფილტრებით, ამოცანების სია, ადმინის ცხრილები. ეს კლასიკური CRUD სცენარებია, რომლებიც სერვერზე დახატულ გვერდებს იდეალურად ერგება. ინტერაქტიული ნაწილი მხოლოდ რუკაა, რომელსაც Leaflet-ის მცირე JavaScript ფაილი ემსახურება. სერვერზე დახატული გვერდი ტელეფონზეც სწრაფად იხსნება (NFR-1: 2 წამი), რადგან დიდი JS bundle-ის ჩამოტვირთვა არ სჭირდება.
3. **პასუხისმგებლობების მკაფიო გამიჯვნა.** Model, View და Controller ცალ-ცალკეა, ბიზნეს-ლოგიკა კი Service ფენაშია. ამიტომ გუნდის წევრებს შეუძლიათ პარალელურად იმუშაონ (ერთი View-ებზე, მეორე სერვისებზე), ხოლო სერვისები Controller-ის გარეშე იტესტება unit ტესტებით (DoD: დაფარვა ≥ 70%). თუ მომავალში მობილური აპლიკაცია (US-18) დაგვჭირდება, იმავე სერვისებზე დაემატება `ApiController`-ები.

**განხილული და უარყოფილი:** მიკროსერვისები (ზედმეტად რთული ჩვენი მასშტაბისთვის); SPA (React) + ცალკე REST API (ორი პროექტი, ორი deploy და ორმაგი ვალიდაცია MVP-სთვის გაუმართლებელია).

## 2. კომპონენტების დიაგრამა

```mermaid
flowchart LR
    subgraph Clients["კლიენტები"]
        BR["ბრაუზერი / ტელეფონი<br/>მოქალაქე, მენეჯერი,<br/>ბრიგადა, ადმინი"]
    end

    OSM["OpenStreetMap<br/>რუკის ფილები"]

    subgraph Server["FixIt სერვერი (Docker Compose)"]
        NG["Nginx<br/>HTTPS, reverse proxy"]
        subgraph APP["ASP.NET Core MVC აპლიკაცია"]
            C["Controllers<br/>Reports, Manage,<br/>Tasks, Admin, Account"]
            V["Views<br/>Razor .cshtml +<br/>Leaflet JS"]
            S["Services<br/>Report, Assignment,<br/>Notification, Stats"]
            M["Models<br/>Entities, ViewModels,<br/>სტატუსის წესები"]
            R["Data<br/>EF Core DbContext,<br/>Repositories"]
            ID["ASP.NET Identity<br/>ავტორიზაცია, როლები"]
            HF["Hangfire Jobs<br/>ფოტოს შეკუმშვა,<br/>ელფოსტა"]
        end
        DB[("PostgreSQL + PostGIS")]
        FS[("ფაილების საცავი<br/>ფოტოები")]
    end

    SMTP["ელფოსტის სერვისი<br/>(SMTP)"]

    BR -->|"HTTPS: GET / POST"| NG
    BR -.->|ფილები| OSM
    NG --> C
    C -->|"ViewModel"| V
    V -->|"HTML"| NG
    C --> S
    C --> ID
    S --> M
    S --> R
    R --> DB
    ID --> DB
    S -->|"ფოტოს შენახვა"| FS
    S -->|"ამოცანა რიგში"| HF
    HF --> DB
    HF --> FS
    HF --> SMTP
```

### MVC მოთხოვნის გზა: მოქალაქე აგზავნის შეტყობინებას

```mermaid
sequenceDiagram
    actor U as მოქალაქე
    participant C as ReportsController
    participant S as ReportService
    participant DB as PostgreSQL
    participant H as Hangfire
    participant V as View (Razor)

    U->>C: POST /reports/create (ფორმა + ფოტო)
    C->>C: ModelState ვალიდაცია
    alt ფორმა არასწორია
        C->>V: Create.cshtml შეცდომებით
        V-->>U: HTML, ველთან შეცდომის ტექსტი
    else ფორმა სწორია
        C->>S: CreateAsync(model, userId)
        S->>DB: INSERT Report (status = NEW)
        S->>H: ProcessPhotos(reportId)
        S-->>C: reportId
        C-->>U: 302 Redirect /reports/{id}
        U->>C: GET /reports/{id}
        C->>V: Details.cshtml + ViewModel
        V-->>U: HTML: "შეტყობინება მიღებულია"
    end
```

| კომპონენტი | პასუხისმგებლობა | Story-ები |
|------------|------------------|-----------|
| `AccountController` + Identity | რეგისტრაცია, შესვლა, ანგარიშის დაბლოკვა 5 მცდელობის შემდეგ | US-01, US-19 |
| `ReportsController` | შეტყობინების შექმნა, ჩემი შეტყობინებები, საჯარო რუკა, მხარდაჭერა | US-02, 03, 04, 06, 07 |
| `ManageController` | მენეჯერის სია ფილტრებით, მინიჭება, უარყოფა | US-08, 09, 10 |
| `TasksController` | ბრიგადის ამოცანები, სტატუსის განახლება, დასრულება ფოტოთი | US-11, US-12 |
| `AdminController` | მომხმარებლები, როლები, კატეგორიები, უწყებები | US-13, US-14 |
| `StatsController` | სტატისტიკა და CSV ექსპორტი | US-15 |
| Hangfire Jobs | ფოტოს შეკუმშვა და EXIF-ის წაშლა, ელფოსტა | US-05, NFR-3 |

## 3. Design Pattern-ები

### Backend

| Pattern | სად და რატომ |
|---------|---------------|
| **MVC** | საბაზისო pattern: Controller იღებს მოთხოვნას, Model ინახავს მონაცემებს და წესებს, View ხატავს HTML-ს. |
| **Repository + Unit of Work** | `IReportRepository` მალავს EF Core-ის მოთხოვნებს; `DbContext.SaveChangesAsync()` არის Unit of Work: სტატუსის ცვლილება და ისტორიის ჩანაწერი ერთ ტრანზაქციაში ინახება. ტესტებში Repository იცვლება mock-ით. |
| **Dependency Injection** | ASP.NET Core-ის ჩაშენებული DI: Controller იღებს `IReportService`-ს კონსტრუქტორში და არ იცის, რომელი კლასი დგას უკან. |
| **State** | შეტყობინების სასიცოცხლო ციკლი: `New → Accepted → InProgress → Resolved`, ასევე `New/Accepted → Rejected` და `Resolved → Accepted` (ხელახლა გახსნა, US-16). თითოეული მდგომარეობის კლასი თავად წყვეტს, რომელი გადასვლაა დაშვებული, ამიტომ `New → Resolved` შეუძლებელია და `if/else` ჯაჭვები არ გვჭირდება. |
| **Observer (Domain Events)** | `AssignmentService` აქვეყნებს მოვლენას `ReportStatusChanged` (MediatR notification), `EmailNotificationHandler` კი მას იჭერს და Hangfire-ში ამატებს ელფოსტის გაგზავნას. ახალი რეაქციის (მაგ. SMS) დამატება არსებულ კოდს არ ცვლის. |
| **Strategy** | `IFileStorage`: `LocalFileStorage` დეველოპმენტისთვის და `S3FileStorage` production-ისთვის; კონკრეტული კლასი `appsettings.json`-ით ირჩევა. |

### Frontend (Razor View-ები)

| Pattern | სად და რატომ |
|---------|---------------|
| **ViewModel** | View არასოდეს იღებს ბაზის Entity-ს პირდაპირ: `ReportCreateViewModel` შეიცავს მხოლოდ ფორმის ველებს და ვალიდაციის ატრიბუტებს (`[Required]`, `[StringLength(500, MinimumLength = 10)]`), `ReportDetailsViewModel` კი მოქალაქის კონტაქტს მხოლოდ თანამშრომლისთვის შეიცავს (NFR-5). |
| **Layout + Partial View** | `_Layout.cshtml` ერთი ნავიგაციით ყველა გვერდისთვის; `_ReportCard.cshtml` და `_StatusBadge.cshtml` ერთხელ იწერება და მოქალაქის, მენეჯერის და ბრიგადის გვერდებზე მეორდება. |
| **View Component** | `MyTasksCountViewComponent` აჩვენებს ბრიგადის აქტიური ამოცანების რაოდენობას მენიუში; საკუთარი ლოგიკა აქვს და Controller-ზე არ არის დამოკიდებული. |
| **Tag Helper** | `<form asp-action="Create">`, `<span asp-validation-for="Description">` ავტომატურად ამატებს მარშრუტს, CSRF ტოკენს და კლიენტის მხარის ვალიდაციას. |

## 4. Endpoint-ები (MVC მარშრუტები)

MVC-ში endpoint არის **Controller-ის action**, რომელიც აბრუნებს HTML-ს (View) ან გადამისამართებას (Redirect). წვდომა კონტროლდება ატრიბუტით `[Authorize(Roles = "...")]`, ფორმები დაცულია `[ValidateAntiForgeryToken]`-ით.

| # | მეთოდი და მარშრუტი | Controller.Action | ვის შეუძლია | აბრუნებს | Story |
|---|---------------------|-------------------|-------------|----------|-------|
| 1 | `POST /reports/create` | `ReportsController.Create` | მოქალაქე | Redirect დეტალებზე ან View შეცდომებით | US-02, US-03 |
| 2 | `GET /reports?status=&category=&mine=true&page=` | `ReportsController.Index` | ავტორიზებული | View: სია ფილტრებით | US-04, US-08 |
| 3 | `GET /reports/{id}` | `ReportsController.Details` | ავტორიზებული | View: დეტალები, ფოტოები, ისტორია | US-04, US-08 |
| 4 | `POST /manage/reports/{id}/assign` | `ManageController.Assign` | მენეჯერი | Redirect სიაზე + შეტყობინება | US-09 |
| 5 | `POST /tasks/{id}/status` | `TasksController.UpdateStatus` | მენეჯერი, ბრიგადა | Redirect ან 400/403/409 | US-10, 11, 12 |

დამატებით, რუკისთვის ერთი JSON endpoint (Leaflet-ი ნიშნულებს გვერდის გადატვირთვის გარეშე ტვირთავს):

| მეთოდი და მარშრუტი | Controller.Action | აბრუნებს | Story |
|---------------------|-------------------|----------|-------|
| `GET /api/map/reports?bbox=44.7,41.6,44.9,41.8&category=3` | `MapApiController.Get` | JSON: `[{ id, lat, lng, status, category }]`, ავტორის მონაცემების გარეშე | US-06 |

**მაგალითი: Controller-ის action**

```csharp
[Authorize(Roles = "Citizen")]
[HttpPost("reports/create"), ValidateAntiForgeryToken]
public async Task<IActionResult> Create(ReportCreateViewModel model)
{
    if (!ModelState.IsValid)
        return View(model);                       // ფორმა შეცდომებით (US-02, სცენარი 2)

    var id = await _reportService.CreateAsync(model, User.GetUserId());
    TempData["Success"] = "შეტყობინება მიღებულია";
    return RedirectToAction(nameof(Details), new { id });
}
```

**სტატუსის ცვლილების პასუხები (`POST /tasks/{id}/status`):**

| კოდი | როდის |
|------|-------|
| `302 Redirect` | გადასვლა დასაშვებია, მომხმარებელი ბრუნდება ამოცანების სიაზე |
| `400 Bad Request` | `Resolved` ფოტოს გარეშე (US-12): View ბრუნდება შეცდომით |
| `403 Forbidden` | თანამშრომელი ცდილობს სხვაზე მინიჭებული ამოცანის შეცვლას |
| `409 Conflict` | დაუშვებელი გადასვლა, მაგ. `New → Resolved` |

## 5. მონაცემთა ბაზა: SQL (PostgreSQL 16 + PostGIS)

**რატომ SQL და არა NoSQL:**
- მონაცემები მკაფიოდ რელაციურია: მომხმარებელი → შეტყობინება → მინიჭება → სტატუსების ისტორია → უწყება.
- სტატუსის ცვლილება და ისტორიის ჩანაწერი ერთ **ტრანზაქციაში** უნდა მოხდეს (ACID).
- **EF Core** და **ASP.NET Identity** რელაციურ ბაზაზეა აგებული: მიგრაციები, კავშირები და Identity-ს ცხრილები მზად მოდის.
- **PostGIS** (EF Core-ში NetTopologySuite-ით) იძლევა გეო-მოთხოვნებს: „ყველა შეტყობინება რუკის ხილულ არეში" ან „მსგავსი პრობლემები 50 მეტრის რადიუსში" (დუბლიკატების აღმოჩენა, US-07, US-10).
- სტატისტიკა (US-15) არის `GROUP BY` და აგრეგაციები, რაც SQL-ის ძლიერი მხარეა.

ფოტოები ბაზაში არ ინახება: ბაზაში არის მხოლოდ ბმული (`StorageKey`), თავად ფაილი კი ფაილების საცავშია.

### ER დიაგრამა

```mermaid
erDiagram
    DEPARTMENTS ||--o{ CATEGORIES : "ემსახურება"
    DEPARTMENTS ||--o{ USERS : "თანამშრომლები"
    USERS ||--o{ REPORTS : "ქმნის"
    USERS ||--o{ REPORTS : "მინიჭებულია"
    CATEGORIES ||--o{ REPORTS : "კატეგორია"
    REPORTS ||--o{ REPORT_PHOTOS : "ფოტოები"
    REPORTS ||--o{ STATUS_HISTORY : "ისტორია"
    USERS ||--o{ STATUS_HISTORY : "შეცვალა"
    REPORTS ||--o{ SUPPORTS : "მხარდაჭერა"
    USERS ||--o{ SUPPORTS : "უჭერს მხარს"

    USERS {
        text Id PK "AspNetUsers (Identity)"
        text Email UK
        text PasswordHash
        text FullName
        text PhoneNumber
        bigint DepartmentId FK
        boolean IsActive
        boolean NotifyByEmail
        timestamptz CreatedAt
    }
    DEPARTMENTS {
        bigint Id PK
        text Name UK
    }
    CATEGORIES {
        bigint Id PK
        text Name UK
        bigint DepartmentId FK
        boolean IsActive
    }
    REPORTS {
        bigint Id PK
        text Number UK
        text AuthorId FK
        bigint CategoryId FK
        text Description
        geography Location "Point, 4326"
        text Address
        text District
        text Status
        text AssigneeId FK
        date DueDate
        text RejectReason
        bigint DuplicateOfId FK
        smallint Rating "1-5"
        timestamptz CreatedAt
        timestamptz UpdatedAt
    }
    REPORT_PHOTOS {
        bigint Id PK
        bigint ReportId FK
        text StorageKey
        text Kind "Before | After"
        text UploadedById FK
        timestamptz CreatedAt
    }
    STATUS_HISTORY {
        bigint Id PK
        bigint ReportId FK
        text FromStatus
        text ToStatus
        text ChangedById FK
        text Comment
        timestamptz ChangedAt
    }
    SUPPORTS {
        bigint ReportId PK, FK
        text UserId PK, FK
        timestamptz CreatedAt
    }
```

როლები (`Citizen`, `Manager`, `Worker`, `Admin`) ინახება Identity-ს სტანდარტულ ცხრილებში `AspNetRoles` და `AspNetUserRoles`.

### Model (EF Core Entity)

```csharp
public enum ReportStatus { New, Accepted, InProgress, Resolved, Rejected }

public class Report
{
    public long Id { get; set; }
    public string Number { get; set; } = default!;          // FX-2026-001042
    public string AuthorId { get; set; } = default!;
    public ApplicationUser Author { get; set; } = default!;
    public long CategoryId { get; set; }
    public Category Category { get; set; } = default!;

    [StringLength(500, MinimumLength = 10)]
    public string Description { get; set; } = default!;
    public Point Location { get; set; } = default!;        // PostGIS, SRID 4326
    public string? Address { get; set; }

    public ReportStatus Status { get; set; } = ReportStatus.New;
    public string? AssigneeId { get; set; }
    public ApplicationUser? Assignee { get; set; }
    public DateOnly? DueDate { get; set; }
    public string? RejectReason { get; set; }
    public long? DuplicateOfId { get; set; }
    public short? Rating { get; set; }

    public List<ReportPhoto> Photos { get; set; } = new();
    public List<StatusHistory> History { get; set; } = new();
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
}
```

ინდექსები (`FixItDbContext.OnModelCreating`): GiST ინდექსი `Location`-ზე, კომპოზიტური ინდექსი `(Status, CategoryId, CreatedAt)` მენეჯერის სიისთვის და ინდექსი `AssigneeId`-ზე ბრიგადის ამოცანებისთვის.

## 6. ტექნოლოგიური სტეკი

| ფენა | ტექნოლოგია | რატომ |
|------|------------|-------|
| ფრეიმვორკი | **ASP.NET Core 8 MVC (C#)** | MVC, DI, ვალიდაცია, CSRF დაცვა ჩაშენებულია; LTS ვერსია |
| View | **Razor** (`.cshtml`), Bootstrap 5, Tag Helpers | რესპონსიული 360 px-დან (NFR-6), ფორმები და ვალიდაცია მინიმალური JS-ით |
| რუკა | **Leaflet + OpenStreetMap** | უფასოა, API გასაღებს არ საჭიროებს |
| ავტორიზაცია | **ASP.NET Core Identity** | რეგისტრაცია, როლები, ანგარიშის დაბლოკვა, პაროლის ჰეშირება (NFR-5) |
| ORM | **Entity Framework Core 8** + Npgsql + NetTopologySuite | მიგრაციები, LINQ მოთხოვნები, PostGIS მხარდაჭერა |
| ბაზა | **PostgreSQL 16 + PostGIS** | იხ. ნაწილი 5 |
| ფონური ამოცანები | **Hangfire** (PostgreSQL storage) | ცალკე Redis არ სჭირდება; აქვს dashboard ამოცანების სანახავად |
| ელფოსტა | MailKit + SMTP (US-05) | `IEmailSender` უკვე Sprint 0-დან: დეველოპმენტში sandbox (Mailtrap/Ethereal), production-ში SMTP ან Resend | ელფოსტა Sprint 1-შივე გვჭირდება (US-01: დადასტურება, US-13: მოწვევა); US-05 მხოლოდ სტატუსის შეტყობინებებს ამატებს |
| ფოტოები | ImageSharp (შეკუმშვა, EXIF-ის წაშლა), ლოკალური დისკი / S3-თავსებადი საცავი | NFR-3: ≤ 1 MB |
| ელფოსტა | MailKit + SMTP | US-05 |
| Event-ები | MediatR | Observer pattern, ReportStatusChanged |
| ტესტები | **xUnit**, Moq, `WebApplicationFactory` (ინტეგრაციული), Playwright, k6 (დატვირთვა, NFR-2) | DoD: დაფარვა ≥ 70% |
| DevOps | Docker, Docker Compose, **GitHub Actions** (build, test, deploy), Nginx | ერთი ბრძანებით გაშვება, CI ყოველ PR-ზე |

## 7. რისკები და მათი შემცირება

| # | რისკი | ალბათობა / გავლენა | შემცირება |
|---|-------|--------------------|-----------|
| 1 | **„მსუქანი" Controller-ები (Fat Controller).** MVC-ში ხშირი შეცდომაა, როცა ბიზნეს-ლოგიკა, ვალიდაცია და ბაზასთან მუშაობა პირდაპირ Controller-ში იწერება. კოდი ძნელად იტესტება და ერთი ცვლილება ბევრ ადგილს ეხება. | მაღალი / საშუალო | ყველა ლოგიკა Service ფენაშია, Controller-ის action არ აღემატება ~15 ხაზს; სტატუსის წესები State pattern-შია; code review-ში ეს DoD-ის ნაწილია. |
| 2 | **პერსონალური მონაცემები ფოტოებში.** ფოტოს EXIF-ში შეიძლება იყოს ზუსტი GPS და მოწყობილობის მონაცემები, კადრში კი ადამიანების სახეები და ავტომობილის ნომრები. ეს იურიდიული სამსახურის ვეტოს რისკია. | საშუალო / მაღალი | Hangfire job შლის EXIF-ს ყველა ფოტოდან; საჯარო რუკაზე ფოტო ჩანს მხოლოდ მოდერაციის შემდეგ; ViewModel-ები კონტაქტს მხოლოდ თანამშრომლებს აჩვენებს; შენახვის ვადა 3 წელი (NFR-3). |
| 3 | **სერვერზე დახატული გვერდების სისწრაფე და ერთი სერვერის ჩავარდნა.** ყოველი ფილტრის ცვლილება გვერდს თავიდან ტვირთავს, ერთი სერვერის გათიშვა კი მთელ სისტემას აჩერებს (NFR-1: 2 წამი, NFR-4: 99.9%). | საშუალო / საშუალო | Output Caching საჯარო რუკაზე, გვერდებად დაყოფა (20 ჩანაწერი), Response Compression, ბაზის ინდექსები; health-check და `restart: always`; ბაზის ყოველდღიური ბექაპი; აპლიკაცია stateless-ია (სესია cookie-ში), ამიტომ საჭიროებისას Nginx-ის უკან მეორე ინსტანსი ემატება. k6 ტესტით ვამოწმებთ 500 მომხმარებელს. |

## 8. პრეზენტაცია

სლაიდები: [docs/FixIt-Architecture.pptx](docs/FixIt-Architecture.pptx) (12 სლაიდი, ~13 წუთი; სპიკერის ტექსტი თითოეული სლაიდის შენიშვნებშია).
