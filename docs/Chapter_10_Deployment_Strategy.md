# Chapter 10: Deployment Strategy

**Co-authored by: Opeto Isaac (Authentication & PDF Generation Lead) & Auma Dilish (Testing, Documentation & Deployment Lead)**

## 10.1 Overview

Resume Builder Pro is designed for containerised deployment to cloud platforms. The strategy ensures reproducibility, security, and scalability across development, staging, and production environments.

## 10.2 Deployment Architecture

```
[Client Browser] <--HTTPS--> [Reverse Proxy (Nginx)]
                                      |
                              [Application Server (Gunicorn)]
                                      |
                              [Django Application]
                                      |
                        [Database (PostgreSQL)] + [Static Files (WhiteNoise)]
```

## 10.3 Environment Configuration

| Environment | Database | Debug | Hosts | SSL |
|---|---|---|---|---|
| **Development** | SQLite3 | True | localhost, 127.0.0.1 | No |
| **Production** | PostgreSQL | False | Domain name | Yes (HTTPS) |

### Required Environment Variables (Production)

| Variable | Description | Example |
|---|---|---|
| `DJANGO_SECRET_KEY` | Cryptographic secret for sessions/CSRF | `django-insecure-...` (replace!) |
| `DJANGO_DEBUG` | Set to `False` in production | `False` |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated allowed hostnames | `resumebuilder.onrender.com` |
| `DATABASE_URL` | PostgreSQL connection string | `postgres://user:pass@host:5432/db` |
| `WEB_CONCURRENCY` | Gunicorn worker count | `3` |

## 10.4 Containerisation

### Dockerfile

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

> **Note:** xhtml2pdf is a pure Python library and requires no system-level dependencies, unlike WeasyPrint which needs libraries such as libpango. This keeps the Docker image lightweight.

### docker-compose.yml (Development)

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

## 10.5 Cloud Platform Deployment (Render)

### Steps:

1. **Push to GitHub** repository
2. **Create Render Web Service** connected to the GitHub repo
3. **Configure build command:** `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
4. **Configure start command:** `gunicorn resume_builder_pro.wsgi:application`
5. **Add environment variables** (SECRET_KEY, DATABASE_URL, etc.)
6. **Add PostgreSQL database** via Render Dashboard
7. **Verify** deployment at the generated URL

## 10.6 Static and Media Files

- **Static files:** Collected via `collectstatic` and served by WhiteNoise middleware, which handles caching headers and efficient delivery without requiring a separate CDN for basic deployments
- **Media files:** User uploads (profile photos, template previews) stored on disk; for production, consider S3-compatible storage

## 10.7 Database Migration

```bash
# Production migration command
python manage.py migrate --noinput
```

Migrations are automatically applied during deployment via the build command.

## 10.8 Security Checklist (Pre-Deployment)

- [ ] `DEBUG` reads from `DJANGO_DEBUG` environment variable (defaults to `False` in production)
- [ ] `DJANGO_SECRET_KEY` set to a strong, unique value via environment variable
- [ ] `ALLOWED_HOSTS` reads from `DJANGO_ALLOWED_HOSTS` environment variable, restricted to actual domain(s)
- [ ] `SECURE_SSL_REDIRECT = True`
- [ ] `SESSION_COOKIE_SECURE = True`
- [ ] `CSRF_COOKIE_SECURE = True`
- [ ] `SECURE_HSTS_SECONDS = 31536000`
- [ ] `SECURE_HSTS_INCLUDE_SUBDOMAINS = True`
- [ ] `SECURE_HSTS_PRELOAD = True`
- [ ] `X_FRAME_OPTIONS = 'DENY'`
- [ ] `SECURE_CONTENT_TYPE_NOSNIFF = True`
- [ ] WhiteNoise middleware configured for static file serving
- [ ] PostgreSQL database provisioned (not SQLite)
- [ ] `.gitignore` excludes `db.sqlite3`, `media/`, `__pycache__/`, `.env`

## 10.9 Monitoring and Logging

- Django logging configured for `accounts` and `pdf_export` modules
- Console-based log output for cloud platform log viewers
- Error tracking recommended: Sentry integration for production

## 10.10 Rollback Strategy

1. Keep previous Docker image tag available
2. Database migrations are forward-only; rollback requires manual data fix
3. Git-based rollback: revert to last known good commit and redeploy
