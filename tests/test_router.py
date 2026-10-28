"""Tests for the router: rubric, tiers, and router eval."""

import pytest

from visual_content import FakeVision, ImageDescriptor, decide, evaluate_router, evaluate_tiers, grade
from visual_content.fixtures import demo_descriptors, demo_gold
from visual_content.router import TIERS, ConfusionMatrix, ModelTier

VISION = FakeVision()


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


def decide_for(**overrides):
    return decide(VISION.describe(mk(**overrides)))


def test_skip_when_everything_passes():
    decision = decide_for()
    assert decision.route == "skip"
    assert decision.tier is None
    assert decision.directives == ()


def test_enhance_when_one_criterion_fails():
    decision = decide_for(sharpness=0.4)
    assert decision.route == "enhance"
    assert "improve_sharpness" in decision.directives


def test_directives_match_failed_criteria_only():
    decision = decide_for(sharpness=0.4, color=0.5)
    assert set(decision.directives) == {"improve_sharpness", "restore_natural_color"}


def test_count_mismatch_routes_to_enhance():
    decision = decide_for(stated_count=8, observed_count=6)
    assert decision.route == "enhance"
    assert "verify_count" in decision.directives


def test_count_unverifiable_flagged():
    decision = decide_for(stated_count=8, observed_count=None)
    assert decision.route == "enhance"
    assert decision.count_unverified is True


def test_missing_score_fails_closed():
    description = VISION.describe(mk())
    broken = type(description)(**{**description.__dict__, "quality": {"sharpness": 0.9}})
    failed = [c.name for c in grade(broken) if not c.passed]
    assert set(failed) == {"composition", "color", "plating"}


def test_tier_lite_at_boundary():
    assert decide_for(composition=0.45).tier == "lite"  # deficit exactly 0.15


def test_tier_standard_above_lite_boundary():
    assert decide_for(composition=0.44).tier == "standard"  # deficit 0.16


def test_tier_pro_for_severe_deficit():
    assert decide_for(plating=0.24).tier == "pro"  # deficit 0.36


def test_tier_standard_for_count_only_failure():
    assert decide_for(stated_count=8, observed_count=6).tier == "standard"


def test_confusion_matrix_math():
    matrix = ConfusionMatrix(tp=7, fp=1, fn=1, tn=3)
    assert matrix.precision == pytest.approx(7 / 8)
    assert matrix.recall == pytest.approx(7 / 8)
    assert matrix.accuracy == pytest.approx(10 / 12)


def test_precision_recall_zero_denominator_is_zero():
    matrix = ConfusionMatrix(tp=0, fp=0, fn=0, tn=5)
    assert matrix.precision == 0.0
    assert matrix.recall == 0.0


def test_evaluate_router_counts():
    decisions = [decide_for(sharpness=0.4), decide_for(), decide_for(color=0.2)]
    matrix = evaluate_router(decisions, ["enhance", "enhance", "skip"])
    assert (matrix.tp, matrix.fp, matrix.fn, matrix.tn) == (1, 1, 1, 0)


def test_demo_router_precision_recall():
    descriptors = demo_descriptors()
    gold_routes, _ = demo_gold()
    decisions = [decide(VISION.describe(d)) for d in descriptors]
    matrix = evaluate_router(decisions, gold_routes)
    # Hand-computed: TP=8, FP=1 (artistic dessert), FN=1 (borderline bowl), TN=3.
    assert (matrix.tp, matrix.fp, matrix.fn, matrix.tn) == (8, 1, 1, 3)
    assert matrix.precision == pytest.approx(8 / 9)
    assert matrix.recall == pytest.approx(8 / 9)
    assert matrix.accuracy == pytest.approx(11 / 13)


def test_demo_recall_clears_guardrail():
    descriptors = demo_descriptors()
    gold_routes, _ = demo_gold()
    decisions = [decide(VISION.describe(d)) for d in descriptors]
    matrix = evaluate_router(decisions, gold_routes)
    assert matrix.recall >= 0.80  # recall guardrail on the demo regression set


def test_demo_tier_matrix():
    descriptors = demo_descriptors()
    _, gold_tiers = demo_gold()
    decisions = [decide(VISION.describe(d)) for d in descriptors]
    predicted = [d.tier for d in decisions]
    result = evaluate_tiers(predicted, gold_tiers)
    # One boundary miss: offcenter pizza is gold standard, router lite.
    assert result["matrix"].get(("standard", "lite"), 0) == 1
    assert result["matrix"].get(("lite", "lite"), 0) == 1
    assert result["matrix"].get(("pro", "pro"), 0) == 1
    assert result["tier_accuracy"] == pytest.approx(7 / 8)
    assert result["per_tier"]["lite"]["precision"] == pytest.approx(1 / 2)
    assert result["per_tier"]["standard"]["recall"] == pytest.approx(5 / 6)


def test_negative_tier_cost_rejected():
    with pytest.raises(ValueError):
        ModelTier("bad", -0.01, 1.0, 1)


def test_negative_tier_latency_rejected():
    with pytest.raises(ValueError):
        ModelTier("bad", 0.01, -1.0, 1)


def test_zero_tier_cost_allowed():
    assert ModelTier("free", 0.0, 0.0, 0).cost_usd == 0.0


def test_tier_cost_latency_increase_with_quality():
    ordered = sorted(TIERS.values(), key=lambda t: t.quality_rank)
    costs = [t.cost_usd for t in ordered]
    latencies = [t.latency_s for t in ordered]
    assert costs == sorted(costs) and latencies == sorted(latencies)
    assert [t.name for t in ordered] == ["lite", "standard", "pro"]
