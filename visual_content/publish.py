"""Publish-ready QA: the redundant final gate (Swiss-cheese pattern).

The QA gate checks edit quality; publish QA independently re-checks
policy, identity, and a stricter quality floor, and it never trusts the
QA gate's verdict -- it takes only (original, candidate) and derives
everything itself, so there is no verdict to forge or bypass. Layers
overlap on purpose: a failure that slips past one layer should be
caught by the next. Anything publish QA catches is measured as leakage
(it reached the final gate); anything it misses would be published, and
the pipeline rollup counts that separately.
"""

from __future__ import annotations

from dataclasses import dataclass

from .descriptors import ImageDescriptor

PUBLISH_FLOOR = 0.75


@dataclass(frozen=True)
class PublishResult:
    decision: str  # "publish" or "reject"
    reasons: tuple
    failure_classes: tuple

    @property
    def published(self):
        return self.decision == "publish"


def publish_qa(original: ImageDescriptor, candidate, variant: str) -> PublishResult:
    """Final holistic gate. ``variant`` is "enhanced" or "original".
    The stricter quality floor applies only to enhanced candidates: an
    original photo is judged on policy and identity, not on whether it
    is beautiful, because the alternative is no photo at all."""
    if candidate is None:
        return PublishResult("reject", ("missing_candidate",), ("candidate",))
    failures = []

    if tuple(candidate.brand_tokens) != tuple(original.brand_tokens):
        failures.append(("brand", "brand_changed: merchant brand tokens differ"))
    if candidate.dish_name != original.dish_name:
        failures.append(("dish", "dish_changed: dish identity differs"))
    if candidate.overlay_text not in (None, original.overlay_text):
        failures.append(("overlay", "new_overlay_text: edit added menu text"))
    if candidate.policy_flags:
        failures.append(("policy", f"policy_flag:{','.join(candidate.policy_flags)}"))
    if original.observed_count is None:
        if original.stated_count is not None and candidate.observed_count is not None:
            failures.append(("count", "count_asserted_unverified"))
    elif candidate.observed_count != original.observed_count:
        failures.append(("count", "count_changed"))
    if variant == "enhanced":
        below = [k for k, v in candidate.quality.items() if v < PUBLISH_FLOOR]
        if below:
            failures.append(("publish_floor", f"below_publish_floor: {','.join(below)}"))

    if failures:
        return PublishResult(
            "reject",
            tuple(reason for _, reason in failures),
            tuple(cls for cls, _ in failures),
        )
    return PublishResult("publish", ("all publish checks pass",), ())
