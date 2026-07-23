# Resume Builder Pro — Full Project Report

**Faculty of Computing and Informatics**
**BSE2301 — Software Engineering Mini Project 2**

**Group W — Project 11: Resume Builder Application**
**Group C**

| Name | Role |
|------|------|
| Opoka Eric | Backend & Database Lead |
| Opeto Isaac | Authentication & PDF Generation Lead |
| Ojok Isaac | Frontend & UI/UX Lead |
| Auma Dilish | Testing, Documentation & Deployment Lead |

**Supervisor / Facilitator:** ______________________
**Date:** July 2026

---

## Table of Contents

1. [Introduction](#chapter-1-introduction)
2. [Requirements Analysis](#chapter-2-requirements-analysis)
3. [System Design](#chapter-3-system-design)
4. [Database Design](#chapter-4-database-design)
5. [User Interface Design](#chapter-5-user-interface-design)
6. [Implementation Plan](#chapter-6-implementation-plan)
7. [Testing Strategy](#chapter-7-testing-strategy)
8. [Risk Analysis](#chapter-8-risk-analysis)
9. [Project Schedule](#chapter-9-project-schedule)
10. [Deployment Strategy](#chapter-10-deployment-strategy)

---

## Chapter 1: Introduction

### 1.1 Background

Job seekers frequently struggle to produce a clean, well-formatted resume, either because they lack design experience or because manually adjusting layouts in word processors is slow and error-prone. Resume Builder Pro solves this by separating content from presentation: the user only supplies information, and the system takes care of formatting it into a chosen professional template.

### 1.2 Problem Statement

Manually created resumes are inconsistent in structure, are time-consuming to update, and offer no easy way to try different visual styles without redoing the layout by hand. There is no simple, self-service tool that lets a user store their career information once and generate multiple styled outputs from it.

### 1.3 Objectives

1. To allow users to register and securely manage a personal account.
2. To allow users to enter personal, education, and work-experience details through a guided, step-by-step form.
3. To provide a set of ready-made, professional resume templates for the user to choose from.
4. To allow the user to preview the assembled resume before downloading it.
5. To generate and let the user download a print-ready PDF copy of the resume.
6. To persist each user's resume data so it can be revisited and edited at any time.

### 1.4 Scope of the Project

The system covers account registration and login, a multi-step resume-data wizard (personal details, education, experience, skills, projects, certifications), template selection, live preview, and PDF export. It does not cover payment processing, third-party job-board integration, or real-time collaborative editing; these are noted as possible future extensions.

### 1.5 Beneficiaries

- Students and recent graduates applying for their first jobs.
- Job seekers who want a fast, consistent way to produce and update a resume.
- Career-services staff who may recommend the tool to clients.

---

## Chapter 2: Requirements Analysis

### 2.1 Functional Requirements

| ID | Requirement |
|----|-------------|
| FR-01 | The system shall allow a new user to register with an email, username, and password. |
| FR-02 | The system shall allow a registered user to log in and log out securely. |
| FR-03 | The system shall provide a multi-step form for personal details, education history, work experience, skills, projects, certifications, and languages. |
| FR-04 | The system shall let the user choose from at least three distinct resume templates. |
| FR-05 | The system shall render a live preview of the resume using the selected template before download. |
| FR-06 | The system shall generate a downloadable PDF version of the completed resume. |
| FR-07 | The system shall save each user's resume data so it persists between sessions. |
| FR-08 | The system shall allow the user to edit and re-generate a previously saved resume. |
| FR-09 | The system shall provide an administrative panel for managing users and templates. |

### 2.2 Non-Functional Requirements

| Quality Attribute | Requirement |
|-------------------|-------------|
| Usability | The wizard shall guide the user one section at a time with clear labels and validation messages. |
| Performance | A resume preview shall render in under 2 seconds and a PDF shall generate in under 5 seconds under normal load. |
| Security | Passwords shall be hashed (Django's PBKDF2 default), and all form input shall be validated and sanitised server-side. |
| Portability | The application shall run on any platform supporting Python 3 and shall be deployable with SQLite in development and PostgreSQL in production. |
| Maintainability | The codebase shall follow Django's app-based structure so each concern (accounts, resumes, templates, PDF export) is isolated and independently testable. |
| Availability | The deployed application shall target 99% uptime during the demonstration and grading period. |

### 2.3 Use Case Descriptions

| ID | Use Case | Actor | Description |
|----|----------|-------|-------------|
| UC-01 | Register Account | Visitor | A visitor supplies an email, username, and password to create a new account. |
| UC-02 | Log In / Log Out | Registered User | A user authenticates to access their dashboard, or ends their session. |
| UC-03 | Enter Resume Details | Registered User | The user progresses through the wizard entering personal, education, experience, skills, project, and certification data. |
| UC-04 | Select Template | Registered User | The user picks one of the available resume templates for rendering. |
| UC-05 | Preview Resume | Registered User | The user views a rendered, on-screen version of the resume before committing to a download. |
| UC-06 | Download Resume as PDF | Registered User | The system converts the rendered resume into a PDF file and serves it to the user. |
| UC-07 | Edit Saved Resume | Registered User | A returning user updates any section of a previously saved resume. |
| UC-08 | Manage Users & Templates | Administrator | An administrator manages user accounts and adds or edits resume templates through the Django admin panel. |

---

## Chapter 3: System Design

### 3.1 Use Case Diagram

```
+-------------------------------------------------+
|                Resume Builder Pro                |
|                                                   |
|  (Visitor)---->  [Register Account]               |
|                                                   |
|  (Registered)--->  [Log In / Log Out]            |
|    (User)        [Enter Resume Details]           |
|                  [Select Template]                |
|                  [Preview Resume]                 |
|                  [Download Resume as PDF]         |
|                  [Edit Saved Resume]              |
|                                                   |
|  (Administrator)>  [Manage Users & Templates]    |
+-------------------------------------------------+
```

### 3.2 Activity Diagram — Create & Download a Resume

```
Start
  |
  v
[Log In / Register]
  |
  v
[Fill Personal Details] -> [Fill Education] -> [Fill Experience]
  |                                                 |
  v                                                 v
[Fill Skills / Projects / Certifications] <---------+
  |
  v
[Select Template]
  |
  v
[Preview Resume] --(edit needed?)--> [Return to relevant step]
  |
  v (looks good)
[Generate PDF]
  |
  v
[Download File]
  |
  v
End
```

### 3.3 Sequence Diagram — Fill Resume & Download PDF

```
User          Browser           Django View        Database        PDF Engine
 |                |                    |                 |               |
 |--fill form---->|                    |                 |               |
 |                |--POST resume data->|                 |               |
 |                |                    |--save records-->|               |
 |                |                    |<--confirm--------|              |
 |                |<--render preview---|                 |               |
 |--click Download|                    |                 |               |
 |                |--GET /download---->|                 |               |
 |                |                    |--fetch data---->|               |
 |                |                    |<--data-----------|              |
 |                |                    |--render HTML--->|               |
 |                |                    |----------------------render PDF>|
 |                |                    |<---------------------PDF bytes--|
 |                |<--PDF file---------|                 |               |
 |<--save/open----|                    |                 |               |
```

### 3.4 Class Diagram

```
+-----------------+      +------------------+      +------------------+
|      User        |      |   UserProfile    |      |     Resume       |
+-----------------+      +------------------+      +------------------+
| id (PK)          |1----1| id (PK)          |1----*| id (PK)          |
| username         |      | user_id (FK)     |      | user_id (FK)     |
| email            |      | phone            |      | title            |
| password_hash    |      | address          |      | template_id (FK) |
+-----------------+      | photo            |      | created_at       |
                          +------------------+      | updated_at       |
                                                    +------------------+
                                                             |1
                     +----------------------------------------+
                     |*                    |*                 |*            |*
             +---------------+   +----------------+  +---------------+  +---------------+ +-------------+
             |   Education   |   |   Experience   |  |     Skill     |  |    Project    | | Certification|
             +---------------+   +----------------+  +---------------+  +---------------+ +-------------+
             | id (PK)       |   | id (PK)        |  | id (PK)       |  | id (PK)       | | id (PK)     |
             | resume_id(FK) |   | resume_id (FK) |  | resume_id(FK) |  | resume_id(FK) | | resume_id(FK)|
             | institution   |   | company        |  | name          |  | name          | | title       |
             | qualification |   | role           |  | level         |  | description   | | issuer      |
             | start/end year|   | start/end year |  +---------------+  +---------------+ | year        |
             +---------------+   | description    |                                        +-------------+
                                  +----------------+
```

### 3.5 Data Flow Diagram (Level 0 & Level 1)

**Level 0 (Context Diagram)**

```
[User] ---resume data---> ((Resume Builder Pro)) ---PDF file---> [User]
                                       |        ^
                                       v        |
                                  [ Database ]
```

**Level 1**

```
[User]--login/register-->(Auth Process)-->[User table]
[User]--wizard data----->(Manage Resume Data)-->[Resume/Education/Experience/Skill tables]
[User]--template choice->(Render Preview)-->[Template table]
[User]--download request->(Generate PDF)-->reads-->[Resume + related tables]-->PDF-->[User]
```

### 3.6 Component Diagram

```
+------------------+   +------------------+   +------------------+   +------------------+
|  accounts app    |   |   resumes app     |   |  templates app   |   |   core / config   |
|  - models        |   |  - models         |   |  - static assets |   |  - urls.py        |
|  - forms         |   |  - forms (wizard) |   |  - preview logic |   |  - settings.py    |
|  - views (auth)  |   |  - views          |   |                  |   |                  |
+------------------+   +------------------+   +------------------+   +------------------+
          \                    |                      |                     /
           \___________________|______________________|____________________/
                                       |
                              +------------------+
                              |   pdf app        |
                              |  - PDF generator |
                              +------------------+
```

### 3.7 Deployment Diagram

```
+----------------------+        +---------------------------+        +----------------------+
|   Client Device      |  HTTPS |     Web/App Server         |        |   Database Server    |
|  (Browser)            |<----->|  (Django + Gunicorn/       |<------>|  (SQLite / Postgres) |
|                       |        |   Nginx, hosted on Render/ |        |                      |
+----------------------+        |   Railway/Heroku)          |        +----------------------+
                                 |  - PDF engine (xhtml2pdf)  |
                                 +---------------------------+
```

---

## Chapter 4: Database Design

### 4.1 Entity-Relationship Diagram

```
+---------------+        +----------------+        +----------------+
|     User      |        |  UserProfile   |        |    Resume      |
|---------------|        |----------------|        |----------------|
| PK id         |<--1:1--| PK id          |<--1:M--| PK id           |
|    username   |        | FK user_id     |        | FK user_id      |
|    email      |        |    phone       |        |    title        |
|    password   |        |    address     |        | FK template_id  |
+---------------+        |    photo       |        +----------------+
                          +----------------+              |
                                                     1:M | (to each child table)
        +----------------+----------------+----------------+----------------+----------------+
        |                |                |                |                |                |
+---------------+ +----------------+ +---------------+ +---------------+ +----------------+ +---------------+
|   Education   | |   Experience   | |     Skill     | |    Project    | | Certification  | |   Language    |
|---------------| |----------------| |---------------| |---------------| |----------------| |---------------|
| PK id         | | PK id          | | PK id         | | PK id         | | PK id          | | PK id         |
| FK resume_id  | | FK resume_id   | | FK resume_id  | | FK resume_id  | | FK resume_id   | | FK resume_id  |
+---------------+ +----------------+ +---------------+ +---------------+ +----------------+ +---------------+

+----------------+
|    Template    |
|----------------|
| PK id          |
|    name        |
|    html_file   |
|    is_active   |
+----------------+
(Resume.template_id references Template.id, M:1)
```

### 4.2 Database Schema

| Table | Key Fields |
|-------|------------|
| **User** | id (PK), username, email, password (hashed), date_joined |
| **UserProfile** | id (PK), user_id (FK -> User), phone, address, photo |
| **Resume** | id (PK), user_id (FK -> User), title, template_id (FK -> Template), created_at, updated_at |
| **Education** | id (PK), resume_id (FK -> Resume), institution, qualification, start_year, end_year, description |
| **Experience** | id (PK), resume_id (FK -> Resume), company, role, start_year, end_year, description |
| **Skill** | id (PK), resume_id (FK -> Resume), name, proficiency_level |
| **Project** | id (PK), resume_id (FK -> Resume), name, description, link |
| **Certification** | id (PK), resume_id (FK -> Resume), title, issuer, year_awarded |
| **Language** | id (PK), resume_id (FK -> Resume), name, proficiency_level |
| **Reference** | id (PK), resume_id (FK -> Resume), name, relationship, contact |
| **ResumeTemplate** | id (PK), name, description, preview_image, html_file, is_active, created_at |

**Total: 11 tables across 4 Django apps**

### 4.3 Entity Descriptions

- **User** — Django's built-in authentication model; stores credentials and session data.
- **UserProfile** — Extends User with phone, address, and profile photo (OneToOne relationship).
- **Resume** — Core entity; each resume belongs to one user and optionally references a template.
- **Education** — Academic history entries linked to a resume (institution, qualification, years).
- **Experience** — Work history entries linked to a resume (company, role, years, description).
- **Skill** — Named skills with proficiency levels (beginner, intermediate, advanced, expert).
- **Project** — Portfolio items with name, description, and optional link.
- **Certification** — Professional certifications with issuer and year.
- **Language** — Spoken/written languages with proficiency (basic, conversational, fluent, native).
- **Reference** — Professional references with name, relationship, and contact.
- **ResumeTemplate** — Pre-built CV template definitions with HTML file paths.

---

## Chapter 5: User Interface Design

### 5.1 Design Philosophy

The interface follows a clean, mobile-responsive Bootstrap 5 layout with an indigo color theme (#4f46e5). Typography uses Inter for body text and Plus Jakarta Sans for headings. All screens extend a shared `base.html` layout with a consistent navbar and footer.

### 5.2 Screen Descriptions

| Page | Description |
|------|-------------|
| **Landing Page** | Hero banner introducing Resume Builder Pro, a short feature summary, and Register / Log In buttons. |
| **Register / Login** | Simple centred form with username/email and password fields, validation messages, and a link to switch between the two forms. |
| **Dashboard** | Lists the user's saved resumes as cards with 'Edit', 'Preview', and 'Delete' actions, plus a 'Create New Resume' button. |
| **Resume Wizard** | A horizontal progress bar (Education -> Experience -> Skills -> Projects -> Certifications -> Languages -> References) with Back/Next buttons on each step. |
| **Template Selection** | A gallery grid of 27 template thumbnails; clicking one highlights it as selected and updates the live preview. |
| **Resume Preview** | Full-page rendered resume using the chosen template, with 'Edit' and 'Download PDF' buttons fixed at the top. |
| **Profile** | User profile management with email, name, phone, address, and photo upload. |
| **Password Change** | Form for changing password with old/new/confirm fields. |
| **Template Gallery** | Public gallery of all 27 resume templates with preview capabilities. |

### 5.3 Color System

| Variable | Hex | Usage |
|----------|-----|-------|
| --primary | #4f46e5 | Primary actions, buttons, links |
| --primary-50 | #eef2ff | Light backgrounds |
| --secondary | #0ea5e9 | Secondary actions |
| --success | #10b981 | Success states |
| --danger | #ef4444 | Error states, delete actions |
| --warning | #f59e0b | Warning states |
| --dark | #1e293b | Text, headings |
| --gray-50 | #f8fafc | Backgrounds |
| --gray-100 | #f1f5f9 | Card backgrounds |
| --gray-200 | #e2e8f0 | Borders |
| --gray-500 | #64748b | Muted text |
| --gray-900 | #0f172a | Body text |

### 5.4 Responsive Breakpoints

| Breakpoint | Width | Layout |
|------------|-------|--------|
| Mobile | < 576px | Single column, stacked cards |
| Tablet | 576px - 768px | Two-column grid |
| Desktop | 768px - 992px | Three-column grid |
| Large | > 992px | Full-width with max-width container |

### 5.5 JavaScript Features

1. **Alert auto-dismiss** — Bootstrap alerts auto-dismiss after 5 seconds
2. **Back-to-top button** — Appears on scroll, smooth scroll to top
3. **Navbar scroll effect** — Navbar background changes on scroll
4. **Password toggle** — Show/hide password visibility
5. **Scroll animations** — Fade-in animations on scroll
6. **Wizard validation** — Client-side form validation for wizard steps
7. **Counter animation** — Animated number counters on landing page

---

## Chapter 6: Implementation Plan

### 6.1 Technology Stack

| Layer | Technology |
|-------|------------|
| Language | Python 3.12+ |
| Framework | Django 6.0.6 |
| Database (Dev) | SQLite3 |
| Database (Prod) | PostgreSQL |
| Frontend | HTML5, CSS3, Bootstrap 5.3 |
| JavaScript | Vanilla JS (form interactivity, wizard) |
| PDF Generation | xhtml2pdf 0.2.17 |
| Image Handling | Pillow 12.3.0 |
| Production Server | Gunicorn 26.0.0 |
| Static Files | WhiteNoise 6.12.0 |
| Version Control | Git & GitHub |

### 6.2 Project Folder Structure

```
Resume_Builder_Pro/
|-- manage.py
|-- requirements.txt
|-- README.md
|-- Dockerfile
|-- docker-compose.yml
|-- Procfile
|-- render.yaml
|-- .gitignore
|-- .dockerignore
|-- db.sqlite3
|-- Resume_Builder_SDD_4_Members.docx
|
|-- resume_builder_pro/        # Project configuration
|   |-- __init__.py
|   |-- settings.py
|   |-- urls.py
|   |-- wsgi.py
|   |-- asgi.py
|
|-- accounts/                  # Registration, login, profile
|   |-- models.py              # UserProfile model
|   |-- forms.py               # RegistrationForm, ProfileForm, PasswordChangeForm
|   |-- views.py               # 5 views (register, login, logout, profile, password_change)
|   |-- urls.py                # 9 URL patterns
|   |-- admin.py               # UserProfileAdmin
|   |-- tests.py               # 32 unit tests
|   |-- migrations/
|
|-- resumes/                   # Resume CRUD & wizard
|   |-- models.py              # 8 models (Resume, Education, Experience, Skill, Project, Certification, Language, Reference)
|   |-- forms.py               # 8 ModelForms
|   |-- views.py               # 14 views
|   |-- urls.py                # 14 URL patterns
|   |-- admin.py               # ResumeAdmin with 7 TabularInlines
|   |-- tests.py               # 41 unit tests
|   |-- integration_tests.py   # 20 integration tests
|   |-- migrations/
|
|-- templates_app/             # Template gallery & selection
|   |-- models.py              # ResumeTemplate model
|   |-- views.py               # 3 views (gallery, preview, preview_frame)
|   |-- urls.py                # 3 URL patterns
|   |-- admin.py               # ResumeTemplateAdmin
|   |-- tests.py               # 21 unit tests
|   |-- fixtures/
|   |   |-- initial_templates.json  # 27 CV templates
|   |-- migrations/
|
|-- pdf_export/                # PDF generation
|   |-- views.py               # 4 functions (generate_pdf_html, render_to_pdf, download_pdf, pdf_preview)
|   |-- urls.py                # 2 URL patterns
|   |-- tests.py               # 11 unit tests
|   |-- models.py
|
|-- templates/                 # 51 HTML templates
|   |-- base.html
|   |-- landing.html
|   |-- accounts/              # 10 templates (login, register, profile, password_change, password_reset, etc.)
|   |-- resumes/               # 8 templates (dashboard, resume_form, wizard_step, preview, etc.)
|   |-- templates_app/         # 2 templates (gallery, preview)
|   |-- pdf/                   # 29 templates (resume_pdf + 27 CV templates + pdf_preview)
|   |-- snippets/              # 1 template (template_preview_card)
|
|-- static/                    # Static assets
|   |-- css/style.css
|   |-- js/main.js
|   |-- js/wizard.js
|
|-- docs/                      # Documentation
|   |-- Full_Project_Report.md
|   |-- Chapter_5_User_Interface_Design.md
|   |-- Chapter_7_Testing.md
|   |-- Chapter_10_Deployment_Strategy.md
|   |-- Chapter_2_NonFunctional_Requirements.md
|   |-- User_Manual.md
|   |-- Bug_Tracking_Report.md
|   |-- Appendices.md
|
|-- test/                      # Manual testing screenshots (19 PNG files)
```

### 6.3 Django App Breakdown

| App | Responsibility | Models | Views | URL Patterns | Tests |
|-----|----------------|--------|-------|--------------|-------|
| **accounts** | User registration, login/logout, profile management | 1 (UserProfile) | 5 | 9 | 32 |
| **resumes** | Resume CRUD, wizard views, all section models | 8 (Resume, Education, Experience, Skill, Project, Certification, Language, Reference) | 14 | 14 | 61 (41 unit + 20 integration) |
| **templates_app** | Template gallery, selection, and preview rendering | 1 (ResumeTemplate) | 3 | 3 | 21 |
| **pdf_export** | Converting the rendered resume HTML into a downloadable PDF | 0 | 4 | 2 | 11 |
| **Total** | | **10 models** | **26 views** | **28 URL patterns** | **125 tests** |

---

## Chapter 7: Testing Strategy

### 7.1 Testing Overview

The testing strategy follows Django's built-in testing framework, which extends Python's `unittest` module. The test suite comprises **125 tests** distributed across four application modules, all of which pass successfully with a **100% pass rate**.

**Test execution command:**
```bash
python manage.py test accounts resumes resumes.integration_tests templates_app pdf_export
```

### 7.2 Unit Testing (105 Tests)

#### 7.2.1 Accounts Module — 32 Tests

| Test Class | Tests | What is Tested |
|------------|-------|----------------|
| RegistrationFormTest | 6 | Valid registration, duplicate email, duplicate username, password mismatch, short username, invalid username characters |
| ProfileFormTest | 3 | Valid profile, invalid phone, duplicate email for different user |
| UserProfileModelTest | 2 | Profile creation, string representation |
| RegisterViewTest | 5 | GET form, successful POST, duplicate rejected, password mismatch, redirect if authenticated |
| LoginViewTest | 5 | GET form, successful login, failed login, wrong password, redirect if authenticated |
| LogoutViewTest | 2 | Logout redirect, redirect to login |
| ProfileViewTest | 5 | Requires login, GET loads, POST updates, data persists, unauthenticated redirect |
| PasswordChangeViewTest | 4 | GET loads, successful change, wrong old password, unauthenticated redirect |

#### 7.2.2 Resumes Module — 41 Tests

| Test Class | Tests | What is Tested |
|------------|-------|----------------|
| ResumeModelTest | 3 | Creation/str, ordering by -updated_at, template nullable |
| EducationModelTest | 2 | Creation/str, end_year nullable |
| ExperienceModelTest | 1 | Creation/str |
| SkillModelTest | 2 | Creation/str/level, default proficiency |
| ProjectModelTest | 1 | Creation/str |
| CertificationModelTest | 1 | Creation/str |
| LanguageModelTest | 2 | Creation/str, default proficiency |
| ReferenceModelTest | 1 | Creation/str |
| DashboardViewTest | 4 | Requires login, loads, shows resumes, empty state |
| ResumeCreateViewTest | 3 | Page loads, POST creates, redirects to wizard |
| WizardStepViewTest | 14 | Each wizard step loads + adds entry (education, experience, skills, projects, certifications, languages, references) + prevents other user access |
| ResumeEditViewTest | 2 | Edit page loads, POST updates title |
| ResumeDeleteViewTest | 2 | Delete page loads, POST deletes |
| ResumePreviewViewTest | 1 | Preview loads with education + skill data |
| TemplateSelectViewTest | 1 | Template select page loads |

#### 7.2.3 PDF Export Module — 11 Tests

| Test Class | Tests | What is Tested |
|------------|-------|----------------|
| GeneratePdfHtmlTest | 2 | HTML generation contains resume data, empty resume works |
| DownloadPdfViewTest | 6 | Authenticated download, unauthenticated redirect, other user 404, content type, non-empty content, PDF with all sections |
| PdfPreviewViewTest | 3 | Authenticated preview, unauthenticated redirect, other user 404 |

#### 7.2.4 Templates App Module — 21 Tests

| Test Class | Tests | What is Tested |
|------------|-------|----------------|
| ResumeTemplateModelTest | 8 | Creation, str, default is_active, default description blank, preview_image nullable, created_at auto, ordering by name, unique instances |
| TemplateGalleryViewTest | 7 | Gallery loads, renders correct template, excludes inactive, empty state, shows multiple active, only shows active, no login required |
| TemplatePreviewViewTest | 6 | Loads when authenticated, redirects when not, redirects to login, other user can access, nonexistent returns 404, inactive template loads |

### 7.3 Integration Testing (20 Tests)

| Test Class | Tests | What is Tested |
|------------|-------|----------------|
| FullRegistrationToResumeFlowTest | 1 | Complete journey: register -> login -> create resume -> all 7 wizard steps -> preview -> PDF download |
| ProfileUpdateFlowTest | 1 | Profile update persists (email, name, phone, address) |
| PasswordChangeFlowTest | 1 | Password change works, old password fails, new password succeeds |
| ResumeAuthorizationFlowTest | 7 | User B cannot see User A's dashboard, preview, edit, delete, PDF, wizard; User A can delete own |
| DashboardStateTransitionTest | 3 | Empty dashboard, populated after creation, empty after deletion |
| PDFGenerationIntegrationTest | 3 | PDF with all sections, PDF preview renders, HTML contains all data |
| TemplateSelectionFlowTest | 4 | Page after wizard, shows active templates, requires auth, requires ownership |

### 7.4 Manual Testing

Manual testing was performed across Chrome, Firefox, and Edge browsers at both desktop and mobile widths. A total of **19 screenshots** were captured during manual testing sessions on July 23, 2026, covering:

| Test Type | Cases |
|-----------|-------|
| UI Test Cases (MT-001 to MT-010) | 10 |
| UX Test Cases (UX-001 to UX-006) | 6 |
| Browser Compatibility | Chrome, Firefox, Edge |
| Responsive Design | Desktop, Tablet, Mobile |

#### 7.4.1 Manual Testing Evidence (Screenshots)

All screenshots are stored in the `test/` directory of the repository.

| # | Screenshot | Description | Timestamp |
|---|-----------|-------------|-----------|
| 1 | `homepage.png` | Landing page — hero banner, feature summary, and Call-to-Action buttons | July 23, 2026 |
| 2 | `Screenshot 2026-07-23 110055.png` | User registration page — form with username, email, and password fields | 11:00 AM |
| 3 | `Screenshot 2026-07-23 111023.png` | User login page — authentication form with validation messages | 11:10 AM |
| 4 | `Screenshot 2026-07-23 111059.png` | Dashboard — empty state with "No resumes yet" message and create button | 11:10 AM |
| 5 | `Screenshot 2026-07-23 111241.png` | Create resume page — option to use a template or start from scratch | 11:12 AM |
| 6 | `Screenshot 2026-07-23 111322.png` | Resume wizard — Education step with form fields and progress indicator | 11:13 AM |
| 7 | `Screenshot 2026-07-23 111347.png` | Resume wizard — Experience step with company, role, and date fields | 11:13 AM |
| 8 | `Screenshot 2026-07-23 111430.png` | Resume wizard — Skills step with proficiency level selector | 11:14 AM |
| 9 | `Screenshot 2026-07-23 111608.png` | Resume wizard — Projects step with name, description, and link fields | 11:16 AM |
| 10 | `Screenshot 2026-07-23 113033.png` | Template selection page — gallery grid of 27 CV templates | 11:30 AM |
| 11 | `Screenshot 2026-07-23 113330.png` | Template preview — iframe preview of selected template with sample data | 11:33 AM |
| 12 | `Screenshot 2026-07-23 113420.png` | Resume preview — full rendered resume using selected template | 11:34 AM |
| 13 | `Screenshot 2026-07-23 113555.png` | PDF preview — rendered PDF output of the completed resume | 11:35 AM |
| 14 | `Screenshot 2026-07-23 113622.png` | PDF download — generated PDF file opened in browser | 11:36 AM |
| 15 | `Screenshot 2026-07-23 113705.png` | User profile page — profile management with photo upload | 11:37 AM |
| 16 | `Screenshot 2026-07-23 113741.png` | Password change page — old/new/confirm password form | 11:37 AM |
| 17 | `Screenshot 2026-07-23 113807.png` | Django admin panel — template management with 27 templates loaded | 11:38 AM |
| 18 | `Screenshot 2026-07-23 113833.png` | Template gallery page — public gallery with preview cards | 11:38 AM |
| 19 | `Screenshot 2026-07-23 114921.png` | Dashboard with resumes — populated dashboard showing saved resumes | 11:49 AM |

### 7.5 Test Results Summary

| Module | Tests | Passed | Failed | Pass Rate |
|--------|-------|--------|--------|-----------|
| accounts (Unit) | 32 | 32 | 0 | 100% |
| resumes (Unit) | 41 | 41 | 0 | 100% |
| resumes (Integration) | 20 | 20 | 0 | 100% |
| pdf_export (Unit) | 11 | 11 | 0 | 100% |
| templates_app (Unit) | 21 | 21 | 0 | 100% |
| **Total** | **125** | **125** | **0** | **100%** |

### 7.6 Coverage Analysis

| Component | Estimated Coverage |
|-----------|-------------------|
| Models | ~95% |
| Forms | ~90% |
| Views | ~85% |
| Templates | ~70% |
| URLs | ~95% |
| Authentication | ~95% |
| PDF Export | ~80% |

### 7.7 Bug Tracking Summary

| Severity | Count | All Fixed |
|----------|-------|-----------|
| Critical | 3 | Yes |
| Major | 5 | Yes |
| Minor | 7 | Yes |
| **Total** | **15** | **Yes** |

Key bugs fixed:
1. Missing xhtml2pdf dependency (Critical)
2. Missing CV template files (Critical)
3. WhiteNoise not configured for static files (Critical)
4. DEBUG hardcoded to True (Major)
5. ALLOWED_HOSTS set to wildcard (Major)
6. template_preview using .get() instead of get_object_or_404() (Major)
7. Zero test coverage for templates_app (Major)
8. No integration tests (Major)
9. Template selection not persisting (Major)
10. Various minor UI and code quality issues (7 minor)

---

## Chapter 8: Risk Analysis

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| PDF rendering differs from on-screen preview (fonts, spacing) | High | Medium | Standardised on xhtml2pdf early and tested every template against it before UI was finalised. |
| Scope creep from adding extra templates or features late in the schedule | Medium | High | Locked the feature list after Chapter 2 sign-off; extra ideas went into a 'Future Work' list. |
| Team member unavailability during the two-week window | High | Low | Daily short check-ins and clearly owned modules so any one member's task can be picked up by another. |
| Data loss or corruption during wizard multi-step entry | High | Medium | Saved progress to the database at the end of each wizard step rather than only at final submission. |
| Deployment issues (missing dependencies, static files not served) | Medium | Medium | Maintained a pinned requirements.txt and tested a full deployment at least 3 days before the presentation date. |
| Security vulnerabilities (XSS, CSRF, SQL injection) | High | Low | Django's built-in protections (CSRF tokens, parameterised queries, template auto-escaping, password hashing). |

---

## Chapter 9: Project Schedule

| Phase | Key Tasks | Duration |
|-------|-----------|----------|
| Requirements & Design (Days 1-3) | Finalise requirements, ER diagram, use cases, wireframes, and design document. | 3 days |
| Core Backend (Days 4-6) | Django project setup, models, migrations, admin panel, authentication. | 3 days |
| Wizard & Frontend (Days 7-9) | Build the multi-step resume form, Bootstrap templates, and JavaScript step logic. | 3 days |
| Templates, Preview & PDF (Days 10-11) | Implement 27 resume templates, live preview, and PDF export. | 2 days |
| Testing & Fixes (Days 12-13) | Unit, integration, and manual testing; bug fixes; supervision check-in. | 2 days |
| Deployment & Presentation Prep (Day 14) | Deploy to hosting platform, finalise GitHub repo and README, rehearse presentation. | 1 day |

### Work Allocation

| Member | Primary Responsibilities |
|--------|-------------------------|
| **Opoka Eric** — Backend & Database Lead | Django project setup and configuration; Design and implement all models and database migrations; Admin panel configuration; Co-author Chapters 3 and 4. |
| **Opeto Isaac** — Authentication & PDF Generation Lead | User registration, login/logout, and profile management; PDF generation logic and the pdf_export app; Security review; Co-author Chapter 2 and Chapter 10. |
| **Ojok Isaac** — Frontend & UI/UX Lead | Bootstrap 5 templates for all wizard steps and the dashboard; Multi-step wizard JavaScript logic; Design and implementation of 27 resume templates; Co-author Chapter 5. |
| **Auma Dilish** — Testing, Documentation & Deployment Lead | Unit, integration, and manual testing; Bug tracking and coordination of fixes; User manual, references, appendices, and final report compilation; GitHub repository management and deployment. |

---

## Chapter 10: Deployment Strategy

### 10.1 Overview

Resume Builder Pro is designed for containerised deployment to cloud platforms. The strategy ensures reproducibility, security, and scalability across development, staging, and production environments.

### 10.2 Deployment Architecture

```
[Client Browser] <--HTTPS--> [Reverse Proxy (Nginx)]
                                      |
                              [Application Server (Gunicorn)]
                                      |
                              [Django Application]
                                      |
                        [Database (PostgreSQL)] + [Static Files (WhiteNoise)]
```

### 10.3 Environment Configuration

| Environment | Database | Debug | Hosts | SSL |
|-------------|----------|-------|-------|-----|
| **Development** | SQLite3 | True | localhost, 127.0.0.1 | No |
| **Production** | PostgreSQL | False | Domain name | Yes (HTTPS) |

**Required Environment Variables (Production):**

| Variable | Description | Example |
|----------|-------------|---------|
| `DJANGO_SECRET_KEY` | Cryptographic secret for sessions/CSRF | `django-insecure-...` |
| `DJANGO_DEBUG` | Set to `False` in production | `False` |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated allowed hostnames | `resumebuilder.onrender.com` |
| `DATABASE_URL` | PostgreSQL connection string | `postgres://user:pass@host:5432/db` |
| `WEB_CONCURRENCY` | Gunicorn worker count | `3` |

### 10.4 Containerisation

**Dockerfile:**
```dockerfile
FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN python manage.py collectstatic --noinput
EXPOSE 8000
CMD ["gunicorn", "resume_builder_pro.wsgi:application", "--bind", "0.0.0.0:8000"]
```

**docker-compose.yml:**
```yaml
version: '3.8'
services:
  web:
    build: .
    command: python manage.py runserver 0.0.0.0:8000
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    environment:
      - DJANGO_DEBUG=True
```

### 10.5 Cloud Platform Deployment (Render)

**Steps:**
1. Push to GitHub repository
2. Create Render Web Service connected to the GitHub repo
3. Configure build command: `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
4. Configure start command: `gunicorn resume_builder_pro.wsgi:application`
5. Add environment variables (SECRET_KEY, DATABASE_URL, etc.)
6. Add PostgreSQL database via Render Dashboard
7. Verify deployment at the generated URL

### 10.6 Security Checklist

- [x] `DEBUG` reads from `DJANGO_DEBUG` environment variable (defaults to `False`)
- [x] `DJANGO_SECRET_KEY` set via environment variable
- [x] `ALLOWED_HOSTS` reads from `DJANGO_ALLOWED_HOSTS` environment variable
- [x] `SECURE_SSL_REDIRECT = True` (when not DEBUG)
- [x] `SESSION_COOKIE_SECURE = True` (when not DEBUG)
- [x] `CSRF_COOKIE_SECURE = True` (when not DEBUG)
- [x] `SECURE_HSTS_SECONDS = 31536000`
- [x] `SECURE_HSTS_INCLUDE_SUBDOMAINS = True`
- [x] `SECURE_HSTS_PRELOAD = True`
- [x] `X_FRAME_OPTIONS = 'DENY'`
- [x] `SECURE_CONTENT_TYPE_NOSNIFF = True`
- [x] WhiteNoise middleware configured for static file serving
- [x] `.gitignore` excludes `db.sqlite3`, `media/`, `__pycache__/`, `.env`

---

## Project Statistics

| Metric | Value |
|--------|-------|
| Total Django Apps | 4 |
| Total Models | 10 |
| Total Views | 26 |
| Total URL Patterns | 28 |
| Total HTML Templates | 51 |
| Total Static Files | 3 |
| Total Tests | 125 |
| Test Pass Rate | 100% |
| Total Bugs Found | 15 |
| Bugs Fixed | 15 (100%) |
| CV Templates | 27 |
| Total Git Commits | 62 |
| Test Screenshots | 19 |
| Documentation Files | 8 |
| Dependencies | 6 (Django, Gunicorn, WhiteNoise, psycopg2-binary, xhtml2pdf, Pillow) |

---

## Appendices

### Appendix A: URL Route Reference

| URL Pattern | View | Auth Required | HTTP Methods |
|-------------|------|---------------|--------------|
| `/` | Landing page | No | GET |
| `/admin/` | Django admin | Yes (staff) | GET, POST |
| `/accounts/register/` | register_view | No | GET, POST |
| `/accounts/login/` | login_view | No | GET, POST |
| `/accounts/logout/` | logout_view | Yes | POST |
| `/accounts/profile/` | profile_view | Yes | GET, POST |
| `/accounts/password-change/` | password_change_view | Yes | GET, POST |
| `/accounts/password-reset/` | PasswordResetView | No | GET, POST |
| `/accounts/password-reset/done/` | PasswordResetDoneView | No | GET |
| `/accounts/password-reset-confirm/` | PasswordResetConfirmView | No | GET, POST |
| `/accounts/password-reset-complete/` | PasswordResetCompleteView | No | GET |
| `/resumes/` | dashboard | Yes | GET |
| `/resumes/create/` | resume_create | Yes | GET, POST |
| `/resumes/create-from-template/<id>/` | create_from_template | Yes | GET |
| `/resumes/<id>/edit/` | resume_edit | Yes | GET, POST |
| `/resumes/<id>/delete/` | resume_delete | Yes | GET, POST |
| `/resumes/<id>/wizard/<step>/` | wizard_step | Yes | GET, POST |
| `/resumes/<id>/wizard/<step>/<entry>/edit/` | wizard_entry_edit | Yes | GET, POST |
| `/resumes/<id>/wizard/<step>/<entry>/delete/` | wizard_entry_delete | Yes | GET, POST |
| `/resumes/<id>/templates/` | template_select | Yes | GET, POST |
| `/resumes/<id>/preview/` | resume_preview | Yes | GET |
| `/resumes/<id>/preview/frame/` | resume_preview_frame | Yes | GET |
| `/resumes/<id>/<section>/<item>/edit/` | section_edit | Yes | GET, POST |
| `/resumes/<id>/<section>/<item>/delete/` | section_delete | Yes | GET, POST |
| `/templates/` | template_gallery | No | GET |
| `/templates/<id>/preview/` | template_preview | Yes | GET |
| `/templates/<id>/frame/` | template_preview_frame | Yes | GET |
| `/pdf/<id>/download/` | download_pdf | Yes | GET |
| `/pdf/<id>/preview/` | pdf_preview | Yes | GET |

### Appendix B: Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| Django | 6.0.6 | Web framework |
| gunicorn | latest | Production WSGI server |
| whitenoise | latest | Static file serving |
| psycopg2-binary | latest | PostgreSQL adapter |
| xhtml2pdf | latest | HTML-to-PDF conversion |
| Pillow | latest | Image processing |

### Appendix C: Future Enhancements

1. AI-powered resume content suggestions
2. Multi-language resume generation
3. LinkedIn profile import
4. Resume versioning and comparison
5. Collaboration features for team resumes
6. Payment processing for premium templates
7. Email resume sharing
8. Resume analytics (views, downloads)
9. Mobile app (React Native / Flutter)
10. REST API for third-party integrations

---

**Report compiled by:** Auma Dilish — Testing, Documentation & Deployment Lead
**Date:** July 23, 2026
