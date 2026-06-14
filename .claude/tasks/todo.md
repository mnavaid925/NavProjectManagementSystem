# TODO — NavPMS Foundation + Module 0

## Status: ✅ COMPLETE & VERIFIED

Built with a parallel multi-agent workflow (7 agents, 2 bursts) after the user asked to "use more Agents".

## Orchestration prep (main loop) ✅
- [x] venv + Django 5.1.15, PyMySQL, Faker, Pillow
- [x] MySQL database (see DB note below)
- [x] `.env` (+ `.env.example`)

## Backend ✅
- [x] config/ scaffold wired to `.env` + PyMySQL + MySQL (+ MariaDB 10.4 compat shim)
- [x] core / accounts / tenants / projects / dashboard apps (models, forms, views, urls, admin)
- [x] navigation.py (full 0–20 module tree), middleware, context processors, audit log
- [x] `seed_demo` management command (idempotent — verified twice)
- [x] migrations generated + migrate + seed against `nav_pms`
- [x] `manage.py check` → 0 issues

## Frontend ✅
- [x] base.html with all layout features + partials (sidebar/topbar/footer/customizer/messages)
- [x] auth, dashboard+core, accounts, tenants (Module 0), projects templates (~57 files)
- [x] static: theme.css, layout.js (customizer + localStorage), charts.js (Chart.js)

## Verification (main loop) ✅
- [x] `manage.py check` clean
- [x] migrate + seed_demo idempotent (run 2 = no dupes)
- [x] Smoke test: **51/51 pages** return 200/302 via test client against seeded data
- [x] Live browser: dashboard renders, **both Chart.js charts drew**, tenant-aware, 112 sidebar links
- [x] Fixed bugs found in verification (see Review)

## Wrap-up ✅
- [x] README.md rewritten (setup, credentials, structure, env notes)
- [x] Review section (below)
- [x] One-file-per-commit PowerShell snippet provided to user

## Review

### What shipped
Full multi-tenant Django PMS foundation + Module 0, a customizable blue/white Tailwind+HTMX dashboard
matching the reference image, auth (login/register/forgot/invite), user & role management, profile +
UI preferences, and a sidebar exposing all 21 modules (0–20) with Module 0 live and 1–20 as roadmap
placeholders. Seeded with Faker (2 tenants, 9 users, 13 projects, 77 tasks, 87 tickets, etc.).

### Key decisions / environment findings
1. **Database collision** — the XAMPP DB named `navpms` is already owned by a *different* Nav app
   (procurement suite, ~170 tables, live data). We did NOT touch it. NavPMS uses its own DB **`nav_pms`**
   (`.env` → `DB_NAME=nav_pms`).
2. **MariaDB 10.4 vs Django 5.1** — XAMPP ships MariaDB 10.4.14; Django 5.1 needs ≥10.5. A minimal,
   documented compat shim was added to `config/__init__.py`. Long-term fix: upgrade MariaDB to ≥10.5.

### Bugs found & fixed during verification
- `apps/tenants/views.py` (onboarding): used wrong reverse accessor `tenant.projects_project_set` →
  fixed to `tenant.projects` (the model's actual `related_name`). (Caused the only 500 in the smoke test.)
- `templates/partials/sidebar.html` + `customizer.html`: multi-line `{# … #}` comments leak as visible
  text in Django → converted to `{% comment %} … {% endcomment %}`.

### Lessons (also a candidate for lessons.md)
- A `CREATE DATABASE IF NOT EXISTS` is a silent no-op when the DB already exists — always verify the DB
  is empty / belongs to this project before assuming it's "ours".
- Django `{# … #}` comments are single-line only; multi-line notes must use `{% comment %}`.
- HTTP-200 smoke tests don't catch template-comment leaks — pair them with a rendered-HTML content check.
