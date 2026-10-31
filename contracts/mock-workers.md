# CT-19 · Mock worker behaviour

| | |
| --- | --- |
| Version | v1.0 |
| Status | Approved |
| Approved by | Marwan (Backend lead), 2026-10-31, without team review |
| Owner | Backend Team |
| Reviewers | Frontend Team · Mobile Team, critical changes only |
| Used by | QA Team, which tests with it and does not review it |
| Built by | P3-I6, replaced worker by worker in P6-R1 |
| Rules | [CT-08 to CT-15](ATLANTECH_Contracts.md) |

## 1. What a mock does

- It consumes the same queue, writes the same rows and sends the same C-06 as the real worker, so the Frontend cannot tell them apart.
- It keeps the write ownership of CT-15, and returns its result within a few seconds.
- Mocks run outside `production` only. In `production` the mock command refuses to start.

## 2. Choosing a scenario

The first match wins:

1. **Vessel tag:** `[MOCK:<SCENARIO>]` in the vessel name, for example `MSC Aurora [MOCK:NO_FEASIBLE_WINDOW]`. It applies to that vessel's jobs on every queue where the name is a valid scenario. Other queues go to rule 2.
2. **Port setting:** the `mock_scenario` key in `port_settings`, with `value_type = JSON` and one scenario per queue:

   ```json
   { "queue:part1": "WINDOWS_FOUND", "queue:part2": "FIFO_FALLBACK" }
   ```

3. **Default:** the first scenario of the queue in section 3.

An unknown scenario name is logged and treated as if it were absent. The key exists only where a tester sets it, so it is not a CT-18 seed key.

## 3. Scenarios

Each row is one C-06 result (CT-14).

| Queue | Scenario | C-06 `status` | C-06 `outcome` | What the mock writes |
| --- | --- | --- | --- | --- |
| `queue:part1` | `WINDOWS_FOUND` | DONE | `WINDOWS_FOUND` | Run, proposal, windows and blocked periods |
| | `NO_FEASIBLE_WINDOW` | DONE | `NO_FEASIBLE_WINDOW` | Run, and the proposal only if DEC-07 says so |
| | `ENV_DATA_UNAVAILABLE` | DONE | `ENV_DATA_UNAVAILABLE` | Run |
| | `FAILED` | FAILED | `null`, with `INTERNAL_ERROR` | Run |
| `queue:part2` | `SOLVED` | DONE | `SOLVED` | Run, recommendations and options for all requests |
| | `PARTIALLY_SOLVED` | DONE | `PARTIALLY_SOLVED` | The same for the first request; the others get `binding_constraints` |
| | `FIFO_FALLBACK` | DONE | `FIFO_FALLBACK`, with `TIMEOUT` | Run and a `source = FIFO` recommendation |
| | `NO_FEASIBLE_PLAN` | DONE | `NO_FEASIBLE_PLAN` | Run and `binding_constraints` |
| | `GENERATION_FAILED` | FAILED | `GENERATION_FAILED`, with `INTERNAL_ERROR` | Run |
| `queue:yard` | `YARD_REC_GENERATED` | DONE | `YARD_REC_GENERATED` | Run, terminal recommendation and placements |
| | `GENERATION_FAILED` | FAILED | `GENERATION_FAILED`, with `INFEASIBLE` | Run and the failure reason |
| `queue:edi` | `PARSED` | DONE | `PARSED` | Run and the manifest rows |
| | `QUARANTINED` | DONE | `QUARANTINED` | Run and `baplie_parse_issues` |
| | `REJECTED` | DONE | `REJECTED` | Run and an ERROR issue on segment UNH |
| | `FAILED` | FAILED | `null`, with `INTERNAL_ERROR` | Run |
| `queue:validate` | `VALID` | DONE | `VALID` | No rows; `validation_result` in C-06 |
| | `VIOLATIONS` | DONE | `VIOLATIONS` | No rows; broken constraints in `validation_result` |
| | `NO_RESPONSE` | None | None | Nothing, so the Backend's "validation unavailable" case runs (CT-13) |

**Drift:** Part 3 has no queue. To test `DRIFT_ALERT`, seed a `drift_measurements` row above its threshold; the poller handles it (CT-14).

## Change log

| Version | Date | Change |
| --- | --- | --- |
| v1.0 | 2026-10-31 | First version: scenario precedence and every outcome of CT-10 to CT-13 |
