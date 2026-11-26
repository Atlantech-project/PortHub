#!/usr/bin/env python3
"""
ATLANTECH Combined Sprint 2 + Sprint 3 Release Test Runner (QA-RT2 + QA-RT3, v0.3.0)
Single entry-point orchestrator executing:
  1. test_api_sprint2.py (FT-02, FT-03)
  2. test_ai_runtime_contracts.py (FT-01, QA-AI2 + BAPLIE D.95B/D.17A corpus check)
  3. test_api_sprint3.py (FT-04, FT-05)

Supports live Docker API/Redis execution (--base-url http://localhost:8000) and
automatic offline contract, schema, and acceptance test specification fallback.

Coverage Inventory (113 Acceptance Test Cases):
  - FT-01: 15
  - FT-02: 20
  - FT-03: 22
  - QA-AI2: 7
  - FT-04: 24
  - FT-05: 25
"""

import argparse
import hashlib
import os
import re
import subprocess
import sys
import time
from typing import Dict, List, Tuple


class Colors:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    CYAN = "\033[96m"
    BOLD = "\033[1m"
    RESET = "\033[0m"


EXPECTED_SUITE_COUNTS: List[Tuple[str, str, str, int]] = [
    ("FT-01", "AI Subsystem Runtime Contracts and Isolation", "FT-01.md", 15),
    ("FT-02", "Sign-in and Session Management (Web and Mobile)", "FT-02.md", 20),
    ("FT-03", "Access Control, RBAC, OCC, and Tenant Isolation", "FT-03.md", 22),
    ("QA-AI2", "BAPLIE D.95B Corpus and CT-12 Version Gate", "QA-AI2-baplie.md", 7),
    ("FT-04", "Port Master Data and Safety Limits", "FT-04.md", 24),
    ("FT-05", "Department and Terminal Master Data", "FT-05.md", 25),
]


def count_test_cases_in_md(filepath: str, suite_id: str) -> int:
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    if suite_id == "QA-AI2":
        matches = set(re.findall(r"###\s+(TC-BAP-\d+):", content))
    else:
        num = suite_id.split("-")[1]
        matches = set(re.findall(rf"###\s+(TC-{num}-\d+):", content))
    return len(matches)


def verify_baplie_corpus(qa_root: str) -> Tuple[bool, str]:
    corpus_dir = os.path.join(qa_root, "baplie-corpus")
    required_files = [
        "01_valid_standard_discharge.edi",
        "02_valid_special_cargo_hazmat_reefer.edi",
        "03_malformed_syntax_error.edi",
        "04_semantic_quarantine_missing_iso.edi",
        "05_duplicate_payload_sample.edi",
        "06_unsupported_version_d17a.edi",
    ]
    for fn in required_files:
        fp = os.path.join(corpus_dir, fn)
        if not os.path.isfile(fp):
            return False, f"Missing corpus file: {fn}"

    with open(os.path.join(corpus_dir, "01_valid_standard_discharge.edi"), "rb") as f1:
        h1 = hashlib.sha256(f1.read()).hexdigest()
    with open(os.path.join(corpus_dir, "05_duplicate_payload_sample.edi"), "rb") as f5:
        h5 = hashlib.sha256(f5.read()).hexdigest()
    if h1 != h5:
        return False, "Files 01 and 05 SHA-256 mismatch"

    with open(os.path.join(corpus_dir, "01_valid_standard_discharge.edi"), "r", encoding="utf-8") as f1t:
        if "BAPLIE:D:95B:UN:SMDG22" not in f1t.read():
            return False, "File 01 missing CT-12 UNH identifier BAPLIE:D:95B:UN:SMDG22"

    with open(os.path.join(corpus_dir, "06_unsupported_version_d17a.edi"), "r", encoding="utf-8") as f6t:
        if "BAPLIE:D:17A:UN:SMDG20" not in f6t.read():
            return False, "File 06 missing D.17A rejection header BAPLIE:D:17A:UN:SMDG20"

    return True, f"6 EDI files verified (CT-12 D.95B + D.17A rejection, SHA-256 {h1[:12]}...)"


def parse_runner_counts(output: str) -> Dict[str, int]:
    counts = {"executed": 0, "passed": 0, "failed": 0, "skipped": 0}
    m_exec = re.search(r"Total (?:Tests Run|Tests Executed|Contract Suites Executed):\s*(\d+)", output)
    m_pass = re.search(r"Passed:\s*(?:\x1b\[[0-9;]*m)?(\d+)", output)
    m_fail = re.search(r"Failed:\s*(?:\x1b\[[0-9;]*m)?(\d+)", output)
    m_skip = re.search(r"Skipped:\s*(?:\x1b\[[0-9;]*m)?(\d+)", output)
    if m_exec:
        counts["executed"] = int(m_exec.group(1))
    if m_pass:
        counts["passed"] = int(m_pass.group(1))
    if m_fail:
        counts["failed"] = int(m_fail.group(1))
    if m_skip:
        counts["skipped"] = int(m_skip.group(1))
    return counts


def run_step(label: str, cmd: List[str]) -> Tuple[int, Dict[str, int], float]:
    print(f"\n{Colors.CYAN}======================================================================{Colors.RESET}")
    print(f"{Colors.BOLD}[STEP] {label}{Colors.RESET}")
    print(f"Command: {' '.join(cmd)}")
    print(f"{Colors.CYAN}======================================================================{Colors.RESET}")
    t0 = time.time()
    proc = subprocess.run(cmd, capture_output=True, text=True)
    dur_ms = (time.time() - t0) * 1000.0
    if proc.stdout:
        print(proc.stdout.rstrip())
    if proc.stderr:
        print(proc.stderr.rstrip(), file=sys.stderr)
    counts = parse_runner_counts(proc.stdout or "")
    return proc.returncode, counts, dur_ms


def main():
    parser = argparse.ArgumentParser(
        description="ATLANTECH Combined Sprint 2 + Sprint 3 Release Test Runner (v0.3.0)"
    )
    parser.add_argument("--base-url", default="http://localhost:8000", help="Target API base URL")
    parser.add_argument("--username", default="admin.damietta", help="Admin username")
    parser.add_argument("--password", default="PortPass123!", help="Admin password")
    parser.add_argument("--token", default=None, help="Pre-authenticated Bearer token")
    parser.add_argument("--redis-host", default="127.0.0.1", help="Redis host for AI runtime contracts")
    parser.add_argument("--redis-port", type=int, default=6379, help="Redis port for AI runtime contracts")
    parser.add_argument("--dry-run", action="store_true", help="Force offline contract and schema verification mode")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging in sub-runners")
    args = parser.parse_args()

    automation_dir = os.path.dirname(os.path.abspath(__file__))
    qa_root = os.path.dirname(automation_dir)
    test_cases_dir = os.path.join(qa_root, "test-cases")

    print(f"{Colors.BOLD}ATLANTECH COMBINED RELEASE VERIFICATION SUITE (Sprint 2 + Sprint 3 / v0.3.0){Colors.RESET}")
    print(f"Target API: {args.base_url} | Target Redis: {args.redis_host}:{args.redis_port}")

    common_api_args = ["--base-url", args.base_url, "--username", args.username, "--password", args.password]
    if args.token:
        common_api_args.extend(["--token", args.token])
    if args.dry_run:
        common_api_args.append("--dry-run")
    if args.verbose:
        common_api_args.append("--verbose")

    ai_args = ["--redis-host", args.redis_host, "--redis-port", str(args.redis_port)]
    if args.dry_run:
        ai_args.append("--check-schema-only")
    if args.verbose:
        ai_args.append("--verbose")

    steps = [
        (
            "1. Sprint 2 API Suite (FT-02, FT-03)",
            [sys.executable, os.path.join(automation_dir, "test_api_sprint2.py")] + common_api_args,
        ),
        (
            "2. AI Runtime Contracts Suite (FT-01, QA-AI2)",
            [sys.executable, os.path.join(automation_dir, "test_ai_runtime_contracts.py")] + ai_args,
        ),
        (
            "3. Sprint 3 API Suite (FT-04, FT-05)",
            [sys.executable, os.path.join(automation_dir, "test_api_sprint3.py")] + common_api_args,
        ),
    ]

    step_results = []
    overall_failed = 0

    for label, cmd in steps:
        rc, counts, dur_ms = run_step(label, cmd)
        step_results.append((label, rc, counts, dur_ms))
        if rc != 0 or counts["failed"] > 0:
            overall_failed += 1

    # Verify QA-AI2 BAPLIE Corpus + 113 Acceptance Test Case Inventory
    corpus_ok, corpus_msg = verify_baplie_corpus(qa_root)
    if not corpus_ok:
        overall_failed += 1

    total_spec_cases = 0
    spec_rows = []
    for suite_id, title, md_file, expected_count in EXPECTED_SUITE_COUNTS:
        fp = os.path.join(test_cases_dir, md_file)
        actual_count = count_test_cases_in_md(fp, suite_id) if os.path.isfile(fp) else 0
        total_spec_cases += actual_count
        status = "VERIFIED" if actual_count == expected_count else f"MISMATCH (expected {expected_count})"
        if actual_count != expected_count:
            overall_failed += 1
        spec_rows.append((suite_id, title, actual_count, status))

    print(f"\n{Colors.CYAN}======================================================================{Colors.RESET}")
    print(f"{Colors.BOLD}COMBINED SPRINT 2 + SPRINT 3 RELEASE SUMMARY (v0.3.0){Colors.RESET}")
    print(f"{Colors.CYAN}======================================================================{Colors.RESET}")

    tot_exec = tot_pass = tot_fail = tot_skip = 0
    for label, rc, c, dur_ms in step_results:
        tot_exec += c["executed"]
        tot_pass += c["passed"]
        tot_fail += c["failed"]
        tot_skip += c["skipped"]
        state_str = f"{Colors.GREEN}PASS{Colors.RESET}" if rc == 0 else f"{Colors.RED}FAIL{Colors.RESET}"
        print(
            f"  [{state_str}] {label}: executed={c['executed']}, passed={c['passed']}, "
            f"failed={c['failed']}, skipped={c['skipped']} ({dur_ms:.0f}ms)"
        )

    corpus_badge = f"{Colors.GREEN}PASS{Colors.RESET}" if corpus_ok else f"{Colors.RED}FAIL{Colors.RESET}"
    print(f"  [{corpus_badge}] 4. QA-AI2 BAPLIE Corpus Check: {corpus_msg}")

    print(f"\n{Colors.BOLD}Acceptance Test Case Coverage Inventory:{Colors.RESET}")
    for suite_id, title, cnt, status in spec_rows:
        print(f"  - {suite_id:6s} | {cnt:2d} cases | {status} | {title}")
    print(f"  Total Acceptance Test Cases Covered: {total_spec_cases} / 113")

    print(f"\nRunner Totals: executed={tot_exec}, passed={tot_pass}, failed={tot_fail}, skipped={tot_skip}")
    if overall_failed == 0:
        print(f"{Colors.GREEN}[OVERALL COMBINED VERDICT: PASSED]{Colors.RESET}")
        sys.exit(0)
    else:
        print(f"{Colors.RED}[OVERALL COMBINED VERDICT: FAILED]{Colors.RESET} ({overall_failed} issue(s) detected)")
        sys.exit(1)


if __name__ == "__main__":
    main()
