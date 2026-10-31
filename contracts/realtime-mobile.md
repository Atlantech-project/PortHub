# CT-06 · Mobile WebSocket events (Reverb)

| | |
| --- | --- |
| Version | v1.0 |
| Status | Approved |
| Approved by | Marwan (Backend lead), 2026-10-31, without team review |
| Owner | Backend Team |
| Reviewers | Mobile Team |
| Built by | P5-N2 (channel) · P5-N1 (notifications) |
| Rules | [`api-conventions.md`](api-conventions.md) · [`sync-events.md`](sync-events.md) |

## 1. Channel

- One private channel per user: `private-user.{user_id}`.
- The app authorises the channel with `POST /api/v1/broadcasting/auth`, sending `Authorization: Bearer <token>` with the Pusher fields `socket_id` and `channel_name`.
- 200 returns the signature that Reverb expects. 403 `FORBIDDEN` means the channel belongs to another user, or the device is revoked. 401 means the token ended: follow FR-AC-07.
- This route does not use `Idempotency-Key` (CT-01 section 4).

## 2. Events

An event says that something changed. The app fetches the content with `GET /api/v1/sync/changes` (CT-07).

| `type` | Sent when | `entity` |
| --- | --- | --- |
| `TASK_UPDATED` | A task of this user is assigned, changed, removed or cancelled | `plan_component` |
| `NOTIFICATION_CREATED` | A notification row is sent to this user on the MOBILE channel | `notification` |

```json
{ "event_id": "e-77-000231", "type": "TASK_UPDATED", "entity": "plan_component", "entity_id": 5012 }
```

A notification's own type is read over REST. These types are sent on the MOBILE channel:

| Notification `type` | Receivers |
| --- | --- |
| `PLAN_ASSIGNMENT`, including the T+10 and T+20 re-sends | The assigned executor |
| `PRE_EXECUTION_REMINDER` | The assigned executor |
| `PLAN_CANCELLED` | The executors of that plan |

Each re-send is a new notification row and a new event. The other notification types are web only (CT-05).

## 3. App rules

- **Duplicates:** ignore any `event_id` already seen. `event_id` is an opaque string.
- **After every reconnect:** call `GET /api/v1/sync/changes`, because events are not replayed on this channel.
- **Delivery is not acknowledgement:** only the `ACKNOWLEDGE` event of CT-07 acknowledges a notification.
- **Unknown type:** ignore the event, then fetch changes as usual.

Push wake-ups (FCM) are post-MVP and not part of this contract.

## Change log

| Version | Date | Change |
| --- | --- | --- |
| v1.0 | 2026-10-31 | First version: channel authorisation, two event types and the notification types on the MOBILE channel |
