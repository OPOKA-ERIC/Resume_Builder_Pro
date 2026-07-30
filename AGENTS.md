# Agents Context — Resume Builder Pro

## Design Principles
- **Premium, modern SaaS aesthetic** — gradients, subtle shadows, clean typography (Inter font), generous whitespace
- **Consistent spacing values**: section padding `4rem 0`, card padding `1.5rem 2rem` / `2rem 2.5rem`
- **Heading stack**: `h2` with `font-size: clamp(1.5rem, 3vw, 2rem)`, sub `p` with `color: #64748b`, `font-size: 0.92rem`
- **Buttons**: `border-radius: 10px`, `padding: 0.7rem 1.35rem`, `font-weight: 700`, `cubic-bezier(0.16, 1, 0.3, 1)` transition
- **Inputs**: `border-radius: 10px`, `border: 1.5px solid #e2e8f0`, focus — `border-color: #4f46e5` with `box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1)`
- **Primary gradient**: `linear-gradient(135deg, #4f46e5, #7c3aed)` with `box-shadow: 0 4px 15px rgba(79, 70, 229, 0.25)` (hover: `0 8px 25px rgba(79, 70, 229, 0.35)`)
- **Sections**: `<section class="... animate-fade-in-up" id="...">`
- **Navbar**: `main.landing-page` class hides bottom border and makes it transparent
- **Feature cards**: gradient top-border via `::before` pseudo-element
- **Page hero sections**: gradient backgrounds with radial overlay, dot grid pattern, flex layout with heading + sub + optional CTA
- **SWUP smooth transitions** enabled site-wide
- **Theme**: Light mode only (no dark mode support needed)

## Premium Pages Redesigned

### 1. Templates Gallery (`/templates/`)
- **Hero**: gradient bg with radial overlays, dot grid, centered heading + sub
- **Template cards**: white cards with `border-radius: 16px`, `box-shadow: 0 4px 20px rgba(0,0,0,0.06)`, hover lift `translateY(-4px)`, image placeholder with overlay, badge chip, category labels
- **Responsive**: 3-col → 2-col (≤991px) → 1-col (≤575px)

### 2. Template Preview (`/templates/1/preview/`)
- **Hero**: same gradient/dot treatment, smaller padding
- **Split layout**: image preview (55%) + details card (45%) with gradient top-border, form styling, back-to-gallery link

### 3. Jobs List (`/jobs/`)
- **Hero**: gradient bg with radial overlays, dot grid
- **Search & filter bar**: glass-morphism card, flexbox layout, select + input with icon
- **Job cards**: white cards with company section (logo placeholder + name/tag), title, description (clamped 3 lines), meta row (location, type, salary, date), action buttons
- **Responsive**: action buttons stack at ≤575px

### 4. Dashboard (`/dashboard/`)
- **Hero**: user greeting with avatar upload (file input + preview), stats grid (4-col → 2-col → 1-col) with animated count-up
- **Resume management cards**: grid of resume cards with action dropdown menus, empty state with CTA
- **Quick actions**: 4-col icon grid
- **Delete modal** with backdrop + animation
- **AJAX**: rename inline, delete via modal, avatar upload with preview
- **JS**: count-up animation on scroll (IntersectionObserver), dropdown toggles, modal controls

### 5. Profile Pages (`/profile/`, `/profile/edit/`, `/profile/delete/`)
- **Profile Hero**: avatar with upload overlay, name, email, member since, stats row (resumes, templates, downloads)
- **Profile Content**: 2-col grid layout (sidebar nav + main content area), nav pills with active indicator
- **Sections**: Personal Info, Account Security, Notification Preferences, Danger Zone (delete account)
- **Form cards**: white cards with gradient top-border, `::before` pseudo-element
- **Sidebar nav**: pill-style nav with icons, active state with gradient bg
- **Danger Zone**: card with red-tinted bg/border, delete confirmation modal
- **Responsive**: sidebar becomes horizontal scroll at ≤991px, full-width at ≤767px

### 6. Auth Pages (Login / Register)
- **Full-viewport gradient background** with dot grid overlay
- **Two-panel card layout** — left: feature list with SVG checkmarks; right: form card
- **Premium form fields** with icon-wrapped inputs, password toggle, error/hint states
- **Premium submit button** matching profile/dashboard style
- **Register**: reverse order (`auth-card-wrap-reverse`) to alternate feature/form sides
- **Responsive**: stacks vertically at ≤767px, mobile padding adjustments

## CSS Architecture
All page-specific CSS lives at the bottom of `static/css/style.css`:
1. Templates Gallery: `/* === TEMPLATES GALLERY === */` (around lines 3500-3900)
2. Template Preview: `/* === TEMPLATE PREVIEW === */` (around lines 3900-4200)
3. Jobs List: `/* === JOBS LIST === */` (around lines 4200-4500)
4. Dashboard: `/* === DASHBOARD === */` (around lines 4500-4900)
5. Profile: `/* === PROFILE === */` (around lines 4900-5314)
6. Auth Pages: `/* === AUTH PAGES === */` (after line 5314)

## JS
All page-specific JS lives at the bottom of `static/js/main.js`:
- Dashboard: count-up animation, dropdown toggle, modal logic, avatar upload
- Profile page: avatar upload with preview

## Git Commits
All premium redesign work is committed to the `master` branch. No external dependencies were added — all styling is custom CSS.

## Code Editing Reminders
- NEVER add comments to files unless asked
- Use Inter font family for premium look
- Prefer SVG inline icons over icon libraries
- Use `cubic-bezier(0.16, 1, 0.3, 1)` for premium transitions
