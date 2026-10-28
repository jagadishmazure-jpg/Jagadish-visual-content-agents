"""Tests for the brand guard: fictional names only, enforced by a
hashed blocklist (real names are never stored in plain text)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from brand_check import BLOCKLIST_HASHES, find_violations, scan_paths

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_blocklist_is_non_empty():
    # A brand check with an empty blocklist checks nothing.
    assert len(BLOCKLIST_HASHES) > 0


def test_repo_files_contain_no_blocklisted_names():
    violations = scan_paths(REPO_ROOT)
    assert violations == {}, f"blocklisted real-company names found: {violations}"


def test_scan_detects_planted_violation(tmp_path):
    # Built from pieces so this test file itself stays clean for the scan.
    planted = tmp_path / "note.md"
    planted.write_text("we benchmark against " + "ub" + "er eats delivery photos\n")
    assert find_violations(planted) != []


def test_demo_fixtures_all_carry_brand_tokens():
    from visual_content.fixtures import demo_descriptors

    descriptors = demo_descriptors()
    assert descriptors, "demo fixture set must not be empty"
    for descriptor in descriptors:
        assert descriptor.brand_tokens, f"{descriptor.id} has no brand tokens"
