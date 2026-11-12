# Sprint 3 Manual Testing Runbook (FRR 3 / QA-RT3)

- Document ID: RB-SP3-001
- Target Milestone: Sprint 3 (FRR 3 Release Handover / QA-RT3)
- Target Release Version: v0.3.0
- Target Environments: Local Docker Compose (`http://localhost:8000`, `http://localhost:3000`), Physical/Virtual Android Tablet (Min SDK 26, Resolution 1280x800)
- Governing Contracts: CT-01, CT-02, CT-17, CT-18, DEC-06, DEC-32, DEC-38, DEC-51, DEC-54, DEC-59

---

## 1. Overview and Pre-requisites

This runbook defines the step-by-step manual test procedures for verifying the Sprint 3 master data management, safety constraints, department fleet and roster setups, and operational invariants across Web and Tablet interfaces. Every procedure specifies exact test inputs, expected visual and behavioral states, and required verification evidence for QA release sign-off.

### 1.1 Test Environment Setup
1. Backend services active via `docker compose up -d` in `project-backend/ATLANTECH` (API at `http://localhost:8000`, MySQL at `localhost:3306`, Redis at `localhost:6379`).
2. Web frontend running via `npm run dev` in `project-frontend` (SPA at `http://localhost:3000`).
3. Mobile tablet application running via `flutter run` on connected Android device or emulator.
4. Database seeded with baseline reference data (`php artisan migrate:fresh --seed`).

### 1.2 Test Roles and Credentials
- Port Administrator: `admin.damietta` / `PortPass123!`
- Tug Manager: `tug.manager` / `PortPass123!`
- Tug Master: `master.omar` / `PortPass123!`
- Pilotage Manager: `pilot.manager` / `PortPass123!`
- Marine Pilot: `pilot.ibrahim` / `PortPass123!`
- Terminal Admin: `terminal.admin1` / `PortPass123!`

---

## 2. Web Master Data Screens Test Procedures (Desktop / Browser)

### 2.1 Procedure W-01: Screen P-26 (Port Profile and Navigation Channel)
- Target Screen: P-26 Port Profile Screen (`/settings/port-profile`)
- Target Role: `PORT_GM` or Port Administrator
- Objective: Verify configuration of port identity, timezone, controlling navigation channel dimensions, and datum reference.
- Test Steps:
  1. Navigate to `http://localhost:3000/settings/port-profile`.
  2. Verify form inputs: Port Name, UN/LOCODE, Timezone dropdown, Channel Width (m), Controlling Depth (m), Maximum Speed Limit (knots), and Depth Datum.
  3. Enter values:
     - Port Name: "Port of Damietta"
     - UN/LOCODE: "EGDAM"
     - Timezone: "Africa/Cairo"
     - Controlling Depth: `15.50`
     - Channel Width: `300.00`
     - Speed Limit: `8.0`
     - Depth Datum: `LAT` (Lowest Astronomical Tide)
  4. Click "حفظ بيانات الميناء والقناة" (Save Port and Channel Data).
  5. Enter an invalid negative depth (`-15.0`) and click Save.
- Expected Results:
  - Valid save displays green toast notification and updates the version token.
  - Invalid negative depth displays inline validation error: "عمق القناة يجب أن يكون قيمة موجبة" (Depth must be positive).
- Required Evidence: Screenshot of saved configuration and inline validation error state.

---

### 2.2 Procedure W-02: Screen P-28 (Berth Management and Shared Berths)
- Target Screen: P-28 Berth Management (`/master-data/berths`)
- Target Role: Port Administrator
- Objective: Verify berth creation, physical dimension rules (LOA <= Length), shared multi-terminal assignment (DEC-51), and soft deactivation.
- Test Steps:
  1. Navigate to `http://localhost:3000/master-data/berths`.
  2. Click "إضافة رصيف جديد" (Add New Berth).
  3. In modal, enter:
     - Code: `B-DCT-09`
     - Name: `East Container Berth 09`
     - Length: `350.00`
     - Water Depth: `15.00`
     - Depth Datum: `LAT`
     - Max Vessel LOA: `380.00` (Intentional error: LOA > Length)
  4. Observe validation response.
  5. Correct Max Vessel LOA to `330.00`.
  6. In "المحطات المرتبطة" (Associated Terminals) multi-select, select both Terminal 1 (CT) and Terminal 2 (NCT).
  7. Click "حفظ الرصيف" (Save Berth).
  8. In the berths table, locate `B-DCT-09` and click the status toggle switch to deactivate.
  9. Confirm warning modal: "تعطيل الرصيف سيمنع التخطيط الجديد عليه مع الاحتفاظ بسجل الرحلات السابقة" (Deactivating berth will exclude it from new planning while preserving history).
- Expected Results:
  - Step 4 flags inline error: "أقصى طول للسفينة يجب ألا يتجاوز طول الرصيف" (Max vessel LOA cannot exceed berth length).
  - Step 7 persists berth and displays multi-terminal badges in table.
  - Step 9 updates status badge to "غير نشط" (Inactive) without removing historical records.
- Required Evidence: Modal screenshot with LOA validation error; table screenshot showing multi-terminal tags and inactive badge.

---

### 2.3 Procedure W-03: Screen P-59 (Safety Constraints and Environmental Limits)
- Target Screen: P-59 Safety Constraints (`/safety/constraints`)
- Target Role: Port Administrator or Marine Safety Officer
- Objective: Verify creation of environmental safety constraints (wind, waves, visibility, UKC) with date range non-overlap enforcement.
- Test Steps:
  1. Navigate to `http://localhost:3000/safety/constraints`.
  2. Click "إضافة قيد سلامة" (Add Safety Constraint).
  3. Select Constraint Type: "أقصى سرعة رياح" (Max Wind Speed).
  4. Scope: Leave Terminal and Berth empty (Port-wide).
  5. Value: `25.0` knots.
  6. Effective From: Select current date 00:00 UTC. Effective To: Leave open-ended.
  7. Click "تطبيق القيد" (Apply Constraint).
  8. Attempt to create another port-wide wind constraint overlapping the same active date window.
- Expected Results:
  - Step 7 saves constraint and displays it in active constraints table.
  - Step 8 shows error notification: "يوجد قيد سلامة مسجل مسبقًا لنفس النطاق في هذه الفترة" (An existing constraint is registered for this scope in the same interval).
- Required Evidence: Screenshot of constraints table and conflict error toast.

---

### 2.4 Procedure W-04: Screen P-62 (Operational Settings and Port Shifts)
- Target Screen: P-62 Operational Settings (`/settings/operations`)
- Target Role: Port Administrator
- Objective: Verify AI operational parameter settings with min/max bounds enforcement (DEC-59) and port shift timetable maintenance.
- Test Steps:
  1. Navigate to `http://localhost:3000/settings/operations`.
  2. Under "معاملات الذكاء الاصطناعي" (AI Parameters), locate `ai.part1.min_window_hours` (Min window hours).
  3. Enter value `0.2` (Allowed bounds: 1.0 to 12.0) and click Save.
  4. Observe error, then correct value to `4.0` and save.
  5. Switch to "ورديات العمل بالميناء" (Port Shifts) tab.
  6. Verify the 3 standard 8-hour shifts:
     - Shift 1 (صباحية / Morning): 08:00 - 16:00
     - Shift 2 (مسائية / Evening): 16:00 - 00:00
     - Shift 3 (ليلية / Night): 00:00 - 08:00
  7. Edit Shift 1 handover grace period to 15 minutes and save.
- Expected Results:
  - Step 3 rejects value with: "القيمة يجب أن تكون بين 1.0 و 12.0 ساعة" (Value must be between 1.0 and 12.0 hours).
  - Step 4 saves parameter successfully.
  - Step 7 updates shift schedule with version confirmation.
- Required Evidence: Bounds error modal and shifts timetable view.

---

### 2.5 Procedure W-05: Screen P-27 (Terminal Management)
- Target Screen: P-27 Terminal Management (`/master-data/terminals`)
- Target Role: Port Administrator
- Objective: Verify terminal registration, container vs non-container type selection, and GeoJSON boundary display.
- Test Steps:
  1. Navigate to `http://localhost:3000/master-data/terminals`.
  2. Verify listing of existing terminals (`Damietta Container Terminal 1`, etc.).
  3. Click "إضافة محطة" (Add Terminal).
  4. Enter Code: `T-GEN`, Name: `Damietta Bulk and General Cargo`, Type: `NON_CONTAINER`.
  5. Click Save.
- Expected Results:
  - Terminal is added with "بضائع عامة / غير حاويات" (Non-Container) tag.
  - Equipment and Yard management tabs remain disabled or restricted for non-container terminals.
- Required Evidence: Terminal list screenshot showing CT and NCT badges.

---

### 2.6 Procedure W-06: Screen P-45 (Tugboat Fleet Management)
- Target Screen: P-45 Tugboat Fleet (`/fleet/tugboats`)
- Target Role: `TUG_MANAGER` or Port Administrator
- Objective: Verify tugboat fleet registration, bollard pull engine ratings, and status toggles.
- Test Steps:
  1. Navigate to `http://localhost:3000/fleet/tugboats`.
  2. Click "إضافة قاطرة جديدة" (Add Tugboat).
  3. Enter Name: `Damietta Tug 07`, Power: `70.0`, Unit: `BOLLARD_PULL_TONNES`, Capacity: `75.0`.
  4. Click Save.
  5. In table row for `Damietta Tug 07`, change status from "متاح" (Available) to "صيانة" (Maintenance).
- Expected Results:
  - Tugboat is saved with default status "متاح" (Available).
  - Changing status to Maintenance updates row styling and triggers master unbinding check.
- Required Evidence: Screenshot of tugboat table with power rating and maintenance state.

---

### 2.7 Procedure W-07: Screen P-46 (Tug Master Management and 1-to-1 Binding)
- Target Screen: P-46 Tug Master Management (`/fleet/tug-masters`)
- Target Role: `TUG_MANAGER`
- Objective: Verify 1-to-1 tugboat binding to tug masters, preventing double-binding.
- Test Steps:
  1. Navigate to `http://localhost:3000/fleet/tug-masters`.
  2. Locate unassigned Tug Master `master.khaled`.
  3. Click "تعيين قاطرة" (Assign Tugboat).
  4. In the dropdown, select a tugboat already bound to `master.omar` (`Damietta Tug 01`).
  5. Observe conflict handling.
  6. Select an unassigned available tugboat (`Damietta Tug 07`).
  7. Click Confirm.
- Expected Results:
  - Step 4 either disables already-assigned tugboats in dropdown or displays conflict error upon submission: "هذه القاطرة معينة بالفعل لربان آخر" (This tugboat is already assigned to another master).
  - Step 7 successfully binds `Damietta Tug 07` to `master.khaled`.
- Required Evidence: Screenshot showing 1-to-1 assignment chips and conflict tooltip.

---

### 2.8 Procedure W-08: Screen P-43 (Pilot Roster and Availability)
- Target Screen: P-43 Pilot Roster (`/pilots/roster`)
- Target Role: `PILOTAGE_MANAGER`
- Objective: Verify pilot seniority rank classification (FIRST, SECOND, THIRD), rank vessel LOA limits, and shift availability.
- Test Steps:
  1. Navigate to `http://localhost:3000/pilots/roster`.
  2. Review pilots list with rank badges ("مرشد أول", "مرشد ثان", "مرشد ثالث").
  3. Click "حدود الرتب" (Rank Limits) settings tab.
  4. Verify maximum vessel LOA configured:
     - Rank THIRD: 180m
     - Rank SECOND: 260m
     - Rank FIRST: No limit (غير محدد)
  5. Edit pilot profile `pilot.junior` and confirm shift schedule assignment.
- Expected Results:
  - Roster displays active shift indicator ("في الوردية", "خارج الوردية").
  - Rank limits are clearly indicated in pilot details modal.
- Required Evidence: Screenshot of pilot roster table and rank limit configuration tab.

---

### 2.9 Procedure W-09: Screens P-48 & P-49 (CT Equipment and Yard Zones)
- Target Screen: P-48 CT Equipment (`/terminals/1/equipment`), P-49 Container Yard (`/terminals/1/yard`)
- Target Role: `TERMINAL_ADMIN`
- Objective: Verify container terminal crane registration and yard block zoning for specialized cargo (reefer plugs, DG classes).
- Test Steps:
  1. Navigate to `/terminals/1/equipment`. Click "إضافة معدة" (Add Equipment).
  2. Select category: "ونش رصيف" (Quay Crane), Code: `QC-04`, Capability: `TWIN_LIFT`. Save.
  3. Navigate to `/terminals/1/yard`. Click "إضافة منطقة ساحة" (Add Yard Zone).
  4. Select Zone Type: `REEFER`, enter reefer plug capacity: `120`. Save.
  5. Add second zone: Type `DANGEROUS_GOODS`, allowed IMDG classes: `["1.1", "3", "7"]`. Save.
- Expected Results:
  - Equipment is registered with supported capabilities.
  - Specialized yard zones are rendered on yard grid with specialized tags.
- Required Evidence: Equipment list and yard zoning schematic screenshots.

---

## 3. Operational and Invariant Verification Procedures

### 3.1 Procedure OP-01: Atomic Tug-Master Unbinding on User Deactivation
- Target Component: Backend Database Service / `tug_master_profiles`
- Objective: Confirm that deactivating a Tug Master user atomically unbinds their assigned tugboat in the same database transaction.
- Verification Steps:
  1. Verify in database: `SELECT user_id, assigned_tugboat_id FROM tug_master_profiles WHERE user_id = 12;` (Assigned to Tug 2).
  2. From Admin Web UI or API, execute deactivation: `PATCH /api/v1/users/12/deactivate`.
  3. Query database immediately:
     ```sql
     SELECT id, is_active FROM users WHERE id = 12;
     SELECT user_id, assigned_tugboat_id FROM tug_master_profiles WHERE user_id = 12;
     ```
- Expected Result:
  - `users.is_active` is `0`.
  - `tug_master_profiles.assigned_tugboat_id` is `NULL`.
  - Both changes committed atomically; no orphaned lock on Tug 2.
- Required Evidence: SQL query output before and after deactivation.

---

### 3.2 Procedure OP-02: Atomic Tug-Master Unbinding on Tug Maintenance State Transition
- Target Component: Backend Fleet Service / `tugboats`
- Objective: Confirm that setting a tugboat to MAINTENANCE or INACTIVE status atomically unbinds any currently assigned master.
- Verification Steps:
  1. Verify Tug 3 is currently assigned to `master.ahmed`.
  2. In UI or API, set Tug 3 status to `MAINTENANCE`.
  3. Query database:
     ```sql
     SELECT id, status FROM tugboats WHERE id = 3;
     SELECT user_id, assigned_tugboat_id FROM tug_master_profiles WHERE assigned_tugboat_id = 3;
     ```
- Expected Result:
  - `tugboats.status` is `'MAINTENANCE'`.
  - Query for `assigned_tugboat_id = 3` returns 0 rows (`master.ahmed` unassigned).
- Required Evidence: Database query results confirming atomic unbinding.

---

### 3.3 Procedure OP-03: License Plan Limit Enforcement (max_berths, max_terminals, max_users)
- Target Component: License Middleware / API Controller
- Objective: Verify that creating resources beyond license quota returns HTTP 422 PLAN_LIMIT_EXCEEDED.
- Verification Steps:
  1. Set license state in DB: `UPDATE license_states SET max_berths = 5 WHERE id = 1;`.
  2. Count current berths: `SELECT count(*) FROM berths;` (Assume 5 existing).
  3. Attempt to create 6th berth via UI or API: `POST /api/v1/berths`.
- Expected Result:
  - HTTP 422 Unprocessable Entity.
  - JSON body contains `code: "PLAN_LIMIT_EXCEEDED"`, `message_key: "errors.plan_limit_exceeded"`.
  - UI displays banner: "تم استنفاد الحد الأقصى للأرصفة المسموح بها في رخصتك (5 أرصفة)" (License berth limit reached).
- Required Evidence: HTTP 422 response payload and UI alert banner screenshot.

---

### 3.4 Procedure OP-04: Re-triggering Pending Recommendations on Berth Dimension Modification (DEC-06)
- Target Component: AI Dispatcher / Part 2 Solve Trigger
- Objective: Verify that modifying berth dimensions marks pending recommendations as REPLACED and re-triggers solving, while protecting confirmed plans.
- Verification Steps:
  1. Confirm Request #101 has a recommendation in `PENDING_REVIEW` on Berth 1.
  2. Confirm Request #80 has a plan in `PLAN_CONFIRMED` on Berth 1.
  3. Edit Berth 1 depth: reduce from 15.0m to 12.0m.
  4. Query recommendation and plan statuses in database.
- Expected Result:
  - Recommendation for Request #101 transitions to status `'REPLACED'`.
  - New Part 2 solve job is queued for Request #101.
  - Plan for Request #80 remains strictly `'PLAN_CONFIRMED'`.
- Required Evidence: Database snapshot showing recommendation status `REPLACED` and unchanged confirmed plan.

---

### 3.5 Procedure OP-05: Optimistic Concurrency Control (OCC) and Stale Version Handling
- Target Component: Write Handlers / Microsecond `updated_at` Check
- Objective: Verify that submitting a stale version token returns HTTP 409 VERSION_CONFLICT with current state.
- Verification Steps:
  1. Fetch Berth 1: note version token `2026-11-12T10:00:00.000000Z`.
  2. Open Berth 1 in two separate browser tabs (Tab A and Tab B).
  3. In Tab A, update berth name to "Damietta Berth 01 Alpha" and save.
  4. In Tab B, without refreshing, attempt to update berth name to "Damietta Berth 01 Beta" and save.
- Expected Result:
  - Tab A succeeds and updates version token.
  - Tab B fails with HTTP 409 Conflict.
  - UI displays concurrency dialog: "تم تعديل هذا السجل بواسطة مستخدم آخر. يرجى مراجعة البيانات المحدثة" (This record was modified by another user. Please reload current state).
- Required Evidence: Browser network tab showing HTTP 409 response and conflict modal screenshot.

---

## 4. Release Sign-off Checklist for QA-RT3 (v0.3.0)

| Requirement / Test Area | Verification Method | Status | Auditor Notes |
| :--- | :--- | :--- | :--- |
| FT-04: Port Profile and Channel Parameters | Manual UI (W-01) + Automated API | [ ] PASS / [ ] FAIL | Controlling depth datum LAT verified |
| FT-04: Berth Dimensions and LOA Constraint | Manual UI (W-02) + Schema Check | [ ] PASS / [ ] FAIL | chk_berth_loa_fits verified |
| FT-04: Shared Berths (DEC-51) | Manual UI (W-02) + Database Check | [ ] PASS / [ ] FAIL | Multi-terminal associations verified |
| FT-04: Soft Deactivation of Berths | Manual UI (W-02) + Integrity Check | [ ] PASS / [ ] FAIL | Historical foreign keys preserved |
| FT-04: Safety Constraints Overlap Prevention | Manual UI (W-03) + API Validation | [ ] PASS / [ ] FAIL | Overlapping intervals rejected |
| FT-04: AI Port Settings min/max Bounds (DEC-59) | Manual UI (W-04) + API Validation | [ ] PASS / [ ] FAIL | Range limits enforced |
| FT-04: Re-triggering Pending Recommendations (DEC-06) | Operational Test (OP-04) | [ ] PASS / [ ] FAIL | Confirmed plans protected |
| FT-05: Terminal Setup (CT vs NCT) | Manual UI (W-05) + Automated API | [ ] PASS / [ ] FAIL | Terminal types and boundaries verified |
| FT-05: Cross-Terminal Isolation (Tenant Security) | Automated API + Manual Test | [ ] PASS / [ ] FAIL | HTTP 404 NOT_FOUND returned |
| FT-05: Tugboat Fleet and Power Ratings | Manual UI (W-06) + Schema Check | [ ] PASS / [ ] FAIL | chk_tugboat_power > 0 verified |
| FT-05: Tug Master 1-to-1 Tugboat Assignment | Manual UI (W-07) + Database Check | [ ] PASS / [ ] FAIL | Unique assigned_tugboat_id enforced |
| FT-05: Atomic Tug Master Unbinding on Deactivation | Operational Test (OP-01, OP-02) | [ ] PASS / [ ] FAIL | Unbound in same DB transaction |
| FT-05: Pilot Seniority Ranks and LOA Limits | Manual UI (W-08) + API Validation | [ ] PASS / [ ] FAIL | pilot_rank_limits enforced |
| FT-05: Pilot Shift Availability Semantics (DEC-32) | Manual UI (W-08) + API Validation | [ ] PASS / [ ] FAIL | Availability derived from shifts & plans |
| FT-05: CT Equipment and Specialized Yard Zones | Manual UI (W-09) + Database Check | [ ] PASS / [ ] FAIL | Reefer, DG, OOG zones configured |
| License: Plan Limit Enforcement (422) | Operational Test (OP-03) | [ ] PASS / [ ] FAIL | PLAN_LIMIT_EXCEEDED returned |
| License: READ_ONLY Mode Enforcement (423) | Automated API + Operational Test | [ ] PASS / [ ] FAIL | LICENSE_READ_ONLY returned |
| Concurrency: OCC Version Token Check (409) | Operational Test (OP-05) | [ ] PASS / [ ] FAIL | VERSION_CONFLICT returned |
| Zero Blocker Defects Open | Bug Tracker / Issue Audit | [ ] PASS / [ ] FAIL | 0 Blocker defects open |
| Overall Sprint 3 Sign-off Verdict | QA Lead Formal Sign-off | [ ] PASS / [ ] FAIL | Release v0.3.0 readiness |

---

**Auditor Sign-off:**  
- QA Lead Auditor: Ma7moudWageeh  
- Date: 2026-11-12  
- Verdict: READY FOR SPRINT 3 RELEASE TESTING (QA-RT3)
