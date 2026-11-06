# ATLANTECH AI Testing Guide (QA-AI1 / CT-24 / CT-25)

Owner: QA Team. Reviewers: AI Team, Backend Team, Leads Council. Status: draft for review.
Items marked **Proposed** are pending domain sign-off or team agreement.

## 1. Purpose and scope

This guide defines the end-to-end QA approach for testing the AI workers, algorithms, and integration boundaries in ATLANTECH. It establishes test levels, boundary assertions, data oracles, corpus definitions, reference data standards, and domain invariants.

Testing covers:
- Python AI workers: BAPLIE/EDI parser (`queue:edi`), Part 1 entry window calculator (`queue:part1`), Part 2 berth recommendation solver (`queue:part2`), Part 3 model evaluation and drift tracker (`queue:part3`), and Yard placement worker (`queue:yard`).
- Inter-process communication boundaries: Redis queue job envelopes (CT-08), synchronous validation (`queue:validate`, CT-13), completion signaling (C-06, CT-14), and worker heartbeats (CT-16).
- Database persistence boundaries: MySQL table write ownership (CT-15), schema alignment (CT-17), and transaction atomicity.
- Domain invariants: System-wide safety, scheduling, physical, and business invariants (I-1 to I-15).

Testing excludes:
- BAPLIE file parse time performance tests across size classes (NFR-PERF-2 removed from MVP per DEC-17 and CT-12).

## 2. AI architecture and queue boundaries

ATLANTECH uses an asynchronous worker pattern over Redis queues with a dedicated MySQL database.

```
+-----------------------------------------------------------------------------------+
|                                  Backend (Laravel)                                |
+-----------------------------------------------------------------------------------+
       | RPUSH (C-01..C-05)                                     ^ BLPOP (C-06)
       v                                                        |
+-----------------------------------------------------------------------------------+
|                                  Redis Queues                                     |
|  queue:part1  |  queue:part2  |  queue:yard  |  queue:edi  |  queue:validate     |
+-----------------------------------------------------------------------------------+
       | BLPOP                                                  ^ RPUSH
       v                                                        |
+-----------------------------------------------------------------------------------+
|                                  AI Workers (Python)                              |
|  Part 1 Worker | Part 2 Worker | Yard Worker | EDI Worker | Validation Worker     |
+-----------------------------------------------------------------------------------+
       | MySQL Writes (Owned Tables / Columns per CT-15)
       v
+-----------------------------------------------------------------------------------+
|                                  MySQL Database                                   |
+-----------------------------------------------------------------------------------+
```

Key architectural rules:
1. Every job is enqueued by the Backend using `RPUSH` with an unprefixed queue name (`queue:part1`, `queue:part2`, `queue:yard`, `queue:edi`, `queue:validate`).
2. Every job uses the canonical outer JSON envelope defined in CT-08 with `contract_version = "1.0"`.
3. Completion messages flow back from AI workers to Backend on `queue:c06` using `RPUSH`.
4. Synchronous validations for user actions (overrides, BAPLIE correction, manual berth adjustments) use `queue:validate` with a 15-second timeout (CT-13).

## 3. Worker contracts summary (CT-08 to CT-16)

| Contract | Name | Producer | Consumer | Interface |
| --- | --- | --- | --- | --- |
| CT-08 | AI Job Envelope | Backend / AI | AI / Backend | Redis JSON envelope |
| CT-09 | C-01 Part 1 Run | Backend | AI (Part 1) | `queue:part1` payload schema |
| CT-10 | C-02 Part 2 Solve | Backend | AI (Part 2) | `queue:part2` payload schema |
| CT-11 | C-03 Yard Placement | Backend | AI (Yard) | `queue:yard` payload schema |
| CT-12 | C-04 BAPLIE Parse | Backend | AI (EDI) | `queue:edi` payload schema |
| CT-13 | C-05 Validation | Backend | AI (Validator) | `queue:validate` request/response |
| CT-14 | C-06 Completion | AI Workers | Backend | `queue:c06` completion schema |
| CT-15 | Result Tables & Ownership | AI Workers | MySQL | Database write ownership rules |
| CT-16 | Worker Health | AI Workers | Redis | Redis hash `worker:health:<name>` |

## 4. Envelope and completion messages

### 4.1 Job envelope (CT-08)
Outer envelope fields:
- `contract_version`: string, must be `"1.0"`.
- `job_type`: ENUM (`PART1_RUN`, `PART2_SOLVE`, `YARD_PLACEMENT`, `BAPLIE_PARSE`, `VALIDATE`).
- `job_id`: UUIDv4 string.
- `run_id`: integer referencing the primary key of the run table (`forecast_runs`, `recommendation_runs`, `yard_runs`, or `baplie_parse_runs`).
- `enqueued_at`: ISO 8601 UTC timestamp.
- `triggered_by_user_id`: integer or `null` (for system-triggered jobs like customs approval).
- `payload`: JSON object validated against the corresponding payload schema (C-01 to C-05).

### 4.2 Completion message C-06 (CT-14)
When an AI job finishes, the worker issues an `RPUSH` to `queue:c06`:
- `contract_version`: `"1.0"`.
- `job_id`: matching envelope `job_id`.
- `run_id`: matching envelope `run_id`.
- `job_type`: matching envelope `job_type`.
- `status`: `DONE` or `FAILED`.
- `outcome`: for BAPLIE (`PARSED`, `QUARANTINED`, `REJECTED`); for Part 1 / Part 2 (`FEASIBLE`, `INFEASIBLE`, `OPTIMAL`, etc.).
- `error_category`: required if `status = FAILED`, forbidden if `status = DONE`. Permitted values: `INVALID_ENVELOPE`, `PRECONDITION_FAILED`, `DATA_UNAVAILABLE`, `CONFIGURATION_ERROR`, `SOLVER_ERROR`, `TIMEOUT`, `INTERNAL_ERROR`.
- `completed_at`: ISO 8601 UTC timestamp.

## 5. Database result rows and write ownership (CT-15)

Strict write isolation applies at all times:
1. **AI Workers** write only to their designated run and result tables:
   - Part 1 writes: `forecast_runs`, `forecast_windows`, `forecast_timeseries`.
   - Part 2 writes: `recommendation_runs`, `berth_recommendations`, `resource_allocations`, `recommendation_metrics`.
   - Yard writes: `yard_runs`, `yard_recommendations`, and specific columns (`lifecycle_status`, `confidence`, `failure_reason`) on `terminal_recommendations`.
   - EDI Worker writes: `baplie_parse_runs`, `baplie_parse_issues`, `baplie_files.parse_status`, `baplie_files.staged_payload`, `containers`, `container_manifest_entries`, `vessels` (fill empty columns only).
2. **Backend** owns entity lifecycle statuses:
   - Backend transitions `berthing_requests.status`.
   - Backend sets `baplie_files.status` (`ACTIVE` / `REPLACED` / `STAGED`). The EDI worker never modifies `baplie_files.status` directly.

## 6. Worker health and heartbeats (CT-16)

Every AI worker must maintain an active heartbeat in Redis:
- Key: `worker:health:<worker_name>` (e.g., `worker:health:edi`, `worker:health:part1`, `worker:health:part2`, `worker:health:yard`).
- Format: Redis HASH containing:
  - `worker_id`: hostname or container ID string.
  - `worker_version`: git commit SHA or semver string.
  - `status`: `IDLE`, `PROCESSING`, or `SHUTTING_DOWN`.
  - `last_heartbeat_at`: ISO 8601 UTC timestamp.
  - `current_job_id`: UUIDv4 string or empty if IDLE.
- Interval: Workers write heartbeat every 15 seconds with a 60-second TTL.
- Alerting threshold: Backend health monitor flags a worker as `DEGRADED` after 45 seconds of silence, and `DOWN` after 120 seconds (2 minutes).

## 7. BAPLIE test corpus (CT-24)

### 7.1 Supported versions and format
Per contract CT-12, the EDI parser supports:
- SMDG BAPLIE version 2.2.1 (UN/EDIFACT D.95B with VGM), identified by `UNH...BAPLIE:D:95B:UN:SMDG22`.
- SMDG BAPLIE version 3.1.1 (UN/EDIFACT D.13B with VGM), identified by `UNH...BAPLIE:D:13B:UN:SMDG31`.

Every test case in the corpus consists of two companion files:
1. `<case-name>.edi`: the test EDI message.
2. `<case-name>.expected.json`: the oracle definition file.

Companion JSON format:
```json
{
  "file": "<case-name>.edi",
  "expected_outcome": "PARSED",
  "expected_parse_status": "PARSED",
  "vessel_imo": "9811000",
  "containers": 212,
  "issues": [
    {
      "severity": "WARNING",
      "code": "CHECK_DIGIT_MISMATCH",
      "segment_ref": "EQD+CN+MSCU1234567"
    }
  ]
}
```

Permitted combinations:
- `expected_outcome = "PARSED"`, `expected_parse_status = "PARSED"`: Valid file, zero ERROR issues, data committed to MySQL.
- `expected_outcome = "QUARANTINED"`, `expected_parse_status = "QUARANTINED"`: Valid EDI structure with domain errors, parsed data written to `staged_payload`, zero containers committed.
- `expected_outcome = "REJECTED"`, `expected_parse_status = "FAILED"`: Non-EDIFACT, wrong message type, or unsupported BAPLIE version.

### 7.2 Standard corpus test cases (18 test cases)

| Case ID | Case Name | Format / Version | Injected Characteristic | Expected Outcome | Expected Parse Status | Key Assertions / Issues |
| --- | --- | --- | --- | --- | --- | --- |
| 01 | `01-valid-221` | SMDG 2.2.1 (D.95B) | Clean valid file with VGM | `PARSED` | `PARSED` | All containers loaded; 0 errors, 0 warnings |
| 02 | `02-valid-311` | SMDG 3.1.1 (D.13B) | Clean valid file with VGM | `PARSED` | `PARSED` | All containers loaded; 0 errors, 0 warnings |
| 03 | `03-valid-with-warnings` | SMDG 2.2.1 (D.95B) | Container check digit mismatch | `PARSED` | `PARSED` | Loaded; WARNING `CHECK_DIGIT_MISMATCH` |
| 04 | `04-imo-mismatch` | SMDG 2.2.1 (D.95B) | Vessel IMO differs from request | `QUARANTINED` | `QUARANTINED` | Staged; ERROR `IMO_MISMATCH` |
| 05 | `05-duplicate-container` | SMDG 2.2.1 (D.95B) | Duplicate container number in file | `QUARANTINED` | `QUARANTINED` | Staged; ERROR `DUPLICATE_CONTAINER_NUMBER` |
| 06 | `06-unknown-iso-size-type` | SMDG 2.2.1 (D.95B) | Invalid ISO code (e.g. `45X9`) | `QUARANTINED` | `QUARANTINED` | Staged; ERROR `UNKNOWN_SIZE_TYPE` |
| 07 | `07-unknown-imdg-class` | SMDG 2.2.1 (D.95B) | Unrecognized IMDG hazard code | `QUARANTINED` | `QUARANTINED` | Staged; ERROR `UNKNOWN_IMDG_CLASS` |
| 08 | `08-malformed-weight` | SMDG 2.2.1 (D.95B) | Negative or non-numeric weight | `QUARANTINED` | `QUARANTINED` | Staged; ERROR `MALFORMED_WEIGHT` |
| 09 | `09-malformed-unlocode` | SMDG 2.2.1 (D.95B) | Invalid port code syntax | `QUARANTINED` | `QUARANTINED` | Staged; ERROR `MALFORMED_UNLOCODE` |
| 10 | `10-temperature-out-of-range` | SMDG 2.2.1 (D.95B) | Reefer temperature < -40 or > +40 | `QUARANTINED` | `QUARANTINED` | Staged; ERROR `TEMPERATURE_OUT_OF_RANGE` |
| 11 | `11-reefer-missing-temp` | SMDG 2.2.1 (D.95B) | Reefer size code without set temp | `QUARANTINED` | `QUARANTINED` | Staged; ERROR `REEFER_MISSING_TEMPERATURE` |
| 12 | `12-invalid-stowage-coordinate` | SMDG 2.2.1 (D.95B) | Stowage bay/row/tier out of bounds | `QUARANTINED` | `QUARANTINED` | Staged; ERROR `INVALID_STOWAGE_COORDINATE` |
| 13 | `13-missing-mandatory-segment` | SMDG 2.2.1 (D.95B) | Missing mandatory LOC or MEA | `QUARANTINED` | `QUARANTINED` | Staged; ERROR `MISSING_MANDATORY_SEGMENT` |
| 14 | `14-multiple-errors-composite` | SMDG 2.2.1 (D.95B) | Combined IMO + size + weight errors | `QUARANTINED` | `QUARANTINED` | Staged; multiple ERROR issues reported |
| 15 | `15-non-edifact-payload` | Plain text / XML | Non-EDI formatted file | `REJECTED` | `FAILED` | 0 rows; ERROR `NOT_EDIFACT` |
| 16 | `16-unsupported-version` | SMDG 1.5 / 2.0 | Outdated or unsupported version | `REJECTED` | `FAILED` | 0 rows; ERROR `UNSUPPORTED_BAPLIE_VERSION` |
| 17 | `17-wrong-message-type` | EDIFACT COPRAR | Valid EDIFACT but wrong type | `REJECTED` | `FAILED` | 0 rows; ERROR `WRONG_MESSAGE_TYPE` |
| 18 | `18-corrupted-syntax` | Truncated EDI | Missing UNZ or broken delimiters | `REJECTED` | `FAILED` | 0 rows; ERROR `CORRUPTED_SYNTAX` |

### 7.3 Performance scope (DEC-17)
Per DEC-17 and CT-12 v1.0, BAPLIE parsing performance targets across size classes (NFR-PERF-2) have been explicitly removed from the MVP by Leads Council decision (2026-10-27). QA does not execute automated performance benchmark gates against BAPLIE size tiers.

## 8. Reference data and port topologies (CT-25)

### 8.1 Port topologies
QA tests algorithms against two mandatory topological scales:
1. **Minimum-scale topology:**
   - 1 terminal, 5 berths.
   - Purpose: Fast local unit/integration tests and minimal constraint validation.
2. **Reference-scale topology (Damietta Port):**
   - 8 terminals, 36 berths, handling approximately 26 vessels per day.
   - Purpose: Production-realistic solver benchmarking, joint-solve scaling, and constraint interaction tests.

### 8.2 Required reference CSV files
All reference CSV datasets reside under `contracts/ai/reference-data/`:
- `berths-minimum.csv`: Minimum-scale berth master data.
- `berths-reference.csv`: Damietta full reference berth master data.
- `safety-thresholds.csv`: Operational environmental thresholds (wind, gust, wave, visibility, minimum UKC).

### 8.3 Data format rules
Every row in every reference CSV file must include:
- `source`: string indicating origin (e.g., `"Damietta Port published berth list"`, `"Synthetic test fixture"`).
- `is_synthetic`: boolean (`true` or `false`). Real-world measured values are marked `false`; generated edge cases are marked `true`.

## 9. Thresholds register inputs (QA-AI1 / DEC-30)

Per DEC-30, numeric thresholds governing AI decisions are consolidated into a canonical register.

Summary of key inputs:
- Under-Keel Clearance (UKC) default: 1.0 m minimum clearance.
- Tide prediction error tolerance: Proposed +/- 15 cm.
- Solver option equivalence margin: 10% (DEC-23, CT-18, CT-10). Two recommendation options with objective scores within 10% are considered equivalent.
- Solver time limit: 10 seconds default (min 1 s, max 120 s) (CT-18).
- Environmental stored data freshness: 48 hours max age (`part1_stored_data_max_age_hours = 48`, CT-18, DEC-12).
- Drift thresholds:
  - `drift_psi_threshold`: Population Stability Index threshold (Proposed: 0.25).
  - `drift_mae_threshold`: Rolling Mean Absolute Error degradation threshold (Proposed: 20% relative increase).
- Maximum Part 1 retry attempts: 3 retries (DEC-04, CT-08).
- Validation timeout: 15 seconds (CT-13, CT-18).
- Validation result TTL: 600 seconds (10 minutes) (CT-18).

## 10. Manual-planning baseline procedure (QA-AI1 / DEC-33)

To validate Part 2 optimization in Sprint 7 (AI-084), AI recommendation quality must be evaluated against a reproducible manual planning baseline using replay scenarios from reference data.

### 10.1 Step-by-step manual allocation procedure (FIFO rule-based)
1. **Ordering:** Sort pending vessel requests chronologically by Estimated Time of Arrival (ETA). Ties broken by request submission timestamp.
2. **Berth Selection:** For each vessel in order:
   - Identify candidate berths whose physical characteristics meet hard vessel requirements (admissible LOA >= vessel LOA, water depth >= vessel draft + minimum UKC).
   - Filter candidates for terminal-specific cargo compatibility (e.g., container vessels allocated to container terminals).
   - Select the earliest available compatible berth time slot where no overlapping vessel is assigned.
3. **Resource Assignment:**
   - Allocate available quay cranes up to berth crane limit.
   - Assign pilot and tug resources following standard port dispatch rules (e.g., 2 tugs per vessel > 200 m LOA).
4. **Conflict Handling:** If no berth meets constraints at ETA, delay vessel assignment to the earliest subsequent feasible window without displacing already scheduled vessels (pure non-preemptive FIFO).

### 10.2 Comparison protocol for Sprint 7 evaluation
Replay scenarios run through three engines:
1. AI Recommendation Engine (Part 2 Solver).
2. Pure FIFO Fallback.
3. Domain Expert / Rule-Based Manual Plan.

Evaluation compares the three outputs across six Master Context indicators:
1. Hard conflicts detected and avoided (zero tolerance for physical overlaps).
2. Resource utilization efficiency (berth occupancy rate, crane utilization).
3. Avoidable waiting time at anchorage (hours per vessel).
4. Total estimated operational delay cost.
5. Feasibility and operational quality score.
6. Downstream yard re-handling movements generated.

## 11. Data oracles and verification techniques

QA utilizes black-box testing techniques across the Redis queue and MySQL boundary:
- **Queue Enqueue Oracle:** Inspect Redis queue payloads using automated test drivers to confirm schema compliance, UUID validity, timestamp precision, and envelope structure prior to worker consumption.
- **Completion Signal Oracle:** Validate that workers emit C-06 messages to `queue:c06` within specified timeout limits, containing valid status, outcome, and error categorization.
- **State Transition Oracle:** Verify that MySQL status transitions on run tables strictly mirror worker outcomes (QUEUED -> RUNNING -> DONE / FAILED).
- **Physical Hand-Calculation Oracle:** Verify Part 1 UKC calculations against independent astronomical tide harmonics and vessel draft formulas.
- **Quarantine Oracle:** Confirm that quarantined BAPLIE files write pure JSON to `staged_payload` without corrupting active container tables.

## 12. Domain invariants (I-1 to I-15)

All automated test suites, contracts, and manual checks must verify that these fifteen domain invariants are never violated:

| Invariant | Name | Rule and Verification |
| --- | --- | --- |
| I-1 | Berth Overlap Prohibition | No two vessels may occupy overlapping physical berth meter marks during overlapping time intervals. Verified across all confirmed recommendations. |
| I-2 | Minimum Under-Keel Clearance | At every point along the vessel transit and berth stay, water depth (chart datum + predicted tide) minus vessel draft must equal or exceed minimum UKC (1.0 m). |
| I-3 | Berth LOA Compliance | Vessel Length Overall (LOA) must not exceed maximum berth physical length and allowable approach span. |
| I-4 | Equipment Assignment Limits | Number of assigned quay cranes must not exceed the physical crane capacity or rail limits of the assigned berth. |
| I-5 | Weather Safety Limits | Berthing and unberthing maneuvers must not be scheduled during forecasted intervals where wind, gust, wave height, or visibility exceed safety thresholds. |
| I-6 | Active Request Uniqueness | A vessel or port call must never have more than one berthing request in an active, non-completed, non-cancelled state simultaneously. |
| I-7 | BAPLIE Active File Uniqueness | At most one BAPLIE file may be `ACTIVE` per berthing request. Activating a newly parsed file atomically marks previous active file `REPLACED`. |
| I-8 | Strict Write Chain Ordering | Every state-changing API request must strictly execute authorization and validation checks in order: 401 -> 403 -> 426 -> 423 -> 409 -> 422. |
| I-9 | License READ_ONLY Enforcement | When port license is `READ_ONLY`, new entity creations return 423 Locked. In-flight status progressions and safety alerts remain permitted. |
| I-10 | Permitted Lifecycle Transitions | Berthing request state transitions must strictly adhere to the defined forward DAG. Backward or illegal leaps (e.g. SUBMITTED directly to PLAN_CONFIRMED) return 409 Conflict. |
| I-11 | Mobile Write Idempotency | Multiple transmissions of a write request with the same `Idempotency-Key` within the 30-day cache window must return identical responses without duplicate mutations. |
| I-12 | Clock Skew Detection | Requests arriving with client timestamps diverging more than 5 minutes from server UTC must be flagged with clock skew warning. |
| I-13 | AI Write Isolation | AI workers must only write to their assigned run and recommendation tables (CT-15). Workers must never alter backend-owned lifecycle status columns. |
| I-14 | Queue Envelope Conformance | Every message enqueued on Redis worker queues must strictly conform to the CT-08 envelope schema. Malformed messages must be rejected without worker crash. |
| I-15 | Worker Heartbeat Liveness | Every active worker must refresh its Redis heartbeat key every 15 seconds. Workers unrefreshed after 120 seconds must be flagged as DOWN and alert operations. |
