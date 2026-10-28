"""Render demo numbers from real runs (router eval + pipeline + prompts).

Every figure printed here comes from executing the code in this repo
over the synthetic fixture set. Copy these numbers into the README;
never hand-edit them.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from visual_content import FakeVision, decide, diversity_report, evaluate_router, evaluate_tiers, generate_prompt, rollup, run_pipeline
from visual_content.fixtures import demo_descriptors, demo_gold

VISION = FakeVision()


def main():
    descriptors = demo_descriptors()
    gold_routes, gold_tiers = demo_gold()
    decisions = [decide(VISION.describe(d)) for d in descriptors]
    matrix = evaluate_router(decisions, gold_routes)
    tiers = evaluate_tiers([d.tier for d in decisions], gold_tiers)
    records = [run_pipeline(d) for d in descriptors]
    summary = rollup(records)
    prompts = [
        generate_prompt(VISION.describe(d), dec.directives)
        for d, dec in zip(descriptors, decisions)
    ]
    diversity = diversity_report(prompts)

    print(f"demo fixtures: {len(descriptors)}")
    print(f"router confusion: TP={matrix.tp} FP={matrix.fp} FN={matrix.fn} TN={matrix.tn}")
    print(f"router precision: {matrix.precision:.3f}")
    print(f"router recall (guardrail): {matrix.recall:.3f}")
    print(f"router accuracy: {matrix.accuracy:.3f}")
    print(f"tier accuracy: {tiers['tier_accuracy']:.3f} over {tiers['n']} routed items")
    print("tier matrix (gold, predicted) -> count:")
    for key in sorted(tiers["matrix"]):
        print(f"  {key}: {tiers['matrix'][key]}")
    for tier, values in sorted(tiers["per_tier"].items()):
        print(f"  tier {tier}: precision={values['precision']:.3f} recall={values['recall']:.3f}")
    print(f"pipeline routes: {summary['by_route']}")
    print(f"pass@K: {summary['pass_at_k']}")
    print(f"coverage hits: {summary['coverage_hits']}")
    print(f"leakage reached publish QA: {summary['leakage_reached_publish_qa']}")
    print(f"published enhanced: {summary['published_enhanced']}")
    print(f"published original: {summary['published_original']}")
    print(f"published none: {summary['published_none']}")
    print(f"published bad: {summary['published_bad']}")
    print(f"failure classes: {summary['failure_class_counts']}")
    print(f"total edit cost (demo tier prices): ${summary['total_edit_cost_usd']:.2f}")
    print(
        f"prompt diversity: {diversity['unique']}/{diversity['prompts']} unique, "
        f"max similarity {diversity['max_pairwise_similarity']}, passed={diversity['passed']}"
    )


if __name__ == "__main__":
    main()
