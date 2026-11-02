# FixIt — Technology Stack Rationale

| Layer | Technology | Why it is selected |
|---|---|---|
| Mobile | React Native + Expo + TypeScript | Android/iOS ერთი საერთო TypeScript codebase-ით; camera, location, secure storage და navigation-ის მზა native modules |
| Mobile routing | Expo Router | file-based navigation, deep links და route groups |
| Mobile secure storage | Expo SecureStore | access/refresh token-ების მოწყობილობის დაცულ საცავში შენახვა |
| Mobile photo | Expo ImagePicker | კამერა/გალერეა და ფოტო selection |
| Mobile location | Expo Location | GPS permission და კოორდინატები |
| Mobile map | react-native-maps | map view და marker selection; provider/key configuration ცალკე საჭიროა |
| Web | Next.js App Router + TypeScript | ცხრილები, filters, management pages და role-specific dashboard |
| Backend | ASP.NET Core 10 Web API | typed controllers, DI, authorization, validation და OpenAPI |
| Auth | ASP.NET Core Identity API | account management; Mobile Bearer token, Web Cookie |
| ORM | EF Core 10 + Npgsql | migrations, typed data access და PostgreSQL |
| Spatial | PostGIS + NetTopologySuite | service-area geofence და spatial queries |
| DB | PostgreSQL | relational integrity, indexes, transaction და JSON საჭიროების შემთხვევაში |
| File storage | S3-compatible private object storage | ფოტოები იზოლირებულია relational DB-ისგან |
| API docs | OpenAPI/Swagger | endpoint contract და interactive test |
| Backend test | xUnit + WebApplicationFactory | unit/API integration tests |
| Mobile test | React Native Testing Library | screen/component tests |
| Web E2E | Playwright | Dispatcher/Admin main flows |
| Load test | k6 | 100 VU NFR verification |
| DevOps | Docker Compose + GitHub Actions | repeatable local stack and CI |

## Setup principles

- Expo/React Native SDK და Next.js ვერსიები შეირჩეს პროექტის შექმნის დღეს არსებული stable release-იდან; `npx expo install` გამოიყენე Expo SDK-სთან თავსებადი native package version-ებისთვის.
- .NET SDK, EF Core და Npgsql provider major versions შეინარჩუნე თავსებადი.
- ყველა secrets გარემოს ცვლადებში/CI secrets-ში ინახება; არ დაამატო `.env`, access token ან DB password Git-ში.
- Maps provider-ის გამოყენების პირობები, API key და billing/quota წინასწარ გადაამოწმე.
- Mobile token storage გამოიყენებს SecureStore-ს, არა AsyncStorage-ს.
