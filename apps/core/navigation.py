"""
Sidebar navigation tree for NavPMS.

Reproduces all 21 modules (0..20) from ProjectManagementSystem.md, each with its
5 sub-modules. Module 0 and a few admin sub-modules link to LIVE url names; every
other sub-module links to the generic placeholder view (core:module_placeholder)
addressed by (module_slug, sub_slug).
"""
from django.utils.text import slugify

# ---------------------------------------------------------------------------
# LIVE url-name mapping. Keyed by (module_number, sub_module_name).
# Anything not present here resolves to the placeholder.
# ---------------------------------------------------------------------------
LIVE_LINKS = {
    (0, 'Tenant Onboarding'): 'tenants:onboarding',
    (0, 'Subscription & Billing'): 'tenants:subscription',
    (0, 'Tenant Isolation & Security'): 'tenants:isolation_security',
    (0, 'Custom Branding'): 'tenants:branding',
    (0, 'Tenant Health Monitoring'): 'tenants:health',
    # Module 1 - Project Initiation & Charter
    (1, 'Project Request & Intake'): 'initiation:request_list',
    (1, 'Business Case & Feasibility'): 'initiation:businesscase_list',
    (1, 'Project Charter Authoring'): 'initiation:charter_list',
    (1, 'Stakeholder Identification & Analysis'): 'initiation:stakeholder_list',
    (1, 'Project Kickoff & Launch'): 'initiation:kickoff_list',
    # Module 2 - Project Planning & Scheduling
    (2, 'Work Breakdown Structure (WBS)'): 'planning:workpackage_list',
    (2, 'Task Sequencing & Dependency Mapping'): 'planning:dependency_list',
    (2, 'Duration & Effort Estimation'): 'planning:task_list',
    (2, 'Milestone & Phase-Gate Definition'): 'planning:milestone_list',
    (2, 'Schedule Baseline & Version Control'): 'planning:baseline_list',
    # Module 3 - Resource Management
    (3, 'Resource Pool & Skills Inventory'): 'resources:resource_list',
    (3, 'Resource Allocation & Leveling'): 'resources:allocation_list',
    (3, 'Team Assembly & Role Assignment'): 'resources:assignment_list',
    (3, 'Resource Forecasting & Demand Planning'): 'resources:forecast_list',
    (3, 'Time Tracking & Timesheets'): 'resources:timeentry_list',
    # Module 4 - Cost & Budget Management
    (4, 'Budget Planning & Estimation'): 'budgeting:budget_list',
    (4, 'Cost Baseline & Control Accounts'): 'budgeting:controlaccount_list',
    (4, 'Expense Tracking & Commitments'): 'budgeting:expense_list',
    (4, 'Forecasting & Estimate at Completion (EAC)'): 'budgeting:forecast_list',
    (4, 'Change Control & Budget Revisions'): 'budgeting:change_list',
    # Module 5 - Risk & Issue Management
    (5, 'Risk Identification & Register'): 'risks:risk_list',
    (5, 'Qualitative & Quantitative Analysis'): 'risks:analysis_list',
    (5, 'Risk Response Planning'): 'risks:response_list',
    (5, 'Issue Logging & Escalation'): 'risks:issue_list',
    (5, 'Risk Monitoring & Reporting'): 'risks:review_list',
    # Module 6 - Quality Management
    (6, 'Quality Planning & Standards'): 'quality:standard_list',
    (6, 'Quality Assurance (QA)'): 'quality:audit_list',
    (6, 'Quality Control (QC) & Inspections'): 'quality:inspection_list',
    (6, 'Continuous Improvement'): 'quality:improvement_list',
    (6, 'Deliverable Acceptance & Sign-off'): 'quality:signoff_list',
    # Module 7 - Scope & Requirements Management
    (7, 'Requirements Elicitation'): 'scope:requirement_list',
    (7, 'Requirements Documentation & Traceability'): 'scope:trace_list',
    (7, 'Scope Definition & Boundaries'): 'scope:statement_list',
    (7, 'Change Request Management'): 'scope:changerequest_list',
    (7, 'Scope Verification & Control'): 'scope:verification_list',
    # Module 8 - Task & Work Management
    (8, 'Task Creation & Assignment'): 'work:workitem_list',
    (8, 'Priority & Urgency Scoring'): 'work:priorityscore_list',
    (8, 'Kanban & Scrum Boards'): 'work:boardcolumn_list',
    (8, 'Gantt Charts & Timeline Views'): 'work:boardcard_list',
    (8, 'Task Dependencies & Blocking'): 'work:workdependency_list',
    # Module 9 - Collaboration & Communication
    (9, 'Team Messaging & Channels'): 'collaboration:channel_list',
    (9, 'Document Sharing & Co-Editing'): 'collaboration:shareddocument_list',
    (9, 'Meeting Management'): 'collaboration:meeting_list',
    (9, 'Notifications & Alerts'): 'collaboration:notification_list',
    (9, 'Activity Streams & Feeds'): 'collaboration:activity_list',
    # Module 10 - Document & Knowledge Management
    (10, 'Document Repository & Folders'): 'documents:document_list',
    (10, 'Document Templates & Standards'): 'documents:documenttemplate_list',
    (10, 'Version Control & Check-in/Out'): 'documents:documentversion_list',
    (10, 'Knowledge Base & Lessons Learned'): 'documents:knowledgearticle_list',
    (10, 'Document Retention & Archiving'): 'documents:retentionpolicy_list',
    # Module 11 - Time & Attendance Tracking
    (11, 'Timesheet Entry & Submission'): 'timesheets:timesheet_list',
    (11, 'Approval Workflows'): 'timesheets:timesheetapproval_list',
    (11, 'Billable vs. Non-Billable Hours'): 'timesheets:timesheetline_list',
    (11, 'Overtime & Leave Integration'): 'timesheets:leaverecord_list',
    (11, 'Time Reporting & Utilization'): 'timesheets:utilizationsnapshot_list',
    # Module 12 - Portfolio & Program Management
    (12, 'Portfolio Dashboard & Heat Maps'): 'portfolio:portfolio_list',
    (12, 'Program Dependency Mapping'): 'portfolio:dependency_list',
    (12, 'Strategic Alignment & Scoring'): 'portfolio:goal_list',
    (12, 'Capacity & Pipeline Planning'): 'portfolio:capacity_list',
    (12, 'Portfolio Reporting & Governance'): 'portfolio:program_list',
    # Module 13 - Agile & Scrum Management
    (13, 'Sprint Planning & Backlog Grooming'): 'agile:backlogitem_list',
    (13, 'Sprint Execution & Daily Standups'): 'agile:sprint_list',
    (13, 'Release & Version Planning'): 'agile:release_list',
    (13, 'Epic & Feature Management'): 'agile:epic_list',
    (13, 'Retrospectives & Team Health'): 'agile:retrospective_list',
    # Module 14 - Client & External Collaboration
    (14, 'Client Portal & Visibility'): 'clients:access_list',
    (14, 'Client Feedback & Approvals'): 'clients:feedback_list',
    (14, 'Contract & SOW Management'): 'clients:contract_list',
    (14, 'External Vendor Coordination'): 'clients:vendor_list',
    (14, 'Billing & Invoicing to Clients'): 'clients:invoice_list',
    # Module 15 - Financial & Billing Management
    (15, 'Project Accounting & Cost Centers'): 'finance:costcenter_list',
    (15, 'Invoice Generation & Delivery'): 'finance:invoice_list',
    (15, 'Payment Tracking & Reconciliation'): 'finance:payment_list',
    (15, 'Budget vs. Actual Analysis'): 'finance:budgetactual_list',
    (15, 'Multi-Currency & Tax Handling'): 'finance:currencyrate_list',
    (19, 'Role & Permission Management'): 'accounts:role_list',
    (20, 'User Management & Provisioning'): 'accounts:user_list',
    (20, 'Audit Trail & Logging'): 'core:audit_log',
}


# ---------------------------------------------------------------------------
# The raw module catalog: (number, name, icon, [sub-module names...])
# Sub-module names are reproduced EXACTLY from ProjectManagementSystem.md.
# ---------------------------------------------------------------------------
MODULE_CATALOG = [
    (0, 'Tenant & Subscription Management', 'shield', [
        'Tenant Onboarding',
        'Subscription & Billing',
        'Tenant Isolation & Security',
        'Custom Branding',
        'Tenant Health Monitoring',
    ]),
    (1, 'Project Initiation & Charter', 'flag', [
        'Project Request & Intake',
        'Business Case & Feasibility',
        'Project Charter Authoring',
        'Stakeholder Identification & Analysis',
        'Project Kickoff & Launch',
    ]),
    (2, 'Project Planning & Scheduling', 'calendar', [
        'Work Breakdown Structure (WBS)',
        'Task Sequencing & Dependency Mapping',
        'Duration & Effort Estimation',
        'Milestone & Phase-Gate Definition',
        'Schedule Baseline & Version Control',
    ]),
    (3, 'Resource Management', 'users', [
        'Resource Pool & Skills Inventory',
        'Resource Allocation & Leveling',
        'Team Assembly & Role Assignment',
        'Resource Forecasting & Demand Planning',
        'Time Tracking & Timesheets',
    ]),
    (4, 'Cost & Budget Management', 'dollar-sign', [
        'Budget Planning & Estimation',
        'Cost Baseline & Control Accounts',
        'Expense Tracking & Commitments',
        'Forecasting & Estimate at Completion (EAC)',
        'Change Control & Budget Revisions',
    ]),
    (5, 'Risk & Issue Management', 'alert-triangle', [
        'Risk Identification & Register',
        'Qualitative & Quantitative Analysis',
        'Risk Response Planning',
        'Issue Logging & Escalation',
        'Risk Monitoring & Reporting',
    ]),
    (6, 'Quality Management', 'check-circle', [
        'Quality Planning & Standards',
        'Quality Assurance (QA)',
        'Quality Control (QC) & Inspections',
        'Continuous Improvement',
        'Deliverable Acceptance & Sign-off',
    ]),
    (7, 'Scope & Requirements Management', 'target', [
        'Requirements Elicitation',
        'Requirements Documentation & Traceability',
        'Scope Definition & Boundaries',
        'Change Request Management',
        'Scope Verification & Control',
    ]),
    (8, 'Task & Work Management', 'check-square', [
        'Task Creation & Assignment',
        'Priority & Urgency Scoring',
        'Kanban & Scrum Boards',
        'Gantt Charts & Timeline Views',
        'Task Dependencies & Blocking',
    ]),
    (9, 'Collaboration & Communication', 'message-square', [
        'Team Messaging & Channels',
        'Document Sharing & Co-Editing',
        'Meeting Management',
        'Notifications & Alerts',
        'Activity Streams & Feeds',
    ]),
    (10, 'Document & Knowledge Management', 'folder', [
        'Document Repository & Folders',
        'Document Templates & Standards',
        'Version Control & Check-in/Out',
        'Knowledge Base & Lessons Learned',
        'Document Retention & Archiving',
    ]),
    (11, 'Time & Attendance Tracking', 'clock', [
        'Timesheet Entry & Submission',
        'Approval Workflows',
        'Billable vs. Non-Billable Hours',
        'Overtime & Leave Integration',
        'Time Reporting & Utilization',
    ]),
    (12, 'Portfolio & Program Management', 'layers', [
        'Portfolio Dashboard & Heat Maps',
        'Program Dependency Mapping',
        'Strategic Alignment & Scoring',
        'Capacity & Pipeline Planning',
        'Portfolio Reporting & Governance',
    ]),
    (13, 'Agile & Scrum Management', 'zap', [
        'Sprint Planning & Backlog Grooming',
        'Sprint Execution & Daily Standups',
        'Release & Version Planning',
        'Epic & Feature Management',
        'Retrospectives & Team Health',
    ]),
    (14, 'Client & External Collaboration', 'user-check', [
        'Client Portal & Visibility',
        'Client Feedback & Approvals',
        'Contract & SOW Management',
        'External Vendor Coordination',
        'Billing & Invoicing to Clients',
    ]),
    (15, 'Financial & Billing Management', 'file-text', [
        'Project Accounting & Cost Centers',
        'Invoice Generation & Delivery',
        'Payment Tracking & Reconciliation',
        'Budget vs. Actual Analysis',
        'Multi-Currency & Tax Handling',
    ]),
    (16, 'Reporting & Business Intelligence', 'bar-chart-2', [
        'Standard Project Reports',
        'Custom Report Builder',
        'Real-Time Dashboards & Widgets',
        'Executive & Steering Committee Packs',
        'Data Export & API Connectivity',
    ]),
    (17, 'Workflow & Automation', 'git-merge', [
        'Visual Workflow Designer',
        'Approval Automation',
        'Notification & Reminder Rules',
        'Recurring Task Automation',
        'Integration Automation (iPaaS)',
    ]),
    (18, 'Integration & API Hub', 'share-2', [
        'ERP & Financial System Sync',
        'CRM Integration',
        'HR & Talent Systems',
        'Development & DevOps Tools',
        'File Storage & Collaboration',
    ]),
    (19, 'Master Data & Configuration', 'sliders', [
        'Project Templates & Methodologies',
        'Custom Fields & Forms',
        'Organization Hierarchy & Teams',
        'Role & Permission Management',
        'Localization & Multi-Language',
    ]),
    (20, 'System Administration & Security', 'shield', [
        'User Management & Provisioning',
        'Security & Compliance',
        'Audit Trail & Logging',
        'Backup & Disaster Recovery',
        'System Health & Performance',
    ]),
]

# Short descriptions per sub-module (used by the placeholder page).
SUBMODULE_DESCRIPTIONS = {
    'Tenant Onboarding': 'Self-service registration, domain provisioning, and initial configuration wizard.',
    'Subscription & Billing': 'Plan management, usage metering, invoicing, and payment gateway integration.',
    'Tenant Isolation & Security': 'Database/schema isolation, encryption keys, and cross-tenant data leak prevention.',
    'Custom Branding': 'White-labeling, custom logos, themes, and email templates per tenant.',
    'Tenant Health Monitoring': 'Resource usage tracking, audit logs, and tenant-level system performance alerts.',
    'Project Request & Intake': 'Standardized request forms, stakeholder submission portals, and demand pipeline tracking.',
    'Business Case & Feasibility': 'Cost-benefit analysis, ROI modeling, risk-adjusted return calculations, and go/no-go gates.',
    'Project Charter Authoring': 'Scope definition, objectives, success criteria, and executive sponsor assignment.',
    'Stakeholder Identification & Analysis': 'RACI matrices, influence/interest mapping, and communication preference capture.',
    'Project Kickoff & Launch': 'Meeting templates, team onboarding checklists, and baseline setting ceremonies.',
    'Work Breakdown Structure (WBS)': 'Hierarchical task decomposition, deliverable mapping, and package definition.',
    'Task Sequencing & Dependency Mapping': 'Finish-to-start, start-to-start, lag, lead, and critical path calculation.',
    'Duration & Effort Estimation': 'Bottom-up, top-down, analogous, and parametric estimating with confidence ranges.',
    'Milestone & Phase-Gate Definition': 'Key decision points, entry/exit criteria, and stage-gate governance.',
    'Schedule Baseline & Version Control': 'Frozen baselines, what-if scenarios, and schedule compression.',
    'Resource Pool & Skills Inventory': 'Employee profiles, competency matrices, certifications, and availability calendars.',
    'Resource Allocation & Leveling': 'Capacity planning, over-allocation alerts, and automatic smoothing algorithms.',
    'Team Assembly & Role Assignment': 'Named resource booking, generic placeholder roles, and substitution workflows.',
    'Resource Forecasting & Demand Planning': 'Pipeline vs. capacity views, hiring triggers, and contractor engagement.',
    'Time Tracking & Timesheets': 'Daily/weekly entry, approval routing, and actuals-to-plan comparison.',
    'Budget Planning & Estimation': 'Labor, material, overhead, and contingency budgeting with bottom-up rollup.',
    'Cost Baseline & Control Accounts': 'Earned value management (EVM) structures and work package cost tracking.',
    'Expense Tracking & Commitments': 'POs, invoices, accruals, and real-time spend against budget.',
    'Forecasting & Estimate at Completion (EAC)': 'Trend analysis, CPI/SPI projections, and to-complete performance index.',
    'Change Control & Budget Revisions': 'Formal change requests, impact analysis, and re-baseline approvals.',
    'Risk Identification & Register': 'Risk taxonomy, brainstorming tools, and checklists for common project types.',
    'Qualitative & Quantitative Analysis': 'Probability/impact matrices, Monte Carlo simulation, and expected monetary value.',
    'Risk Response Planning': 'Avoid, transfer, mitigate, accept strategies with action owners and triggers.',
    'Issue Logging & Escalation': 'Issue capture, severity classification, resolution tracking, and escalation paths.',
    'Risk Monitoring & Reporting': 'Top-risk dashboards, burn-down of risk exposure, and lessons learned integration.',
    'Quality Planning & Standards': 'Acceptance criteria, regulatory requirements, and industry standard mapping.',
    'Quality Assurance (QA)': 'Process audits, compliance checklists, and methodology adherence reviews.',
    'Quality Control (QC) & Inspections': 'Testing protocols, defect tracking, and inspection result recording.',
    'Continuous Improvement': 'Kaizen events, retrospectives, and process maturity assessments.',
    'Deliverable Acceptance & Sign-off': 'Formal review gates, customer validation, and acceptance documentation.',
    'Requirements Elicitation': 'Interviews, workshops, surveys, and user story mapping sessions.',
    'Requirements Documentation & Traceability': 'SRS, user stories, traceability matrices, and version control.',
    'Scope Definition & Boundaries': 'In-scope/out-scope statements, assumptions, and constraints registry.',
    'Change Request Management': 'Scope change proposals, impact analysis on schedule/cost/quality, and CCB decisions.',
    'Scope Verification & Control': 'Deliverable inspection, scope creep alerts, and formal acceptance workflows.',
    'Task Creation & Assignment': 'Individual and team tasks, sub-tasks, checklists, and bulk operations.',
    'Priority & Urgency Scoring': 'MoSCoW, Eisenhower matrix, and custom priority frameworks.',
    'Kanban & Scrum Boards': 'Visual workflow states, WIP limits, and drag-and-drop progression.',
    'Gantt Charts & Timeline Views': 'Bar charts, timeline dependencies, and progress shading.',
    'Task Dependencies & Blocking': 'Predecessor/successor links, blocked status, and unblock criteria.',
    'Team Messaging & Channels': 'Project-specific chat, threaded discussions, and @mention notifications.',
    'Document Sharing & Co-Editing': 'Centralized repositories, version history, and real-time collaborative editing.',
    'Meeting Management': 'Agenda builders, minutes capture, action item tracking, and recurrence scheduling.',
    'Notifications & Alerts': 'Customizable triggers for assignments, due dates, mentions, and system events.',
    'Activity Streams & Feeds': 'Chronological project updates, audit trails, and social-style engagement.',
    'Document Repository & Folders': 'Hierarchical storage, metadata tagging, and project-specific organization.',
    'Document Templates & Standards': 'Standardized formats for charters, plans, reports, and status updates.',
    'Version Control & Check-in/Out': 'Revision history, comparison tools, and conflict resolution.',
    'Knowledge Base & Lessons Learned': 'Searchable repository of past project insights, playbooks, and retrospectives.',
    'Document Retention & Archiving': 'Lifecycle policies, legal hold, and post-project archival workflows.',
    'Timesheet Entry & Submission': 'Daily/weekly time logs by project/task with notes and activity codes.',
    'Approval Workflows': 'Manager review, rejection with comments, and resubmission loops.',
    'Billable vs. Non-Billable Hours': 'Chargeability ratios, overhead allocation, and client billing splits.',
    'Overtime & Leave Integration': 'Calendar sync, holiday rules, and overtime calculation.',
    'Time Reporting & Utilization': 'Individual and team utilization dashboards, capacity vs. demand views.',
    'Portfolio Dashboard & Heat Maps': 'Multi-project health indicators, bubble charts, and investment balance views.',
    'Program Dependency Mapping': 'Cross-project dependencies, shared resources, and milestone alignment.',
    'Strategic Alignment & Scoring': 'Objective key result (OKR) linkage, weighted scoring models, and prioritization.',
    'Capacity & Pipeline Planning': 'Resource pool across programs, demand funnel, and intake governance.',
    'Portfolio Reporting & Governance': 'Executive summaries, steering committee packs, and investment reviews.',
    'Sprint Planning & Backlog Grooming': 'Story point estimation, velocity tracking, and backlog prioritization.',
    'Sprint Execution & Daily Standups': 'Burndown charts, impediment tracking, and standup note capture.',
    'Release & Version Planning': 'Release trains, feature flags, and version roadmap visualization.',
    'Epic & Feature Management': 'Hierarchical story organization, cross-sprint feature tracking, and progress rollups.',
    'Retrospectives & Team Health': 'Sprint retrospective boards, action item tracking, and team sentiment surveys.',
    'Client Portal & Visibility': 'Branded external access, project progress views, and deliverable sharing.',
    'Client Feedback & Approvals': 'Review cycles, annotation tools, and formal sign-off workflows.',
    'Contract & SOW Management': 'Statement of work authoring, amendment tracking, and milestone billing linkage.',
    'External Vendor Coordination': 'Third-party task assignment, deliverable handoffs, and vendor scorecards.',
    'Billing & Invoicing to Clients': 'Time-and-materials, fixed-fee, and milestone-based invoice generation.',
    'Project Accounting & Cost Centers': 'Revenue recognition, cost allocation, and profit/loss by project.',
    'Invoice Generation & Delivery': 'Automated billing from timesheets and expenses, PDF generation, and email dispatch.',
    'Payment Tracking & Reconciliation': 'A/R aging, collections workflow, and cash flow forecasting.',
    'Budget vs. Actual Analysis': 'Real-time cost variance, earned value metrics, and forecast updates.',
    'Multi-Currency & Tax Handling': 'Exchange rate management, tax jurisdiction rules, and international billing.',
    'Standard Project Reports': 'Status reports, risk registers, issue logs, and milestone summaries.',
    'Custom Report Builder': 'Drag-and-drop fields, filters, grouping, and calculated columns.',
    'Real-Time Dashboards & Widgets': 'KPI cards, trend charts, and personalized home screens.',
    'Executive & Steering Committee Packs': 'High-level summaries, RAG status, and strategic narrative generation.',
    'Data Export & API Connectivity': 'CSV, Excel, PDF exports, and OData/REST feeds to external BI tools.',
    'Visual Workflow Designer': 'Drag-and-drop process automation with conditional logic and branching.',
    'Approval Automation': 'Auto-approval within thresholds, escalation on timeout, and delegation rules.',
    'Notification & Reminder Rules': 'Custom triggers for deadlines, status changes, and risk thresholds.',
    'Recurring Task Automation': 'Template-based repetition, auto-assignment, and schedule generation.',
    'Integration Automation (iPaaS)': 'Webhooks, Zapier/Make-style connectors, and event-driven actions.',
    'ERP & Financial System Sync': 'SAP, Oracle, NetSuite, Workday, and Microsoft Dynamics connectors.',
    'CRM Integration': 'Salesforce, HubSpot, and Microsoft Dynamics Sales linkage for client projects.',
    'HR & Talent Systems': 'Workday, BambooHR, and ADP integration for resource pools and time data.',
    'Development & DevOps Tools': 'Jira, GitHub, GitLab, Azure DevOps, and CI/CD pipeline connections.',
    'File Storage & Collaboration': 'SharePoint, Google Drive, Dropbox, and Box synchronization.',
    'Project Templates & Methodologies': 'Waterfall, Agile, hybrid templates with pre-built WBS and workflows.',
    'Custom Fields & Forms': 'User-defined data capture, validation rules, and conditional visibility.',
    'Organization Hierarchy & Teams': 'Departments, business units, locations, and matrix team structures.',
    'Role & Permission Management': 'Granular access control, data visibility rules, and field-level security.',
    'Localization & Multi-Language': 'Regional settings, language packs, date/number formats, and time zones.',
    'User Management & Provisioning': 'SSO (SAML/OIDC), SCIM provisioning, and guest user controls.',
    'Security & Compliance': 'SOC 2, ISO 27001, GDPR alignment, encryption at rest and in transit.',
    'Audit Trail & Logging': 'Immutable activity logs, data change history, and forensic search.',
    'Backup & Disaster Recovery': 'Automated snapshots, geo-redundancy, and recovery time objectives.',
    'System Health & Performance': 'Uptime monitoring, API rate limits, storage quotas, and usage analytics.',
}


def _build_submodule(module_number, name):
    """Build a single sub-module dict with the right link target."""
    sub_slug = slugify(name)
    live = LIVE_LINKS.get((module_number, name))
    return {
        'name': name,
        'slug': sub_slug,
        'description': SUBMODULE_DESCRIPTIONS.get(name, ''),
        'url_name': live or 'core:module_placeholder',
        'is_live': bool(live),
    }


def get_modules():
    """Return the full module list (numbers 0..20) with sub-modules."""
    modules = []
    for number, name, icon, subs in MODULE_CATALOG:
        module_slug = slugify(name)
        modules.append({
            'number': number,
            'name': name,
            'icon': icon,
            'slug': module_slug,
            'submodules': [_build_submodule(number, sub) for sub in subs],
        })
    return modules


def get_navigation():
    """Return the full sidebar tree consumed by the base template."""
    return {
        'sections': [
            {
                'label': 'Dashboard',
                'icon': 'grid',
                'items': [
                    {'label': 'Dashboard', 'icon': 'grid', 'url_name': 'dashboard:index'},
                ],
            },
            {
                'label': 'Workspace',
                'icon': 'briefcase',
                'items': [
                    {'label': 'Projects', 'icon': 'briefcase', 'url_name': 'projects:project_list'},
                    {'label': 'Tasks', 'icon': 'check-square', 'url_name': 'projects:task_list'},
                    {'label': 'Meetings', 'icon': 'calendar', 'url_name': 'projects:meeting_list'},
                    {'label': 'Tickets', 'icon': 'life-buoy', 'url_name': 'projects:ticket_list'},
                    {'label': 'Invoices', 'icon': 'file-text', 'url_name': 'projects:invoice_list'},
                ],
            },
            {
                'label': 'Modules',
                'icon': 'layers',
                'modules': get_modules(),
            },
        ],
    }


def find_submodule(module_slug, sub_slug):
    """Look up a (module, sub-module) pair by their slugs. Returns (module, sub) or (None, None)."""
    for module in get_modules():
        if module['slug'] == module_slug:
            for sub in module['submodules']:
                if sub['slug'] == sub_slug:
                    return module, sub
            return module, None
    return None, None
