"""Tests for publish-ready QA, incl. the Swiss-cheese catch and
fail-closed paths. Publish QA takes only (original, candidate): there
is no QA verdict parameter to forge, so a skipped QA gate cannot be
papered over at publish time."""

import inspect

from visual_content import ImageDescriptor, publish_qa, qa_gate


def mk(**overrides):
    base = dict(
        id="t1",
        merchant="Emberline Kitchen",
        dish_name="Test Dish",
        stated_count=None,
        observed_count=None,
        objects=("dish", "sauce"),
        sharpness=0.9,
        composition=0.9,
        color=0.9,
        plating=0.9,
        brand_tokens=("emberline-logo",),
    )
    base.update(overrides)
    return ImageDescriptor(**base)


def test_publish_passes_clean_enhanced_candidate():
    result = publish_qa(mk(), mk(), "enhanced")
    assert result.published is True


def test_publish_qa_catches_brand_change_qa_gate_misses():
    original = mk()
    candidate = mk(brand_tokens=("other-logo",))
    assert qa_gate(original, candidate).passed is True  # QA never checks brand
    result = publish_qa(original, candidate, "enhanced")
    assert result.published is False
    assert "brand" in result.failure_classes


def test_publish_rejects_dish_change():
    result = publish_qa(mk(), mk(dish_name="Other Dish"), "enhanced")
    assert "dish" in result.failure_classes


def test_publish_rejects_new_overlay_text():
    result = publish_qa(mk(), mk(overlay_text="100% organic!"), "enhanced")
    assert "overlay" in result.failure_classes


def test_publish_rejects_policy_flag():
    result = publish_qa(mk(), mk(policy_flags=("misleading_claim",)), "enhanced")
    assert "policy" in result.failure_classes


def test_publish_rejects_count_change():
    original = mk(stated_count=8, observed_count=8)
    result = publish_qa(original, mk(observed_count=6), "enhanced")
    assert "count" in result.failure_classes


def test_publish_floor_rejects_qa_passing_band():
    # QA floor is 0.70; publish floor is 0.75. A candidate at 0.70 passes
    # QA but must fail publish QA: this is measurable leakage.
    original = mk(sharpness=0.5)
    candidate = mk(sharpness=0.70)
    assert qa_gate(original, candidate).passed is True
    result = publish_qa(original, candidate, "enhanced")
    assert result.published is False
    assert "publish_floor" in result.failure_classes


def test_publish_floor_passes_at_threshold():
    result = publish_qa(mk(), mk(sharpness=0.75), "enhanced")
    assert result.published is True


def test_publish_original_ignores_quality_floor():
    # An original photo is judged on policy/identity, not beauty.
    result = publish_qa(mk(sharpness=0.3), mk(sharpness=0.3), "original")
    assert result.published is True


def test_publish_missing_candidate_rejected():
    result = publish_qa(mk(), None, "enhanced")
    assert result.published is False
    assert result.reasons == ("missing_candidate",)


def test_publish_qa_takes_no_qa_verdict_parameter():
    params = inspect.signature(publish_qa).parameters
    assert "qa_result" not in params
    assert "qa" not in params
    assert set(params) == {"original", "candidate", "variant"}
