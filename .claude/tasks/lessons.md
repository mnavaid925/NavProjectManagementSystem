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

## L6 — Stale/orphaned dev servers mask code fixes (verify via a single fresh server)
A template fix can be correct on disk + clean in `render_to_string` and the test client, yet a browser still
shows the OLD output — because a **leftover server is serving a pre-fix snapshot**. On Windows, Django
`runserver` uses `SO_REUSEADDR`, so **multiple orphaned processes can all LISTEN on the same port** (e.g. a
`preview_start` server started before the fix + `runserver` children orphaned when their wrapper task was
TaskStop'd). `Get-NetTCPConnection`/`Win32_Process` filtered by name can miss them. **Rule:** when a fix "won't
show", `netstat -ano | findstr :PORT`, kill EVERY LISTENING pid in a loop until the port is empty, `preview_stop`
any preview servers (check `preview_list`), then start ONE fresh server and re-verify over real HTTP. Then the
user must hard-refresh (Ctrl+Shift+R). The in-process test client is the authoritative render check.

## L5 — User workflow preference: fan out aggressively
The user explicitly asked to "use more Agents to complete the task as soon as possible." For large builds,
prefer a parallel multi-agent Workflow (e.g. foundation+shell in parallel, then a burst of page agents)
over a 2-agent sequential pipeline. Keep critical-path/single-writer work (migrations, shared base/static)
solo; parallelize disjoint file sets (per-app templates).

## L7 — When backend & template agents are split, PIN the detail/edit context-var name
Separate agents wrote views (`models.py`/`views.py`) and templates from a shared spec. The spec pinned the
**list** context var (`requests`, `charters`, …) but NOT the **detail/edit object** var. Result: 4/16 models
drifted — view passed `request_obj`/`business_case`/`kickoff_task`/`time_entry`, template used
`obj`/`businesscase`/`kickoff`/`timeentry` → `{% url … X.pk %}` got an empty pk → **NoReverseMatch (500)**.
**Rule:** the contract handed to parallel agents must pin EVERY context key a template consumes (detail object,
edit-mode object, every `*_choices`, every FK queryset), not just the list var. 12/16 matched only by luck
(agents independently chose the model name). The fix here was to align the view's key to the template's var.

## L8 — A GET-200 smoke test does NOT prove the page is correct (add a content assertion)
A wrong detail context var renders **blank** (Django silently swallows a missing top-level var) and still
returns 200 — only the `{% url … X.pk %}` case 500s. **Rule:** after the status-code sweep, also assert each
detail page's rendered HTML contains the object's identifier (e.g. a token from `str(obj)`); this catches the
silent-blank class. Also run the test client with `Client(raise_request_exception=False)` so one pass collects
**all** 500s instead of aborting on the first.

## L9 — Django pagination: never emit `page_obj.previous_page_number` unconditionally
`Page.previous_page_number()` / `next_page_number()` **raise `EmptyPage`** when there is no prev/next page.
Putting `…page={{ page_obj.previous_page_number }}` in a "Prev" href 500s on page 1 — but only once a list
exceeds the page size, so it's invisible with small seed data (the reference invoice list has the same latent
bug and never paginates). **Rule:** guard with `{% if page_obj.has_previous %}{{ page_obj.previous_page_number }}{% else %}1{% endif %}`
(and `has_next` / `paginator.num_pages` for Next).

## L10 — `{{ fk.get_full_name|default:fk.username|default:"—" }}` 500s when fk is None
Django swallows a failed lookup on the **main** variable, but a failed lookup in a **filter argument**
(`default:fk.username` when `fk` is None) raises `VariableDoesNotExist` and 500s. Seed data that always sets
the FK hides this. **Rule:** guard user-FK display with `{% if fk %}{{ fk.get_full_name|default:fk.username }}{% else %}—{% endif %}`.

## L11 — Integer FK list filters must validate input before `.filter(fk_id=…)`
`qs.filter(project_id=request.GET.get('project'))` raises `ValueError → 500` on non-numeric input
(`?project=abc`). Dropdowns only emit int pks, so it never shows in normal use, but a hand-edited URL hits it.
**Rule:** guard with `if value.isdigit():` (string-choice filters are immune; only int/FK params need this).
