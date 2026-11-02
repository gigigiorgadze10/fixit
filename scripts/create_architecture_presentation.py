from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs' / 'FixIt-Architecture.pptx'
OUT.parent.mkdir(parents=True, exist_ok=True)

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
BLANK = prs.slide_layouts[6]
FONT = 'Noto Sans Georgian'
BG = RGBColor(13, 22, 39)
PANEL = RGBColor(25, 39, 61)
PANEL2 = RGBColor(31, 52, 77)
WHITE = RGBColor(245, 248, 252)
MUTED = RGBColor(174, 190, 209)
TEAL = RGBColor(48, 190, 173)
BLUE = RGBColor(84, 151, 232)
ORANGE = RGBColor(240, 160, 75)
PURPLE = RGBColor(165, 135, 224)
RED = RGBColor(229, 105, 110)
GREEN = RGBColor(105, 190, 132)


def add_bg(slide):
    fill = slide.background.fill
    fill.solid(); fill.fore_color.rgb = BG


def textbox(slide, x, y, w, h, text, size=16, color=WHITE, bold=False, align=PP_ALIGN.LEFT, font=FONT):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.clear(); tf.word_wrap = True
    tf.margin_left = Inches(0.04); tf.margin_right = Inches(0.04)
    tf.margin_top = Inches(0.02); tf.margin_bottom = Inches(0.02)
    p = tf.paragraphs[0]; p.alignment = align
    r = p.add_run(); r.text = text
    r.font.name = font; r.font.size = Pt(size); r.font.bold = bold; r.font.color.rgb = color
    return box


def rect(slide, x, y, w, h, text, fill=PANEL, line=PANEL2, color=WHITE, size=14, bold=False, radius=True, align=PP_ALIGN.CENTER):
    shape_type = MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE
    sh = slide.shapes.add_shape(shape_type, Inches(x), Inches(y), Inches(w), Inches(h))
    sh.fill.solid(); sh.fill.fore_color.rgb = fill
    sh.line.color.rgb = line; sh.line.width = Pt(1.1)
    tf = sh.text_frame; tf.clear(); tf.word_wrap = True
    tf.margin_left = Inches(0.10); tf.margin_right = Inches(0.10)
    tf.margin_top = Inches(0.06); tf.margin_bottom = Inches(0.04)
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]; p.alignment = align
    r = p.add_run(); r.text = text
    r.font.name = FONT; r.font.size = Pt(size); r.font.bold = bold; r.font.color.rgb = color
    return sh


def line(slide, x1, y1, x2, y2, color=MUTED, width=1.5, arrow=True):
    c = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    c.line.color.rgb = color; c.line.width = Pt(width)
    if arrow:
        try:
            from pptx.enum.dml import MSO_ARROWHEAD
            c.line.end_arrowhead = MSO_ARROWHEAD.TRIANGLE
        except Exception:
            pass
    return c


def header(slide, title, subtitle=None, number=None):
    textbox(slide, 0.55, 0.28, 12.1, 0.52, title, 25, WHITE, True)
    if subtitle:
        textbox(slide, 0.58, 0.86, 12.0, 0.42, subtitle, 11, MUTED)
    sh = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.58), Inches(1.30), Inches(12.15), Inches(0.025))
    sh.fill.solid(); sh.fill.fore_color.rgb = TEAL; sh.line.fill.background()
    textbox(slide, 0.58, 7.12, 9.5, 0.22, 'FixIt • DevOps and Software Engineering • Architecture', 8, MUTED)
    if number:
        textbox(slide, 12.25, 7.10, 0.45, 0.22, str(number), 9, MUTED, align=PP_ALIGN.RIGHT)


def bullet_block(slide, x, y, w, h, title, bullets, accent=TEAL, size=14):
    rect(slide, x, y, w, h, '', fill=PANEL, line=PANEL2)
    textbox(slide, x+0.18, y+0.12, w-0.36, 0.34, title, 16, accent, True)
    yy = y+0.60
    for b in bullets:
        textbox(slide, x+0.20, yy, w-0.38, 0.46, '• ' + b, size, WHITE)
        yy += 0.52

# Slide 1 — cover
s = prs.slides.add_slide(BLANK); add_bg(s)
textbox(s, 0.75, 0.85, 4.0, 0.35, 'SOFTWARE ARCHITECTURE • SCENARIO D', 11, TEAL, True)
textbox(s, 0.75, 1.65, 7.2, 1.05, 'FixIt', 48, WHITE, True)
textbox(s, 0.80, 2.70, 7.3, 0.95, 'მუნიციპალური პრობლემების\nშეტყობინებისა და მართვის სისტემა', 24, WHITE, True)
textbox(s, 0.82, 4.28, 6.7, 0.70, 'Native Mobile App + Web Dashboard + Shared API', 17, TEAL, True)
textbox(s, 0.82, 6.38, 6.7, 0.35, 'ავტორი: გიგი გიორგაძე', 12, MUTED)
rect(s, 8.7, 1.0, 3.6, 1.10, 'React Native + Expo\nAndroid / iOS', fill=PANEL2, line=BLUE, size=16, bold=True)
rect(s, 8.7, 2.55, 3.6, 1.10, 'Next.js\nDispatcher / Admin', fill=PANEL2, line=PURPLE, size=16, bold=True)
rect(s, 8.7, 4.10, 3.6, 1.10, 'ASP.NET Core 10 Web API', fill=PANEL2, line=TEAL, size=16, bold=True)
rect(s, 8.7, 5.65, 3.6, 0.90, 'PostgreSQL + PostGIS', fill=PANEL2, line=ORANGE, size=16, bold=True)
for yy in [2.10,3.65,5.20]: line(s, 10.5, yy, 10.5, yy+0.43, MUTED)

# Slide 2 — problem and roles
s = prs.slides.add_slide(BLANK); add_bg(s); header(s, '1. პროდუქტის მიზანი და მომხმარებლები', 'FixIt ციფრულად აერთიანებს პრობლემის დაფიქსირებას, გადანაწილებასა და შესრულების კონტროლს.', 2)
bullet_block(s, 0.75, 1.65, 5.65, 4.85, 'პრობლემა', [
    'ინფორმაცია ტელეფონებსა და სოციალურ ქსელებში იკარგება.',
    'მოქალაქემ არ იცის, ვინ ამუშავებს განაცხადს და მოგვარდა თუ არა პრობლემა.',
    'მუნიციპალიტეტს არ აქვს ერთიანი ისტორია და პასუხისმგებლობის ჯაჭვი.'
], ORANGE, 15)
bullet_block(s, 6.80, 1.65, 5.75, 4.85, 'მომხმარებლები', [
    'Citizen — ფოტო, კატეგორია, GPS, განაცხადის სტატუსი.',
    'Field Worker — დავალებები, სამუშაოს დაწყება და დასრულების ფოტო.',
    'Dispatcher — განაცხადების ფილტრი, შემოწმება და მინიჭება.',
    'Admin — ანგარიშები, როლები და სისტემური კონფიგურაცია.'
], TEAL, 14)

# Slide 3 — style and rationale
s = prs.slides.add_slide(BLANK); add_bg(s); header(s, '2. არქიტექტურული სტილის არჩევა', 'სისტემის დონეზე Client–Server; Backend-ის შიგნით Layered Modular Monolith.', 3)
rect(s, 0.80, 1.75, 3.65, 1.35, 'Client–Server\nMobile + Web clients', fill=PANEL2, line=BLUE, size=18, bold=True)
rect(s, 4.85, 1.75, 3.65, 1.35, 'Layered Modular Monolith\nერთი ASP.NET Core API', fill=PANEL2, line=TEAL, size=17, bold=True)
rect(s, 8.90, 1.75, 3.65, 1.35, 'PostgreSQL + PostGIS\nერთი მონაცემთა წყარო', fill=PANEL2, line=ORANGE, size=17, bold=True)
bullet_block(s, 0.80, 3.55, 3.65, 2.65, 'რატომ?', ['ტელეფონი საჭიროებს camera/GPS-ს.', 'დისპეჩერს სჭირდება დიდი Web Dashboard.'], BLUE, 13)
bullet_block(s, 4.85, 3.55, 3.65, 2.65, 'რატომ?', ['ერთიანი ბიზნესლოგიკა.', 'მარტივი deployment და ტრანზაქციები.'], TEAL, 13)
bullet_block(s, 8.90, 3.55, 3.65, 2.65, 'რატომ?', ['Reports/Assignments/History რელაციურია.', 'PostGIS ამოწმებს Service Area-ს.'], ORANGE, 13)

# Slide 4 — component diagram
s = prs.slides.add_slide(BLANK); add_bg(s); header(s, '3. კომპონენტების დიაგრამა', 'ორივე კლიენტი იყენებს ერთ API-ს; UI-ში დამალვა არ წარმოადგენს უსაფრთხოების კონტროლს.', 4)
rect(s, 0.85, 1.60, 3.30, 0.80, 'React Native + Expo\nCitizen / Worker', fill=PANEL2, line=BLUE, size=15, bold=True)
rect(s, 9.15, 1.60, 3.30, 0.80, 'Next.js Dashboard\nDispatcher / Admin', fill=PANEL2, line=PURPLE, size=15, bold=True)
rect(s, 4.75, 2.90, 3.80, 0.85, 'HTTPS / REST API\nASP.NET Core 10', fill=PANEL2, line=TEAL, size=16, bold=True)
line(s, 2.50, 2.40, 5.55, 2.90, BLUE); line(s, 10.80, 2.40, 7.80, 2.90, PURPLE)
mods = [('Identity & Access',0.75),('Reports',3.05),('Dispatch / Assignments',5.35),('Tasks / Workflow',7.65),('Attachments',9.95)]
for label,x in mods:
    rect(s,x,4.25,2.05,0.78,label,fill=PANEL,line=PANEL2,size=12,bold=True)
    line(s,6.65,3.75,x+1.0,4.25,TEAL,1.0)
rect(s, 2.25, 5.75, 3.50, 0.82, 'PostgreSQL + PostGIS', fill=PANEL2, line=ORANGE, size=15, bold=True)
rect(s, 7.50, 5.75, 3.50, 0.82, 'Private Object Storage', fill=PANEL2, line=ORANGE, size=15, bold=True)
line(s,4.10,5.03,4.0,5.75,ORANGE); line(s,10.95,5.03,9.3,5.75,ORANGE)

# Slide 5 — backend layers
s = prs.slides.add_slide(BLANK); add_bg(s); header(s, '4. Backend-ის ფენები და მოდულები', 'Controller იღებს მოთხოვნას; Application Service ასრულებს use case-ს; Domain იცავს წესებს.', 5)
rect(s, 1.0, 1.65, 11.3, 0.88, 'Presentation Layer  •  API Controllers • DTO Validation • Authorization', fill=PANEL2, line=BLUE, size=16, bold=True)
rect(s, 1.0, 2.85, 11.3, 0.88, 'Application Layer  •  CreateReport • AssignWorker • StartTask • CompleteTask', fill=PANEL2, line=TEAL, size=16, bold=True)
rect(s, 1.0, 4.05, 11.3, 0.88, 'Domain Layer  •  Report • Assignment • ReportStatusRules • Invariants', fill=PANEL2, line=PURPLE, size=16, bold=True)
rect(s, 1.0, 5.25, 11.3, 0.88, 'Infrastructure Layer  •  EF Core • PostgreSQL/PostGIS • Identity • Object Storage', fill=PANEL2, line=ORANGE, size=16, bold=True)
for yy in [2.53,3.73,4.93]: line(s,6.65,yy,6.65,yy+0.30,MUTED,1.4)

# Slide 6 — API + Auth
s = prs.slides.add_slide(BLANK); add_bg(s); header(s, '5. API და Authentication', 'API აბსტრაქცია ორივე კლიენტისთვის ერთნაირ ბიზნეს წესებს უზრუნველყოფს.', 6)
bullet_block(s, 0.8, 1.65, 5.65, 4.85, 'Mobile App', [
    'Identity Bearer token რეჟიმი.',
    'Access token — Authorization header-ში.',
    'Refresh token — სესიის განახლებისთვის.',
    'ტოკენები ინახება Expo SecureStore-ში.'
], BLUE, 14)
bullet_block(s, 6.85, 1.65, 5.65, 4.85, 'Web Dashboard', [
    'Secure + HttpOnly + SameSite Cookie.',
    'State-changing მოთხოვნებზე Anti-Forgery/CSRF.',
    'CORS allowlist მხოლოდ საჭირო origin-ებზე.',
    'Backend ამოწმებს role-სა და resource ownership-ს.'
], PURPLE, 14)
textbox(s, 1.05, 6.63, 11.1, 0.30, 'შენიშვნა: ASP.NET Core Identity-ის ჩაშენებული Bearer token proprietary token-ია და არა JWT.', 11, ORANGE, True, align=PP_ALIGN.CENTER)

# Slide 7 — data model
s = prs.slides.add_slide(BLANK); add_bg(s); header(s, '6. მონაცემთა ბაზის მოდელი', 'PostgreSQL ინახავს ურთიერთობებს; PostGIS გამოიყენება გეოგრაფიული შემოწმებისთვის.', 7)
# ER blocks
rect(s,0.75,1.65,2.25,0.86,'AppUsers / Roles',fill=PANEL2,line=BLUE,size=13,bold=True)
rect(s,3.45,1.65,2.25,0.86,'Departments\nCategories',fill=PANEL2,line=TEAL,size=13,bold=True)
rect(s,6.15,1.65,2.25,0.86,'ServiceAreas\n(MultiPolygon)',fill=PANEL2,line=ORANGE,size=13,bold=True)
rect(s,8.85,1.65,2.25,0.86,'Reports\n(Point)',fill=PANEL2,line=PURPLE,size=13,bold=True)
rect(s,2.10,3.75,2.45,0.86,'Assignments\n(active + history)',fill=PANEL2,line=BLUE,size=13,bold=True)
rect(s,5.25,3.75,2.45,0.86,'ReportPhotos\nSubmission / Completion',fill=PANEL2,line=TEAL,size=12,bold=True)
rect(s,8.40,3.75,2.45,0.86,'StatusHistory',fill=PANEL2,line=ORANGE,size=13,bold=True)
line(s,2.95,2.51,3.2,3.75,BLUE); line(s,4.55,2.51,4.0,3.75,TEAL); line(s,7.25,2.51,9.9,1.65,ORANGE); line(s,9.98,2.51,6.45,3.75,PURPLE)
line(s,10.0,2.51,9.6,3.75,PURPLE)
textbox(s,0.9,5.25,11.5,0.90,'მნიშვნელოვანი წესები: ერთი აქტიური Assignment თითო Report-ზე; Resolved მოითხოვს Completion ფოტოს; StatusHistory ინახება სტატუსის ცვლილებასთან ერთად; StorageKey ინახება DB-ში, ფაილი — private Object Storage-ში.',13,WHITE,False,align=PP_ALIGN.CENTER)

# Slide 8 — patterns
s = prs.slides.add_slide(BLANK); add_bg(s); header(s, '7. Design Patterns', 'Backend, Mobile და Web პასუხისმგებლობები განცალკევებულია.', 8)
bullet_block(s,0.80,1.65,3.75,4.85,'Backend',[ 'Service Layer / Use Case — business logic controller-ის გარეთ.', 'State Transition Policy — დასაშვები სტატუსები.', 'Unit of Work — Report + StatusHistory ერთ DB transaction-ში.' ],TEAL,13)
bullet_block(s,4.80,1.65,3.75,4.85,'Mobile',[ 'MVVM-inspired — UI და მდგომარეობის ლოგიკა განცალკევებულია.', 'Repository — API კომუნიკაციის აბსტრაქცია.', 'Secure storage — session tokens დაცულ საცავში.' ],BLUE,13)
bullet_block(s,8.80,1.65,3.75,4.85,'Web',[ 'Feature-based structure — reports, assignments, users.', 'Shared API client და reusable components.', 'Server/Client Components შესაბამისი ამოცანის მიხედვით.' ],PURPLE,13)

# Slide 9 — NFR and risks
s = prs.slides.add_slide(BLANK); add_bg(s); header(s, '8. ხარისხი, უსაფრთხოება და რისკები', 'რიცხვითი მოთხოვნები უნდა დამტკიცდეს ტესტებით და არა ვარაუდით.', 9)
bullet_block(s,0.75,1.60,5.75,4.95,'NFR სამიზნეები',[ '100 VU-ზე API GET p95 ≤ 2 წამი.', '100 VU-ზე error rate < 1%.', '1–3 JPEG/PNG ფოტო; თითოეული ≤ 10 MB.', 'Mobile ≥ 360 dp; Web ≥ 1024 CSS px.', 'დაცული API-ების 100%-ზე 401/403 და ownership ტესტები.' ],TEAL,13)
bullet_block(s,6.80,1.60,5.75,4.95,'ძირითადი რისკები',[ 'OS/device განსხვავება → Android/iOS smoke tests.', 'GPS შეცდომა → ხელით რუკაზე მონიშვნა + server geofence.', 'EXIF/privacy → metadata stripping + private storage.', 'Storage/DB failure → compensation + orphan cleanup.' ],ORANGE,13)

# Slide 10 — stack and MVP
s = prs.slides.add_slide(BLANK); add_bg(s); header(s, '9. ტექნოლოგიური სტეკი და MVP', 'Mobile-First არქიტექტურა არის ერთი API-ით დაკავშირებული ორი კლიენტი.', 10)
stack = [
    ('Mobile','React Native + Expo + TypeScript'),
    ('Web','Next.js App Router + TypeScript'),
    ('Backend','ASP.NET Core 10 Web API'),
    ('Data','EF Core 10 + PostgreSQL + PostGIS'),
    ('Storage / Maps','Private S3-compatible storage; native/web map clients'),
    ('Testing / DevOps','xUnit, Playwright, RN Testing Library, k6; Docker + GitHub Actions'),
]
for i,(a,b) in enumerate(stack):
    yy=1.60+i*0.70
    rect(s,0.85,yy,2.15,0.52,a,fill=PANEL2,line=TEAL,size=13,bold=True)
    rect(s,3.15,yy,5.35,0.52,b,fill=PANEL,line=PANEL2,size=12,align=PP_ALIGN.LEFT)
rect(s,9.0,1.75,3.15,1.25,'MVP\n10 Must Have Stories\n39 Story Points',fill=PANEL2,line=GREEN,size=18,bold=True)
rect(s,9.0,3.35,3.15,1.05,'Full Backlog\n20 Stories / 74 SP',fill=PANEL2,line=ORANGE,size=17,bold=True)
rect(s,9.0,4.75,3.15,1.05,'Push Notifications\nFuture scope',fill=PANEL2,line=PURPLE,size=15,bold=True)

# Slide 11 — references
s = prs.slides.add_slide(BLANK); add_bg(s); header(s, 'ტექნიკური წყაროები', 'ტექნოლოგიური გადაწყვეტილებები დაფუძნებულია ოფიციალურ დოკუმენტაციაზე.', 11)
refs = [
    'React Native: reactnative.dev/docs/environment-setup',
    'Expo: docs.expo.dev/get-started/create-a-project',
    'Next.js App Router: nextjs.org/docs/app',
    'ASP.NET Core Identity API: learn.microsoft.com/aspnet/core/security/authentication/identity-api-authorization',
    'EF Core Spatial: learn.microsoft.com/ef/core/modeling/spatial',
    'Npgsql PostGIS: npgsql.org/efcore/mapping/nts.html',
]
for i,ref in enumerate(refs):
    textbox(s,0.95,1.70+i*0.70,11.6,0.45,f'{i+1}. {ref}',14,WHITE)
textbox(s,0.95,6.25,11.5,0.45,'შენიშვნა: API კონტრაქტი და არქიტექტურა აღწერს დაგეგმილ დიზაინს; რეალიზაციისას აუცილებელია კოდის, ტესტებისა და დოკუმენტაციის სინქრონიზაცია.',10,MUTED)

prs.save(OUT)
print(OUT)
