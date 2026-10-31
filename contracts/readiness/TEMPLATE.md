# FT-xx <feature title> — API readiness pack

| | |
| --- | --- |
| FRR | <Sprint n FRR, date> |
| Built from | `develop` at `<commit>` · <date> |
| Backend tasks | <IDs merged> · not merged: <IDs or "none"> |

## Endpoints (merged to develop)

| Method and path | Roles | Purpose | Task |
| --- | --- | --- | --- |

## OpenAPI diff

- <PR links that changed `contracts/openapi/port-api.yaml` for this feature>

## Examples

### <METHOD /api/v1/...> → <status>

```json
// request
```

```json
// response
```

(one block per endpoint and status it can return; errors in the CT-01 shape with `code` and `message_key`)

## Seed data on the dev server

- <what exists: counts per status, files, users per role>

## Events

| Event | Channel (SSE CT-05 / WebSocket CT-06) | When | Payload |
| --- | --- | --- | --- |

## Behind it

| Endpoint | Mock worker queue | Default scenario | How to choose another |
| --- | --- | --- | --- |

## Known gaps

- <unmerged task, draft contract, open decision, missing seed> · or "none"

---

## Checklist before sharing

- [ ] Every endpoint is on `develop` and on the dev server.
- [ ] Every status code listed has an example; error bodies match CT-01 and the error catalogue.
- [ ] Event names match CT-05 / CT-06 exactly.
- [ ] Every AI-triggering endpoint names its mock scenario (CT-19).
- [ ] `contract-checker` found no Blocker, or the mismatch is listed under Known gaps.
- [ ] The lead approved the pack.
