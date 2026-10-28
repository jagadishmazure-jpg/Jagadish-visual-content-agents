"""Tests for descriptor validation."""

import math

import pytest

from visual_content import ImageDescriptor


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


def test_valid_descriptor_stores_fields():
    desc = mk(sharpness=0.5, composition=0.6)
    assert desc.sharpness == 0.5
    assert desc.composition == 0.6
    assert desc.mean_quality == pytest.approx((0.5 + 0.6 + 1.0 + 1.0) / 4)


def test_score_above_one_rejected():
    with pytest.raises(ValueError):
        mk(sharpness=1.2)


def test_score_below_zero_rejected():
    with pytest.raises(ValueError):
        mk(color=-0.1)


def test_score_bool_rejected():
    with pytest.raises(TypeError):
        mk(plating=True)


def test_score_nan_rejected():
    with pytest.raises(ValueError):
        mk(sharpness=math.nan)


def test_negative_count_rejected():
    with pytest.raises(ValueError):
        mk(observed_count=-1)


def test_count_none_allowed():
    desc = mk(observed_count=None, stated_count=8)
    assert desc.observed_count is None


def test_quality_dict_keys():
    desc = mk()
    assert set(desc.quality) == {"sharpness", "composition", "color", "plating"}
