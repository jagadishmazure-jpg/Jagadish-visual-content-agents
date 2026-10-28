"""Fake vision backend: descriptor -> structured description.

This stands in for a multimodal model that looks at a photo and describes
it. It is deterministic and offline: it derives the description from the
descriptor's own fields, so every behaviour in this repo is reproducible
without any model, key, or network call. The README and limitations doc
say this plainly.
"""

from __future__ import annotations

from dataclasses import dataclass

from .descriptors import ImageDescriptor

RUBRIC_THRESHOLD = 0.6


@dataclass(frozen=True)
class Description:
    descriptor_id: str
    merchant: str
    dish_name: str
    stated_count: int | None
    observed_count: int | None
    count_verifiable: bool
    objects: tuple
    quality: dict
    plating_realistic: bool
    plating_style: str
    color_natural: bool
    plate_covers_sauce: bool
    brand_tokens: tuple
    overlay_text: str | None
    policy_flags: tuple
    issues: tuple


class FakeVision:
    """Deterministic stand-in for an image-understanding model."""

    def describe(self, descriptor: ImageDescriptor) -> Description:
        issues = []
        quality = descriptor.quality
        if descriptor.sharpness < RUBRIC_THRESHOLD:
            issues.append("low_sharpness")
        if descriptor.composition < RUBRIC_THRESHOLD:
            issues.append("poor_composition")
        if descriptor.color < RUBRIC_THRESHOLD:
            issues.append("poor_color")
        if descriptor.plating < RUBRIC_THRESHOLD:
            issues.append("poor_plating")
        if not descriptor.plating_realistic:
            issues.append("unrealistic_plating")
        if descriptor.plate_covers_sauce:
            issues.append("plate_covers_sauce")
        # A count only needs verifying when the menu actually claims one.
        if descriptor.stated_count is not None and descriptor.observed_count is None:
            issues.append("count_unverifiable")
        elif (
            descriptor.stated_count is not None
            and descriptor.observed_count is not None
            and descriptor.observed_count != descriptor.stated_count
        ):
            issues.append("count_mismatch")
        return Description(
            descriptor_id=descriptor.id,
            merchant=descriptor.merchant,
            dish_name=descriptor.dish_name,
            stated_count=descriptor.stated_count,
            observed_count=descriptor.observed_count,
            count_verifiable=descriptor.stated_count is None
            or descriptor.observed_count is not None,
            objects=descriptor.objects,
            quality=dict(quality),
            plating_realistic=descriptor.plating_realistic,
            plating_style=descriptor.plating_style,
            color_natural=descriptor.color_natural,
            plate_covers_sauce=descriptor.plate_covers_sauce,
            brand_tokens=descriptor.brand_tokens,
            overlay_text=descriptor.overlay_text,
            policy_flags=descriptor.policy_flags,
            issues=tuple(issues),
        )
