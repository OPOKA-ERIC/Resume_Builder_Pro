# Resume Builder Pro — Final Report

**Group C, BSE2301**  
**Course:** Web Development Projects (Django & Flask)  
**Year:** 2026

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Visuals — Key Screenshots](#2-visuals--key-screenshots)
3. [System Documentation](#3-system-documentation)
   - 3.1 [System Architecture](#31-system-architecture)
   - 3.2 [Technology Stack](#32-technology-stack)
   - 3.3 [Project Structure](#33-project-structure)
   - 3.4 [Database Schema](#34-database-schema)
   - 3.5 [URL Routing](#35-url-routing)
   - 3.6 [Key Features Walkthrough](#36-key-features-walkthrough)
   - 3.7 [Setup & Installation](#37-setup--installation)
4. [Source Code](#4-source-code)

---

## 1. Introduction

Resume Builder Pro is a full-stack web application developed by Group C (BSE2301) that enables users to create, customise, and download professional resumes in minutes. The application provides a step-by-step wizard for entering personal details, education, work experience, skills, projects, certifications, languages, and references. Users can choose from 27 professionally designed PDF templates and generate print-ready resumes with one click.

The system addresses a common problem faced by students and early-career professionals: creating a polished, ATS-optimised resume without design skills or expensive software. Resume Builder Pro is entirely free, with no premium tiers or hidden charges.

### Key Capabilities

- **Multi-step wizard** — guided data entry across 7 sections
- **27 PDF templates** — diverse visual styles (Classic, Modern, Compact, Corporate, Creative, and more)
- **32 theme skins** — additional visual customisation with colour palettes
- **Instant PDF export** — server-side rendering via xhtml2pdf
- **User authentication** — registration, login, password management, profile editing
- **Dashboard** — manage all saved resumes with edit/preview/delete actions
- **Responsive design** — works on desktop, tablet, and mobile (Bootstrap 5)

---

## 2. Visuals — Key Screenshots

*Screenshots should be placed at the locations indicated below. Each image is referenced with a suggested filename.*

### 2.1 Landing Page — Hero & Features

> **Suggested screenshot:** `screenshots/01_landing.png`  
> *Place here.*  
> Captures the hero section with the typewriter effect, CTA buttons, stats counters, feature cards ("Why Resume Builder Pro?"), "How It Works" steps, testimonials, and the final CTA.

### 2.2 Registration / Login

> **Suggested screenshot:** `screenshots/02_register.png`  
> *Place here.*  
> Shows the registration card with username, email, password fields, and the gradient header.

> **Suggested screenshot:** `screenshots/03_login.png`  
> *Place here.*  
> Shows the login form with email/username and password fields.

### 2.3 Dashboard

> **Suggested screenshot:** `screenshots/04_dashboard.png`  
> *Place here.*  
> Shows the "My Resumes" dashboard with stat cards (total resumes, templates, exports, availability), resume cards with Edit/Preview/Delete buttons, and the "Create New" button.

### 2.4 Wizard — Step Example

> **Suggested screenshot:** `screenshots/05_wizard.png`  
> *Place here.*  
> Shows the wizard step indicator (progress bar with numbered circles), the "Experience" form with company, role, start/end year, description fields, and existing items list with edit/delete options.

### 2.5 Template Selection Gallery

> **Suggested screenshot:** `screenshots/06_templates.png`  
> *Place here.*  
> Shows the grid of available templates with thumbnail images, names, descriptions, and "Use Template" buttons.

### 2.6 Resume Preview & Section Editing

> **Suggested screenshot:** `screenshots/07_preview.png`  
> *Place here.*  
> Shows the full-page rendered resume preview in an iframe, plus the "Edit Sections" area below with expandable cards for each section.

### 2.7 PDF Output Sample

> **Suggested screenshot:** `screenshots/08_pdf.png`  
> *Place here.*  
> Shows one of the generated PDF templates (e.g., Classic or Modern) rendered as a document.

### 2.8 Mobile Responsive View

> **Suggested screenshot:** `screenshots/09_mobile.png`  
> *Place here.*  
> Shows the landing page or wizard at 375px width (Chrome DevTools mobile view) to demonstrate responsive behaviour.

---

## 3. System Documentation

### 3.1 System Architecture

The application follows Django's standard **Model-View-Template (MVT)** architectural pattern:

```
┌─────────────────────────────────────────────────────────────┐
│                         Browser                              │
└──────────────────┬──────────────────────────────────────────┘
                   │  HTTP Request / Response
┌──────────────────▼──────────────────────────────────────────┐
│                     Django Server                             │
│                                                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │   urls.py    │──│   views.py  │──│   models.py          │ │
│  │  (routing)   │  │  (business  │  │   (database schema)  │ │
│  │              │  │   logic)    │  │                      │ │
│  └─────────────┘  └──────┬──────┘  └─────────────────────┘ │
│                          │                                   │
│  ┌───────────────────────▼────────────────────────────────┐ │
│  │                    Templates (UI)                        │ │
│  │  base.html ← landing.html, dashboard.html, wizard_*.html│ │
│  │  pdf/template_*.html (27 print templates)                │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                               │
│  ┌─────────────┐  ┌─────────────┐                             │
│  │  Static     │  │  Media      │                             │
│  │  CSS / JS   │  │  Uploads    │                             │
│  └─────────────┘  └─────────────┘                             │
└───────────────────────────────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────────┐
│                    SQLite Database                            │
│   User ←── Resume ──→ Education, Experience, Skill,          │
│   Project, Certification, Language, Reference                │
│   Resume ──→ ResumeTemplate                                 │
└──────────────────────────────────────────────────────────────┘
```

**Data flow summary:**

1. User visits a URL → `urls.py` routes to the appropriate view
2. View fetches/updates data from models → `views.py` processes the request
3. View renders a template with context → `template.html` generates HTML
4. Static assets (CSS, JS) enhance the UI in the browser
5. PDF generation bypasses the template layer — xhtml2pdf renders `template_*.html` directly to a PDF document

### 3.2 Technology Stack

| Layer | Technology | Version |
|---|---|---|
| **Backend Framework** | Django (Python) | 6.0.6 |
| **Database** | SQLite3 | Built-in |
| **Frontend** | Bootstrap 5.3 | CDN |
| **Icons** | Bootstrap Icons 1.10 | CDN |
| **Fonts** | Google Fonts (Inter, Plus Jakarta Sans) | CDN |
| **PDF Generation** | xhtml2pdf | Latest |
| **Image Processing** | Pillow | Latest |
| **Static File Serving** | WhiteNoise | Latest |
| **Deployment** | Gunicorn + WhiteNoise | — |

### 3.3 Project Structure

```
Resume_Builder_Pro/
│
├── manage.py                          # Django CLI entry point
├── requirements.txt                   # Python dependencies
├── .gitignore
├── README.md
│
├── resume_builder_pro/                # Project configuration
│   ├── settings.py                    # All Django settings
│   ├── urls.py                        # Root URL routing
│   ├── wsgi.py                        # WSGI entry point
│   └── asgi.py                        # ASGI entry point
│
├── accounts/                          # Auth & user profiles app
│   ├── models.py                      # UserProfile model
│   ├── forms.py                       # RegistrationForm, ProfileForm
│   ├── views.py                       # Register, Login, Profile views
│   └── urls.py                        # Auth URL patterns
│
├── resumes/                           # Core resume management app
│   ├── models.py                      # Resume, Education, Experience,
│   │                                  # Skill, Project, Certification,
│   │                                  # Language, Reference
│   ├── forms.py                       # All 7 section forms with validation
│   ├── views.py                       # Dashboard, Wizard, Preview, Edit,
│   │                                  # Delete, Template Select
│   └── urls.py                        # ~20 URL patterns
│
├── templates_app/                     # Template gallery app
│   ├── models.py                      # ResumeTemplate model
│   ├── views.py                       # Gallery, Preview views
│   └── urls.py                        # Template URL patterns
│
├── pdf_export/                        # PDF generation app
│   ├── views.py                       # Download PDF view
│   └── urls.py                        # PDF URL patterns
│
├── static/
│   ├── css/
│   │   ├── style.css                  # Complete design system (~1696 lines)
│   │   └── themes/themes.css          # Theme colour customisation
│   └── js/
│       ├── main.js                    # Typewriter, counters, scroll animations,
│       │                              # form validation, unsaved changes warning
│       └── wizard.js                  # Wizard-specific required-field validation
│
├── templates/
│   ├── base.html                      # Shared layout (navbar, footer, messages)
│   ├── landing.html                   # Homepage (hero, stats, features, CTA)
│   ├── accounts/                      # Login, Register, Password Reset, Profile
│   ├── resumes/                       # Dashboard, Wizard Step, Preview, Template
│   │   └── themes/                    # Select, Delete Confirmations, Edit Forms
│   │       ├── skins/                 # 32 colour/typography skins
│   │       └── archetypes/            # 6 layout archetypes
│   ├── pdf/                           # 27 print-ready PDF templates
│   └── snippets/                      # template_preview_card.html
│
└── media/                             # User uploads (profile photos)
```

### 3.4 Database Schema

The database consists of 9 models across 4 Django apps:

```
accounts_UserProfile
├── user (FK → auth.User)
├── phone (CharField)
├── address (TextField)
└── photo (ImageField)

resumes_Resume
├── user (FK → auth.User)
├── title (CharField)
├── template (FK → ResumeTemplate, nullable)
├── created_at (DateTimeField)
└── updated_at (DateTimeField)
     │
     ├── resumes_Education
     │   ├── institution, qualification
     │   ├── start_year, end_year
     │   └── description
     │
     ├── resumes_Experience
     │   ├── company, role
     │   ├── start_year, end_year
     │   └── description
     │
     ├── resumes_Skill
     │   ├── name
     │   └── proficiency_level (beginner/intermediate/advanced/expert)
     │
     ├── resumes_Project
     │   ├── name, description
     │   └── link (URL)
     │
     ├── resumes_Certification
     │   ├── title, issuer
     │   └── year_awarded
     │
     ├── resumes_Language
     │   ├── name
     │   └── proficiency_level (basic/conversational/fluent/native)
     │
     └── resumes_Reference
         ├── name, relationship
         └── contact

templates_app_ResumeTemplate
├── name, description
├── preview_image
├── html_file (legacy template path)
├── is_active
├── archetype (A-F)
├── skin_file (new theming path)
├── tags, swatches (JSON)
├── supports_photo, supports_monochrome
└── ats_safe
```

### 3.5 URL Routing

| URL Pattern | View Name | Description |
|---|---|---|
| `/` | `landing` | Landing page |
| `/admin/` | — | Django admin |
| `/accounts/register/` | `register` | User registration |
| `/accounts/login/` | `login` | Login |
| `/accounts/logout/` | `logout` | Logout |
| `/accounts/profile/` | `profile` | Edit profile |
| `/accounts/password-change/` | `password_change` | Change password |
| `/accounts/password-reset/` | `password_reset` | Reset password |
| `/resumes/` | `dashboard` | Resume dashboard |
| `/resumes/create/` | `resume_create` | Create new resume |
| `/resumes/create-from-template/<id>/` | `create_from_template` | Create from template |
| `/resumes/<id>/wizard/<step>/` | `wizard_step` | Wizard step |
| `/resumes/<id>/wizard/<step>/<entry_id>/edit/` | `wizard_entry_edit` | Edit wizard entry |
| `/resumes/<id>/wizard/<step>/<entry_id>/delete/` | `wizard_entry_delete` | Delete wizard entry |
| `/resumes/<id>/templates/` | `template_select` | Choose template |
| `/resumes/<id>/preview/` | `resume_preview` | Resume preview |
| `/resumes/<id>/preview/frame/` | `resume_preview_frame` | Preview iframe src |
| `/templates/` | `gallery` | Template gallery |
| `/templates/<id>/preview/` | `preview` | Template detail |
| `/templates/<id>/frame/` | `preview_frame` | Template preview iframe |
| `/pdf/download/<id>/` | `download_pdf` | Download PDF |

### 3.6 Key Features Walkthrough

#### Landing Page

The landing page (`templates/landing.html`, extending `base.html`) is the public-facing home. It features:

- **Hero section** with gradient background, typewriter effect (`main.js` lines 82–126 cycles through "Minutes.", "No Design Skills Needed.", "For Free.", "Like a Pro."), and two CTA buttons (Get Started Free + Browse Templates)
- **CSS-only resume mockup** in the right column (visible on desktop) — pure divs and dots, no images, with floating badges ("ATS Optimized", "Professional")
- **Stats counter** (`main.js` lines 129–152) uses `IntersectionObserver` + `setInterval` to animate numbers from 0 to their target when scrolled into view (1,000 resumes, 3 templates, 7 steps, 100% free)
- **Feature cards**, "How It Works" steps, testimonials, and a bottom CTA — all animated with staggered `animate-fade-in-up` delays

#### User Authentication

The `accounts` app handles all auth with Django's built-in system:

- **Registration** (`accounts/forms.py` `RegistrationForm`): validates unique username, unique email, strong password (min 8 chars, not common, not similar to user info). On save, creates both `User` and `UserProfile`.
- **Login/Logout**: standard Django auth views with Bootstrap-styled templates
- **Profile editing** (`ProfileForm`): updates both `User` (email, first/last name) and `UserProfile` (phone, address, photo)
- **Password change/reset**: Django's built-in views, custom-styled with `CustomPasswordChangeForm`

#### Resume Dashboard

The dashboard (`templates/resumes/dashboard.html`) loads at `/resumes/`.

- **Stat cards** show totals (Total Resumes, Templates, Exports, Availability)
- **Resume cards** display title, template name, last-updated date, and action buttons: Edit, Preview, Delete
- **Pagination** (Django `Paginator`, 9 per page) with Bootstrap pagination UI
- **Empty state** with CTA when user has zero resumes
- **Create New button** calls `/resumes/create/` which creates a blank `Resume` record and redirects to the wizard's first step

#### Multi-Step Wizard

The wizard (`resumes/views.py` `wizard_step`) uses a single template (`templates/resumes/wizard_step.html`) with branching logic:

- **Progress indicator** — 7 numbered circles (completed = green checkmark, active = highlighted, upcoming = grey) connected by a coloured bar whose width is calculated via `{% widthratio step_index steps|length|add:'-1' 100 %}`
- **Existing items list** — shows previously saved entries with inline Edit/Delete buttons
- **Form rendering** — loops over Django form fields dynamically; supports 7 different forms (Education, Experience, Skill, Project, Certification, Language, Reference)
- **Navigation** — "Add Another" (stays on same step), "Save & Next" (advances), "Back", "Save & Exit"
- **JavaScript validation** (`wizard.js`): checks `[required]` fields on submit, adds `is-invalid` class to empty fields, focuses the first invalid field, shows a Bootstrap Toast notification
- **Unsaved changes warning** (`main.js` lines 181–192): `beforeunload` event fires if any form field changed

#### Template Selection

After completing all wizard steps, users choose a template (`templates/resumes/template_select.html`):

- 4-column responsive grid of template cards
- Each card has a thumbnail (via `snippets/template_preview_card.html`), name, description, and "Use Template" button
- The currently selected template shows a green "Currently Selected" banner
- Selection submits via POST to `resumes:template_select` view, which sets `resume.template` and redirects to preview

#### Resume Preview

The preview page (`templates/resumes/preview.html`) at `/resumes/<id>/preview/`:

- **Action bar** with Download PDF, Change Template, Dashboard buttons
- **Rendered resume** in an iframe (src = `/resumes/<id>/preview/frame/`) — the `resume_preview_frame` view renders the chosen template's HTML with the resume data
- **Edit Sections** area — expandable cards for each section with inline Edit (link to `section_edit` view) and Delete (inline POST form with JS confirm dialog) actions

#### PDF Generation

The `pdf_export` app handles PDF creation via xhtml2pdf:

- Renders the selected `template_*.html` (e.g., `template_classic.html`, `template_modern.html`, `template_compact.html`) with resume context data
- Uses print-safe CSS — `@page { size: A4; margin: 20mm 18mm; }`, `page-break-inside: avoid` on entry blocks, fixed units (`pt`, `mm`, `in`)
- 27 distinct templates plus 32 theme skins for visual diversity
- The view returns an `HttpResponse` with `content_type='application/pdf'` and `Content-Disposition: attachment`

#### Client-Side JavaScript

`static/js/main.js` (218 lines) provides interactive features:

| Feature | Lines | Mechanism |
|---|---|---|
| Auto-dismiss alerts | 5–12 | `bootstrap.Alert.close()` after 5s |
| Back to Top | 14–27 | Scroll listener → toggle `.visible` class |
| Navbar scroll effect | 29–39 | Adds `.scrolled` class on scroll > 50px |
| Form field focus | 41–50 | Adds `.field-focused` on parent on focus |
| Smooth scroll anchors | 52–61 | `scrollIntoView({ behavior: 'smooth' })` |
| Scroll animations (IO) | 63–79 | `IntersectionObserver` unpauses CSS animations |
| Typewriter | 82–126 | `setInterval` typing/deleting 4 phrases |
| Counter animation | 129–152 | `setInterval` counting + IO observer |
| Wizard validation | 155–178 | Required field check + `is-invalid` toggle |
| Unsaved changes | 181–192 | `beforeunload` listener on form change |
| Progress bar animation | 195–202 | Reset width to 0, animate to target |

`static/js/wizard.js` (30 lines) adds wizard-specific validation with `form[data-wizard-step]` scoping, focus-to-first-invalid, and Bootstrap Toast feedback.

#### Responsive Design

All pages use Bootstrap 5's responsive grid system (`col-6 col-md-4 col-lg-3` pattern). Custom CSS adds `clamp()` for fluid font sizing on headings and body text. The responsive media queries at breakpoints 768px and 576px adjust:

- Padding and font sizes on hero, stats, feature cards, testimonials, CTA
- Stack buttons vertically on mobile
- Hide decorative pseudo-elements on very small screens
- Adjust wizard step indicator spacing

#### Security Configuration

`sessions.py` defines production-ready settings:

- `SESSION_COOKIE_AGE`: 7 days
- `SESSION_COOKIE_HTTPONLY`: True (no JS access to session cookie)
- `SESSION_COOKIE_SAMESITE`: 'Lax'
- `CSRF_COOKIE_HTTPONLY`, `CSRF_COOKIE_SAMESITE`: set
- `X_FRAME_OPTIONS`: 'DENY' (except `resume_preview_frame` which uses `@xframe_options_sameorigin`)
- Production mode: `SECURE_SSL_REDIRECT`, `HSTS`, secure cookies enabled
- Password validation: min 8 chars, common-password check, numeric-password check

### 3.7 Setup & Installation

#### Prerequisites

- Python 3.10+
- pip (Python package manager)
- Git

#### Installation Steps

```bash
# 1. Clone the repository
git clone https://github.com/OPOKA-ERIC/Resume_Builder_Pro.git
cd Resume_Builder_Pro

# 2. Create and activate virtual environment
python -m venv venv
source venv/bin/activate          # Linux/Mac
# venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run database migrations
python manage.py migrate

# 5. Load template data (required — gallery will be empty without this)
python manage.py loaddata initial_templates

# 6. Create admin user (optional)
python manage.py createsuperuser

# 7. Collect static files for production
python manage.py collectstatic --noinput

# 8. Start development server
python manage.py runserver
```

The application will be accessible at `http://127.0.0.1:8000/`.

#### Environment Variables

| Variable | Default | Description |
|---|---|---|
| `DJANGO_SECRET_KEY` | Dev fallback key | Secret key for Django |
| `DJANGO_DEBUG` | `True` | Debug mode toggle |
| `DJANGO_ALLOWED_HOSTS` | `localhost,127.0.0.1` | Production hostnames |

---

## 4. Source Code

The complete source code is hosted on GitHub:

**Repository URL:** [https://github.com/OPOKA-ERIC/Resume_Builder_Pro](https://github.com/OPOKA-ERIC/Resume_Builder_Pro)

### Repository Contents

| Directory | Purpose |
|---|---|
| `accounts/` | User authentication and profile management |
| `resumes/` | Core resume CRUD, wizard, preview, sections |
| `templates_app/` | Resume template gallery and preview |
| `pdf_export/` | PDF generation with xhtml2pdf |
| `resume_builder_pro/` | Project settings, URLs, WSGI/ASGI config |
| `templates/` | All HTML templates (base, landing, auth, resume, PDF) |
| `static/` | CSS, JavaScript, and theme files |
| `media/` | User-uploaded profile photos |
| `requirements.txt` | Python package dependencies |
| `README.md` | Setup instructions |

---

*End of Report — Resume Builder Pro, Group C, BSE2301*
