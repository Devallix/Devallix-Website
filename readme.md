# Devallix Portfolio Website

A full-stack personal portfolio and application distribution platform built
with Django. It combines a public marketing site, four portfolio verticals, a
blog, a contact/newsletter funnel, and a staff-only CMS for managing every
piece of content.

- **Repository:** https://github.com/Devallix/Devallix-Website
- **Implementation plan:** [plan.md](plan.md)

---

## Overview

The project is a single Django codebase with two experiences:

1. **Public site** - animated dark-themed pages for the portfolio owner's
   desktop apps, web projects, mobile apps, graphic design work, blog, skills,
   testimonials, and contact details.
2. **Dashboard** - a private, staff-only control panel to create, edit, publish,
   and delete all content, read messages, manage subscribers, review download
   statistics, and edit site-wide settings.

All content is database-driven. Uploaded images and resumes live under
`MEDIA_ROOT`; large desktop installers are hosted externally and linked by URL.

---

## Features

### Public site

- **Home** - hero with animated particles and typing effect, live stats,
  "What I Do" services, featured/latest desktop apps, web projects, mobile
  apps, featured skills, testimonial slider, CTA, and newsletter signup.
- **About** - profile image, "Who I Am", Mission, Vision, and Development
  Philosophy.
- **Skills** - grouped by category with proficiency values.
- **Portfolio hub** - live project counts, a "Selected Work" card grid
  pulling recent desktop, web, mobile, and graphic design items, and
  category cards linking to every content vertical.
- **Desktop apps** - search, category/platform filters, sorting, pagination,
  detail pages with screenshots, versions, requirements, FAQs, related apps,
  and tracked downloads.
- **Web projects** - search, filter, sort, gallery, tech stack, live demo and
  GitHub links.
- **Mobile apps** - search, platform filter, sort, store links, related apps.
- **Graphic design** - search, category filter, sort, tools, client, project
  link.
- **Blog** - search, category/tag archives, author card, view counter, related
  posts, share links, approved comments, per-post SEO fields.
- **Testimonials** - star ratings, client metadata, pagination.
- **Contact** - validated form; messages are stored in the dashboard inbox.
- **Newsletter** - idempotent subscribe endpoint with clear feedback.
- **Accounts** - login, logout, profile, profile edit, password change, and
  password reset.
- **Legal** - privacy policy and terms pages.
- **SEO** - per-page titles/descriptions, canonical URL, Open Graph/Twitter
  tags, dynamic favicon, and clean slugs.
- **Responsive** - phone, tablet, and desktop layouts across every page,
  including an off-canvas dashboard sidebar.

### Dashboard (staff only)

- Overview with totals for every content type, unread messages, active
  subscribers, recent activity, and most-downloaded apps.
- CRUD for desktop apps (with versions and screenshot uploads), web projects,
  mobile apps, graphic design, skills, blog posts, testimonials, and app
  categories.
- Contact inbox with status filters and read/replied/archive/delete actions.
- Subscriber list with CSV export.
- Download statistics and recent download events.
- Site settings editor for branding, hero copy, footer, social links, SEO,
  analytics, and contact information.
- Search and pagination across lists; responsive tables that scroll instead of
  squashing.

---

## Tech Stack

| Category | Tools |
| --- | --- |
| Backend | Django 6.0, Python 3.12+ |
| Database | SQLite (default), PostgreSQL (optional) |
| Templates | Django templates, Bootstrap 5.3.3 |
| Forms | django-crispy-forms, crispy-bootstrap5 |
| Styling | Custom `main.css` and `dashboard.css` design system |
| Icons | Font Awesome 6.5.1 |
| Animation | AOS, CSS keyframes, canvas particles |
| Sliders | Swiper 11 |
| Charts | Chart.js |
| Media | Pillow, Django `MEDIA_ROOT` |
| Static | WhiteNoise (compressed manifest storage) |
| Config | python-decouple (`.env`) |
| CORS | django-cors-headers |
| Server | Gunicorn |

---

## Requirements

- Python **3.12 or newer** (Django 6 requirement)
- pip
- Git
- Optional: PostgreSQL 14+ if not using SQLite

---

## Quick Start

```bash
git clone https://github.com/Devallix/Devallix-Website.git
cd Devallix-Website

python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS / Linux
# source .venv/bin/activate

pip install -r requirements.txt
```

Create a `.env` file in the project root (see the next section):

```dotenv
SECRET_KEY=replace-this-with-a-long-random-string
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3
```

Then initialize the database and run the server:

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open:

- Public site: http://127.0.0.1:8000/
- Login: http://127.0.0.1:8000/accounts/login/
- Dashboard: http://127.0.0.1:8000/dashboard/
- Django admin: http://127.0.0.1:8000/admin/

`createsuperuser` produces an `is_staff` and `is_superuser` account, which is
required for dashboard access.

> Keep `DEBUG=True` locally. With `DEBUG=False`, Django does not serve
> `MEDIA_URL` files, and the email backend switches from console to SMTP.

---

## Environment Variables

`config/settings.py` reads these through `python-decouple`. Only `SECRET_KEY`
has an insecure development fallback; set everything explicitly in production.

| Variable | Default | Purpose |
| --- | --- | --- |
| `SECRET_KEY` | insecure dev key | Django cryptographic signing |
| `DEBUG` | `False` | Debug mode; `True` for local development |
| `ALLOWED_HOSTS` | `devallix.vercel.app,localhost,127.0.0.1` | Comma-separated allowed hosts |
| `DB_ENGINE` | `django.db.backends.sqlite3` | Database backend |
| `DB_NAME` | `db.sqlite3` | Database name or absolute path |
| `DB_USER` | empty | Database user |
| `DB_PASSWORD` | empty | Database password |
| `DB_HOST` | empty | Database host |
| `DB_PORT` | empty | Database port |
| `EMAIL_BACKEND` | console in DEBUG, SMTP otherwise | Email backend |
| `EMAIL_HOST` | `smtp.mail.yahoo.com` | SMTP host |
| `EMAIL_PORT` | `465` | SMTP port |
| `EMAIL_USE_SSL` | `True` | SMTP SSL |
| `EMAIL_USE_TLS` | `False` | SMTP TLS |
| `EMAIL_HOST_USER` | empty | SMTP username |
| `EMAIL_HOST_PASSWORD` | empty | SMTP password |
| `EMAIL_TIMEOUT` | `10` | SMTP timeout in seconds |
| `DEFAULT_FROM_EMAIL` | `EMAIL_HOST_USER` or `noreply@devportfolio.com` | Sender address |
| `CORS_ALLOWED_ORIGINS` | `http://localhost:3000,http://127.0.0.1:3000` | Comma-separated CORS origins |

SQLite names are normalized to an absolute path so the web worker and console
use the same file.

---

## Project Structure

```
manage.py
requirements.txt
.env                      local environment (never committed)
db.sqlite3                local SQLite database
config/                   settings, root URLs, WSGI/ASGI
apps/
  accounts/               custom user, profiles, auth flows
  core/                   home, about, skills, legal, settings, favicon
  portfolio/              technologies, skill categories, skills
  desktop_apps/           apps, versions, screenshots, FAQs, downloads
  web_projects/           web projects and galleries
  mobile_apps/            mobile applications
  graphic_design/         design projects
  blog/                   categories, tags, posts, comments
  contact/                contact form and stored messages
  testimonials/           client testimonials
  newsletter/             subscribers and newsletters
  downloads/              download event log
  dashboard/              staff-only CMS
templates/                all HTML templates
static/css|js|images/     source assets
media/                    runtime uploads
```

The top-level folders `accounts/`, `blog/`, `contact/`, `core/`, `dashboard/`,
`desktop_apps/`, `downloads/`, `newsletter/`, `portfolio/`, `testimonials/`,
and `web_projects/` are empty legacy scaffolding and are **not** installed.
The active code lives under `apps/`.

---

## Key Routes

| Area | Path |
| --- | --- |
| Home | `/` |
| About / Skills | `/about/`, `/skills/` |
| Portfolio hub | `/portfolio/` |
| Desktop apps | `/desktop-apps/`, `/desktop-apps/<slug>/` |
| Desktop app download | `/desktop-apps/<slug>/download/` |
| Web projects | `/web-apps/`, `/web-apps/<slug>/` |
| Mobile apps | `/mobile-apps/`, `/mobile-apps/<slug>/` |
| Graphic design | `/graphic-design/`, `/graphic-design/<slug>/` |
| Blog | `/blog/`, `/blog/<slug>/`, `/blog/category/<slug>/`, `/blog/tag/<slug>/` |
| Contact | `/contact/` |
| Testimonials | `/testimonials/` |
| Newsletter | `/newsletter/subscribe/` |
| Accounts | `/accounts/login/`, `/accounts/logout/`, `/accounts/profile/` |
| Dashboard | `/dashboard/` (staff only) |
| Admin | `/admin/` |

---

## How Content Works

### Desktop app downloads

`DesktopApplication` stores `installer_url` and optional `zip_url` instead of
uploaded binaries. The download route:

1. Finds the published app.
2. Records a `Download` row with IP, user agent, and the authenticated user (if
   any).
3. Increments `download_count`.
4. Redirects to the external URL.

If neither URL is set, it redirects back to the app detail page. Host the actual
files on GitHub Releases, S3, Dropbox, or a similar service.

### Contact messages

Submissions are validated, saved as `ContactMessage` with a `unread` status and
the sender's IP address, and emailed to the address configured in Site Settings
(falling back to `DEFAULT_FROM_EMAIL`). The sender's address is set as the
`Reply-To`, so replying goes straight back to them. If SMTP delivery fails the
message is still stored and the visitor sees a warning instead of a false
success message. Staff read, mark replied, archive, or delete messages from
`/dashboard/messages/`.

### Newsletter

`POST /newsletter/subscribe/` creates the subscriber or reports that the email
is already subscribed, then redirects back to the referring page. Staff can
review and export the list from `/dashboard/subscribers/`.

### Site settings

`SiteSettings` is a singleton edited at `/dashboard/site-settings/`. It controls
the site name, tagline, logo, favicon, hero copy, about image, footer text,
contact details, social URLs, SEO metadata, Open Graph image, and analytics
snippet.

---

## Dashboard Access and Permissions

- All dashboard views require an authenticated **staff** user
  (`is_staff=True`).
- Staff-only pages are protected by `LoginRequiredMixin` + `UserPassesTestMixin`.
- Public login redirects already-authenticated users to the dashboard.
- Logout is POST-only.
- The Django admin is available at `/admin/`, but no content models are
  registered under `apps/`; content is managed through `/dashboard/` instead.

---

## Static and Media Files

- Source assets: `static/` (`STATICFILES_DIRS`).
- Collected output: `staticfiles/` (`STATIC_ROOT`).
- Uploads: `media/` (`MEDIA_ROOT`), served by Django only when `DEBUG=True`.
- WhiteNoise serves compressed, hashed static files in production.

Run this during deployment or whenever static files change:

```bash
python manage.py collectstatic --noinput
```

---

## Deployment

Typical production setup:

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
gunicorn config.wsgi:application
```

Checklist:

1. Set `DEBUG=False`.
2. Set a strong `SECRET_KEY`.
3. Set `ALLOWED_HOSTS` to your domain(s).
4. Configure the database (`DB_*`) if not using SQLite.
5. Configure SMTP (`EMAIL_*`) for password-reset email.
6. Run migrations and `collectstatic` in the release step.
7. Serve `media/` from the web server, a CDN, or object storage. On ephemeral
   hosts (for example serverless platforms), local `media/` does not persist -
   use external storage and update `MEDIA_URL`.
8. Add `CSRF_TRUSTED_ORIGINS` in settings if the site is served over HTTPS from
   a proxy or platform domain.

The default `ALLOWED_HOSTS` includes `devallix.vercel.app`, matching the
project's configured host.

---

## Verification

Run these before shipping:

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py collectstatic --noinput
```

The project was verified with:

- Django system check: 0 issues.
- Migration check: no pending changes.
- All 67 templates compiled through the template loader.
- Public smoke tests (home, about, skills, portfolio, blog, contact,
  testimonials, all list pages, representative detail pages): HTTP 200.
- Authenticated smoke tests (profile, profile edit, password change, dashboard
  home, content lists, app create/detail, messages, site settings): HTTP 200.

Manual responsive review is recommended at **375, 480, 768, 820, and 992 px**.

---

## Known Issues

These are verified and documented rather than hidden:

1. `/downloads/` returns a template error - `downloads/download_list.html` is
   missing. Download data is still available in the dashboard.
2. `/newsletter/subscribe/` works for POST requests but a direct GET hits a
   missing `newsletter/subscribe.html` template.
3. Web project technology filtering references `Technology.slug`, which does
   not exist, so that filter does not work.
4. Public registration is not exposed (view/form exist, but no URL or template).
5. Blog comments render when approved, but there is no submission endpoint.
6. No `admin.py` modules exist under `apps/`, so `/admin/` exposes no content
   models; use the custom dashboard.
7. `tests.py` files are Django stubs; there is no automated test suite.
8. Local `media/` storage needs replacement on ephemeral hosting.

See [plan.md](plan.md) for the full list and the roadmap.

---

## Troubleshooting

**Static files look broken with `DEBUG=False`.**
Run `python manage.py collectstatic --noinput`. WhiteNoise only serves collected
files.

**Uploaded images do not load in production.**
Django does not serve `media/` outside debug. Configure the web server, CDN, or
object storage.

**Dashboard returns 403.**
The account must have `is_staff=True`. Use `createsuperuser` or update the user
in the shell.

**Password-reset email does not arrive locally.**
That is expected: `DEBUG=True` uses the console email backend. Check the
terminal output.

**Email fails in production with Gmail (`535-5.7.8 Username and Password not accepted`).**
Gmail no longer accepts your normal account password over SMTP. Enable 2-Step
Verification on the Google account, create an App Password at
<https://myaccount.google.com/apppasswords>, and set
`EMAIL_HOST_PASSWORD` to that 16-character password. Do not wrap the value in
quotes in a hosting dashboard (decouple only strips quotes found in `.env`
files). Use `EMAIL_PORT=587` with `EMAIL_USE_TLS=True`, or `465` with
`EMAIL_USE_SSL=True` — never both. Redeploy after changing environment
variables, then verify with:

```bash
python manage.py sendtestemail you@example.com
```

**Database seems empty after deploy.**
SQLite paths are normalized to absolute paths; make sure the deployed working
directory and `DB_NAME` point at the same persistent file, or switch to
PostgreSQL.

**Large uploads fail.**
Upload limits are 50 MB (`FILE_UPLOAD_MAX_MEMORY_SIZE` and
`DATA_UPLOAD_MAX_MEMORY_SIZE`). Prefer external URLs for installers.

---

## Credits

Built with Django, Bootstrap, Font Awesome, AOS, Swiper, Chart.js, and the
Inter and JetBrains Mono typefaces. Icons and fonts are served from public
CDNs, so an internet connection is required for the full visual experience.

## License

No license file is included in this repository. Add one before redistributing
or reusing the code publicly.
