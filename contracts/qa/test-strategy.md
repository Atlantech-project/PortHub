# ATLANTECH Test Strategy (QA-01)

Owner: QA Team. Reviewers: all teams. Status: draft for review.
Items marked **Proposed** are not decided yet and need the teams to agree before this document is final.

## 1. Purpose and scope

This document says how ATLANTECH is tested: the test levels, the environments, what counts as evidence, and how defects are reported and fixed on the release branches.

It covers four code repositories: `project-backend`, `project-frontend`, `project-mobile` and `project-ai`. Contracts, the OpenAPI file and the database schema live in `PortHub`.

AI test data (the BAPLIE corpus and the reference data) follows its own contracts, CT-24 and CT-25, and is not repeated here.

## 2. Roles

| Who | Responsibility |
| --- | --- |
| Developers | Write and run their own unit and integration tests. Test their work on `develop` before it moves to `release`. Fix defects. |
| Leads (merge owners) | Merge pull requests into `develop`, merge components into `release`, and merge a finished version into `main`. |
| QA Team | Write acceptance test cases, test the `release` branch, report defects, retest fixes, and publish the release test report with the sign-off. |

## 3. Sprint rhythm

- A sprint starts on Sunday. The deadline is Friday at 12:00 midnight. Saturday is the review day.
- During the week QA prepares the acceptance test cases for the features that will be handed over at the FRR (QA-TC tasks).
- After the handover QA tests the release branch and publishes the sign-off report (QA-RT tasks).

## 4. Branches and where QA tests

| Branch | Purpose | QA role |
| --- | --- | --- |
| `feature/<task-name>` | Work on one task, created from `develop` | None |
| `develop` | Integration of finished tasks. Pull request required. | None. The developer makes a first test here. |
| `release` | Components that passed the developer's test, merged by the leads | **QA tests here** |
| `main` | A complete, tested version | Receives only a version signed off by QA |

Flow:

1. The developer tests the work on `develop`.
2. The leads merge the component into `release`.
3. QA tests `release`. If there are defects, QA reports them (section 9) and the work goes back to `develop`.
4. After the fix, the component is merged into `release` again and QA retests it.
5. When a full version is tested and signed off, it goes to `main` and is tagged, for example `git tag -a v1.0.0 -m "Release version 1.0.0"`.

## 5. Test levels

| Level | Owner | Where | When |
| --- | --- | --- | --- |
| Unit and integration | Developers | In each repository, run by CI on pull requests | Every pull request |
| Acceptance | QA | Against the feature's requirements and screens | Cases written each sprint (QA-TC), run on `release` |
| Regression | QA | Re-run of earlier acceptance cases on `release` | Every release test (QA-RT) |
| End to end | QA, with all teams | The eight main workflows WF-1 to WF-8 on the demo environment | Sprint 7 (QA-E2E) |
| User acceptance | QA | UAT script and demo rehearsal | Sprint 8 (QA-UAT) |

## 6. Approach per component

**Proposed.** Automate as much as possible, and keep manual testing for what cannot be automated well.

| Component | What QA covers | How |
| --- | --- | --- |
| Backend | API behaviour against the OpenAPI file: the checks in the write chain (401, 403, 426, 423, 409, 422), license modes, state transitions, audit entries | Automated API tests against the Docker environment. Cases come from the requirements and the OpenAPI file. |
| Frontend | The main user journeys on the dashboard, role and terminal restrictions, read-only behaviour, live updates | Automated browser tests for the main journeys. Manual checks for layout and wording. |
| Mobile | Sign-in and re-sign-in, offline work, the outbox and its sync, duplicate and rejected events, the read-only banner | Automated tests where possible. Offline and device behaviour is tested manually on an emulator and a real device. |
| AI | Worker contract behaviour (CT-08 to CT-16), queue envelopes, C-06 completion messages, database result rows, heartbeats, and domain invariants (I-1 to I-15). | Black-box testing at the Redis queue and MySQL boundary plus data oracles (BAPLIE corpus, reference data, hand calculations), as detailed in contracts/qa/ai-testing-guide.md. |

## 7. Environments

| Environment | Use | Status |
| --- | --- | --- |
| Local | Run the backend from `develop` or `release` with `docker compose --profile server up -d --build`. It runs the app, nginx, MySQL and Redis at `http://localhost:8000`. | Available |
| CI (GitHub Actions) | Developer tests on pull requests. Backend, frontend and AI have CI. Mobile has none yet. | Partly available |
| Dev server | Updated on every merge to `develop` | Planned (P6-R6) |
| Demo | Separate environment updated on every release. Used for the end-to-end suite. | Planned (P6-R6) |

Seed data arrives with P1-B6. Until then QA creates the data each test needs and lists it in the evidence.

## 8. Entry and exit criteria for testing a release

**Entry** (QA starts testing a release when):

- The component is merged into `release` by the leads.
- The developer's own tests passed on `develop` and CI is green.
- The API readiness pack for the FRR (CT-23) is available.

**Exit** (the release test is finished when):

- Every acceptance case for the handed-over features was run.
- The regression cases were run.
- No Blocker defect is open.
- The release test report is published in `contracts/qa/reports/`.

## 9. Evidence rules

A test result counts only with evidence.

- Every test case has an ID, steps, an expected result and an actual result.
- Evidence is a screenshot, a log, or an API request and response with the status code.
- Every result records the repository, the branch and the commit that was tested, and the date.
- A defect without evidence is not accepted.
- A test is marked Passed only after it was run on the commit named in the report.

## 10. Defect workflow on the release branches

Defects are logged as GitHub Issues with the defect form (CT-26). Labels: `defect`, `severity:blocker`, `severity:major`, `severity:minor`.

| Severity | Meaning |
| --- | --- |
| Blocker | Stops the release. The version cannot go to `main`. |
| Major | A feature does not work and there is no workaround. |
| Minor | Cosmetic issue, or a workaround exists. |

Steps:

1. **Open.** QA opens an Issue in the repository that owns the problem, filled in with the defect form and evidence.
2. **Fixing.** The owning team takes it, creates `feature/<task-name>` from `develop`, fixes it, and merges it through a pull request.
3. **Back to release.** The leads merge the fix into `release`.
4. **Retest.** QA retests on `release` and writes the result and evidence in the Issue.
5. **Closed or reopened.** QA closes the Issue if it passes. If it fails, QA reopens it with new evidence.

Release result in the report:

- **PASS:** no open defects.
- **PASS WITH NOTES:** no open Blocker. Open Major or Minor defects are listed in the notes. **Proposed.**
- **FAIL:** at least one open Blocker.

## 11. Reporting

For every release QA publishes `contracts/qa/reports/release-report-v0.N.0.md`, made from the template in `contracts/qa/release-report-template.md`.

## 12. Points the teams need to agree

1. How an open Major defect is handled when a release goes to `main` (the PASS WITH NOTES rule above).
2. How fast a Blocker must be taken by the owning team.
3. Adding CI to `project-mobile`.
4. The place for acceptance test cases. **Proposed:** `contracts/qa/test-cases/FT-xx.md`.
5. The test data to use until seed data (P1-B6) is available.
