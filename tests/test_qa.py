"""Tests for the multi-dimensional QA gate, incl. fail-closed paths."""

from visual_content import ImageDescriptor, qa_gate


def mk(**overrides):
    base = dict(
        id="t1",
        merchant="Emberline Kitchen",
        dish_name="Test Dish",
        stated_count=None,
        observed_count=None,
        objects=("dish", "sauce"),
        brand_tokens=("emberline-logo",),
    )
    base.update(overrides)
    return ImageDescriptor(**base)


def clean_edited(**overrides):
    base = dict(sharpness=0.9, composition=0.9, color=0.9, plating=0.9)
    base.update(overrides)
    return mk(**base)


def test_qa_passes_clean_candidate():
    result = qa_gate(mk(), clean_edited())
    assert result.passed is True
    assert result.reasons == ()


def test_qa_fails_low_plating():
    result = qa_gate(mk(), clean_edited(plating=0.5))
    assert result.passed is False
    assert "plating" in result.failure_classes


def test_qa_fails_unrealistic_plating():
    result = qa_gate(mk(), clean_edited(plating_realistic=False))
    assert "plating" in result.failure_classes


def test_qa_fails_low_color():
    result = qa_gate(mk(), clean_edited(color=0.5))
    assert "colors" in result.failure_classes


def test_qa_fails_unnatural_color():
    result = qa_gate(mk(), clean_edited(color_natural=False))
    assert "colors" in result.failure_classes


def test_qa_fails_added_object():
    result = qa_gate(mk(), clean_edited(objects=("dish", "sauce", "shrimp")))
    assert "faithfulness" in result.failure_classes
    assert any("shrimp" in reason for reason in result.reasons)


def test_qa_fails_removed_object():
    result = qa_gate(mk(), clean_edited(objects=("dish",)))
    assert "completeness" in result.failure_classes


def test_qa_fails_genericization():
    result = qa_gate(mk(plating_style="rustic-board"), clean_edited(plating_style="generic"))
    assert "naturalness" in result.failure_classes


def test_qa_fails_plate_covering_sauce():
    result = qa_gate(mk(), clean_edited(plate_covers_sauce=True))
    assert "naturalness" in result.failure_classes


def test_qa_fails_count_changed():
    result = qa_gate(mk(stated_count=8, observed_count=8), clean_edited(observed_count=6))
    assert "count" in result.failure_classes


def test_qa_fails_count_asserted_when_unverifiable():
    original = mk(stated_count=8, observed_count=None)
    result = qa_gate(original, clean_edited(observed_count=8))
    assert "count" in result.failure_classes
    assert any("count_unverifiable" in reason for reason in result.reasons)


def test_qa_fails_menu_count_mismatch():
    original = mk(stated_count=8, observed_count=6)
    result = qa_gate(original, clean_edited(observed_count=6))
    assert "count" in result.failure_classes


def test_qa_missing_candidate_fails_closed():
    result = qa_gate(mk(), None)
    assert result.passed is False
    assert result.reasons == ("missing_candidate",)


def test_qa_remediation_fails_when_flagged_criterion_unmet():
    result = qa_gate(mk(sharpness=0.4), clean_edited(sharpness=0.65), ("sharpness",))
    assert "remediation" in result.failure_classes


def test_qa_remediation_passes_when_flagged_criterion_met():
    result = qa_gate(mk(sharpness=0.4), clean_edited(sharpness=0.75), ("sharpness",))
    assert result.passed is True


def test_qa_remediation_never_passes_count_criterion():
    original = mk(stated_count=8, observed_count=6)
    result = qa_gate(original, clean_edited(observed_count=6), ("count",))
    assert "remediation" in result.failure_classes
