"""Demo fixture set for the fictional Savorlane marketplace.

Gold labels here play the role of human labels: they are hand-assigned
in this file, and they deliberately differ from the router rubric in
two places (the borderline photo and the artistic dessert), because a
router eval that agrees with its own rubric by construction proves
nothing. Gold route rule, in words: enhance when the worst quality
score is below 0.65, or the count disagrees with the menu, or the count
cannot be verified. Gold tier rule: worst deficit against 0.65 --
up to 0.20 is lite, up to 0.40 is standard, beyond that is pro; a
count-only failure is standard. The router, by contrast, grades against
0.60, so boundary photos separate the two -- that is the point of the
n-by-n matrix.

All merchants, dishes, and photos are invented. Savorlane is a fictional
marketplace name; a web check on 2026-10-28 found no exact-match real
business under that name.
"""

from __future__ import annotations

from .descriptors import ImageDescriptor

# (descriptor, gold_route, gold_tier)
FIXTURES = []


def _add(descriptor, gold_route, gold_tier):
    FIXTURES.append((descriptor, gold_route, gold_tier))
    return descriptor


GOOD_BURGER = _add(
    ImageDescriptor(
        id="good-burger",
        merchant="Emberline Kitchen",
        dish_name="Smash Burger",
        stated_count=None,
        observed_count=None,
        objects=("burger", "fries"),
        sharpness=0.90,
        composition=0.90,
        color=0.90,
        plating=0.90,
        brand_tokens=("emberline-logo",),
    ),
    "skip",
    None,
)

GOOD_SALAD = _add(
    ImageDescriptor(
        id="good-salad",
        merchant="Juniper Table",
        dish_name="Garden Salad",
        stated_count=None,
        observed_count=None,
        objects=("salad", "dressing"),
        sharpness=0.85,
        composition=0.88,
        color=0.90,
        plating=0.86,
        brand_tokens=("juniper-mark",),
    ),
    "skip",
    None,
)

BLURRY_NOODLES = _add(
    ImageDescriptor(
        id="blurry-noodles",
        merchant="Saffron Lantern",
        dish_name="Garlic Noodles",
        stated_count=None,
        observed_count=None,
        objects=("noodles", "herbs"),
        sharpness=0.35,
        composition=0.80,
        color=0.80,
        plating=0.80,
        brand_tokens=("saffron-seal",),
    ),
    "enhance",
    "standard",
)

DARK_SOUP = _add(
    ImageDescriptor(
        id="dark-soup",
        merchant="Copper Ladle",
        dish_name="Tomato Soup",
        stated_count=None,
        observed_count=None,
        objects=("soup", "bread"),
        sharpness=0.80,
        composition=0.80,
        color=0.30,
        plating=0.80,
        brand_tokens=("copper-stamp",),
    ),
    "enhance",
    "standard",
)

OFFCENTER_PIZZA = _add(
    ImageDescriptor(
        id="offcenter-pizza",
        merchant="Maple & Thyme",
        dish_name="Margherita Pizza",
        stated_count=None,
        observed_count=None,
        objects=("pizza",),
        sharpness=0.80,
        composition=0.45,
        color=0.80,
        plating=0.80,
        brand_tokens=("maple-leaf-mark",),
    ),
    "enhance",
    "standard",  # gold tier differs from the router's lite: boundary case
)

MESSY_PASTA = _add(
    ImageDescriptor(
        id="messy-pasta",
        merchant="The Rustic Board",
        dish_name="Pesto Pasta",
        stated_count=None,
        observed_count=None,
        objects=("pasta", "basil"),
        sharpness=0.80,
        composition=0.80,
        color=0.80,
        plating=0.40,
        brand_tokens=("rustic-board-mark",),
    ),
    "enhance",
    "standard",
)

TERRIBLE_TAKEAWAY = _add(
    ImageDescriptor(
        id="terrible-takeaway",
        merchant="Emberline Kitchen",
        dish_name="Chicken Plate",
        stated_count=None,
        observed_count=None,
        objects=("chicken", "rice"),
        sharpness=0.25,
        composition=0.30,
        color=0.35,
        plating=0.20,
        brand_tokens=("emberline-logo",),
    ),
    "enhance",
    "pro",
)

BORDERLINE_BOWL = _add(
    ImageDescriptor(
        id="borderline-bowl",
        merchant="Juniper Table",
        dish_name="Grain Bowl",
        stated_count=None,
        observed_count=None,
        objects=("bowl", "grains"),
        sharpness=0.62,
        composition=0.65,
        color=0.63,
        plating=0.64,
        brand_tokens=("juniper-mark",),
    ),
    "enhance",  # gold says enhance (worst 0.62 < 0.65); router rubric says skip
    "lite",
)

ARTISTIC_DESSERT = _add(
    ImageDescriptor(
        id="artistic-dessert",
        merchant="Saffron Lantern",
        dish_name="Chocolate Fondant",
        stated_count=None,
        observed_count=None,
        objects=("fondant", "berries"),
        sharpness=0.90,
        composition=0.90,
        color=0.90,
        plating=0.90,
        plating_realistic=False,  # signature stylised presentation
        brand_tokens=("saffron-seal",),
    ),
    "skip",  # gold says skip: the stylisation is the merchant's signature
    None,
)

WINGS_8PC = _add(
    ImageDescriptor(
        id="wings-8pc",
        merchant="Copper Ladle",
        dish_name="8 Piece Chicken Wings",
        stated_count=8,
        observed_count=6,
        objects=("wings", "dip"),
        sharpness=0.85,
        composition=0.85,
        color=0.85,
        plating=0.85,
        brand_tokens=("copper-stamp",),
    ),
    "enhance",
    "standard",
)

WONTONS_8PC = _add(
    ImageDescriptor(
        id="wontons-8pc",
        merchant="Maple & Thyme",
        dish_name="8 Piece Wontons",
        stated_count=8,
        observed_count=None,  # partially out of frame: cannot verify
        objects=("wontons", "dip"),
        sharpness=0.85,
        composition=0.85,
        color=0.85,
        plating=0.85,
        brand_tokens=("maple-leaf-mark",),
    ),
    "enhance",
    "standard",
)

PERFECT_SUSHI = _add(
    ImageDescriptor(
        id="perfect-sushi",
        merchant="The Rustic Board",
        dish_name="Salmon Sushi Set",
        stated_count=8,
        observed_count=8,
        objects=("sushi", "ginger"),
        sharpness=0.95,
        composition=0.95,
        color=0.95,
        plating=0.95,
        brand_tokens=("rustic-board-mark",),
    ),
    "skip",
    None,
)

DIM_RAMEN = _add(
    ImageDescriptor(
        id="dim-ramen",
        merchant="Emberline Kitchen",
        dish_name="Tonkotsu Ramen",
        stated_count=None,
        observed_count=None,
        objects=("ramen", "egg"),
        sharpness=0.50,
        composition=0.85,
        color=0.85,
        plating=0.85,
        brand_tokens=("emberline-logo",),
    ),
    "enhance",
    "lite",
)


def demo_descriptors():
    """All demo fixtures, in a stable order."""
    return [descriptor for descriptor, _, _ in FIXTURES]


def demo_gold():
    """(gold routes, gold tiers) aligned with demo_descriptors()."""
    return (
        [gold_route for _, gold_route, _ in FIXTURES],
        [gold_tier for _, _, gold_tier in FIXTURES],
    )
