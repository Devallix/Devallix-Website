# Implementation Plan - Devallix Portfolio Website

**Status:** Implemented and live
**Last updated:** October 26, 2026
**Repository:** https://github.com/Devallix/Devallix-Website

This document records the full plan that was designed and implemented for the
site: the goals, the architecture, each delivery phase, the responsive
hardening pass, the verification performed, and the remaining known gaps.

---

## 1. Goals and Success Criteria

The site had to serve two audiences from a single Django codebase:

1. **Visitors** - a fast, animated, SEO-friendly portfolio that presents
   desktop apps, web projects, mobile apps, graphic design work, a blog, and a
   way to get in touch.
2. **The owner** - a private, staff-only dashboard to publish and manage every
   piece of content without touching code or the Django admin.

Success criteria:

- One consistent dark visual identity across all public pages.
- Every publishable content type is database-driven and editable from the
  dashboard (apps, projects, designs, blog posts, skills, testimonials,
  categories, and site settings).
- Desktop app downloads are tracked and redirect to externally hosted files.
- Contact messages, newsletter subscribers, and download events are captured.
- Fully usable layout from 320 px phones through large desktops.
- Static assets are production-ready (WhiteNoise, hashed/compressed files).
- Secure defaults: environment-driven secrets, staff-only dashboard, CSRF,
  password validators, POST-only logout.

**Out of scope for this phase:** payments, user-generated accounts,
multi-author workflows, and a public REST/GraphQL API.

---

## 2. Technical Stack

| Layer | Choice |
| --- | --- |
| Framework | Django 6.0 (Python 3.12+) |
| Database | SQLite by default, PostgreSQL via environment variables |
| Templates | Django template engine + Bootstrap 5.3.3 |
| Forms | django-crispy-forms + crispy-bootstrap5 |
| Styling | Custom `main.css` + `dashboard.css` design system |
| Icons | Font Awesome 6.5.1 |
| Animation | AOS (scroll reveal), custom canvas particles, CSS keyframes |
| Sliders | Swiper 11 |
| Charts | Chart.js (loaded globally for dashboard use) |
| Fonts | Inter + JetBrains Mono (Google Fonts) |
| Media | Pillow + Django `MEDIA_ROOT` |
| Static serving | WhiteNoise (`CompressedManifestStaticFilesStorage`) |
| Config | python-decouple reading `.env` |
| CORS | django-cors-headers |
| Server | Gunicorn (WSGI) |

---

## 3. Architecture

A single Django project (`config`) with 13 purpose-built apps under `apps/`.
The public site, the account area, and the dashboard are separated by URL
prefix and by access rules.

```
config/                  project settings, root URLconf, WSGI/ASGI
apps/
  accounts/              custom user, profile, auth flows
  core/                  home, about, skills, legal pages, site settings, favicon
  portfolio/             technologies, skill categories, skills, portfolio hub
  desktop_apps/          desktop applications, versions, screenshots, FAQs, downloads
  web_projects/          web projects + gallery images
  mobile_apps/           mobile applications
  graphic_design/        graphic design projects
  blog/                  categories, tags, posts, comments
  contact/               contact form + stored messages
  testimonials/          client testimonials
  newsletter/            subscribers + newsletter model
  downloads/             download event log
  dashboard/             staff-only CMS for every content type
templates/               all HTML (67 templates)
static/css|js|images     source static assets
media/                   uploaded images and resumes
```

### App responsibilities

| App | Public routes | Key models | Dashboard |
| --- | --- | --- | --- |
| `core` | `/`, `/about/`, `/skills/`, `/privacy-policy/`, `/terms/`, `/favicon.ico` | `SiteSettings` (singleton) | Site settings editor |
| `accounts` | `/accounts/login/`, `/logout/`, `/profile/`, `/profile/edit/`, password change/reset | `User`, `Profile`, `TimelineEvent` | Profile via account pages |
| `portfolio` | `/portfolio/` | `Technology`, `SkillCategory`, `Skill` | Skill CRUD |
| `desktop_apps` | `/desktop-apps/`, `/desktop-apps/category/<slug>/`, `/desktop-apps/<slug>/`, `/desktop-apps/<slug>/download/` | `DesktopApplication`, `ApplicationVersion`, `Screenshot`, `FaqItem`, `ApplicationCategory` | App, version, screenshot, category CRUD |
| `web_projects` | `/web-apps/`, `/web-apps/<slug>/` | `WebProject`, `ProjectImage` | Project CRUD |
| `mobile_apps` | `/mobile-apps/`, `/mobile-apps/<slug>/` | `MobileApp` | Mobile app CRUD |
| `graphic_design` | `/graphic-design/`, `/graphic-design/<slug>/` | `GraphicDesignProject` | Design CRUD |
| `blog` | `/blog/`, `/blog/category/<slug>/`, `/blog/tag/<slug>/`, `/blog/<slug>/` | `BlogCategory`, `Tag`, `BlogPost`, `Comment` | Post CRUD |
| `contact` | `/contact/` | `ContactMessage` | Inbox, read/replied/archive/delete |
| `testimonials` | `/testimonials/` | `Testimonial` | Testimonial CRUD |
| `newsletter` | `/newsletter/subscribe/` | `NewsletterSubscriber`, `Newsletter` | Subscriber list + CSV export |
| `downloads` | `/downloads/` | `Download` | Download statistics |
| `dashboard` | `/dashboard/...` (staff only) | - | All of the above |

### Access model

- `AUTH_USER_MODEL = accounts.User` (email is unique; includes avatar, bio,
  job title, phone, location, website, GitHub, LinkedIn, Twitter).
- `Profile` is created on demand (`get_or_create`) and stores longer bio,
  mission, vision, philosophy, counters, resume, and timeline events.
- Dashboard views inherit `LoginRequiredMixin` + `UserPassesTestMixin` and
  require `request.user.is_staff`.
- Logout is POST-only; the public login page redirects authenticated users to
  the dashboard.

---

## 4. Design System and Frontend

Defined in `static/css/main.css` and `static/css/dashboard.css`.

**Public theme**

- Near-black background (`#0F1115`), layered cards, subtle borders.
- Lime accent `#B6FF00` with cyan secondary `#00D9FF`.
- Inter for UI, JetBrains Mono for code/technical labels.
- Shared components: `.card-custom`, `.btn-primary-custom`,
  `.btn-outline-custom`, `.btn-secondary-custom`, `.badge-custom`,
  `.section-title`, `.section-subtitle`, `.divider`, `.icon-box`,
  `.glass-card`, `.hero-*`, `.service-*`, `.swiper` cards.
- Motion: AOS reveal, hero particle canvas, typing effect, animated counters,
  progress bars, hover lifts, page preloader, floating orbs.
- Chrome: fixed transparent-to-solid navbar, apps dropdown, back-to-top,
  footer with contact/social/quick links, toast-style Django messages.

**Dashboard theme**

- Separate dark palette with a fixed 260 px sidebar and 60 px sticky topbar.
- Sidebar sections: Main, Content, Engagement, Configuration.
- Stat cards, data tables, search/filter toolbars, Crispy forms, empty states.
- Chart.js is loaded in both layouts; no charts are instantiated yet, so the
  library is available for future dashboard visualizations.

**JavaScript (`static/js/main.js`, 269 lines)**

- Preloader dismissal on window load.
- Sticky navbar state on scroll.
- Back-to-top button.
- Typing headline effect.
- Counter animation triggered in view.
- Bootstrap tooltip initialization.
- Progress-bar reveal.
- Hero particle canvas (resize + mouse repulsion).
- Swiper initialization for testimonial/featured sliders.

---

## 5. Delivery Phases

### Phase 0 - Foundation

- [x] Create the `config` project and split code into `apps/`.
- [x] Environment configuration with `python-decouple`; secrets never in code.
- [x] Custom user model (`accounts.User`) before the first migration.
- [x] SQLite default with PostgreSQL support (absolute-path guard for SQLite).
- [x] Static/media configuration; WhiteNoise manifest storage.
- [x] Crispy Forms with the Bootstrap 5 pack.
- [x] CORS allow-list, 50 MB upload limits, SMTP settings.
- [x] Global `site_settings` context processor with safe fallback.
- [x] Custom favicon endpoint with uploaded-file, static, and collected
      fallbacks and a 24-hour cache header.

### Phase 1 - Public shell

- [x] `base.html` with SEO meta, Open Graph/Twitter tags, canonical URL,
      favicon, Google Fonts, Bootstrap, Font Awesome, AOS, Swiper, Chart.js.
- [x] Responsive navbar with brand, primary links, apps dropdown, and Hire Me
      CTA; animated mobile collapse panel.
- [x] Footer with brand, contact info, quick links, resources, socials, and
      newsletter form.
- [x] Shared dark design system and component library.
- [x] Preloader, toast messages, back-to-top, and scroll animations.

### Phase 2 - Core content pages

- [x] Home: hero with badges, stats, services ("What I Do"), featured/latest
      desktop apps, featured/latest web projects, featured/latest mobile apps,
      featured skills, testimonials slider, CTA, newsletter.
- [x] About: profile image, "Who I Am", feature highlights, Mission, Vision,
      Development Philosophy.
- [x] Skills: grouped by category with proficiency values.
- [x] Privacy Policy and Terms pages.
- [x] Portfolio hub linking each content vertical.

### Phase 3 - Portfolio verticals

- [x] Desktop apps: paginated list with search, category, platform, and sort;
      detail page with banner, screenshots, versions, requirements,
      installation steps, FAQs, related apps, and download action.
- [x] Web projects: paginated list with search, technology, and sort; detail
      page with gallery, tech stack, live demo/GitHub links, related projects.
- [x] Mobile apps: paginated list with search, platform, and sort; detail page
      with store links and related apps.
- [x] Graphic design: paginated list with search, category, and sort; detail
      page with image, tools, client, project link, related designs.
- [x] Shared `Technology` tags across web and mobile projects.
- [x] Slug generation on save for all content models.

### Phase 4 - Engagement

- [x] Contact page with validated form; every submission is stored with IP
      address and starts as `unread`.
- [x] Newsletter subscribe endpoint with get-or-create semantics:
      "subscribed" vs "already subscribed" feedback, redirect back to referer.
- [x] Testimonials list with star ratings, client metadata, and pagination.
- [x] Featured testimonials pulled onto the home page slider.

### Phase 5 - Blog and SEO

- [x] Post list with search, category, and tag filtering.
- [x] Category and tag archive pages with pagination.
- [x] Post detail with author card, featured image, tags, share links, related
      posts, and approved comments.
- [x] View counter incremented on each detail request.
- [x] Draft/published workflow; drafts excluded from every public query.
- [x] Per-object SEO fields (`meta_title`, `meta_description`) plus site-wide
      meta, Open Graph image, and canonical URLs.

### Phase 6 - Downloads and analytics

- [x] `installer_url` / `zip_url` fields replace stored installer binaries, so
      large files can live on GitHub Releases, S3, Dropbox, etc.
- [x] `/desktop-apps/<slug>/download/` resolves the primary URL, records a
      `Download` row (IP, user agent, user when authenticated), increments the
      app counter, then redirects externally.
- [x] Fallback redirect to the detail page if no URL is configured.
- [x] Dashboard download statistics: totals, per-app ranking, recent events.

### Phase 7 - Accounts

- [x] Login with username or email, success message, redirect to dashboard.
- [x] Logout (POST) back to home.
- [x] Profile view and edit: names, email, avatar, bio, job title, phone,
      location, website, GitHub, LinkedIn, Twitter.
- [x] Password change with success message.
- [x] Password reset request + confirm flow with email template.
- [x] Staff shortcut from the profile page to the dashboard.

### Phase 8 - Dashboard CMS

- [x] Staff-only dashboard shell with sidebar, topbar, and messages.
- [x] Overview page: counts for every content type, unread messages, active
      subscribers, recent activity, most-downloaded apps.
- [x] Full CRUD for desktop apps, versions, screenshots, web projects, mobile
      apps, graphic design, skills, blog posts, testimonials, and categories.
- [x] Multi-file screenshot upload and current-version handling.
- [x] Contact inbox with status filters and read/replied/archive/delete actions.
- [x] Subscriber list with CSV export.
- [x] Site settings editor for branding, hero, footer, social links, SEO,
      analytics, and contact details.
- [x] Search on app/project/blog lists; pagination across all lists.
- [x] Crispy Bootstrap 5 forms with consistent validation styling.

### Phase 9 - Responsive hardening

**Public site (`main.css`)**

- [x] Breakpoints at 992 px (navigation collapse), 768 px, 576 px, and 480 px.
- [x] Navbar: hamburger panel scrolls within `100dvh`, apps dropdown becomes an
      inline accordion-style menu, brand text truncates, CTA spans the panel.
- [x] Hero, services, stats, cards, testimonials, CTA, and newsletter stack and
      wrap cleanly; hero buttons go full width on phones.
- [x] List pages: filter toolbars wrap, "Showing N results" rows wrap, card
      footers and action groups wrap.
- [x] Detail pages: inline heading sizes are capped, quick-info and share rows
      wrap, breadcrumbs and badges shrink.
- [x] Account pages: login footer row wraps, profile header and action rows
      wrap.
- [x] Footer brand row and contact rows wrap; long emails/URLs break safely.
- [x] Overflow safety net: `overflow-wrap`, image `max-width: 100%`, wrapping
      pagination, `min-width: 0` on input groups and flex text columns.
- [x] Ultra-narrow (< 307 px): apps-submenu icons are hidden and item text is
      centered; header centered too.
- [x] About page on phones: "Who I Am" text, feature rows (stacked and
      centered), and Mission/Vision cards/icons are centered.
- [x] Home "What I Do" on phones: each card's top service icon is centered.

**Dashboard (`dashboard.css` + shell template)**

- [x] Off-canvas sidebar below 992 px: `min(280px, 84vw)`, `100dvh`, elevated
      `z-index`, shadow, and `translateX` transition.
- [x] Backdrop with blur, body scroll lock, and auto-close on link tap,
      backdrop click, Escape, and resize back to desktop.
- [x] Fixed content margin bug removed: `#page-content-wrapper` is always
      full-width on mobile.
- [x] Topbar title ellipsis; "View Site" label and username/chevron hide at
      small widths; avatar stays fixed-size.
- [x] Page headers, search/filter toolbars, card footers, and form action rows
      wrap.
- [x] Tables keep a 640 px minimum inside `.table-responsive` so they scroll
      instead of squashing.
- [x] Reduced card/form padding and stat/icon sizes at 768 px and 576 px.

**Responsive rules of thumb**

- Content width is never fixed; flex rows get `flex-wrap` + `gap`.
- Text containers get `min-width: 0` so ellipsis/truncation can work.
- Tables and long media scroll horizontally; the page itself never does.
- Touch targets remain at least ~40 px where controls shrink.

### Phase 10 - Security, performance, deployment readiness

- [x] Secrets and hosts read from `.env`; `DEBUG` defaults to `False`.
- [x] Password validators (similarity, minimum length, common, numeric).
- [x] CSRF middleware and POST-only destructive/auth actions.
- [x] Staff gate on every dashboard view (not merely `login_required`).
- [x] WhiteNoise compressed manifest static storage.
- [x] Safe `SiteSettings` singleton (`load()`), with a clear error if a second
      row is created manually.
- [x] Pagination on every public list (9-12 per page) and dashboard list (20).
- [x] `select_related` / `prefetch_related` on the read-heavy queries.
- [x] External download hosting keeps the repository and server light.

### Phase 11 - Verification and QA

- [x] `python manage.py check` returns 0 issues.
- [x] `python manage.py makemigrations --check --dry-run` reports no changes.
- [x] All 67 templates compile through the Django template loader.
- [x] Public smoke test: home, about, skills, portfolio, blog, contact,
      testimonials, all four list pages, and representative detail pages
      return HTTP 200.
- [x] Authenticated smoke test: profile, profile edit, password change,
      dashboard home, all content lists, app create/detail, messages, and site
      settings return HTTP 200.
- [x] CSS files checked for balanced braces after the responsive pass.
- [x] Manual responsive review at 375, 480, 768, 820, and 992 px (browser
      DevTools) is the final visual gate.

---

## 6. Data Model Summary

25 models across 12 apps:

- **Site/identity:** `SiteSettings`, `User`, `Profile`, `TimelineEvent`.
- **Skills:** `Technology`, `SkillCategory`, `Skill`.
- **Desktop apps:** `ApplicationCategory`, `DesktopApplication`,
  `ApplicationVersion`, `Screenshot`, `FaqItem`.
- **Web:** `WebProject`, `ProjectImage`.
- **Mobile:** `MobileApp`.
- **Graphic design:** `GraphicDesignProject`.
- **Blog:** `BlogCategory`, `Tag`, `BlogPost`, `Comment`.
- **Engagement:** `ContactMessage`, `Testimonial`,
  `NewsletterSubscriber`, `Newsletter`.
- **Analytics:** `Download`.

Conventions applied throughout:

- Slug auto-generated from the name/title when left blank.
- `display_order` fields drive manual ordering on listing pages.
- `featured` flags drive home-page sections.
- `published` / `status` fields hide drafts from public queries.
- `created_at` / `updated_at` timestamps on content models.
- Optional per-object SEO fields.

---

## 7. URL Map

Public:

```
/                                   home
/about/                             about
/skills/                            skills
/portfolio/                         portfolio hub
/desktop-apps/                      desktop app list (search/filter/sort)
/desktop-apps/category/<slug>/      category listing
/desktop-apps/<slug>/               app detail
/desktop-apps/<slug>/download/      tracked redirect to installer
/web-apps/                          web project list
/web-apps/<slug>/                   project detail
/mobile-apps/                       mobile app list
/mobile-apps/<slug>/                app detail
/graphic-design/                    design list
/graphic-design/<slug>/             design detail
/blog/                              post list (search/filter)
/blog/category/<slug>/              category archive
/blog/tag/<slug>/                   tag archive
/blog/<slug>/                       post detail
/contact/                           contact form
/testimonials/                      testimonials
/newsletter/subscribe/              subscribe (POST)
/privacy-policy/  /terms/           legal pages
/favicon.ico                        dynamic favicon
/accounts/...                       login, logout, profile, password flows
/admin/                             Django admin
/downloads/                         download log page
```

Dashboard (`/dashboard/...`, staff only):

```
/                          overview
/desktop-apps/             list + create/detail/edit/delete
/desktop-apps/<pk>/versions/create/
/desktop-apps/<pk>/screenshots/upload/
/web-apps/                 list + create/edit/delete
/mobile-apps/              list + create/edit/delete
/graphic-design/           list + create/edit/delete
/skills/                   list + create/edit/delete
/blog/                     list + create/edit/delete
/messages/                 inbox + detail + actions
/testimonials/             list + create/edit/delete
/subscribers/              list + CSV export
/categories/               list + create/edit/delete
/download-stats/           analytics
/site-settings/            singleton editor
```

---

## 8. Responses and Fault Handling

- Public queries always exclude drafts/unpublished rows.
- Missing objects return 404 through `get_object_or_404` / `DetailView`.
- Detail pages increment counters with `update_fields` to avoid full saves.
- Newsletter re-submission is idempotent (`get_or_create`) and reports clearly.
- Downloads without a configured URL fall back to the app detail page.
- Dashboard actions return success messages and redirect to a safe page.
- Site settings and profile objects are created on first use.
- Favicon resolves through three fallbacks before raising 404.

---

## 9. Known Gaps and Follow-ups

These are verified gaps, not planned features:

1. `/downloads/` raises `TemplateDoesNotExist` - `downloads/download_list.html`
   is missing. Download data is still available in the dashboard.
2. `/newsletter/subscribe/` only works for POST from an existing form; a direct
   GET hits the missing `newsletter/subscribe.html` template.
3. Web project technology filtering references `Technology.slug` and
   `technologies__slug`, but `Technology` has no slug field. The filter is
   effectively non-functional.
4. Public registration is not exposed: `UserRegisterView` and
   `UserRegistrationForm` exist, but there is no URL and no
   `accounts/register.html`.
5. Blog comments are modeled and approved comments render, but there is no
   comment submission endpoint.
6. None of the `apps/*` packages ship an `admin.py`, so no content models are
   registered in the Django admin. Content is managed through the custom
   dashboard by design (the empty legacy top-level app folders do include stub
   admin files, but those apps are not installed).
7. The contact form stores messages but does not email the owner; the dashboard
   inbox is the notification path.
8. Top-level folders such as `/core`, `/blog`, `/portfolio` are empty legacy
   stubs and are not in `INSTALLED_APPS`.
9. There are no real automated tests (`tests.py` files are Django stubs).
10. Uploaded media lives on local disk; serverless/ephemeral hosts need
    object storage plus a matching `MEDIA_URL`.

---

## 10. Future Roadmap

- Add the missing downloads and newsletter templates (or remove those routes).
- Fix technology filtering by adding a slug (or filtering by name/id).
- Wire blog comment submission with moderation.
- Email notification for new contact messages.
- Optional public registration or invite-only staff onboarding.
- Add automated tests for public views, dashboard permissions, and download
  tracking.
- Optimize media delivery through a CDN or object storage.
- Add structured data (JSON-LD) for projects, apps, and blog posts.
- Optional REST API for app metadata and release feeds.
