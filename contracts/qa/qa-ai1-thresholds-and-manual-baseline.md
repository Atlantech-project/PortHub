# QA-AI1: Thresholds Register Inputs (DEC-30) and Manual-Planning Baseline Procedure (DEC-33)

Owner: QA Team
Reviewers: AI Team, Leads Council, Harbor Master / Domain Experts
Status: Draft Proposal (Sprint 1 QA Deliverable)
Reference Decisions: DEC-30 (Thresholds register), DEC-33 (Manual-planning baseline)

## Overview

This deliverable establishes the formal QA inputs for two critical open decisions in the ATLANTECH architecture:
- **Part 1 (DEC-30):** Draft Thresholds Register Inputs defining the quantitative parameters and boundaries for AI workers, separating agreed contractual numbers from proposed values awaiting domain expert sign-off.
- **Part 2 (DEC-33):** The Manual-Planning Baseline Procedure defining the deterministic FIFO and rule-based heuristic allocation workflow and evaluation protocol to benchmark AI Part 2 in Sprint 7.

---

# Part 1. Draft Thresholds Register Inputs (DEC-30)

Per decision DEC-30, ATLANTECH requires a centralized, authoritative numeric register governing worker constraints, timeouts, model health, and physical thresholds.

### 1.1 Status definitions
- **Agreed:** Sourced from approved contracts (CT-08, CT-10, CT-12, CT-13, CT-18) or closed architectural decisions.
- **Proposed:** Draft figures prepared by QA and AI teams based on preliminary maritime standards, pending formal sign-off by the Harbor Master / Marine Safety Officer or domain contact.

### 1.2 Quantitative thresholds register table

| TR ID | Parameter / Threshold | Category | Value | Status | Source / Basis | Needed By |
| --- | --- | --- | --- | --- | --- | --- |
| TR-01 | `drift_psi_threshold` | Model Health | 0.25 (PSI >= 0.25 flags significant population drift) | **Proposed** | Standard statistical process control; awaiting AI-072 | AI-072, CT-18 |
| TR-02 | `drift_mae_threshold` | Model Health | 20.0% relative increase in rolling MAE | **Proposed** | QA baseline recommendation; awaiting AI-072 | AI-072, CT-18 |
| TR-03 | Rolling MAE window length | Model Health | 30 days (minimum 50 vessel calls) | **Proposed** | Architecture Section 9.1; awaiting AI-072 | AI-072 |
| TR-04 | Model data sufficiency threshold | Model Training | 9,500 historical port calls (approx. 1 year of data) | **Proposed** | Master Context Section 4; awaiting AI-024 | AI-024 |
| TR-05 | Model promotion margin (M2, M3, M4) | Governance | 5.0% MAE improvement over Champion | **Proposed** | Architecture Section 10; awaiting AI-101..AI-103 | AI-101..103 |
| TR-06 | C3 Champion/Challenger guard | Governance | Non-inferiority on both MAE and operator override rate | Agreed | Architecture Section 9.3, UML AD-16 | AI-104 |
| TR-07 | Tide prediction error tolerance | Physical Safety | +/- 15 cm against published Admiralty tide tables | **Proposed** | DEC-27 reference tolerance; awaiting Marine Safety sign-off | AI-021 |
| TR-08 | BAPLIE size-class performance | Parser | Excluded from MVP | Agreed | Out of MVP scope per DEC-17 and CT-12 v1.0 | None |
| TR-09 | AI test coverage gate | CI/CD | 80.0% line coverage (`fail_under = 80`) | **Proposed** | AI-016 task specification; awaiting team approval | AI-016 |
| TR-10a | Minimum Under-Keel Clearance (UKC) | Physical Safety | 1.0 m (Container/General Cargo), 1.5 m (Tanker) | **Proposed** | Port Safety Baseline; awaiting Harbor Master sign-off | AI-044, CT-18 |
| TR-10b | Maximum operating wind speed | Physical Safety | 25 knots (berthing), 28 knots (unberthing) | **Proposed** | Standard port operating limits; awaiting Safety Officer sign-off | AI-044, CT-18 |
| TR-10c | Maximum operating wind gust | Physical Safety | 32 knots (berthing), 35 knots (unberthing) | **Proposed** | Standard port operating limits; awaiting Safety Officer sign-off | AI-044, CT-18 |
| TR-10d | Maximum wave height | Physical Safety | 1.5 m significant wave height (Hs) | **Proposed** | Harbor basin wave limit; awaiting Safety Officer sign-off | AI-044, CT-18 |
| TR-10e | Minimum visibility | Physical Safety | 1.0 nautical mile (NM) | **Proposed** | Navigation safety rule; awaiting Safety Officer sign-off | AI-044, CT-18 |
| TR-11 | Window accuracy definition (C1) | Evaluation | Actual berthing start within +/- 30 min of window | **Proposed** | AI-071 operational metric | AI-071 |
| TR-12 | `part1_stored_data_max_age_hours` | Data Freshness | 48 hours | Agreed | CT-18 v1.0, DEC-12 (Closed), Architecture Section 7.2 | AI-025, AI-041 |
| TR-13a | `solver_time_limit_seconds` (CP-SAT) | Solver | 10 seconds (configurable default: min 1 s, max 120 s) | Agreed | CT-18 v1.0, CT-10 | AI-055 |
| TR-13b | Total Part 2 pipeline latency | Solver | <= 12 seconds end-to-end | **Proposed** | Derived from TR-13a + queue overhead; awaiting AI-061 | AI-061 |
| TR-14 | Concurrent parallel solve requests | Scalability | Up to 4 simultaneous solves without queue degradation | **Proposed** | NFR capacity target; awaiting AI-061 | AI-061 |
| TR-15 | `solver_option_equivalence_pct` | Optimization | 10.0% of Option 1 objective score | Agreed | DEC-23 (Closed), CT-18 v1.0, CT-10 | AI-055 |
| TR-16a | `validation_timeout_seconds` | Inter-process | 15 seconds | Agreed | CT-13, CT-18 v1.0 | AI-060 |
| TR-16b | `validation_result_ttl_seconds` | Cache | 600 seconds (10 minutes) | Agreed | CT-18 v1.0 | AI-067 |
| TR-17 | `part1_max_retries` | Fault Tolerance | 3 attempts | Agreed | DEC-04 (Closed), CT-08 v1.0, CT-18 v1.0 | AI-048 |
| TR-18 | Worker down alert threshold | Health | 120 seconds (2 minutes of silence on Redis heartbeat) | Agreed | CT-16, DEC-10 (Closed) | Backend, AI |
| TR-19 | Reference daily vessel traffic scale | Topology | Approx. 26 vessels per day (Damietta reference port) | Agreed | Master Context Section 4; reference scale for AI-084 | AI-084 |

---

# Part 2. Manual-Planning Baseline Procedure (DEC-33)

To validate the real-world value of AI Part 2 berthing recommendations, the project must establish a rigorous, repeatable baseline representing current manual dispatch operations. Per DEC-33 (Option 1), QA defines this baseline procedure to be executed against replay scenarios in Sprint 7 (AI-084).

### 2.1 Replay scenario construction
1. **Scenario Source:** Scenarios are sampled from the reference-scale dataset (`berths-reference.csv`) and historical port call records (or validated synthetic traffic generators).
2. **Scenario Horizon:** 7-day rolling window with an average load of 26 vessels per day (total ~182 vessel calls per scenario).
3. **Data Integrity:** All inputs carry explicit `source` and `is_synthetic` flags.
4. **Variations:** Scenarios must include:
   - Nominal traffic flow (scheduled arrivals evenly distributed).
   - Arrival burst (clustering of 6 container vessels within 3 hours).
   - Weather disruption (36-hour storm window exceeding wind/wave limits).
   - Terminal bottleneck (2 berths temporarily closed for maintenance).

### 2.2 Deterministic FIFO rule-based manual allocation algorithm
The manual allocation engine executes a strict, non-preemptive heuristic simulating a port dispatcher:

```
Step 1: Ingestion & Ordering
  - Collect all pending berthing requests within the scheduling horizon.
  - Sort requests in ascending order by Estimated Time of Arrival (ETA).
  - Break ties using request creation timestamp (earliest submitted first).

Step 2: Candidate Berth Filtering
  - For each vessel in queue order:
    a. Check Physical Constraints:
       - Berth length >= Vessel LOA + safety margin (minimum 15 m).
       - Berth water depth at lowest predicted astronomical tide during stay >= Vessel draft + minimum UKC (1.0 m).
    b. Check Operational Constraints:
       - Terminal cargo type must match vessel cargo (e.g. Container -> DCT).
       - Berth must possess required equipment (e.g. Quay Cranes for container discharge).
    c. Filter out all non-compliant berths.

Step 3: Earliest Feasible Slot Allocation
  - Evaluate the schedule of compliant berths starting from Vessel ETA.
  - Identify the earliest contiguous idle interval whose duration >= estimated port stay:
      Duration = (Total Move Count / Cranes Assigned / Crane Productivity) + Mooring Overhead.
  - If multiple candidate berths are free at the same time:
      Select berth minimizing crane travel distance or preferential terminal berth.
  - Lock in berth meter span and time interval.

Step 4: Resource Allocation (Tugs, Pilots, Mooring)
  - Assign pilot at berthing start (arrival) and unberthing end (departure).
  - Assign tugs based on vessel LOA:
      - LOA < 150 m: 1 tug
      - 150 m <= LOA < 250 m: 2 tugs
      - LOA >= 250 m: 3 tugs or 4 tugs
  - If tug/pilot capacity is exhausted at the chosen slot:
      Shift the berthing window forward to the earliest slot with available marine resources.

Step 5: Deviation and Delay Propagation
  - Never displace or reschedule an already allocated vessel to accommodate a newly arriving vessel (pure non-preemptive queue).
  - If a vessel cannot be berthed upon arrival, record waiting time at anchorage.
```

### 2.3 Sprint 7 evaluation and comparison protocol (AI-084)
In Sprint 7, each replay scenario runs through three distinct engines under identical environmental conditions:
1. **Engine A: AI Part 2 Recommendation Solver (CP-SAT Multi-Objective Optimization).**
2. **Engine B: Deterministic Manual Baseline (the FIFO heuristic above).**
3. **Engine C: Human Domain Expert Plan (interactive dispatch by harbor operations staff).**

### 2.4 Evaluation metrics (The Six Master Context Indicators)
The output schedules are compared across six standardized metrics defined in Master Context Section 4 and Proposal Section 12:

1. **Safety and Invariant Compliance (I-1 to I-15):**
   - Total number of physical overlaps, UKC violations, or weather limit breeches (Target: exactly 0 for both AI and Manual).
2. **Anchor Waiting Time:**
   - Cumulative waiting hours at outer anchorage before berthing commences.
   - Target: AI achieves >= 15% reduction in waiting time relative to Manual Baseline.
3. **Berth & Resource Utilization:**
   - Overall berth occupancy rate (%) and quay crane operating efficiency (moves per hour).
   - Target: AI demonstrates higher utilization without creating bottleneck congestion.
4. **Estimated Operational Delay Cost:**
   - Calculated demurrage and vessel idling costs based on published port tariff structures.
   - Target: Measurable financial saving from AI allocation over FIFO.
5. **Downstream Yard Impact:**
   - Yard truck travel distances and predicted container re-handling moves based on berth-to-stack distance.
6. **Plan Stability and Operator Overrides:**
   - Degree of deviation required by human operators to accept the plan into execution.

### 2.5 Deliverable sign-off workflow
- **Sprint 1 (Now):** QA prepares and publishes this procedure draft in `PortHub/contracts/qa/`.
- **Sprint 2:** Marine Safety Officer reviews and signs off on Proposed thresholds in Part 1.
- **Sprint 6:** Replay datasets and test harnesses configured.
- **Sprint 7:** QA-E2E and AI-084 execute the comparative benchmark and publish the official evaluation report.
