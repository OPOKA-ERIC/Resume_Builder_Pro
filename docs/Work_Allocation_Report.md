# Resume Builder Pro — Work Allocation & Contribution Report

**Project:** Resume Builder Pro (Django Web Application)
**Group:** C — BSE2301
**Date:** July 22, 2026
**Prepared for:** Project Supervisor

---

## 1. Team Composition & Role Assignments

| # | Team Member | Role | Core Domain |
|---|-------------|------|-------------|
| 1 | **Opeto Isaac** | Authentication & PDF Generation Lead | User accounts, security, PDF export |
| 2 | **Auma Dilish** | Testing, Documentation & Deployment Lead | Testing, bug tracking, docs, GitHub, deployment |
| 3 | **[Member 3]** | Resume Management & Wizard Lead | Resume CRUD, 7-step wizard, data models |
| 4 | **[Member 4]** | Template Design & Frontend Lead | UI/UX templates, HTML/CSS/JS, static assets |

---

## 2. Deliverables per Team Member

### 2.1 Opeto Isaac — Authentication & PDF Generation Lead

**Files Owned:** 22 files (~980 lines of code)

| Deliverable | Files | Description |
|-------------|-------|-------------|
| **User Registration** | `accounts/forms.py`, `accounts/views.py`, `templates/accounts/register.html` | Custom `RegistrationForm` with username regex, duplicate email/username validation, password strength enforcement. View secured with `@csrf_protect`, `@never_cache`, `@require_http_methods`. |
| **Login/Logout** | `accounts/views.py`, `templates/accounts/login.html` | Session-based auth with 7-day expiry, failed login logging, `AuthenticationForm` integration. |
| **Profile Management** | `accounts/models.py`, `accounts/views.py`, `templates/accounts/profile.html` | `UserProfile` model (OneToOne to User), `ProfileForm` with email uniqueness, phone format validation, profile photo upload. |
| **Password Change** | `accounts/views.py`, `accounts/forms.py`, `templates/accounts/password_change.html` | `CustomPasswordChangeForm` with Bootstrap widgets, `update_session_auth_hash()` to maintain session after password change. |
| **PDF Generation** | `pdf_export/views.py`, `templates/pdf/resume_pdf.html` | `generate_pdf_html()` renders resume to HTML, `render_to_pdf()` converts via xhtml2pdf `pisa.CreatePDF`. A4 page formatting with inline CSS. |
| **PDF Download & Preview** | `pdf_export/views.py`, `templates/pdf/pdf_preview.html` | Authenticated download with `Content-Disposition` header, iframe-based browser preview, owner-only access via `get_object_or_404(Resume, user=request.user)`. |
| **Security Configuration** | `resume_builder_pro/settings.py` | Password validators (4 configured), session security (HTTP-only, SameSite=Lax), CSRF protection, `X_FRAME_OPTIONS=DENY`, `SECURE_CONTENT_TYPE_NOSNIFF`, HSTS settings for production. |
| **Logging** | `resume_builder_pro/settings.py`, `accounts/views.py`, `pdf_export/views.py` | Structured logging for `accounts` and `pdf_export` modules — login attempts, registrations, PDF generation events. |

**Key Technical Contributions:**
- Designed the `UserProfile` model extending Django's built-in User
- Implemented 5 decorator-secured views (`@csrf_protect`, `@never_cache`, `@require_http_methods`, `@login_required`)
- Integrated xhtml2pdf for server-side PDF rendering with error handling
- Configured 4 AUTH_PASSWORD_VALIDATORS for security compliance

---

### 2.2 Auma Dilish — Testing, Documentation & Deployment Lead

**Files Owned:** 13 files (~2,555 lines of documentation and test code)

| Deliverable | Files | Description |
|-------------|-------|-------------|
| **Unit Tests — templates_app** | `templates_app/tests.py` (166 lines) | 21 tests: model creation/str/defaults/ordering (8), gallery view active/inactive filtering (7), preview view auth/404/inactive (6). |
| **Integration Tests** | `resumes/integration_tests.py` (336 lines) | 20 end-to-end tests: full registration→wizard→PDF journey, profile update persistence, password change with re-login, cross-user authorization (7 tests), dashboard state transitions, PDF generation with all sections, template selection flow. |
| **Bug Tracking Report** | `docs/Bug_Tracking_Report.md` | 15 bugs identified: 9 fixed (3 critical, 4 major, 2 minor), 6 open (documented with reproduction steps). |
| **Chapter 7: Testing** | `docs/Chapter_7_Testing.md` (832 lines) | Complete testing strategy: unit testing (85 tests across 4 modules), integration testing (20 tests), manual testing, test results summary, coverage analysis. |
| **Chapter 10: Deployment** | `docs/Chapter_10_Deployment_Strategy.md` | Updated to reflect actual stack (xhtml2pdf, WhiteNoise, environment-based DEBUG/ALLOWED_HOSTS). |
| **User Manual** | `docs/User_Manual.md` (299 lines) | End-user guide: registration, profile, 7-step wizard walkthrough, template selection, PDF download, troubleshooting FAQ. |
| **Appendices** | `docs/Appendices.md` (352 lines) | Architecture diagrams, database schema, URL route reference, test case catalog (all 105 tests), tech stack, final reflections. |
| **Bug Fixes** | `settings.py`, `templates_app/views.py`, `accounts/views.py` | Fixed WhiteNoise middleware, DEBUG/ALLOWED_HOSTS from env vars, template_preview 404 handling, unused import removal. |
| **Missing Templates** | `templates/templates_app/gallery.html`, `templates/templates_app/preview.html` | Created previously missing templates that caused runtime TemplateDoesNotExist errors. |
| **GitHub Management** | Git commits, push to origin | Committed all changes, managed branch, verified repo integrity. |

**Key Technical Contributions:**
- Wrote 41 new tests (21 unit + 20 integration), bringing total from 84 to 105
- Identified and fixed 9 bugs (3 critical, 4 major, 2 minor)
- Produced ~2,500 lines of formal project documentation
- Ensured 100% test pass rate across the entire test suite

---

### 2.3 [Member 3] — Resume Management & Wizard Lead

**Files Owned:** 15 files (~653 lines of code)

| Deliverable | Files | Description |
|-------------|-------|-------------|
| **Resume Model** | `resumes/models.py` | `Resume` model with user FK, title, template FK (nullable), timestamps. Ordering by `-updated_at`. |
| **Section Models (7)** | `resumes/models.py` | `Education`, `Experience`, `Skill`, `Project`, `Certification`, `Language`, `Reference` — each with FK to Resume, CASCADE deletion, appropriate field types and choices. |
| **Resume Forms (8)** | `resumes/forms.py` | `ResumeForm` + 7 section-specific `ModelForm`s with Bootstrap widgets, date inputs (`type="date"`), textarea rows, select dropdowns for proficiency levels. |
| **Dashboard View** | `resumes/views.py`, `templates/resumes/dashboard.html` | Grid of resume cards with edit/preview/delete actions, empty state with CTA, login-required. |
| **Resume Create** | `resumes/views.py`, `templates/resumes/resume_form.html` | Title-only creation form, auto-redirects to wizard step 1. |
| **7-Step Wizard** | `resumes/views.py`, `templates/resumes/wizard_step.html` | Dynamic form rendering per step, progress bar, existing items display, auto-advance to next step, prevents cross-user access. |
| **Resume Edit** | `resumes/views.py`, `templates/resumes/resume_form.html` | Title editing with `ResumeForm` instance, success message. |
| **Resume Delete** | `resumes/views.py`, `templates/resumes/resume_confirm_delete.html` | Confirmation page with POST-to-delete pattern, success message. |
| **Resume Preview** | `resumes/views.py`, `templates/resumes/preview.html` | Full resume rendering with all 7 sections, owner-only access. |
| **Template Selection** | `resumes/views.py`, `templates/resumes/template_select.html` | Active template grid after wizard completion. |
| **Admin Configuration** | `resumes/admin.py` | `ResumeAdmin` with 7 `TabularInline` editors for all section models. |

**Key Technical Contributions:**
- Designed the 8-model data schema supporting 7 resume sections
- Built the 7-step wizard with dynamic form routing and progress tracking
- Implemented owner-only authorization on all views via `get_object_or_404(Resume, user=request.user)`
- Configured Django admin with inline editors for efficient data management

---

### 2.4 [Member 4] — Template Design & Frontend Lead

**Files Owned:** 14 files (~384 lines of code)

| Deliverable | Files | Description |
|-------------|-------|-------------|
| **Base Layout** | `templates/base.html` | Responsive navbar (adaptive auth links), Bootstrap 5.3.0 CDN, Bootstrap Icons, flash messages with auto-dismiss, footer. |
| **Landing Page** | `templates/landing.html` | Hero section with CTA buttons, 3 feature cards (wizard, templates, PDF). |
| **Global Stylesheet** | `static/css/style.css` | Card hover effects, progress bar transitions, form focus states, footer styling. |
| **JavaScript** | `static/js/main.js` | Auto-dismiss Bootstrap alerts after 5 seconds. |
| **Resume Templates (6)** | `templates/resumes/*.html` | Dashboard, wizard step, resume form, preview, template select, delete confirmation — all extending base.html with consistent Bootstrap 5 styling. |
| **Template App Model** | `templates_app/models.py` | `ResumeTemplate` with name, description, preview_image, html_file, is_active, ordering. |
| **Template App Views** | `templates_app/views.py` | Public gallery (active templates only), authenticated preview. |
| **Template App URLs** | `templates_app/urls.py` | Gallery at `/templates/`, preview at `/templates/<id>/preview/`. |
| **Admin** | `templates_app/admin.py` | `ResumeTemplateAdmin` with list_display, list_filter, search_fields. |

**Key Technical Contributions:**
- Designed the responsive UI framework using Bootstrap 5.3.0
- Created 16 HTML templates with consistent styling and navigation
- Implemented adaptive navbar (different links for authenticated vs anonymous users)
- Built the template gallery system for resume styling options

---

## 3. Contribution Summary

### 3.1 By the Numbers

| Metric | Opeto Isaac | Auma Dilish | [Member 3] | [Member 4] |
|--------|-------------|-------------|-------------|-------------|
| **Files Owned** | 22 | 13 | 15 | 14 |
| **Lines of Code** | ~980 | ~2,555 | ~653 | ~384 |
| **Git Commits** | 1 | 1 | — | — |
| **Test Cases** | — | 41 new (105 total) | — | — |
| **Bugs Fixed** | — | 9 (3 critical) | — | — |
| **Documentation Pages** | 1 | 5 | — | — |
| **Templates Created** | 6 | 2 | 6 | 10 |

### 3.2 Percentage Contribution by Domain

| Domain | Opeto Isaac | Auma Dilish | [Member 3] | [Member 4] |
|--------|-------------|-------------|-------------|-------------|
| Authentication (accounts) | **85%** | 10% | — | 5% |
| Resume Management (resumes) | — | — | **90%** | 10% |
| PDF Generation (pdf_export) | **90%** | 10% | — | — |
| Template System (templates_app) | — | 15% | — | **85%** |
| Frontend / UI | 10% | — | — | **90%** |
| Testing | 15% | **80%** | 5% | — |
| Documentation | 10% | **85%** | — | 5% |
| Deployment & DevOps | 20% | **75%** | — | 5% |
| Security Configuration | **70%** | 30% | — | — |

---

## 4. Technical Architecture Overview

```
┌──────────────────────────────────────────────────────────┐
│                    CLIENT BROWSER                         │
│              Bootstrap 5.3.0 + Custom CSS/JS              │
└─────────────────────────┬────────────────────────────────┘
                          │ HTTPS
                          ▼
┌──────────────────────────────────────────────────────────┐
│                   DJANGO 6.0.6                            │
│                                                           │
│  ┌──────────┐  ┌──────────┐  ┌────────────┐  ┌────────┐ │
│  │ accounts  │  │ resumes  │  │templates_app│  │pdf_exp │ │
│  │  (Isaac)  │  │(Member3) │  │ (Member4)  │  │(Isaac) │ │
│  └─────┬─────┘  └────┬─────┘  └─────┬──────┘  └───┬────┘ │
│        └──────────────┴──────────────┴─────────────┘       │
│                           │                                │
│                    Django ORM + Security                    │
│        (CSRF, Session mgmt, Password hashing)             │
└───────────────────────────┼────────────────────────────────┘
                            │
              ┌─────────────┼──────────────┐
              │             │              │
              ▼             ▼              ▼
        ┌──────────┐  ┌──────────┐  ┌──────────────┐
        │ SQLite3  │  │ WhiteNoise│  │  xhtml2pdf   │
        │   Dev    │  │  Static  │  │  PDF Engine  │
        └──────────┘  └──────────┘  └──────────────┘
```

---

## 5. Testing Evidence

| Test Suite | Module | Tests | Owner | Status |
|-----------|--------|-------|-------|--------|
| `accounts/tests.py` | Authentication | 31 | Auma Dilish (tests) / Opeto Isaac (domain) | All Pass |
| `resumes/tests.py` | Resume Management | 34 | Auma Dilish (tests) / [Member 3] (domain) | All Pass |
| `pdf_export/tests.py` | PDF Generation | 9 | Auma Dilish (tests) / Opeto Isaac (domain) | All Pass |
| `templates_app/tests.py` | Template System | 21 | Auma Dilish | All Pass |
| `resumes/integration_tests.py` | Cross-Module | 20 | Auma Dilish | All Pass |
| **Total** | | **105** | | **100% Pass** |

### Test Categories Covered

- **Unit Tests (85):** Individual model creation, form validation, view responses, authorization checks
- **Integration Tests (20):** End-to-end workflows spanning multiple modules
- **Manual Tests:** Browser-based UI verification for responsive design, form submissions, PDF downloads

---

## 6. Bug Discovery & Resolution

| Severity | Found | Fixed | Open |
|----------|-------|-------|------|
| Critical | 3 | 3 | 0 |
| Major | 5 | 4 | 1 |
| Minor | 7 | 2 | 5 |
| **Total** | **15** | **9** | **6** |

**Critical Bugs Fixed:**
1. Missing xhtml2pdf dependency blocking all tests
2. Missing templates_app templates causing runtime errors
3. WhiteNoise middleware not configured for production

**Open Bugs (Documented):**
- Template selection not persisted (BUG-011)
- Wizard back navigation (BUG-012)
- No edit/delete for wizard entries (BUG-013)
- Resume edit limited to title (BUG-014)
- Login template form rendering (BUG-015)
- Documentation WeasyPrint references (BUG-010)

---

## 7. Documentation Produced

| Document | Pages (est.) | Author | Content |
|----------|-------------|--------|---------|
| Chapter 2: Non-Functional Requirements | ~5 | Opeto Isaac | Security, Usability, Performance, Portability, Maintainability, Availability |
| Chapter 7: Testing | ~15 | Auma Dilish | Strategy, unit/integration/manual testing, results, bug tracking, coverage |
| Chapter 10: Deployment Strategy | ~6 | Opeto Isaac + Auma Dilish | Architecture, Docker, Render deployment, security checklist |
| Bug Tracking Report | ~8 | Auma Dilish | 15-bug registry with severity, reproduction, resolution |
| User Manual | ~12 | Auma Dilish | Registration, wizard walkthrough, PDF download, FAQ |
| Appendices | ~14 | Auma Dilish | Architecture, schema, URL reference, test catalog, tech stack |

---

## 8. Evidence of Collaboration

The project demonstrates genuine team collaboration through:

1. **Shared Code Ownership:** 15 files were modified by 2+ team members
2. **Scaffold → Enhancement Pattern:** OPOKA-ERIC scaffolded the initial codebase; team members enhanced their respective domains
3. **Cross-Module Integration:** Auth (Isaac) → Resumes (Member 3) → PDF (Isaac) → Testing (Auma) required coordination
4. **Bug Discovery Loop:** Testing (Auma) found bugs → Fixes applied across modules (Isaac, Auma)
5. **Documentation Pipeline:** Code (all) → Tests (Auma) → Docs (Auma + Isaac) → Deployment (Auma)

---

*This report documents the complete contribution of each team member to the Resume Builder Pro project. All claims are verifiable through the Git commit history at `https://github.com/OPOKA-ERIC/Resume_Builder_Pro.git`.*
