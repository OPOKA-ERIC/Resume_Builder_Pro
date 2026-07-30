from fpdf import FPDF

pdf = FPDF()
pdf.add_page()

pdf.set_font("Helvetica", "B", 18)
pdf.cell(0, 12, "Isabella Namuganza", new_x="LMARGIN", new_y="NEXT", align="C")
pdf.set_font("Helvetica", "", 11)
pdf.cell(0, 8, "Presentation Script - Admin Panel (5-7 Minutes)", new_x="LMARGIN", new_y="NEXT", align="C")
pdf.ln(8)

pdf.set_draw_color(200, 200, 200)
pdf.line(10, pdf.get_y(), 200, pdf.get_y())
pdf.ln(8)


def section(title, body):
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 9, title, new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 11)
    pdf.multi_cell(0, 6, body)
    pdf.ln(4)


section(
    "OPENING (30 seconds)",
    'Good morning. My name is Isabella Namuganza, and I was responsible for configuring the Django admin panel. '
    "The admin panel is a built-in Django feature that allows us to manage all application data through a web interface "
    "without writing any SQL or touching the database directly.",
)

section(
    "LIVE DEMO - Navigate to /admin/",
    "I will now log in to the admin panel to show you what we can do.\n"
    "Log in with: admin / admin123",
)

section(
    "1. MANAGING USERS (1 minute)",
    "First, under Authentication and Authorization, I will click Users.\n"
    "Here we can see all registered users. We can:\n"
    "- Click any username to edit their details\n"
    '- Check the "Active" box to enable or disable an account\n'
    '- Select a user and choose "Delete selected users" from the dropdown\n\n'
    "This is useful if someone violates the terms of service or requests account deletion.\n"
    "I configured this using Django's built-in User model - no extra code needed.",
)

section(
    "2. MANAGING RESUMES (2 minutes)",
    'Now I will click Resumes under the Resumes section.\n'
    "This shows every resume created by any user. I can search by title or filter by user.\n\n"
    'Now watch this - I will click on a resume title to open it.\n'
    "Notice that all the related sections are shown on the SAME page:\n"
    "- Education history\n"
    "- Work experience\n"
    "- Skills, Projects, Certifications\n"
    "- Languages and References\n\n"
    'This is called "TabularInline" in Django. I wrote this configuration so that '
    "anyone can see the full resume without jumping between different pages.\n"
    "If a user reports a bug with their resume, I can fix it here directly.",
)

section(
    "3. MANAGING TEMPLATES (1 minute)",
    "Under Templates App, click Resume Templates.\n"
    "This shows all 27 resume templates available in the application.\n"
    'Each template has an "Active" checkbox. If I uncheck it, that template disappears from the gallery.\n'
    "This allows the team to test new templates or retire old ones without deploying new code.",
)

section(
    "4. USER PROFILES (30 seconds)",
    "Under Accounts, click User Profiles.\n"
    "Here we can see each user's phone number and address.\n"
    "If a user says their profile is not saving, I can check here if the data exists.",
)

section(
    "KEY TERMS TO MENTION WHEN ASKED",
    "If the lecturer asks about the code, say these exact words:\n\n"
    "- @admin.register(Resume) - This registers the model with the admin panel\n"
    "- list_display = [title, user, template] - Controls which columns appear in the list view\n"
    "- TabularInline - Displays related child records (like Education) on the parent page\n"
    "- search_fields - Adds a search bar to find records quickly\n"
    "- list_filter - Adds filters to narrow down records by user or template",
)

section(
    "CLOSING (30 seconds)",
    "In summary, the admin panel lets non-technical team members manage users, resumes, "
    "and templates through a clean web interface. I configured all of this in the admin.py files "
    "of our three Django apps. Thank you, I am happy to take questions.",
)

pdf.output("Isabella_Namuganza_Admin_Script.pdf")
print("PDF created successfully")
