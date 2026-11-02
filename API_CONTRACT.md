# FixIt — REST API Contract

**Base path:** `/api/v1`  
**Transport:** HTTPS  
**Formats:** JSON; `multipart/form-data` ფოტოს ატვირთვისას  
**Clients:** React Native Mobile App, Next.js Web Dashboard  
**Roles:** `Citizen`, `Manager`, `Worker`, `Admin`

ეს არის დაგეგმილი API კონტრაქტი და არა უკვე გაშვებული სერვერის აღწერა. Endpoint-ების იმპლემენტაციისას OpenAPI/Swagger სქემა ამ დოკუმენტთან სინქრონულად უნდა განახლდეს.

## 1. Authentication და Authorization

### 1.1 Mobile

Mobile client იყენებს ASP.NET Core Identity API-ის Bearer token რეჟიმს. Login response აბრუნებს მოკლევადიან access token-სა და refresh token-ს. Access token გადაეცემა `Authorization: Bearer <token>` header-ში; ტოკენები ინახება მოწყობილობის უსაფრთხო საცავში (`expo-secure-store`) და არა AsyncStorage-ში ან ჩვეულებრივ ფაილში.

**მნიშვნელოვანი:** ASP.NET Core Identity API-ის ჩაშენებული Bearer token proprietary token-ია და არა JWT. MVP-ის პირველი მხარის Mobile კლიენტისთვის ის საკმარისია. სტანდარტული OAuth2/OIDC/JWT საჭიროებისას ცალკე Identity Provider უნდა დაემატოს.

### 1.2 Web Dashboard

Next.js Dashboard იყენებს Secure, HttpOnly, SameSite Cookie session-ს. Cookie არ იკითხება JavaScript-იდან. State-changing მოთხოვნები იცავს Anti-Forgery/CSRF წესებს. API-ზე Web origin-ებისთვის CORS allowlist მკაფიოდ განისაზღვრება; `AllowAnyOrigin` credential-ებთან არ გამოიყენება.

### 1.3 საერთო წესები

- საჯარო რეგისტრაცია ქმნის მხოლოდ `Citizen` როლს.
- `Manager`, `Worker`, `Admin` ანგარიშებსა და როლებს ანიჭებს უფლებამოსილი Admin.
- ყველა დაცული endpoint ამოწმებს authentication-ს, role-ს და resource-level permission-ს.
- Citizen ხედავს მხოლოდ საკუთარ განაცხადებს; Worker მხოლოდ საკუთარ აქტიურ Assignment-ს; Manager — მხოლოდ საკუთარ Department-ის განაცხადებს.
- `401` ნიშნავს, რომ ავთენტიფიკაცია არ არსებობს/ვერ დადასტურდა; `403` — მომხმარებელი ცნობილია, მაგრამ უფლება არ აქვს.
- თარიღები იგზავნება ISO 8601 UTC ფორმატით.
- Pagination: `page` იწყება 1-დან; `pageSize` მაქსიმუმ 100.
- შეცდომები ბრუნდება `application/problem+json` სტანდარტის მიხედვით.

## 2. Error response

```json
{
  "type": "about:blank",
  "title": "Validation failed",
  "status": 400,
  "detail": "One or more fields are invalid.",
  "errors": {
    "description": ["Description must contain 10-500 characters."]
  }
}
```

## 3. MVP Endpoint-ები

### 3.1 რეგისტრაცია

`POST /api/v1/auth/register`  
**Access:** Public · **Content-Type:** `application/json`

Request:
```json
{
  "fullName": "Nino Example",
  "email": "nino@example.com",
  "password": "ExamplePassword123!",
  "phoneNumber": "+9955XXXXXXXX"
}
```

Response `201 Created`:
```json
{
  "userId": "c74fd6c0-6e8e-4e03-a0f5-29e1d21bd143",
  "email": "nino@example.com",
  "role": "Citizen",
  "emailConfirmationRequired": true
}
```

ვალიდაცია: Email უნიკალურია; Password მოწმდება Identity password policy-ით; Role request body-დან არ მიიღება — სერვერი ანიჭებს `Citizen`-ს.

### 3.2 Email confirmation

`POST /api/v1/auth/confirm-email`  
**Access:** Public · **Content-Type:** `application/json`

Request:
```json
{
  "userId": "c74fd6c0-6e8e-4e03-a0f5-29e1d21bd143",
  "code": "<encoded-email-confirmation-code>"
}
```

Response `200 OK`: `{ "emailConfirmed": true }`. Code უნდა იყოს ერთჯერადი/ვადიანი; მომხმარებლის არსებობა ზედმეტად არ უნდა გამჟღავნდეს.

### 3.3 შესვლა

`POST /api/v1/auth/login`  
**Access:** Public · **Content-Type:** `application/json`

Mobile request:
```json
{
  "email": "nino@example.com",
  "password": "ExamplePassword123!",
  "useCookies": false
}
```

Mobile response `200 OK` (Identity token response-ის შემოკლებული მაგალითი):
```json
{
  "tokenType": "Bearer",
  "accessToken": "<opaque-access-token>",
  "expiresIn": 3600,
  "refreshToken": "<opaque-refresh-token>"
}
```

Web client იყენებს Cookie რეჟიმს; Cookie-ის პარამეტრები და CSRF პროცესი სერვერის კონფიგურაციით განისაზღვრება.

### 3.4 Token refresh

`POST /api/v1/auth/refresh`  
**Access:** Mobile refresh token

Request:
```json
{ "refreshToken": "<opaque-refresh-token>" }
```

Response `200 OK`: ახალი access/refresh token წყვილი. ძველი refresh token აღარ უნდა იყოს განმეორებით გამოსაყენებელი, თუ გამოყენებული Identity token policy ამას უზრუნველყოფს; logout-ისას სესია/refresh token უქმდება.

### 3.5 Logout

`POST /api/v1/auth/logout`  
**Access:** Authenticated

Mobile: SecureStore-იდან access/refresh token-ების წაშლა. ჩაშენებული Identity token-ის დაუყოვნებლივი server-side revocation ცალკე არ არის გარანტირებული; მოკლე access-token lifetime ამცირებს რისკს. თუ სერვერზე მყისიერი გაუქმება მოთხოვნილია, დაემატოს DB-backed MobileSessions/revocation მექანიზმი. Web: Cookie session-ის sign-out და Anti-Forgery დაცვა.

### 3.6 მიმდინარე მომხმარებელი

`GET /api/v1/auth/me`  
**Access:** Authenticated

Response `200 OK`:
```json
{
  "id": "c74fd6c0-6e8e-4e03-a0f5-29e1d21bd143",
  "fullName": "Nino Example",
  "email": "nino@example.com",
  "role": "Citizen",
  "departmentId": null
}
```

### 3.7 განაცხადის შექმნა

`POST /api/v1/reports`  
**Access:** `Citizen` · **Content-Type:** `multipart/form-data`

Fields:

| Field | Type | Required | Validation |
|---|---|---:|---|
| `categoryId` | integer | yes | არსებული და აქტიური კატეგორია |
| `description` | string | yes | 10–500 სიმბოლო |
| `latitude` | decimal | yes | -90…90 |
| `longitude` | decimal | yes | -180…180 |
| `photos` | file[] | yes | 1–3 JPEG/PNG, თითოეული ≤10 MB |

Response `201 Created`:
```json
{
  "id": 1042,
  "number": "FX-2026-001042",
  "status": "New",
  "createdAt": "2026-11-03T10:30:00Z"
}
```

სერვერი ამოწმებს, რომ წერტილი ServiceArea/მუნიციპალიტეტის დასაშვებ საზღვრებშია. GPS permission უარყოფისას მომხმარებელს რუკაზე ხელით წერტილის მონიშვნა შეუძლია. EXIF metadata იშლება. Storage და DB ცალკე სისტემებია: ფაილი აიტვირთება, შემდეგ DB transaction ქმნის Report/Photo metadata-ს; DB შეცდომისას შესრულდება ფაილის კომპენსატორული წაშლა.

### 3.8 საკუთარი განაცხადები

`GET /api/v1/reports/mine?page=1&pageSize=20`  
**Access:** `Citizen`

Response `200 OK`:
```json
{
  "items": [
    {
      "id": 1042,
      "number": "FX-2026-001042",
      "category": "Street lighting",
      "status": "InProgress",
      "createdAt": "2026-11-03T10:30:00Z"
    }
  ],
  "page": 1,
  "pageSize": 20,
  "totalCount": 1
}
```

ReporterId მიიღება ავტორიზებული მომხმარებლის claim-იდან და არა query/body-დან.

### 3.9 განაცხადის დეტალები

`GET /api/v1/reports/{reportId}`  
**Access:** Report owner (`Citizen`) ან შესაბამისი `Manager`/მინიჭებული `Worker`.

Response შეიცავს განაცხადის ნომერს, კატეგორიას, აღწერას, კოორდინატებს, მიმდინარე სტატუსს, დასაშვებ ფოტოების ავტორიზებულ ბმულებსა და შესაბამის პასუხისმგებელ ინფორმაციას. პირადი მონაცემები როლების მიხედვით მინიმიზებულია.

### 3.10 სტატუსის ისტორია

`GET /api/v1/reports/{reportId}/history`  
**Access:** Report owner, შესაბამისი Manager ან მინიჭებული Worker.

Response `200 OK`:
```json
{
  "items": [
    { "from": null, "to": "New", "changedAt": "2026-11-03T10:30:00Z" },
    { "from": "New", "to": "Accepted", "changedAt": "2026-11-03T11:00:00Z" }
  ]
}
```

### 3.11 დისპეჩერის განაცხადების სია

`GET /api/v1/manager/reports?status=New&categoryId=2&district=Saburtalo&page=1&pageSize=20`  
**Access:** `Manager`

Response აბრუნებს მხოლოდ Manager-ის Department-ის ჩანაწერებს; ფილტრები და pagination სერვერზე სრულდება.

### 3.12 თანამშრომელზე მინიჭება / ხელახალი მინიჭება

`POST /api/v1/manager/reports/{reportId}/assignment`  
**Access:** `Manager` · **Content-Type:** `application/json`

Request:
```json
{
  "workerId": "worker-identity-id",
  "dueDate": "2026-11-10",
  "reason": "საწყისი მინიჭება ან გადანაწილების მიზეზი"
}
```

Response `200 OK`:
```json
{
  "reportId": 1042,
  "status": "Accepted",
  "activeWorkerId": "worker-identity-id",
  "assignedAt": "2026-11-03T11:00:00Z"
}
```

წესები: `New` განაცხადის პირველი მინიჭება ქმნის Assignment-ს და სტატუსს ცვლის `Accepted`-ზე. თუ Report უკვე `Accepted`-ია, Manager-ს შეუძლია Worker-ის შეცვლა — ძველი Assignment იხურება (`EndedAt`), ახალი იქმნება და მიზეზი ინახება. `InProgress` ან `Resolved` სტატუსში გადანაწილება MVP-ში აკრძალულია. Worker უნდა იყოს აქტიური და იმავე Department-ს/Service Area-ს ეკუთვნოდეს. პარალელური ცვლილება → `409 Conflict`.

### 3.13 Worker-ის დავალებები

`GET /api/v1/worker/tasks?status=Accepted&page=1&pageSize=20`  
**Access:** `Worker`

სერვერი აბრუნებს მხოლოდ მიმდინარე მომხმარებლის აქტიურ Assignment-ებს.

### 3.14 სამუშაოს დაწყება

`PATCH /api/v1/worker/tasks/{reportId}/status`  
**Access:** Assigned `Worker`

Request:
```json
{ "status": "InProgress" }
```

დასაშვებია მხოლოდ `Accepted → InProgress`. `Resolved` მნიშვნელობის მოთხოვნა ამ endpoint-ით უარყოფილია.

### 3.15 დასრულების ფოტოს ატვირთვა

`POST /api/v1/worker/tasks/{reportId}/completion-photo`  
**Access:** Assigned `Worker` · **Content-Type:** `multipart/form-data`

Field: `photo` — ერთი JPEG/PNG, ≤10 MB. Report უნდა იყოს `InProgress`; ატვირთული ფოტო `Completion` ტიპით ინახება. მხოლოდ ფაილის წარმატებით შენახვისა და metadata-ს რეგისტრაციის შემდეგ ხდება `Resolved` სტატუსზე გადასვლა და StatusHistory ჩანაწერის დამატება.

Response `200 OK`:
```json
{
  "reportId": 1042,
  "status": "Resolved",
  "completionPhotoId": 987,
  "resolvedAt": "2026-11-03T15:00:00Z"
}
```

### 3.16 Admin — მომხმარებლების შექმნა, სია და როლის მართვა

`POST /api/v1/admin/users` — `Admin` only, ქმნის თანამშრომლის ანგარიშს და აგზავნის მოწვევას/პაროლის დაყენების ბმულს.  
`GET /api/v1/admin/users?page=1&pageSize=20` — `Admin` only.  
`PATCH /api/v1/admin/users/{userId}/role` — `Admin` only.

Request:
```json
{ "role": "Worker", "departmentId": 3 }
```

საჯარო მომხმარებელი საკუთარ როლს ვერ ცვლის. მინიმუმ ერთი აქტიური Admin-ის დაკარგვა უნდა აიცილოს ადმინისტრაციულმა წესმა.

### 3.17 Admin — ანგარიშის აქტიურობა

`PATCH /api/v1/admin/users/{userId}/status` — `Admin` only.

Request:
```json
{ "isActive": false }
```

გათიშული მომხმარებელი ვეღარ ავთენტიფიცირდება; მისი ძველი Assignment/StatusHistory ჩანაწერები რჩება აუდიტისთვის.

## 4. მომავალი ფუნქციების Endpoint-ები

| Story | Endpoint | Priority |
|---|---|---|
| US-05 Email notification preference | `PATCH /api/v1/users/me/notification-preferences` | Should |
| US-06 Public issue map | `GET /api/v1/map/reports?bbox=...` | Should |
| US-07 Support existing issue | `POST /api/v1/reports/{id}/support` and `DELETE /api/v1/reports/{id}/support` | Could |
| US-10 Reject/duplicate review | `PATCH /api/v1/manager/reports/{id}/review` | Should |
| US-14 Categories/departments | `POST/GET/PATCH /api/v1/admin/categories` და `/departments` | Should |
| US-15 Analytics | `GET /api/v1/admin/analytics/summary` | Could |
| US-16 Rating | `POST /api/v1/reports/{id}/rating` | Could |
| US-19 Password recovery | Identity password recovery endpoints | Should |
| US-20 Reopen request | `POST /api/v1/reports/{id}/reopen-request`; `PATCH /api/v1/manager/reopen-requests/{id}` | Could |

US-20-ის მოთხოვნა არ ცვლის Report status-ს დაუყოვნებლივ. ის ქმნის ცალკე ReopenRequest-ს `Pending` სტატუსით. Manager-ის დამტკიცებისას Report გადადის `Accepted`-ზე და იქმნება ახალი Assignment/Workflow; უარყოფისას Report რჩება `Resolved`.

## 5. HTTP Status Codes

| Code | გამოყენება |
|---|---|
| 200 | წარმატებული მოთხოვნა |
| 201 | ახალი რესურსი შეიქმნა |
| 204 | წარმატებული ოპერაცია პასუხის body-ის გარეშე |
| 400 | ვალიდაციის შეცდომა ან აკრძალული status transition |
| 401 | ავტორიზაცია არ არსებობს/არასწორია |
| 403 | როლი ან resource permission არ ჰყოფნის |
| 404 | რესურსი არ არსებობს ან არ უნდა გამჟღავნდეს მომხმარებლისთვის |
| 409 | პარალელური ცვლილების/მდგომარეობის კონფლიქტი |
| 413 | ფაილი ზედმეტად დიდია |
| 415 | MIME/file type დაუშვებელია |
| 500 | მოულოდნელი სერვერული შეცდომა; დეტალები კლიენტს არ ეცნობება |

## 6. Backlog-თან შესაბამისობა

| Story | ძირითადი API |
|---|---|
| US-01 | register, login, me |
| US-02/03 | POST reports (multipart, coordinates, service-area validation) |
| US-04 | reports/mine, reports/{id}, reports/{id}/history |
| US-08 | manager/reports |
| US-09 | manager/reports/{id}/assignment |
| US-11 | worker/tasks, worker/tasks/{id}/status |
| US-12 | worker/tasks/{id}/completion-photo |
| US-13 | admin/users, admin/users/{id}/role, admin/users/{id}/status |
| US-18 | auth/session, app config and profile endpoints; app shell consumes shared API |

## 7. Implementation notes

- API response-ში EF Core Entity პირდაპირ არ დაბრუნდეს; გამოიყენე Request/Response DTO.
- Multipart upload-ზე შეამოწმე content type, magic bytes, file size და image decoder; მხოლოდ ფაილის გაფართოებას ნუ ენდობი.
- Rate limiting გამოიყენე login/register და report creation endpoint-ებზე.
- API versioning და OpenAPI schema განახლდეს კონტრაქტის ცვლილებისას.
- Cookie + Bearer authentication სქემები მკაფიოდ გაიმიჯნოს endpoint policy-ებით; CORS allowlist იყოს მხოლოდ საჭირო Web origin-ებზე.
