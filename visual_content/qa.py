"""Multi-dimensional QA gate for enhanced candidates.

Each dimension is an independent pass/fail with a reason, so a rejection
says exactly what was wrong. The gate fails closed: a missing candidate,
a missing score, or an unverifiable count that an edit tries to assert
all fail rather than slipping through. Counts are a safety property, not
a quality score: editing can never repair a count mismatch, so a photo
whose count disagrees with the menu fails QA on every iteration and is
withheld (a coverage hit) instead of being published with invented items.
"""

from __future__ import annotations

from dataclasses import dataclass

from .descriptors import ImageDescriptor

QA_FLOOR = 0.7


@dataclass(frozen=True)
class DimensionResult:
    name: str
    passed: bool
    reason: str

    @property
    def failure_class(self):
        return None if self.passed else self.name


@dataclass(frozen=True)
class QAResult:
    candidate_id: str
    dimensions: tuple

    @property
    def passed(self):
        return all(d.passed for d in self.dimensions)

    @property
    def reasons(self):
        return tuple(d.reason for d in self.dimensions if not d.passed)

    @property
    def failure_classes(self):
        return tuple(d.failure_class for d in self.dimensions if not d.passed)


def _missing_candidate() -> QAResult:
    return QAResult(
        "missing",
        (DimensionResult("candidate", False, "missing_candidate"),),
    )


def qa_gate(original: ImageDescriptor, candidate, failed_criteria=()) -> QAResult:
    """Judge an enhanced candidate against the original photo."""
    if candidate is None:
        return _missing_candidate()
    dims = []

    # Plating: good enough and physically plausible in presentation.
    if candidate.plating >= QA_FLOOR and candidate.plating_realistic:
        dims.append(DimensionResult("plating", True, "plating acceptable"))
    else:
        dims.append(
            DimensionResult(
                "plating",
                False,
                f"plating_below_floor: plating={candidate.plating:.2f} realistic={candidate.plating_realistic}",
            )
        )

    # Faithfulness: the edit must not invent objects.
    added = sorted(set(candidate.objects) - set(original.objects))
    if not added:
        dims.append(DimensionResult("faithfulness", True, "no objects added"))
    else:
        dims.append(
            DimensionResult("faithfulness", False, f"added_object:{','.join(added)}")
        )

    # Colors: good enough and still natural (not oversaturated).
    if candidate.color >= QA_FLOOR and candidate.color_natural:
        dims.append(DimensionResult("colors", True, "colors acceptable"))
    else:
        dims.append(
            DimensionResult(
                "colors",
                False,
                f"colors_below_floor: color={candidate.color:.2f} natural={candidate.color_natural}",
            )
        )

    # Completeness: the edit must not remove objects.
    removed = sorted(set(original.objects) - set(candidate.objects))
    if not removed:
        dims.append(DimensionResult("completeness", True, "no objects removed"))
    else:
        dims.append(
            DimensionResult("completeness", False, f"removed_object:{','.join(removed)}")
        )

    # Naturalness: no genericization, no physically incoherent occlusion.
    genericized = (
        original.plating_style != "generic" and candidate.plating_style == "generic"
    )
    if not genericized and not candidate.plate_covers_sauce:
        dims.append(DimensionResult("naturalness", True, "natural presentation"))
    elif genericized:
        dims.append(
            DimensionResult("naturalness", False, "oversteer: distinctive plating replaced by generic plating")
        )
    else:
        dims.append(
            DimensionResult("naturalness", False, "incoherent: plate covers the sauce")
        )

    # Count: never guess. When the menu claims a count, an unverifiable
    # original count must stay unverified, and a known count must not
    # change. When the menu claims nothing, count is not a fidelity axis.
    if original.stated_count is None and original.observed_count is None:
        dims.append(DimensionResult("count", True, "no count claim to verify"))
    elif original.observed_count is None:
        if candidate.observed_count is None:
            dims.append(DimensionResult("count", True, "count still unverified, nothing asserted"))
        else:
            dims.append(
                DimensionResult("count", False, "count_unverifiable: edit asserts a count the photo cannot confirm")
            )
    elif candidate.observed_count != original.observed_count:
        dims.append(
            DimensionResult("count", False, f"count_changed: {original.observed_count} -> {candidate.observed_count}")
        )
    elif original.stated_count is not None and original.observed_count != original.stated_count:
        dims.append(
            DimensionResult("count", False, "count_mismatch: photo count disagrees with the menu")
        )
    else:
        dims.append(DimensionResult("count", True, "count consistent"))

    # Remediation: the criteria the router flagged must now actually pass.
    # Count criteria can never be remediated by editing.
    if not failed_criteria:
        dims.append(DimensionResult("remediation", True, "no remediation required"))
    else:
        unmet = []
        for criterion in failed_criteria:
            if criterion == "count":
                unmet.append("count cannot be fixed by editing")
            else:
                score = candidate.quality.get(criterion)
                if score is None or score < QA_FLOOR:
                    unmet.append(f"{criterion} still below floor")
        if unmet:
            dims.append(DimensionResult("remediation", False, "remediation_failed: " + "; ".join(unmet)))
        else:
            dims.append(DimensionResult("remediation", True, "flagged criteria remediated"))

    return QAResult(candidate.id, tuple(dims))
