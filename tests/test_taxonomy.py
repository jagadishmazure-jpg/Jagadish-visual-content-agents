"""Failure-taxonomy tests: each class has a failing fixture and a
passing control, judged by both the QA gate and the pairwise eval."""

from visual_content import ImageDescriptor, pairwise_compare, qa_gate


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


def clean(**overrides):
    return mk(**overrides)


def test_taxonomy_added_object():
    original = mk()
    failing = mk(objects=("dish", "sauce", "shrimp"))
    control = clean()
    assert "faithfulness" in qa_gate(original, failing).failure_classes
    assert pairwise_compare(original, failing).verdict == "no"
    assert qa_gate(original, control).passed is True
    assert pairwise_compare(original, control).verdict != "no"


def test_taxonomy_removed_object():
    original = mk()
    failing = mk(objects=("dish",))
    control = clean()
    assert "completeness" in qa_gate(original, failing).failure_classes
    assert pairwise_compare(original, failing).verdict == "no"
    assert qa_gate(original, control).passed is True


def test_taxonomy_oversteer_reward_hack():
    original = mk(plating_style="rustic-board", sharpness=0.5)
    failing = mk(plating_style="generic", sharpness=0.9)
    control = mk(plating_style="rustic-board", sharpness=0.9)
    assert "naturalness" in qa_gate(original, failing).failure_classes
    assert pairwise_compare(original, failing).verdict == "unsure"
    assert qa_gate(original, control).passed is True
    assert pairwise_compare(original, control).verdict == "yes"


def test_taxonomy_object_coherence_physics():
    original = mk()
    failing = mk(plate_covers_sauce=True)
    control = clean()
    assert "naturalness" in qa_gate(original, failing).failure_classes
    assert pairwise_compare(original, failing).verdict == "no"
    assert qa_gate(original, control).passed is True


def test_taxonomy_count_uncertainty():
    original = mk(stated_count=8, observed_count=None)
    failing = mk(stated_count=8, observed_count=8)
    control = mk(stated_count=8, observed_count=None)
    assert "count" in qa_gate(original, failing).failure_classes
    assert pairwise_compare(original, failing).verdict == "unsure"
    assert qa_gate(original, control).passed is True
