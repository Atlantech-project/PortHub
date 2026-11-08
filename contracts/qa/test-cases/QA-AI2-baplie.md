# Acceptance Test Cases: QA-AI2 BAPLIE Corpus & Parser Validation

- Task ID: QA-AI2
- Component: PortHub / project-ai / EDI Parser
- Governing Contracts: CT-08, CT-12, CT-14, CT-15, CT-16, CT-17, CT-24, CT-25
- Specifications: UN/EDIFACT D.95B (SMDG 2.2.1) & D.13B (SMDG 3.1.1) per CT-12, RFC 9457 Problem Details
- Lifecycle States: STAGED, ACTIVE, REPLACED, WITHDRAWN
- Parse Statuses: PENDING, PARSED, QUARANTINED, FAILED
- Processing Queue: queue:edi

---

## Test Suite Summary

| Test Case ID | Title | Level | Severity | Expected Result |
| :--- | :--- | :--- | :--- | :--- |
| TC-BAP-001 | Valid EDI Parsing & Extraction (D.95B) | EDI / Automated | Blocker | Parse status PARSED, file ACTIVE, 12 containers committed |
| TC-BAP-002 | Special Cargo: Reefer & Hazmat Tagging (D.95B) | Data Contract | Major | Cargo attributes populated in DB (temp -18C, IMDG Class 3) |
| TC-BAP-003 | Corrupt File Syntax Error | Parser Robustness | Blocker | Parse status FAILED, error logged, worker remains healthy |
| TC-BAP-004 | Semantic Field Error Quarantine | Workflow | Major | Parse status QUARANTINED, staged edit enabled |
| TC-BAP-005 | SHA-256 Duplicate Upload Detection | API / Security | Major | HTTP 409 Conflict, no duplicate processing |
| TC-BAP-006 | Manifest Withdrawal & Replacement | Lifecycle State | Minor | Previous file REPLACED, withdrawn file WITHDRAWN |
| TC-BAP-007 | Unsupported Version Rejection (D.17A) | Protocol Validation | Blocker | Parse status FAILED, outcome REJECTED, ERROR on UNH |

---

## Detailed Test Cases

### TC-BAP-001: Valid EDI Parsing & Extraction (D.95B)
- Description: Verify that a compliant UN/EDIFACT D.95B BAPLIE manifest (SMDG 2.2.1 with identifier `BAPLIE:D:95B:UN:SMDG22`) for container vessel "AL FARAHIDI" (IMO 9234567) is successfully uploaded, processed asynchronously by the EDI worker via queue:edi, and committed to database tables `containers` and `container_manifest_entries`.
- Target Sample File: `contracts/qa/baplie-corpus/01_valid_standard_discharge.edi`
- Preconditions:
  - Active berthing request `BR-DAM-2026-001` exists for vessel "AL FARAHIDI" (IMO 9234567).
  - No active BAPLIE file attached to this berthing request.
  - Background worker `w_edi` is active and consuming `queue:edi`.
- Execution Steps:
  1. Upload `01_valid_standard_discharge.edi` via `POST /api/v1/berthing-requests/BR-DAM-2026-001/baplie`.
  2. Backend calculates SHA-256 hash (`72abea92aacabb62768d5109788dfc5f244a793f0d7fe05091d79d5ba798f2f1`), inserts row into `baplie_files` (`status = STAGED`, `parse_status = PENDING`), and inserts row into `baplie_parse_runs` (`status = QUEUED`, `source = FILE`) in a single transaction.
  3. Backend enqueues CT-08 job envelope to Redis `queue:edi` with `job_type = BAPLIE_PARSE` and payload `{"baplie_file_id": 1, "source": "FILE"}`.
  4. Worker `w_edi` consumes the job, marks `baplie_parse_runs.status = RUNNING`, verifies UNH identifier `BAPLIE:D:95B:UN:SMDG22`, and parses UNA, UNB, UNH, BGM, DTM, TDT, LOC, MEA, EQD segments.
  5. Worker inserts 12 container records into `containers` and `container_manifest_entries` with discharge port `EGDAM` and verified gross mass.
  6. Worker updates `baplie_parse_runs` (`status = DONE`, `outcome = PARSED`, `container_count = 12`) and updates `baplie_files.parse_status = PARSED`.
  7. Worker emits C-06 completion message to `queue:c06` (`status = SUCCESS`, `metrics.container_count = 12`).
  8. Backend consumes C-06 completion and transitions `baplie_files.status = ACTIVE`.
- Expected DB / Queue Result:
  - `baplie_files`: `parse_status = 'PARSED'`, `status = 'ACTIVE'`.
  - `baplie_parse_runs`: `status = 'DONE'`, `outcome = 'PARSED'`, `container_count = 12`.
  - `containers`: 12 rows created with verified ISO 6346 container numbers (`MSKU1234565`, `MSKU2345671`, `CMAU3456787`, etc.).
  - `container_manifest_entries`: 12 rows created with stowage cell coordinates (`0010282`, `0010482`, etc.) and port of discharge `EGDAM`.
  - `queue:c06`: Completion envelope published with `status = 'SUCCESS'`.
- Negative / Edge Cases Covered: Validates that standard 20ft (22G1) and 40ft (45G1) dry containers are correctly mapped under D.95B rules.
- Evidence Requirements: Database rows from `baplie_files`, `baplie_parse_runs`, and `container_manifest_entries`; Redis C-06 completion message log.

---

### TC-BAP-002: Special Cargo: Reefer & Hazmat Tagging (D.95B)
- Description: Verify that specialized cargo segments in UN/EDIFACT D.95B BAPLIE (temperature setting `TMP` for refrigerated containers and dangerous goods `DGS` for IMDG hazardous materials) are parsed and correctly mapped to domain columns.
- Target Sample File: `contracts/qa/baplie-corpus/02_valid_special_cargo_hazmat_reefer.edi`
- Preconditions:
  - Active berthing request `BR-DAM-2026-002`.
  - Worker `w_edi` listening on `queue:edi`.
- Execution Steps:
  1. Upload `02_valid_special_cargo_hazmat_reefer.edi` via `POST /api/v1/berthing-requests/BR-DAM-2026-002/baplie`.
  2. Backend stages file and enqueues job envelope to `queue:edi`.
  3. Worker `w_edi` processes manifest segments under D.95B rules:
     - Confirms UNH version `BAPLIE:D:95B:UN:SMDG22`.
     - Identifies reefer container `SUDU5566772` (ISO `45R1`) with segment `TMP+2+-18:CEL'` and ventilation `FTX+AAA+++VENT CLOSED'`.
     - Identifies hazmat container `HLXU6677881` (ISO `22G1`) with segment `DGS+IMD+3+1993+23:CEL+3'` and text `FTX+AAD+++FLAMMABLE LIQUID N.O.S.'`.
  4. Worker writes container records to database with specific cargo attributes populated.
  5. Worker completes parse run (`outcome = PARSED`) and sends C-06 message.
  6. Backend activates file (`status = ACTIVE`).
- Expected DB / Queue Result:
  - Reefer container `SUDU5566772`:
    - `is_reefer = 1`
    - `set_temperature = -18.00`
    - `temperature_unit = 'CEL'`
    - `ventilation = 'VENT CLOSED'`
    - `iso_type = '45R1'`
  - Hazmat container `HLXU6677881`:
    - `is_hazmat = 1`
    - `imdg_class = '3'`
    - `un_number = '1993'`
    - `flashpoint = 23.00`
    - `packing_group = '3'`
    - `proper_shipping_name = 'FLAMMABLE LIQUID N.O.S.'`
  - `baplie_files.parse_status = 'PARSED'`, `baplie_files.status = 'ACTIVE'`.
- Negative / Edge Cases Covered: Ensures negative temperatures are properly signed floats and IMDG classes with packing groups parse cleanly without data truncation.
- Evidence Requirements: Query results from `containers` table verifying temperature and IMDG columns.

---

### TC-BAP-003: Corrupt File Syntax Error
- Description: Verify parser robustness when processing an unrecoverable syntactically corrupted EDI file (unterminated segments, illegal characters, missing UNZ trailer), ensuring graceful failure without worker crash.
- Target Sample File: `contracts/qa/baplie-corpus/03_malformed_syntax_error.edi`
- Preconditions:
  - Active berthing request `BR-DAM-2026-003`.
  - Worker `w_edi` listening on `queue:edi`.
- Execution Steps:
  1. Upload `03_malformed_syntax_error.edi` via `POST /api/v1/berthing-requests/BR-DAM-2026-003/baplie`.
  2. Backend stages file and enqueues parse job to `queue:edi`.
  3. Worker `w_edi` attempts lexing and segment parsing.
  4. Parser encounters unterminated segment at line 4 (`BGM++CORRUPT_SYNTAX_03+9` missing apostrophe) and illegal character sequences at line 5.
  5. Parser traps the syntax exception, generates diagnostic error details, and records error in `baplie_parse_issues`.
  6. Worker updates `baplie_parse_runs` (`status = 'FAILED'`, `outcome = 'REJECTED'`, `error_category = 'INVALID_ENVELOPE'`).
  7. Worker updates `baplie_files.parse_status = 'FAILED'`. File status remains `STAGED`.
  8. Worker emits C-06 failure message (`status = 'FAILED'`, `error_code = 'BAPLIE_SYNTAX_ERROR'`).
  9. Worker returns to Redis event loop immediately to process subsequent queue items.
- Expected DB / Queue Result:
  - `baplie_files`: `parse_status = 'FAILED'`, `status = 'STAGED'`.
  - `baplie_parse_runs`: `status = 'FAILED'`, `outcome = 'REJECTED'`, `error_category = 'INVALID_ENVELOPE'`.
  - Zero rows inserted into `containers` or `container_manifest_entries`.
  - Redis worker heartbeat remains active (`worker:health:edi` TTL refreshed).
  - Worker process does not crash or exit with unhandled exception.
- Negative / Edge Cases Covered: Unterminated segments, missing message trailers (UNT/UNZ), and illegal non-ASCII character sequences.
- Evidence Requirements: `baplie_parse_runs` row with `outcome = 'REJECTED'`, error log stack trace confirming handled exception, and Redis worker health key.

---

### TC-BAP-004: Semantic Field Error Quarantine
- Description: Verify the quarantine and staged correction workflow when a structurally valid D.95B message contains semantic field defects (missing ISO size/type, invalid check digit, missing gross weight).
- Target Sample File: `contracts/qa/baplie-corpus/04_semantic_quarantine_missing_iso.edi`
- Preconditions:
  - Active berthing request `BR-DAM-2026-004`.
  - Worker `w_edi` active on `queue:edi`.
- Execution Steps:
  1. Upload `04_semantic_quarantine_missing_iso.edi` via `POST /api/v1/berthing-requests/BR-DAM-2026-004/baplie`.
  2. Backend stages file and enqueues job to `queue:edi`.
  3. Worker verifies UNH identifier `BAPLIE:D:95B:UN:SMDG22`, then runs semantic validation rules:
     - Detects missing ISO equipment size/type on line 2 (`MSKU2345671`).
     - Detects invalid ISO 6346 check digit on line 3 (`CMAU3456789`: expected 7, found 9).
     - Detects missing verified gross mass on line 4 (`CMAU4567893`: empty MEA weight).
  4. Worker records 3 issue rows in `baplie_parse_issues` with severity `ERROR`.
  5. Worker serializes extracted line objects into JSON and stores in `baplie_files.staged_payload`.
  6. Worker updates `baplie_parse_runs` (`status = 'DONE'`, `outcome = 'QUARANTINED'`) and `baplie_files.parse_status = 'QUARANTINED'`.
  7. Worker emits C-06 message (`status = 'PARTIAL_SUCCESS'`).
  8. Port staff accesses UI Screen P-21 (BAPLIE Quarantine & Correction), reviews highlighted field errors, inputs missing ISO type `22G1` and missing weight `26000`, and clicks "إعادة التحقق والاعتماد" (Re-validate & Commit).
  9. Backend enqueues new job to `queue:edi` with `source = 'STAGED_PAYLOAD'`.
  10. Worker validates edited payload, commits containers to database, sets `parse_status = 'PARSED'`, and Backend activates file (`status = 'ACTIVE'`).
- Expected DB / Queue Result:
  - Initial upload:
    - `baplie_files.parse_status = 'QUARANTINED'`, `baplie_files.status = 'STAGED'`.
    - `baplie_parse_runs.outcome = 'QUARANTINED'`.
    - `baplie_parse_issues`: 3 rows with issue codes `MISSING_ISO_TYPE`, `INVALID_CHECK_DIGIT`, `MISSING_WEIGHT`.
    - `baplie_files.staged_payload`: Valid JSON containing extracted lines.
    - Zero active container manifest records committed during quarantine.
  - Post-correction re-parse:
    - `baplie_files.parse_status = 'PARSED'`, `baplie_files.status = 'ACTIVE'`.
    - Corrected container records committed.
- Negative / Edge Cases Covered: Field-level quarantine vs file-level rejection; staff in-place correction workflow without re-uploading whole EDI file.
- Evidence Requirements: `baplie_parse_issues` rows, `staged_payload` JSON before and after correction, and final committed container entries.

---

### TC-BAP-005: SHA-256 Duplicate Upload Detection
- Description: Verify that attempting to upload an identical BAPLIE manifest for the same berthing request is immediately detected and rejected at the API boundary via SHA-256 hash collision, returning HTTP 409 Conflict.
- Target Sample File: `contracts/qa/baplie-corpus/05_duplicate_payload_sample.edi` (SHA-256 matches `01_valid_standard_discharge.edi`: `72abea92aacabb62768d5109788dfc5f244a793f0d7fe05091d79d5ba798f2f1`)
- Preconditions:
  - Berthing request `BR-DAM-2026-001` has already received, parsed, and activated `01_valid_standard_discharge.edi`.
  - File record in `baplie_files` is in status `ACTIVE`.
- Execution Steps:
  1. Operator attempts to upload `05_duplicate_payload_sample.edi` for `BR-DAM-2026-001`.
  2. Backend API streams the incoming file and computes its SHA-256 checksum: `72abea92aacabb62768d5109788dfc5f244a793f0d7fe05091d79d5ba798f2f1`.
  3. Backend queries `baplie_files` for existing active or pending file matching `(berthing_request_id, file_hash)`.
  4. Collision is detected against unique index `uq_bf_request_live_hash`.
  5. Backend rejects the request immediately, without inserting into `baplie_files` or `baplie_parse_runs`, and without publishing any message to `queue:edi`.
- Expected DB / Queue Result:
  - HTTP Status: `409 Conflict`.
  - Response Body: RFC 9457 Problem Details:
    - `type: "https://damietta-port.gov.eg/errors/duplicate-baplie"`
    - `code: "DUPLICATE_BAPLIE_FILE"`
    - `title: "Duplicate BAPLIE Manifest"`
    - `status: 409`
    - `detail: "An identical BAPLIE manifest (SHA-256: 72abea92aacabb62768d5109788dfc5f244a793f0d7fe05091d79d5ba798f2f1) is already active for this berthing request."`
  - Zero rows added to `baplie_files` or `baplie_parse_runs`.
  - Zero messages enqueued to `queue:edi`.
- Negative / Edge Cases Covered: Rapid double-submission by user, automated webhook retry deduplication.
- Evidence Requirements: HTTP 409 response payload and database query verifying file count remains unchanged.

---

### TC-BAP-006: Manifest Withdrawal & Replacement
- Description: Verify lifecycle state transitions across `STAGED`, `ACTIVE`, `REPLACED`, and `WITHDRAWN` when a revised manifest replaces an existing one, or when an active manifest is officially withdrawn.
- Target Sample File: Sequence of `01_valid_standard_discharge.edi`, revised manifest upload, and withdrawal action.
- Preconditions:
  - Berthing request `BR-DAM-2026-005` with existing active manifest (File ID 101, `status = 'ACTIVE'`).
  - Operational staff authenticated with role `BERTH_PLANNER` or `PORT_ADMIN`.
- Execution Steps:
  1. Shipping line provides revised manifest with updated bay allocations.
  2. Operator uploads revised manifest (File ID 102).
  3. Backend stages File ID 102 (`status = 'STAGED'`). Previous File ID 101 remains `ACTIVE` while parsing occurs.
  4. Worker `w_edi` parses File ID 102 successfully (`outcome = 'PARSED'`).
  5. Upon receiving C-06 completion, Backend executes atomic database transaction:
     - Sets File ID 101: `status = 'REPLACED'`.
     - Sets File ID 102: `status = 'ACTIVE'`.
  6. Due to operational cancellation of the vessel call, Port Authority staff invokes withdrawal:
     `POST /api/v1/berthing-requests/BR-DAM-2026-005/baplie/102/withdraw` with reason `VESSEL_CALL_CANCELLED`.
  7. Backend updates File ID 102: `status = 'WITHDRAWN'`.
  8. Associated container manifest entries are flagged as withdrawn; downstream yard placement jobs referencing this manifest are cancelled.
- Expected DB / Queue Result:
  - File ID 101 history: `STAGED` -> `ACTIVE` -> `REPLACED`.
  - File ID 102 history: `STAGED` -> `ACTIVE` -> `WITHDRAWN`.
  - Database table `baplie_files` maintains complete history of both records with timestamps and user attribution (`uploaded_by`, `withdrawn_by`).
  - No foreign key integrity violations.
- Negative / Edge Cases Covered: Uploading revised file does not prematurely replace active file before parse success; withdrawing manifest gracefully cascades to downstream yard jobs.
- Evidence Requirements: State audit logs in `audit_logs` table and history rows in `baplie_files`.

---

### TC-BAP-007: Unsupported Version Rejection (D.17A)
- Description: Verify that uploading an unsupported UN/EDIFACT directory version (such as D.17A `BAPLIE:D:17A:UN:SMDG20`) is rejected per contract CT-12 with outcome `REJECTED`, parse status `FAILED`, and an explicit diagnostic ERROR issue on segment UNH citing supported versions (SMDG 2.2.1 D.95B and SMDG 3.1.1 D.13B).
- Target Sample File: `contracts/qa/baplie-corpus/06_unsupported_version_d17a.edi`
- Preconditions:
  - Active berthing request `BR-DAM-2026-007`.
  - Worker `w_edi` active on `queue:edi`.
- Execution Steps:
  1. Upload `06_unsupported_version_d17a.edi` via `POST /api/v1/berthing-requests/BR-DAM-2026-007/baplie`.
  2. Backend stages file and enqueues parse job to `queue:edi`.
  3. Worker `w_edi` inspects UNH segment: `UNH+00001+BAPLIE:D:17A:UN:SMDG20'`.
  4. Parser evaluates directory version against supported versions: SMDG 2.2.1 (`D:95B`) and SMDG 3.1.1 (`D:13B`).
  5. Parser detects unsupported directory version `D:17A`.
  6. Worker records one ERROR issue in `baplie_parse_issues`:
     - `severity = 'ERROR'`
     - `segment_ref = 'UNH'`
     - `message = 'Unsupported BAPLIE version: BAPLIE:D:17A:UN:SMDG20. Supported: SMDG 2.2.1 (D.95B), SMDG 3.1.1 (D.13B)'`
  7. Worker updates `baplie_parse_runs` (`status = 'DONE'`, `outcome = 'REJECTED'`, `error_category = 'INVALID_ENVELOPE'`), updates `baplie_files.parse_status = 'FAILED'`. File status remains `STAGED`.
  8. Worker emits C-06 failure completion message to `queue:c06` (`status = 'FAILED'`, `error_code = 'UNSUPPORTED_BAPLIE_VERSION'`).
- Expected DB / Queue Result:
  - `baplie_files`: `parse_status = 'FAILED'`, `status = 'STAGED'`.
  - `baplie_parse_runs`: `status = 'DONE'`, `outcome = 'REJECTED'`, `error_category = 'INVALID_ENVELOPE'`.
  - `baplie_parse_issues`: exactly 1 row with `severity = 'ERROR'`, `segment_ref = 'UNH'`, and `message = 'Unsupported BAPLIE version: BAPLIE:D:17A:UN:SMDG20. Supported: SMDG 2.2.1 (D.95B), SMDG 3.1.1 (D.13B)'`.
  - Zero rows inserted into `containers` or `container_manifest_entries`.
  - `queue:c06`: Failure completion envelope published.
- Negative / Edge Cases Covered: Verifies strict version gate enforcement preventing unsupported EDI structures from corrupting container master data.
- Evidence Requirements: `baplie_parse_issues` record with exact error message, `baplie_parse_runs` outcome row, and C-06 event.
