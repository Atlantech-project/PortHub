# CT-01 · Error code catalogue

| | |
| --- | --- |
| Version | v1.5 |
| Status | Approved |
| Owner | Backend Team |
| Reviewers | Frontend Team · Mobile Team, critical changes only ([README](README.md)) |
| Approved by | Marwan (Backend lead), 2026-10-30. Adopted without team review (DEC-57) |
| Rules | [`api-conventions.md`](api-conventions.md), section 6 |

Every stable error code the port API returns. A code, its HTTP status and its `message_key` never change once approved.

A new code is added in the PR of the task that introduces it, with a minor version bump ([`README.md`](README.md)).

## Codes

- `code` is UPPER_SNAKE.
- `message_key` is `errors.<lower_snake code>`.
- `type` is `https://atlantech.io/errors/<kebab-code>`.
- A reserved code is defined but not returned yet.

| `code` | `message_key` | Status | Meaning | Introduced by |
| --- | --- | --- | --- | --- |
| `BAD_REQUEST` | `errors.bad_request` | 400 | Any other client error the framework raises (for example 413, 415), or a web sign-in from an origin that is not allowed | P1-A2 |
| `UNAUTHENTICATED` | `errors.unauthenticated` | 401 | Not signed in, session ended, or wrong credentials | P1-A2 |
| `FORBIDDEN` | `errors.forbidden` | 403 | Signed in, but the role or terminal scope does not allow this | P1-A2 |
| `ACCOUNT_DISABLED` | `errors.account_disabled` | 403 | The account is deactivated | P1-A2 |
| `DEVICE_REVOKED` | `errors.device_revoked` | 403 | Mobile sign-in from a device the Port Admin revoked; no token is issued (DEC-60) | P1-C3 |
| `PASSWORD_CHANGE_REQUIRED` | `errors.password_change_required` | 403 | The user must change their password before anything else | P1-A2 |
| `NOT_FOUND` | `errors.not_found` | 404 | The record or address does not exist | P1-A2 |
| `METHOD_NOT_ALLOWED` | `errors.method_not_allowed` | 405 | Wrong method; the `Allow` header lists the valid ones | P1-A2 |
| `VERSION_CONFLICT` | `errors.version_conflict` | 409 | The version token is stale; the body carries `current` | P1-A2 |
| `CONFLICT` | `errors.conflict` | 409 | A business rule refuses the change in the record's current state; `detail` holds a feature key that says which | P2-E1 |
| `SESSION_EXPIRED` | `errors.session_expired` | 419 | CSRF token missing or stale on a web request; fetch a new CSRF cookie and retry | P1-C1 |
| `VALIDATION_FAILED` | `errors.validation_failed` | 422 | The data is not valid; the body carries `errors` | P1-A2 |
| `IDEMPOTENCY_KEY_REUSED` | `errors.idempotency_key_reused` | 422 | The `Idempotency-Key` was already used with a different request (body, path or method) | P1-A2 |
| `PLAN_LIMIT_EXCEEDED` | `errors.plan_limit_exceeded` | 422 | The write would exceed a plan limit: active users (P2-E1, FR-AC-09); terminals and berths stay reserved until P2-D5 (DEC-54) | P1-A2 |
| `LICENSE_READ_ONLY` | `errors.license_read_only` | 423 | Reserved: the licence is read-only, so writes are blocked (DEC-54) | P1-A2 |
| `APP_UPDATE_REQUIRED` | `errors.app_update_required` | 426 | The mobile app is older than the port's minimum; the body carries `min_app_version` | P1-A2 |
| `TOO_MANY_ATTEMPTS` | `errors.too_many_attempts` | 429 | Sign-in and password-change throttling; carries `Retry-After` | P1-A2 |
| `SERVER_ERROR` | `errors.server_error` | 500 | Unexpected failure, with no details | P1-A2 |
| `SERVICE_UNAVAILABLE` | `errors.service_unavailable` | 503 | Temporarily unavailable; may carry `Retry-After` | P1-A2 |

## Feature-specific keys

These are message keys, not codes. They give a more specific message under one of the codes above, in the form `errors.<area>.<name>`.

| Key | Used under | Meaning | Introduced by |
| --- | --- | --- | --- |
| `errors.auth.invalid_credentials` | `UNAUTHENTICATED`, as the text of `detail` | The username or password is incorrect | P1-C1 |
| `errors.users.cannot_deactivate_self` | `CONFLICT`, as the text of `detail` | A user cannot deactivate their own account | P2-E1 |
| `errors.users.last_port_admin` | `CONFLICT`, as the text of `detail` | At least one active Port Admin must remain (FR-AC-12) | P2-E1 |

## Change log

| Version | Date | Change |
| --- | --- | --- |
| v1.5 | 2026-11-21 | Added `CONFLICT` 409 and the keys `errors.users.cannot_deactivate_self`, `errors.users.last_port_admin` (P2-E1). `PLAN_LIMIT_EXCEEDED` is now returned for the active-user limit; the other plan limits stay reserved |
| v1.4 | 2026-11-06 | `IDEMPOTENCY_KEY_REUSED` also covers another path or method under the same key (IDEMP-01). `SERVICE_UNAVAILABLE` (503, `Retry-After`) is now also returned while the first request with the same key still runs; its row already allowed `Retry-After`. Wording only, code, status and key unchanged |
| v1.3 | 2026-11-06 | Added `DEVICE_REVOKED` 403, introduced by P1-C3 (DEC-60, CT-04 v1.2) |
| v1.2 | 2026-10-30 | 429 also covers password-change throttling (P1-C2) |
| v1.1 | 2026-10-30 | Review rule: Frontend and Mobile review critical changes only; QA tests and does not review |
| v1.0 | 2026-10-30 | First version: 17 codes, matching `ErrorCode` on `develop` (P1-A2, P1-C1) |
