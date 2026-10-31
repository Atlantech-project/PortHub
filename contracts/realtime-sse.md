# CT-05 · Web SSE events

| | |
| --- | --- |
| Version | v1.0 |
| Status | Approved |
| Approved by | Marwan (Backend lead), 2026-10-31, without team review |
| Owner | Backend Team |
| Reviewers | Frontend Team |
| Built by | P3-I4 (endpoint) · P5-N1 (notifications) |
| Decisions | DEC-05 · DEC-11 |
| Rules | [`api-conventions.md`](api-conventions.md) |

## 1. The stream

`GET /api/v1/events` returns `text/event-stream`. It uses the web session cookie, like every other web request.

- An event only says that something changed. The Frontend fetches the details over REST.
- Events are sent after the database commit, within 5 seconds (NFR-PERF-4, FR-DP-10).
- A refusal happens before the stream opens, as a normal CT-01 problem body: 401 `UNAUTHENTICATED`, 403 `ACCOUNT_DISABLED` or 403 `PASSWORD_CHANGE_REQUIRED`. Do not reconnect after one of these; follow CT-03.

## 2. Connection

- The server sends a comment line (`: ping`) at least every 30 seconds. A client that hears nothing for 60 seconds reconnects.
- The server may close a stream at any time, because each open stream holds a PHP worker (DEC-05). P3-I4 sets the limit. Clients must reconnect without showing an error.
- The server sends `retry: 3000`. Reconnects use the `Last-Event-ID` header, which `EventSource` sends by itself.

## 3. Catch-up

- Events are kept for **1 hour** in a short-lived Redis store.
- A valid `Last-Event-ID` inside that hour replays the events the user may see, in order.
- A value that is older, unknown or lost (for example after a Redis failure) gets one `RESYNC` event. The client then refetches what is on screen.
- `id` is an opaque string. Store it and never parse it.

```
id: 1762077734000-0
event: RESYNC
data: {"at":"2026-11-02T10:02:14.123456Z"}
```

## 4. Who receives what

Terminal-scoped users receive only events of their own terminal (P-18). Everything below is also filtered by that scope.

| Group | Roles |
| --- | --- |
| Office | `PORT_GM` · `PORT_STAFF` · `PILOTAGE_MANAGER` · `PILOTAGE_OFFICER` · `TUG_MANAGER` · `TUG_OFFICER` · `TERMINAL_ADMIN` · `TERMINAL_OFFICER` |
| Dispatch | `PORT_STAFF` · `PILOTAGE_MANAGER` · `PILOTAGE_OFFICER` · `TUG_MANAGER` · `TUG_OFFICER` |

`MARINE_PILOT`, `TUG_MASTER` and `TERMINAL_SUPERVISOR` use the tablet and CT-06, not this stream.

## 5. Events

Every `data` carries `entity`, `id` and `at`. The rest is listed per event.

| Event | Sent when | Receivers | `entity` | Extra fields |
| --- | --- | --- | --- | --- |
| `REQUEST_STATUS_CHANGED` | A request changes status | Office | `berthing_request` | `status` |
| `BAPLIE_PARSED` | A parse finishes (FR-BQ-09) | `PORT_STAFF` | `baplie_file` | `berthing_request_id` · `outcome` (`PARSED` · `QUARANTINED` · `REJECTED`) |
| `ENTRY_WINDOW_READY` | Part 1 finishes with an outcome (FR-EW-02) | `PORT_STAFF` | `berthing_request` | `outcome` · `entry_window_proposal_id` (may be null) |
| `RECOMMENDATION_READY` | A recommendation is written (FR-RC-09) | `PORT_STAFF` | `berthing_request` | `recommendation_id` · `status` |
| `PLAN_CONFIRMED` | A plan is confirmed | Office | `operational_plan` | `berthing_request_id` |
| `PLAN_CANCELLED` | A plan is cancelled (FR-PL-05) | Office | `operational_plan` | `berthing_request_id` |
| `ASSIGNMENT_CHANGED` | A crew assignment changes | Dispatch | `plan_component` | `operational_plan_id` · `component_type` |
| `NOTIFICATION_CREATED` | A notification row is sent on the WEB channel | That user | `notification` | `type` |
| `NOTIFICATION_ACKNOWLEDGED` | The executor acknowledges (P5-O3) | The assigning officer | `notification` | `plan_component_id` |
| `DEVIATION_DETECTED` | A `deviation_logs` row is written (FR-EX-03) | `PORT_STAFF` | `deviation` | `plan_component_id` |
| `REPLAN_PROPOSED` | A delay re-plan proposal is written (FR-EX-04) | `PORT_STAFF` | `berthing_request` | `recommendation_id` |
| `YARD_RECOMMENDATION_READY` | A yard result is stored (FR-YD-03) | `TERMINAL_OFFICER` | `terminal_recommendation` | `berthing_request_id` |
| `YARD_RECOMMENDATION_FAILED` | A yard run fails or times out (FR-YD-03) | `TERMINAL_OFFICER` | `terminal_recommendation` | `berthing_request_id` |
| `DRIFT_ALERT` | Part 3 finds drift | `PORT_GM` | `drift_measurement` | none |
| `RUN_FAILED` | A Part 1, Part 2 or BAPLIE run fails | `PORT_STAFF` | `berthing_request` | `run_type` (`PART1` · `PART2` · `BAPLIE`) · `error_category` |
| `RESYNC` | Section 3 | The reconnecting client | none | Only `at` |

A notification of a domain event produces both events: for example `RECOMMENDATION_READY` refreshes the page, and `NOTIFICATION_CREATED` with `type = RECOMMENDATION_READY` updates the list on P-19.

`type` is any value of `notification_logs.type`. `LICENSE_EXPIRY_WARNING` is deferred with the licence work (DEC-54).

A new event, field or receiver is a minor version. Clients must ignore an event name they do not know.

## 6. Example

```
id: 1762077734000-1
event: RECOMMENDATION_READY
data: {"entity":"berthing_request","id":1550,"recommendation_id":880,"status":"RECOMMENDATION_GENERATED","at":"2026-11-02T10:02:14.123456Z"}
```

## Change log

| Version | Date | Change |
| --- | --- | --- |
| v1.0 | 2026-10-31 | First version: receivers, event shapes, 1 hour catch-up and `RESYNC` |
