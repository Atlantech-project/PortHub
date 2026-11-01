# CT-24: BAPLIE Test Corpus Format and Specifications

Between: QA Team -> AI Team (EDI Parser)
Owner: QA Team
Reviewers: AI Team, Leads Council
Status: Active Contract Draft

## 1. Scope and purpose

This contract establishes the standardized test corpus for verifying the ATLANTECH BAPLIE/EDI parser (worker `queue:edi`, contract CT-12). The corpus validates parser compliance, schema adherence, quarantine isolation, error reporting, and character-level EDIFACT parsing without executing live database mutations on operational systems.

## 2. Supported BAPLIE versions

Per contract CT-12 v1.0, the parser supports the following SMDG BAPLIE versions:
1. **SMDG BAPLIE 2.2.1 (VGM):** Based on UN/EDIFACT directory D.95B. Identified by segment `UNH+<msg_ref>+BAPLIE:D:95B:UN:SMDG22`. Files of the D.95B family (2.1, 2.1.1, 2.2) are parsed with 2.2.1 rules.
2. **SMDG BAPLIE 3.1.1 (VGM):** Based on UN/EDIFACT directory D.13B. Identified by segment `UNH+<msg_ref>+BAPLIE:D:13B:UN:SMDG31`.

Any other version, directory (such as BAPLIE 1.5, 2.0, or 2.3), other message types (such as COPRAR, MOVINS), or non-EDIFACT files result in outcome `REJECTED` and `parse_status = FAILED` with an issue on segment `UNH`.

## 3. Exclusion of performance test files (DEC-17)

Per DEC-17 and CT-12 v1.0, requirement NFR-PERF-2 (parser execution time across arbitrary size tiers) was formally removed from the MVP by Leads Council decision on 2026-10-27. The test corpus does not contain performance size-class benchmarks; all test cases focus on functional correctness, validation rules, quarantine logic, and syntax handling.

## 4. Companion file structure

Every test scenario in this corpus consists of a pair of files with matching base names:
- `<case-name>.edi`: Raw EDI message content using standard UN/EDIFACT delimiters (`'` for segment terminator, `+` for data element separator, `:` for component separator, `?` for release character).
- `<case-name>.expected.json`: Test oracle file containing expected results and validations.

### 4.1 Schema of `<case-name>.expected.json`

```json
{
  "file": "<case-name>.edi",
  "expected_outcome": "PARSED",
  "expected_parse_status": "PARSED",
  "vessel_imo": "9811000",
  "containers": 212,
  "issues": [
    {
      "severity": "WARNING",
      "code": "CHECK_DIGIT_MISMATCH",
      "segment_ref": "EQD+CN+MSCU1234567"
    }
  ]
}
```

Fields:
- `file`: string, base file name including `.edi`.
- `expected_outcome`: string, must be one of `PARSED`, `QUARANTINED`, or `REJECTED`.
- `expected_parse_status`: string, must be one of `PARSED`, `QUARANTINED`, or `FAILED`.
- `vessel_imo`: string, 7-digit IMO number expected in the vessel header.
- `containers`: integer, total container count parsed from the file.
- `issues`: array of expected issues, each containing `severity` (`ERROR` or `WARNING`), `code` (e.g. `IMO_MISMATCH`, `UNKNOWN_SIZE_TYPE`), and optional `segment_ref`.

Permitted outcome mappings:
- `expected_outcome = "PARSED"` <-> `expected_parse_status = "PARSED"`
- `expected_outcome = "QUARANTINED"` <-> `expected_parse_status = "QUARANTINED"`
- `expected_outcome = "REJECTED"` <-> `expected_parse_status = "FAILED"`

## 5. Standard corpus test suite (18 cases)

The 18 standard test cases defined in `contracts/qa/ai-testing-guide.md` Section 7.2 comprise the full acceptance suite:

| Case ID | Case Name | Format / Version | Injected Characteristic | Expected Outcome | Expected Parse Status | Key Assertions / Issues |
| --- | --- | --- | --- | --- | --- | --- |
| 01 | `01-valid-221` | SMDG 2.2.1 (D.95B) | Clean valid file with VGM | `PARSED` | `PARSED` | All containers loaded; 0 errors, 0 warnings |
| 02 | `02-valid-311` | SMDG 3.1.1 (D.13B) | Clean valid file with VGM | `PARSED` | `PARSED` | All containers loaded; 0 errors, 0 warnings |
| 03 | `03-valid-with-warnings` | SMDG 2.2.1 (D.95B) | Container check digit mismatch | `PARSED` | `PARSED` | Loaded; WARNING `CHECK_DIGIT_MISMATCH` |
| 04 | `04-imo-mismatch` | SMDG 2.2.1 (D.95B) | Vessel IMO differs from request | `QUARANTINED` | `QUARANTINED` | Staged; ERROR `IMO_MISMATCH` |
| 05 | `05-duplicate-container` | SMDG 2.2.1 (D.95B) | Duplicate container number in file | `QUARANTINED` | `QUARANTINED` | Staged; ERROR `DUPLICATE_CONTAINER_NUMBER` |
| 06 | `06-unknown-iso-size-type` | SMDG 2.2.1 (D.95B) | Invalid ISO code (e.g. `45X9`) | `QUARANTINED` | `QUARANTINED` | Staged; ERROR `UNKNOWN_SIZE_TYPE` |
| 07 | `07-unknown-imdg-class` | SMDG 2.2.1 (D.95B) | Unrecognized IMDG hazard code | `QUARANTINED` | `QUARANTINED` | Staged; ERROR `UNKNOWN_IMDG_CLASS` |
| 08 | `08-malformed-weight` | SMDG 2.2.1 (D.95B) | Negative or non-numeric weight | `QUARANTINED` | `QUARANTINED` | Staged; ERROR `MALFORMED_WEIGHT` |
| 09 | `09-malformed-unlocode` | SMDG 2.2.1 (D.95B) | Invalid port code syntax | `QUARANTINED` | `QUARANTINED` | Staged; ERROR `MALFORMED_UNLOCODE` |
| 10 | `10-temperature-out-of-range` | SMDG 2.2.1 (D.95B) | Reefer temperature < -40 or > +40 | `QUARANTINED` | `QUARANTINED` | Staged; ERROR `TEMPERATURE_OUT_OF_RANGE` |
| 11 | `11-reefer-missing-temp` | SMDG 2.2.1 (D.95B) | Reefer size code without set temp | `QUARANTINED` | `QUARANTINED` | Staged; ERROR `REEFER_MISSING_TEMPERATURE` |
| 12 | `12-invalid-stowage-coordinate` | SMDG 2.2.1 (D.95B) | Stowage bay/row/tier out of bounds | `QUARANTINED` | `QUARANTINED` | Staged; ERROR `INVALID_STOWAGE_COORDINATE` |
| 13 | `13-missing-mandatory-segment` | SMDG 2.2.1 (D.95B) | Missing mandatory LOC or MEA | `QUARANTINED` | `QUARANTINED` | Staged; ERROR `MISSING_MANDATORY_SEGMENT` |
| 14 | `14-multiple-errors-composite` | SMDG 2.2.1 (D.95B) | Combined IMO + size + weight errors | `QUARANTINED` | `QUARANTINED` | Staged; multiple ERROR issues reported |
| 15 | `15-non-edifact-payload` | Plain text / XML | Non-EDI formatted file | `REJECTED` | `FAILED` | 0 rows; ERROR `NOT_EDIFACT` |
| 16 | `16-unsupported-version` | SMDG 1.5 / 2.0 | Outdated or unsupported version | `REJECTED` | `FAILED` | 0 rows; ERROR `UNSUPPORTED_BAPLIE_VERSION` |
| 17 | `17-wrong-message-type` | EDIFACT COPRAR | Valid EDIFACT but wrong type | `REJECTED` | `FAILED` | 0 rows; ERROR `WRONG_MESSAGE_TYPE` |
| 18 | `18-corrupted-syntax` | Truncated EDI | Missing UNZ or broken delimiters | `REJECTED` | `FAILED` | 0 rows; ERROR `CORRUPTED_SYNTAX` |

## 6. Synthetic starter files

This directory contains three starter pairs demonstrating each outcome class:
1. `01-valid-221.edi` and `01-valid-221.expected.json` (`PARSED` / `PARSED`)
2. `04-imo-mismatch.edi` and `04-imo-mismatch.expected.json` (`QUARANTINED` / `QUARANTINED`)
3. `16-unsupported-version.edi` and `16-unsupported-version.expected.json` (`REJECTED` / `FAILED`)

All starter files are synthetic test artifacts generated for automated regression testing.
