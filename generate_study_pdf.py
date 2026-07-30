#!/usr/bin/env python
"""Generate a comprehensive Django study guide PDF for presentation preparation."""

import os
import sys

# Ensure Django settings are configured
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resume_builder_pro.settings')

from xhtml2pdf import pisa

HTML_CONTENT = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
    @page {
        size: A4;
        margin: 2cm;
    }
    body {
        font-family: 'Helvetica', 'Arial', sans-serif;
        font-size: 11pt;
        line-height: 1.6;
        color: #1a1a1a;
    }
    h1 {
        color: #1a56db;
        font-size: 24pt;
        text-align: center;
        border-bottom: 3px solid #1a56db;
        padding-bottom: 10px;
        margin-top: 30px;
    }
    h2 {
        color: #1e40af;
        font-size: 16pt;
        border-bottom: 2px solid #3b82f6;
        padding-bottom: 5px;
        margin-top: 25px;
        page-break-after: avoid;
    }
    h3 {
        color: #2563eb;
        font-size: 13pt;
        margin-top: 18px;
        page-break-after: avoid;
    }
    h4 {
        color: #374151;
        font-size: 11pt;
        margin-top: 14px;
        page-break-after: avoid;
    }
    .cover-page {
        text-align: center;
        padding-top: 150px;
        page-break-after: always;
    }
    .cover-page h1 {
        font-size: 32pt;
        border: none;
        color: #1e40af;
    }
    .cover-page .subtitle {
        font-size: 16pt;
        color: #6b7280;
        margin-top: 20px;
    }
    .cover-page .author {
        font-size: 14pt;
        color: #374151;
        margin-top: 40px;
    }
    .cover-page .date {
        font-size: 12pt;
        color: #9ca3af;
        margin-top: 10px;
    }
    .section {
        page-break-before: always;
    }
    .no-break {
        page-break-inside: avoid;
    }
    table {
        width: 100%;
        border-collapse: collapse;
        margin: 12px 0;
        font-size: 10pt;
        page-break-inside: avoid;
    }
    th {
        background-color: #1e40af;
        color: white;
        padding: 8px 10px;
        text-align: left;
        border: 1px solid #1e40af;
    }
    td {
        padding: 6px 10px;
        border: 1px solid #d1d5db;
        vertical-align: top;
    }
    tr:nth-child(even) {
        background-color: #f3f4f6;
    }
    code {
        background-color: #f3f4f6;
        padding: 2px 5px;
        border-radius: 3px;
        font-family: 'Courier New', monospace;
        font-size: 10pt;
        color: #dc2626;
    }
    pre {
        background-color: #1f2937;
        color: #e5e7eb;
        padding: 12px 15px;
        border-radius: 6px;
        font-family: 'Courier New', monospace;
        font-size: 9pt;
        line-height: 1.4;
        overflow-wrap: break-word;
        white-space: pre-wrap;
        page-break-inside: avoid;
    }
    pre code {
        background-color: transparent;
        color: #e5e7eb;
        padding: 0;
    }
    .highlight {
        background-color: #dbeafe;
        padding: 10px 15px;
        border-left: 4px solid #1e40af;
        margin: 12px 0;
        page-break-inside: avoid;
    }
    .warning {
        background-color: #fef3c7;
        padding: 10px 15px;
        border-left: 4px solid #f59e0b;
        margin: 12px 0;
        page-break-inside: avoid;
    }
    .correct {
        color: #16a34a;
        font-weight: bold;
    }
    .wrong {
        color: #dc2626;
        font-weight: bold;
    }
    ul, ol {
        margin: 8px 0;
        padding-left: 25px;
    }
    li {
        margin-bottom: 4px;
    }
    .toc {
        page-break-after: always;
    }
    .toc h2 {
        border-bottom: 3px solid #1e40af;
    }
    .toc ul {
        list-style: none;
        padding-left: 0;
    }
    .toc ul li {
        padding: 5px 0;
        border-bottom: 1px dotted #d1d5db;
    }
    .qa-section {
        background-color: #f8fafc;
        padding: 12px;
        border: 1px solid #e2e8f0;
        border-radius: 6px;
        margin: 10px 0;
        page-break-inside: avoid;
    }
    .qa-section strong {
        color: #1e40af;
    }
    .flow-diagram {
        text-align: center;
        font-family: 'Courier New', monospace;
        font-size: 9pt;
        background-color: #f8fafc;
        padding: 15px;
        border: 1px solid #e2e8f0;
        border-radius: 6px;
        margin: 12px 0;
        line-height: 1.8;
        page-break-inside: avoid;
    }
</style>
</head>
<body>

<!-- COVER PAGE -->
<div class="cover-page">
    <h1>DJANGO CRASH COURSE<br>&amp; PROJECT STUDY GUIDE</h1>
    <div class="subtitle">Resume Builder Pro &mdash; BSE2301 Software Engineering Mini Project 2</div>
    <div class="author"><strong>Prepared for:</strong> Opoka Eric (Backend &amp; Database Lead)</div>
    <div class="author"><strong>Group W &mdash; Project 11</strong></div>
    <div class="author">Members: Opoka Eric, Opeto Isaac, Ojok Isaac, Auma Dillis</div>
    <div class="date">July 2026</div>
    <div class="date" style="margin-top: 60px; font-style: italic; color: #6b7280;">
        Presentation Day Study Material<br>
        Covers: Django Fundamentals, Project Architecture, Backend/Database Deep Dive, Q&A Preparation
    </div>
</div>

<!-- TABLE OF CONTENTS -->
<div class="toc">
    <h2>Table of Contents</h2>
    <ul>
        <li><strong>Part 1:</strong> Verifying What You Already Know (Corrections)</li>
        <li><strong>Part 2:</strong> Django Crash Course (Complete)
            <ul style="padding-left: 20px;">
                <li>2.1 Installation &amp; Setup</li>
                <li>2.2 Projects vs Apps</li>
                <li>2.3 settings.py &mdash; The Configuration Hub</li>
                <li>2.4 Models &mdash; Database Design</li>
                <li>2.5 Relationships (OneToOne, ForeignKey)</li>
                <li>2.6 Migrations</li>
                <li>2.7 Admin Panel</li>
                <li>2.8 Views &mdash; Business Logic</li>
                <li>2.9 URLs &mdash; Routing</li>
                <li>2.10 Templates &mdash; Template Language</li>
                <li>2.11 Forms</li>
                <li>2.12 Authentication</li>
                <li>2.13 Static Files &amp; Media</li>
                <li>2.14 Database Querying (ORM)</li>
            </ul>
        </li>
        <li><strong>Part 3:</strong> Your Specific Role &mdash; Opoka Eric</li>
        <li><strong>Part 4:</strong> Project Architecture Breakdown</li>
        <li><strong>Part 5:</strong> Presentation Q&A Cheat Sheet</li>
    </ul>
</div>

<!-- PART 1: CORRECTIONS -->
<div class="section">
<h1>Part 1: Verifying What You Already Know</h1>

<h2>What You Got Right</h2>
<table>
    <tr><th>Statement</th><th>Status</th><th>Notes</th></tr>
    <tr><td><code>pip install django</code></td><td class="correct">CORRECT</td><td>Installs Django globally or in venv</td></tr>
    <tr><td><code>python -m venv .venv</code></td><td class="correct">CORRECT</td><td>Creates virtual environment</td></tr>
    <tr><td><code>django-admin startproject name folder</code></td><td class="correct">CORRECT</td><td>Creates the project structure</td></tr>
    <tr><td><code>settings.py</code> contains all configurations</td><td class="correct">CORRECT</td><td>Apps, DB, templates, auth, security, etc.</td></tr>
    <tr><td><code>python manage.py runserver</code></td><td class="correct">CORRECT</td><td>Starts the development server</td></tr>
    <li>Templates for HTML/CSS go in a templates/ folder</li>
</table>

<h2>What Needs Correction</h2>

<div class="warning">
<strong>Correction 1:</strong> Creating an app<br>
You said: <code>django-admin startapp folder</code><br>
<strong>Correct:</strong> <code>python manage.py startapp appname</code> (run from inside the project where manage.py lives)
</div>

<div class="warning">
<strong>Correction 2:</strong> App file list<br>
You said: admin.py, apps.py, models.py, tests.py, views.py<br>
<strong>You missed:</strong> urls.py (each app has its own URL patterns), forms.py (form validation), __init__.py, and migrations/ folder
</div>

<div class="warning">
<strong>Correction 3:</strong> Templates folder structure<br>
You said: "create a templates/ folder inside the app, then create a todos/ folder inside that"<br>
<strong>Correct:</strong> In our project, templates are in a PROJECT-LEVEL templates/ folder (at the root), NOT inside each app. The settings.py line <code>'DIRS': [BASE_DIR / 'templates']</code> tells Django to look there. Inside, they're organized: templates/accounts/, templates/resumes/, etc.
</div>

<div class="warning">
<strong>Correction 4:</strong> The relationship flow<br>
You said: "views connects to urls.py"<br>
<strong>Correct flow:</strong> URLs connects to Views. Browser &rarr; URL &rarr; urls.py matches it &rarr; calls the correct view function &rarr; view does logic &rarr; returns HTML response
</div>
</div>

<!-- PART 2: DJANGO CRASH COURSE -->
<div class="section">
<h1>Part 2: Django Crash Course (Complete)</h1>

<h2>2.1 Installation &amp; Setup</h2>
<pre><code>pip install django                # Install Django
python -m venv .venv              # Create virtual environment
.venv\Scripts\activate            # Activate it (Windows)
pip install django                # Install INSIDE the venv</code></pre>

<div class="highlight">
<strong>Why venv?</strong> It isolates your project's packages from your global Python so different projects can use different versions of the same library. Without it, Project A might need Django 4 and Project B needs Django 5, and they'd conflict.
</div>

<h2>2.2 Projects vs Apps (Critical Distinction)</h2>

<p>Django has TWO things: <strong>Projects</strong> and <strong>Apps</strong>.</p>

<pre><code>django-admin startproject resume_builder_pro   # Creates the PROJECT
cd resume_builder_pro
python manage.py startapp accounts             # Creates an APP inside the project
python manage.py startapp resumes
python manage.py startapp templates_app
python manage.py startapp pdf_export</code></pre>

<table>
    <tr><th>Concept</th><th>What It Is</th><th>Created</th><th>Example</th></tr>
    <tr><td><strong>Project</strong></td><td>The entire website</td><td>Once</td><td>resume_builder_pro</td></tr>
    <tr><td><strong>App</strong></td><td>A module that does ONE thing</td><td>Multiple per project</td><td>accounts, resumes, pdf_export</td></tr>
</table>

<div class="highlight">
<strong>Rule of thumb:</strong> If you removed an app, the rest of the project should still work (just without that feature). Apps should be somewhat independent.
</div>

<p><strong>Your project has 4 apps:</strong></p>
<table>
    <tr><th>App</th><th>Purpose</th></tr>
    <tr><td><code>accounts</code></td><td>User registration, login, logout, profile management</td></tr>
    <tr><td><code>resumes</code></td><td>Resume, Education, Experience, Skill, Project, Certification, Language, Reference models &amp; wizard views</td></tr>
    <tr><td><code>templates_app</code></td><td>Resume template gallery, selection, and preview rendering</td></tr>
    <tr><td><code>pdf_export</code></td><td>Converting rendered resume HTML into a downloadable PDF</td></tr>
</table>

<h2>2.3 settings.py &mdash; The Configuration Hub</h2>

<p>Every Django project has one <code>settings.py</code>. It controls EVERYTHING.</p>

<table>
    <tr><th>Setting</th><th>What It Does</th><th>Our Project</th></tr>
    <tr><td><code>SECRET_KEY</code></td><td>Security key for sessions, CSRF tokens</td><td>Generated key stored</td></tr>
    <tr><td><code>DEBUG</code></td><td>Show error pages? True in dev, False in prod</td><td>Reads from env var</td></tr>
    <tr><td><code>ALLOWED_HOSTS</code></td><td>Which domains can access the site</td><td>localhost, 127.0.0.1</td></tr>
    <tr><td><code>INSTALLED_APPS</code></td><td>All apps registered here</td><td>accounts, resumes, templates_app, pdf_export</td></tr>
    <tr><td><code>MIDDLEWARE</code></td><td>Code that runs on EVERY request/response</td><td>Security, sessions, auth, CSRF, etc.</td></tr>
    <tr><td><code>DATABASES</code></td><td>Database configuration</td><td>SQLite for dev</td></tr>
    <tr><td><code>TEMPLATES</code></td><td>Where to find HTML files</td><td><code>BASE_DIR / 'templates'</code></td></tr>
    <tr><td><code>STATIC_URL</code></td><td>URL prefix for CSS/JS/images</td><td><code>'static/'</code></td></tr>
    <tr><td><code>MEDIA_URL</code></td><td>URL prefix for user uploads</td><td><code>'media/'</code></td></tr>
    <tr><td><code>LOGIN_URL</code></td><td>Where to redirect if not logged in</td><td><code>'accounts:login'</code></td></tr>
    <tr><td><code>LOGIN_REDIRECT_URL</code></td><td>Where to go after login</td><td><code>'/resumes/'</code></td></tr>
</table>

<h3>INSTALLED_APPS</h3>
<pre><code>INSTALLED_APPS = [
    'django.contrib.admin',        # Admin panel
    'django.contrib.auth',         # Authentication system
    'django.contrib.contenttypes', # Content type framework
    'django.contrib.sessions',     # Session framework
    'django.contrib.messages',     # Messaging framework
    'django.contrib.staticfiles',  # Static file serving
    'accounts',                    # Your app
    'resumes',                     # Your app
    'templates_app',               # Your app
    'pdf_export',                  # Your app
]</code></pre>

<div class="highlight">
<strong>Why register apps?</strong> Django needs to know about your apps to find their models, templates, admin configs, etc. Without registration, Django ignores your app entirely.
</div>

<h3>MIDDLEWARE (Security Layers)</h3>
<p>Middleware runs on EVERY request and response. Think of it as security checkpoints:</p>
<table>
    <tr><th>Middleware</th><th>Purpose</th></tr>
    <tr><td>SecurityMiddleware</td><td>HTTPS, HSTS headers</td></tr>
    <tr><td>WhiteNoiseMiddleware</td><td>Serves static files efficiently in production</td></tr>
    <tr><td>SessionMiddleware</td><td>Manages user sessions (cookies)</td></tr>
    <tr><td>CsrfViewMiddleware</td><td>Prevents Cross-Site Request Forgery attacks</td></tr>
    <tr><td>AuthenticationMiddleware</td><td>Attaches the logged-in user to each request</td></tr>
    <tr><td>MessageMiddleware</td><td>Handles flash messages (success/error alerts)</td></tr>
    <tr><td>XFrameOptionsMiddleware</td><td>Prevents clickjacking attacks</td></tr>
</table>

<h2>2.4 Models &mdash; Database Design</h2>

<p>Models are Python classes that map to database tables. Each attribute = a column.</p>

<h3>Field Types Used in Our Project</h3>
<table>
    <tr><th>Field Type</th><th>What It Stores</th><th>Example</th></tr>
    <tr><td><code>CharField</code></td><td>Short text (with max length)</td><td><code>title = models.CharField(max_length=200)</code></td></tr>
    <tr><td><code>TextField</code></td><td>Long text (no limit)</td><td><code>address = models.TextField()</code></td></tr>
    <tr><td><code>IntegerField</code></td><td>Whole numbers</td><td><code>start_year = models.IntegerField()</code></td></tr>
    <tr><td><code>EmailField</code></td><td>Email (validated format)</td><td>Django auth User has this</td></tr>
    <tr><td><code>BooleanField</code></td><td>True/False</td><td><code>is_active = models.BooleanField(default=True)</code></td></tr>
    <tr><td><code>DateTimeField</code></td><td>Date + time</td><td><code>created_at = models.DateTimeField(auto_now_add=True)</code></td></tr>
    <tr><td><code>ImageField</code></td><td>Image upload</td><td><code>photo = models.ImageField(upload_to='profile_photos/')</code></td></tr>
    <tr><td><code>URLField</code></td><td>URL (validated)</td><td><code>link = models.URLField(blank=True)</code></td></tr>
</table>

<h3>Field Options</h3>
<table>
    <tr><th>Option</th><th>Meaning</th><th>Example</th></tr>
    <tr><td><code>max_length</code></td><td>Maximum characters</td><td><code>max_length=200</code></td></tr>
    <tr><td><code>blank=True</code></td><td>Form can leave it empty</td><td><code>description = models.TextField(blank=True)</code></td></tr>
    <tr><td><code>null=True</code></td><td>Database can store NULL</td><td><code>end_year = models.IntegerField(null=True)</code></td></tr>
    <tr><td><code>default=X</code></td><td>Default value if not provided</td><td><code>default='intermediate'</code></td></tr>
    <tr><td><code>choices=X</code></td><td>Only allowed values from a list</td><td><code>choices=PROFICIENCY_CHOICES</code></td></tr>
    <tr><td><code>upload_to=X</code></td><td>Subfolder for uploads</td><td><code>upload_to='profile_photos/'</code></td></tr>
    <tr><td><code>on_delete=X</code></td><td>What happens when related object is deleted</td><td><code>on_delete=models.CASCADE</code></td></tr>
</table>

<div class="highlight">
<strong>CRITICAL DISTINCTION (common exam question):</strong><br>
<code>blank=True</code> = Form validation allows empty (HTML form level)<br>
<code>null=True</code> = Database stores NULL (database level)<br><br>
<code>CharField(blank=True)</code> &rarr; form accepts empty string ""<br>
<code>CharField(null=True)</code> &rarr; database stores NULL (different from "")
</div>

<h2>2.5 Relationships (Critical for Presentation)</h2>

<h3>Relationship Type 1: OneToOneField</h3>
<pre><code># accounts/models.py
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)</code></pre>

<table>
    <tr><th>Part</th><th>Meaning</th></tr>
    <tr><td><code>OneToOneField(User)</code></td><td>One User has exactly ONE UserProfile</td></tr>
    <tr><td><code>on_delete=models.CASCADE</code></td><td>If the User is deleted, delete the UserProfile too</td></tr>
    <tr><td><code>related_name='profile'</code></td><td>You can say <code>user.profile</code> to get the profile</td></tr>
</table>

<h3>Relationship Type 2: ForeignKey (Many-to-One)</h3>
<pre><code># resumes/models.py
class Resume(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='resumes')
    title = models.CharField(max_length=200)

class Education(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='educations')
    institution = models.CharField(max_length=200)</code></pre>

<table>
    <tr><th>Part</th><th>Meaning</th></tr>
    <tr><td><code>ForeignKey(User)</code></td><td>Many Resumes belong to ONE User</td></tr>
    <tr><td><code>on_delete=models.CASCADE</code></td><td>If User is deleted, ALL their Resumes are deleted too</td></tr>
    <tr><td><code>related_name='resumes'</code></td><td>You can say <code>user.resumes.all()</code> to get all user's resumes</td></tr>
</table>

<h3>on_delete Options (Know These!)</h3>
<table>
    <tr><th>Option</th><th>What Happens</th><th>Use When</th></tr>
    <tr><td><code>CASCADE</code></td><td>Delete the related object too</td><td>Child depends on parent (most common)</td></tr>
    <tr><td><code>SET_NULL</code></td><td>Set field to NULL</td><td>Optional relationship (needs null=True)</td></tr>
    <tr><td><code>PROTECT</code></td><td>Prevent deletion (raise error)</td><td>Can't allow orphaned data</td></tr>
    <tr><td><code>SET_DEFAULT</code></td><td>Set to default value</td><td>Has a sensible default</td></tr>
</table>

<h3>The related_name Reverse Lookup</h3>
<pre><code>resume = Resume.objects.get(id=1)
resume.educations.all()        # All Education entries for this resume
resume.experiences.all()       # All Experience entries
resume.skills.all()            # All Skill entries
resume.projects.all()          # All Project entries
resume.certifications.all()    # All Certification entries
resume.languages.all()         # All Language entries
resume.references.all()        # All Reference entries

user = User.objects.get(username='opoka')
user.resumes.all()             # All resumes by this user
user.profile                   # This user's profile (OneToOne reverse)</code></pre>

<h3>Our Complete Entity Relationships</h3>
<div class="flow-diagram">
User (Django built-in)<br>
&nbsp;&nbsp;|<br>
&nbsp;&nbsp;|--- OneToOne ---&gt; UserProfile<br>
&nbsp;&nbsp;|<br>
&nbsp;&nbsp;|--- ForeignKey (1:M) ---&gt; Resume<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|--- ForeignKey ---&gt; ResumeTemplate<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|--- FK (1:M) ---&gt; Education<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|--- FK (1:M) ---&gt; Experience<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|--- FK (1:M) ---&gt; Skill<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|--- FK (1:M) ---&gt; Project<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|--- FK (1:M) ---&gt; Certification<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|--- FK (1:M) ---&gt; Language<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|--- FK (1:M) ---&gt; Reference
</div>

<h2>2.6 Migrations</h2>

<p>Migrations are Django's way of propagating changes you make to your models into your database schema.</p>

<pre><code>python manage.py makemigrations          # Generate migration files (plans)
python manage.py migrate                # Execute those plans against the DB
python manage.py showmigrations          # See all migrations and their status
python manage.py migrate resumes 0003   # Roll back to a specific migration</code></pre>

<h3>What Happens Internally</h3>
<ol>
    <li>You write/modify models in models.py</li>
    <li><code>makemigrations</code> reads your models and compares to current DB state</li>
    <li>It creates a migration file: <code>resumes/migrations/0001_initial.py</code></li>
    <li><code>migrate</code> runs that script, creating/altering tables</li>
    <li>Django tracks which migrations have been applied in a special table</li>
</ol>

<div class="highlight">
<strong>Golden Rule:</strong> Every time you change a model, run <code>makemigrations</code> then <code>migrate</code>. Never edit the database directly.
</div>

<h2>2.7 Admin Panel</h2>

<p>Django auto-generates an admin interface at <code>/admin/</code>. You configure it in <code>admin.py</code>.</p>

<pre><code># resumes/admin.py
@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'template', 'created_at', 'updated_at']
    list_filter = ['user', 'template']
    search_fields = ['title', 'user__username']
    inlines = [EducationInline, ExperienceInline, SkillInline,
               ProjectInline, CertificationInline, LanguageInline, ReferenceInline]</code></pre>

<table>
    <tr><th>Feature</th><th>What It Does</th></tr>
    <tr><td><code>list_display</code></td><td>Columns shown in the list view</td></tr>
    <tr><td><code>list_filter</code></td><td>Sidebar filters</td></tr>
    <tr><td><code>search_fields</code></td><td>Search bar functionality</td></tr>
    <tr><td><code>inlines</code></td><td>Show related objects on the same page</td></tr>
    <tr><td><code>@admin.register()</code></td><td>Shortcut to register the model</td></tr>
</table>

<h2>2.8 Views &mdash; Business Logic</h2>

<p>Views are functions that handle HTTP requests and return HTTP responses.</p>

<h3>The View Pattern</h3>
<pre><code>@login_required                    # 1. Decorator: must be logged in
def dashboard(request):            # 2. Receives HTTP request object
    # 3. Query the database
    resumes_list = Resume.objects.filter(user=request.user)
    paginator = Paginator(resumes_list, 9)
    page_number = request.GET.get('page')
    resumes = paginator.get_page(page_number)
    # 4. Return HTML response with data
    return render(request, 'resumes/dashboard.html', {'resumes': resumes})</code></pre>

<h3>The request Object</h3>
<table>
    <tr><th>Attribute</th><th>What It Contains</th></tr>
    <tr><td><code>request.method</code></td><td>GET or POST</td></tr>
    <tr><td><code>request.user</code></td><td>Currently logged-in user</td></tr>
    <tr><td><code>request.POST</code></td><td>Form data submitted via POST</td></tr>
    <tr><td><code>request.GET</code></td><td>URL query parameters (?page=2)</td></tr>
    <tr><td><code>request.session</code></td><td>Session data (persists across requests)</td></tr>
</table>

<h3>Common View Patterns</h3>

<h4>Pattern 1: Show a page (GET only)</h4>
<pre><code>def some_view(request):
    data = MyModel.objects.all()
    return render(request, 'template.html', {'data': data})</code></pre>

<h4>Pattern 2: Handle form submission (GET + POST)</h4>
<pre><code>def some_view(request):
    if request.method == 'POST':
        form = MyForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('some_url')  # PRG pattern
    else:
        form = MyForm()
    return render(request, 'form.html', {'form': form})</code></pre>

<h3>Decorators (The @ symbols above views)</h3>
<table>
    <tr><th>Decorator</th><th>Purpose</th></tr>
    <tr><td><code>@login_required</code></td><td>Redirect to login page if not authenticated</td></tr>
    <tr><td><code>@csrf_protect</code></td><td>Require CSRF token (security against form attacks)</td></tr>
    <tr><td><code>@never_cache</code></td><td>Don't let browser cache this page</td></tr>
    <tr><td><code>@require_http_methods(["GET", "POST"])</code></td><td>Only allow certain HTTP methods</td></tr>
    <tr><td><code>@xframe_options_sameorigin</code></td><td>Allow this page in iframes from same domain</td></tr>
</table>

<h2>2.9 URLs &mdash; Routing</h2>

<h3>The Routing Chain</h3>
<div class="flow-diagram">
Browser: GET /resumes/1/preview/<br>
&nbsp;&nbsp;&darr;<br>
resume_builder_pro/urls.py:<br>
&nbsp;&nbsp;path('resumes/', include('resumes.urls'))<br>
&nbsp;&nbsp;&darr;<br>
resumes/urls.py:<br>
&nbsp;&nbsp;path('&lt;int:resume_id&gt;/preview/', views.resume_preview)<br>
&nbsp;&nbsp;&darr;<br>
views.py:<br>
&nbsp;&nbsp;def resume_preview(request, resume_id):
</div>

<h3>URL Parameters</h3>
<table>
    <tr><th>Syntax</th><th>Captures</th><th>Type</th><th>Example URL</th></tr>
    <tr><td><code>&lt;int:resume_id&gt;</code></td><td>Integer</td><td>int</td><td>/resumes/<strong>1</strong>/preview/</td></tr>
    <tr><td><code>&lt;str:step&gt;</code></td><td>String</td><td>str</td><td>/resumes/1/wizard/<strong>education</strong>/</td></tr>
</table>

<h3>Namespacing (app_name)</h3>
<pre><code># resumes/urls.py
app_name = 'resumes'  # Creates a NAMESPACE

# In templates:
{% url 'resumes:dashboard' %}
{% url 'resumes:resume_preview' resume_id=1 %}

# In views:
return redirect('resumes:dashboard')
return redirect('resumes:resume_preview', resume_id=resume.id)</code></pre>

<div class="highlight">
<strong>Why namespacing?</strong> Without it, two apps might both have a URL named 'dashboard', causing conflicts. Namespacing makes them <code>resumes:dashboard</code> and <code>accounts:dashboard</code>.
</div>

<h2>2.10 Templates &mdash; Django Template Language</h2>

<pre><code>{% extends 'base.html' %}              &lt;!-- Inherit from base template --&gt;
{% load static %}                       &lt;!-- Load static file tags --&gt;

{% block content %}                     &lt;!-- Override the content block --&gt;
    {% if user.is_authenticated %}      &lt;!-- Conditional --&gt;
        &lt;p&gt;Welcome, {{ user.username }}&lt;/p&gt;  &lt;!-- Output variable --&gt;
    {% endif %}

    {% for resume in resumes %}         &lt;!-- Loop --&gt;
        &lt;h2&gt;{{ resume.title }}&lt;/h2&gt;
    {% endfor %}

    &lt;form method="post"&gt;
        {% csrf_token %}                &lt;!-- Security token (REQUIRED for POST) --&gt;
        {{ form.as_p }}                 &lt;!-- Render form fields as paragraphs --&gt;
        &lt;button type="submit"&gt;Save&lt;/button&gt;
    &lt;/form&gt;

    &lt;a href="{% url 'resumes:dashboard' %}"&gt;Back&lt;/a&gt;  &lt;!-- URL by name --&gt;
    &lt;img src="{% static 'img/logo.png' %}"&gt;           &lt;!-- Static file --&gt;
{% endblock %}</code></pre>

<table>
    <tr><th>Tag/Syntax</th><th>Purpose</th></tr>
    <tr><td><code>{{ variable }}</code></td><td>Output a variable's value</td></tr>
    <tr><td><code>{% if %}...{% endif %}</code></td><td>Conditional rendering</td></tr>
    <tr><td><code>{% for %}...{% endfor %}</code></td><td>Loop through items</td></tr>
    <tr><td><code>{% url 'name' %}</code></td><td>Generate URL by its name</td></tr>
    <tr><td><code>{% static 'path' %}</code></td><td>Link to static files</td></tr>
    <tr><td><code>{% csrf_token %}</code></td><td>Security token for forms</td></tr>
    <tr><td><code>{% extends 'base.html' %}</code></td><td>Inherit from parent template</td></tr>
    <tr><td><code>{% block name %}...{% endblock %}</code></td><td>Define overridable sections</td></tr>
    <tr><td><code>{% load static %}</code></td><td>Load static file template tags</td></tr>
</table>

<h2>2.11 Forms</h2>

<h3>ModelForm &mdash; Auto-generate forms from models</h3>
<pre><code>class EducationForm(forms.ModelForm):
    class Meta:
        model = Education
        fields = ['institution', 'qualification', 'start_year', 'end_year', 'description']
        widgets = {
            'institution': forms.TextInput(attrs={'class': 'form-control'}),
        }</code></pre>

<h3>How Forms Work in Views</h3>
<pre><code>if request.method == 'POST':
    form = EducationForm(request.POST)         # Bind form with submitted data
    if form.is_valid():                        # Run all validation
        education = form.save(commit=False)    # Create object but DON'T save yet
        education.resume = resume               # Set the foreign key
        education.save()                        # NOW save to database</code></pre>

<div class="highlight">
<strong>Why commit=False?</strong> It creates the object in memory but doesn't save to DB yet. This lets you add extra data (like the foreign key <code>resume</code>) before saving. Without it, the Education entry would be saved without knowing which Resume it belongs to.
</div>

<h2>2.12 Authentication</h2>

<p>Django provides a complete auth system out of the box.</p>

<pre><code>from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm</code></pre>

<table>
    <tr><th>Function</th><th>What It Does</th></tr>
    <tr><td><code>User.objects.create_user()</code></td><td>Create a new user with hashed password</td></tr>
    <tr><td><code>authenticate(username=..., password=...)</code></td><td>Verify credentials, returns user or None</td></tr>
    <tr><td><code>login(request, user)</code></td><td>Start a session (set cookie)</td></tr>
    <tr><td><code>logout(request)</code></td><td>End the session</td></tr>
    <tr><td><code>request.user.is_authenticated</code></td><td>Check if user is logged in</td></tr>
</table>

<p><strong>Our auth flow:</strong></p>
<ol>
    <li>User fills RegistrationForm (username, email, password1, password2)</li>
    <li><code>form.save()</code> creates User with hashed password</li>
    <li><code>UserProfile.objects.create(user=user)</code> creates the profile</li>
    <li>User logs in with AuthenticationForm</li>
    <li><code>login(request, user)</code> starts the session</li>
    <li><code>@login_required</code> decorator protects views</li>
    <li><code>logout(request)</code> ends the session</li>
</ol>

<h2>2.13 Static Files &amp; Media</h2>

<table>
    <tr><th></th><th>Static Files</th><th>Media Files</th></tr>
    <tr><td><strong>What</strong></td><td>CSS, JS, images that ship with the app</td><td>User-uploaded files</td></tr>
    <tr><td><strong>Location</strong></td><td>/static/</td><td>/media/</td></tr>
    <tr><td><strong>URL prefix</strong></td><td>STATIC_URL = 'static/'</td><td>MEDIA_URL = 'media/'</td></tr>
    <tr><td><strong>In templates</strong></td><td>{% static 'css/style.css' %}</td><td>{{ user.profile.photo.url }}</td></tr>
    <tr><td><strong>Template tag</strong></td><td>{% load static %}</td><td>(use .url attribute)</td></tr>
    <tr><td><strong>Settings</strong></td><td>STATICFILES_DIRS, STATIC_ROOT</td><td>MEDIA_ROOT</td></tr>
</table>

<h2>2.14 Database Querying (ORM)</h2>

<pre><code># CREATE
Resume.objects.create(user=user, title='My Resume')
Education.objects.create(resume=resume, institution='Stanford', ...)

# READ
Resume.objects.all()                                    # All resumes
Resume.objects.filter(user=request.user)                # Filter by condition
Resume.objects.get(id=1)                                # Get one (error if not found)
get_object_or_404(Resume, id=1, user=request.user)      # Get one or show 404 page

# READ (related objects)
resume.educations.all()                                 # All education entries
resume.skills.filter(name='Python')                     # Filter within related

# UPDATE
resume.title = 'New Title'
resume.save()                                           # Must call .save()!

# DELETE
resume.delete()                                         # Deletes from database</code></pre>

<div class="highlight">
<strong>get_object_or_404 vs get:</strong><br>
<code>Resume.objects.get(id=1)</code> &rarr; raises <code>DoesNotExist</code> error if not found (shows ugly error page)<br>
<code>get_object_or_404(Resume, id=1)</code> &rarr; shows a nice 404 "Page Not Found" page. Always use this in views.
</div>
</div>

<!-- PART 3: YOUR SPECIFIC ROLE -->
<div class="section">
<h1>Part 3: Your Specific Role &mdash; Opoka Eric</h1>

<h2>Your Responsibilities</h2>
<table>
    <tr><th>Responsibility</th><th>Chapter</th></tr>
    <tr><td>Django project setup and configuration</td><td>Settings, root urls.py, manage.py</td></tr>
    <tr><td>Design and implement ALL models and database migrations</td><td>Chapter 4</td></tr>
    <tr><td>Admin panel configuration</td><td>admin.py files</td></tr>
    <tr><td>Co-author Chapters 3 and 4</td><td>System Design &amp; Database Design</td></tr>
</table>

<h2>A. Project Setup &amp; Configuration</h2>

<h3>If asked: "How did you configure the project?"</h3>
<div class="qa-section">
<strong>Answer:</strong> "I set up the Django project with <code>django-admin startproject resume_builder_pro</code>, then created four apps using <code>python manage.py startapp</code>. In settings.py, I registered all apps in INSTALLED_APPS, configured the template directory to look in the project root templates/ folder, set up SQLite as the development database, configured static files with WhiteNoise for production serving, set up media file handling for user uploads, and configured authentication redirects so unauthenticated users go to the login page."
</div>

<h3>If asked: "Why did you use SQLite?"</h3>
<div class="qa-section">
<strong>Answer:</strong> "SQLite is Django's default for development. It requires no server setup, stores everything in a single file (db.sqlite3), and is perfect for development and testing. For production, we'd switch to PostgreSQL by changing the DATABASES setting in settings.py."
</div>

<h3>If asked: "What is WhiteNoise and why did you add it?"</h3>
<div class="qa-section">
<strong>Answer:</strong> "WhiteNoise is a middleware that serves static files efficiently in production. Without it, Django doesn't serve CSS/JS files on production servers like Render or Heroku. It also compresses files and adds caching headers for better performance."
</div>

<h2>B. Models &amp; Database Migrations (Your Core Expertise)</h2>

<h3>If asked: "Explain the database design"</h3>
<div class="qa-section">
<strong>Answer:</strong> "We have 10 models across 3 apps. The User model is Django's built-in authentication model. UserProfile extends it with phone, address, and photo using a OneToOneField. Resume belongs to a User via ForeignKey and links to a ResumeTemplate. Each Resume has many Education, Experience, Skill, Project, Certification, Language, and Reference entries &mdash; all linked via ForeignKey with CASCADE deletion, meaning if a Resume is deleted, all its sections are deleted too."
</div>

<h3>If asked: "What relationships did you use?"</h3>
<div class="qa-section">
<strong>Answer:</strong>
<ul>
    <li><strong>OneToOneField:</strong> User &harr; UserProfile (one user, one profile)</li>
    <li><strong>ForeignKey (1:M):</strong> User &rarr; Resumes (one user, many resumes)</li>
    <li><strong>ForeignKey (1:M):</strong> Resume &rarr; Education/Experience/Skill/etc. (one resume, many entries)</li>
</ul>
</div>

<h3>If asked: "What does on_delete=models.CASCADE mean?"</h3>
<div class="qa-section">
<strong>Answer:</strong> "It means if the parent object is deleted, all child objects are deleted too. For example, if a User is deleted, all their Resumes are deleted, and all Education/Experience entries on those Resumes are also deleted. This maintains referential integrity and prevents orphaned data in the database."
</div>

<h3>If asked: "What does related_name do?"</h3>
<div class="qa-section">
<strong>Answer:</strong> "It creates a reverse relationship. If Resume has <code>user = ForeignKey(User, related_name='resumes')</code>, then from a User object, I can access all their resumes with <code>user.resumes.all()</code>. Without related_name, I'd have to use the less readable <code>user.resume_set.all()</code>."
</div>

<h3>If asked: "How did you handle the migrations?"</h3>
<div class="qa-section">
<strong>Answer:</strong> "After defining all models, I ran <code>python manage.py makemigrations</code> which reads the models and generates migration files. Then <code>python manage.py migrate</code> which executes those migrations against the database, creating the actual tables. Each time we changed a model, we ran makemigrations again to generate a new migration. This gives us a version-controlled history of all database changes."
</div>

<h3>If asked: "Why did you use IntegerField for years instead of DateField?"</h3>
<div class="qa-section">
<strong>Answer:</strong> "For education and experience, we only need the year (not the exact date). IntegerField is simpler and avoids the complexity of handling full dates when the user only knows the year. We store start_year and end_year, and end_year is nullable to represent 'present' or 'ongoing'."
</div>

<h2>C. Admin Panel Configuration</h2>

<h3>If asked: "How did you set up the admin?"</h3>
<div class="qa-section">
<strong>Answer:</strong> "In each app's admin.py, I registered models using the @admin.register() decorator. For the Resume model, I used list_display to show key columns (title, user, template, dates), list_filter and search_fields for filtering and searching, and TabularInline classes for Education, Experience, Skill, etc. so they appear on the Resume admin page without needing separate pages."
</div>

<h3>If asked: "Why use inlines?"</h3>
<div class="qa-section">
<strong>Answer:</strong> "Because Education, Experience, etc. are child models of Resume (ForeignKey). Using TabularInline, an admin can manage all related entries directly on the Resume page instead of navigating to separate pages. It's more efficient and shows the relationship clearly."
</div>
</div>

<!-- PART 4: PROJECT ARCHITECTURE -->
<div class="section">
<h1>Part 4: Project Architecture Breakdown</h1>

<h2>Complete Request Flow</h2>
<div class="flow-diagram">
1. User opens browser, goes to 127.0.0.1:8000<br>
2. Django starts, reads settings.py, loads all apps<br>
3. Request hits resume_builder_pro/urls.py (ROOT urlconf)<br>
4. URL prefix matches &rarr; forwards to app's urls.py<br>
5. App's urls.py matches exact path &rarr; calls view function<br>
6. View queries database via Models (ORM)<br>
7. View renders HTML template with data<br>
8. Response sent back to browser<br>
9. Browser displays the page
</div>

<h2>All URL Routes in Our Project</h2>
<table>
    <tr><th>URL</th><th>App</th><th>View</th><th>Purpose</th></tr>
    <tr><td>/</td><td>-</td><td>TemplateView</td><td>Landing page</td></tr>
    <tr><td>/admin/</td><td>-</td><td>Django admin</td><td>Admin panel</td></tr>
    <tr><td>/accounts/register/</td><td>accounts</td><td>register_view</td><td>Registration form</td></tr>
    <tr><td>/accounts/login/</td><td>accounts</td><td>login_view</td><td>Login form</td></tr>
    <tr><td>/accounts/logout/</td><td>accounts</td><td>logout_view</td><td>Logout</td></tr>
    <tr><td>/accounts/profile/</td><td>accounts</td><td>profile_view</td><td>Profile page</td></tr>
    <tr><td>/accounts/password-change/</td><td>accounts</td><td>password_change_view</td><td>Change password</td></tr>
    <tr><td>/resumes/</td><td>resumes</td><td>dashboard</td><td>User's resume dashboard</td></tr>
    <tr><td>/resumes/create/</td><td>resumes</td><td>resume_create</td><td>Create new resume</td></tr>
    <tr><td>/resumes/&lt;id&gt;/wizard/&lt;step&gt;/</td><td>resumes</td><td>wizard_step</td><td>Multi-step form</td></tr>
    <tr><td>/resumes/&lt;id&gt;/templates/</td><td>resumes</td><td>template_select</td><td>Choose template</td></tr>
    <tr><td>/resumes/&lt;id&gt;/preview/</td><td>resumes</td><td>resume_preview</td><td>Preview resume</td></tr>
    <tr><td>/resumes/&lt;id&gt;/edit/</td><td>resumes</td><td>resume_edit</td><td>Edit resume</td></tr>
    <tr><td>/resumes/&lt;id&gt;/delete/</td><td>resumes</td><td>resume_delete</td><td>Delete resume</td></tr>
    <tr><td>/templates/</td><td>templates_app</td><td>template_gallery</td><td>Browse templates</td></tr>
    <tr><td>/templates/&lt;id&gt;/preview/</td><td>templates_app</td><td>template_preview</td><td>Preview template</td></tr>
    <tr><td>/pdf/&lt;id&gt;/download/</td><td>pdf_export</td><td>download_pdf</td><td>Download PDF</td></tr>
    <tr><td>/pdf/&lt;id&gt;/preview/</td><td>pdf_export</td><td>pdf_preview</td><td>Preview PDF</td></tr>
</table>

<h2>Technology Stack</h2>
<table>
    <tr><th>Technology</th><th>Version</th><th>Purpose</th></tr>
    <tr><td>Python</td><td>3.12</td><td>Programming language</td></tr>
    <tr><td>Django</td><td>6.0.6</td><td>Web framework (MVT pattern)</td></tr>
    <tr><td>SQLite</td><td>-</td><td>Development database</td></tr>
    <tr><td>PostgreSQL</td><td>-</td><td>Production database</td></tr>
    <tr><td>Bootstrap</td><td>5.3.0</td><td>CSS framework for responsive UI</td></tr>
    <tr><td>WhiteNoise</td><td>-</td><td>Static file serving in production</td></tr>
    <tr><td>xhtml2pdf</td><td>-</td><td>HTML to PDF conversion</td></tr>
    <tr><td>Pillow</td><td>-</td><td>Image handling (profile photos)</td></tr>
    <tr><td>Gunicorn</td><td>-</td><td>Production web server</td></tr>
    <tr><td>Git/GitHub</td><td>-</td><td>Version control</td></tr>
</table>
</div>

<!-- PART 5: Q&A CHEAT SHEET -->
<div class="section">
<h1>Part 5: Presentation Q&amp;A Cheat Sheet</h1>

<h2>General Django Questions</h2>

<div class="qa-section">
<strong>Q: What is Django?</strong><br>
A: Django is a Python web framework that follows the MVT (Model-View-Template) pattern. It handles the boring stuff (database, URLs, forms, security) so developers focus on building features. It's batteries-included, meaning it comes with authentication, admin panel, ORM, and more out of the box.
</div>

<div class="qa-section">
<strong>Q: What is the difference between a project and an app?</strong><br>
A: A project is the entire website (created once with django-admin startproject). An app is a module that handles one specific feature (created with python manage.py startapp). A project contains multiple apps. If you removed an app, the rest should still work.
</div>

<div class="qa-section">
<strong>Q: What is the MVT pattern?</strong><br>
A: Model-View-Template. Model = database structure. View = business logic (handles request, talks to model). Template = HTML presentation. It's Django's version of MVC (Model-View-Controller).
</div>

<div class="qa-section">
<strong>Q: What is the ORM?</strong><br>
A: Object-Relational Mapping. It lets you write Python code instead of SQL to interact with the database. You define models as Python classes, and the ORM converts them to database tables and queries.
</div>

<div class="qa-section">
<strong>Q: How does Django handle security?</strong><br>
A: CSRF tokens prevent form attacks. Passwords are hashed (PBKDF2 by default). The ORM prevents SQL injection. XSS protection via template auto-escaping. Session management with secure cookies. Middleware for security headers.
</div>

<div class="qa-section">
<strong>Q: What is a migration?</strong><br>
A: A migration is a Python file that describes changes to the database schema. makemigrations generates them from model changes. migrate applies them to the database. They're version-controlled so you can roll back changes.
</div>

<div class="qa-section">
<strong>Q: What is the difference between blank=True and null=True?</strong><br>
A: blank=True = form validation allows the field to be empty (form level). null=True = the database stores NULL (database level). For CharField, blank=True means empty string "", null=True means NULL (they're different!).
</div>

<div class="qa-section">
<strong>Q: Why did you use ForeignKey instead of OneToOne for Resume to User?</strong><br>
A: Because one user can have many resumes. OneToOne would limit them to exactly one resume, which doesn't match our requirements. ForeignKey allows the one-to-many relationship.
</div>

<div class="qa-section">
<strong>Q: What is the Django admin panel?</strong><br>
A: A auto-generated interface for managing data, configured in admin.py of each app. It provides CRUD operations, search, filtering, and inline editing of related models. It's great for development and content management.
</div>

<div class="qa-section">
<strong>Q: How does the wizard save data?</strong><br>
A: Each step saves to the database immediately via form.save(). This means progress isn't lost if the user navigates away. Each step creates related objects (Education, Experience, etc.) linked to the Resume via ForeignKey.
</div>

<div class="qa-section">
<strong>Q: What is {% csrf_token %} and why is it needed?</strong><br>
A: CSRF = Cross-Site Request Forgery. It's a security token that Django generates for each form. When the form is submitted, Django verifies the token matches. This prevents malicious websites from submitting forms on behalf of your users.
</div>

<div class="qa-section">
<strong>Q: What is {% url 'resumes:dashboard' %}?</strong><br>
A: It's the Django template tag for generating URLs by their name instead of hardcoding paths. 'resumes' is the namespace (app_name), 'dashboard' is the URL name. This is better than hardcoding '/resumes/' because if you change the URL path, the template still works.
</div>

<div class="qa-section">
<strong>Q: What is commit=False in form.save()?</strong><br>
A: It creates the model object in memory but doesn't save it to the database yet. This lets you modify the object (like setting the foreign key) before committing. In our wizard, we do: obj = form.save(commit=False); obj.resume = resume; obj.save()
</div>

<h2>Project-Specific Questions</h2>

<div class="qa-section">
<strong>Q: Why did you choose Django over Flask?</strong><br>
A: Django is batteries-included. It comes with authentication, admin panel, ORM, forms, and security features built in. For a resume builder that needs user accounts, database management, and an admin panel, Django saves a lot of development time compared to Flask where you'd need to add these as separate libraries.
</div>

<div class="qa-section">
<strong>Q: How many models does your project have and why?</strong><br>
A: We have 10 models across 3 apps. User and UserProfile for authentication. Resume as the main entity. Education, Experience, Skill, Project, Certification, Language, and Reference as child models linked to Resume. ResumeTemplate for available designs. Each model represents a distinct data entity.
</div>

<div class="qa-section">
<strong>Q: What are the future extensions you mentioned?</strong><br>
A: Payment processing for premium templates, third-party job-board integration, and real-time collaborative editing. These were out of scope for this project but noted in the design document.
</div>

<div class="qa-section">
<strong>Q: How does PDF generation work?</strong><br>
A: The pdf_export app uses xhtml2pdf. It takes the resume data, renders it into an HTML string using the selected template, then converts that HTML to a PDF using pisa.CreatePDF(). The PDF is served as a download response.
</div>

<div class="qa-section">
<strong>Q: How does the template selection work?</strong><br>
A: ResumeTemplate model stores template metadata (name, description, preview image, html_file path). Users browse a gallery, preview templates with sample data, and select one. The resume stores a ForeignKey to the selected template. When previewing or exporting, the system renders the resume data using the template's HTML file.
</div>

<div class="highlight" style="page-break-before: always;">
<strong>PRESENTATION TIPS:</strong>
<ul>
    <li>Always speak about YOUR specific contributions (setup, models, migrations, admin)</li>
    <li>Use the actual file paths when explaining (e.g., "In resumes/models.py, line 6...")</li>
    <li>Demo the admin panel to show database management</li>
    <li>Walk through the wizard flow to show the multi-step form</li>
    <li>Explain WHY you made decisions, not just WHAT you did</li>
    <li>If you don't know an answer, say "That's a great question, let me think..." rather than guessing</li>
    <li>Show the GitHub repository and explain the commit history</li>
</ul>
</div>

</body>
</html>
"""

def generate_pdf():
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Django_Study_Guide_Opoka_Eric.pdf")

    with open(output_path, "wb") as out_file:
        pisa_status = pisa.CreatePDF(HTML_CONTENT, dest=out_file)

    if pisa_status.err:
        print(f"Error generating PDF: {pisa_status.err}")
        return False

    print(f"PDF generated successfully: {output_path}")
    return True

if __name__ == "__main__":
    generate_pdf()
