"""Tests for image-specific prompts and the diversity check."""

from visual_content import FakeVision, ImageDescriptor, diversity_report, generate_prompt

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


def prompt_for(**overrides):
    return generate_prompt(
        VISION.describe(mk(**overrides)),
        ("improve_sharpness", "restore_natural_color"),
    )


def test_prompt_names_dish_and_merchant():
    prompt = prompt_for(dish_name="Garlic Noodles", merchant="Saffron Lantern")
    assert "Garlic Noodles" in prompt
    assert "Saffron Lantern" in prompt


def test_prompt_includes_directive_text():
    prompt = prompt_for(sharpness=0.3)
    assert "sharpen details" in prompt


def test_prompt_with_empty_directives_falls_back():
    prompt = generate_prompt(VISION.describe(mk()), ())
    assert "Test Dish" in prompt
    assert "overall photo quality" in prompt


def test_prompt_includes_qa_feedback():
    prompt = generate_prompt(
        VISION.describe(mk()), ("improve_plating",), ("plating still below floor",)
    )
    assert "plating still below floor" in prompt


def test_prompt_is_deterministic():
    description = VISION.describe(mk())
    assert generate_prompt(description, ("improve_sharpness",)) == generate_prompt(
        description, ("improve_sharpness",)
    )


def test_diversity_passes_for_distinct_prompts():
    prompts = [
        prompt_for(dish_name="Garlic Noodles", merchant="Saffron Lantern"),
        prompt_for(dish_name="Tomato Soup", merchant="Copper Ladle"),
        prompt_for(dish_name="Margherita Pizza", merchant="Maple & Thyme"),
    ]
    report = diversity_report(prompts)
    assert report["unique"] == 3
    assert report["passed"] is True


def test_diversity_fails_for_shared_prompt():
    prompt = prompt_for()
    report = diversity_report([prompt, prompt, prompt])
    assert report["passed"] is False
    assert report["max_pairwise_similarity"] == 1.0
