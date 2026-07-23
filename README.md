# Resume Builder Pro

Build professional, polished resumes in minutes. No design skills needed.

Built by Group C, BSE2301.

## Setup

```bash
# Clone the repo
git clone https://github.com/OPOKA-ERIC/Resume_Builder_Pro.git
cd Resume_Builder_Pro

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Load the 27 CV templates into the database
python manage.py loaddata initial_templates

# Create a superuser (optional)
python manage.py createsuperuser

# Run the server
python manage.py runserver
```

> **Important:** You must run `python manage.py loaddata initial_templates` after migrating. Without this, the template gallery will be empty because the template records live in a database fixture, not in migrations.
