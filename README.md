# NavPMS — Project Management System

A **multi-tenant Project Management System** built with **Django** (backend) and **Tailwind CSS + HTMX**
(frontend). Clean, responsive, blue/white SaaS dashboard with a fully customizable layout. This first
release delivers the complete foundation — multi-tenancy, authentication, user management, and a
feature-rich dashboard — plus **Module 0: Tenant & Subscription Management** end-to-end. The remaining
20 modules from the product roadmap are present in the navigation as "on the roadmap" placeholders.

---

## ✨ Features

### Platform foundation
- **Multi-tenancy** — row-level isolation. Every tenant-scoped record carries a `tenant` FK; a
  `TenantMiddleware` sets `request.tenant` from the logged-in user and every query is tenant-filtered.
- **Authentication** — login (username **or** email), self-service registration (tenant onboarding),
  forgot/reset password, and email-based user invitations.
- **User management** — users list (search + role/status filters), invite, edit, activate/deactivate,
  delete; **roles & permissions**; **user profile** with avatar upload, change password, and UI preferences.
- **Audit log** — tenant-scoped activity trail.

### Customizable dashboard (all toggles live in the right-hand Customizer)
- Layouts: **Vertical · Horizontal · Detached**
- **Light & Dark** modes · **Fluid & Boxed** width · **Fixed & Scrollable** positions
- **Light & Dark** topbars · Sidebars: **Default · Compact · Small-Icon · Icon-Hovered**
- **Light & Colored** sidebars · **LTR & RTL** · **Preloader** toggle
- Preferences persist in `localStorage` **and** server-side per user (`UserPreference`).
- Reference "Project Dashboard": KPI cards, Projects Overview donut, Income vs Expense chart (Chart.js),
  My Tasks, My Meetings, Invoice Overview bars, and Open Tickets.

### Module 0 — Tenant & Subscription Management (complete)
Tenant Onboarding · Subscription & Billing (plans, subscriptions, invoices, mock payment methods) ·
Tenant Isolation & Security · Custom Branding (logo/colors/white-label) · Tenant Health Monitoring
(usage metering + system alerts).

> Modules 1–20 (Project Initiation, Planning, Resources, Cost, Risk, Quality, … System Administration)
> are listed in the sidebar and link to a roadmap placeholder page. See `ProjectManagementSystem.md`.

---

## 🧱 Tech stack

| Layer | Choice |
|-------|--------|
| Backend | Django 5.1 (custom `accounts.User`) |
| Database | MySQL / MariaDB (XAMPP) via **PyMySQL** |
| Frontend | Tailwind CSS (Play CDN) + HTMX + Chart.js + Lucide icons |
| Config | `python-dotenv` (`.env`) |
| Seed data | Faker |
| Images | Pillow |

---

## 🚀 Getting started (Windows + XAMPP)

### 1. Prerequisites
- Python 3.10+
- XAMPP running **MySQL/MariaDB** (Apache not required — Django serves the app)

### 2. Create the database
NavPMS uses its **own** database. In phpMyAdmin or the MySQL CLI:

```sql
CREATE DATABASE nav_pms CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

> ⚠️ Do **not** reuse a database name already taken by another app in your MySQL instance.

### 3. Set up the environment
```powershell
python -m venv venv
venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env      # then edit .env if your MySQL user/password differ
```
Default `.env` assumes XAMPP defaults: user `root`, empty password, host `127.0.0.1`, db `nav_pms`.

### 4. Migrate & seed
```powershell
venv\Scripts\python.exe manage.py migrate
venv\Scripts\python.exe manage.py seed_demo
```
`seed_demo` is **idempotent** — safe to re-run. Use `--flush` to rebuild demo data.

### 5. Run
```powershell
venv\Scripts\python.exe manage.py runserver
```
Open **http://127.0.0.1:8000/** → you'll be redirected to the login page.

---

## 🔑 Demo credentials

| Account | Username | Password | Notes |
|---------|----------|----------|-------|
| Tenant admin (Acme Corp) | `admin_acme` | `password123` | **Use this** to see module data |
| Tenant admin (Globex Inc) | `admin_globex` | `password123` | Second tenant |
| Django superuser | `admin` | `admin123` | `tenant=None` — module data is **hidden** by design |
| Faker members | _(printed by seeder)_ | `password123` | Regular tenant users |

> The superuser has **no tenant**, so tenant-scoped module data will not appear when logged in as `admin`.
> Always log in as a **tenant admin** to explore the app. (`/admin/` is the Django admin site.)

---

## 🗂️ Project structure

```
config/                 # Django project (settings wired to .env, PyMySQL, MySQL)
apps/
  core/                 # Tenant, base models, middleware, navigation tree, audit log, placeholders
  accounts/             # custom User, Role, UserInvite, UserPreference; auth + user mgmt + profile
  tenants/              # Module 0: Plan, Subscription, Invoice, PaymentMethod, UsageMetric, Branding, Alerts
  projects/             # demo data powering the dashboard: Project, Task, Meeting, Ticket, Invoice, Snapshot
  dashboard/            # aggregation views (no models)
templates/              # base.html + partials + auth/dashboard/accounts/tenants/projects/core pages
static/css|js/          # theme.css, layout.js (customizer), charts.js
```

---

## ⚙️ Environment notes

- **MySQL driver:** PyMySQL is installed as the MySQLdb shim in `config/__init__.py`.
- **MariaDB 10.4 (XAMPP):** Django 5.1 officially requires MariaDB ≥ 10.5. XAMPP ships 10.4.x, so
  `config/__init__.py` contains a small, documented compatibility shim (relaxes the version floor and
  disables `INSERT … RETURNING` for MariaDB < 10.5). The clean long-term fix is to upgrade XAMPP's
  MariaDB to ≥ 10.5, after which the shim can be removed.
- **Email:** development uses the console backend — invitation and password-reset emails print to the
  terminal running `runserver`.

---

## 🗺️ Roadmap

Module 0 is complete. Modules 1–20 (see `ProjectManagementSystem.md`) are scaffolded in navigation and
will be implemented in future iterations, reusing the same multi-tenant + CRUD + dashboard patterns.
