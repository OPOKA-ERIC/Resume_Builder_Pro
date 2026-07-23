# User Manual

**Resume Builder Pro**
**Version 1.0 — July 2026**

---

## 1. Introduction

Resume Builder Pro is a web-based application that enables users to create professional, polished resumes without design skills. The application guides you through a step-by-step wizard to enter your career information, choose from professionally designed templates, and download a print-ready PDF.

### System Requirements

- **Web Browser:** Google Chrome 90+, Mozilla Firefox 88+, Microsoft Edge 90+, or Safari 14+
- **Internet Connection:** Required (application is web-based)
- **Screen Resolution:** Minimum 1024x768; responsive design supports mobile devices

---

## 2. Getting Started

### 2.1 Creating an Account

1. Navigate to the application homepage at the provided URL.
2. Click **"Get Started Free"** on the landing page.
3. Fill in the registration form:
   - **Username:** 3-30 characters; letters, digits, and @/./+/-/_ only
   - **Email:** Your valid email address (used for account identification)
   - **Password:** Minimum 8 characters; cannot be entirely numeric or a common password
   - **Confirm Password:** Must match the password field
4. Click **"Create Account"**.
5. You will be redirected to the login page with a success message.

### 2.2 Logging In

1. Click **"Login"** in the navigation bar.
2. Enter your username and password.
3. Click **"Sign In"**.
4. You will be redirected to your **Dashboard**.

> **Note:** Your session remains active for 1 week. You will need to log in again after the session expires or if you clear your browser cookies.

### 2.3 Logging Out

Click **"Logout"** in the navigation bar. You will be redirected to the login page.

---

## 3. Profile Management

### 3.1 Viewing Your Profile

1. Click **"Profile"** in the navigation bar.
2. Your current profile information is displayed, including:
   - Username (read-only)
   - Email address
   - First name and last name
   - Phone number
   - Address
   - Profile photo (if uploaded)

### 3.2 Updating Your Profile

1. Navigate to **Profile** from the navigation bar.
2. Edit any of the following fields:
   - **Email:** Must be unique across all users
   - **First Name / Last Name:** Optional personal details
   - **Phone:** Validated format (7-20 digits with spaces, +, -, parentheses)
   - **Address:** Free-text field
   - **Photo:** Upload an image file (JPG, PNG, etc.)
3. Click **"Update Profile"**.
4. A success message confirms the update.

---

## 4. Creating a Resume

### 4.1 Starting a New Resume

1. From the **Dashboard**, click **"Create New Resume"**.
2. Enter a **title** for your resume (e.g., "Software Engineer CV").
3. Click **"Create"**.
4. You will be automatically directed to the **Resume Wizard**.

### 4.2 The Resume Wizard

The wizard guides you through 7 sections. Each section has a progress bar showing your current step.

#### Step 1: Education

Add your educational background:
- **Institution:** Name of school/university (e.g., "Makerere University")
- **Qualification:** Degree or certificate (e.g., "BSc Computer Science")
- **Start Date:** When you started
- **End Date:** When you graduated (leave blank if currently studying)
- **Description:** Additional details (honours, relevant coursework)

Click **"Save & Next"** to proceed. You can add multiple education entries.

#### Step 2: Experience

Add your work experience:
- **Company:** Employer name (e.g., "MTN Uganda")
- **Role:** Job title (e.g., "Software Developer")
- **Start Date:** Employment start date
- **End Date:** Employment end date (leave blank if current position)
- **Description:** Key responsibilities and achievements

Click **"Save & Next"** to proceed.

#### Step 3: Skills

Add your technical and soft skills:
- **Name:** Skill name (e.g., "Python", "Project Management")
- **Proficiency Level:** Select from:
  - Beginner
  - Intermediate
  - Advanced
  - Expert

Click **"Save & Next"** to proceed.

#### Step 4: Projects

Add notable projects:
- **Name:** Project name (e.g., "Resume Builder Pro")
- **Description:** What the project does and your role
- **Link:** URL to the project (e.g., GitHub repository)

Click **"Save & Next"** to proceed.

#### Step 5: Certifications

Add professional certifications:
- **Title:** Certification name (e.g., "AWS Cloud Practitioner")
- **Issuer:** Certifying organization (e.g., "Amazon Web Services")
- **Date Awarded:** When you received the certification

Click **"Save & Next"** to proceed.

#### Step 6: Languages

Add languages you speak:
- **Name:** Language name (e.g., "English", "Luganda")
- **Proficiency Level:** Select from:
  - Basic
  - Conversational
  - Fluent
  - Native

Click **"Save & Next"** to proceed.

#### Step 7: References

Add professional references:
- **Name:** Reference's full name (e.g., "Dr. Okello")
- **Relationship:** How you know them (e.g., "Supervisor", "Colleague")
- **Contact:** Email or phone number

Click **"Save & Finish"** to complete the wizard.

### 4.3 Adding Multiple Entries

Each wizard step allows you to add multiple entries. For example, you can add multiple education entries (undergraduate, postgraduate) or multiple work experiences. Entries you have already added are displayed above the form.

### 4.4 Editing and Deleting Entries

Each wizard step displays your previously added entries with edit and delete buttons:

1. **To edit an entry:** Click the pencil icon next to any entry. You will be taken to an edit form pre-filled with the entry's current data. Make your changes and click "Save Changes".
2. **To delete an entry:** Click the trash icon next to any entry. You will be asked to confirm the deletion. Click "Delete" to permanently remove the entry.

### 4.5 Navigating Between Steps

- **Save & Next:** Saves your current entry and moves to the next step.
- **Back:** Returns to the previous step (your previously saved entries are preserved).
- **Save & Exit:** Saves your progress and returns to the Dashboard. You can resume the wizard later from the Dashboard.

---

## 5. Viewing and Editing Resumes

### 5.1 Dashboard

The Dashboard (`/resumes/`) displays all your resumes as cards showing:
- Resume title
- Selected template (or "None selected")
- Last updated date

Each card has action buttons:
- **Edit** — Change the resume title
- **Preview** — View the full resume
- **Delete** — Remove the resume (with confirmation)

### 5.2 Editing a Resume

1. From the Dashboard, click **"Edit"** on the resume card.
2. Modify the resume title.
3. Click **"Save"** to update.

> **Note:** To edit section data (education, experience, skills, etc.), use the **Preview** button to view your resume, then navigate back to the Dashboard and use the wizard to make changes. You can also access the wizard directly to edit individual entries.

### 5.3 Deleting a Resume

1. From the Dashboard, click **"Delete"** on the resume card.
2. Review the confirmation page.
3. Click **"Yes, Delete"** to permanently remove the resume and all its data.

---

## 6. Choosing a Template

After completing the wizard, you are directed to the **Template Selection** page.

1. Browse the available templates displayed as cards.
2. Each template card shows a preview image (if available) and description.
3. Click **"Select & Preview"** on a template to apply it to your resume.
4. The selected template is saved and will be used when generating the PDF.

You can also browse all templates from the **Template Gallery** link.

---

## 7. Previewing and Downloading PDF

### 7.1 Resume Preview

1. From the Dashboard, click **"Preview"** on any resume card.
2. The preview page displays your complete resume with all sections:
   - Contact information (from your profile)
   - Education history
   - Work experience
   - Skills with proficiency levels
   - Projects
   - Certifications
   - Languages
   - References

### 7.2 Downloading as PDF

1. From the resume preview page, click **"Download PDF"**.
2. The PDF file will be generated and downloaded to your computer.
3. The PDF includes professional formatting suitable for printing or email.

> **Note:** PDF generation typically takes 2-5 seconds depending on the resume complexity.

### 7.3 PDF Preview

1. From the resume preview page, click **"Preview PDF"**.
2. The PDF is rendered in an embedded viewer within the browser.
3. You can review the formatted output before downloading.

---

## 8. Account Settings

### 8.1 Changing Your Password

1. Navigate to **Profile** → **Change Password** (or go to `/accounts/password-change/`).
2. Enter your **current password**.
3. Enter your **new password** (must meet complexity requirements).
4. Confirm your **new password**.
5. Click **"Change Password"**.
6. Your session will be maintained; you remain logged in with the new password.

### 8.2 Password Requirements

- Minimum 8 characters
- Cannot be entirely numeric
- Cannot be a commonly used password
- Cannot be too similar to your personal information

---

## 9. Troubleshooting FAQ

### Q: I forgot my password. How do I reset it?

A: Currently, password reset via email is not implemented. Contact your system administrator to reset your password through the Django admin interface at `/admin/`.

### Q: The PDF download is not working.

A: Ensure that xhtml2pdf is properly installed on the server. If you see a "PDF generation failed" message, try again after a few moments. If the issue persists, contact support.

### Q: I can't see my template in the gallery.

A: Templates must be marked as "Active" in the admin panel. Inactive templates are hidden from the gallery. Contact your administrator to activate templates.

### Q: My resume data disappeared after deleting the resume.

A: Deleting a resume permanently removes all associated data (education, experience, skills, etc.). This action cannot be undone. Always ensure you have a PDF copy before deleting.

### Q: Can I have multiple resumes?

A: Yes. You can create as many resumes as you need from the Dashboard. Each resume is independent and can have different content and templates.

### Q: Is my data secure?

A: Yes. All passwords are hashed using Django's PBKDF2 algorithm. Your data is only accessible when you are logged in. Other users cannot see your resumes. HTTPS is enforced in production.

---

## 10. Tips for a Great Resume

1. **Keep it concise:** Aim for 1-2 pages. Recruiters spend an average of 6-7 seconds scanning a resume.
2. **Use action verbs:** Start descriptions with "Developed", "Managed", "Led", "Implemented", etc.
3. **Quantify achievements:** Include numbers where possible (e.g., "Increased performance by 40%").
4. **Tailor to the job:** Customize your resume for each application.
5. **Proofread:** Check for spelling and grammar errors before downloading.
6. **Use a professional template:** Keep it clean and readable.
7. **Include relevant skills:** Focus on skills mentioned in the job posting.
8. **Update regularly:** Keep your resume current with your latest achievements.
