# CT-07 · Mobile sync (Outbox)

| | |
| --- | --- |
| Version | v1.0 |
| Status | Draft: waiting for the Mobile Team to approve the event shape |
| Owner | Backend Team (endpoints) · Mobile Team (event shape) |
| Reviewers | Mobile Team · Backend Team |
| Built by | P5-O1 · P5-O2 · P5-O3 · P5-O4 · P5-O5 · P5-O8 |
| Decisions | DEC-39 · DEC-40 · DEC-44 |
| Rules | [`api-conventions.md`](api-conventions.md) |

## 1. Send events

`POST /api/v1/sync/events` takes up to **100** events in Outbox order. Send more in a later request.

```json
{
  "events": [
    {
      "client_event_id": "2c1f6a7e-1d0b-4c11-9a51-7f1e2b3c4d5e",
      "type": "STATUS_UPDATE",
      "payload": { "plan_component_id": 5012, "new_status": "STARTED" },
      "reported_at": "2026-11-02T11:40:00.000000Z",
      "client_sent_at": "2026-11-02T11:52:10.000000Z",
      "sync_source": "TABLET"
    }
  ]
}
```

| Field | Rule |
| --- | --- |
| `client_event_id` | UUID v4, made once on the device. A re-send keeps it. This replaces `Idempotency-Key` (CT-01 section 4) |
| `type` | `STATUS_UPDATE` · `ACKNOWLEDGE` |
| `reported_at` | When it happened on the ground. CT-01 input format |
| `client_sent_at` | Device clock when this request was sent. CT-01 input format |
| `sync_source` | `MOBILE` · `TABLET`, the device class |

## 2. Event types

| Type | Payload | Who | Effect |
| --- | --- | --- | --- |
| `STATUS_UPDATE` | `{ plan_component_id, new_status }` | The component's assigned user | Writes `actual_status_updates` |
| `ACKNOWLEDGE` | `{ notification_id }` | The notification's user | Marks it `ACKNOWLEDGED` and cancels its re-sends. The plan state does not change (FR-DP-06) |

**`new_status`** is `STARTED` or `DONE`, for pilot, tug and terminal components (DEC-39). P-55 labels them In progress and Executed. The order is one way: `ASSIGNED` → `STARTED` → `DONE`, with no skipping and no return (FR-EX-01).

## 3. Results

200 returns one result per event, in the same order. A rejected event does not stop the ones after it.

```json
{
  "results": [
    { "client_event_id": "2c1f6a7e-…", "result": "APPLIED" },
    { "client_event_id": "8d9e…", "result": "REJECTED", "reason_code": "PLAN_CANCELLED" },
    {
      "client_event_id": "a41b…",
      "result": "REJECTED",
      "reason_code": "ILLEGAL_TRANSITION",
      "current": { "status": "DONE", "version": "2026-11-02T11:45:00.123456Z" }
    }
  ]
}
```

| `result` | Meaning | Outbox state |
| --- | --- | --- |
| `APPLIED` | Done now | `DONE` |
| `DUPLICATE` | Done before. For `STATUS_UPDATE`: this `client_event_id` exists. For `ACKNOWLEDGE`: the notification is already `ACKNOWLEDGED` | `DONE` |
| `REJECTED` | Refused with `reason_code`, and logged (FR-EX-06) | `REJECTED`, reason shown, no re-send |

| `reason_code` | Meaning |
| --- | --- |
| `PLAN_CANCELLED` | The plan was cancelled |
| `ILLEGAL_TRANSITION` | The status breaks the order in section 2. `current` holds the stored task state |
| `NOT_ASSIGNED` | The task or notification is not this user's |
| `NOT_FOUND` | The record does not exist |
| `INVALID_EVENT` | The event's type, payload or time is not valid |

A new `reason_code` is a minor version. Show an unknown one as a general rejection.

**Clock skew:** an event whose `received_at` minus `client_sent_at` is more than 5 minutes is applied and flagged `clock_skew_suspect`. Staff see the flag only, with no review note (DEC-44).

### Refusing the whole request

No event is processed, and the app keeps them all.

| Status | Code | App |
| --- | --- | --- |
| 401 | `UNAUTHENTICATED` | Ask for sign-in. Send only if the same user signs back in (FR-AC-07) |
| 403 | `ACCOUNT_DISABLED` · `PASSWORD_CHANGE_REQUIRED` | Stop the sync cycle and follow CT-04 |
| 422 | `VALIDATION_FAILED` | The request is malformed, or holds more than 100 events |
| 426 | `APP_UPDATE_REQUIRED` | Pause sync until the app is updated (FR-MB-08) |

**423:** both event types are allowed in `READ_ONLY` (FR-MB-05), and v1.0 has no creation events, so this endpoint does not return 423. The rule returns with the licence work (DEC-54).

## 4. Fetch changes

`GET /api/v1/sync/changes?since=<sync_token>` returns what changed for this user.

- Leave out `since` on first use, to get all active tasks and notifications.
- `sync_token` is an opaque string. Store the new one only after saving the response. A token this server cannot read returns 422 `VALIDATION_FAILED`: call again without `since`.
- The app calls this after a sync cycle and after every WebSocket reconnect (CT-06).

```json
{
  "tasks": [
    {
      "id": 5012,
      "version": "2026-11-02T11:40:01.123456Z",
      "component_type": "PILOT",
      "status": "STARTED",
      "planned_start": "2026-11-03T06:00:00.000000Z",
      "planned_end": "2026-11-03T18:30:00.000000Z",
      "plan_status": "CONFIRMED",
      "vessel": { "id": 310, "name": "MSC Aurora", "imo_number": "9839430" },
      "berth": { "id": 12, "code": "B12" },
      "terminal": { "id": 3, "name": "DCT" },
      "tugboats": [ { "id": 7, "name": "Damietta 2" } ],
      "pilot": { "id": 4, "name": "Marine Pilot" }
    }
  ],
  "notifications": [
    {
      "id": 9120,
      "type": "PLAN_ASSIGNMENT",
      "related_entity": { "type": "PLAN_COMPONENT", "id": 5012 },
      "status": "SENT",
      "sent_at": "2026-11-02T09:00:00.000000Z",
      "acknowledged_at": null
    }
  ],
  "removed": [ { "entity": "plan_component", "id": 5003 } ],
  "sync_token": "tok_131"
}
```

- `status` is `ASSIGNED`, `STARTED` or `DONE`. The server reads it from the assignment and the latest `actual_status_updates` row.
- `berth`, `terminal`, `pilot` are null and `tugboats` is empty where they do not apply.
- `removed` lists tasks that left this user's list. The app deletes them from its cache.

## Change log

| Version | Date | Change |
| --- | --- | --- |
| v1.0 | 2026-10-31 | First version: event rules, results, reason codes, 100 event limit and the shape of `tasks` and `notifications` |
