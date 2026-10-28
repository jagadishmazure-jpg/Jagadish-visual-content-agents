"""Rubric router: enhance/skip decisions, model tiers, and router eval.

The router grades a description against a fixed rubric. Any failed
criterion routes the photo to enhancement; a photo that passes everything
is skipped and the original is kept. The guardrail metric is RECALL on
the "needs enhancement" class: a bad photo approved as-is (a false
negative) is the failure to minimise, because a skipped bad photo stays
on the menu while an unnecessarily enhanced photo only costs compute.

The router also assigns an edit tier trading cost vs latency vs quality.
Tier prices below are illustrative demo prices for the fake tiers, not
vendor prices. Cost and latency inputs must be non-negative.
"""

from __future__ import annotations

from dataclasses import dataclass

from .describe import Description, RUBRIC_THRESHOLD

# Criterion name -> description quality key (None = non-score criterion).
CRITERIA = (
    ("sharpness", "sharpness"),
    ("composition", "composition"),
    ("color", "color"),
    ("plating", "plating"),
)


@dataclass(frozen=True)
class ModelTier:
    name: str
    cost_usd: float
    latency_s: float
    quality_rank: int

    def __post_init__(self):
        if self.cost_usd < 0:
            raise ValueError(f"tier cost must be >= 0, got {self.cost_usd!r}")
        if self.latency_s < 0:
            raise ValueError(f"tier latency must be >= 0, got {self.latency_s!r}")


# Illustrative demo prices for the fake tiers (not vendor prices).
TIERS = {
    "lite": ModelTier("lite", 0.02, 2.0, 1),
    "standard": ModelTier("standard", 0.08, 8.0, 2),
    "pro": ModelTier("pro", 0.25, 25.0, 3),
}


@dataclass(frozen=True)
class CriterionResult:
    name: str
    passed: bool
    detail: str


@dataclass(frozen=True)
class RouteDecision:
    route: str  # "enhance" or "skip"
    tier: str | None
    criteria: tuple
    directives: tuple
    count_unverified: bool

    @property
    def failed_criteria(self):
        return tuple(c.name for c in self.criteria if not c.passed)


def grade(description: Description) -> tuple:
    """Grade every rubric criterion; a missing score fails closed."""
    results = []
    for name, key in CRITERIA:
        score = description.quality.get(key)
        if score is None:
            results.append(CriterionResult(name, False, f"{name} score missing"))
        elif name == "plating":
            ok = score >= RUBRIC_THRESHOLD and description.plating_realistic
            results.append(
                CriterionResult(name, ok, f"plating={score:.2f} realistic={description.plating_realistic}")
            )
        else:
            results.append(
                CriterionResult(name, score >= RUBRIC_THRESHOLD, f"{name}={score:.2f}")
            )
    if description.stated_count is None:
        # No menu claim: there is no count to verify.
        results.append(CriterionResult("count", True, "no count claimed"))
    elif not description.count_verifiable:
        results.append(CriterionResult("count", False, "item count cannot be verified"))
    elif description.observed_count != description.stated_count:
        results.append(
            CriterionResult(
                "count",
                False,
                f"observed={description.observed_count} stated={description.stated_count}",
            )
        )
    else:
        results.append(CriterionResult("count", True, "count matches the menu"))
    return tuple(results)


def _tier_for(criteria) -> str:
    """Worst quality deficit picks the tier; count-only failure is standard."""
    deficits = [
        RUBRIC_THRESHOLD - c_detail_score
        for c_detail_score in _failing_scores(criteria)
    ]
    if not deficits:
        return "standard"  # only a count criterion failed
    worst = max(deficits)
    if worst <= 0.15:
        return "lite"
    if worst <= 0.35:
        return "standard"
    return "pro"


def _failing_scores(criteria):
    # Recover failing quality scores from criterion details ("name=0.35").
    scores = []
    for criterion in criteria:
        if criterion.passed or criterion.name == "count":
            continue
        try:
            scores.append(float(criterion.detail.split("=")[1].split()[0]))
        except (IndexError, ValueError):
            continue
    return scores


_DIRECTIVES = {
    "sharpness": "improve_sharpness",
    "composition": "recenter_composition",
    "color": "restore_natural_color",
    "plating": "improve_plating",
    "count": "verify_count",
}


def decide(description: Description) -> RouteDecision:
    criteria = grade(description)
    failed = [c.name for c in criteria if not c.passed]
    count_unverified = (
        description.stated_count is not None and not description.count_verifiable
    )
    if not failed:
        return RouteDecision("skip", None, criteria, (), count_unverified)
    return RouteDecision(
        "enhance",
        _tier_for(criteria),
        criteria,
        tuple(_DIRECTIVES[name] for name in failed),
        count_unverified,
    )


@dataclass(frozen=True)
class ConfusionMatrix:
    tp: int
    fp: int
    fn: int
    tn: int

    @property
    def precision(self):
        denom = self.tp + self.fp
        return self.tp / denom if denom else 0.0

    @property
    def recall(self):
        denom = self.tp + self.fn
        return self.tp / denom if denom else 0.0

    @property
    def accuracy(self):
        total = self.tp + self.fp + self.fn + self.tn
        return (self.tp + self.tn) / total if total else 0.0


def evaluate_router(decisions, gold_routes) -> ConfusionMatrix:
    """Binary enhance/skip eval. Gold "enhance" is the positive class."""
    tp = fp = fn = tn = 0
    for decision, gold in zip(decisions, gold_routes):
        predicted = decision.route == "enhance"
        actual = gold == "enhance"
        if predicted and actual:
            tp += 1
        elif predicted and not actual:
            fp += 1
        elif not predicted and actual:
            fn += 1
        else:
            tn += 1
    return ConfusionMatrix(tp, fp, fn, tn)


def evaluate_tiers(predicted_tiers, gold_tiers):
    """n-by-n routing matrix: (gold tier, predicted tier) -> count, plus
    per-tier precision/recall over the items the router chose to enhance."""
    matrix: dict = {}
    tiers = sorted({t for t in gold_tiers if t} | {t for t in predicted_tiers if t})
    for gold, predicted in zip(gold_tiers, predicted_tiers):
        if gold is None or predicted is None:
            continue
        matrix[(gold, predicted)] = matrix.get((gold, predicted), 0) + 1
    per_tier = {}
    for tier in tiers:
        tp = matrix.get((tier, tier), 0)
        fp = sum(v for (g, p), v in matrix.items() if p == tier and g != tier)
        fn = sum(v for (g, p), v in matrix.items() if g == tier and p != tier)
        per_tier[tier] = {
            "precision": tp / (tp + fp) if (tp + fp) else 0.0,
            "recall": tp / (tp + fn) if (tp + fn) else 0.0,
        }
    correct = sum(v for (g, p), v in matrix.items() if g == p)
    total = sum(matrix.values())
    return {
        "matrix": matrix,
        "per_tier": per_tier,
        "tier_accuracy": correct / total if total else 0.0,
        "n": total,
    }
