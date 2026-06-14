# TODO — NavPMS Modules 1–3 (Initiation, Planning, Resources)

## Status: ✅ COMPLETE & VERIFIED

Built with a parallel multi-agent **Workflow** (19 build agents in 1 burst, then a 4-agent adversarial
review) after the user asked to "start next three modules with multiple Agent upto 100 max, use workflow".
Main loop kept the single-DB-writer work (settings/urls/navigation wire-up, makemigrations/migrate/seed,
verification) to itself.

## Modules delivered
| # | app slug | models | sub-modules → Live |
|---|----------|--------|--------------------|
| 1 | `initiation` | ProjectRequest, BusinessCase, ProjectCharter, Stakeholder, KickoffTask | 5/5 |
| 2 | `planning` | WorkPackage(WBS), ScheduleTask, TaskDependency, Milestone, ScheduleBaseline | 5/5 |
| 3 | `resources` | Resource, Skill, Allocation, TeamAssignment, DemandForecast, TimeEntry | 5/5 |

## Orchestration ✅
- [x] Wrote authoritative spec contract (`temp/specs/`) pinning every model/field/choice/url/context-var
- [x] Workflow `build-navpms-modules-1-3`: 3 backend agents + 16 template agents (read the specs)
- [x] Wire-up (main loop): INSTALLED_APPS, config/urls.py, navigation.py LIVE_LINKS (15 entries), .gitignore temp/
- [x] makemigrations (16 models) → migrate → seed (×2, idempotent) → `manage.py check` = 0 issues

## Verification (main loop) ✅
- [x] Smoke test: **80/80** URL checks (list/create/detail/edit/delete × 16) → 200/302
- [x] Detail pages render their object identifier (silent-context-var-mismatch detector)
- [x] No template-comment leak markers
- [x] **16/16 CRUD create→delete round-trips** (real persistence, correct tenant, working delete; net-zero)
- [x] **16/16 tenant-isolation checks** (admin_acme → 404 on globex objects)
- [x] Malformed-filter probe: **8/8** FK filters reject `?fk=abc` gracefully (200, not 500)
- [x] Adversarial review workflow (3 module + 1 security agent): **0 high, 0 medium**, 2 low nits

## Bugs found & fixed during verification
1. **Detail context-var mismatch (4 models)** — `request_detail`/`businesscase_detail`/`kickoff_detail`/
   `timeentry_detail` templates referenced a different object var than their view passed (`obj` vs
   `request_obj`; `businesscase` vs `business_case`; `kickoff` vs `kickoff_task`; `timeentry` vs
   `time_entry`) → `NoReverseMatch` (empty pk). Aligned the views to the templates' vars.
2. **Pagination `EmptyPage`** — `{{ page_obj.previous_page_number }}`/`next_page_number` were evaluated in
   the href even on the first/last page (the method raises when there is no prev/next). Latent in **all 16**
   list templates (copied from the never-paginated reference invoice list); surfaced only on the >10-row
   lists (task=12, allocation=12, timeentry=14). Guarded with `has_previous`/`has_next` (32 guards).
3. **None-FK crash** — `{{ fk.get_full_name|default:fk.username|default:"—" }}` raised
   `VariableDoesNotExist` when the user FK is `None` (seeder leaves some `resource.user` null). Guarded
   9 occurrences with `{% if fk %}…{% else %}—{% endif %}`.
4. **Unvalidated integer FK filter (review nit)** — `?project=abc` → `qs.filter(project_id='abc')` →
   `ValueError` → 500. Guarded 8 list views with `if <fk>_id.isdigit():`.

## Review nits NOT actioned (intentional)
- **Global auto-number sequence** (`REQ/BC/CHTR/TE`): uses a global `unique=True` counter, not per-tenant.
  Reviewer confirmed not exploitable (informational enumeration signal only). Left as-is for **consistency
  with the reference convention** (`INV-#####`, `PINV-#####` are also global). Documented as intentional.

## Notes
- Throwaway verifiers live in `temp/` (gitignored): `smoke_modules_1_3.py`, `crud_modules_1_3.py`,
  `fix_templates.py`, `diag.py`, `diag2.py`, and the `specs/` contract.

---

# (history) TODO — NavPMS Foundation + Module 0

## Status: ✅ COMPLETE & VERIFIED

Built with a parallel multi-agent workflow (7 agents, 2 bursts) after the user asked to "use more Agents".

### What shipped
Full multi-tenant Django PMS foundation + Module 0, a customizable blue/white Tailwind+HTMX dashboard
matching the reference image, auth (login/register/forgot/invite), user & role management, profile +
UI preferences, and a sidebar exposing all 21 modules (0–20).

### Key environment findings (still relevant)
1. **Database** — XAMPP `navpms` is a *different* app (procurement). NavPMS uses its own DB **`nav_pms`**.
2. **MariaDB 10.4 vs Django 5.1** — compat shim in `config/__init__.py`; long-term fix is MariaDB ≥10.5.

### Bugs found & fixed during Module 0 verification
- `apps/tenants/views.py` (onboarding): wrong reverse accessor → fixed to `tenant.projects`.
- `templates/partials/sidebar.html` + `customizer.html`: multi-line `{# … #}` leak → `{% comment %}`.
