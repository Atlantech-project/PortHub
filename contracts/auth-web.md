# CT-03 · Web sign-in and session

| | |
| --- | --- |
| Version | v1.0 |
| Owner | Backend Team |
| Reviewers | Frontend Team |
| Endpoints | Auth section of [`openapi/port-api.yaml`](openapi/port-api.yaml) |
| Rules | [`api-conventions.md`](api-conventions.md) |

## Flow

1. `GET /sanctum/csrf-cookie`. Send the `XSRF-TOKEN` cookie's value as `X-XSRF-TOKEN` on every write.
2. `POST /api/v1/auth/login` with `username` and password (DEC-35; users have no email).
3. If `must_change_password` is `true`: `POST /api/v1/auth/change-password`.
4. After a page reload: `GET /api/v1/auth/me` tells who is signed in.
5. `POST /api/v1/auth/logout` ends the session: 204, and the next signed-in request is 401.

Sign-in and password change both give a new session id. A stale CSRF token returns 419 `SESSION_EXPIRED`: fetch a new cookie and retry.

## Sign-in

```json
// POST /api/v1/auth/login
{ "username": "staff.ahmed", "password": "••••••••" }

// 200
{
  "id": 41,
  "name": "Port Staff",
  "role": "PORT_STAFF",
  "terminal_ids": [],
  "must_change_password": false
}
```

A wrong username and a wrong password get the same 401. Failed attempts are throttled with 429 and `Retry-After`.

## Password change

While `must_change_password` is `true`, every signed-in route answers 403 `PASSWORD_CHANGE_REQUIRED`, except `auth/me`, `auth/change-password` and `auth/logout`.

```json
// POST /api/v1/auth/change-password
{
  "current_password": "••••••••",
  "new_password": "••••••••",
  "new_password_confirmation": "••••••••"
}

// 200: the profile, with the flag cleared
{
  "id": 41,
  "name": "Port Staff",
  "role": "PORT_STAFF",
  "terminal_ids": [],
  "must_change_password": false
}
```

The new password has at least 8 characters with letters and numbers, and differs from the current one. A refused value returns 422 `VALIDATION_FAILED`, with keys such as `validation.current_password`, `validation.confirmed`, `validation.different` and `validation.password` under `errors`. The route allows 5 requests per minute per user, then 429.

## Deactivated user

A deactivated user cannot sign in, and on the next request of an open session gets 403 `ACCOUNT_DISABLED` and is signed out. The request after that is 401.

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

## Change log

| Version | Date | Change |
| --- | --- | --- |
| v1.0 | 2026-10-30 | First version, matching the code (P1-C1, P1-C2, web part of P1-C4) |
