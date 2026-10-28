"""Image-specific prompt generation and the diversity check.

Every enhanced photo gets its own prompt built from that photo's
description plus the router's directives plus accumulated QA feedback.
One shared prompt for every photo is a failure mode: it collapses the
diversity of the marketplace, so the diversity check below proves
prompts actually differ per image.
"""

from __future__ import annotations

from .describe import Description

DIRECTIVE_TEXT = {
    "improve_sharpness": "sharpen details without inventing texture",
    "recenter_composition": "re-center the dish in the frame",
    "restore_natural_color": "restore natural colors without oversaturating",
    "improve_plating": "tidy the plating while keeping the dish itself unchanged",
    "verify_count": "do not add or remove items; keep the item count exactly as photographed",
}


def generate_prompt(description: Description, directives, feedback=()) -> str:
    """Build one prompt specific to this photo. Empty directives still
    yield a prompt (a general-improvement fallback), never a crash."""
    lines = [f"Edit the photo of {description.dish_name} from {description.merchant}:"]
    if directives:
        for directive in directives:
            lines.append(f"- {DIRECTIVE_TEXT.get(directive, directive)}")
    else:
        lines.append("- improve overall photo quality while keeping the dish unchanged")
    for note in feedback:
        lines.append(f"- previous QA feedback to address: {note}")
    lines.append("- keep the merchant's branding, dish identity, and item count unchanged")
    return "\n".join(lines)


def _tokens(text: str) -> set:
    return {word.strip(".,:;") for word in text.lower().split() if word.strip(".,:;")}


def _jaccard(left: set, right: set) -> float:
    if not left and not right:
        return 1.0
    return len(left & right) / len(left | right)


def diversity_report(prompts, threshold: float = 0.9) -> dict:
    """Prove prompts differ per image. Two identical prompts score 1.0
    similarity and fail; genuinely different prompts stay below threshold."""
    token_sets = [_tokens(prompt) for prompt in prompts]
    max_similarity = 0.0
    for i in range(len(token_sets)):
        for j in range(i + 1, len(token_sets)):
            max_similarity = max(max_similarity, _jaccard(token_sets[i], token_sets[j]))
    unique = len(set(prompts))
    return {
        "prompts": len(prompts),
        "unique": unique,
        "max_pairwise_similarity": round(max_similarity, 3),
        "passed": unique == len(prompts) and max_similarity < threshold,
    }
