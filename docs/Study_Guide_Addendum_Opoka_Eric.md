# Study Guide Addendum — Opoka Eric (Backend & Database Lead)

## New Changes & Missing Details (Post-Merge)

This addendum covers what the original study guide omits based on the actual project code after pulling from `origin/main`.

---

## 1. Project Setup — Additional Details

### Django Version & Python
- **Django 6.0.6** (not 5.x as the SDD says)
- **Python 3.14** (development); Docker uses `python:3.12-slim`

### Settings Configuration (`resume_builder_pro/settings.py`)
The study guide covers basic settings. These are also configured and relevant to your role:

```python
# Static file serving for production
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

# Logout redirect
LOGOUT_REDIRECT_URL = 'accounts:login'

# Session security
SESSION_COOKIE_AGE = 60 * 60 * 24 * 7   # 1 week
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

# CSRF security
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'

# Clickjacking protection
X_FRAME_OPTIONS = 'DENY'  # Overridden per-view with @xframe_options_sameorigin for iframes
SECURE_CONTENT_TYPE_NOSNIFF = True

# Production-only security (when DEBUG=False)
if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_SSL_REDIRECT = True

# Logging
LOGGING = {
    'version': 1,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'accounts': {'handlers': ['console'], 'level': 'INFO'},
        'pdf_export': {'handlers': ['console'], 'level': 'INFO'},
    },
}

# Email (console backend for development)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

### Q&A: "How did you handle production security?"
**Answer:** I configured environment-variable-based settings with `os.environ.get()` for `SECRET_KEY`, `DEBUG`, and `ALLOWED_HOSTS`. When `DEBUG=False`, Django enforces HTTPS via `SECURE_SSL_REDIRECT`, sets HSTS headers for one year, enables the browser XSS filter, and makes session/CSRF cookies secure-only. WhiteNoise handles static file serving with compression and caching headers. Logging is configured for both `accounts` and `pdf_export` apps at INFO level.

---

## 2. Models — Corrections & Missing Models

### The study guide says "8 models"
**Actual count: 10 models** across 4 apps. The two missing from the guide:

| Model | App | Fields | Purpose |
|-------|-----|--------|---------|
| `Language` | resumes | resume (FK), name, proficiency_level | Spoken languages with Basic/Conversational/Fluent/Native levels |
| `Reference` | resumes | resume (FK), name, relationship, contact | Professional references |

### All 10 models with their actual file locations:

**accounts/models.py** — 1 model:
1. `UserProfile` — OneToOneField to User

**resumes/models.py** — 8 models:
2. `Resume` — user (FK), title, template (FK→ResumeTemplate), created_at, updated_at
3. `Education` — resume (FK), institution, qualification, start_year, end_year, description
4. `Experience` — resume (FK), company, role, start_year, end_year, description
5. `Skill` — resume (FK), name, proficiency_level (beginner/intermediate/advanced/expert)
6. `Project` — resume (FK), name, description, link
7. `Certification` — resume (FK), title, issuer, year_awarded
8. **`Language`** — resume (FK), name, proficiency_level (basic/conversational/fluent/native)
9. **`Reference`** — resume (FK), name, relationship, contact

**templates_app/models.py** — 1 model:
10. `ResumeTemplate` — name, description, preview_image, html_file, is_active, created_at

### KEY CORRECTION: Year fields are IntegerField, NOT DateField

The original study guide says `start_date`/`end_date` (DateField). The actual project uses **IntegerField**:

| Model | Old DateField | Actual IntegerField |
|-------|--------------|-------------------|
| Education | start_date, end_date | **start_year**, **end_year** |
| Experience | start_date, end_date | **start_year**, **end_year** |
| Certification | date_awarded | **year_awarded** |

**Why?** We only need the year (not the exact date). IntegerField is simpler. `end_year` is nullable to represent "present/ongoing". Validation ensures end_year ≥ start_year.

### Q&A: "What migrations did you run to change from DateField to IntegerField?"
**Answer:** The migration history shows this was a 4-step process:
1. `0001_initial` — Created Resume model with DateFields
2. `0002_add_year_fields` — Added new IntegerFields for years
3. `0003_populate_year_fields` — Data migration to copy year values from DateFields to IntegerFields
4. `0004_remove_old_date_fields` — Removed the old DateField columns

This is a textbook example of a safe schema migration: add columns → populate → remove old.

---

## 3. Admin Panel — Additional Details

### All admin configurations:

**accounts/admin.py:**
```python
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'address']
    search_fields = ['user__username', 'user__email']
```

**resumes/admin.py** — 7 inline classes + 1 ModelAdmin + 7 direct registrations:
```python
# Inline classes for each child model:
class EducationInline(admin.TabularInline):   model = Education,   extra = 0
class ExperienceInline(admin.TabularInline):  model = Experience,  extra = 0
class SkillInline(admin.TabularInline):       model = Skill,       extra = 0
class ProjectInline(admin.TabularInline):     model = Project,     extra = 0
class CertificationInline(admin.TabularInline): model = Certification, extra = 0
class LanguageInline(admin.TabularInline):    model = Language,    extra = 0
class ReferenceInline(admin.TabularInline):   model = Reference,   extra = 0

@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'template', 'created_at', 'updated_at']
    list_filter = ['user', 'template']
    search_fields = ['title', 'user__username']
    inlines = [all 7 inline classes]

# Direct registration for each child model
admin.site.register(Education)
admin.site.register(Experience)
# ... etc for all 7 child models
```

**templates_app/admin.py:**
```python
@admin.register(ResumeTemplate)
class ResumeTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name']
```

---

## 4. Full URL Route Table (Corrected & Complete)

### New/Corrected routes not in the study guide:

| URL | View | Description |
|-----|------|-------------|
| `/resumes/create-from-template/<id>/` | `create_from_template` | Create resume pre-filled with sample data |
| `/resumes/<id>/preview/frame/` | `resume_preview_frame` | Standalone HTML for iframe (with `@xframe_options_sameorigin`) |
| `/resumes/<id>/wizard/<step>/<entry_id>/edit/` | `wizard_entry_edit` | Edit a specific wizard entry |
| `/resumes/<id>/wizard/<step>/<entry_id>/delete/` | `wizard_entry_delete` | Delete a specific wizard entry |
| `/resumes/<id>/<section>/<item_id>/edit/` | `section_edit` | Edit section item from preview page |
| `/resumes/<id>/<section>/<item_id>/delete/` | `section_delete` | Delete section item from preview page |
| `/templates/<id>/frame/` | `template_preview_frame` | Template preview as standalone HTML (no login required, `@xframe_options_sameorigin`) |
| `/pdf/<id>/preview/` | `pdf_preview` | Preview the PDF HTML version |

The study guide also omits the password-reset routes in `accounts/urls.py`:
- `/accounts/password-reset/`
- `/accounts/password-reset/done/`
- `/accounts/password-reset-confirm/<uidb64>/<token>/`
- `/accounts/password-reset-complete/`

---

## 5. Template Fixture — 27 CV Templates

The study guide says "at least 3 templates". The actual project has **27 templates** loaded via fixture at `templates_app/fixtures/initial_templates.json`. The fixture maps to HTML files in `templates/pdf/`:

Classic, Modern, Compact, Minimalist, Academic, Architect, Bold, Consultant, Corporate, Creative, Designer, Elegant, Engineer, Executive, Finance, Flat, Graduate, Journalist, Lawyer, Marketing, Medical, Photographer, Researcher, Startup, Swiss, Tech, Writer

Plus 4 additional templates added manually: resume_creative.html, resume_modern.html, resume_professional.html, template_corporate.html

**Total unique template HTML files: 31** in `templates/pdf/`

### Q&A: "How are templates loaded?"
**Answer:** Templates are stored in the database via a fixture file. After running `python manage.py migrate`, you must run `python manage.py loaddata initial_templates` to populate the `ResumeTemplate` table. Each template record has a `name`, `description`, `html_file` path (pointing to `templates/pdf/template_*.html`), and an `is_active` boolean. The gallery view (`templates_app/views.py`) filters `is_active=True`. The `html_file` field is used by `render_to_string()` to render resume data into the template.

---

## 6. Additional Features You Should Know

### `create_from_template` view (`resumes/views.py:60-89`)
Creates a new resume pre-filled with sample data (education, experience, skills, projects, certifications, languages, references). Uses the `_sample_data()` helper function.

### `_sample_data()` vs `_sample_context()`
- `resumes/views.py:_sample_data()` — Returns plain dicts for pre-filling a user's new resume
- `templates_app/views.py:_sample_context()` — Returns `QuerySet`-wrapped objects for template previews

### `_QuerySet` helper class (`templates_app/views.py:9-18`)
Wraps a plain Python list to mimic Django's QuerySet interface (supports `.all()`, iteration, `__bool__`). Used by the template preview system so template HTML files can use `{% for edu in resume.educations.all() %}` with sample data.

### `@xframe_options_sameorigin` decorator
Used on `resume_preview_frame` and `template_preview_frame` views to allow these pages to render inside iframes on the same domain, while the global `X_FRAME_OPTIONS = 'DENY'` in settings.py blocks iframe embedding from external sites.

### PDF Preview vs PDF Download
- `/pdf/<id>/preview/` — Renders HTML in a browser page
- `/pdf/<id>/download/` — Generates actual PDF via xhtml2pdf and serves as file attachment

---

## 7. Deployment Files (New from Remote Merge)

The merge brought in these deployment-related files that you should know about:

### Dockerfile
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt . && pip install --no-cache-dir -r requirements.txt
COPY . .
RUN python manage.py collectstatic --noinput
EXPOSE 8000
CMD ["gunicorn", "resume_builder_pro.wsgi:application", "--bind", "0.0.0.0:8000"]
```

### docker-compose.yml
```yaml
services:
  web:
    build: .
    command: python manage.py runserver 0.0.0.0:8000
    volumes: [.:/app]
    ports: ["8000:8000"]
    environment: [DJANGO_DEBUG=True]
```

### Procfile (for Heroku/Render)
```
web: gunicorn resume_builder_pro.wsgi:application
```

### render.yaml (Render platform deployment)
- Build: `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
- Start: `gunicorn resume_builder_pro.wsgi:application`
- PostgreSQL database provisioned automatically
- `DJANGO_SECRET_KEY` auto-generated, `DJANGO_DEBUG=False`
- `WEB_CONCURRENCY=3`

### Q&A: "How did you deploy the application?"
**Answer:** We containerized the application using Docker with a Python 3.12-slim image. The Dockerfile installs dependencies, runs `collectstatic` at build time, and serves via Gunicorn on port 8000. For cloud deployment, we configured a `render.yaml` that provisions a free-tier PostgreSQL database, sets production environment variables (secret key auto-generated, debug=False), and runs migrations automatically on deploy. We also have a `Procfile` for alternative platforms like Heroku. The settings.py reads `DATABASE_URL` from environment variables for production PostgreSQL connection.

---

## 8. Complete Request Flow (Updated)

1. User opens `127.0.0.1:8000` → TemplateView shows `landing.html`
2. User registers at `/accounts/register/` → `register_view` creates User + UserProfile, hashes password
3. User logs in at `/accounts/login/` → `login_view` with Django `AuthenticationForm`, session set for 7 days
4. User sees dashboard at `/resumes/` → `dashboard` paginates resumes (9 per page)
5. User clicks "Create New Resume" → `resume_create` → redirect to wizard (first step: education)
6. Wizard at `/resumes/<id>/wizard/<step>/` → 7 steps: education → experience → skills → projects → certifications → languages → references
   - Each step saves immediately to DB via `form.save(commit=False); obj.resume = resume; obj.save()`
   - User can add multiple entries per step ("Add Another" button)
   - User can edit/delete entries within each step
7. After wizard → `/resumes/<id>/templates/` → pick from 27+ templates with live iframe preview
8. Preview at `/resumes/<id>/preview/` → rendered via `render_to_string(template.html_file, context)`
9. Download PDF at `/pdf/<id>/download/` → `xhtml2pdf.pisa.CreatePDF()` converts HTML to PDF

---

## 9. Complete Entity Relationships (Updated Diagram)

```
User (Django auth.User)
 |
 |--- OneToOne ---> UserProfile (phone, address, photo)
 |
 |--- ForeignKey (1:M) ---> Resume (title, template, dates)
                               |
                               |--- ForeignKey (M:1) ---> ResumeTemplate (27 templates)
                               |
                               |--- FK (1:M) ---> Education (institution, qualification, start_year, end_year)
                               |--- FK (1:M) ---> Experience (company, role, start_year, end_year)
                               |--- FK (1:M) ---> Skill (name, proficiency_level)
                               |--- FK (1:M) ---> Project (name, description, link)
                               |--- FK (1:M) ---> Certification (title, issuer, year_awarded)
                               |--- FK (1:M) ---> Language (name, proficiency_level)
                               |--- FK (1:M) ---> Reference (name, relationship, contact)
```

---

## 10. Presentation Tips — New Additions

- **Demo the template gallery** at `/templates/` — show 27 templates loading from fixture data
- **Show the iframe preview system** — explain `@xframe_options_sameorigin` and how `X_FRAME_OPTIONS = 'DENY'` is overridden per-view
- **Show the admin panel** — demonstrate TabularInline for all 7 child models on the Resume change page
- **Show the migrations** — run `python manage.py showmigrations` and point out `0002→0003→0004` year-field migration sequence
- **Show the Dockerfile** — explain the multi-stage build with `collectstatic`
- **Show the test suite** — run `python manage.py test` to show 125 tests passing
- **Show the logging** — mention the console logger for `accounts` and `pdf_export` apps
