# Chapter 5: User Interface Design

## 5.1 Design Philosophy

Resume Builder Pro follows a **mobile-first, content-focused** design philosophy. The UI is built with Bootstrap 5.3 and custom CSS, using a cohesive indigo-based color system (`#4f46e5` primary) with CSS custom properties for consistent theming. All pages use Inter + Plus Jakarta Sans typography via Google Fonts. Animations are kept subtle and purposeful — fade-in-up for page loads, hover transforms on cards, and scroll-triggered reveals via IntersectionObserver.

Key design principles:
- **Clarity over decoration** — every element serves a purpose
- **Progressive disclosure** — the wizard breaks a complex task into 7 digestible steps
- **Consistent patterns** — all forms, cards, and action bars follow the same visual language
- **Accessible** — sufficient color contrast, semantic HTML, keyboard-navigable forms

## 5.2 Screen Descriptions

### 5.2.1 Landing Page (`/`)

**Purpose:** Convert visitors into registered users.

**Layout:**
- Full-width hero section with animated gradient background (`linear-gradient(135deg, #4f46e5 0%, #3730a3 50%, #1e1b4b 100%)`) and floating decorative circles
- Two-column hero: left side has headline ("Build Your Dream Resume In Minutes"), subtitle, and two CTA buttons (Get Started / Login); right side has a large document emoji
- Three feature cards in a responsive grid below the hero, each with a colored icon badge, title, and description
- "How It Works" section with 3 numbered steps (Create Profile → Choose Template → Download PDF)
- Bottom CTA card with gradient background encouraging sign-up

**Interaction:** Feature cards lift on hover (`translateY(-8px)`). All sections animate in on scroll.

**Wireframe:**
```
┌─────────────────────────────────────────┐
│  [Navbar: Logo · Login · Get Started]   │
├─────────────────────────────────────────┤
│                                         │
│  Build Your Dream Resume      📄        │
│  In Minutes                           │
│  ─────────────────────                 │
│  Create professional, polished...      │
│                                         │
│  [Get Started Free]  [Login]            │
│                                         │
├─────────────────────────────────────────┤
│  ┌──────┐  ┌──────┐  ┌──────┐         │
│  │ 📝   │  │ 🎨   │  │ 📄   │         │
│  │Step-by│  │Templ-│  │ PDF  │         │
│  │Step   │  │ates  │  │Export│         │
│  └──────┘  └──────┘  └──────┘         │
├─────────────────────────────────────────┤
│  How It Works: ① → ② → ③              │
├─────────────────────────────────────────┤
│  [CTA: Ready to Build Your Resume?]    │
├─────────────────────────────────────────┤
│  [Footer: Product · Account · About]    │
└─────────────────────────────────────────┘
```

### 5.2.2 Login Page (`/accounts/login/`)

**Purpose:** Authenticate existing users.

**Layout:**
- Centered auth card with gradient header containing a lock icon, "Welcome Back" title, and subtitle
- Two input fields (username, password) with left-aligned icons and password visibility toggle
- Full-width "Sign In" button with gradient
- Bottom link to registration page

**Interaction:** Password field has an eye icon toggle (JavaScript `togglePassword()`). Input fields highlight on focus with an indigo ring.

### 5.2.3 Registration Page (`/accounts/register/`)

**Purpose:** Create new user accounts.

**Layout:**
- Same auth card structure as login, but with a person-plus icon header
- Four fields: Username, Email, Password, Confirm Password — each with input icons
- Password fields have visibility toggles
- Password help text displayed with info icon below the field
- Inline validation errors shown with red exclamation icons

**Interaction:** Same password toggle as login. Server-side validation provides error messages; client-side `is-invalid` class adds red borders.

### 5.2.4 Dashboard (`/resumes/`)

**Purpose:** Manage all resumes — view, create, edit, preview, delete.

**Layout:**
- Gradient header banner with "My Resumes" title, description, and "Create New" button
- 3-column responsive grid of resume cards, each with:
  - Top accent bar (gradient blue)
  - Resume title and template badge
  - Metadata: template name, last updated date
  - Action bar: Edit (pencil), Preview (eye), Delete (trash) buttons
- Empty state: floating document icon, "No resumes yet" message, and CTA button

**Interaction:** Cards lift and gain border on hover. Delete navigates to confirmation page.

**Wireframe:**
```
┌─────────────────────────────────────────┐
│  [Navbar]                               │
├─────────────────────────────────────────┤
│  ┌─────────────────────────────────┐    │
│  │  My Resumes         [+ Create]  │    │
│  │  Manage your resumes            │    │
│  └─────────────────────────────────┘    │
│                                         │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐  │
│  │ ▓▓▓▓▓▓▓ │ │ ▓▓▓▓▓▓▓ │ │ ▓▓▓▓▓▓▓ │  │
│  │ Title 1 │ │ Title 2 │ │ Title 3 │  │
│  │ Template│ │ Template│ │ Template│  │
│  │ Updated │ │ Updated │ │ Updated │  │
│  │[Edit]   │ │[Edit]   │ │[Edit]   │  │
│  │[Preview]│ │[Preview]│ │[Preview]│  │
│  │[Delete] │ │[Delete] │ │[Delete] │  │
│  └─────────┘ └─────────┘ └─────────┘  │
└─────────────────────────────────────────┘
```

### 5.2.5 Resume Wizard (`/resumes/<id>/wizard/<step>/`)

**Purpose:** Guided step-by-step data entry for resume sections.

**Layout (7 steps):**
1. **Education** — Institution, qualification, start/end date, description
2. **Experience** — Company, role, start/end date, description
3. **Skills** — Name, proficiency level (beginner/intermediate/advanced/expert)
4. **Projects** — Name, description, link
5. **Certifications** — Title, issuer, date awarded
6. **Languages** — Name, proficiency level (basic/conversational/fluent/native)
7. **References** — Name, relationship, contact

**Navigation bar:**
- Horizontal row of 7 numbered circles connected by a line
- Completed steps: filled circle with checkmark icon
- Current step: filled circle with pulse animation and glow ring
- Upcoming steps: gray circle
- Step labels below each circle (abbreviated on mobile)
- Progress bar fills proportionally beneath the circles

**Form card:**
- Section header with contextual icon (book for education, briefcase for experience, etc.)
- Previously added items shown in a list-group above the form with section-specific icons and badges
- Form fields in Bootstrap layout
- Action buttons: Save & Next (primary), Start Over (outline), Save & Exit (danger, right-aligned)

**Interaction:**
- Client-side validation via `wizard.js` — required fields get `is-invalid` class on empty submit
- Completed step circles animate to show a checkmark on transition
- The connector line fills with primary color as steps advance

### 5.2.6 Template Selection (`/resumes/<id>/templates/`)

**Purpose:** Choose a visual template for the resume.

**Layout:**
- Back button + title header
- 3-column grid of template cards, each with:
  - Preview area (image or placeholder icon with gradient top bar)
  - Template name and description
  - "Select & Preview" button
- Empty state with palette icon when no templates exist

**Interaction:** Cards lift and gain primary border on hover.

### 5.2.7 Resume Preview (`/resumes/<id>/preview/`)

**Purpose:** View the resume as it will appear in the PDF.

**Layout:**
- Action bar: title, Download PDF (green), Edit (outline), Dashboard (outline)
- Full-width resume card styled to match PDF output:
  - **Header:** dark gradient background, white name, contact info with icons
  - **Sections:** each section has a primary-colored uppercase title with underline accent
  - **Entries:** flexbox layout with title/subtitle on left, dates on right
  - **Skills:** pill-shaped badges with primary background
  - **Languages:** pill-shaped badges with blue background
  - **References:** cards with left accent border
- Bottom "Download as PDF" CTA button

### 5.2.8 Profile Page (`/accounts/profile/`)

**Purpose:** View and edit user profile information.

**Layout:**
- Gradient header with circular profile photo (or placeholder avatar icon)
- User name and email displayed in the header
- Form body divided into profile sections with labeled section headers:
  - Account Information (username, first/last name, email with icons)
  - Contact Details (phone, address with icons)
  - Profile Photo (file upload)
- Action buttons: Save Changes, Change Password

### 5.2.9 Delete Confirmation (`/resumes/<id>/delete/`)

**Purpose:** Confirm irreversible resume deletion.

**Layout:**
- Centered card with red gradient header containing trash icon
- Resume title in bold
- Warning text with exclamation icon
- Two buttons: "Yes, Delete" (danger), "Cancel" (outline)

### 5.2.10 Template Gallery (`/templates/`)

**Purpose:** Browse available resume templates (public page).

**Layout:**
- Centered heading with palette icon and description text
- 3-column responsive grid of template cards (same structure as template selection)
- Each card links to a detailed preview page
- Empty state when no templates are available

### 5.2.11 PDF Preview (`/pdf/<id>/preview/`)

**Purpose:** View the generated PDF in-browser before downloading.

**Layout:**
- Action bar with title, Download PDF button, and Back button
- Full-width card containing an iframe (85vh height) loading the PDF

## 5.3 Color System

| Token | Hex | Usage |
|---|---|---|
| Primary | `#4f46e5` | Buttons, links, accents, active states |
| Primary Dark | `#3730a3` | Button hover states, gradient endpoints |
| Primary Light | `#818cf8` | Focus rings, subtle accents |
| Primary 50 | `#eef2ff` | Skill badge backgrounds, feature icon backgrounds |
| Secondary | `#0ea5e9` | Language badges, secondary accents |
| Accent | `#f59e0b` | Highlights, hero title accent |
| Success | `#10b981` | Download PDF buttons, success alerts |
| Danger | `#ef4444` | Delete actions, delete confirmation header |
| Gray 900 | `#0f172a` | Headings, dark backgrounds |
| Gray 800 | `#1e293b` | Body text |
| Gray 500 | `#64748b` | Secondary text, dates |
| Gray 200 | `#e2e8f0` | Borders, dividers |
| Gray 50 | `#f8fafc` | Page background |

## 5.4 Component Library

### Buttons
- **Primary:** Gradient from primary to primary-dark with glow shadow
- **Success:** Gradient from success to #059669
- **Danger:** Gradient from danger to #dc2626
- **Outline variants:** 2px border, transparent background, fills on hover
- All buttons: `border-radius: 8px`, `font-weight: 600`, `translateY(-1px)` on hover

### Cards
- No border, 12px border-radius, subtle shadow (`0 1px 3px rgba(0,0,0,0.08)`)
- Hover: elevated shadow + translateY(-4px)
- `.card-gradient` variant: primary gradient background with white text

### Forms
- 2px border (`#e2e8f0`), 8px border-radius
- Focus: indigo border with 4px glow ring
- Input icons: left-aligned Bootstrap Icons with color transition on focus
- Password toggle: eye icon button inside input group

### Alerts
- No border, 12px border-radius, colored background (not outline style)
- Auto-dismiss after 5 seconds via JavaScript

### Footer
- Dark background (`#0f172a`), 4-column responsive layout
- Brand section, Product links, Account links, About section
- Social icons in circular buttons with hover glow

## 5.5 Responsive Behavior

| Breakpoint | Behavior |
|---|---|
| `> 1200px` | Full 3-column layouts, horizontal wizard steps |
| `768px–1200px` | 2-column grids, slightly compressed wizard |
| `576px–768px` | Single column, wizard steps wrap with smaller circles |
| `< 576px` | Stacked layouts, full-width buttons, hero text shrinks |

## 5.6 Accessibility

- All color combinations meet WCAG 2.1 AA contrast ratio (4.5:1 minimum)
- Form inputs have associated `<label>` elements
- Interactive elements have focus styles (indigo ring)
- Error messages use both color and icon indicators
- Semantic HTML structure (`<main>`, `<nav>`, `<footer>`)
- Bootstrap 5 provides built-in screen reader support

## 5.7 JavaScript Features

| Feature | File | Description |
|---|---|---|
| Alert auto-dismiss | `main.js` | Dismisses Bootstrap alerts after 5 seconds |
| Back to top button | `main.js` | Appears after 300px scroll, smooth scrolls to top |
| Navbar scroll effect | `main.js` | Reduces padding and deepens shadow on scroll |
| Password toggle | `main.js` | Eye icon toggles password visibility |
| Form focus animations | `main.js` | Adds/removes focus class on form controls |
| Scroll animations | `main.js` | IntersectionObserver pauses/plays CSS animations |
| Wizard validation | `wizard.js` | Client-side required field validation with visual feedback |

## 5.8 Template System (PDF Templates)

Three PDF templates are provided, all sharing the same Django template context variables (`resume`, `user`) for seamless swapping:

### Classic (`template_classic.html`)
- **Style:** Single-column, serif typography (Georgia), minimal color
- **Best for:** Formal industries, ATS compatibility, conservative roles
- **Layout:** Centered header, horizontal rule dividers, skill pills in gray

### Modern (`template_modern.html`)
- **Style:** Two-column, dark sidebar, sans-serif (Arial), blue accent
- **Best for:** Tech, creative, startup, marketing roles
- **Layout:** Dark sidebar with skills, languages, certifications, references; main column with education, experience, projects

### Compact (`template_compact.html`)
- **Style:** Dense two-column, sans-serif, cyan accent, small type
- **Best for:** Experienced professionals with extensive work history
- **Layout:** Tight spacing, two-column body with left (education, experience, projects) and right (skills, certifications, languages, references)

All templates use:
- `@page { size: A4 }` with defined margins
- `page-break-inside: avoid` on entry blocks
- Fixed units (`pt`, `mm`) for print accuracy
- No external dependencies — pure HTML+CSS for xhtml2pdf compatibility
