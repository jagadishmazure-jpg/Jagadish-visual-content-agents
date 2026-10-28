"""Pairwise generation eval: is the output actually better than the input?

The judge compares the original photo with the enhanced candidate on
four criteria -- faithful, complete, natural, realistic -- plus the
improvement itself. The verdict is "yes" (better), "no" (worse on some
criterion), or "unsure" (cannot tell, or the change is too small to
count). "Unsure" is a real verdict, not a shrug: a nugatory change that
moves pixels without meaningfully improving the photo must not be
reported as a win, and a count that cannot be verified must not be
guessed in either direction.
"""

from __future__ import annotations

from dataclasses import dataclass

from .descriptors import ImageDescriptor

MEANINGFUL_DELTA = 0.05


@dataclass(frozen=True)
class PairwiseVerdict:
    verdict: str  # "yes", "no", or "unsure"
    reasons: tuple


def pairwise_compare(original: ImageDescriptor, edited: ImageDescriptor) -> PairwiseVerdict:
    added = sorted(set(edited.objects) - set(original.objects))
    if added:
        return PairwiseVerdict("no", (f"faithfulness: added {','.join(added)}",))
    removed = sorted(set(original.objects) - set(edited.objects))
    if removed:
        return PairwiseVerdict("no", (f"completeness: removed {','.join(removed)}",))
    if edited.plate_covers_sauce and not original.plate_covers_sauce:
        return PairwiseVerdict("no", ("realism: plate covers the sauce",))
    if original.observed_count is not None and edited.observed_count != original.observed_count:
        return PairwiseVerdict("no", ("count: edited count differs from the photo",))
    if original.stated_count is not None and original.observed_count is None:
        return PairwiseVerdict("unsure", ("count: claimed count unverifiable, fidelity cannot be confirmed",))
    if original.plating_style != "generic" and edited.plating_style == "generic":
        return PairwiseVerdict("unsure", ("naturalness: distinctive plating replaced by generic plating",))
    delta = edited.mean_quality - original.mean_quality
    if delta < MEANINGFUL_DELTA:
        return PairwiseVerdict(
            "unsure", (f"nugatory: mean quality delta {delta:.3f} below {MEANINGFUL_DELTA}",)
        )
    return PairwiseVerdict("yes", (f"better: mean quality delta {delta:.3f}",))
