# CT-07 · Mobile sync (Outbox)

| | |
| --- | --- |
| Version | v1.1 |
| Status | Approved |
| Approved by | Marwan (Backend lead) and Farouk (Mobile Team), 2026-10-31, on PortHub PR #27 |
| Owner | Backend Team (endpoints) · Mobile Team (event shape) |
| Reviewers | Mobile Team · Backend Team |
| Built by | P5-O1 · P5-O2 · P5-O3 · P5-O4 · P5-O5 · P5-O8 |
| Decisions | DEC-39 · DEC-40 · DEC-44 · DEC-58 |
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
| `client_event_id` | UUID v4, made once on the device. A re-send keeps it. This replaces `Idempotency-Key` (CT-01 section 4). It has no 24-hour limit: an applied status update keeps it for as long as its `actual_status_updates` row exists, so an event may wait offline for days |
| `type` | `STATUS_UPDATE` · `ACKNOWLEDGE` |
| `reported_at` | When it happened on the ground. CT-01 input format |
| `client_sent_at` | Device clock when this request was sent. CT-01 input format |
| `sync_source` | `MOBILE` · `TABLET`, the device class. The app always sends it: `TABLET` when the shortest display side is 600 dp or more, otherwise `MOBILE` |

## 2. Event types

| Type | Payload | Who | Effect |
| --- | --- | --- | --- |
| `STATUS_UPDATE` | `{ plan_component_id, new_status }` | The component's assigned user | Writes `actual_status_updates` |
| `ACKNOWLEDGE` | `{ notification_id }` | The notification's user | Marks it `ACKNOWLEDGED` and cancels its re-sends. The plan state does not change (FR-DP-06) |

**Acknowledging a re-sent task.** Each re-send (T+10, T+20) is a new notification row. Send any `notification_id` of the task, normally the newest. All `SENT` rows with the same user, related entity and type become `ACKNOWLEDGED` with the same `acknowledged_at`, and come back in the next `GET /api/v1/sync/changes`. `FAILED` rows stay `FAILED`. The officer gets one `NOTIFICATION_ACKNOWLEDGED` (CT-05). Notification status is `SENT` · `FAILED` · `ACKNOWLEDGED`; an escalation is a row of type `ACK_ESCALATION`, not a status.

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
| `INVALID_EVENT` | The event's type, payload or time is not valid. Only this event is refused, and the ones after it still run |

A new `reason_code` is a minor version. Show an unknown one as a general rejection.

**Clock skew:** an event whose `received_at` minus `client_sent_at` is more than 5 minutes is applied and flagged `clock_skew_suspect`. Staff see the flag only, with no review note (DEC-44).

### Refusing the whole request

No event is processed, and the app keeps them all.

| Status | Code | App |
| --- | --- | --- |
| 401 | `UNAUTHENTICATED` | Ask for sign-in. Send only if the same user signs back in (FR-AC-07) |
| 403 | `ACCOUNT_DISABLED` · `PASSWORD_CHANGE_REQUIRED` | Stop the sync cycle and follow CT-04 |
| 422 | `VALIDATION_FAILED` | The request itself is malformed: `events` is not a list, holds more than 100 events, or an event has no valid `client_event_id` to report against |
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
      "system_label": null,
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
- `component_type` is `PILOT`, `TUG` or `TERMINAL_OPS`. `plan_status` is `CONFIRMED`, `CANCELLED` or `COMPLETED`.
- `berth`, `terminal`, `pilot` are null and `tugboats` is empty where they do not apply.
- `removed` lists tasks that left this user's list. The app deletes them from its cache.

### `system_label`

The server sets this field for the labels on P-55 (DEC-58). It is null otherwise.

| Value | Set when | Cleared when | Task actions |
| --- | --- | --- | --- |
| `UPDATED` | The task's planned time or resources change after it was assigned to this user | This user sends `ACKNOWLEDGE` or `STATUS_UPDATE` for the task | Allowed |
| `OVERRIDDEN` | The task stops being this user's, because an officer reassigned it or a confirmed re-plan moved it | The task moves to `removed` after 24 hours | None: `STATUS_UPDATE` gets `NOT_ASSIGNED` |
| `CANCELLED` | The plan is cancelled | The task moves to `removed` after 24 hours | None: `STATUS_UPDATE` gets `PLAN_CANCELLED` |

An `OVERRIDDEN` or `CANCELLED` task stays in `tasks` during those 24 hours, so the user sees why it stopped. The label belongs to the user, not to the device. P5-O1 decides how it is stored and adds any table or column to CT-17.

## Change log

| Version | Date | Change |
| --- | --- | --- |
| v1.1 | 2026-10-31 | Mobile Team review: acknowledgement across re-sends, `system_label`, the values of `component_type` and `plan_status`, and the limits of `INVALID_EVENT` and 422 (DEC-58) |
| v1.0 | 2026-10-31 | First version: event rules, results, reason codes, 100 event limit and the shape of `tasks` and `notifications` |
