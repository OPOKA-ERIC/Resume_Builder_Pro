# Resume Builder Pro - Software Design Document (Updated)
## Group W, BSE2301 | Project 11: Resume Builder Application (Django)

---

## Chapter 1: Introduction

### 1.1 Background
Resume Builder Pro is a Django-based web application that allows users to create, manage, and download professional resumes without needing any design or formatting skill. Users register an account, enter their personal, educational, and work-experience details through a guided step-by-step wizard, choose from a set of professionally designed resume templates, preview the final result, and download it as a polished PDF document.

### 1.2 Problem Statement
Manually created resumes are inconsistent in structure, are time-consuming to update, and offer no easy way to try different visual styles without redoing the layout by hand. Resume Builder Pro solves this by separating content from presentation: the user only supplies information, and the system takes care of formatting it into a chosen professional template.

### 1.3 Objectives
1. Allow users to register and securely manage a personal account.
2. Allow users to enter personal, education, and work-experience details through a guided, step-by-step form.
3. Provide a set of ready-made, professional resume templates for the user to choose from.
4. Allow the user to preview the assembled resume before downloading it.
5. Generate and let the user download a print-ready PDF copy of the resume.
6. Persist each user's resume data so it can be revisited and edited at any time.
7. Analyse a user's resume against a job description and provide skill gap analysis with proficiency scoring (Job Match Analyzer).
8. Generate a shareable, public portfolio/CV page accessible via a unique link and QR code (Portfolio Generator).
9. Integrate job adverts from external platforms (LinkedIn, etc.) into the system for browsing and analysis.
10. Leverage AI for intelligent skill recommendations, job description parsing, and content improvement suggestions.

### 1.4 Scope of the Project
The system covers account registration and login, a multi-step resume-data wizard (7 steps: Education, Experience, Skills, Projects, Certifications, Languages, References), template selection with 3 distinct templates, live preview, individual section editing, and PDF export. Additionally, the system includes a Job Match Analyzer that scores user skills against job descriptions and recommends improvements, a Portfolio Generator that creates shareable public portfolio pages with QR codes, integration with external job boards (LinkedIn, etc.) for importing and analysing job adverts, and AI capabilities powering job matching, skill recommendations, and content suggestions. It does not cover payment processing or real-time collaborative editing.

---

## Chapter 2: Requirements Analysis

### 2.1 Functional Requirements
| ID | Requirement | Status |
|---|---|---|
| FR-01 | The system shall allow a new user to register with an email, username, and password. | Implemented |
| FR-02 | The system shall allow a registered user to log in and log out securely. | Implemented |
| FR-03 | The system shall provide a multi-step form for personal details, education history, work experience, skills, projects, certifications, languages, and references. | Implemented (7 steps) |
| FR-04 | The system shall let the user choose from at least three distinct resume templates. | Implemented (Professional, Modern, Creative) |
| FR-05 | The system shall render a live preview of the resume using the selected template before download. | Implemented |
| FR-06 | The system shall generate a downloadable PDF version of the completed resume. | Implemented (xhtml2pdf) |
| FR-07 | The system shall save each user's resume data so it persists between sessions. | Implemented |
| FR-08 | The system shall allow the user to edit and re-generate a previously saved resume. | Implemented (title edit + section edit/delete) |
| FR-09 | The system shall provide an administrative panel for managing users and templates. | Implemented |
| FR-10 | The system shall allow password reset via email. | Implemented |
| FR-11 | The system shall allow the user to edit individual resume sections (education, experience, etc.) after creation. | Implemented |
| FR-12 | The system shall paginate the dashboard when a user has many resumes. | Implemented (9 per page) |
| FR-13 | The system shall allow a user to input a job description URL or text and receive a skill gap analysis with proficiency scoring. | In Development |
| FR-14 | The system shall recommend missing or underdeveloped skills based on the analysed job description. | In Development |
| FR-15 | The system shall generate a shareable public portfolio/CV page with a unique URL. | In Development |
| FR-16 | The system shall generate a QR code for the shareable portfolio page. | In Development |
| FR-17 | The system shall allow importing and browsing job adverts from external platforms (LinkedIn, etc.). | In Development |
| FR-18 | The system shall use AI to parse job descriptions and provide intelligent skill recommendations and resume improvement suggestions. | In Development |

### 2.2 Non-Functional Requirements
| Quality Attribute | Requirement |
|---|---|
| Usability | The wizard shall guide the user one section at a time with clear labels, validation messages, and a visual progress bar. Client-side validation provides instant feedback. |
| Performance | A resume preview renders in under 2 seconds and a PDF generates in under 5 seconds under normal load. |
| Security | Passwords are hashed (Django's PBKDF2), all form input is validated and sanitised server-side, CSRF protection on all forms, POST-based logout, HTTP-only session cookies, SameSite=Lax. |
| Portability | The application runs on any platform supporting Python 3, deployable with SQLite (dev) and PostgreSQL (prod). |
| Maintainability | The codebase follows Django's app-based structure with 4 isolated apps, each independently testable. 84 unit tests. |
| Availability | The deployed application targets 99% uptime during the demonstration period. |

### 2.3 Use Case Descriptions
| ID | Use Case | Actor | Description |
|---|---|---|---|---|
| UC-01 | Register Account | Visitor | A visitor supplies an email, username, and password to create a new account. |
| UC-02 | Log In / Log Out | Registered User | A user authenticates (session-based) or ends their session (POST-based logout). |
| UC-03 | Enter Resume Details | Registered User | The user progresses through 7 wizard steps entering education, experience, skills, projects, certifications, languages, and references. |
| UC-04 | Select Template | Registered User | The user picks one of 3 available resume templates; selection is saved and applied to PDF output. |
| UC-05 | Preview Resume | Registered User | The user views a rendered, on-screen version of the resume with edit/delete buttons for each section. |
| UC-06 | Download Resume as PDF | Registered User | The system converts the rendered resume into a PDF file using the selected template and serves it as a download. |
| UC-07 | Edit Saved Resume | Registered User | A returning user updates the title or any individual section of a previously saved resume. |
| UC-08 | Reset Password | Registered User/Visitor | A user requests a password reset link via email and sets a new password. |
| UC-09 | Manage Users & Templates | Administrator | An administrator manages user accounts and adds or edits resume templates through the Django admin panel. |
| UC-10 | Analyse Job Match | Registered User | The user submits a job description URL or text; the system analyses their resume skills against the job requirements and returns a match score with recommendations. |
| UC-11 | Generate Portfolio Link | Registered User | The user generates a shareable public portfolio/CV page with a unique URL and QR code for distribution. |
| UC-12 | Browse Job Adverts | Registered User | The user browses imported job adverts from external platforms and analyses them against their resume. |
| UC-13 | AI Resume Improvement | Registered User | The user receives AI-powered suggestions for improving resume content, keywords, and structure based on target job descriptions. |

---

## Chapter 3: System Design

### 3.1 Architecture Overview
The application follows Django's MTV (Model-Template-View) pattern with 4 modular apps:

```
resume_builder_pro/     → Project config (settings, root URLs, WSGI)
accounts/               → Authentication (register, login, logout, profile, password)
resumes/                → Core domain (Resume + 7 child models, wizard, CRUD, section editing)
templates_app/          → Resume template gallery and management
pdf_export/             → PDF generation with template-aware rendering
```

### 3.2 Data Flow
1. User submits form → Django view processes POST data through ModelForm validation
2. Valid data saved → Model instances created/updated in database
3. Redirect issued → PRG (Post-Redirect-Get) pattern prevents duplicate submissions
4. Flash messages → Django's messages framework provides success/error feedback
5. Session-based auth → Django session middleware manages authentication state
6. Template rendering → Django template engine renders server-side HTML with Bootstrap 5

### 3.3 Component Diagram
```
+------------------+   +------------------+   +------------------+   +------------------+   +------------------+
|  accounts app    |   |   resumes app     |   |  templates_app   |   |  job_analysis    |   |   portfolio      |
|  - models        |   |  - models         |   |  - models        |   |  - job matcher   |   |  - public pages  |
|  - forms         |   |  - forms (wizard) |   |  - views         |   |  - skill scorer  |   |  - QR generator  |
|  - views (auth)  |   |  - views (CRUD)   |   |                  |   |  - AI integration |   |  - sharing       |
+------------------+   +------------------+   +------------------+   +------------------+   +------------------+
          \                    |                      |                     /                     /
           \___________________|______________________|____________________/_____________________/
                                        |
                               +------------------+
                               |   pdf_export     |
                               |  - views (PDF)   |
                               |  - template map  |
                               +------------------+

                               +---------------------+
                               |  job_board (NEW)    |
                               |  - advert importer  |
                               |  - LinkedIn parser  |
                               |  - advert browser   |
                               +---------------------+

                               +---------------------+
                               |  ai_engine (NEW)    |
                               |  - NLP parser       |
                               |  - skill recommender |
                               |  - content suggester |
                               +---------------------+
```

---

## Chapter 4: Database Design

### 4.1 Entity-Relationship Diagram
```
+---------------+        +----------------+        +----------------+
|     User      |        |  UserProfile   |        |    Resume      |
|---------------|        |----------------|        |----------------|
| PK id         |<--1:1--| PK id          |         PK id           |
|    username   |        | FK user_id     |<--1:M--| FK user_id     |
|    email      |        |    phone       |        |    title       |
|    password   |        |    address     |        | FK template_id |
+---------------+        |    photo       |        |    created_at  |
                          +----------------+        |    updated_at  |
                                                             |
                                                          1:M | (to each child table)
        +----------------+----------------+----------------+----------------+----------------+----------------+
        |                |                |                |                |                |                |
+---------------+ +----------------+ +---------------+ +---------------+ +----------------+ +---------------+ +---------------+
|   Education   | |   Experience   | |     Skill     | |    Project    | | Certification  | |   Language    | |   Reference   |
|---------------| |----------------| |---------------| |---------------| |----------------| |---------------| |---------------|
| PK id         | | PK id          | | PK id         | | PK id         | | PK id          | | PK id         | | PK id         |
| FK resume_id  | | FK resume_id   | | FK resume_id  | | FK resume_id  | | FK resume_id   | | FK resume_id  | | FK resume_id  |
+---------------+ +----------------+ +---------------+ +---------------+ +----------------+ +---------------+ +---------------+

+----------------+
|    Template    |
|----------------|
| PK id          |
|    name        |
|    description |
|    html_file   |
|    is_active   |
|    preview_img |
+----------------+
(Resume.template_id references Template.id, M:1, SET_NULL)
```

### 4.2 Database Schema
| Table | Key Fields |
|---|---|
| User | id (PK), username, email, password (hashed), date_joined |
| UserProfile | id (PK), user_id (FK→User), phone, address, photo |
| Resume | id (PK), user_id (FK→User), title, template_id (FK→Template, SET_NULL), created_at, updated_at |
| Education | id (PK), resume_id (FK→Resume, CASCADE), institution, qualification, start_date, end_date, description |
| Experience | id (PK), resume_id (FK→Resume, CASCADE), company, role, start_date, end_date, description |
| Skill | id (PK), resume_id (FK→Resume, CASCADE), name, proficiency_level (choices) |
| Project | id (PK), resume_id (FK→Resume, CASCADE), name, description, link |
| Certification | id (PK), resume_id (FK→Resume, CASCADE), title, issuer, date_awarded |
| Language | id (PK), resume_id (FK→Resume, CASCADE), name, proficiency_level (choices) |
| Reference | id (PK), resume_id (FK→Resume, CASCADE), name, relationship, contact |
| ResumeTemplate | id (PK), name, description, html_file, preview_image, is_active, created_at |
| JobAnalysis | id (PK), user_id (FK→User), resume_id (FK→Resume), job_title, company, job_description, match_score, created_at |
| SkillScore | id (PK), job_analysis_id (FK→JobAnalysis), skill_name, required_level, user_level, score, recommendation |
| Portfolio | id (PK), user_id (FK→User), resume_id (FK→Resume), slug (unique), qr_code, is_published, views, created_at |
| JobAdvert | id (PK), source (LinkedIn, etc.), source_id, title, company, description, url, posted_date, imported_by (FK→User), created_at |

### 4.3 Relationship Design Decisions
- **User ↔ UserProfile:** OneToOneField — extends Django's User without modifying the auth model.
- **Resume → User:** ForeignKey with CASCADE — deleting a user deletes all their resumes.
- **Resume → ResumeTemplate:** ForeignKey with SET_NULL — deleting a template doesn't delete resumes.
- **Resume → Children (Education, etc.):** ForeignKey with CASCADE — deleting a resume removes all its sections.

---

## Chapter 5: User Interface Design

### 5.1 Technology
- Bootstrap 5.3.0 loaded via CDN (no build step required)
- Bootstrap Icons 1.10.0 for iconography
- Minimal custom CSS (39 lines) for card hover effects, form focus states, and footer styling
- Custom JavaScript for alert auto-dismiss, wizard form validation, and progress bar animation

### 5.2 Key Screens
| Page | URL | Description |
|---|---|---|
| Landing Page | `/` | Hero banner with features summary, Register/Login buttons |
| Register | `/accounts/register/` | Username, email, password, confirm password |
| Login | `/accounts/login/` | Username, password, "Forgot password?" link |
| Dashboard | `/resumes/` | Card grid of user's resumes with Edit/Preview/Delete actions, pagination |
| Resume Create | `/resumes/create/` | Single field: Resume title |
| Wizard Step | `/resumes/<id>/wizard/<step>/` | Form for current step + progress bar + existing items list + Back/Next/Save & Exit buttons |
| Template Select | `/resumes/<id>/templates/` | Gallery grid of 3 templates with Select & Preview buttons |
| Resume Preview | `/resumes/<id>/preview/` | Full resume display with edit/delete buttons per section |
| Section Edit | `/resumes/<id>/<section>/<item_id>/edit/` | Edit form for a specific section entry |
| Password Reset | `/accounts/password-reset/` | Email input form |
| Profile | `/accounts/profile/` | Edit name, email, phone, address, photo |

### 5.3 Wizard Progress Bar
The wizard displays a horizontal progress indicator with:
- Numbered circles for each step (1-7)
- Color-coded: blue (completed/current) vs grey (upcoming)
- Animated progress bar underneath
- Current step name displayed in bold

---

## Chapter 6: Implementation Plan

### 6.1 Technology Stack
| Layer | Technology |
|---|---|
| Language | Python 3.12 |
| Framework | Django 6.0.6 |
| Database (dev) | SQLite3 |
| Database (prod) | PostgreSQL (psycopg2-binary) |
| PDF Generation | xhtml2pdf (pisa) |
| Image Handling | Pillow |
| Frontend CSS | Bootstrap 5.3.0 (CDN) |
| Frontend JS | Bootstrap 5.3.0 Bundle (CDN) + custom validation |
| Static Files | WhiteNoise |
| WSGI Server | Gunicorn |
| Version Control | Git & GitHub |

### 6.2 Project Folder Structure
```
resume_builder_pro/
├── manage.py
├── requirements.txt
├── resume_builder_pro/        # Project config
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── accounts/                  # Authentication
│   ├── models.py             # UserProfile
│   ├── forms.py              # RegistrationForm, ProfileForm, CustomPasswordChangeForm
│   ├── views.py              # register, login, logout, profile, password_change
│   ├── urls.py               # 9 URL patterns (including password reset)
│   ├── admin.py
│   ├── tests.py              # 25 test methods
│   └── migrations/
├── resumes/                   # Core domain
│   ├── models.py             # 8 models: Resume + 7 children
│   ├── forms.py              # 8 ModelForms
│   ├── views.py              # dashboard, create, wizard, template_select, preview, edit, delete, section_edit, section_delete
│   ├── urls.py               # 9 URL patterns
│   ├── admin.py              # ResumeAdmin with 7 TabularInlines
│   ├── tests.py              # ~35 test methods
│   └── migrations/
├── templates_app/             # Template gallery
│   ├── models.py             # ResumeTemplate
│   ├── views.py              # gallery, preview
│   ├── urls.py               # 2 URL patterns
│   ├── admin.py
│   └── migrations/
│       └── 0002_seed_templates.py  # Seeds 3 templates
├── pdf_export/                # PDF generation
│   ├── views.py              # generate_pdf_html (template-aware), render_to_pdf, download_pdf, pdf_preview
│   ├── urls.py               # 2 URL patterns
│   └── tests.py              # ~10 test methods
├── job_analysis/              # NEW - Job Match Analyzer
│   ├── models.py             # JobAnalysis, SkillScore
│   ├── forms.py
│   ├── views.py              # job_analysis dashboard, skill scoring, recommendations
│   ├── urls.py
│   ├── admin.py
│   └── migrations/
├── portfolio/                 # NEW - Portfolio Generator
│   ├── models.py             # Portfolio (slug, QR code, views)
│   ├── forms.py
│   ├── views.py              # portfolio creation, public view, QR generation
│   ├── urls.py
│   └── migrations/
├── job_board/                 # NEW - Job Adverts Integration
│   ├── models.py             # JobAdvert
│   ├── forms.py
│   ├── views.py              # advert browser, LinkedIn importer, search
│   ├── urls.py
│   └── migrations/
├── ai_engine/                 # NEW - AI Integration
│   ├── models.py             # (none - service layer)
│   ├── services.py           # NLP parser, skill recommender, content suggester
│   ├── views.py              # AI analysis endpoints
│   └── urls.py
├── templates/                 # HTML templates
│   ├── base.html             # Master layout with navbar, messages, footer
│   ├── landing.html
│   ├── accounts/             # 8 templates (login, register, profile, password_change, password_reset, password_reset_done, password_reset_confirm, password_reset_complete)
│   ├── resumes/              # 7 templates (dashboard, wizard_step, template_select, preview, resume_form, resume_confirm_delete, section_edit)
│   ├── job_analysis/         # NEW - templates for job matching dashboard
│   ├── portfolio/            # NEW - templates for portfolio pages
│   ├── job_board/            # NEW - templates for job adverts
│   └── pdf/                  # 5 templates (resume_pdf, resume_professional, resume_modern, resume_creative, pdf_preview)
├── static/
│   ├── css/style.css
│   └── js/main.js            # Alert auto-dismiss, wizard validation, unsaved changes warning
└── media/                    # User uploads
```

### 6.3 Resume Template System
The application includes 3 distinct PDF templates:

| Template | Style | Best For |
|---|---|---|
| Professional | Serif fonts (Georgia), centered header, clean sections, underline separators | Corporate, finance, academic |
| Modern | Sidebar layout, sans-serif (Helvetica), blue accent (#1a5276), skill bars | Tech, creative, startup |
| Creative | Gradient header (purple), pill badges, colored date tags, border accents | Designers, marketing |

Template selection is stored in `Resume.template` (FK). The `generate_pdf_html()` function maps template names to HTML files:
```python
TEMPLATE_MAP = {
    'Professional': 'pdf/resume_professional.html',
    'Modern': 'pdf/resume_modern.html',
    'Creative': 'pdf/resume_creative.html',
}
```

---

## Chapter 7: Testing Strategy

### 7.1 Test Summary
| App | Test Count | Coverage |
|---|---|---|
| accounts | 25 | Forms (valid, duplicate email/username, password mismatch, short username, invalid chars), Models (`__str__`), Views (register GET/POST, login GET/POST/fail, logout, profile GET/update, password change/wrong old, auth required) |
| resumes | ~35 | All 8 models (creation, `__str__`, nullable fields, defaults, ordering), All views (dashboard, create, wizard every step, edit, delete, preview, template_select, 404 for other user's resume) |
| pdf_export | ~10 | HTML generation (content includes all fields, empty resume), download (auth/unauth/404/content type), preview (auth/unauth/404) |
| **Total** | **~70** | **All critical paths covered** |

### 7.2 Key Test Cases
| Test | Description | Assertion |
|---|---|---|
| `test_wizard_prevents_other_users_resume` | User B tries to access User A's wizard | 404 response |
| `test_download_pdf_other_user_resume` | User B tries to download User A's PDF | 404 response |
| `test_download_pdf_content_type` | Authenticated user downloads PDF | Content-Type: application/pdf |
| `test_duplicate_email` | Register with existing email | Form invalid, error on email field |
| `test_resume_ordering` | Create 2 resumes, check list order | Newest first (`-updated_at`) |

### 7.3 Running Tests
```bash
python manage.py test accounts resumes pdf_export
```

---

## Chapter 8: Risk Analysis

| Risk | Mitigation |
|---|---|
| PDF rendering differs from on-screen preview | 3 separate PDF templates with inline CSS, tested against xhtml2pdf |
| Scope creep from adding extra features | Feature list locked after Chapter 2 sign-off |
| Team member unavailability | Daily check-ins and clearly owned modules |
| Data loss during wizard entry | Progress saved to DB at the end of each wizard step |
| Deployment issues | Pinned requirements.txt, tested deployment 3 days before presentation |

---

## Chapter 9: Project Schedule

| Phase | Key Tasks | Status |
|---|---|---|
| Requirements & Design (Days 1-3) | Finalise requirements, ER diagram, use cases, wireframes, SDD | Complete |
| Core Backend (Days 4-6) | Django project setup, models, migrations, admin, auth | Complete |
| Wizard & Frontend (Days 7-9) | Multi-step resume form, Bootstrap templates, JS validation | Complete |
| Templates, Preview & PDF (Days 10-11) | 3 resume templates, live preview, PDF export with template selection | Complete |
| Testing & Fixes (Days 12-13) | Unit, integration testing; bug fixes; 84 tests passing | Complete |
| Deployment & Presentation Prep (Day 14) | Deploy to hosting, finalise README, rehearse presentation | In Progress |

---

## Chapter 10: Deployment Strategy

### 10.1 Architecture
```
+----------------------+        +---------------------------+        +----------------------+
|   Client Device      |  HTTPS |     Web/App Server        |        |   Database Server    |
|  (Browser)           |<------>|  (Django + Gunicorn/      |<------>|  (SQLite / Postgres) |
|                      |        |   Nginx, Render/Railway)   |        |                      |
+----------------------+        |  - PDF engine (xhtml2pdf) |        +----------------------+
                                +---------------------------+
```

### 10.2 Deployment Steps
```bash
# Local Development
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver

# Production
pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate
gunicorn resume_builder_pro.wsgi:application
```

### 10.3 Environment Variables
- `DJANGO_SECRET_KEY` — Django secret key
- `DATABASE_URL` — PostgreSQL connection string (production)

---

## Appendix: URL Routing Table

| URL Pattern | View | Name | Auth Required |
|---|---|---|---|
| `/` | TemplateView(landing.html) | `landing` | No |
| `/admin/` | Django admin | — | Yes (staff) |
| `/accounts/register/` | `register_view` | `accounts:register` | No |
| `/accounts/login/` | `login_view` | `accounts:login` | No |
| `/accounts/logout/` | `logout_view` | `accounts:logout` | No (POST) |
| `/accounts/profile/` | `profile_view` | `accounts:profile` | Yes |
| `/accounts/password-change/` | `password_change_view` | `accounts:password_change` | Yes |
| `/accounts/password-reset/` | PasswordResetView | `accounts:password_reset` | No |
| `/accounts/password-reset/done/` | PasswordResetDoneView | `accounts:password_reset_done` | No |
| `/accounts/password-reset-confirm/` | PasswordResetConfirmView | `accounts:password_reset_confirm` | No |
| `/accounts/password-reset-complete/` | PasswordResetCompleteView | `accounts:password_reset_complete` | No |
| `/resumes/` | `dashboard` | `resumes:dashboard` | Yes |
| `/resumes/create/` | `resume_create` | `resumes:resume_create` | Yes |
| `/resumes/<id>/edit/` | `resume_edit` | `resumes:resume_edit` | Yes |
| `/resumes/<id>/delete/` | `resume_delete` | `resumes:resume_delete` | Yes |
| `/resumes/<id>/wizard/<step>/` | `wizard_step` | `resumes:wizard_step` | Yes |
| `/resumes/<id>/templates/` | `template_select` | `resumes:template_select` | Yes |
| `/resumes/<id>/preview/` | `resume_preview` | `resumes:resume_preview` | Yes |
| `/resumes/<id>/<section>/<item_id>/edit/` | `section_edit` | `resumes:section_edit` | Yes |
| `/resumes/<id>/<section>/<item_id>/delete/` | `section_delete` | `resumes:section_delete` | Yes |
| `/templates/` | `template_gallery` | `templates_app:gallery` | No |
| `/templates/<id>/preview/` | `template_preview` | `templates_app:preview` | Yes |
| `/pdf/<id>/download/` | `download_pdf` | `pdf_export:download_pdf` | Yes |
| `/pdf/<id>/preview/` | `pdf_preview` | `pdf_export:pdf_preview` | Yes |

---

## Appendix: Security Measures

| Layer | Mechanism | Implementation |
|---|---|---|
| CSRF Protection | `{% csrf_token %}` in all forms | CsrfViewMiddleware + template tag |
| Authentication | `@login_required` decorator | All protected views |
| Authorization | `get_object_or_404(..., user=request.user)` | Every resume view |
| Input Validation | Regex validators, email uniqueness, password validators | Forms |
| Session Security | HTTP-only cookies, SameSite=Lax, 1-week expiry | settings.py |
| HTTP Headers | X_FRAME_OPTIONS=DENY, SECURE_CONTENT_TYPE_NOSNIFF | settings.py |
| Password Hashing | PBKDF2 + SHA256, 600k iterations | Django auth default |
| HTTP Methods | `@require_http_methods(["GET", "POST"])` | Auth views |
| Caching | `@never_cache` on register/login | accounts views |
| POST-based Logout | Logout via form submission, not GET link | Base navbar template |
| Logging | Auth events (login, register, logout, password change, PDF gen) | settings.py LOGGING |
| Password Reset | Email-based reset with token validation | Django auth views |
