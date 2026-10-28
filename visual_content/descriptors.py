"""Synthetic image descriptors.

A descriptor is a structured stand-in for a food photo: the numbers and
labels a vision backend would report about it. No real images are read,
stored, or edited anywhere in this repo. Every descriptor below is
invented fixture data for a fictional marketplace.
"""

from __future__ import annotations

import math
from dataclasses import dataclass


def _score(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{name} must be a number, got {value!r}")
    value = float(value)
    if math.isnan(value) or not 0.0 <= value <= 1.0:
        raise ValueError(f"{name} must be between 0 and 1, got {value!r}")
    return value


def _count(value, name):
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{name} must be an int or None, got {value!r}")
    if value < 0:
        raise ValueError(f"{name} must be >= 0, got {value!r}")
    return value


@dataclass(frozen=True)
class ImageDescriptor:
    """Structured stand-in for one merchant menu photo.

    Quality scores are 0..1 (higher is better). ``observed_count`` is None
    when the item count cannot be verified from the photo itself -- the
    system must never guess a count in that case. ``brand_tokens`` are the
    merchant's identity markers (logo text, packaging marks, signature
    plating cues); edits must never change them.
    """

    id: str
    merchant: str
    dish_name: str
    stated_count: int | None  # menu claim, e.g. 8 pieces; None if no claim
    observed_count: int | None  # counted in the photo; None = unverifiable
    objects: tuple = ()
    sharpness: float = 1.0
    composition: float = 1.0
    color: float = 1.0
    plating: float = 1.0
    plating_realistic: bool = True
    plating_style: str = "house"  # "house" (merchant's own) or "generic"
    color_natural: bool = True
    plate_covers_sauce: bool = False
    brand_tokens: tuple = ()
    overlay_text: str | None = None
    policy_flags: tuple = ()

    def __post_init__(self):
        object.__setattr__(self, "sharpness", _score(self.sharpness, "sharpness"))
        object.__setattr__(self, "composition", _score(self.composition, "composition"))
        object.__setattr__(self, "color", _score(self.color, "color"))
        object.__setattr__(self, "plating", _score(self.plating, "plating"))
        object.__setattr__(self, "stated_count", _count(self.stated_count, "stated_count"))
        object.__setattr__(self, "observed_count", _count(self.observed_count, "observed_count"))
        object.__setattr__(self, "objects", tuple(self.objects))
        object.__setattr__(self, "brand_tokens", tuple(self.brand_tokens))
        object.__setattr__(self, "policy_flags", tuple(self.policy_flags))

    @property
    def quality(self):
        return {
            "sharpness": self.sharpness,
            "composition": self.composition,
            "color": self.color,
            "plating": self.plating,
        }

    @property
    def mean_quality(self):
        values = self.quality.values()
        return sum(values) / len(values)
