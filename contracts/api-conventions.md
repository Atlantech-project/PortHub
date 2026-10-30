# CT-01 · Port API conventions

| | |
| --- | --- |
| Version | v1.0 |
| Status | Approved |
| Owner | Backend Team |
| Reviewers (from v1.1) | Frontend Team · Mobile Team · QA Team |
| Approved by | Marwan (Backend lead), 2026-10-30. Adopted without Frontend, Mobile or QA review; those teams review every change from now on (DEC-57) |
| Error codes | [`error-codes.md`](error-codes.md) |

These rules apply to every endpoint of the port API under `/api/v1`. The endpoints themselves are in [`openapi/port-api.yaml`](openapi/port-api.yaml) (CT-02). How this file changes is in [`README.md`](README.md).

## 1. Base path and versioning

- The base path is `/api/v1`.
- A breaking change means a new base path, `/api/v2`, served alongside `/api/v1`.
- Requests and responses are JSON. Errors use the content type `application/problem+json`.

## 2. Time

- **Output:** every datetime is ISO 8601 in UTC with microseconds: `2026-11-02T10:15:04.123456Z`.
- **Input:** a datetime must carry `Z` or an explicit `±HH:MM` offset, with up to 6 fraction digits. It is converted to UTC.
- A value with no timezone, or in another shape, is refused with 422 and `validation.regex`. A correct shape that is not a real date is refused with `validation.date`.
- The client converts to local time for display (DEC-45).
- Shift times (local `TIME` values) are not datetimes and do not follow this section.

## 3. Headers

| Client | Header | When |
| --- | --- | --- |
| Web | Session cookie (Sanctum SPA) | Every request |
| Web | `X-XSRF-TOKEN`: the value of the `XSRF-TOKEN` cookie | Every write |
| Mobile | `Authorization: Bearer <token>` | Every signed-in request |
| Mobile | `X-App-Version` | Every request |
| Mobile | `X-Device-Id` | Every request |
| Mobile | `Idempotency-Key` | Every write (section 4) |

The web client gets the CSRF cookie from `GET /sanctum/csrf-cookie`. A missing or stale token returns 419 `SESSION_EXPIRED`: fetch a new cookie and retry.

## 4. Idempotency

- Every mobile write carries an `Idempotency-Key`: a UUID v4, one per logical write. Retries of the same write reuse the same key.
- The server keeps a key for 24 hours.
- Same key and same body: the first response is replayed, and the write does not run again.
- Same key and a different body: 422 `IDEMPOTENCY_KEY_REUSED`.
- A missing or malformed key: 422 `VALIDATION_FAILED`.
- Sync events do not use this header; they keep `client_event_id` (CT-07).

## 5. Version token

- Every editable record returns a `version` field. Its value is the record's `updated_at` (`DATETIME(6)`), in the output format of section 2.
- Treat `version` as an opaque string: store it and send it back exactly as received. Do not parse it into a date type, because JavaScript's `Date` keeps milliseconds only and the rounded value would be refused.
- Every update sends the `version` it last read. A stale value returns 409 `VERSION_CONFLICT`, and the body carries `current: { id, version }` with the stored values.

## 6. Errors

Every error on `/api/v1` is an RFC 9457 problem body with all of these members:

| Member | Value |
| --- | --- |
| `type` | `https://atlantech.io/errors/<kebab-code>`. An identifier, not a page |
| `title` | A short English title, fixed per code |
| `status` | The HTTP status |
| `code` | The stable code, in UPPER_SNAKE ([catalogue](error-codes.md)) |
| `message_key` | The translation key: `errors.<lower_snake code>` |
| `detail` | An English message for people. It may be more specific than the catalogue text, so never branch on it |

Extra members by status: `errors` on 422, `current` on 409, `min_app_version` on 426.

Rules:

- Clients branch on `code` and translate by `message_key`. Bodies never contain stack traces, SQL, class names or file paths.
- `errors.<area>.<name>` is for feature-specific keys only, for example `errors.berth.loa_exceeds_length`.
- `detail` is English in v1.0. Keys live in `lang/en` now and in `lang/ar` when FR-GL-09 is scheduled. There is no `Accept-Language` in v1.0.

### Validation errors

422 `VALIDATION_FAILED` carries `errors` as `{ field: [message keys] }`. The values are keys, not English sentences:

- Laravel rules: `validation.<rule>`, for example `validation.max`.
- Feature rules: `errors.<area>.<name>`.

`detail` is the first English message.

## 7. Status codes

| Status | Meaning | Code |
| --- | --- | --- |
| 200 | Success with a body | — |
| 201 | Record created | — |
| 202 | Accepted; the work runs asynchronously (for example customs approval) | — |
| 204 | Success with no body | — |
| 400 | Any other client error (for example 413, 415) | `BAD_REQUEST` |
| 401 | Not signed in, session ended, or wrong credentials | `UNAUTHENTICATED` |
| 403 | Signed in but not allowed | `FORBIDDEN`, `ACCOUNT_DISABLED`, `PASSWORD_CHANGE_REQUIRED` |
| 404 | The record or address does not exist | `NOT_FOUND` |
| 405 | Wrong method; the `Allow` header lists the valid ones | `METHOD_NOT_ALLOWED` |
| 409 | Stale version token; features add their own business-rule conflicts | `VERSION_CONFLICT` |
| 419 | CSRF token missing or stale (web) | `SESSION_EXPIRED` |
| 422 | The data was refused | `VALIDATION_FAILED`, `IDEMPOTENCY_KEY_REUSED`, `PLAN_LIMIT_EXCEEDED` (reserved) |
| 423 | Reserved: the licence is read-only; the licence work is deferred (DEC-54) | `LICENSE_READ_ONLY` |
| 426 | Mobile app older than the port's minimum | `APP_UPDATE_REQUIRED` |
| 429 | Sign-in throttling only; carries `Retry-After` | `TOO_MANY_ATTEMPTS` |
| 500 | Unexpected failure, with no details | `SERVER_ERROR` |
| 503 | Temporarily unavailable; may carry `Retry-After` | `SERVICE_UNAVAILABLE` |

When several refusals apply, a write returns the first in this order (FR-GL-01): 401, 403, 426, 423, 409 for the version token, 409 or 422 for business rules, 422 for plan limits.

## 8. Pagination

- Request: `?page=&per_page=`. `page` is 1 to 1 000 000, default 1. `per_page` is 1 to 100, default 25.
- Response: `{ "data": [...], "meta": { "page", "per_page", "total" } }` and nothing else: no `links` and no other paginator fields.
- A value out of range returns 422 `VALIDATION_FAILED`. It is never clamped.
- A page past the end returns 200 with empty `data`.
- Each endpoint states its ordering in the OpenAPI file.

## 9. Single records

A single record is the response body itself, with no `data` wrapper. Only lists use `data` (section 8).

## 10. Examples

### 200 list

```json
{ "data": [ { "id": 1 } ], "meta": { "page": 1, "per_page": 25, "total": 132 } }
```

### 201 created

```json
{ "id": 12, "version": "2026-11-02T10:15:04.123456Z" }
```

### 202 accepted

The endpoint defines the body. It is often the record in its new state:

```json
{ "id": 12, "version": "2026-11-02T10:15:04.123456Z" }
```

### 204 no content

No body.

### 400

```json
{
  "type": "https://atlantech.io/errors/bad-request",
  "title": "Bad request",
  "status": 400,
  "code": "BAD_REQUEST",
  "message_key": "errors.bad_request",
  "detail": "The request could not be processed. Check what you sent and try again."
}
```

### 401

```json
{
  "type": "https://atlantech.io/errors/unauthenticated",
  "title": "Unauthenticated",
  "status": 401,
  "code": "UNAUTHENTICATED",
  "message_key": "errors.unauthenticated",
  "detail": "You are not signed in, or your session has expired. Sign in and try again."
}
```

### 403

```json
{
  "type": "https://atlantech.io/errors/account-disabled",
  "title": "Account disabled",
  "status": 403,
  "code": "ACCOUNT_DISABLED",
  "message_key": "errors.account_disabled",
  "detail": "Your account has been disabled. Contact your port administrator."
}
```

### 404

```json
{
  "type": "https://atlantech.io/errors/not-found",
  "title": "Not found",
  "status": 404,
  "code": "NOT_FOUND",
  "message_key": "errors.not_found",
  "detail": "The requested item was not found. It may have been removed."
}
```

### 405

Response header: `Allow: GET, HEAD`

```json
{
  "type": "https://atlantech.io/errors/method-not-allowed",
  "title": "Method not allowed",
  "status": 405,
  "code": "METHOD_NOT_ALLOWED",
  "message_key": "errors.method_not_allowed",
  "detail": "This action is not supported at this address."
}
```

### 409

```json
{
  "type": "https://atlantech.io/errors/version-conflict",
  "title": "Record changed",
  "status": 409,
  "code": "VERSION_CONFLICT",
  "message_key": "errors.version_conflict",
  "detail": "This record was changed by another user. Reload it and apply your changes again.",
  "current": { "id": 12, "version": "2026-11-02T10:15:04.123456Z" }
}
```

### 419

```json
{
  "type": "https://atlantech.io/errors/session-expired",
  "title": "Session expired",
  "status": 419,
  "code": "SESSION_EXPIRED",
  "message_key": "errors.session_expired",
  "detail": "Your session security token has expired. Reload the page and try again."
}
```

### 422

```json
{
  "type": "https://atlantech.io/errors/validation-failed",
  "title": "Validation failed",
  "status": 422,
  "code": "VALIDATION_FAILED",
  "message_key": "errors.validation_failed",
  "detail": "The name field is required.",
  "errors": {
    "name": ["validation.required"],
    "max_vessel_loa": ["errors.berth.loa_exceeds_length"]
  }
}
```

### 423 (reserved)

```json
{
  "type": "https://atlantech.io/errors/license-read-only",
  "title": "License is read-only",
  "status": 423,
  "code": "LICENSE_READ_ONLY",
  "message_key": "errors.license_read_only",
  "detail": "The port license is read-only: you can view data, but changes are blocked. Contact your port administrator."
}
```

### 426

```json
{
  "type": "https://atlantech.io/errors/app-update-required",
  "title": "App update required",
  "status": 426,
  "code": "APP_UPDATE_REQUIRED",
  "message_key": "errors.app_update_required",
  "detail": "This version of the app is no longer supported. Update the app to continue.",
  "min_app_version": "2.4.0"
}
```

### 429

Response header: `Retry-After: 60`

```json
{
  "type": "https://atlantech.io/errors/too-many-attempts",
  "title": "Too many attempts",
  "status": 429,
  "code": "TOO_MANY_ATTEMPTS",
  "message_key": "errors.too_many_attempts",
  "detail": "Too many attempts. Wait a moment and try again."
}
```

### 500

```json
{
  "type": "https://atlantech.io/errors/server-error",
  "title": "Server error",
  "status": 500,
  "code": "SERVER_ERROR",
  "message_key": "errors.server_error",
  "detail": "Something went wrong on our side. Try again; if the problem continues, contact support."
}
```

### 503

```json
{
  "type": "https://atlantech.io/errors/service-unavailable",
  "title": "Service unavailable",
  "status": 503,
  "code": "SERVICE_UNAVAILABLE",
  "message_key": "errors.service_unavailable",
  "detail": "The service is temporarily unavailable. Try again in a few minutes."
}
```

## Change log

| Version | Date | Change |
| --- | --- | --- |
| v1.0 | 2026-10-30 | First version, written to match the code on `develop` (P1-A2, P1-A4, P1-C1) |
