# NavPMS — Project Management System

A **multi-tenant Project Management System** built with **Django 5.1** (backend) and **Tailwind CSS + HTMX**
(frontend). It ships a clean, fully-responsive, blue/white SaaS dashboard with a live layout **Customizer**
(light/dark, vertical/horizontal/detached, boxed/fluid, RTL, sidebar variants, preloader), row-level
multi-tenancy, full authentication & user management, and a reference "Project Dashboard".

This release delivers the complete **Foundation** (multi-tenancy, authentication, user/role management, themed
dashboard) and **Modules 0–7** end-to-end — Tenant & Subscription, Project Initiation & Charter, Project
Planning & Scheduling, Resource, Cost & Budget, Risk & Issue, Quality, and Scope & Requirements Management
(all five sub-modules each) — plus a lightweight **Workspace** (Projects / Tasks / Meetings / Tickets / Invoices)
that powers the dashboard with real seeded data. The remaining 13 modules from `ProjectManagementSystem.md`
appear in the sidebar as navigable **"on the roadmap"** placeholders and are generated on demand by the
`/next-module` Claude Code skill.

---

## Table of Contents
1. [Tech Stack](#tech-stack)
2. [Features](#features)
3. [Project Structure](#project-structure)
4. [Quick Start (Windows + XAMPP)](#quick-start-windows--xampp)
5. [Environment Variables](#environment-variables)
6. [Management Commands](#management-commands)
7. [Seeded Demo Data](#seeded-demo-data)
8. [Dashboard & Layout Customizer](#dashboard--layout-customizer)
9. [Module 0 — Tenant & Subscription Management](#module-0--tenant--subscription-management)
10. [Workspace (Projects demo)](#workspace-projects-demo)
11. [Module Roadmap (0–20)](#module-roadmap-020)
12. [Routes / URL Map](#routes--url-map)
13. [Multi-Tenancy Model](#multi-tenancy-model)
14. [Security Notes](#security-notes)
15. [Developer Tooling (Claude Code)](#developer-tooling-claude-code)
16. [Browser Compatibility](#browser-compatibility)
17. [Roadmap](#roadmap)

---

## Tech Stack

| Layer | Choice |
|------|--------|
| Backend | Django 5.1 (function-based views, `@login_required`) |
| Auth | Custom `User` (`accounts.User`) extending `AbstractUser`; login by **username or email** |
| Database | MySQL / MariaDB (XAMPP) via **PyMySQL** (installed as the `MySQLdb` shim) |
| Frontend | **Tailwind CSS** (Play CDN) + **HTMX** + **Chart.js 4** + **Lucide** icons |
| Templates | Server-rendered Django templates extending a single `base.html` + a shared design system in `static/css/theme.css` |
| Config | `python-dotenv` (`.env`) |
| Seeding | Faker (single idempotent `seed_demo` command) |
| Images | Pillow (avatars, logos, favicons) |
| Billing | **Simulated** — plans, subscriptions, invoices, and mock `PaymentMethod`s (no real payment gateway) |

> No Node/npm build step (Tailwind via Play CDN). No Bootstrap, no jQuery, no SPA framework.

---

## Features

### Platform foundation
- **Multi-tenancy** — shared-schema, **row-level isolation**. Every tenant-scoped record carries a `tenant` FK;
  `apps.core.middleware.TenantMiddleware` sets `request.tenant` from the logged-in user, and every view filters
  `Model.objects.filter(tenant=request.tenant)`.
- **Authentication** — login (username **or** email), self-service registration (= tenant onboarding: creates a
  Tenant + admin User + Administrator role + trial Subscription + Branding), forgot/reset password, logout.
- **User management** — users list (search + role/status filters + pagination), email **invitations** (UUID
  token, expiry, accept flow), edit, activate/deactivate, delete; **roles & permissions** CRUD; **user profile**
  with avatar upload, change password, and per-user UI preferences.
- **Audit log** — tenant-scoped activity trail (`core.AuditLog`).

### Customizable dashboard
All toggles live in the right-hand **Customizer** and persist in `localStorage` **and** server-side per user
(`accounts.UserPreference`): **Vertical · Horizontal · Detached** layouts · **Light & Dark** modes ·
**Fluid & Boxed** width · **Fixed & Scrollable** positions · **Light & Dark** topbars · Sidebars
(**Default · Compact · Small-Icon · Icon-Hovered**, **Light · Colored · Dark**) · **LTR & RTL** · **Preloader**.

The reference **Project Dashboard** shows KPI cards, a Projects-Overview donut, an Income-vs-Expense area chart
(Chart.js), My Tasks, My Meetings, an Invoice-Overview bar breakdown, and Open Tickets — all tenant-scoped.

### Module 0 — Tenant & Subscription Management (complete)
Tenant **Onboarding** · **Subscription & Billing** (plans, subscriptions, invoices, mock payment methods) ·
**Isolation & Security** · **Custom Branding** (logo/favicon/colors/white-label) · **Health Monitoring**
(usage metering + system alerts). Full CRUD on every list page.

### Module 1 — Project Initiation & Charter (complete)
**Project Request & Intake** · **Business Case & Feasibility** (ROI / payback / go-no_go-hold) · **Project
Charter Authoring** (sponsor / PM / objectives) · **Stakeholder Identification & Analysis**
(influence / interest / engagement) · **Project Kickoff & Launch**. Models: `ProjectRequest` (`REQ-#####`),
`BusinessCase` (`BC-#####`), `ProjectCharter` (`CHTR-#####`), `Stakeholder`, `KickoffTask`.

### Module 2 — Project Planning & Scheduling (complete)
**Work Breakdown Structure (WBS)** · **Task Sequencing & Dependency Mapping** (FS/SS/FF/SF + lag) · **Duration
& Effort Estimation** (analogous / parametric / bottom-up / three-point) · **Milestone & Phase-Gate Definition** ·
**Schedule Baseline & Version Control**. Models: `WorkPackage`, `ScheduleTask`, `TaskDependency`, `Milestone`,
`ScheduleBaseline`.

### Module 3 — Resource Management (complete)
**Resource Pool & Skills Inventory** · **Resource Allocation & Leveling** (over-allocation flagging) · **Team
Assembly & Role Assignment** · **Resource Forecasting & Demand Planning** (demand vs capacity gap) · **Time
Tracking & Timesheets**. Models: `Resource`, `Skill`, `Allocation`, `TeamAssignment`, `DemandForecast`,
`TimeEntry` (`TE-#####`).

### Module 4 — Cost & Budget Management (complete)
**Budget Planning & Estimation** · **Cost Baseline & Control Accounts** (EVM: BAC / EV / AC / CPI) · **Expense
Tracking & Commitments** · **Forecasting & EAC** (BAC / EAC / VAC) · **Change Control & Budget Revisions**.
Models: `Budget` (`BUD-#####`), `ControlAccount`, `Expense` (`EXP-#####`), `CostForecast`, `BudgetChange` (`BCR-#####`).

### Module 5 — Risk & Issue Management (complete)
**Risk Identification & Register** · **Qualitative & Quantitative Analysis** (EMV) · **Risk Response Planning**
(avoid/transfer/mitigate/accept/escalate) · **Issue Logging & Escalation** · **Risk Monitoring & Reporting**.
Models: `Risk` (`RSK-#####`), `RiskAnalysis`, `RiskResponse`, `Issue` (`ISS-#####`), `RiskReview`.

### Module 6 — Quality Management (complete)
**Quality Planning & Standards** · **Quality Assurance (QA)** · **Quality Control (QC) & Inspections** ·
**Continuous Improvement** · **Deliverable Acceptance & Sign-off**. Models: `QualityStandard`, `QualityAudit`
(`QA-#####`), `Inspection` (`QC-#####`), `ImprovementAction` (`CI-#####`), `DeliverableSignoff` (`SO-#####`).

### Module 7 — Scope & Requirements Management (complete)
**Requirements Elicitation** (MoSCoW) · **Documentation & Traceability** · **Scope Definition & Boundaries** ·
**Change Request Management** · **Scope Verification & Control** (scope-creep flag). Models: `Requirement`
(`RQ-#####`), `RequirementTrace`, `ScopeStatement` (`SCP-#####`), `ChangeRequest` (`CR-#####`), `ScopeVerification` (`SV-#####`).

---

## Project Structure

```
NavProjectManagementSystem/
├── apps/
│   ├── core/                 # Tenant; abstract TimeStampedModel/TenantScopedModel; AuditLog;
│   │                         # TenantMiddleware; navigation.py (Modules 0–20 + LIVE_LINKS);
│   │                         # context_processors (nav + UI prefs); module_placeholder + audit_log views
│   ├── accounts/             # Custom User, Role, UserInvite, UserPreference; EmailOrUsername backend;
│   │                         # auth (login/register/logout/password-reset/accept-invite),
│   │                         # user mgmt, role CRUD, profile, change-password, preferences
│   ├── tenants/              # Module 0: Plan, Subscription, Invoice (INV-#####), PaymentMethod,
│   │                         # UsageMetric, BrandingSettings, SystemAlert + onboarding/subscription/
│   │                         # plans/invoices/payment-methods/isolation-security/branding/health/usage
│   ├── projects/             # Workspace demo (powers the dashboard): Project, Task, Meeting, Ticket,
│   │                         # ProjectInvoice (PINV-#####), FinancialSnapshot — full CRUD
│   ├── dashboard/            # Aggregation view only (no models): KPIs + Chart.js feeds
│   ├── initiation/           # Module 1: ProjectRequest, BusinessCase, ProjectCharter, Stakeholder, KickoffTask
│   ├── planning/             # Module 2: WorkPackage(WBS), ScheduleTask, TaskDependency, Milestone, ScheduleBaseline
│   ├── resources/            # Module 3: Resource, Skill, Allocation, TeamAssignment, DemandForecast, TimeEntry
│   ├── budgeting/            # Module 4: Budget, ControlAccount, Expense, CostForecast, BudgetChange
│   ├── risks/                # Module 5: Risk, RiskAnalysis, RiskResponse, Issue, RiskReview
│   ├── quality/              # Module 6: QualityStandard, QualityAudit, Inspection, ImprovementAction, DeliverableSignoff
│   └── scope/                # Module 7: Requirement, RequirementTrace, ScopeStatement, ChangeRequest, ScopeVerification
├── config/                   # settings.py (reads .env), urls.py, wsgi.py, asgi.py,
│                             # __init__.py (PyMySQL + MariaDB-10.4 compatibility shim)
├── templates/
│   ├── base.html             # App shell: topbar + sidebar + customizer + preloader + all layout toggles
│   ├── partials/             # sidebar (full 0–20 nav), topbar, footer, customizer, messages
│   ├── auth/                 # login, register, forgot, reset(+done/complete), accept_invite (+ _auth_base)
│   ├── dashboard/index.html  # Reference "Project Dashboard"
│   ├── accounts/             # user_list/detail/form/invite, role_list/form, profile/edit, change_password
│   ├── tenants/              # onboarding, subscription, plans, invoices, payment-methods,
│   │                         # isolation_security, branding, health, usage
│   ├── projects/             # project/task/meeting/ticket/invoice list+detail+form
│   ├── initiation/           # request/businesscase/charter/stakeholder/kickoff list+detail+form
│   ├── planning/             # workpackage/task/dependency/milestone/baseline list+detail+form
│   ├── resources/            # skill/resource/allocation/assignment/forecast/timeentry list+detail+form
│   ├── budgeting/            # budget/controlaccount/expense/forecast/change list+detail+form
│   ├── risks/                # risk/analysis/response/issue/review list+detail+form
│   ├── quality/              # standard/audit/inspection/improvement/signoff list+detail+form
│   ├── scope/                # requirement/trace/statement/changerequest/verification list+detail+form
│   └── core/                 # module_placeholder (roadmap page), audit_log
├── static/
│   ├── css/  theme.css       # Blue/white design system (cards, badges, tables, forms, dark mode, RTL)
│   └── js/   layout.js       # Customizer + theme persistence + preloader
│           charts.js         # Chart.js init (donut + area) from the dashboard JSON contract
├── .claude/                  # Project rules (CLAUDE.md), skills, subagents, task notes
├── .env / .env.example       # Local environment (.env is gitignored)
├── manage.py
├── requirements.txt
├── ProjectManagementSystem.md  # The full 0–20 module roadmap spec
└── README.md
```

---

## Quick Start (Windows + XAMPP)

> Prereqs: **Python 3.10+**, XAMPP with **MySQL/MariaDB** running on port 3306. (Apache is not required —
> Django serves the app.)

```powershell
# 1. Create the database (NavPMS uses its OWN database — do not reuse a name another app owns)
#    phpMyAdmin -> New -> name: nav_pms -> Collation: utf8mb4_unicode_ci
#    or via CLI:
& "C:\xampp\mysql\bin\mysql.exe" -u root -e "CREATE DATABASE IF NOT EXISTS nav_pms CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# 2. Create + activate a virtualenv
python -m venv venv
.\venv\Scripts\Activate.ps1

# 3. Install dependencies
python -m pip install -r requirements.txt

# 4. Copy the env template (or keep the supplied .env)
Copy-Item .env.example .env        # then edit if your MySQL user/password differ

# 5. Migrate
python manage.py migrate

# 6. Seed demo data (plans + 2 tenants + users + subscriptions + invoices + projects/tasks/…)
python manage.py seed_demo

# 7. Run the dev server
python manage.py runserver
```

Open **http://127.0.0.1:8000/** → you'll be redirected to **`/login/`**. Sign in with a seeded **tenant admin**
(below).

> ⚠️ The Django superuser (`admin`) has `tenant=None`, so module data is **hidden** for it by design. Log in as a
> **tenant admin** (e.g. `admin_acme`) to see populated data.

---

## Environment Variables

All values are read from `.env` via `python-dotenv`. Defaults assume XAMPP (MySQL user `root`, empty password).

| Variable | Default | Notes |
|----------|---------|-------|
| `SECRET_KEY` | dev placeholder | Replace before any deploy. |
| `DEBUG` | `True` | Set `False` for production. |
| `ALLOWED_HOSTS` | `127.0.0.1,localhost` | Comma-separated. |
| `DB_ENGINE` | `django.db.backends.mysql` | |
| `DB_NAME` | `nav_pms` | Dedicated DB — create it first. |
| `DB_USER` | `root` | |
| `DB_PASSWORD` | _(empty)_ | Default XAMPP MySQL has no password. |
| `DB_HOST` | `127.0.0.1` | |
| `DB_PORT` | `3306` | |
| `EMAIL_BACKEND` | console | Dev: invitation/reset emails print to the terminal. |
| `DEFAULT_FROM_EMAIL` | `NavPMS <no-reply@navpms.local>` | |
| `EMAIL_HOST` / `EMAIL_PORT` / `EMAIL_HOST_USER` / `EMAIL_HOST_PASSWORD` / `EMAIL_USE_TLS` | localhost / 25 / — / — / False | Used only with a real SMTP backend. |
| `SITE_NAME` | `NavPMS` | Shown in titles / topbar. |
| `SITE_URL` | `http://127.0.0.1:8000` | Used to build invite/reset links. |

---

## Management Commands

| Command | What it does |
|---------|--------------|
| `python manage.py migrate` | Apply migrations to `nav_pms`. |
| `python manage.py seed_demo` | **Idempotent** demo seeder — plans, tenants, users, roles, subscriptions, invoices, branding, usage, alerts, projects/tasks/meetings/tickets/invoices, 12-month financial snapshots, and audit logs. Prints login credentials on completion. |
| `python manage.py seed_demo --flush` | Wipe and re-seed demo data. |
| `python manage.py seed_initiation` | **Idempotent** Module 1 seeder (requests, business cases, charters, stakeholders, kickoff tasks) for both tenants. Run after `seed_demo`. |
| `python manage.py seed_planning` | **Idempotent** Module 2 seeder (work packages, schedule tasks, dependencies, milestones, baselines). |
| `python manage.py seed_resources` | **Idempotent** Module 3 seeder (skills, resources, allocations, team assignments, demand forecasts, time entries). |
| `python manage.py seed_budgeting` | **Idempotent** Module 4 seeder (budgets, control accounts, expenses, cost forecasts, budget changes). |
| `python manage.py seed_risks` | **Idempotent** Module 5 seeder (risks, analyses, responses, issues, risk reviews). |
| `python manage.py seed_quality` | **Idempotent** Module 6 seeder (quality standards, audits, inspections, improvement actions, deliverable sign-offs). |
| `python manage.py seed_scope` | **Idempotent** Module 7 seeder (requirements, traces, scope statements, change requests, scope verifications). |
| `python manage.py createsuperuser` | Optional cross-tenant Django admin (`tenant=None`). |
| `python manage.py runserver` | Start the dev server on `127.0.0.1:8000`. |

> `seed_demo` is safe to run repeatedly — it guards each tenant with an existence check and skips already-seeded
> data (no duplicates). Use `--flush` to rebuild from scratch.

---

## Seeded Demo Data

### Plans (global, `tenant=None`)
**Starter**, **Professional**, and **Enterprise** (monthly/yearly pricing, seat/project/storage limits).

### Tenants & login credentials
All seeded users share the password **`password123`**.

| Tenant | Slug | Subscription | Tenant-admin username |
|--------|------|--------------|-----------------------|
| Acme Corp | `acme` | Professional (active) | `admin_acme` |
| Globex Inc | `globex` | Starter (trialing) | `admin_globex` |

The Django **superuser** is `admin` / `admin123` (`tenant=None` → module data hidden by design).

### Per tenant
Each tenant additionally gets: 3–6 Faker member users; roles (Administrator, Project Manager, Member, Client);
a Subscription; a handful of subscription **Invoices** (`INV-#####`, mixed statuses incl. overdue); a mock
PaymentMethod; usage metrics (users / storage / projects with limits); BrandingSettings; system alerts (mixed
severity); **5–8 Projects** (mixed status/progress/budget), each with several **Tasks**; **Meetings**;
**Tickets**; **ProjectInvoices** (`PINV-#####`); **12 monthly FinancialSnapshots** (income vs expense — feeds the
dashboard chart); and audit-log entries.

### Snapshot after `seed_demo` (2 tenants)
~9 users · 3 plans · 2 subscriptions · 10 subscription invoices · 13 projects · 77 tasks · 87 tickets ·
64 project invoices · 24 financial snapshots (12/tenant) · plus meetings, usage metrics, branding, alerts, and
audit logs. (Exact counts vary slightly because Faker randomizes within ranges.)

---

## Dashboard & Layout Customizer

The shell (`templates/base.html` + `static/js/layout.js`) implements **every** requested layout feature, driven
by `<html>`/`<body>` data-attributes (seeded server-side from the user's `UserPreference`, overridable live via
the Customizer and persisted to `localStorage`):

- **Layout:** Vertical · Horizontal · Detached
- **Theme:** Light · Dark (Tailwind `darkMode: 'class'`)
- **Width:** Fluid · Boxed   ·   **Position:** Fixed · Scrollable
- **Topbar:** Light · Dark
- **Sidebar size:** Default · Compact · Small-Icon · Icon-Hovered   ·   **Sidebar color:** Light · Colored · Dark
- **Direction:** LTR · RTL   ·   **Preloader:** on / off

The reference dashboard (`templates/dashboard/index.html`) renders: KPI stat cards (Total Projects, Active Tasks,
Overdue Invoices, Team Members), a **Projects Overview** doughnut, an **Income vs Expense** area chart, **My
Tasks**, **My Meetings**, an **Invoice Overview** colored-bar breakdown, and **Open Tickets**.

---

## Module 0 — Tenant & Subscription Management

| Sub-module | Page(s) | Backing models |
|------------|---------|----------------|
| Tenant Onboarding | `/tenants/onboarding/` | `Tenant`, `BrandingSettings`, `Subscription` |
| Subscription & Billing | `/tenants/subscription/`, `/tenants/plans/…`, `/tenants/invoices/…`, `/tenants/payment-methods/…` | `Plan`, `Subscription`, `Invoice` (`INV-#####`), `PaymentMethod` (mock) |
| Tenant Isolation & Security | `/tenants/isolation-security/` | tenant model + security `SystemAlert`s + audit summary |
| Custom Branding | `/tenants/branding/` | `BrandingSettings` (logo/favicon/colors/white-label) |
| Tenant Health Monitoring | `/tenants/health/`, `/tenants/usage/` | `UsageMetric`, `SystemAlert` |

Every list page has search + filters + pagination and a full Actions column (view / edit / delete). Invoices
support a status-gated **Mark as paid** action. Plan create/edit/delete is gated to staff or tenant admins
(`_can_manage_plans`).

---

## Workspace (Projects demo)

A lightweight `projects` app provides real, tenant-scoped CRUD that populates the dashboard:

| Entity | URL prefix | Notes |
|--------|-----------|-------|
| Projects | `/projects/projects/` | status · priority · progress · budget/spent · owner |
| Tasks | `/projects/tasks/` | status · priority · assignee · due date |
| Meetings | `/projects/meetings/` | type · organizer · scheduled-for |
| Tickets | `/projects/tickets/` | status · category · priority · requester/assignee |
| Invoices | `/projects/invoices/` | client billing (`PINV-#####`), status incl. partially-paid/overdue |

`FinancialSnapshot` (12 months/tenant) is seed-only and feeds the Income-vs-Expense chart.

---

## Module Roadmap (0–20)

`ProjectManagementSystem.md` defines 21 modules. Modules 0–7 are **complete**; Modules 8–20 are sidebar
**placeholders** today and are scaffolded on demand by the `/next-module` skill (one Django app per module, built
from the `apps/tenants` reference pattern).

| # | Module | Status |
|---|--------|--------|
| 0 | Tenant & Subscription Management | ✅ Complete (`apps/tenants`) |
| 1 | Project Initiation & Charter | ✅ Complete (`apps/initiation`) |
| 2 | Project Planning & Scheduling | ✅ Complete (`apps/planning`) |
| 3 | Resource Management | ✅ Complete (`apps/resources`) |
| 4 | Cost & Budget Management | ✅ Complete (`apps/budgeting`) |
| 5 | Risk & Issue Management | ✅ Complete (`apps/risks`) |
| 6 | Quality Management | ✅ Complete (`apps/quality`) |
| 7 | Scope & Requirements Management | ✅ Complete (`apps/scope`) |
| 8 | Task & Work Management | 🗺️ Roadmap → `apps/work` |
| 9 | Collaboration & Communication | 🗺️ Roadmap → `apps/collaboration` |
| 10 | Document & Knowledge Management | 🗺️ Roadmap → `apps/documents` |
| 11 | Time & Attendance Tracking | 🗺️ Roadmap → `apps/timesheets` |
| 12 | Portfolio & Program Management | 🗺️ Roadmap → `apps/portfolio` |
| 13 | Agile & Scrum Management | 🗺️ Roadmap → `apps/agile` |
| 14 | Client & External Collaboration | 🗺️ Roadmap → `apps/clients` |
| 15 | Financial & Billing Management | 🗺️ Roadmap → `apps/finance` |
| 16 | Reporting & Business Intelligence | 🗺️ Roadmap → `apps/reporting` |
| 17 | Workflow & Automation | 🗺️ Roadmap → `apps/automation` |
| 18 | Integration & API Hub | 🗺️ Roadmap → `apps/integrations` |
| 19 | Master Data & Configuration | 🗺️ Roadmap → `apps/masterdata` |
| 20 | System Administration & Security | 🗺️ Roadmap → `apps/administration` |

Build the next one with: **`/next-module`** (auto-detects the lowest unbuilt module) or **`/next-module 8`** /
**`/next-module "Task & Work Management"`**.

---

## Routes / URL Map

| Area | Prefix | Examples |
|------|--------|----------|
| Dashboard | `/` | `/` (login required) |
| Auth | `/` | `/login/`, `/register/`, `/logout/`, `/password-reset/`, `/invite/accept/<token>/` |
| User & role mgmt | `/` | `/users/`, `/users/invite/`, `/users/<pk>/edit/`, `/roles/`, `/profile/`, `/profile/password/` |
| Module 0 | `/tenants/` | `/tenants/onboarding/`, `/tenants/subscription/`, `/tenants/invoices/`, `/tenants/branding/`, `/tenants/health/` |
| Workspace | `/projects/` | `/projects/projects/`, `/projects/tasks/`, `/projects/tickets/`, `/projects/invoices/` |
| Module 1 | `/initiation/` | `/initiation/requests/`, `/initiation/business-cases/`, `/initiation/charters/`, `/initiation/stakeholders/`, `/initiation/kickoff/` |
| Module 2 | `/planning/` | `/planning/work-packages/`, `/planning/tasks/`, `/planning/dependencies/`, `/planning/milestones/`, `/planning/baselines/` |
| Module 3 | `/resources/` | `/resources/resources/`, `/resources/skills/`, `/resources/allocations/`, `/resources/assignments/`, `/resources/forecasts/`, `/resources/time-entries/` |
| Module 4 | `/budgeting/` | `/budgeting/budgets/`, `/budgeting/control-accounts/`, `/budgeting/expenses/`, `/budgeting/forecasts/`, `/budgeting/changes/` |
| Module 5 | `/risks/` | `/risks/register/`, `/risks/analysis/`, `/risks/responses/`, `/risks/issues/`, `/risks/reviews/` |
| Module 6 | `/quality/` | `/quality/standards/`, `/quality/audits/`, `/quality/inspections/`, `/quality/improvements/`, `/quality/signoffs/` |
| Module 7 | `/scope/` | `/scope/requirements/`, `/scope/traces/`, `/scope/statements/`, `/scope/change-requests/`, `/scope/verifications/` |
| Roadmap placeholders | `/m/<module>/<sub>/` | e.g. `/m/task-work-management/task-board/` |
| Audit log | `/audit-log/` | tenant-scoped activity trail |
| Django admin | `/admin/` | superuser only |

---

## Multi-Tenancy Model

- **Strategy:** shared database / shared schema, **row-level isolation**. Each tenant-scoped model declares
  `tenant = models.ForeignKey('core.Tenant', on_delete=models.CASCADE, related_name=...)`.
- **Resolution:** `apps.core.middleware.TenantMiddleware` sets `request.tenant = request.user.tenant` for
  authenticated users.
- **Enforcement:** every view filters `Model.objects.filter(tenant=request.tenant)` and fetches single objects
  via `get_object_or_404(Model, pk=pk, tenant=request.tenant)` — so a tenant can never read or modify another
  tenant's rows (cross-tenant IDOR returns 404).
- **Superuser caveat:** the `admin` superuser has `tenant=None`; tenant-scoped queries return empty for it by
  design. Always use a tenant admin to view data.

---

## Security Notes

- Secrets (`SECRET_KEY`, DB/email creds) come from `.env` (gitignored); `.env.example` is the committed template.
- CSRF on every POST form (`{% csrf_token %}`); delete actions are POST-only with a confirm dialog.
- Passwords hashed with Django's PBKDF2 (`set_password` / `create_user`); invitations use single-use, expiring
  UUID tokens.
- Billing is **simulated**: `PaymentMethod` stores only mock brand/last4 — **no** real card data.
- **MariaDB 10.4 (XAMPP):** Django 5.1 officially requires MariaDB ≥ 10.5. `config/__init__.py` contains a small,
  documented compatibility shim (relaxes the version floor and disables `INSERT … RETURNING` for MariaDB < 10.5).
  The clean long-term fix is to upgrade XAMPP's MariaDB to ≥ 10.5 and remove the shim.
- For production: set `DEBUG=False`, a real `SECRET_KEY` + `ALLOWED_HOSTS`, a compiled Tailwind build (instead of
  the Play CDN), and serve static/media behind the web server.

---

## Developer Tooling (Claude Code)

The repo ships project-specific Claude Code skills and subagents under `.claude/`:

| Type | Name | Purpose |
|------|------|---------|
| Skill | `/next-module` | Scaffold & build the next module (Django app + models + CRUD + templates + seeder + nav wiring + migrations). |
| Skill | `/dump-module` | Dump one module's backend + frontend code into `temp/<NN>_<slug>.txt`. |
| Skill | `/manual-test` | Generate a senior-level manual QA / click-through test plan. |
| Skill | `/sqa-review` | Generate a comprehensive SQA report (tests, automation, code review, OWASP). |
| Agent | `code-reviewer` | Reviews uncommitted changes (correctness, multi-tenant safety, CRUD/filters). |
| Agent | `explorer` | Read-only repo map before implementing a feature. |
| Agent | `security-reviewer` | Django security review (tenant IDOR, CSRF, XSS, injection, secrets, uploads). |

Project conventions live in `.claude/CLAUDE.md` (multi-tenancy, CRUD completeness, filter rules, seed
idempotency, one-file-per-commit, PowerShell-safe shell).

---

## Browser Compatibility

Server-rendered HTML5 + CSS + vanilla JS (no SPA framework) → works in modern **Chrome**, **Firefox**, **Safari**,
**Microsoft Edge**, and other WebKit/Blink browsers on Windows, macOS, and Linux. Dark mode, RTL, and the layout
Customizer are pure CSS/JS and require no plugins.

---

## Roadmap

Modules 0–7 are complete and the foundation is production-shaped. Modules 8–20 (`ProjectManagementSystem.md`) reuse
the same multi-tenant + CRUD + dashboard patterns and are built incrementally via `/next-module`. Planned
hardening: compiled Tailwind pipeline, an automated test suite (pytest + pytest-django), real email/SMTP, and an
optional real payment gateway behind the existing simulated billing.
