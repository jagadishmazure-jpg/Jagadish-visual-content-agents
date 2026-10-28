"""Tests for the end-to-end pipeline and its flat run log."""

import json

import pytest

from visual_content import ImageDescriptor, pass_at_k, rollup, run_pipeline
from visual_content.fixtures import demo_descriptors


def mk(**overrides):
    base = dict(
        id="t1",
        merchant="Emberline Kitchen",
        dish_name="Test Dish",
        stated_count=None,
        observed_count=None,
        objects=("dish",),
        brand_tokens=("emberline-logo",),
    )
    base.update(overrides)
    return ImageDescriptor(**base)


def test_skip_path_publishes_original():
    record = run_pipeline(mk())
    assert record["route"] == "skip"
    assert record["published_variant"] == "original"
    assert record["iterations"] == 0


def test_enhance_passes_on_first_iteration():
    record = run_pipeline(mk(sharpness=0.55))
    assert record["route"] == "enhance"
    assert record["qa_pass_iteration"] == 1
    assert record["published_variant"] == "enhanced"
    assert record["pairwise_verdict"] == "yes"


def test_enhance_passes_on_second_iteration():
    record = run_pipeline(mk(sharpness=0.35))
    assert record["qa_pass_iteration"] == 2
    assert record["published_variant"] == "enhanced"


def test_count_mismatch_is_a_coverage_hit():
    record = run_pipeline(mk(stated_count=8, observed_count=6))
    assert record["coverage_hit"] is True
    assert record["published_variant"] == "original"
    assert "count" in record["failure_classes"]


def test_unfixable_plating_is_a_coverage_hit():
    record = run_pipeline(mk(plating=0.9, plating_realistic=False))
    assert record["coverage_hit"] is True
    assert record["published_variant"] == "original"


def test_publish_floor_leakage_falls_back_to_original():
    # Sharpness 0.50 -> 0.70 passes QA (floor 0.70) but fails publish QA
    # (floor 0.75), so the original is published instead.
    record = run_pipeline(mk(sharpness=0.50))
    assert record["qa_passed"] is True
    assert record["published_variant"] == "original"
    assert "publish_floor" in record["failure_classes"]


def test_run_record_is_flat_json():
    record = run_pipeline(mk(sharpness=0.35))
    json.dumps(record)  # must serialise
    for value in record.values():
        assert value is None or isinstance(
            value, (str, int, float, bool, list)
        ), f"nested value in flat record: {value!r}"
        if isinstance(value, list):
            assert all(isinstance(item, str) for item in value)


def test_pass_at_k_curve():
    records = [
        {"route": "enhance", "qa_pass_iteration": 1},
        {"route": "enhance", "qa_pass_iteration": 2},
        {"route": "enhance", "qa_pass_iteration": None},
        {"route": "skip", "qa_pass_iteration": None},
    ]
    assert pass_at_k(records, 3) == [0.333, 0.667, 0.667]


def test_demo_rollup_numbers():
    records = [run_pipeline(d) for d in demo_descriptors()]
    summary = rollup(records)
    assert summary["runs"] == 13
    assert summary["by_route"] == {"skip": 4, "enhance": 9}
    assert summary["pass_at_k"] == [0.111, 0.556, 0.667]
    assert summary["coverage_hits"] == 3
    assert summary["leakage_reached_publish_qa"] == 2  # dark soup + dim ramen land in the 0.70-0.75 band
    assert summary["published_bad"] == 0
    assert summary["published_enhanced"] == 4
    assert summary["published_original"] == 9
    assert summary["published_none"] == 0
    assert summary["total_edit_cost_usd"] == pytest.approx(0.71)
