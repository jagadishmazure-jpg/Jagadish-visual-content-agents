"""Public package surface for the visual-content pipeline."""

from .describe import Description, FakeVision
from .descriptors import ImageDescriptor
from .edit import edit
from .pairwise import PairwiseVerdict, pairwise_compare
from .pipeline import pass_at_k, rollup, run_pipeline
from .prompts import diversity_report, generate_prompt
from .publish import PublishResult, publish_qa
from .qa import QAResult, qa_gate
from .router import (
    TIERS,
    ConfusionMatrix,
    RouteDecision,
    decide,
    evaluate_router,
    evaluate_tiers,
    grade,
)

__all__ = [
    "Description",
    "FakeVision",
    "ImageDescriptor",
    "edit",
    "PairwiseVerdict",
    "pairwise_compare",
    "pass_at_k",
    "rollup",
    "run_pipeline",
    "diversity_report",
    "generate_prompt",
    "PublishResult",
    "publish_qa",
    "QAResult",
    "qa_gate",
    "TIERS",
    "ConfusionMatrix",
    "RouteDecision",
    "decide",
    "evaluate_router",
    "evaluate_tiers",
    "grade",
]
