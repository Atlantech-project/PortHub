# ATLANTECH contracts

This folder is the single source of truth for what the ATLANTECH teams (Backend, Frontend, Mobile, AI, QA) promise each other. If a contract here and a team's code or notes disagree, the contract wins until it is changed through the rule below. The exception is CT-01 and CT-02: when the code on `develop` differs, the contract is corrected to match (see below).

## Files

| File | What it holds | Owner |
| --- | --- | --- |
| [`api-conventions.md`](api-conventions.md) | CT-01: the rules every port API endpoint follows (base path, time, headers, idempotency, version token, errors, pagination) | Backend Team |
| [`error-codes.md`](error-codes.md) | CT-01: the catalogue of stable error codes | Backend Team |
| [`auth-web.md`](auth-web.md) | CT-03: web sign-in, password change and session | Backend Team |
| [`realtime-sse.md`](realtime-sse.md) | CT-05: web SSE events | Backend Team |
| [`realtime-mobile.md`](realtime-mobile.md) | CT-06: mobile WebSocket events | Backend Team |
| [`sync-events.md`](sync-events.md) | CT-07: mobile sync (Outbox) | Backend and Mobile Teams |
| [`mock-workers.md`](mock-workers.md) | CT-19: mock worker behaviour | Backend Team |
| [`status-vocabulary.json`](status-vocabulary.json) | CT-21: every enum value, generated from the PHP enums | Backend Team |
| [`openapi/port-api.yaml`](openapi/port-api.yaml) | CT-02: the port API OpenAPI file | Backend Team |
| [`readiness/`](readiness/TEMPLATE.md) | CT-23: the API readiness pack template and one pack per feature | Backend Team |
| [`ATLANTECH_Contracts.md`](ATLANTECH_Contracts.md) | All contracts CT-01 to CT-26: summary, owners, reviewers and the text of those without a file of their own | Backend Team, with each contract's owner |
| [`ATLANTECH_Decisions.md`](ATLANTECH_Decisions.md) | The decision log (`DEC-xx`) | Leads Council |
| [`ai/`](ai/) | AI payload schemas and the Data Ownership Matrix (CT-15) | Backend and AI Teams |
| [`db/`](db/) | The schema snapshot and the table names | Backend Team |

## Versioning

Every contract file carries its version and status in its header, and a change log.

- **Status:** `Draft` while under review, `Approved` once its reviewers have approved it. The header records the approvers and the date.
- **Changing an approved contract** needs three things in the same PortHub PR:
  1. Agreement of both sides: the owner and a reviewer from each team that consumes the contract.
  2. An entry in the decision log.
  3. A new version number and a change-log line.
- **Major version** (`v2.0`): a breaking change. On the API this also means a new base path (`/api/v2`) served alongside `/api/v1`.
- **Minor version** (`v1.1`): an addition that breaks nobody. Adding an error code to `error-codes.md` is a minor change made in the PR of the task that introduces the code; it needs no review and no decision-log entry.
- A code, its HTTP status and its `message_key` never change once approved. Retiring one is a breaking change.

### Port API contracts (CT-01, CT-02)

The Backend Team's code is the source of truth, and the clients build on it. So these two contracts replace the "both sides" condition above:

- Frontend and Mobile review **critical changes only**: a breaking change, or a change to a rule or shape they already build on.
- Any other change needs no team review and no decision-log entry, only a new version and a change-log line.
- QA tests against these contracts and does not review them.

## Working here

Changes reach `main` only through a pull request; branches are named `feature/<task-id>-<slug>`.
