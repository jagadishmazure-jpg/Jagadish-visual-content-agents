"""Tests for the deterministic fake editor."""

from visual_content import ImageDescriptor, edit


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


def test_edit_improves_targeted_dimension_by_one_step():
    edited = edit(mk(sharpness=0.4), ("improve_sharpness",))
    assert edited.sharpness == 0.6
    assert edited.color == 1.0  # untouched dimensions do not move


def test_edit_caps_at_ceiling():
    edited = edit(mk(sharpness=0.9), ("improve_sharpness",))
    assert edited.sharpness == 0.95


def test_edit_applies_each_directive_once():
    edited = edit(
        mk(sharpness=0.4, color=0.4), ("improve_sharpness", "restore_natural_color")
    )
    assert edited.sharpness == 0.6
    assert edited.color == 0.6


def test_verify_count_directive_changes_nothing():
    original = mk(stated_count=8, observed_count=6, sharpness=0.4)
    edited = edit(original, ("verify_count",))
    assert edited == original


def test_edit_never_changes_identity_or_counts():
    original = mk(
        stated_count=8,
        observed_count=6,
        objects=("wings", "dip"),
        brand_tokens=("emberline-logo",),
        plating_style="house",
    )
    edited = edit(original, ("improve_sharpness", "improve_plating"))
    assert edited.dish_name == original.dish_name
    assert edited.objects == original.objects
    assert edited.observed_count == original.observed_count
    assert edited.brand_tokens == original.brand_tokens
    assert edited.plating_style == original.plating_style


def test_unknown_directive_ignored():
    original = mk(sharpness=0.4)
    assert edit(original, ("do_something_magical",)) == original
