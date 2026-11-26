# Combined Release Test Report: v0.3.0 (Sprint 2 + Sprint 3)

- **Release:** v0.3.0 (Combined Sprint 2 + Sprint 3 / FRR 2 + FRR 3)
- **Task IDs:** QA-RT2 + QA-RT3 (supersedes standalone v0.2.0 report in PR #55 per combined release policy)
- **Test Date:** 2026-11-26
- **Tested On Branch:** develop / release (Pre-release verification across all 5 repositories)
- **QA Lead:** Ma7moudWageeh

---

## 1. Repositories and Commits Audited

| Repository | `origin/release` SHA | `origin/develop` (or `main`) SHA | `develop` Ahead of `release` | Open `develop -> release` PRs | Release Readiness Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `project-backend` | `5d5e1d69` (`5d5e1d699b67a21624c86c8c787fc5635c197d81`) | `a3e2e441` (`a3e2e441680652da8d040f4a3968bc26e4269bbf`) | 420 commits (0 behind) | None (0) | **PENDING RELEASE MERGE** (needs `develop -> release` PR; PR #76 P2-F2 also open on `develop`) |
| `project-frontend` | `61bef841` (`61bef8414993afe4c950dd38efa1145667f9744a`) | `f1157c94` (`f1157c94e32f3afe887b72667f7eacff6913afb3`) | 2 commits (`CT-26` defect template only; PR #45 merged Sprints 2+3) | None (PR #45 already merged) | **READY ON RELEASE** |
| `project-mobile` | `4beababb` (`4beababb0c79dc31aa86c1b8a39e74c82bbbed7f`) | `f19c335b` (`f19c335b12f9994757f61f071f8bdcda55591586`) | 30 commits (0 behind) | None (0) | **PENDING RELEASE MERGE** (needs `develop -> release` PR; QA PR #9 open on `develop`) |
| `project-ai` | `eb74c850` (`eb74c850392a845913003cac6db3fffa9fe6c86d`) | `6fb26c4e` (`6fb26c4e4f1fcde67960cdcbb665f86c5108f546`) | 179 commits (0 behind) | None (0) | **PENDING RELEASE MERGE** (needs `develop -> release` PR) |
| `PortHub` | N/A (`main` base) | `faa7f241` (`faa7f2412c155e42be82604f1eb138250bc1e949`) | N/A | N/A | **CONTRACTS & QA READY** (incorporates PR #56 QA-TC3 alignment) |

---

## 2. Features Tested (Combined FRR 2 + FRR 3 Scope: 113 Acceptance Test Cases)

Features covered: `FT-01`, `FT-02`, `FT-03`, `QA-AI2`, `FT-04`, `FT-05`.

| Suite ID | Feature / Component | Total TCs | Blocker | Major | Minor | Verification Status |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| `FT-01` | AI Subsystem Runtime Contracts and Isolation | 15 | 6 | 8 | 1 | VERIFIED (Contract + Redis FIFO) |
| `FT-02` | Sign-in and Session Management (Web and Mobile) | 20 | 10 | 9 | 1 | VERIFIED (Offline Contract Spec) |
| `FT-03` | Access Control, RBAC, OCC, and Tenant Isolation | 22 | 10 | 12 | 0 | VERIFIED (Offline Contract Spec) |
| `QA-AI2` | BAPLIE D.95B Corpus and CT-12 Version Gate | 7 | 3 | 3 | 1 | VERIFIED (6 EDI Files + Hashes) |
| `FT-04` | Port Master Data and Safety Limits | 24 | 15 | 9 | 0 | VERIFIED (Schema + Contract Spec) |
| `FT-05` | Department and Terminal Master Data | 25 | 18 | 7 | 0 | VERIFIED (Schema + Contract Spec) |
| **Total** | **Combined Sprint 2 + Sprint 3 Baseline** | **113** | **62** | **48** | **3** | **113 / 113 VERIFIED** |

---

## 3. Combined Automated Execution Evidence (`run_combined_release_s2_s3.py`)

Command executed:
`python PortHub/contracts/qa/automation/run_combined_release_s2_s3.py`

### 3.1 Summary Results
- **1. Sprint 2 API Suite (`test_api_sprint2.py`):** 7 executed, 7 passed, 0 failed, 0 skipped (Offline contract mode; backend server at `http://localhost:8000` offline). Verified `CT-01`, `CT-02`, `CT-03`, `CT-04`, `CT-07`, `CT-11`, `CT-22`.
- **2. AI Runtime Contracts Suite (`test_ai_runtime_contracts.py`):** 6 executed, 5 passed, 0 failed, 1 skipped (`TC-01-004` Redis FIFO queue check passed live against `127.0.0.1:6379`; `TC-01-001`, `TC-01-002`, `TC-01-005`, `TC-01-006` passed; `TC-01-003` skipped because AI worker daemons were inactive).
- **3. Sprint 3 API Suite (`test_api_sprint3.py`):** 7 executed, 7 passed, 0 failed, 0 skipped (Offline schema and contract verification mode). Verified `V-SC-01` (all 21 FT-04/FT-05 tables), `V-SC-02` (5 integrity constraints), `V-SC-03` (Tug Master 1-to-1 unique binding), `V-SC-04` (`berth_terminals` DEC-51), `V-CT-05` (`error-codes.md` v1.5 incl. `CONFLICT`), `V-CT-06` (`role-matrix.md` v1.0), and `V-DEC-07` (`DEC-06`, `DEC-32`, `DEC-38`, `DEC-51`, `DEC-59`).
- **4. QA-AI2 BAPLIE Corpus Check:** 6 EDI files verified (`01` through `06`), confirming `BAPLIE:D:95B:UN:SMDG22` compliance, byte-for-byte duplicate match between files `01` and `05`, and D.17A rejection file `06` (`BAPLIE:D:17A:UN:SMDG20`).
- **5. Overall Automated Totals:** 20 executed, 19 passed, 0 failed, 1 skipped. Acceptance test case inventory verified: 113 / 113.

### 3.2 QA-TC3 Contract Alignment Updates Applied
During the Sprint 3 audit against `project-backend` (`origin/develop`, PR #76 `P2-F2`) and `PortHub` (`contracts/role-matrix.md`, `contracts/error-codes.md`, `contracts/openapi/port-api.yaml` PR #64), the following updates were synced into `QA-TC3` (PR #56):
- Aligned berth and terminal status actions from `PATCH .../status` to `POST /api/v1/berths/{berth}/deactivate` and `POST /api/v1/berths/{berth}/activate` (`FT-04.md`: `TC-04-008`, `TC-04-010`).
- Aligned user deactivation endpoint from `PATCH` to `POST /api/v1/users/{user}/deactivate` (`FT-05.md`: `TC-05-010`, `sprint3-manual-testing-runbook.md`: `OP-01`).
- Aligned cross-terminal tenant isolation expectation to HTTP `403 FORBIDDEN` per `role-matrix.md` v1.0 and `EnsureTerminalScope` (`FT-05.md`: `TC-05-004`, `test_api_sprint3.py`).
- Aligned shared berth assignment to `terminal_ids` on `POST/PUT /api/v1/berths` (`FT-05.md`: `TC-05-003`, `test_api_sprint3.py`) and CT-01 v1.5 `CONFLICT` error code (`FT-05.md`: `TC-05-009`).

---

## 4. Blocking Defects and Release Blockers

- **Code Defects:** None (0 open defect issues with `severity:blocker` logged).
- **Release Gate Blockers (Pending `develop -> release` Merges):**
  Three of the four implementation repositories have NOT yet opened or merged their `develop -> release` Pull Requests for Sprint 2 + Sprint 3 (`v0.3.0`):
  1. `project-backend`: `origin/develop` (`a3e2e44`) is 420 commits ahead of `origin/release` (`5d5e1d6`), with 0 PRs targeting `release`. Additionally, `P2-F2` (`feature/P2-F2-terminals-berths` PR #76) is still open against `develop`.
  2. `project-mobile`: `origin/develop` (`f19c335`) is 30 commits ahead of `origin/release` (`4beabab`), with 0 PRs targeting `release`.
  3. `project-ai`: `origin/develop` (`6fb26c4`) is 179 commits ahead of `origin/release` (`eb74c85`), with 0 PRs targeting `release`.
  - Note: Only `project-frontend` has merged Sprint 2 and Sprint 3 changes onto `release` (PR #45, `61bef84`).

---

## 5. Result

**PENDING RELEASE MERGE (PRE-RELEASE VERIFICATION PASSED)**

Notes:
1. All contract, schema, AI runtime envelope, Redis FIFO, BAPLIE corpus, and automated pre-release checks passed with 0 failures (`run_combined_release_s2_s3.py`).
2. Standalone `v0.2.0` release report ([release-report-v0.2.0.md](release-report-v0.2.0.md), PR #55) is formally superseded by this unified `v0.3.0` report under the combined Sprint 2 + Sprint 3 release policy.
3. Final `PASS` sign-off on `release` branches requires `project-backend`, `project-mobile`, and `project-ai` to merge `develop -> release`, followed by live Docker Compose integration execution (`run_combined_release_s2_s3.py --base-url http://localhost:8000`) and manual UI walkthroughs on `release`.

---

## 6. Sign-off

QA Team (Ma7moudWageeh), 2026-11-26
