"""End-to-end pipeline: describe -> route -> edit loop -> publish QA.

One flat JSON record per run holds every agent's inputs, outputs, and
decisions in a single level of keys, so anyone -- technical or not --
can read one run without chasing nested structures. The rollup
aggregates runs: routes, pass@K, coverage hits, leakage, and published
variants. A "coverage hit" means enhancement was withheld and the
original went to publish QA instead; "leakage" means a candidate passed
the QA gate but failed publish QA (it reached the final gate).
"""

from __future__ import annotations

from .describe import FakeVision
from .descriptors import ImageDescriptor
from .edit import edit
from .pairwise import pairwise_compare
from .prompts import generate_prompt
from .publish import publish_qa
from .qa import qa_gate
from .router import decide

VISION = FakeVision()


def run_pipeline(descriptor: ImageDescriptor, max_iterations: int = 3) -> dict:
    """Run one photo end to end and return its flat run record."""
    description = VISION.describe(descriptor)
    decision = decide(description)
    record = {
        "run_id": f"run-{descriptor.id}",
        "merchant": descriptor.merchant,
        "dish": descriptor.dish_name,
        "route": decision.route,
        "tier": decision.tier or "",
        "tier_cost_usd": _tier_cost(decision.tier),
        "count_unverified": decision.count_unverified,
        "iterations": 0,
        "qa_pass_iteration": None,
        "qa_passed": False,
        "coverage_hit": False,
        "pairwise_verdict": "",
        "publish_decision": "",
        "published_variant": "",
        "qa_reasons": [],
        "publish_reasons": [],
        "failure_classes": [],
    }
    if decision.route == "skip":
        result = publish_qa(descriptor, descriptor, "original")
        record["publish_decision"] = result.decision
        record["published_variant"] = "original" if result.published else "none"
        record["publish_reasons"] = list(result.reasons)
        record["failure_classes"] = list(result.failure_classes)
        return record

    current = descriptor
    feedback: list = []
    qa_result = None
    for iteration in range(1, max_iterations + 1):
        prompt = generate_prompt(description, decision.directives, feedback)
        current = edit(current, decision.directives)
        qa_result = qa_gate(descriptor, current, decision.failed_criteria)
        record["iterations"] = iteration
        if qa_result.passed:
            record["qa_passed"] = True
            record["qa_pass_iteration"] = iteration
            break
        feedback.extend(qa_result.reasons)
    record["qa_reasons"] = list(qa_result.reasons) if qa_result else []

    if not record["qa_passed"]:
        record["coverage_hit"] = True
        record["failure_classes"] = sorted(set(qa_result.failure_classes))
        result = publish_qa(descriptor, descriptor, "original")
        record["publish_decision"] = result.decision
        record["published_variant"] = "original" if result.published else "none"
        record["publish_reasons"] = list(result.reasons)
        record["failure_classes"] = sorted(
            set(record["failure_classes"]) | set(result.failure_classes)
        )
        return record

    verdict = pairwise_compare(descriptor, current)
    record["pairwise_verdict"] = verdict.verdict
    result = publish_qa(descriptor, current, "enhanced")
    record["publish_decision"] = result.decision
    if result.published:
        record["published_variant"] = "enhanced"
    else:
        # Final-gate rejection falls back to the original photo.
        fallback = publish_qa(descriptor, descriptor, "original")
        record["publish_decision"] = fallback.decision
        record["published_variant"] = "original" if fallback.published else "none"
        record["publish_reasons"] = list(result.reasons) + list(fallback.reasons)
        record["failure_classes"] = sorted(set(result.failure_classes))
        return record
    record["publish_reasons"] = list(result.reasons)
    record["failure_classes"] = list(result.failure_classes)
    return record


def _tier_cost(tier):
    from .router import TIERS

    return TIERS[tier].cost_usd if tier else 0.0


def pass_at_k(records, max_iterations: int = 3) -> list:
    """Cumulative pass rate by iteration over enhanced attempts only."""
    attempts = [r for r in records if r["route"] == "enhance"]
    curve = []
    for k in range(1, max_iterations + 1):
        passed = sum(
            1
            for r in attempts
            if r["qa_pass_iteration"] is not None and r["qa_pass_iteration"] <= k
        )
        curve.append(round(passed / len(attempts), 3) if attempts else 0.0)
    return curve


def rollup(records, max_iterations: int = 3) -> dict:
    """Aggregate rollup over flat run records."""
    by_route = {}
    for record in records:
        by_route[record["route"]] = by_route.get(record["route"], 0) + 1
    failure_counts: dict = {}
    for record in records:
        for cls in record["failure_classes"]:
            failure_counts[cls] = failure_counts.get(cls, 0) + 1
    enhanced = [r for r in records if r["route"] == "enhance"]
    leakage = sum(
        1
        for r in enhanced
        if r["qa_passed"] and r["published_variant"] == "original"
    )
    published_bad = sum(
        1
        for r in records
        if r["published_variant"] == "enhanced" and r["failure_classes"]
    )
    return {
        "runs": len(records),
        "by_route": by_route,
        "pass_at_k": pass_at_k(records, max_iterations),
        "coverage_hits": sum(1 for r in records if r["coverage_hit"]),
        "leakage_reached_publish_qa": leakage,
        "published_bad": published_bad,
        "published_enhanced": sum(
            1 for r in records if r["published_variant"] == "enhanced"
        ),
        "published_original": sum(
            1 for r in records if r["published_variant"] == "original"
        ),
        "published_none": sum(1 for r in records if r["published_variant"] == "none"),
        "failure_class_counts": failure_counts,
        "total_edit_cost_usd": round(
            sum(r["tier_cost_usd"] for r in enhanced), 2
        ),
    }
