# Chapter 2: Requirements Analysis

## 2.1 Non-Functional Requirements (Quality Attributes)

**Co-authored by: Opeto Isaac (Authentication & PDF Generation Lead)**

### 2.1.1 Security

| Requirement | Description | Implementation |
|---|---|---|
| **Password Hashing** | All passwords are hashed using Django's PBKDF2 algorithm with SHA256, a minimum of 600,000 iterations | Django's built-in `django.contrib.auth` password hashers |
| **Password Validation** | Enforced password complexity: minimum 8 characters, no common passwords, no numeric-only passwords, no user-attribute similarity | Four `AUTH_PASSWORD_VALIDATORS` in settings.py |
| **CSRF Protection** | All POST forms include CSRF tokens; `CsrfViewMiddleware` enabled globally | `{% csrf_token %}` in all templates, `@csrf_protect` on sensitive views |
| **Input Validation** | All user inputs validated server-side via Django forms and model fields; username regex enforced | `RegistrationForm` and `ProfileForm` custom validators |
| **Session Security** | HTTP-only cookies, SameSite=Lax, 1-week expiry, session invalidation on password change | `SESSION_COOKIE_HTTPONLY`, `SESSION_COOKIE_SAMESITE`, `update_session_auth_hash()` |
| **XSS Prevention** | Django template auto-escaping enabled; `SECURE_CONTENT_TYPE_NOSNIFF` set; `X_FRAME_OPTIONS=DENY` | Middleware and template engine defaults |
| **Authentication Guards** | All protected views use `@login_required`; resume access restricted to owner via `user=request.user` filter | `get_object_or_404(Resume, id=resume_id, user=request.user)` |

### 2.1.2 Usability

| Requirement | Description |
|---|---|
| **Guided Wizard** | Multi-step form guides users one section at a time with a visual progress bar |
| **Responsive Design** | Bootstrap 5 ensures the application is usable on desktop, tablet, and mobile devices |
| **Form Feedback** | Real-time validation errors displayed inline with descriptive messages |
| **Flash Messages** | Success/error notifications shown via Django messages framework with auto-dismiss |
| **Intuitive Navigation** | Navbar adapts based on authentication state; clear call-to-action buttons |

### 2.1.3 Performance

| Requirement | Description |
|---|---|
| **Preview Rendering** | Resume preview renders in under 2 seconds using efficient template rendering |
| **PDF Generation** | PDF generation completes in under 5 seconds for typical resumes using xhtml2pdf |
| **Static File Serving** | WhiteNoise serves static files efficiently; `STATIC_ROOT` for collectstatic |
| **Database Efficiency** | SQLite for development; PostgreSQL for production with proper indexing on foreign keys |
| **Session Expiry** | 1-week session lifetime reduces unnecessary database lookups |

### 2.1.4 Portability

| Requirement | Description |
|---|---|
| **Cross-Platform** | Runs on any platform supporting Python 3.10+ |
| **Database Flexibility** | SQLite (development) / PostgreSQL (production) via Django ORM abstraction |
| **Containerization** | Docker-ready deployment with `Dockerfile` and `docker-compose.yml` |
| **Environment Configuration** | All secrets managed via environment variables; no hardcoded credentials |

### 2.1.5 Maintainability

| Requirement | Description |
|---|---|
| **Modular Architecture** | Four Django apps (`accounts`, `resumes`, `templates_app`, `pdf_export`) each handling a distinct concern |
| **Separation of Concerns** | Models, views, forms, and templates separated per Django best practices |
| **Testability** | Comprehensive test suite for accounts and PDF export functionality |
| **Logging** | Structured logging configured for `accounts` and `pdf_export` modules |
| **Code Standards** | PEP 8 compliance; consistent naming conventions across the codebase |

### 2.1.6 Availability

| Requirement | Description |
|---|---|
| **Uptime Target** | 99% availability during demonstration/grading period |
| **Error Handling** | Graceful error handling for PDF generation failures with user-friendly messages |
| **Fallback Mechanisms** | xhtml2pdf import error returns HTTP 501 with installation instructions |

## 2.2 Use Cases (Extended)

### UC-01: Register Account
- **Actor:** Visitor
- **Precondition:** Visitor is not logged in
- **Flow:** Visitor navigates to `/accounts/register/`, enters username, email, password, confirms password
- **Postcondition:** Account created, user redirected to login page
- **Validation:** Username uniqueness, email uniqueness, password strength requirements

### UC-02: Log In / Log Out
- **Actor:** Registered User
- **Precondition:** User has an account
- **Flow:** User enters credentials, system validates and creates session
- **Postcondition:** User is authenticated and redirected to dashboard
- **Security:** Failed attempts logged; session expires after 1 week

### UC-03: Manage Profile
- **Actor:** Registered User
- **Precondition:** User is logged in
- **Flow:** User navigates to profile, updates email/name/phone/address/photo
- **Postcondition:** Profile updated, success message displayed
- **Validation:** Email uniqueness, phone format validation

### UC-04: Change Password
- **Actor:** Registered User
- **Precondition:** User is logged in
- **Flow:** User enters current password, new password, confirmation
- **Postcondition:** Password updated, session maintained, success message displayed
- **Security:** Current password verified; new password validated against complexity rules

### UC-06: Download Resume as PDF
- **Actor:** Registered User
- **Precondition:** User has created a resume with at least one section
- **Flow:** User clicks "Download PDF" on resume preview page
- **Postcondition:** PDF file downloaded with professional formatting
- **Technical:** xhtml2pdf renders HTML template to PDF with A4 page size

### UC-08: Security Review
- **Actor:** System Administrator
- **Precondition:** Application deployed
- **Flow:** Review password hashing, input validation, session management, CSRF protection
- **Postcondition:** Application meets security requirements
