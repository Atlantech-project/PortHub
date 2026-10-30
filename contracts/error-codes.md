# CT-01 · Error code catalogue

| | |
| --- | --- |
| Version | v1.1 |
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
| `PASSWORD_CHANGE_REQUIRED` | `errors.password_change_required` | 403 | The user must change their password before anything else | P1-A2 |
| `NOT_FOUND` | `errors.not_found` | 404 | The record or address does not exist | P1-A2 |
| `METHOD_NOT_ALLOWED` | `errors.method_not_allowed` | 405 | Wrong method; the `Allow` header lists the valid ones | P1-A2 |
| `VERSION_CONFLICT` | `errors.version_conflict` | 409 | The version token is stale; the body carries `current` | P1-A2 |
| `SESSION_EXPIRED` | `errors.session_expired` | 419 | CSRF token missing or stale on a web request; fetch a new CSRF cookie and retry | P1-C1 |
| `VALIDATION_FAILED` | `errors.validation_failed` | 422 | The data is not valid; the body carries `errors` | P1-A2 |
| `IDEMPOTENCY_KEY_REUSED` | `errors.idempotency_key_reused` | 422 | The `Idempotency-Key` was already used with a different body | P1-A2 |
| `PLAN_LIMIT_EXCEEDED` | `errors.plan_limit_exceeded` | 422 | Reserved: the write would exceed a plan limit (DEC-54) | P1-A2 |
| `LICENSE_READ_ONLY` | `errors.license_read_only` | 423 | Reserved: the licence is read-only, so writes are blocked (DEC-54) | P1-A2 |
| `APP_UPDATE_REQUIRED` | `errors.app_update_required` | 426 | The mobile app is older than the port's minimum; the body carries `min_app_version` | P1-A2 |
| `TOO_MANY_ATTEMPTS` | `errors.too_many_attempts` | 429 | Sign-in throttling; carries `Retry-After` | P1-A2 |
| `SERVER_ERROR` | `errors.server_error` | 500 | Unexpected failure, with no details | P1-A2 |
| `SERVICE_UNAVAILABLE` | `errors.service_unavailable` | 503 | Temporarily unavailable; may carry `Retry-After` | P1-A2 |

## Feature-specific keys

These are message keys, not codes. They give a more specific message under one of the codes above, in the form `errors.<area>.<name>`.

| Key | Used under | Meaning | Introduced by |
| --- | --- | --- | --- |
| `errors.auth.invalid_credentials` | `UNAUTHENTICATED`, as the text of `detail` | The username or password is incorrect | P1-C1 |

## Change log

| Version | Date | Change |
| --- | --- | --- |
| v1.1 | 2026-10-30 | Review rule: Frontend and Mobile review critical changes only; QA tests and does not review |
| v1.0 | 2026-10-30 | First version: 17 codes, matching `ErrorCode` on `develop` (P1-A2, P1-C1) |
