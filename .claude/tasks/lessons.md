# Lessons

## L1 — Verify a database is actually ours (and empty) before migrating
`CREATE DATABASE IF NOT EXISTS x` is a **silent no-op** when `x` already exists. On this XAMPP instance,
`navpms` was already owned by a different Nav app (~170 procurement tables, live data). **Rule:** before
pointing `.env` at a DB and running migrate, check `SELECT COUNT(*) FROM information_schema.tables WHERE
table_schema='<db>'` and confirm it's empty or ours. Never flush/fake-migrate a non-empty unknown DB.
NavPMS uses its own DB **`nav_pms`**.

## L2 — Django `{# … #}` comments are single-line only
Multi-line `{# … #}` comments **leak as visible text**. Use `{% comment %} … {% endcomment %}` for any
note longer than one line. (Found in `sidebar.html` + `customizer.html` during verification.)

## L3 — HTTP-200 smoke tests miss template-comment / content leaks
A page can return 200 yet render leaked comment text or wrong content. **Pair** the status-code smoke test
(Django test client over all url names) with a **rendered-HTML content check** (assert no `{#`/`{% comment`
markers, assert expected chart/script ids and tenant name present).

## L4 — XAMPP MariaDB 10.4 vs modern Django
Django 5.1 requires MariaDB ≥ 10.5; XAMPP ships 10.4.x. Either upgrade MariaDB, pin Django 4.2 LTS, or use
a documented features shim in `config/__init__.py` (we used the shim; it disables `INSERT … RETURNING` for
MariaDB < 10.5 and relaxes the version floor).

## L5 — User workflow preference: fan out aggressively
The user explicitly asked to "use more Agents to complete the task as soon as possible." For large builds,
prefer a parallel multi-agent Workflow (e.g. foundation+shell in parallel, then a burst of page agents)
over a 2-agent sequential pipeline. Keep critical-path/single-writer work (migrations, shared base/static)
solo; parallelize disjoint file sets (per-app templates).
