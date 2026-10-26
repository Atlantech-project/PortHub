# ATLANTECH — Team Contracts

This file lists every contract that two or more teams must agree on. For each contract it states:

- **Between:** who delivers and who receives.
- **Owner:** the team that writes the contract and keeps it current.
- **Reviewers:** the receiving teams, who must approve it.
- **Output:** the file or format that is delivered, with an example.

All contracts are written and approved in **Sprint 1**. Each contract has a task with the same ID (`CT-01` …). Any change after approval needs both sides to agree, an entry in the decision log, and a new version number.

**Proposed location:** a `contracts/` folder in the `PortHub` repository. Every OpenAPI file and JSON Schema in that folder is the single source of truth.

## Summary

| ID | Contract | From (owner) | To (receiver) | Related decision |
| --- | --- | --- | --- | --- |
| CT-01 | Port API conventions | Backend | Frontend · Mobile · QA | DEC-13 |
| CT-02 | Port API OpenAPI file | Backend | Frontend · Mobile · QA | DEC-13 |
| CT-03 | Web sign-in and session | Backend | Frontend | DEC-35 |
| CT-04 | Mobile sign-in and system info | Backend | Mobile | DEC-35 |
| CT-05 | Web SSE events | Backend | Frontend | DEC-05 |
| CT-06 | Mobile WebSocket events (Reverb) | Backend | Mobile | — |
| CT-07 | Mobile sync (Outbox) | Backend | Mobile | DEC-39 · DEC-40 |
| CT-08 | AI job envelope | AI (schema) · Backend (sending) | AI workers | DEC-04 |
| CT-09 | C-01 · Part 1 run | Backend | AI | DEC-14 |
| CT-10 | C-02 · Part 2 solve | Backend | AI | DEC-15 |
| CT-11 | C-03 · Yard placement | Backend | AI | DEC-16 |
| CT-12 | C-04 · BAPLIE parse | Backend | AI | DEC-17 |
| CT-13 | C-05 · Validation (`queue:validate`) | AI | Backend | DEC-03 · DEC-18 |
| CT-14 | C-06 · Completion message | AI | Backend | DEC-01 · DEC-19 |
| CT-15 | AI result tables and write ownership | AI | Backend | DEC-02 |
| CT-16 | Worker health over Redis | AI | Backend | DEC-10 |
| CT-17 | Database schema (migrations) | Backend | AI | DEC-08 |
| CT-18 | AI seed data and `port_setting` keys | AI | Backend | DEC-12 · DEC-23 |
| CT-19 | Mock worker behaviour | Backend | Frontend · Mobile · QA | — |
| CT-20 | AI result read endpoints | Backend | Frontend | DEC-43 |
| CT-21 | Shared status vocabulary | Backend | Frontend · Mobile · AI · QA | — |
| CT-22 | Screen design hand-off | UI/UX | Frontend · Mobile | — |
| CT-23 | API readiness pack (per FRR) | Backend | Frontend · Mobile · QA | DEC-13 |
| CT-24 | BAPLIE test corpus | QA | AI | DEC-17 |
| CT-25 | Reference data and thresholds inputs | QA | AI | DEC-30 · DEC-33 |
| CT-26 | QA report and defect format | QA | All teams | — |

---

## CT-01 · Port API conventions

| | |
| --- | --- |
| Between | Backend → Frontend · Mobile · QA |
| Owner | Backend Team |
| Reviewers | Frontend Team · Mobile Team · QA Team |
| Output | `contracts/api-conventions.md` |

**Content:**

- **Base path:** `/api/v1`. All times are ISO 8601 in UTC.
- **Headers:**
  - Web: cookie + `X-XSRF-TOKEN`.
  - Mobile: `Authorization: Bearer <token>`, `X-App-Version` and `X-Device-Id`.
  - Every mobile write carries an `Idempotency-Key`.
- **Version token:** every editable record returns a `version` (the `updated_at` value). Every update must send it back; a stale version returns 409.
- **Errors:** RFC 9457 format with a stable `code` and a `message_key`.
- **Error codes:** 401 · 403 · 409 · 422 · 426 · 503.
- **Pagination:** `?page=&per_page=`.

**Error example:**

```json
{
  "type": "https://atlantech.io/errors/version-conflict",
  "title": "Record changed",
  "status": 409,
  "code": "VERSION_CONFLICT",
  "message_key": "errors.version_conflict",
  "detail": "The berth was changed by another user.",
  "current": { "id": 12, "version": "2026-11-02T10:15:04Z" }
}
```

**422 example:**

```json
{
  "status": 422,
  "code": "VALIDATION_FAILED",
  "message_key": "errors.validation_failed",
  "errors": { "max_vessel_loa": ["errors.berth.loa_exceeds_length"] }
}
```

**Pagination example:**

```json
{ "data": [ { "id": 1 } ], "meta": { "page": 1, "per_page": 25, "total": 132 } }
```

---

## CT-02 · Port API OpenAPI file

| | |
| --- | --- |
| Between | Backend → Frontend · Mobile · QA |
| Owner | Backend Team (single owner, DEC-13) |
| Reviewers | Frontend Team · Mobile Team |
| Output | `contracts/openapi/port-api.yaml` (OpenAPI 3.0), updated in the same PR that changes an endpoint |

**Example:**

```yaml
paths:
  /api/v1/berthing-requests:
    post:
      summary: Create a berthing request
      tags: [Berthing]
      security: [{ cookieAuth: [] }]
      requestBody:
        content:
          application/json:
            schema: { $ref: '#/components/schemas/BerthingRequestCreate' }
      responses:
        '201': { content: { application/json: { schema: { $ref: '#/components/schemas/BerthingRequest' } } } }
        '403': { $ref: '#/components/responses/Forbidden' }
        '422': { $ref: '#/components/responses/ValidationFailed' }
components:
  schemas:
    BerthingRequestCreate:
      type: object
      required: [imo_number, requested_terminal_id, requested_eta, arrival_draft]
      properties:
        imo_number: { type: string, pattern: '^[0-9]{7}$' }
        requested_terminal_id: { type: integer }
        requested_eta: { type: string, format: date-time }
        arrival_draft: { type: number }
        cargo_lines: { type: array, items: { $ref: '#/components/schemas/CargoLine' } }
```

---

## CT-03 · Web sign-in and session

| | |
| --- | --- |
| Between | Backend → Frontend |
| Owner | Backend Team |
| Reviewers | Frontend Team |
| Output | Auth section of `port-api.yaml` + the flow steps in `contracts/auth-web.md` |

**Flow:**

1. `GET /sanctum/csrf-cookie`
2. `POST /api/v1/auth/login`
3. If `must_change_password = true`: `POST /api/v1/auth/change-password`
4. `POST /api/v1/auth/logout`

The sign-in identifier is set by DEC-35 (proposed: username).

```json
// POST /api/v1/auth/login
{ "username": "staff.ahmed", "password": "••••••••" }

// 200
{
  "id": 41,
  "name": "Port Staff",
  "role": "PORT_AUTHORITY_STAFF",
  "terminal_ids": [],
  "must_change_password": false
}

// 403
{ "status": 403, "code": "ACCOUNT_DISABLED", "message_key": "errors.account_disabled" }
```

---

## CT-04 · Mobile sign-in and system info

| | |
| --- | --- |
| Between | Backend → Mobile |
| Owner | Backend Team |
| Reviewers | Mobile Team |
| Output | Mobile auth section of `port-api.yaml` |

```json
// GET /api/v1/system/info
{ "port_id": "EGDAM", "port_name": "Damietta Port", "min_app_version": "1.0.0" }

// POST /api/v1/auth/mobile/login
{ "username": "pilot.k", "password": "••••••••", "device_id": "a1b2c3", "platform": "android", "app_version": "1.0.0" }

// 200
{
  "token": "<opaque>",
  "expires_at": "2026-12-02T10:00:00Z",
  "user": { "id": 77, "name": "Marine Pilot", "role": "MARINE_PILOT", "must_change_password": true }
}

// 426
{ "status": 426, "code": "APP_UPDATE_REQUIRED", "min_app_version": "1.1.0" }
```

---

## CT-05 · Web SSE events

| | |
| --- | --- |
| Between | Backend → Frontend |
| Owner | Backend Team |
| Reviewers | Frontend Team |
| Output | `contracts/realtime-sse.md`: the event list and the shape of each event |

`GET /api/v1/events` (`text/event-stream`):

- Events are filtered by role and terminal.
- After a dropped connection, `Last-Event-ID` replays the missed events.
- An event only says that something changed; the Frontend fetches the details over REST.

**Events:**
`REQUEST_STATUS_CHANGED` · `BAPLIE_PARSED` · `ENTRY_WINDOW_READY` · `RECOMMENDATION_READY` · `PLAN_CONFIRMED` · `PLAN_CANCELLED` · `ASSIGNMENT_CHANGED` · `NOTIFICATION_CREATED` · `NOTIFICATION_ACKNOWLEDGED` · `DEVIATION_DETECTED` · `REPLAN_PROPOSED` · `YARD_RECOMMENDATION_READY` · `YARD_RECOMMENDATION_FAILED` · `DRIFT_ALERT` · `RUN_FAILED`

```
id: 9f2c-0001
event: RECOMMENDATION_READY
data: {"entity":"berthing_request","id":1550,"recommendation_id":880,"status":"RECOMMENDATION_GENERATED","at":"2026-11-02T10:02:14Z"}
```

---

## CT-06 · Mobile WebSocket events (Reverb)

| | |
| --- | --- |
| Between | Backend → Mobile |
| Owner | Backend Team |
| Reviewers | Mobile Team |
| Output | `contracts/realtime-mobile.md` |

- **Channel:** `private-user.{user_id}`.
- **Event:** carries only the `event_id` and its type; the app fetches the details over REST.
- **Duplicates:** the app ignores any `event_id` it has already seen.
- **After every reconnect:** the app calls `GET /sync/changes`.

```json
{ "event_id": "e-77-000231", "type": "TASK_UPDATED", "entity": "plan_component", "entity_id": 5012 }
```

---

## CT-07 · Mobile sync (Outbox)

| | |
| --- | --- |
| Between | Mobile ↔ Backend |
| Owner | Backend Team (endpoints) · Mobile Team (event shape) |
| Reviewers | Mobile Team · Backend Team |
| Output | Sync section of `port-api.yaml` + `contracts/sync-events.md` |

**Event types:**

| Type | Payload | Note |
| --- | --- | --- |
| `STATUS_UPDATE` | `{ plan_component_id, new_status }` | In progress / Executed only (DEC-39) |
| `ACKNOWLEDGE` | `{ notification_id }` | DEC-40 |

```json
// POST /api/v1/sync/events
{
  "events": [
    {
      "client_event_id": "2c1f6a7e-1d0b-4c11-9a51-7f1e2b3c4d5e",
      "type": "STATUS_UPDATE",
      "payload": { "plan_component_id": 5012, "new_status": "STARTED" },
      "recorded_at": "2026-11-02T11:40:00Z",
      "client_sent_at": "2026-11-02T11:52:10Z",
      "sync_source": "TABLET"
    }
  ]
}

// 200: one result per event, in the same order
{
  "results": [
    { "client_event_id": "2c1f6a7e-…", "result": "APPLIED" },
    { "client_event_id": "8d9e…", "result": "REJECTED", "reason_code": "PLAN_CANCELLED" }
  ]
}

// GET /api/v1/sync/changes?since=tok_118
{ "tasks": [ ], "notifications": [ ], "removed": [ { "entity": "plan_component", "id": 5003 } ], "sync_token": "tok_131" }
```

`result` values: `APPLIED` · `DUPLICATE` · `REJECTED`.

---

## CT-08 · AI job envelope

| | |
| --- | --- |
| Between | Backend → AI |
| Owner | AI Team (JSON Schema) · Backend Team (sending with RPUSH) |
| Reviewers | Backend Team · AI Team |
| Output | `contracts/ai/envelope.schema.json` |

- **Queues:** `queue:part1` · `queue:part2` · `queue:edi`.
- **`job_type`:** `PART1_RUN` · `PART2_SOLVE` · `YARD_PLACEMENT` · `BAPLIE_PARSE`.
- **Idempotency:** the worker claims the run with a conditional update (QUEUED → RUNNING), so a second delivery of the same run is ignored.

**Updates from approved contracts (CT-11 · CT-13 · CT-14, 2026-10-27):**

| Queue | `job_type` | Worker account |
| --- | --- | --- |
| `queue:part1` | `PART1_RUN` | `w_part1` |
| `queue:part2` | `PART2_SOLVE` | `w_part2` |
| `queue:yard` | `YARD_PLACEMENT` | `w_yard` |
| `queue:edi` | `BAPLIE_PARSE` | `w_edi` |
| `queue:validate` | `VALIDATION` | `w_validate` |
| `queue:ai-results` | C-06 messages (worker → Backend) | — |

- `run_id` is `integer | null`: `null` only for `VALIDATION` (which also requires `triggered_by_user_id`); an integer for every other job type.
- Each payload schema (C-01 to C-05) describes the payload only and is referenced from `envelope.schema.json` with `if job_type = … then payload: { $ref }`.

**Error categories:**
`INVALID_ENVELOPE` · `PRECONDITION_FAILED` · `DATA_UNAVAILABLE` · `CONFIGURATION_ERROR` · `INFEASIBLE` · `SOLVER_ERROR` · `TIMEOUT` · `INTERNAL_ERROR`

```json
{
  "contract_version": "1.0",
  "job_type": "PART2_SOLVE",
  "job_id": "a2c9d1f0-1b77-4c2e-8f44-5d6e7f809a1b",
  "run_id": 2301,
  "enqueued_at": "2026-11-02T10:02:11Z",
  "triggered_by_user_id": 41,
  "payload": { }
}
```

---

## CT-09 · C-01 · Part 1 run

| | |
| --- | --- |
| Between | Backend → AI (Part 1) |
| Owner | Backend Team (sending) on the AI Team schema |
| Reviewers | AI Team |
| Output | `contracts/ai/c01-part1-run.schema.json` |

```json
{
  "contract_version": "1.0",
  "job_type": "PART1_RUN",
  "job_id": "3f6b2c1e-8a1d-4a51-9f1e-2b0c7d9e4a10",
  "run_id": 812,
  "enqueued_at": "2026-11-02T09:15:04Z",
  "triggered_by_user_id": 41,
  "payload": { "berthing_request_id": 1550, "reason": "CUSTOMS_APPROVAL" }
}
```

- **`reason` values:** `CUSTOMS_APPROVAL` · `RECOMPUTE` · `MANUAL_DATA` · `REOPEN`.
- With `MANUAL_DATA`, the payload also carries `manual_forecast_run_id`.
- **Result in the database:**
  - `part1_run`: status and outcome (`WINDOWS_FOUND` · `NO_FEASIBLE_WINDOW` · `ENV_DATA_UNAVAILABLE`).
  - `entry_window_proposal`, `feasible_window` and `blocked_period`.

---

## CT-10 · C-02 · Part 2 solve

| | |
| --- | --- |
| Between | Backend → AI (Part 2) |
| Owner | Backend Team (sending) on the AI Team schema |
| Reviewers | AI Team |
| Output | `contracts/ai/c02-part2-solve.schema.json` (payload only) |
| Status | Approved v1.0 · 2026-10-26 (DEC-15) |

The schema describes the **payload only**. `envelope.schema.json` (CT-08) references it with `if job_type = PART2_SOLVE then payload: { $ref: c02-part2-solve.schema.json }`. C-01, C-03 and C-04 follow the same pattern.

```json
{
  "contract_version": "1.0",
  "job_type": "PART2_SOLVE",
  "job_id": "b81e…",
  "run_id": 2302,
  "enqueued_at": "2026-11-02T12:20:00Z",
  "triggered_by_user_id": 41,
  "payload": {
    "trigger_type": "REPLAN",
    "triggers": [
      { "trigger_type": "NEW_REQUEST", "berthing_request_ids": [1560, 1561] },
      {
        "trigger_type": "RESOURCE_CHANGE",
        "berthing_request_ids": [1550, 1553],
        "changed_resources": [ { "type": "TUG", "id": 7 }, { "type": "BERTH", "id": 12 } ]
      },
      {
        "trigger_type": "MANUAL",
        "berthing_request_ids": [1548],
        "requested_by_user_id": 41,
        "context_note": "Agent asked to regenerate after cargo update"
      },
      { "trigger_type": "REPLAN", "berthing_request_ids": [1540], "operational_plan_id": 311 }
    ]
  }
}
```

**Trigger entries:**

| `trigger_type` | Sent by the Backend when | `berthing_request_ids` | Extra fields |
| --- | --- | --- | --- |
| `NEW_REQUEST` | Part 1 finishes with `WINDOWS_FOUND` | Requests in `ENTRY_WINDOW_CONFIRMED` or `RECOMMENDATION_GENERATED` | — |
| `MANUAL` | A user presses "Regenerate" | Same as `NEW_REQUEST` | `requested_by_user_id` (required) |
| `RESOURCE_CHANGE` | A berth, tug or pilot becomes unavailable or available again | Pending requests whose current recommendation uses a changed resource, or whose window overlaps the change. The Backend computes this from `recommendation_option` and `recommendation_option_tug` | `changed_resources` (required, `minItems: 1`) |
| `REPLAN` | A deviation is recorded on a confirmed plan | Exactly one: the request that owns the plan | `operational_plan_id` (required) |

- `changed_resources[].type`: `BERTH` · `TUG` · `PILOT` (closed enum for v1). `id` is `berth.id`, `tugboat.id` or the pilot's `user.id`. A tug master shift change is sent as `TUG` with the tug's id (DEC-32). The worker reads the current resource state from the database, so no "what changed" field is sent.
- `changed_resources` is forbidden outside `RESOURCE_CHANGE`; `operational_plan_id` is forbidden outside `REPLAN`; `requested_by_user_id` is forbidden outside `MANUAL`.
- `context_note`: optional on every entry, `string | null`, `maxLength: 500`. Logs only: not stored in result tables, not used by the solve, never in the rationale.
- `berthing_request_ids` has `minItems: 1` in every entry.
- `purpose` is not sent. The AI derives it per request and writes it to `recommendation.purpose`: `DELAY_REPLAN` for a request in a `REPLAN` entry, `INITIAL` otherwise.

**Backend sending rules:**

- **One solve at a time:** the Backend never enqueues a `PART2_SOLVE` while another is QUEUED or RUNNING. Triggers that arrive meanwhile are held and merged into one message sent when the current solve finishes.
- **`payload.trigger_type`** is the highest-precedence type in `triggers`: `REPLAN > RESOURCE_CHANGE > MANUAL > NEW_REQUEST`. The Backend writes it to `solver_run.trigger_type`.
- **One entry per request:** a request id appears in at most one entry. If two triggers hit the same request, the higher-precedence entry wins; two `RESOURCE_CHANGE` entries merge their `changed_resources`.
- **No empty solves:** a resource change that affects no pending request is not enqueued.
- **Confirmed plans change only through `REPLAN`:** a resource change that hits a confirmed plan is sent as a `REPLAN` entry for that plan.
- **Envelope `triggered_by_user_id`:** the `requested_by_user_id` of the MANUAL entry if there is one, otherwise `null`. With several MANUAL entries, it is the user of the MANUAL trigger the Backend received last.
- The Backend validates every message against the schema before RPUSH.

**Solve scope (DEC-06, Option 2):** the variable set is the union of `berthing_request_ids` across all entries. Every confirmed plan and every other pending recommendation is fixed and treated as occupied capacity. When the Backend receives C-06, it marks REPLACED only the previous `PENDING_REVIEW` version of each request in the message that got a new recommendation.

**`solver_run.result_detail` (written by the AI):**

```json
{
  "outcome": "PARTIALLY_SOLVED",
  "failure_reason": null,
  "requests": [
    { "request_id": 1550, "outcome": "SOLVED", "purpose": "INITIAL", "recommendation_id": 880, "options_count": 2, "binding_constraints": [] },
    {
      "request_id": 1553, "outcome": "NO_FEASIBLE_PLAN", "purpose": "INITIAL", "recommendation_id": null, "options_count": 0,
      "binding_constraints": [
        { "kind": "STRUCTURAL", "constraint_type_code": "MAX_LOA", "detail": "No berth in terminal DCT accepts LOA 366 m" }
      ]
    }
  ]
}
```

**Run-level `outcome`** (the same value is sent as `outcome` in C-06):

| `outcome` | `solver_run.status` | Recommendations written |
| --- | --- | --- |
| `SOLVED` | `OPTIMAL` / `FEASIBLE` | For every request |
| `PARTIALLY_SOLVED` | `OPTIMAL` / `FEASIBLE` | For some requests; the others are `NO_FEASIBLE_PLAN` |
| `NO_FEASIBLE_PLAN` | `INFEASIBLE` | None. Requests stay `ENTRY_WINDOW_CONFIRMED` |
| `FIFO_FALLBACK` | `ERROR` | FIFO plans (`source = FIFO`) for the requests that pass the hard filter. C-06 carries `status = DONE` (plans were written) with the technical reason in `error_category`, while `solver_run.status` stays `ERROR` (CT-14) |
| `GENERATION_FAILED` | `ERROR` | None |

- **Per-request `outcome`:** `SOLVED` · `FIFO_FALLBACK` · `NO_FEASIBLE_PLAN`.
- **`options_count`:** 1 to 3 when a recommendation is written, otherwise 0 (DEC-23). Options 2 and 3 are returned only within `solver_option_equivalence_pct` of option 1 (CT-18).
- **`binding_constraints`:** non-empty only when the per-request outcome is `NO_FEASIBLE_PLAN`. `detail` is an English diagnostic string, at most 255 characters.
  - `kind = "SAFETY"`: `constraint_type_code` is any `constraint_type.code` from the CT-18 seed (for example `MAX_WIND_KN`).
  - `kind = "STRUCTURAL"`: closed list for v1: `MAX_LOA` · `MAX_DRAFT` · `TERMINAL_COMPATIBILITY` · `BERTH_UNAVAILABLE` · `BERTH_OCCUPIED` · `TUG_UNAVAILABLE` · `PILOT_UNAVAILABLE` · `ENTRY_WINDOW`. Adding a code is a minor version change (1.x).
- **`failure_reason`:** non-null only when `solver_run.status = ERROR` (`FIFO_FALLBACK` or `GENERATION_FAILED`):

```json
"failure_reason": { "error_category": "TIMEOUT", "message": "CP-SAT reached solver_time_limit_seconds (10) without a feasible solution" }
```

  - `error_category` (CT-08 list): `PRECONDITION_FAILED` · `DATA_UNAVAILABLE` · `CONFIGURATION_ERROR` · `SOLVER_ERROR` · `TIMEOUT` · `INTERNAL_ERROR`. `INFEASIBLE` is never used for Part 2. C-06 carries the same value.
  - `message`: diagnostic text, at most 1,000 characters, never shown to end users.

---

## CT-11 · C-03 · Yard placement

| | |
| --- | --- |
| Between | Backend → AI (yard worker) |
| Owner | Backend Team (sending) on the AI Team schema |
| Reviewers | AI Team |
| Output | `contracts/ai/c03-yard.schema.json` (payload only) |
| Status | Approved v1.0 · 2026-10-27 (DEC-16) |

The schema describes the **payload only**. `envelope.schema.json` (CT-08) references it with `if job_type = YARD_PLACEMENT`. The job runs on its own queue, **`queue:yard`**, served by a separate worker process (own DB account and grants per DEC-08, own heartbeat).

```json
{
  "contract_version": "1.0",
  "job_type": "YARD_PLACEMENT",
  "job_id": "c4d…",
  "run_id": 97,
  "enqueued_at": "2026-11-02T13:00:00Z",
  "triggered_by_user_id": null,
  "payload": { "terminal_recommendation_id": 640, "operational_plan_id": 311 }
}
```

- Both payload fields are required. `run_id` is `yard_run.id`, not `terminal_recommendation_id`.
- `operational_plan_id` lets the worker check that the plan is still the confirmed plan of that recommendation.

**Backend sending rules:**

- **When:** once both hold: the `operational_plan` is CONFIRMED on a CONTAINER terminal, **and** the request has an ACTIVE `baplie_file` with `parse_status = PARSED`. Whichever happens last triggers the job.
- **One transaction before RPUSH:** set `terminal_recommendation` (`rec_type = YARD_PLACEMENT`, `lifecycle_status = YARD_REC_REQUESTED`) and insert `yard_run` (QUEUED).
- **`triggered_by_user_id`:** `null` for the automatic trigger; the user who pressed "Regenerate" otherwise.
- **Regenerate:** offered when `lifecycle_status` is `GENERATION_FAILED` or `YARD_REC_REJECTED`. Because of `uq_tr_rec_type`, the same row is reused: reset to `YARD_REC_REQUESTED`, delete the old `yard_placement_item` rows, mark any QUEUED or RUNNING `yard_run` of that row as `REPLACED`, then insert a new `yard_run`.
- **Stale recommendation:** after a confirmed REPLAN or a BAPLIE revision becoming ACTIVE, the Backend regenerates automatically if the recommendation is not yet `YARD_REC_ACCEPTED`. If it is accepted, the Backend raises a notification only.
- **Incomplete lines:** the Backend blocks yard recommendations while any line of the ACTIVE file has a NULL `full_empty` **or** a NULL `port_of_discharge`.
- **No one-at-a-time rule:** different terminal recommendations may run in parallel; `uq_yr_active` allows one active run per terminal recommendation.
- The Backend validates every message against the schema before RPUSH.

**`yard_run` table (added by the Backend through CT-17):**

```sql
CREATE TABLE `yard_run` (
  `id` bigint PRIMARY KEY AUTO_INCREMENT,
  `terminal_recommendation_id` bigint NOT NULL,
  `triggered_by` bigint NULL,
  `status` ENUM ('QUEUED', 'RUNNING', 'DONE', 'FAILED', 'REPLACED') NOT NULL DEFAULT 'QUEUED',
  `outcome` ENUM ('YARD_REC_GENERATED', 'GENERATION_FAILED') NULL,
  `error_category` ENUM ('INVALID_ENVELOPE', 'PRECONDITION_FAILED', 'DATA_UNAVAILABLE',
                         'CONFIGURATION_ERROR', 'INFEASIBLE', 'TIMEOUT', 'INTERNAL_ERROR') NULL,
  `retry_count` tinyint NOT NULL DEFAULT 0,
  `result_detail` json NULL,
  `worker_version` varchar(40) NULL,
  `queued_at` datetime NOT NULL DEFAULT (CURRENT_TIMESTAMP),
  `started_at` datetime NULL,
  `finished_at` datetime NULL,
  `active_key` bigint GENERATED ALWAYS AS
    (IF(status IN ('QUEUED', 'RUNNING'), terminal_recommendation_id, NULL)) STORED,
  UNIQUE KEY `uq_yr_active` (`active_key`),
  KEY `idx_yr_tr` (`terminal_recommendation_id`),
  CONSTRAINT `fk_yr_tr` FOREIGN KEY (`terminal_recommendation_id`) REFERENCES `terminal_recommendation` (`id`),
  CONSTRAINT `fk_yr_user` FOREIGN KEY (`triggered_by`) REFERENCES `user` (`id`),
  CONSTRAINT `chk_yr_finished` CHECK (status IN ('QUEUED', 'RUNNING', 'REPLACED') OR finished_at IS NOT NULL),
  CONSTRAINT `chk_yr_outcome` CHECK (
       (status = 'DONE'   AND outcome = 'YARD_REC_GENERATED')
    OR (status = 'FAILED' AND outcome = 'GENERATION_FAILED')
    OR (status IN ('QUEUED', 'RUNNING', 'REPLACED') AND outcome IS NULL)),
  CONSTRAINT `chk_yr_error` CHECK ((status = 'FAILED') = (error_category IS NOT NULL))
);
```

**Run flow:**

| Step | Who | What |
| --- | --- | --- |
| 1 | Backend | Sets `YARD_REC_REQUESTED`, inserts `yard_run` (QUEUED), RPUSH with `run_id = yard_run.id` |
| 2 | AI | Claims: `UPDATE yard_run SET status='RUNNING', started_at=… WHERE id=? AND status='QUEUED'`. 0 rows → duplicate or replaced delivery, ignore |
| 3 | AI | One transaction: inserts `yard_placement_item` rows; on `terminal_recommendation` sets `lifecycle_status`, `confidence`, `rationale_template_id`, `failure_reason`; sets `yard_run` to DONE or FAILED. Before commit it re-checks that the run is still RUNNING and the row still `YARD_REC_REQUESTED`; otherwise it rolls back and sends nothing |
| 4 | AI | Sends C-06 with `job_type = YARD_PLACEMENT` and `outcome = YARD_REC_GENERATED` or `GENERATION_FAILED` |

**Worker preconditions (in order):**

| # | Check | If it fails |
| --- | --- | --- |
| 1 | `yard_run` is QUEUED (claim succeeds) | Ignore silently |
| 2 | `terminal_recommendation` exists, `rec_type = YARD_PLACEMENT`, `lifecycle_status = YARD_REC_REQUESTED` | `PRECONDITION_FAILED` |
| 3 | `operational_plan` exists, `status = CONFIRMED`, and its `recommendation_id` equals `terminal_recommendation.recommendation_id` | `PRECONDITION_FAILED` |
| 4 | Terminal type is `CONTAINER` | `PRECONDITION_FAILED` |
| 5 | The request has an ACTIVE `baplie_file` with `parse_status = PARSED` | `PRECONDITION_FAILED` |
| 6 | No line has a NULL `full_empty` or a NULL `port_of_discharge` | `PRECONDITION_FAILED` |
| 7 | At least one container is in scope | `PRECONDITION_FAILED` |
| 8 | The terminal has a container yard with active slots | `CONFIGURATION_ERROR` |

**Containers in scope:** `container_manifest_entry` rows of the request's ACTIVE `baplie_file` with `port_of_discharge = port_profile.port_code`. Transshipment and empty containers are included; remain-on-board is excluded; export containers are not in the BAPLIE (DEC-28).

**Result:**

- **Partial placement:** if at least one container is placed, the outcome is `YARD_REC_GENERATED` and unplaced containers get no `yard_placement_item` row. If none can be placed, the outcome is `GENERATION_FAILED` with `INFEASIBLE`.
- **`yard_slot_id`:** always `NULL` in v1 (block level, FR-2.2.3). Nothing the worker writes is a reservation; any capacity check at accept or export time belongs to the Backend.
- **Capacity counting:** active slots with `container_id IS NULL`, minus capacity already given to other recommendations of the same terminal in `YARD_REC_GENERATED` or `YARD_REC_ACCEPTED` (not yet exported). Counted in TEU via `container_size_type.teu_factor`, 1 slot = 1 TEU.
- **`confidence`** = `preferred_zone_count / in_scope_count`, rounded to 3 decimals (DEC-29 Option A). Never null with `YARD_REC_GENERATED`, always null with `GENERATION_FAILED`. Reefer, DG and OOG containers can only go to their zone; general containers may overflow to a special zone and then count as not preferred.

**`yard_run.result_detail`:**

```json
{
  "in_scope_count": 212,
  "placed_count": 208,
  "preferred_zone_count": 200,
  "unplaced": [
    { "manifest_entry_id": 99812, "reason_code": "NO_REEFER_CAPACITY" },
    { "manifest_entry_id": 99840, "reason_code": "NO_DG_ZONE" }
  ],
  "failure_reason": null
}
```

- **`unplaced[].reason_code`** (closed list for v1): `NO_REEFER_CAPACITY` · `NO_DG_ZONE` · `NO_OOG_ZONE` · `NO_CAPACITY`.
- **`failure_reason`:** `{ "error_category": "...", "message": "..." }`, same shape as C-02, non-null only when the run is FAILED. `terminal_recommendation.failure_reason` holds `"<ERROR_CATEGORY>: <message>"` truncated to 500 characters.
- **`error_category`** for yard: `INVALID_ENVELOPE` · `PRECONDITION_FAILED` · `CONFIGURATION_ERROR` (no container yard, no active slots or no active rationale template) · `DATA_UNAVAILABLE` · `INFEASIBLE` · `TIMEOUT` · `INTERNAL_ERROR`. `SOLVER_ERROR` is not used.

**Impact on other contracts:** CT-08 queue list becomes `queue:part1` · `queue:part2` · `queue:yard` · `queue:edi`. CT-17 adds `yard_run`. CT-19 maps the mock yard row to `queue:yard`. CT-15 must record that the yard worker writes `lifecycle_status`, `confidence` and `failure_reason` on `terminal_recommendation` (DEC-02).

---

## CT-12 · C-04 · BAPLIE parse

| | |
| --- | --- |
| Between | Backend → AI (EDI parser) |
| Owner | Backend Team (sending) on the AI Team schema |
| Reviewers | AI Team |
| Output | `contracts/ai/c04-baplie.schema.json` (payload only) |
| Status | Approved v1.0 · 2026-10-27 (DEC-17) |

The schema describes the **payload only**, referenced from `envelope.schema.json` with `if job_type = BAPLIE_PARSE`.

```json
{
  "contract_version": "1.0",
  "job_type": "BAPLIE_PARSE",
  "job_id": "d9a…",
  "run_id": 318,
  "enqueued_at": "2026-11-02T08:05:00Z",
  "triggered_by_user_id": 41,
  "payload": { "baplie_file_id": 205, "source": "FILE" }
}
```

| Field | Type | Rule |
| --- | --- | --- |
| `baplie_file_id` | integer ≥ 1 | Required |
| `source` | `FILE` · `STAGED_PAYLOAD` | Required. `FILE` = parse the uploaded file. `STAGED_PAYLOAD` = re-validate and commit the staff-corrected `staged_payload` of a QUARANTINED file |

`additionalProperties: false`. `run_id` is `baplie_parse_run.id`, not `baplie_file_id`.

**Backend sending rules:**

- **Upload:** the Backend stores the file and its SHA-256, inserts `baplie_file` (`STAGED`, `PENDING`) and `baplie_parse_run` (QUEUED) in one transaction, then RPUSH. `triggered_by_user_id = uploaded_by`.
- **Upload limits:** max 10 MB; extensions `.edi` · `.txt` · `.baplie`.
- **Duplicate file:** same hash for the same request → 409 at upload (`uq_bf_request_live_hash`).
- **One parse at a time per request:** no new upload while a file of the same request is `PENDING` → 409.
- **Retries:** technical failures are retried once (DEC-04). `REJECTED` and `QUARANTINED` are never retried.
- The Backend validates every message against the schema before RPUSH.

**`baplie_parse_run` table (added by the Backend through CT-17):**

```sql
CREATE TABLE `baplie_parse_run` (
  `id` bigint PRIMARY KEY AUTO_INCREMENT,
  `baplie_file_id` bigint NOT NULL,
  `source` ENUM ('FILE', 'STAGED_PAYLOAD') NOT NULL DEFAULT 'FILE',
  `triggered_by` bigint NULL,
  `status` ENUM ('QUEUED', 'RUNNING', 'DONE', 'FAILED', 'REPLACED') NOT NULL DEFAULT 'QUEUED',
  `outcome` ENUM ('PARSED', 'QUARANTINED', 'REJECTED') NULL,
  `error_category` ENUM ('INVALID_ENVELOPE', 'PRECONDITION_FAILED', 'DATA_UNAVAILABLE',
                         'CONFIGURATION_ERROR', 'TIMEOUT', 'INTERNAL_ERROR') NULL,
  `retry_count` tinyint NOT NULL DEFAULT 0,
  `container_count` int NULL,
  `result_detail` json NULL,
  `worker_version` varchar(40) NULL,
  `queued_at` datetime NOT NULL DEFAULT (CURRENT_TIMESTAMP),
  `started_at` datetime NULL,
  `finished_at` datetime NULL,
  `active_key` bigint GENERATED ALWAYS AS
    (IF(status IN ('QUEUED', 'RUNNING'), baplie_file_id, NULL)) STORED,
  UNIQUE KEY `uq_bpr_active` (`active_key`),
  KEY `idx_bpr_file` (`baplie_file_id`),
  CONSTRAINT `fk_bpr_file` FOREIGN KEY (`baplie_file_id`) REFERENCES `baplie_file` (`id`),
  CONSTRAINT `fk_bpr_user` FOREIGN KEY (`triggered_by`) REFERENCES `user` (`id`),
  CONSTRAINT `chk_bpr_finished` CHECK (status IN ('QUEUED', 'RUNNING', 'REPLACED') OR finished_at IS NOT NULL),
  CONSTRAINT `chk_bpr_outcome` CHECK (
       (status = 'DONE' AND outcome IS NOT NULL)
    OR (status <> 'DONE' AND outcome IS NULL)),
  CONSTRAINT `chk_bpr_error` CHECK ((status = 'FAILED') = (error_category IS NOT NULL))
);
```

**Run flow:**

| Step | Who | What |
| --- | --- | --- |
| 1 | Backend | Inserts `baplie_parse_run` (QUEUED) and RPUSH, in one transaction with the upload or the correction save |
| 2 | AI | Claims: `UPDATE … SET status='RUNNING' WHERE id=? AND status='QUEUED'`. 0 rows → ignore |
| 3 | AI | One all-or-nothing transaction: data rows, `baplie_parse_issue` rows, `baplie_file.parse_status` (and `staged_payload` when QUARANTINED). The final run update is guarded by `AND status = 'RUNNING'`; 0 rows → roll back everything and send nothing |
| 4 | AI | Sends C-06 with `job_type = BAPLIE_PARSE` and the outcome |
| 5 | Backend | On `PARSED`, in one transaction: new file → `ACTIVE`, previous ACTIVE → `REPLACED`. On anything else the file stays `STAGED` and the previous ACTIVE file stays ACTIVE |

The worker never writes `baplie_file.status` (DEC-08). Between step 3 and step 5 the file is PARSED but still STAGED; Part 1 and yard read only the ACTIVE file.

**Outcomes:**

| Run result | `parse_status` | Meaning | What the user does |
| --- | --- | --- | --- |
| DONE · `PARSED` | `PARSED` | Data committed. May carry `WARNING` issues | Nothing, or fix incomplete lines |
| DONE · `QUARANTINED` | `QUARANTINED` | Readable BAPLIE with at least one `ERROR` issue. Nothing committed; extracted data in `staged_payload` | Correct on the quarantine screen |
| DONE · `REJECTED` | `FAILED` | Not a usable BAPLIE: not UN/EDIFACT, not a BAPLIE message, unsupported version, or corrupted | Upload a new file |
| FAILED · `error_category` | `FAILED` | Technical error. Retried once (DEC-04) | Retry, or contact support |

- **ERROR issues (→ QUARANTINED):** IMO in the file ≠ `vessel.imo_number` of the request · duplicate container number in the file · unknown ISO size type · unknown `imdg_class` · malformed value (weight, UN/LOCODE, temperature outside −40 … 40) · reefer without set temperature.
- **WARNING issues (→ still PARSED):** wrong container check digit · missing `full_empty` (written NULL) · missing `port_of_discharge` (written NULL) · vessel name differs from `vessel.name` · existing container with a different size type.
- The Backend blocks customs approval and yard recommendations while any line has a NULL `full_empty` or a NULL `port_of_discharge`.
- **Supported BAPLIE versions (v1.0):**

  | SMDG BAPLIE | UN/EDIFACT directory | `UNH` message identifier |
  | --- | --- | --- |
  | 2.2.1 (VGM) | D.95B | `BAPLIE:D:95B:UN:SMDG22` |
  | 3.1.1 (VGM) | D.13B | `BAPLIE:D:13B:UN:SMDG31` |

  The version is detected from the `UNH` segment (type, version, release, agency). The association code is read but not required to match: 2.x files of the D.95B family (2.1, 2.1.1, 2.2) are parsed with the 2.2.1 rules. Any other directory (for example BAPLIE 1.5), a version still in development (2.3, 3.2), a different message type or a non-EDIFACT file → `REJECTED` with one ERROR issue: `segment_ref = "UNH"`, `message = "Unsupported BAPLIE version: <found>. Supported: SMDG 2.2.1 (D.95B), SMDG 3.1.1 (D.13B)"`. Adding a version is a minor change (1.x).
  - Schema description text: *The EDI Parser accepts SMDG BAPLIE 2.2.1 (UN/EDIFACT D.95B) and SMDG BAPLIE 3.1.1 (UN/EDIFACT D.13B), detected from the UNH message identifier. Any other version, message type or non-EDIFACT file ends as outcome REJECTED (parse_status FAILED) with an ERROR issue on segment UNH.*

**Where failure reasons live:** parse problems (including `REJECTED` reasons) → `baplie_parse_issue` rows. Technical failures → `baplie_parse_run.error_category` and `result_detail.failure_reason = { "error_category", "message" }`, same shape as C-02 and C-03. No column is added to `baplie_file`.

```json
{
  "container_count": 1840,
  "discharged_here_count": 612,
  "issue_counts": { "ERROR": 0, "WARNING": 3 },
  "vessel_fields_filled": ["call_sign"],
  "parse_time_ms": 4210,
  "failure_reason": null
}
```

**Quarantine and correction:**

`staged_payload` (written by the worker, edited on the quarantine screen):

```json
{
  "format_version": "1.0",
  "vessel": { "imo_number": "9811000", "name": "MSC EXAMPLE", "call_sign": "3FAB7" },
  "lines": [
    {
      "line_no": 1,
      "segment_ref": "LOC+147+0010282",
      "container_number": "MSCU1234565",
      "iso_size_type": "45G1",
      "full_empty": "FULL",
      "weight_kg": 24500,
      "imdg_class": null,
      "oog": { "front_cm": null, "back_cm": null, "right_cm": null, "left_cm": null, "height_cm": null },
      "reefer_set_temperature": null,
      "stowage": { "bay": 1, "row": 2, "tier": 82 },
      "port_of_load": "CNSHA",
      "port_of_discharge": "EGDAM",
      "issues": [ { "severity": "ERROR", "code": "UNKNOWN_SIZE_TYPE", "message": "Size type 45X9 not found" } ]
    }
  ]
}
```

1. Staff edit lines. The Backend saves the edited `staged_payload` and sets `is_manually_corrected`, `corrected_by`, `corrected_at` (audited).
2. The Backend enqueues a new run with `source = STAGED_PAYLOAD`.
3. The worker re-validates `staged_payload` with the same rules. Still has ERROR issues → QUARANTINED again with refreshed issues. Clean → commits exactly like a PARSED file.

All commit logic for `container` / `container_manifest_entry` / `vessel` stays in the worker; the Backend never writes those rows from a BAPLIE. `staged_payload` is shown only to the owning agent and the terminal (§42 isolation).

**`container` rows:** upsert by `container_number` (uppercase, no spaces). New number → insert with `size_type_id`. Existing number → no update; a different size type keeps the stored value and adds a WARNING.

**`vessel` rows:** the worker fills only NULL `call_sign` and `flag_state`; it never overwrites a value. `imo_number` mismatch → ERROR; `name` mismatch → WARNING. Filled columns are listed in `result_detail.vessel_fields_filled`.

**Performance:** no size classes in this contract. NFR-PERF-2 is removed from the MVP (Leads Council, 2026-10-27).

**Impact on other contracts:** CT-17 adds `baplie_parse_run`. CT-13 / DEC-03: BAPLIE correction validation runs on the worker through `source = STAGED_PAYLOAD`. CT-14: C-06 for BAPLIE carries `outcome` = `PARSED` · `QUARANTINED` · `REJECTED`, or `error_category` on a FAILED run.

---

## CT-13 · C-05 · Validation (`queue:validate`)

| | |
| --- | --- |
| Between | Backend → AI (`w_validate`) → Backend |
| Owner | AI Team |
| Reviewers | Backend Team |
| Output | `contracts/ai/c05-validation.schema.json` (payload only) |
| Status | Approved v1.0 · 2026-10-27 (DEC-03 · DEC-18) |

FastAPI is cancelled (DEC-10), so validation is an async job. A result with violations is a **warning**: the officer can still confirm with a reason (DEC-03).

| Validation | Where |
| --- | --- |
| `OVERRIDE` (berth, pilot, tug, start time) | `queue:validate` → `w_validate` (this contract) |
| `YARD_ADJUSTMENT` | `queue:validate` → `w_validate` (this contract) |
| BAPLIE correction | `queue:edi` → `w_edi`, a `BAPLIE_PARSE` job with `source = STAGED_PAYLOAD` (CT-12) |
| Window re-check on confirm | Laravel (DEC-03) |

**Flow:**

| Step | Who | What |
| --- | --- | --- |
| 1 | Backend | Stores the proposed change under a new `job_id` in Redis (TTL `validation_result_ttl_seconds`), RPUSHes a `VALIDATION` job and answers **202** with the `job_id` |
| 2 | AI | `w_validate` reads port state from the primary and checks the change. It writes **nothing** to the DB |
| 3 | AI | Sends C-06 with `job_type = VALIDATION`, the same `job_id` and `validation_result` |
| 4 | Backend | Matches C-06 by `job_id`, keeps the result for `validation_result_ttl_seconds`, sends an SSE event to that officer |
| 5 | Officer | `VALID` → confirms. `VIOLATIONS` → sees each broken constraint and may still confirm with a reason |
| 6 | Backend | Applies the override only if the result exists, has not expired, and was produced for the **same proposed change** and the **same recommendation version**. An override with violations is audited with `action = SAFETY_EXCEPTION` |

- **Fail closed:** no result within `validation_timeout_seconds` (15) → "validation unavailable" and the change is refused. A missing check is not a checked warning.
- **Recommendation version (Backend):** `recommendation` has no version column, so the Backend stores with the job the recommendation `status` and the latest `recommendation_override.id` of that option; the result is valid only if both are unchanged at confirm time.

**Envelope:** `job_type = VALIDATION`, `run_id = null` (no run table; `job_id` is the correlation key), `triggered_by_user_id` = the officer, never retried (the Backend timeout covers a lost job).

```json
{
  "contract_version": "1.0",
  "job_type": "VALIDATION",
  "job_id": "7c1e4b2a-9d3f-4e8a-b6c5-1f2e3d4c5b6a",
  "run_id": null,
  "enqueued_at": "2026-11-02T10:20:00Z",
  "triggered_by_user_id": 41,
  "payload": {
    "validation_type": "OVERRIDE",
    "subject_id": 9031,
    "proposed_change": {
      "changes": [
        { "component_type": "BERTH", "override_berth_id": 14 },
        { "component_type": "TUG", "original_tugboat_id": 7, "override_tugboat_id": 11 }
      ]
    }
  }
}
```

```json
{
  "validation_type": "YARD_ADJUSTMENT",
  "subject_id": 640,
  "proposed_change": { "placements": [ { "manifest_entry_id": 99812, "yard_block_id": 31, "yard_slot_id": null } ] }
}
```

**Payload rules** (full schema in `c05-validation.schema.json`):

- `subject_id` = `recommendation_option.id` for `OVERRIDE`, `terminal_recommendation.id` for `YARD_ADJUSTMENT`.
- `OVERRIDE.changes`: 1 to 8 items, validated together as one plan. Items: `BERTH` (`override_berth_id`) · `PILOT` (`override_pilot_user_id`) · `TUG` (`original_tugboat_id`, `override_tugboat_id`; null original = added, null override = removed, never both null) · `START_TIME` (`override_start`).
- `YARD_ADJUSTMENT.placements`: only the changed containers, each with `manifest_entry_id`, `yard_block_id`, `yard_slot_id` (nullable).
- **Checked by the Backend before RPUSH** (the worker returns `INVALID_ENVELOPE` otherwise): at most one `BERTH`, one `PILOT` and one `START_TIME` item; a `manifest_entry_id` appears at most once.

**Preconditions** (C-06 `FAILED` / `PRECONDITION_FAILED`):

| `validation_type` | Check |
| --- | --- |
| `OVERRIDE` | `recommendation_option` exists and its recommendation is `PENDING_REVIEW` or `MODIFIED_BY_STAFF` |
| `YARD_ADJUSTMENT` | `terminal_recommendation` exists, `rec_type = YARD_PLACEMENT`, `lifecycle_status` is `YARD_REC_GENERATED` or `YARD_REC_ACCEPTED`; every `manifest_entry_id` belongs to the ACTIVE BAPLIE of that request; every block belongs to the terminal's yard |

**Result** (`validation_result` in C-06, defined in `c06-completion.schema.json`):

```json
{
  "validation_type": "OVERRIDE",
  "subject_id": 9031,
  "valid": false,
  "violations": [
    { "kind": "STRUCTURAL", "constraint_type_code": "MAX_DRAFT", "is_hard_safety_limit": false,
      "message_key": "validation.berth.draft_exceeded", "detail": "Arrival draft 14.2 m exceeds berth B14 depth 13.5 m",
      "change_index": 0, "manifest_entry_id": null },
    { "kind": "SAFETY", "constraint_type_code": "MIN_UKC_M", "is_hard_safety_limit": true,
      "message_key": "validation.ukc.below_minimum", "detail": "UKC 0.4 m at berth B14 on 2026-11-03 06:00 is below the minimum 0.8 m",
      "change_index": null, "manifest_entry_id": null }
  ]
}
```

- `kind = SAFETY`: `constraint_type_code` from the CT-18 seed; `is_hard_safety_limit` copied from that row. `kind = STRUCTURAL`: codes below; `is_hard_safety_limit` always `false`.
- `change_index`: index in `changes` (`null` when the problem comes from the combination). `manifest_entry_id`: the container concerned (yard).
- At most 500 violations; `violations_truncated = true` if there were more. `message_key` ≤ 120, `detail` ≤ 255 characters.
- **STRUCTURAL codes, `OVERRIDE`:** `MAX_LOA` · `MAX_DRAFT` · `TERMINAL_COMPATIBILITY` · `BERTH_UNAVAILABLE` · `BERTH_OCCUPIED` · `TUG_UNAVAILABLE` · `TUG_COUNT` (DEC-20) · `PILOT_UNAVAILABLE` (DEC-32) · `PILOT_RANK_LIMIT` · `ENTRY_WINDOW`.
- **STRUCTURAL codes, `YARD_ADJUSTMENT`:** `YARD_REEFER_PLUG` · `YARD_DG_CLASS` · `YARD_OOG_LIMIT` · `YARD_BLOCK_CAPACITY` (CT-11 counting rule) · `YARD_SLOT_OCCUPIED` · `YARD_SLOT_BLOCKED`.

**New `port_setting` keys (CT-18):** `validation_timeout_seconds` = 15 · `validation_result_ttl_seconds` = 600.

---

## CT-14 · C-06 · Completion message (`queue:ai-results`)

| | |
| --- | --- |
| Between | AI → Backend |
| Owner | AI Team (message shape, DEC-19) · Backend Team (delivery and handling, DEC-01) |
| Reviewers | Backend Team · AI Team |
| Output | `contracts/ai/c06-completion.schema.json` |
| Status | Approved v1.0 · 2026-10-27 (DEC-01 · DEC-19) |

**Delivery (worker side):**

- The worker RPUSHes to `queue:ai-results` (no Redis prefix, DEC-04) **after** its result transaction has committed. One message per run, after the last retry.
- A run that lost its final conditional update (REPLACED while running) rolls back and sends nothing (DEC-08).
- Delivery is at-least-once; the Backend de-duplicates.

**Handling (Backend side, DEC-01):**

- A supervised consumer, `php artisan ai:consume-results`, reads with BLPOP. Target: SSE and notifications within 5 s of the commit.
- **Poller safety net** every 30 s: runs that are DONE or FAILED with `result_handled_at IS NULL`, and `drift_measurement` rows with `is_drifted = 1` and `notified_at IS NULL`, are handled as if C-06 had arrived. `VALIDATION` has no poller; its timeout covers a lost message.
- **De-duplication:** run jobs are claimed with `UPDATE <run> SET result_handled_at = NOW() WHERE id = ? AND result_handled_at IS NULL` (0 rows → ignore). `VALIDATION` and `PART3_EVALUATION` are de-duplicated with a Redis key on `job_id`. `result_handled_at` and `drift_measurement.notified_at` are Backend-only columns (CT-17).
- On receipt the Backend performs the request transition, the audit entry, the notification and the SSE event, then closes old rows (REPLACED, ACTIVE) as agreed in DEC-08.
- **Stale runs:** the Backend sweeper marks a run RUNNING longer than `run_stale_after_seconds` as FAILED / `TIMEOUT` and handles it like a FAILED C-06.

**Fields by `job_type`:**

| `job_type` | `run_id` | `status = DONE` → `outcome` | `status = FAILED` → `outcome` | Extra field |
| --- | --- | --- | --- | --- |
| `PART1_RUN` | `part1_run.id` | `WINDOWS_FOUND` · `NO_FEASIBLE_WINDOW` · `ENV_DATA_UNAVAILABLE` | `null` | `entry_window_proposal_id`: integer with `WINDOWS_FOUND` (and with `NO_FEASIBLE_WINDOW` if DEC-07 = Option 1), otherwise `null` |
| `PART2_SOLVE` | `solver_run.id` | `SOLVED` · `PARTIALLY_SOLVED` · `NO_FEASIBLE_PLAN` · `FIFO_FALLBACK` | `GENERATION_FAILED` | Per-request detail in `solver_run.result_detail` (CT-10) |
| `YARD_PLACEMENT` | `yard_run.id` | `YARD_REC_GENERATED` | `GENERATION_FAILED` | `terminal_recommendation_id` |
| `BAPLIE_PARSE` | `baplie_parse_run.id` | `PARSED` · `QUARANTINED` · `REJECTED` | `null` | `baplie_file_id` |
| `VALIDATION` | `null` | `VALID` · `VIOLATIONS` | `null` | `validation_result` (DONE only) |
| `PART3_EVALUATION` | `null` | `EVALUATED` · `DRIFT_DETECTED` | `null` | `drift_measurement_ids` (at least 1 with `DRIFT_DETECTED`) |

**`error_category`:** `null` with DONE, except `FIFO_FALLBACK`, which carries the technical reason (`SOLVER_ERROR` · `TIMEOUT` · `INTERNAL_ERROR`). Required with FAILED. `INFEASIBLE` is used only by `YARD_PLACEMENT`.

```json
{ "contract_version": "1.0", "job_type": "PART1_RUN", "job_id": "3f6b2c1e-8a1d-4a51-9f1e-2b0c7d9e4a10", "run_id": 812,
  "status": "DONE", "outcome": "WINDOWS_FOUND", "error_category": null, "entry_window_proposal_id": 455,
  "finished_at": "2026-11-02T09:15:41Z", "worker_version": "0.6.0" }
```

```json
{ "contract_version": "1.0", "job_type": "PART2_SOLVE", "job_id": "b81e0c2d-4f5a-4b6c-8d7e-9f0a1b2c3d4e", "run_id": 2302,
  "status": "DONE", "outcome": "FIFO_FALLBACK", "error_category": "TIMEOUT",
  "finished_at": "2026-11-02T12:20:13Z", "worker_version": "0.6.0" }
```

```json
{ "contract_version": "1.0", "job_type": "PART3_EVALUATION", "job_id": "5e4d3c2b-1a09-4f8e-9d7c-6b5a4f3e2d1c", "run_id": null,
  "status": "DONE", "outcome": "DRIFT_DETECTED", "error_category": null, "drift_measurement_ids": [41, 42],
  "finished_at": "2026-11-03T02:00:31Z", "worker_version": "0.6.0" }
```

- `job_id` is the envelope `job_id`; for `PART3_EVALUATION` (no envelope) the worker generates it.
- Every field outside a job type's row is forbidden for that job type (see the schema).

**What the Backend does on receipt:**

| `job_type` | Backend actions |
| --- | --- |
| `PART1_RUN` | Previous `entry_window_proposal` → REPLACED · request transition · audit · SSE `ENTRY_WINDOW_READY` or `RUN_FAILED` · notification |
| `PART2_SOLVE` | Previous PENDING_REVIEW recommendation of each solved request → REPLACED · request transitions · audit · SSE `RECOMMENDATION_READY` · sends the held triggers as the next solve (CT-10) |
| `YARD_PLACEMENT` | Audit · SSE `YARD_RECOMMENDATION_READY` / `YARD_RECOMMENDATION_FAILED` |
| `BAPLIE_PARSE` | On PARSED: new file ACTIVE, previous REPLACED · stale yard regeneration (CT-11) · audit · SSE `BAPLIE_PARSED` |
| `VALIDATION` | Stores the result for `validation_result_ttl_seconds` · SSE to the officer |
| `PART3_EVALUATION` | On DRIFT_DETECTED: SSE `DRIFT_ALERT` · notification · sets `drift_measurement.notified_at` |

---

## CT-15 · AI result tables and write ownership

| | |
| --- | --- |
| Between | AI ↔ Backend |
| Owner | AI Team (document) · Backend Team (DEC-02) |
| Reviewers | Backend Team |
| Output | `contracts/ai/table-ownership.md` |
| Status | Approved v1.0 · 2026-10-27 (DEC-02 · DEC-08) |

**Rules:**

- The worker inserts new rows and completes **only its own run**; every final run update is conditional on `status = 'RUNNING'`.
- The Backend creates runs and closes old rows (REPLACED, ACTIVE, CONFIRMED, REJECTED), and writes every request transition, history row and audit entry.
- No worker deletes anything. `VALIDATION` writes nothing (`w_validate` has SELECT only).

| Table | Created by | Completed / changed by | AI columns (UPDATE) |
| --- | --- | --- | --- |
| `part1_run` | Backend (QUEUED) | AI: its own run. Backend: old run → REPLACED when it sends a new one | `status`, `outcome`, `retry_count`, `entry_window_proposal_id`, `started_at`, `finished_at` |
| `entry_window_proposal` | AI (PROPOSED) | Backend: CONFIRMED, REJECTED, REPLACED (on C-06) and the confirm / reject columns | — |
| `feasible_window` · `blocked_period` | AI | — | — |
| `forecast_run` · `environment_forecast_point` | AI (SCHEDULED, ON_DEMAND; a failed pull inserts a FAILED run) · Backend (MANUAL) | — | — |
| `tide_prediction_run` · `tide_prediction_point` · `demand_forecast_slot` | AI | — | — |
| `solver_run` | Backend (QUEUED, `solver_version` from `port_setting`) | AI: its own run | `status`, `objective_value`, `solve_time_ms`, `solver_version`, `result_detail`, `started_at`, `finished_at` |
| `solver_run_model_version` | AI | — | — |
| `recommendation` · `recommendation_option` · `recommendation_option_tug` · `recommendation_rationale_factor` | AI | Backend: REPLACED, CONFIRMED, MODIFIED_BY_STAFF | — |
| `terminal_recommendation` (YARD_PLACEMENT) | Backend (YARD_REC_REQUESTED; reset on regeneration) | AI: generation result. Backend: decision, accept or reject, export | `lifecycle_status` (GENERATED / GENERATION_FAILED only), `confidence`, `rationale_template_id`, `failure_reason` |
| `yard_run` | Backend (QUEUED; old run → REPLACED) | AI: its own run | `status`, `outcome`, `error_category`, `result_detail`, `worker_version`, `started_at`, `finished_at` |
| `yard_placement_item` | AI | Backend: deletes old items on regeneration | — |
| `baplie_file` | Backend (STAGED, PENDING) | AI: parse result. Backend: ACTIVE / REPLACED / WITHDRAWN, correction columns, edits `staged_payload` on correction | `parse_status`, `staged_payload` |
| `baplie_parse_run` | Backend (QUEUED; old run → REPLACED) | AI: its own run | `status`, `outcome`, `error_category`, `retry_count`, `container_count`, `result_detail`, `worker_version`, `started_at`, `finished_at` |
| `baplie_parse_issue` · `container` · `container_manifest_entry` | AI | — | — |
| `vessel` | Backend | AI: fills NULL columns only | `call_sign`, `flag_state` |
| `evaluation_metric` · `drift_measurement` | AI (`w_part3`) | Backend: `drift_measurement.notified_at` | — |
| `result_handled_at` (all run tables) | — | Backend only | — |
| `terminal_recommendation` (TIMING / STORAGE_ALLOCATION) · `storage_allocation_item` | Nobody (DEC-55, future work) | — | — |
| `berthing_request` (+ history) · `operational_plan` · `plan_component` · `recommendation_override` · `audit_log` · `notification_log` | Backend only | — | — |

---

## CT-16 · Worker health over Redis (replaces the FastAPI internal API)

| | |
| --- | --- |
| Between | AI → Backend |
| Owner | AI Team |
| Reviewers | Backend Team |
| Output | `contracts/ai/worker-heartbeat.schema.json` |
| Status | Approved v1.0 · 2026-10-27 (DEC-10) |

FastAPI is cancelled (DEC-10):

| Old endpoint | Replacement |
| --- | --- |
| `GET /internal/v1/health` | Heartbeat keys below |
| `GET /internal/v1/workers` | Heartbeat keys + `LLEN` of each queue (read by the Backend) |
| `GET /internal/v1/runs/{job_type}/{run_id}` | The Backend reads the run tables directly |
| `POST /internal/v1/validate` | CT-13 (`queue:validate`) |

**Heartbeat rules:**

- **Key:** `worker:{name}:heartbeat`, `name` = `part1` · `part2` · `yard` · `edi` · `validate` · `part3`. Written every 15 s with `SET … EX 60`.
- **DOWN:** key missing. **Stale:** `last_heartbeat` older than 45 s (warning). **DEGRADED:** running but a dependency fails (reason in `status_detail`). **DRAINING:** finishing the current job, taking no new ones (deploys).
- **Backend:** the admin worker-status page reads the keys and `LLEN` of each queue; an alert is raised when a worker is DOWN for more than 2 minutes.

```json
{
  "contract_version": "1.0",
  "name": "part1",
  "status": "UP",
  "status_detail": null,
  "version": "0.6.0",
  "host": "port-ai-01",
  "started_at": "2026-11-02T06:00:00Z",
  "last_heartbeat": "2026-11-02T10:05:00Z",
  "current_job": { "job_type": "PART1_RUN", "job_id": "3f6b2c1e-8a1d-4a51-9f1e-2b0c7d9e4a10", "run_id": 812, "started_at": "2026-11-02T10:04:58Z" },
  "processed_total": 120,
  "failed_total": 1,
  "schedules": { "last_weather_pull_at": "2026-11-02T06:00:12Z", "last_tide_compute_at": "2026-11-02T00:00:40Z", "last_demand_forecast_at": "2026-11-02T06:01:03Z" }
}
```

`current_job.job_type` also covers the scheduled jobs `WEATHER_PULL` · `TIDE_COMPUTE` · `DEMAND_FORECAST`. `schedules` is sent by `part1` and `part3` only.

---

## CT-17 · Database schema (migrations)

| | |
| --- | --- |
| Between | Backend → AI |
| Owner | Backend Team (single owner of migrations) |
| Reviewers | AI Team |
| Output | Migrations in `project-backend`, and `contracts/db/schema.sql` updated with every new migration |

- The AI Team builds its test schema from `schema.sql`.
- **Pending additions from approved contracts:** new `yard_run` (CT-11) · new `baplie_parse_run` (CT-12) · `result_handled_at datetime NULL` on `part1_run`, `solver_run`, `yard_run`, `baplie_parse_run` and `notified_at datetime NULL` on `drift_measurement` (CT-14, Backend-only columns) · the worker grants script (DEC-08).
- Any change to a table the AI writes to is requested through the Backend and needs AI Team approval.

```sql
-- contracts/db/schema.sql (excerpt)
CREATE TABLE part1_run (
  id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  berthing_request_id BIGINT UNSIGNED NOT NULL,
  status ENUM('QUEUED','RUNNING','DONE','FAILED','REPLACED') NOT NULL,
  outcome ENUM('WINDOWS_FOUND','NO_FEASIBLE_WINDOW','ENV_DATA_UNAVAILABLE') NULL,
  retry_count TINYINT UNSIGNED NOT NULL DEFAULT 0,
  entry_window_proposal_id BIGINT UNSIGNED NULL
);
```

---

## CT-18 · AI seed data and `port_setting` keys

| | |
| --- | --- |
| Between | AI → Backend |
| Owner | AI Team |
| Reviewers | Backend Team (writes the seeders) |
| Output | `contracts/ai/seed-spec.json` |

```json
{
  "constraint_type": [ { "code": "MAX_WIND_KN", "category": "ENVIRONMENT", "unit": "kn", "comparator": "<=", "is_hard_safety_limit": true } ],
  "objective_term": [ { "code": "WAITING_TIME", "weight": 1.0 }, { "code": "RESOURCE_UTILISATION", "weight": 0.2 } ],
  "rationale_template": [ { "code": "BEST_WAIT", "version": 1, "text": "Lowest waiting time for {vessel} at berth {berth}." } ],
  "ml_model": [ { "key": "B3_SERVICE_TIME", "phase": 1 } ],
  "port_setting": [ { "key": "solver_time_limit_seconds", "type": "int", "value": 10 } ]
}
```

- **Keys added by approved contracts (to be included in the seed spec):** `solver_option_equivalence_pct` = 10 (CT-10, DEC-23) · `validation_timeout_seconds` = 15 · `validation_result_ttl_seconds` = 600 (CT-13).

---

## CT-19 · Mock worker behaviour

| | |
| --- | --- |
| Between | Backend → Frontend · Mobile · QA |
| Owner | Backend Team |
| Reviewers | Frontend Team · QA Team |
| Output | `contracts/mock-workers.md`: for each queue, the results it returns and how to choose a scenario |

- Mocks write contract-shaped rows and send C-06, so the Frontend cannot tell them apart from the real workers.
- The scenario is selected with the `mock_scenario` key in `port_setting`, or with a tag in the vessel name.

| Queue | Scenarios |
| --- | --- |
| `queue:part1` | `WINDOWS_FOUND` · `NO_FEASIBLE_WINDOW` · `ENV_DATA_UNAVAILABLE` · `FAILED` |
| `queue:part2` | `SOLVED` · `FIFO_FALLBACK` · `NO_FEASIBLE_PLAN` · `GENERATION_FAILED` |
| `queue:edi` | `PARSED` · `QUARANTINED` · `FAILED` |
| yard | `YARD_REC_GENERATED` · `GENERATION_FAILED` |

---

## CT-20 · AI result read endpoints

| | |
| --- | --- |
| Between | Backend → Frontend |
| Owner | Backend Team |
| Reviewers | Frontend Team |
| Output | AI results section of `port-api.yaml` |

| Endpoint | Returns | Role |
| --- | --- | --- |
| `GET /api/v1/berthing-requests/{id}/part1-result` | Outcome, windows, blocked periods, data sources and their age | Port Authority Staff |
| `GET /api/v1/berthing-requests/{id}/recommendation` | Current version, options, tugs, rationale and binding constraints | Port Authority Staff |
| `GET /api/v1/terminal-recommendations/{id}` | Yard placements, rationale and confidence | CT Operation Planner (own terminal) |
| `GET /api/v1/environment/conditions` | Weather, tide, surge, source and data age | All office users |
| `GET /api/v1/ai/evaluation` · `GET /api/v1/ai/drift` | Metrics and drift | Port Admin |

```json
// GET /api/v1/berthing-requests/1550/recommendation
{
  "recommendation_id": 880,
  "version": 2,
  "status": "PENDING_REVIEW",
  "source": "AI",
  "purpose": "INITIAL",
  "options": [
    {
      "id": 9031, "rank": 1, "berth": { "id": 12, "code": "B12" },
      "start": "2026-11-03T06:00:00Z", "end": "2026-11-03T18:30:00Z",
      "pilot": { "id": 4 }, "tugs": [ { "id": 7 }, { "id": 9 } ],
      "service_time_hours": 12.5, "delay_risk": null,
      "objective_score": 0.82, "rationale": "Lowest waiting time for MSC Aurora at berth B12."
    }
  ]
}
```

---

## CT-21 · Shared status vocabulary

| | |
| --- | --- |
| Between | Backend → Frontend · Mobile · AI · QA |
| Owner | Backend Team (from the PHP enums) |
| Reviewers | All teams |
| Output | `contracts/status-vocabulary.json`, generated automatically from the enums |

```json
{
  "berthing_request.status": ["SUBMITTED","NEEDS_REVISION","PRELIMINARY_APPROVED","CUSTOMS_APPROVED","ENTRY_WINDOW_CONFIRMED","RECOMMENDATION_GENERATED","PLAN_CONFIRMED","PLAN_CANCELLED","COMPLETED","REJECTED","CANCELLED"],
  "plan_component.status": ["UNASSIGNED","ASSIGNED","STARTED","DONE"],
  "recommendation.status": ["PENDING_REVIEW","MODIFIED_BY_STAFF","CONFIRMED","REPLACED"],
  "notification.status": ["SENT","FAILED","ESCALATED"],
  "terminal_recommendation.lifecycle_status": ["YARD_REC_REQUESTED","YARD_REC_GENERATED","GENERATION_FAILED","ACCEPTED","REJECTED","EXPORTED_TO_TOS"]
}
```

---

## CT-22 · Screen design hand-off

| | |
| --- | --- |
| Between | UI/UX → Frontend · Mobile |
| Owner | UI/UX Team |
| Reviewers | Frontend Team · Mobile Team |
| Output | A Figma file where every frame is named by its Page ID with all its states next to it, plus the tokens in `contracts/design/tokens.json` |

**Rules:**

- Frame names follow the pattern `P-38 / Recommendation Review / Default`, with the states next to it: `/ Loading`, `/ Empty`, `/ Error`, `/ Conflict`.
- Web and tablet are separate frames.

```json
{
  "color": {
    "navy": "#083A4F", "gold": "#A58D66", "teal-light": "#C0D5D6",
    "teal-mid": "#407E8C", "off-white": "#E5E1DD"
  },
  "font": { "heading": "Montserrat", "body": "Inter" },
  "radius": { "sm": 4, "md": 8 },
  "space": [4, 8, 12, 16, 24, 32]
}
```

---

## CT-23 · API readiness pack (per FRR)

| | |
| --- | --- |
| Between | Backend → Frontend · Mobile · QA |
| Owner | Backend Team |
| Reviewers | Frontend Team · Mobile Team · QA Team at the FRR |
| Output | `contracts/readiness/FT-xx.md` for each feature |

```markdown
# FT-06 Berthing requests and BAPLIE — API readiness pack
- Endpoints (merged to develop): POST /api/v1/berthing-requests, GET /api/v1/berthing-requests, ...
- OpenAPI diff: link to the PR
- Examples: requests and responses for 201, 403, 409, 422
- Seed data on the dev server: 5 requests in every status, 2 BAPLIE files (parsed, quarantined)
- Events: REQUEST_STATUS_CHANGED, BAPLIE_PARSED
- Behind it: mock worker for queue:edi (scenario PARSED)
- Known gaps: none
```

---

## CT-24 · BAPLIE test corpus

| | |
| --- | --- |
| Between | QA → AI |
| Owner | QA Team |
| Reviewers | AI Team |
| Output | Folder `contracts/ai/baplie-corpus/`: every `.edi` file with an `.expected.json` file next to it |

```json
// valid-small-01.expected.json
{
  "file": "valid-small-01.edi",
  "expected_parse_status": "PARSED",
  "containers": 212,
  "issues": [],
  "vessel_imo": "9811000"
}
```

Scenarios that must be covered: a valid file, a file with a different IMO (`QUARANTINED`), a file with invalid values (`QUARANTINED` with diagnostics), an unreadable file (`FAILED`), and every size class.

---

## CT-25 · Reference data and thresholds inputs

| | |
| --- | --- |
| Between | QA → AI |
| Owner | QA Team |
| Reviewers | AI Team |
| Output | `contracts/ai/reference-data/*.csv`, with a `source` column and an `is_synthetic` column on every row |

```csv
berth_code,terminal_code,length_m,depth_m,max_loa_m,source,is_synthetic
B12,DCT,350,14.5,345,"Damietta Port published berth list",false
B13,DCT,350,14.5,345,"Generated to complete terminal",true
```

---

## CT-26 · QA report and defect format

| | |
| --- | --- |
| Between | QA → All teams |
| Owner | QA Team |
| Reviewers | Leads Council |
| Output | `contracts/qa/release-report-template.md` and the defect template in GitHub Issues |

```markdown
# Release test report — v0.N.0
- Repositories and commits tested: backend@abc123, frontend@def456, mobile@..., ai@...
- Features tested (from FRR): FT-xx, FT-yy
- Result: PASS / PASS WITH NOTES / FAIL
- Blocking defects: #123, #130
- Sign-off: QA Team
```

**Defect fields:** `ID` · `Feature` · `Page ID / Endpoint` · `Steps` · `Expected` · `Actual` · `Severity (Blocker / Major / Minor)` · `Repository` · `Found on (release branch)`.
