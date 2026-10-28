"""Tests for the fake vision backend."""

from visual_content import FakeVision, ImageDescriptor


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


VISION = FakeVision()


def test_description_mirrors_descriptor():
    desc = VISION.describe(mk(sharpness=0.4, dish_name="Noodles"))
    assert desc.dish_name == "Noodles"
    assert desc.quality["sharpness"] == 0.4
    assert desc.brand_tokens == ("emberline-logo",)


def test_low_scores_become_issues():
    desc = VISION.describe(mk(sharpness=0.3, composition=0.9, color=0.2, plating=0.9))
    assert "low_sharpness" in desc.issues
    assert "poor_color" in desc.issues
    assert "poor_composition" not in desc.issues


def test_count_mismatch_issue():
    desc = VISION.describe(mk(stated_count=8, observed_count=6))
    assert "count_mismatch" in desc.issues
    assert desc.count_verifiable is True


def test_count_unverifiable_issue():
    desc = VISION.describe(mk(stated_count=8, observed_count=None))
    assert "count_unverifiable" in desc.issues
    assert desc.count_verifiable is False


def test_unrealistic_plating_issue():
    desc = VISION.describe(mk(plating_realistic=False))
    assert "unrealistic_plating" in desc.issues


def test_describe_is_deterministic():
    descriptor = mk(sharpness=0.4)
    assert VISION.describe(descriptor) == VISION.describe(descriptor)
