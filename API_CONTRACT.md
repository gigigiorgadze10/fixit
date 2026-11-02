# FixIt — REST API Contract

**Base path:** `/api/v1`  
**Format:** JSON (ფაილის ატვირთვისას `multipart/form-data`)  
**Authentication:** ASP.NET Core Identity cookie authentication  
**Authorization:** role-based (`Citizen`, `Manager`, `Worker`, `Admin`)

ეს კონტრაქტი აღწერს მეორე პრაქტიკული დავალებისთვის საჭირო REST API-ს. Endpoint-ები იმავე ASP.NET Core აპლიკაციაში იმუშავებს, სადაც Razor MVC გვერდებიცაა.

## 1. საერთო წესები

- წარმატებული JSON პასუხები იყენებს შესაბამის HTTP status code-ს.
- შეცდომის პასუხები ერთიან ფორმატში ბრუნდება.
- ყველა თარიღი/დრო გადაეცემა ISO 8601 UTC ფორმატით.
- ყველა დაცული Endpoint ამოწმებს მომხმარებლის ანგარიშსა და როლს.
- მოქალაქეს შეუძლია მხოლოდ საკუთარი განაცხადის ნახვა; თანამშრომელს — მხოლოდ საკუთარ თავზე მინიჭებული დავალების შეცვლა.
- ფოტოები ინახება კერძო Object Storage-ში; API აბრუნებს დროებით/ავტორიზებულ ბმულს ან დაცულ download endpoint-ს და არა საჯარო storage path-ს.

### Error response

```json
{
  "type": "https://httpstatuses.com/400",
  "title": "Validation failed",
  "status": 400,
  "detail": "One or more fields are invalid.",
  "errors": {
    "description": ["Description must contain 10-500 characters."]
  }
}
```

## 2. ძირითადი Endpoint-ები

### 2.1 რეგისტრაცია

`POST /api/v1/auth/register`  
**Access:** Public  
**Content-Type:** `application/json`

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
  "userId": "identity-user-id",
  "email": "nino@example.com",
  "role": "Citizen"
}
```

ვალიდაცია: ელფოსტა უნიკალურია; პაროლი მოწმდება Identity-ის პოლიტიკით; საჯარო რეგისტრაცია ქმნის მხოლოდ `Citizen` როლს. სხვა როლს მომხმარებელი თვითონ ვერ მიანიჭებს თავს.

### 2.2 შესვლა

`POST /api/v1/auth/login`  
**Access:** Public  
**Content-Type:** `application/json`

Request:

```json
{
  "email": "nino@example.com",
  "password": "ExamplePassword123!"
}
```

Response `200 OK`:

```json
{
  "userId": "identity-user-id",
  "fullName": "Nino Example",
  "role": "Citizen"
}
```

სესიის Cookie იგზავნება `Secure`, `HttpOnly` და შესაბამისი `SameSite` პარამეტრებით. Cookie-ზე დაფუძნებულ state-changing მოთხოვნებზე გამოიყენება Anti-Forgery დაცვა.

### 2.3 პრობლემის განაცხადის შექმნა

`POST /api/v1/reports`  
**Access:** `Citizen`  
**Content-Type:** `multipart/form-data`

Fields:

| Field | Type | Required | Validation |
|---|---|---|---|
| `categoryId` | integer | yes | არსებული და აქტიური კატეგორია |
| `description` | string | yes | 10–500 სიმბოლო |
| `latitude` | decimal | yes | -90…90 |
| `longitude` | decimal | yes | -180…180 |
| `photos` | file[] | yes | 1–3 JPEG/PNG ფაილი; თითოეული ≤ 10 MB |

Response `201 Created`:

```json
{
  "id": 1042,
  "number": "FX-2026-001042",
  "status": "New",
  "createdAt": "2026-11-03T10:30:00Z"
}
```

ფოტოები მოწმდება MIME/type-ისა და ზომის მიხედვით. EXIF იშლება შენახვამდე. განაცხადი და ფოტოების მეტამონაცემები ინახება თანმიმდევრულად; ფაილის საცავში წარუმატებლობისას API არ აბრუნებს წარმატებულ შექმნას.

### 2.4 მოქალაქის განაცხადების სია

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

სერვერი მომხმარებლის ID-ს იღებს ავტორიზებული სესიიდან და არა Query ან Request Body-დან.

### 2.5 დისპეჩერის განაცხადების სია

`GET /api/v1/manager/reports?status=New&categoryId=2&district=Saburtalo&page=1&pageSize=20`  
**Access:** `Manager`

Response `200 OK`:

```json
{
  "items": [
    {
      "id": 1042,
      "number": "FX-2026-001042",
      "category": "Street lighting",
      "description": "Street light is not working.",
      "status": "New",
      "district": "Saburtalo",
      "latitude": 41.7151,
      "longitude": 44.8271,
      "createdAt": "2026-11-03T10:30:00Z"
    }
  ],
  "page": 1,
  "pageSize": 20,
  "totalCount": 1
}
```

მენეჯერი ხედავს მხოლოდ იმ უწყების განაცხადებს, რომელზეც უფლებამოსილია.

### 2.6 თანამშრომელზე მინიჭება

`POST /api/v1/manager/reports/{reportId}/assignment`  
**Access:** `Manager`  
**Content-Type:** `application/json`

Request:

```json
{
  "assigneeId": "worker-identity-id",
  "dueDate": "2026-11-10"
}
```

Response `200 OK`:

```json
{
  "reportId": 1042,
  "status": "Accepted",
  "assigneeId": "worker-identity-id",
  "assignedAt": "2026-11-03T11:00:00Z"
}
```

წესები: განაცხადი უნდა იყოს `New`; თანამშრომელი აქტიური უნდა იყოს და იმავე შესაბამის უწყებას ეკუთვნოდეს; მინიჭება და სტატუსის ისტორია ინახება ერთ ტრანზაქციაში. უკვე შეცვლილი ჩანაწერის პარალელური მინიჭებისას ბრუნდება `409 Conflict`.

### 2.7 თანამშრომლის დავალებების სია

`GET /api/v1/worker/tasks?status=Accepted&page=1&pageSize=20`  
**Access:** `Worker`

Response `200 OK`:

```json
{
  "items": [
    {
      "reportId": 1042,
      "number": "FX-2026-001042",
      "description": "Street light is not working.",
      "status": "Accepted",
      "dueDate": "2026-11-10",
      "latitude": 41.7151,
      "longitude": 44.8271
    }
  ],
  "page": 1,
  "pageSize": 20,
  "totalCount": 1
}
```

სერვერი აბრუნებს მხოლოდ ავტორიზებული თანამშრომლისთვის მინიჭებულ დავალებებს.

### 2.8 დავალების დაწყება

`PATCH /api/v1/worker/tasks/{reportId}/status`  
**Access:** `Worker`  
**Content-Type:** `application/json`

Request:

```json
{
  "status": "InProgress"
}
```

Response `200 OK`:

```json
{
  "reportId": 1042,
  "status": "InProgress",
  "changedAt": "2026-11-03T12:00:00Z"
}
```

MVP-ში Worker-ს ამ Endpoint-ით შეუძლია `Accepted → InProgress` გადასვლა. `Resolved` სტატუსის პირდაპირ მოთხოვნა უარყოფილია.

### 2.9 სამუშაოს დასრულების დადასტურება

`POST /api/v1/worker/tasks/{reportId}/completion-photo`  
**Access:** `Worker`  
**Content-Type:** `multipart/form-data`

Field: `photo` — ერთი JPEG/PNG ფაილი, მაქსიმუმ 10 MB.

Response `200 OK`:

```json
{
  "reportId": 1042,
  "status": "Resolved",
  "completionPhotoId": 987,
  "resolvedAt": "2026-11-03T15:00:00Z"
}
```

სისტემა ამოწმებს, რომ დავალება ავტორიზებულ Worker-ზეა მინიჭებული და მიმდინარე სტატუსია `InProgress`. ფოტოს შენახვის დადასტურების შემდეგ სტატუსი და ისტორია ერთ ტრანზაქციაში იცვლება.

### 2.10 საჯარო რუკის მონაცემები

`GET /api/v1/map/reports?minLat=41.6&minLng=44.7&maxLat=41.8&maxLng=44.9&categoryId=2`  
**Access:** Public — მხოლოდ იმ შემთხვევაში, თუ US-06 განხორციელებულია.

Response `200 OK` აბრუნებს მხოლოდ გამოქვეყნებისთვის დაშვებულ განაცხადებს, კოორდინატებს, კატეგორიასა და სტატუსს. ავტორის სახელი, ელფოსტა, ტელეფონი და კერძო StorageKey პასუხში არ შედის. `New` და `Rejected` განაცხადები საჯარო რუკაზე არ ჩანს.

## 3. HTTP Status Codes

| Code | გამოყენება |
|---|---|
| `200 OK` | მოთხოვნა წარმატებით შესრულდა |
| `201 Created` | ახალი რესურსი შეიქმნა |
| `400 Bad Request` | ვალიდაციის შეცდომა ან არასწორი გადასვლა |
| `401 Unauthorized` | მომხმარებელი ავტორიზებული არ არის |
| `403 Forbidden` | ავტორიზებულია, მაგრამ როლი/წვდომა არ ჰყოფნის |
| `404 Not Found` | რესურსი არ არსებობს ან მომხმარებლისთვის მიუწვდომელია |
| `409 Conflict` | სტატუსი ან ჩანაწერი შეიცვალა პარალელური მოთხოვნისას |
| `413 Payload Too Large` | ატვირთული ფაილი დაშვებულ ზომას აჭარბებს |
| `415 Unsupported Media Type` | ფაილის ფორმატი დაუშვებელია |
| `500 Internal Server Error` | მოულოდნელი სერვერული შეცდომა; დეტალები ლოგში ინახება |

## 4. Story-ებთან შესაბამისობა

| User Story | Endpoint |
|---|---|
| US-01 | `POST /auth/register`, `POST /auth/login` |
| US-02, US-03 | `POST /reports` |
| US-04 | `GET /reports/mine` |
| US-05 | Notification Service — სტატუსის ცვლილების event |
| US-06 | `GET /map/reports` |
| US-08 | `GET /manager/reports` |
| US-09 | `POST /manager/reports/{id}/assignment` |
| US-10 | დამატებითი `PATCH /manager/reports/{id}/review` — Should Have |
| US-11 | `GET /worker/tasks`, `PATCH /worker/tasks/{id}/status` |
| US-12 | `POST /worker/tasks/{id}/completion-photo` |
| US-13 | Admin-only user/role management endpoints — MVP ადმინისტრირების ოპერაციები |
| US-14 | Admin-only category/department endpoints — Should Have |
| US-15 | Statistics endpoint — Could Have |
| US-16 | `PATCH /reports/{id}/rating` — Could Have |
| US-19 | Password reset endpoints — Should Have |
