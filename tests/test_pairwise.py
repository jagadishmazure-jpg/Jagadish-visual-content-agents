"""Tests for the pairwise generation eval."""

from visual_content import ImageDescriptor, pairwise_compare


def mk(**overrides):
    base = dict(
        id="t1",
        merchant="Emberline Kitchen",
        dish_name="Test Dish",
        stated_count=None,
        observed_count=None,
        objects=("dish", "sauce"),
        sharpness=0.5,
        composition=0.5,
        color=0.5,
        plating=0.5,
        brand_tokens=("emberline-logo",),
    )
    base.update(overrides)
    return ImageDescriptor(**base)


def improved(**overrides):
    base = dict(sharpness=0.9, composition=0.9, color=0.9, plating=0.9)
    base.update(overrides)
    return mk(**base)


def test_pairwise_yes_for_clean_improvement():
    verdict = pairwise_compare(mk(), improved())
    assert verdict.verdict == "yes"


def test_pairwise_no_for_added_object():
    verdict = pairwise_compare(mk(), improved(objects=("dish", "sauce", "shrimp")))
    assert verdict.verdict == "no"
    assert "faithfulness" in verdict.reasons[0]


def test_pairwise_no_for_removed_object():
    verdict = pairwise_compare(mk(), improved(objects=("dish",)))
    assert verdict.verdict == "no"
    assert "completeness" in verdict.reasons[0]


def test_pairwise_no_for_plate_covering_sauce():
    verdict = pairwise_compare(mk(), improved(plate_covers_sauce=True))
    assert verdict.verdict == "no"


def test_pairwise_no_for_changed_count():
    original = mk(stated_count=8, observed_count=8)
    verdict = pairwise_compare(original, improved(observed_count=6))
    assert verdict.verdict == "no"


def test_pairwise_unsure_for_unverifiable_claimed_count():
    original = mk(stated_count=8, observed_count=None)
    verdict = pairwise_compare(original, improved(observed_count=None))
    assert verdict.verdict == "unsure"


def test_pairwise_unsure_for_genericization():
    original = mk(plating_style="rustic-board")
    verdict = pairwise_compare(original, improved(plating_style="generic"))
    assert verdict.verdict == "unsure"


def test_pairwise_unsure_for_nugatory_change():
    original = mk(sharpness=0.80, composition=0.80, color=0.80, plating=0.80)
    edited = mk(sharpness=0.82, composition=0.81, color=0.80, plating=0.80)
    verdict = pairwise_compare(original, edited)
    assert verdict.verdict == "unsure"
    assert "nugatory" in verdict.reasons[0]


def test_pairwise_yes_at_meaningful_delta_boundary():
    original = mk(sharpness=0.80, composition=0.80, color=0.80, plating=0.80)
    edited = mk(sharpness=0.90, composition=0.90, color=0.80, plating=0.80)
    # Mean delta is exactly 0.05: at the threshold, it counts as better.
    verdict = pairwise_compare(original, edited)
    assert verdict.verdict == "yes"
