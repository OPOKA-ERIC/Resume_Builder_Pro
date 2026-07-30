# Appendices & Final Report Compilation

**Resume Builder Pro**
**Group C — BSE2301**
**July 2026**

---

## Appendix A: Project Member Roles and Contributions

| Member | Role | Primary Responsibilities |
|--------|------|------------------------|
| **Opoka Eric** | Backend & Database Lead / Portfolio Generator | Django project setup and configuration; Design and implement all models and database migrations; Admin panel configuration; **Portfolio Generator** (shareable portfolio pages with QR codes) |
| **Opeto Isaac** | Authentication & PDF Generation / Job Match Analyzer | User registration, login, logout, profile management, PDF generation; **Job Match Analyzer** (skill gap analysis, proficiency scoring, AI-powered recommendations) |
| **Ojok Isaac** | Frontend & UI/UX Lead / Job Adverts Integration | Bootstrap templates, wizard JavaScript, 27 resume templates; **Job Adverts Integration** (LinkedIn and external platform import) |
| **Auma Dilish** | Testing, Documentation & Deployment Lead | Unit testing, integration testing, bug tracking, user manual, project documentation, GitHub management, deployment configuration |
| **Namuganza Isabella** | Admin Configuration & Django Admin Lead | Django admin panel configuration, admin interface for users/resumes/templates/job analyses, admin dashboard reporting, data management |

---

## Appendix B: System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Client Browser                         │
│              (HTML/CSS/JS via Bootstrap 5)                   │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTP/HTTPS
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                   Django Application                         │
│                                                              │
│  ┌──────────┐  ┌──────────┐  ┌────────────┐  ┌──────────┐  ┌─────────────┐  ┌──────────┐  ┌──────────┐ │
│  │ accounts  │  │ resumes  │  │templates_app│  │pdf_export│  │job_analysis │  │ portfolio│  │job_board │ │
│  │  (Auth)   │  │  (CRUD)  │  │ (Gallery)  │  │  (PDF)   │  │ (Matching)  │  │ (Shares) │  │(Adverts)│ │
│  └─────┬─────┘  └────┬─────┘  └─────┬──────┘  └────┬─────┘  └──────┬──────┘  └────┬─────┘  └────┬─────┘ │
│        │              │              │               │        │
│        └──────────────┴──────────────┴───────────────┘        │
│                           │                                   │
│                    Django ORM Layer                            │
│                           │                                   │
└───────────────────────────┼───────────────────────────────────┘
                            │
              ┌─────────────┼──────────────┐
              │             │              │
              ▼             ▼              ▼
        ┌──────────┐  ┌──────────┐  ┌──────────────┐
        │ SQLite3  │  │ Static   │  │ xhtml2pdf    │
        │  (Dev)   │  │  Files   │  │  (PDF Gen)   │
        └──────────┘  └──────────┘  └──────────────┘
```

### Production Architecture

```
[Client] ←HTTPS→ [Nginx Reverse Proxy]
                        │
                [Gunicorn WSGI Server]
                        │
                [Django Application]
                        │
          [PostgreSQL] + [WhiteNoise Static]
```

---

## Appendix C: Database Schema

### Entity Relationship Description

**ResumeTemplate**
| Field | Type | Constraints |
|-------|------|-------------|
| id | BigAutoField | PK |
| name | CharField(100) | Required |
| description | TextField | Blank allowed |
| preview_image | ImageField | Upload to `template_previews/`, nullable |
| html_file | CharField(200) | Required |
| is_active | BooleanField | Default: True |
| created_at | DateTimeField | Auto-set on creation |

**UserProfile** (extends Django User)
| Field | Type | Constraints |
|-------|------|-------------|
| id | BigAutoField | PK |
| user | OneToOneField → User | CASCADE |
| phone | CharField | Optional |
| address | TextField | Optional |
| photo | ImageField | Optional |

**Resume**
| Field | Type | Constraints |
|-------|------|-------------|
| id | BigAutoField | PK |
| user | ForeignKey → User | CASCADE, related_name='resumes' |
| title | CharField(200) | Required |
| template | ForeignKey → ResumeTemplate | SET_NULL, nullable |
| created_at | DateTimeField | Auto-set |
| updated_at | DateTimeField | Auto-updated |

**Education, Experience, Skill, Project, Certification, Language, Reference**
Each has a `ForeignKey → Resume` with `CASCADE` deletion and model-specific fields as described in the User Manual.

**JobAnalysis** — stores job description analysis results with match score
| Field | Type | Constraints |
|-------|------|-------------|
| id | BigAutoField | PK |
| user | ForeignKey → User | CASCADE |
| resume | ForeignKey → Resume | CASCADE |
| job_title | CharField | Optional |
| company | CharField | Optional |
| job_description | TextField | Required |
| match_score | FloatField | 0-100 scale |
| created_at | DateTimeField | Auto-set |

**SkillScore** — individual skill scoring within a JobAnalysis
| Field | Type | Constraints |
|-------|------|-------------|
| id | BigAutoField | PK |
| job_analysis | ForeignKey → JobAnalysis | CASCADE |
| skill_name | CharField | Required |
| required_level | CharField | Required level from job |
| user_level | CharField | Current user proficiency |
| score | FloatField | Match score 0-100 |
| recommendation | TextField | AI suggestion |

**Portfolio** — shareable public portfolio page
| Field | Type | Constraints |
|-------|------|-------------|
| id | BigAutoField | PK |
| user | ForeignKey → User | CASCADE |
| resume | ForeignKey → Resume | CASCADE |
| slug | SlugField | Unique, used in URL |
| qr_code | ImageField | Uploaded QR image |
| is_published | BooleanField | Default: False |
| views | IntegerField | View counter |
| created_at | DateTimeField | Auto-set |

**JobAdvert** — imported job listing
| Field | Type | Constraints |
|-------|------|-------------|
| id | BigAutoField | PK |
| source | CharField | e.g. 'LinkedIn' |
| source_id | CharField | External platform ID |
| title | CharField | Job title |
| company | CharField | Company name |
| description | TextField | Full job description |
| url | URLField | Original listing URL |
| posted_date | DateField | When posted |
| imported_by | ForeignKey → User | Who imported it |
| created_at | DateTimeField | Auto-set |

### Key Relationships

- User → (1:N) → Resume
- Resume → (1:N) → Education, Experience, Skill, Project, Certification, Language, Reference
- ResumeTemplate → (1:N) → Resume
- User → (1:1) → UserProfile
- User → (1:N) → JobAnalysis
- JobAnalysis → (1:N) → SkillScore
- User → (1:N) → Portfolio
- User → (1:N) → JobAdvert

---

## Appendix D: URL Route Reference

| URL Pattern | View | Name | Auth Required | Method |
|-------------|------|------|---------------|--------|
| `/` | TemplateView (landing.html) | `landing` | No | GET |
| `/admin/` | Django Admin | — | Staff | GET/POST |
| `/accounts/register/` | `register_view` | `accounts:register` | No | GET/POST |
| `/accounts/login/` | `login_view` | `accounts:login` | No | GET/POST |
| `/accounts/logout/` | `logout_view` | `accounts:logout` | No | GET |
| `/accounts/profile/` | `profile_view` | `accounts:profile` | Yes | GET/POST |
| `/accounts/password-change/` | `password_change_view` | `accounts:password_change` | Yes | GET/POST |
| `/resumes/` | `dashboard` | `resumes:dashboard` | Yes | GET |
| `/resumes/create/` | `resume_create` | `resumes:resume_create` | Yes | GET/POST |
| `/resumes/<id>/edit/` | `resume_edit` | `resumes:resume_edit` | Yes | GET/POST |
| `/resumes/<id>/delete/` | `resume_delete` | `resumes:resume_delete` | Yes | GET/POST |
| `/resumes/<id>/wizard/<step>/` | `wizard_step` | `resumes:wizard_step` | Yes | GET/POST |
| `/resumes/<id>/wizard/<step>/<entry_id>/edit/` | `wizard_entry_edit` | `resumes:wizard_entry_edit` | Yes | GET/POST |
| `/resumes/<id>/wizard/<step>/<entry_id>/delete/` | `wizard_entry_delete` | `resumes:wizard_entry_delete` | Yes | GET/POST |
| `/resumes/<id>/templates/` | `template_select` | `resumes:template_select` | Yes | GET/POST |
| `/resumes/<id>/preview/` | `resume_preview` | `resumes:resume_preview` | Yes | GET |
| `/pdf/<id>/download/` | `download_pdf` | `pdf_export:download_pdf` | Yes | GET |
| `/pdf/<id>/preview/` | `pdf_preview` | `pdf_export:pdf_preview` | Yes | GET |
| `/templates/` | `template_gallery` | `templates_app:gallery` | No | GET |
| `/templates/<id>/preview/` | `template_preview` | `templates_app:preview` | Yes | GET |
| `/analysis/` | `job_analysis_dashboard` | `job_analysis:dashboard` | Yes | GET |
| `/analysis/<resume_id>/match/` | `run_job_match` | `job_analysis:run_match` | Yes | GET/POST |
| `/analysis/<id>/results/` | `view_analysis_results` | `job_analysis:results` | Yes | GET |
| `/portfolio/` | `portfolio_list` | `portfolio:list` | Yes | GET |
| `/portfolio/<slug>/` | `public_portfolio_view` | `portfolio:public` | No | GET |
| `/portfolio/<id>/generate/` | `generate_portfolio` | `portfolio:generate` | Yes | GET/POST |
| `/jobs/` | `advert_list` | `job_board:list` | Yes | GET |
| `/jobs/import/` | `import_adverts` | `job_board:import` | Yes | GET/POST |
| `/jobs/<id>/` | `advert_detail` | `job_board:detail` | Yes | GET |
| `/ai/suggest/` | `ai_suggestions` | `ai_engine:suggest` | Yes | GET/POST |

---

## Appendix E: Test Case Catalog

### accounts/tests.py — 32 Unit Tests

| # | Test Class | Test Method | Description |
|---|-----------|-------------|-------------|
| 1 | RegistrationFormTest | test_valid_registration | Valid form data passes validation |
| 2 | RegistrationFormTest | test_duplicate_email | Duplicate email rejected |
| 3 | RegistrationFormTest | test_duplicate_username | Duplicate username rejected |
| 4 | RegistrationFormTest | test_password_mismatch | Mismatched passwords rejected |
| 5 | RegistrationFormTest | test_short_username | Username < 3 chars rejected |
| 6 | RegistrationFormTest | test_invalid_username_characters | Special chars in username rejected |
| 7 | ProfileFormTest | test_valid_profile | Valid profile form passes |
| 8 | ProfileFormTest | test_invalid_phone | Invalid phone format rejected |
| 9 | ProfileFormTest | test_duplicate_email_different_user | Email collision detected |
| 10 | UserProfileModelTest | test_profile_created_on_user_creation | Profile __str__ returns correct value |
| 11 | UserProfileModelTest | test_profile_str | Profile string representation |
| 12 | RegisterViewTest | test_get_register | GET returns 200 with form |
| 13 | RegisterViewTest | test_successful_registration | POST creates user and profile |
| 14 | RegisterViewTest | test_duplicate_registration | Duplicate rejected, stays on page |
| 15 | RegisterViewTest | test_register_password_mismatch | Mismatched passwords stay on page |
| 16 | RegisterViewTest | test_redirect_authenticated_user | Authenticated user redirected |
| 17 | LoginViewTest | test_get_login | GET returns 200 |
| 18 | LoginViewTest | test_successful_login | Valid credentials redirect |
| 19 | LoginViewTest | test_failed_login | Wrong password stays on page |
| 20 | LoginViewTest | test_login_wrong_password | Wrong password with logging |
| 21 | LoginViewTest | test_redirect_authenticated_user | Auth user redirected |
| 22 | LogoutViewTest | test_logout | Logout redirects |
| 23 | LogoutViewTest | test_logout_redirects_to_login | Redirects to login page |
| 24 | ProfileViewTest | test_profile_requires_login | Unauthenticated redirect |
| 25 | ProfileViewTest | test_get_profile | GET returns 200 with form |
| 26 | ProfileViewTest | test_update_profile | POST updates profile |
| 27 | ProfileViewTest | test_profile_update_data | Data persisted correctly |
| 28 | ProfileViewTest | test_unauthenticated_access | Redirect to login |
| 29 | PasswordChangeViewTest | test_get_password_change | GET returns 200 |
| 30 | PasswordChangeViewTest | test_successful_password_change | Password updated |
| 31 | PasswordChangeViewTest | test_wrong_old_password | Wrong password stays on page |

### resumes/tests.py — 41 Unit Tests

| # | Test Class | Test Method | Description |
|---|-----------|-------------|-------------|
| 1 | ResumeModelTest | test_resume_creation | Resume created and __str__ correct |
| 2 | ResumeModelTest | test_resume_ordering | Ordering by -updated_at |
| 3 | ResumeModelTest | test_resume_template_nullable | Template can be None |
| 4 | EducationModelTest | test_education_creation | Education __str__ format |
| 5 | EducationModelTest | test_education_end_date_nullable | End date can be None |
| 6 | ExperienceModelTest | test_experience_creation | Experience __str__ format |
| 7 | SkillModelTest | test_skill_creation | Skill __str__ and level |
| 8 | SkillModelTest | test_skill_default_proficiency | Default is 'intermediate' |
| 9 | ProjectModelTest | test_project_creation | Project __str__ |
| 10 | CertificationModelTest | test_certification_creation | Certification __str__ |
| 11 | LanguageModelTest | test_language_creation | Language __str__ |
| 12 | LanguageModelTest | test_language_default_proficiency | Default is 'fluent' |
| 13 | ReferenceModelTest | test_reference_creation | Reference __str__ |
| 14 | DashboardViewTest | test_dashboard_requires_login | Unauthenticated redirect |
| 15 | DashboardViewTest | test_dashboard_loads | GET returns 200 |
| 16 | DashboardViewTest | test_dashboard_shows_resumes | Resumes displayed |
| 17 | DashboardViewTest | test_dashboard_empty_state | Empty message shown |
| 18 | ResumeCreateViewTest | test_create_page_loads | GET returns 200 |
| 19 | ResumeCreateViewTest | test_create_resume | POST creates resume |
| 20 | ResumeCreateViewTest | test_create_redirects_to_wizard | Redirects to wizard |
| 21 | WizardStepViewTest | test_wizard_education_loads | Education step loads |
| 22-34 | WizardStepViewTest | (12 more tests) | All wizard steps load and save |

### pdf_export/tests.py — 11 Unit Tests

| # | Test Class | Test Method | Description |
|---|-----------|-------------|-------------|
| 1-2 | GeneratePdfHtmlTest | test_generate_pdf_html, empty | HTML contains resume data |
| 3-8 | DownloadPdfViewTest | auth/unauth/other/content/sections | PDF download behavior |
| 9 | PdfPreviewViewTest | test_pdf_preview_authenticated | Preview renders |

### templates_app/tests.py — 21 Unit Tests

| # | Test Class | Test Method | Description |
|---|-----------|-------------|-------------|
| 1-8 | ResumeTemplateModelTest | model tests | Creation, __str__, defaults, ordering |
| 9-15 | TemplateGalleryViewTest | view tests | Loads, active/inactive filtering |
| 16-21 | TemplatePreviewViewTest | view tests | Auth, 404, inactive templates |

### resumes/integration_tests.py — 20 Integration Tests

| # | Test Class | Test Method | Description |
|---|-----------|-------------|-------------|
| 1 | FullRegistrationToResumeFlowTest | test_complete_user_journey | Register→Login→Create→Wizard→Preview→PDF |
| 2 | ProfileUpdateFlowTest | test_profile_update_persists | Profile changes persisted |
| 3 | PasswordChangeFlowTest | test_password_change_and_relogin | Old password fails, new works |
| 4-10 | ResumeAuthorizationFlowTest | 7 tests | Cross-user access denied |
| 11-13 | DashboardStateTransitionTest | 3 tests | Empty→populated→empty |
| 14-16 | PDFGenerationIntegrationTest | 3 tests | PDF with all sections |
| 17-20 | TemplateSelectionFlowTest | 4 tests | Template gallery and selection |

---

## Appendix F: Bug Report Summary

See **Bug_Tracking_Report.md** for the complete bug registry.

| Bug ID | Severity | Status | Module |
|--------|----------|--------|--------|
| BUG-001 | Critical | FIXED | pdf_export (dependency) |
| BUG-002 | Critical | FIXED | templates_app (missing templates) |
| BUG-003 | Critical | FIXED | settings.py (WhiteNoise) |
| BUG-004 | Major | FIXED | settings.py (DEBUG) |
| BUG-005 | Major | FIXED | settings.py (ALLOWED_HOSTS) |
| BUG-006 | Major | FIXED | templates_app (404 handling) |
| BUG-007 | Minor | FIXED | accounts (unused import) |
| BUG-008 | Major | FIXED | templates_app (no tests) |
| BUG-009 | Major | FIXED | resumes (no integration tests) |
| BUG-010 | Minor | FIXED | Documentation (WeasyPrint refs) |
| BUG-011 | Major | FIXED | resumes (template not saved) |
| BUG-012 | Minor | FIXED | resumes (wizard back nav) |
| BUG-013 | Minor | FIXED | resumes (no edit/delete entries) |
| BUG-014 | Minor | FIXED | resumes (edit only title) |
| BUG-015 | Minor | FIXED | accounts (login template) |

---

## Appendix G: Technology Stack

### Backend

| Technology | Version | Purpose |
|-----------|---------|---------|
| Python | 3.14 | Programming language |
| Django | 6.0.6 | Web framework |
| xhtml2pdf | 0.2.17 | PDF generation |
| Pillow | Latest | Image processing |

### Frontend

| Technology | Version | Purpose |
|-----------|---------|---------|
| Bootstrap | 5.3.0 | CSS framework |
| Bootstrap Icons | 1.10.0 | Icon library |
| Custom CSS | — | Application-specific styles |
| JavaScript | Vanilla | Alert auto-dismiss |

### Infrastructure

| Technology | Purpose |
|-----------|---------|
| SQLite3 | Development database |
| PostgreSQL | Production database |
| Gunicorn | WSGI HTTP server |
| WhiteNoise | Static file serving |
| Docker | Containerization |
| Git/GitHub | Version control |

### Python Dependencies (requirements.txt)

```
Django==6.0.6
gunicorn
whitenoise
psycopg2-binary
xhtml2pdf
Pillow
openai           # AI integration for job analysis and recommendations
qrcode           # QR code generation for portfolio sharing
beautifulsoup4   # Web scraping for job advert import
requests         # HTTP requests for external API calls
```

---

## Appendix H: User Manual Reference

For complete user-facing documentation, see **User_Manual.md**.

Key sections:
1. Getting Started (Registration & Login)
2. Profile Management
3. Creating a Resume (7-step wizard)
4. Viewing and Editing Resumes
5. Choosing a Template
6. Previewing and Downloading PDF
7. Account Settings
8. Troubleshooting FAQ

---

## Appendix I: Final Project Summary & Reflections

### Project Overview

Resume Builder Pro is a full-stack Django web application that enables users to create professional resumes through a guided, step-by-step interface. The application demonstrates practical implementation of software engineering principles including modular design, security best practices, automated testing, and deployment readiness.

### Key Achievements

1. **Modular Architecture:** Seven well-separated Django apps (accounts, resumes, templates_app, pdf_export, job_analysis, portfolio, job_board) plus an AI engine service layer, following the Django best practice of "small, reusable apps."

2. **Comprehensive Test Suite:** 125 automated tests covering unit testing of models, forms, and views across all modules, plus integration tests for end-to-end user workflows. All tests pass consistently.

3. **Security Implementation:** Password hashing (PBKDF2), CSRF protection, session management with 1-week expiry, authentication guards on all protected views, input validation via Django forms, XSS prevention via template auto-escaping, and clickjacking protection via X-Frame-Options.

4. **PDF Generation:** Integration with xhtml2pdf for server-side PDF rendering, producing professional A4-formatted resumes from user data.

5. **Bug Discovery and Resolution:** 15 bugs identified through systematic testing, all of which have been fixed. Each bug is documented with clear reproduction steps and resolution details.

### Lessons Learned

- **Testing early and often** catches integration issues before they compound. The cross-module tests revealed that the templates_app was fundamentally broken (missing templates) despite individual views being correctly coded.
- **Dependency management** is critical — the missing xhtml2pdf package blocked all test execution, highlighting the importance of `requirements.txt` accuracy.
- **Documentation drift** occurs when code changes outpace documentation updates (WeasyPrint → xhtml2pdf switch).
- **Template rendering** in Django requires all referenced templates to exist, even for views that are functionally correct.

### Future Enhancements

1. Email-based password reset functionality
2. Social authentication (Google, GitHub)
3. Resume versioning (save snapshots)
4. Cover letter generation
5. ATS (Applicant Tracking System) compatibility checker
6. JavaScript testing with Selenium/Playwright
7. Load and stress testing
8. Mobile app (React Native / Flutter)
9. REST API for third-party integrations
