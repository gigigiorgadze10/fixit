# FixIt: პროგრამული არქიტექტურა

| | |
|---|---|
| სისტემის სტილი | Client-Server |
| Backend-ის სტილი | Layered Modular Monolith |
| მობილური კლიენტი | React Native + Expo + TypeScript (Android/iOS) |
| ვებ-პანელი | Next.js App Router + TypeScript |
| Backend | ASP.NET Core 10 Web API |
| მონაცემთა ბაზა | PostgreSQL + PostGIS |
| ფაილები | Azure Blob Storage, private container |
| ჰოსტინგი | Azure |

## 1. არქიტექტურული გადაწყვეტილება

FixIt-ს აქვს ორი კლიენტი და ერთი Backend. მოქალაქე და საველე თანამშრომელი ტელეფონით მუშაობენ და სჭირდებათ კამერა, GPS და რუკა, ამიტომ მათთვის კეთდება მობილური აპლიკაცია. დისპეჩერსა და ადმინისტრატორს სჭირდებათ დიდი ცხრილები, ფილტრები და მართვის ფორმები, ამიტომ მათთვის კეთდება ვებ-პანელი. Backend არის ერთი ASP.NET Core Web API, რომლის შიგნით კოდი ფენებად და ბიზნესმოდულებად არის დაყოფილი.

**რატომ ეს არქიტექტურა:**

1. **მომხმარებლის საჭიროება.** კამერა, GPS და ტოკენის უსაფრთხო შენახვა მობილური აპლიკაციის ბუნებრივი შესაძლებლობებია, ხოლო დისპეჩერის ცხრილური სამუშაო ვებში უფრო მოსახერხებელია.
2. **ერთი ბიზნესლოგიკა.** ორივე კლიენტი ერთ API-ს იყენებს, ამიტომ განაცხადის, მინიჭებისა და სტატუსის წესები ერთ ადგილას სრულდება, ხოლო PostgreSQL-ის ერთი ტრანზაქცია ინახავს სტატუსს და მის ისტორიას ერთად.
3. **სემესტრის მასშტაბი.** ერთი deploy-ადი Backend და ერთი ბაზა ერთ ადამიანს შეუძლია სამ თვეში ააწყოს და მართოს.

**განხილული ალტერნატივები:**

| ალტერნატივა | რატომ არ აირჩა |
|---|---|
| მხოლოდ responsive ვებსაიტი ან PWA | არ იძლევა ინსტალირებად აპს და კამერის/GPS-ის/SecureStore-ის სრულ ინტეგრაციას; PWA სამომავლო ალტერნატივაა |
| Flutter + ვებ-პანელი | კარგი ვარიანტია, მაგრამ TypeScript ორივე კლიენტში ამცირებს ერთი ადამიანის სამუშაოს |
| მიკროსერვისები | Reports, Assignments და StatusHistory მჭიდროდ არის დაკავშირებული; განაწილებული ტრანზაქციები და ცალკე deploy ზედმეტი სირთულეა |
| MongoDB | მონაცემები რელაციურია და საჭიროებს Foreign Key-ებს და ტრანზაქციებს |
| საკუთარი JWT გამცემი | უსაფრთხოების რისკი; გამოიყენება ASP.NET Core Identity-ის ჩაშენებული ტოკენები |

**შედეგები:** ორი Frontend კოდბაზის მოვლა, Android/iOS ტესტირება და API კონტრაქტის სტაბილურობის საჭიროება. ამას ამცირებს ერთი ენა (TypeScript) კლიენტებში და აქ აღწერილი API კონტრაქტი.

## 2. კომპონენტების დიაგრამა

```mermaid
flowchart TB
    CIT[მოქალაქე] --> MOB
    WRK[საველე თანამშრომელი] --> MOB
    DSP[დისპეჩერი] --> WEB
    ADM[ადმინი] --> WEB

    subgraph CLIENTS[კლიენტები]
      MOB[React Native + Expo<br/>Android / iOS]
      WEB[Next.js ვებ-პანელი]
    end

    MOB -->|HTTPS, REST, Bearer token| API
    WEB -->|HTTPS, REST, Cookie<br/>Next.js proxy /api| API

    subgraph BACKEND[ASP.NET Core 10 Web API]
      API[Controllers, DTO ვალიდაცია, ავტორიზაცია]
      APP[Application Services]
      ID[Identity & Access]
      REP[Reports]
      DIS[Dispatch & Assignments]
      WF[Tasks & Status Workflow]
      CAT[Departments & Categories]
      ATT[Attachments]
      API --> APP
      APP --> ID & REP & DIS & WF & CAT & ATT
    end

    APP --> DB[(PostgreSQL + PostGIS)]
    ATT --> BLOB[(Azure Blob Storage<br/>private)]
    APP -.-> MAIL[ელფოსტის სერვისი]
    MOB --> DEV[კამერა, GPS, SecureStore]
    MOB --> MAP[რუკის ფილები]
    WEB --> MAP
```

ელფოსტა MVP-ში გამოიყენება ელფოსტის დადასტურებისა (US-01) და თანამშრომლის მოწვევისთვის (US-13). Push-შეტყობინებები MVP-ში არ შედის.

## 3. ტექნოლოგიები

| ფენა | ტექნოლოგია | რატომ |
|---|---|---|
| მობილური | React Native + Expo + TypeScript | Android და iOS ერთი კოდით; მზა მოდულები კამერისთვის, მდებარეობისთვის და ნავიგაციისთვის |
| მობილური მოდულები | Expo Router, ImagePicker, Location, SecureStore | ნავიგაცია, კამერა/გალერეა, GPS, ტოკენის დაცული შენახვა (არა AsyncStorage) |
| მობილური რუკა | react-native-maps | რუკა და წერტილის მონიშვნა |
| ვები | Next.js App Router + TypeScript, Leaflet | ცხრილები, ფილტრები, მართვის გვერდები, რუკა |
| Backend | ASP.NET Core 10 Web API | DI, ავტორიზაცია, ვალიდაცია, OpenAPI |
| ავთენტიფიკაცია | ASP.NET Core Identity | პაროლის ჰეში (PBKDF2), ბლოკირება, ელფოსტის დადასტურება, Bearer და Cookie სქემები |
| ORM | EF Core 10 + Npgsql + NetTopologySuite | migrations, ტიპიზებული წვდომა, PostGIS ტიპები |
| ბაზა | PostgreSQL + PostGIS | რელაციური მთლიანობა, ტრანზაქციები, მუნიციპალიტეტის საზღვრის შემოწმება |
| ფაილები | Azure Blob Storage (ლოკალურად Azurite) | ფოტოები ბაზისგან ცალკე; მოკლევადიანი SAS ბმულები |
| სურათის დამუშავება | ImageSharp | ფორმატის შემოწმება, EXIF-ის წაშლა, შეკუმშვა |
| ტესტები | xUnit + WebApplicationFactory, React Native Testing Library, Playwright, k6 | Backend, მობილური, ვები, დატვირთვა |
| DevOps | Docker Compose, GitHub Actions, Dependabot | ერთნაირი ლოკალური გარემო, CI, დამოკიდებულებების განახლება |
| მონიტორინგი | Application Insights, uptime მონიტორი | ლოგები, შეცდომები, ხელმისაწვდომობა (NFR-02) |

ვერსიები ფიქსირდება Sprint 0-ში იმ დღის stable გამოშვებებით; Expo-ს native პაკეტები ყენდება `npx expo install`-ით. Secrets (connection string, storage key) არ ინახება Git-ში: ლოკალურად `dotnet user-secrets`, CI-ში GitHub Secrets, Azure-ში App Settings.

## 4. Backend

### 4.1 ფენები

| ფენა | პასუხისმგებლობა | მაგალითები |
|---|---|---|
| Presentation | HTTP, DTO ვალიდაცია, ავტორიზაციის policy-ები, HTTP კოდები | ReportsController, ManagerReportsController, WorkerTasksController |
| Application | use case-ები და ორკესტრაცია | CreateReport, AssignWorker, StartTask, CompleteTask |
| Domain | ბიზნესობიექტები და წესები | Report, Assignment, ReportStatusRules |
| Infrastructure | ტექნიკური ინტეგრაციები | EF Core DbContext, Identity, BlobFileStorage, SmtpEmailSender |

### 4.2 მოდულები

- **Identity & Access:** რეგისტრაცია, შესვლა, ტოკენის განახლება, გასვლა, როლები.
- **Reports:** განაცხადის შექმნა, მოქალაქის სია, დეტალები, ისტორია.
- **Dispatch & Assignments:** დისპეჩერის სია, მინიჭება და გადანაწილება.
- **Tasks & Workflow:** თანამშრომლის დავალებები და სტატუსის გადასვლები.
- **Departments & Categories:** უწყებები, კატეგორიები, მომსახურების არეალები.
- **Attachments:** ფოტოს შემოწმება, EXIF-ის წაშლა, Blob Storage.
- **Notifications:** ელფოსტა (US-05, Should have).

### 4.3 Design Patterns

- **Service Layer / Use Case.** Controller არ შეიცავს ბიზნესლოგიკას: ამოწმებს DTO-ს, იძახებს Application Service-ს და აბრუნებს პასუხს. მაგალითად `AssignWorkerService` ამოწმებს სტატუსს, დისპეჩერის უწყებას და თანამშრომლის აქტიურობას.
- **State Transition Policy.** `ReportStatusRules` ერთ ადგილას ინახავს დაშვებულ გადასვლებს (ნაწილი 8). აკრძალული გადასვლა აბრუნებს 409-ს.
- **Unit of Work.** EF Core-ის ერთი `SaveChangesAsync` ინახავს Report-ის ცვლილებას და StatusHistory-ს ერთად. Generic Repository ყველა ცხრილისთვის არ იქმნება.
- **Dependency Injection და ადაპტერები.** `IFileStorage` (ლოკალურად Azurite, production-ში Blob Storage) და `IEmailSender` (dev-ში sandbox, production-ში SMTP სერვისი) DI-ით მიეწოდება, ამიტომ ტესტებში ადვილად იცვლება.

## 5. Frontend

### 5.1 მობილური: MVVM-ის მსგავსი სტრუქტურა + Repository

ეკრანი (Screen) მხოლოდ UI-ს აჩვენებს. ViewModel-ის როლს ასრულებს feature hook, რომელიც მართავს loading/error/data მდგომარეობას და მომხმარებლის მოქმედებებს. Repository მალავს HTTP-ს დეტალებს, ამიტომ ეკრანი პირდაპირ API-ს არ იძახებს.

```text
mobile/
  app/                    Expo Router-ის ეკრანები
  src/features/
    auth/                 შესვლა, რეგისტრაცია, hook-ები, repository
    reports/              შექმნა, სია, დეტალები
    tasks/                თანამშრომლის დავალებები, დასრულების ფოტო
  src/shared/
    api/                  ტიპიზებული API client
    storage/              SecureStore-ის wrapper
    components/
```

### 5.2 ვები: Feature-based სტრუქტურა

Next.js პანელი იყოფა feature-ებად: `reports`, `assignments`, `users`, `categories`. საერთო API client, auth guard და კომპონენტები `shared`-შია. Server Components იღებს საწყის მონაცემებს, ფილტრები და ფორმები Client Components-შია. Next.js `rewrites` გადაამისამართებს `/api/*` მოთხოვნებს Backend-ზე, ამიტომ ავტორიზაციის Cookie ბრაუზერისთვის იმავე origin-ის Cookie-ა და CORS არ არის საჭირო.

## 6. ავტორიზაცია და უსაფრთხოება

- საჯარო რეგისტრაცია ქმნის მხოლოდ `Citizen` როლს; დანარჩენ როლებს ანიჭებს Admin.
- მობილური: ASP.NET Core Identity-ის Bearer token (access + refresh), ინახება SecureStore-ში. ეს ტოკენი JWT არ არის.
- ვები: Secure, HttpOnly Cookie და Anti-Forgery დაცვა.
- პაროლი ≥ 8 სიმბოლო; 5 წარუმატებელი მცდელობის შემდეგ ანგარიში 15 წუთით იბლოკება.
- ყოველი დაცული მოთხოვნა ამოწმებს როლს და რესურსის მფლობელობას; ღილაკის დამალვა UI-ში დაცვა არ არის.
- ფოტოს საჯარო ბმული არ არსებობს: API აბრუნებს 15-წუთიან SAS ბმულს.

## 7. REST API

### 7.1 წესები

- Base path: `/api/v1`; მხოლოდ HTTPS; JSON, ფოტოსთვის `multipart/form-data`.
- თარიღები ISO 8601 UTC. Pagination: `page` 1-დან, `pageSize` ≤ 100.
- შეცდომები: `application/problem+json`.
- Entity პირდაპირ არ ბრუნდება, მხოლოდ Request/Response DTO. OpenAPI სქემა განახლდება ყოველ ცვლილებაზე.
- ფაილი მოწმდება ზომით, magic bytes-ით და image decoder-ით, არა მხოლოდ გაფართოებით.

### 7.2 MVP endpoint-ები

| Method | Endpoint | წვდომა | დანიშნულება | Story |
|---|---|---|---|---|
| POST | `/auth/register` | საჯარო | მოქალაქის რეგისტრაცია (`fullName`, `email`, `password`, `phoneNumber`) | US-01 |
| POST | `/auth/confirm-email` | საჯარო | ელფოსტის დადასტურება ერთჯერადი კოდით | US-01 |
| POST | `/auth/login` | საჯარო | `useCookies: false` აბრუნებს Bearer ტოკენებს (მობილური), `true` აყენებს Cookie-ს (ვები) | US-01 |
| POST | `/auth/refresh` | მობილური | ახალი access/refresh წყვილი | US-18 |
| POST | `/auth/logout` | ავტორიზებული | სესიის დასრულება | US-18 |
| GET | `/auth/me` | ავტორიზებული | მიმდინარე მომხმარებელი, როლი, უწყება | US-18 |
| GET | `/categories` | ავტორიზებული | აქტიური კატეგორიები ფორმისთვის | US-02 |
| POST | `/reports` | Citizen | განაცხადის შექმნა ფოტოებით და კოორდინატებით | US-02, US-03 |
| GET | `/reports/mine` | Citizen | საკუთარი განაცხადები | US-04 |
| GET | `/reports/{id}` | მფლობელი, უწყების Manager, მინიჭებული Worker | დეტალები და ფოტოების SAS ბმულები | US-04, US-08 |
| GET | `/reports/{id}/history` | იგივე | სტატუსის ისტორია | US-04 |
| GET | `/manager/reports` | Manager | უწყების განაცხადები; ფილტრები `status`, `categoryId`, `serviceAreaId`, `from`, `to` | US-08 |
| GET | `/manager/workers` | Manager | უწყების აქტიური თანამშრომლები მინიჭებისთვის | US-09 |
| POST | `/manager/reports/{id}/assignment` | Manager | მინიჭება ან გადანაწილება | US-09 |
| GET | `/worker/tasks` | Worker | საკუთარი აქტიური დავალებები | US-11 |
| PATCH | `/worker/tasks/{reportId}/status` | მინიჭებული Worker | მხოლოდ `Accepted` → `InProgress` | US-11 |
| POST | `/worker/tasks/{reportId}/completion` | მინიჭებული Worker | დასრულების ფოტო და კომენტარი, სტატუსი `Resolved` | US-12 |
| POST | `/admin/users` | Admin | თანამშრომლის ანგარიში და მოწვევის წერილი | US-13 |
| GET | `/admin/users` | Admin | მომხმარებლების სია | US-13 |
| PATCH | `/admin/users/{id}/role` | Admin | როლი და უწყება | US-13 |
| PATCH | `/admin/users/{id}/status` | Admin | ანგარიშის გათიშვა ან აღდგენა | US-13 |
| GET | `/health` | საჯარო | ხელმისაწვდომობის შემოწმება (ბაზასთან კავშირით) | NFR-02 |

MVP-ის შემდეგი ფუნქციების endpoint-ები (US-05, 06, 07, 10, 14, 15, 16, 19, 20) დაემატება იმავე წესით, როცა შესაბამისი Story სპრინტში მოხვდება. შეცდომები ბრუნდება სტანდარტული HTTP კოდებით: 400 ვალიდაცია, 401/403 წვდომა, 404 არ არსებობს, 409 დაუშვებელი სტატუსის ცვლილება, 413/415 ფაილის ზომა ან ფორმატი.

## 8. სტატუსები და ბიზნესწესები

```mermaid
stateDiagram-v2
  [*] --> New: მოქალაქე ქმნის
  New --> Accepted: დისპეჩერი ანიჭებს თანამშრომელს
  New --> Rejected: დისპეჩერი უარყოფს (US-10)
  Accepted --> InProgress: თანამშრომელი იწყებს
  InProgress --> Resolved: დასრულების ფოტო შენახულია
  Resolved --> Accepted: დამტკიცებული ხელახლა გახსნა (US-20)
  Rejected --> [*]
  Resolved --> [*]
```

- **გადანაწილება** შესაძლებელია მხოლოდ `Accepted` სტატუსში: ძველი Assignment იხურება (`EndedAt`), იქმნება ახალი და ინახება მიზეზი. `InProgress` და `Resolved` სტატუსში გადანაწილება აბრუნებს 409-ს.
- **დუბლიკატი** ცალკე სტატუსი არ არის: ეს არის `Rejected` მიზეზით "დუბლიკატი" და `DuplicateOfId`-ით.
- **`Resolved`** მოითხოვს მინიმუმ ერთ `Completion` ფოტოს.
- **ხელახლა გახსნის მოთხოვნა** (US-20) სტატუსს მაშინვე არ ცვლის: იქმნება `Pending` ReopenRequest, და მხოლოდ დისპეჩერის დამტკიცებისას Report ბრუნდება `Accepted`-ში.
- ყოველი სტატუსის ცვლილება და StatusHistory-ს ჩანაწერი ერთ ტრანზაქციაში ინახება.

## 9. მონაცემთა ბაზა

### 9.1 რატომ PostgreSQL + PostGIS

მონაცემები რელაციურია: მომხმარებელი ქმნის Report-ს, Report-ს აქვს Category და ServiceArea, ასევე რამდენიმე Assignment, ფოტო და ისტორიის ჩანაწერი. საჭიროა Foreign Key-ები, შეზღუდვები და ტრანზაქციები. PostGIS გამოიყენება ორ ადგილას: წერტილი მუნიციპალიტეტის საზღვარშია თუ არა (US-03) და რუკის მართკუთხედში მოხვედრილი განაცხადები (US-06).

### 9.2 ცხრილები

Identity იყენებს ASP.NET Core Identity-ის სტანდარტულ ცხრილებს (`AspNetUsers`, `AspNetRoles`, `AspNetUserRoles` ...). `AppUser` ამატებს ველებს `FullName`, `DepartmentId`, `IsActive`, `NotifyByEmail` (US-05).

| ცხრილი | ძირითადი ველები | დანიშნულება |
|---|---|---|
| Departments | Id, Name, IsActive | უწყებები |
| Categories | Id, DepartmentId, Name, IsActive | კატეგორია და პასუხისმგებელი უწყება |
| ServiceAreas | Id, DepartmentId, Name, Boundary | მომსახურების არეალი (უბანი), `geometry(MultiPolygon,4326)` |
| Reports | Id, Number, ReporterId, CategoryId, ServiceAreaId, Description, Location, Status, RejectReason, DuplicateOfId, CreatedAt, UpdatedAt | განაცხადი; `Location` არის `geometry(Point,4326)` |
| Assignments | Id, ReportId, WorkerId, AssignedById, AssignedAt, DueDate, EndedAt, ReassignmentReason | მინიჭებების სრული ისტორია |
| ReportPhotos | Id, ReportId, Kind, StorageKey, MimeType, SizeBytes, UploadedById, CreatedAt | ფოტოს მეტამონაცემები (`Submission` / `Completion`) |
| StatusHistory | Id, ReportId, FromStatus, ToStatus, ChangedById, ChangedAt, Comment | სტატუსის ცვლილებების აუდიტი; დასრულების კომენტარი |
| ReportSupports | ReportId, CitizenId, CreatedAt | US-07, MVP-ის შემდეგ |
| ReportRatings | Id, ReportId, CitizenId, Rating (1-5), CreatedAt | US-16, MVP-ის შემდეგ |
| ReopenRequests | Id, ReportId, RequestedById, Reason, Status, ReviewedById, ReviewedAt, ReviewComment | US-20, MVP-ის შემდეგ |

### 9.3 ER დიაგრამა (MVP)

```mermaid
erDiagram
    DEPARTMENTS ||--o{ APP_USERS : employs
    DEPARTMENTS ||--o{ CATEGORIES : owns
    DEPARTMENTS ||--o{ SERVICE_AREAS : manages
    CATEGORIES ||--o{ REPORTS : classifies
    SERVICE_AREAS ||--o{ REPORTS : contains
    APP_USERS ||--o{ REPORTS : creates
    REPORTS ||--o{ ASSIGNMENTS : has
    APP_USERS ||--o{ ASSIGNMENTS : "works on / assigns"
    REPORTS ||--o{ REPORT_PHOTOS : contains
    APP_USERS ||--o{ REPORT_PHOTOS : uploads
    REPORTS ||--o{ STATUS_HISTORY : tracks
    APP_USERS ||--o{ STATUS_HISTORY : changes

    DEPARTMENTS {
        bigint Id PK
        varchar Name UK
        boolean IsActive
    }
    APP_USERS {
        uuid Id PK
        varchar FullName
        bigint DepartmentId FK
        boolean IsActive
        boolean NotifyByEmail
    }
    CATEGORIES {
        bigint Id PK
        bigint DepartmentId FK
        varchar Name
        boolean IsActive
    }
    SERVICE_AREAS {
        bigint Id PK
        bigint DepartmentId FK
        varchar Name
        geometry Boundary
    }
    REPORTS {
        bigint Id PK
        varchar Number UK
        uuid ReporterId FK
        bigint CategoryId FK
        bigint ServiceAreaId FK
        varchar Description
        geometry Location
        varchar Status
        varchar RejectReason
        bigint DuplicateOfId FK
        timestamptz CreatedAt
        timestamptz UpdatedAt
    }
    ASSIGNMENTS {
        bigint Id PK
        bigint ReportId FK
        uuid WorkerId FK
        uuid AssignedById FK
        timestamptz AssignedAt
        date DueDate
        timestamptz EndedAt
        varchar ReassignmentReason
    }
    REPORT_PHOTOS {
        bigint Id PK
        bigint ReportId FK
        varchar Kind
        varchar StorageKey UK
        varchar MimeType
        bigint SizeBytes
        uuid UploadedById FK
        timestamptz CreatedAt
    }
    STATUS_HISTORY {
        bigint Id PK
        bigint ReportId FK
        varchar FromStatus
        varchar ToStatus
        uuid ChangedById FK
        timestamptz ChangedAt
        varchar Comment
    }
```

### 9.4 მონაცემთა წესები

1. `Reports.Number` უნიკალურია (`FX-2026-001042`) და იქმნება sequence-დან.
2. `Categories.DepartmentId` სავალდებულოა: კატეგორია განსაზღვრავს, რომელი უწყების დისპეჩერი ხედავს განაცხადს.
3. `Location`: SRID 4326, X = longitude, Y = latitude. შემოწმება სერვერზე `ST_Covers(boundary, location)`-ით, რომ საზღვარზე მდებარე წერტილიც დაშვებული იყოს.
4. ერთ Report-ს ერთდროულად მაქსიმუმ ერთი აქტიური Assignment აქვს (partial unique index). ორი დისპეჩერის ერთდროული მინიჭება ერთ-ერთს აძლევს 409-ს. Report-ის სტატუსის ცვლილებას იცავს optimistic concurrency (`xmin`).
5. თანამშრომელი და დისპეჩერი ერთ უწყებას უნდა ეკუთვნოდნენ.
6. მომხმარებელი არ იშლება, მხოლოდ ითიშება (`IsActive = false`), რომ ისტორია შენარჩუნდეს; Foreign Key-ები `ON DELETE RESTRICT`.
7. საჯარო რუკის DTO არ შეიცავს ავტორს, კონტაქტს და `StorageKey`-ს.

### 9.5 ფოტოების შენახვა

1. API ამოწმებს ზომას, magic bytes-ს და ფაილს ხსნის ImageSharp-ით; EXIF იშლება და ფოტო იკუმშება.
2. ფაილი იტვირთება Blob Storage-ის private container-ში შემთხვევითი `StorageKey`-ით.
3. შემდეგ ერთი DB ტრანზაქცია ქმნის Report-ს (ან სტატუსის ცვლილებას), ReportPhotos-ს და StatusHistory-ს.
4. თუ ტრანზაქცია ჩავარდა, ატვირთული ფაილი იშლება; ღამის ფონური ამოცანა (`BackgroundService`) შლის ფაილებს, რომლებსაც ბაზაში ჩანაწერი არ აქვთ.

Blob Storage და PostgreSQL ერთ ACID ტრანზაქციაში ვერ ერთიანდება, ამიტომ თანმიმდევრულობას ეს ოთხი ნაბიჯი უზრუნველყოფს.

## 10. Deployment და DevOps

- **ლოკალურად:** Docker Compose (PostgreSQL + PostGIS, Azurite), ვები `npm run dev`, მობილური Expo-ით.
- **staging და production:** Azure. API და ვები App Service-ზე (Basic, SLA 99.95%), ბაზა PostgreSQL Flexible Server-ზე (zonal HA, SLA 99.95%, ავტომატური ბექაპი 7 დღე), ფოტოები Blob Storage-ში.
- **ხელმისაწვდომობა (NFR-02):** 99.95% × 99.95% ≈ 99.9%, ანუ თვეში დაახლოებით 43 წუთი. ბაზა HA-ს გარეშე მხოლოდ 99.9%-ს იძლევა, რაც ჯამში ≈ 99.85%-ია, ამიტომ production-ში HA საჭიროა. Free/Shared გეგმებს SLA არ აქვთ.
- **CI/CD (GitHub Actions):** ყოველ Pull Request-ზე build და ტესტები; merge `main`-ში აშვებს staging-ს; production ხელით, Sprint Review-ს შემდეგ.
- **მობილური:** Android APK რეალურ ტელეფონზე, iOS სიმულატორი; App Store-ში გამოქვეყნება ფარგლებს გარეთაა.
