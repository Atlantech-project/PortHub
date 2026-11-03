# CT-25: Reference Data and Thresholds Contract Format

Between: QA Team -> AI Team
Owner: QA Team
Reviewers: AI Team, Backend Team
Status: Active Contract Draft

## 1. Scope and purpose

This contract establishes the reference data schemas, formats, and mandatory port topologies used for algorithm validation, solver benchmarking, simulation replays, and baseline evaluations.

Reference data provides deterministic baselines so test results can be verified across environments without dependency on external or live systems.

## 2. Mandatory CSV metadata columns

Every dataset defined under this contract must include two standardized metadata columns on every row:
1. `source`: string describing the provenance of the row (e.g., `"Damietta Port published berth list"`, `"Official Port Safety Manual"`, `"Synthetic test fixture"`).
2. `is_synthetic`: boolean string (`true` or `false`). Real-world operational or published values are marked `false`; simulated or boundary test data rows are marked `true`.

## 3. Mandatory port topologies

QA evaluates algorithms against two topologies:

### 3.1 Minimum-scale topology (`minimum-scale`)
- Structure: 1 terminal, 5 berths.
- Scale: 5 berths total (B01 to B05), depth 12.0 m to 14.5 m, length 250 m to 350 m.
- Purpose: Fast local unit testing, isolated constraint verification, and quick CI runs.
- File: `berths-minimum.csv`.

### 3.2 Reference-scale topology (`reference-scale` - Damietta Port)
- Structure: 8 terminals, 36 berths.
- Scale: 36 berths total across Container, General Cargo, Bulk, Ro-Ro, and Liquid terminals, handling approximately 26 vessels per day.
- Purpose: Full-scale solver performance evaluation, joint-solve scaling tests, and realistic operational replay scenarios.
- File: `berths-reference.csv`.

## 4. Dataset specifications

### 4.1 Berth datasets (`berths-minimum.csv`, `berths-reference.csv`)
Columns:
- `berth_code`: string, unique identifier within the port (e.g. `B01`, `DCT-01`).
- `terminal_code`: string, foreign key identifying owning terminal (e.g. `T1`, `DCT`).
- `length_m`: decimal, physical berth length in meters.
- `depth_m`: decimal, water depth at chart datum in meters.
- `max_loa_m`: decimal, maximum allowable vessel Length Overall in meters.
- `max_draft_m`: decimal, maximum allowable vessel draft in meters.
- `source`: string, provenance description.
- `is_synthetic`: boolean (`true` or `false`).

### 4.2 Safety thresholds dataset (`safety-thresholds.csv`)
Columns:
- `parameter`: string code (`WIND_SPEED_MAX_KTS`, `WIND_GUST_MAX_KTS`, `WAVE_HEIGHT_MAX_M`, `VISIBILITY_MIN_NM`, `UKC_MIN_M`).
- `operation_type`: string (`BERTHING`, `UNBERTHING`, `CANAL_TRANSIT`, `GENERAL`).
- `vessel_type`: string (`ALL`, `CONTAINER`, `TANKER`, `BULK`).
- `threshold_value`: decimal, numerical limit.
- `unit`: string (`KTS`, `M`, `NM`).
- `source`: string, provenance documentation.
- `is_synthetic`: boolean (`true` or `false`).
