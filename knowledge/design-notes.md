# Design notes: visual-content agents for a food marketplace

Distilled design notes for this repo, written in our own words. The
fictional setting is Savorlane, a food-delivery marketplace whose small
independent merchants upload phone photos of uneven quality. A photo is
often the first thing a customer sees, so photo quality moves orders --
but only if the photo stays honest.

## The problem, in one paragraph

Small merchants lack time, photography know-how, and budget for
professional shoots, and menus change often, so photos drift out of
date. Customers want photos that look like what will actually arrive,
and a meaningful share of them distrust anything that looks
machine-made. So enhancement must thread a needle: improve quality
selectively, stay faithful to the original dish, preserve each
merchant's brand, and never make every photo look the same.

## Design principles

1. **Authenticity before beauty.** An edit that invents, removes, or
   restyles the dish is a failure even if the result looks prettier.
   Faithfulness and completeness are gates, not preferences.
2. **Improve selectively, optimise globally.** Only photos that fail
   the rubric are enhanced. A good photo is skipped, not "improved",
   because editing a good photo costs compute and risks degrading it.
   Decisions must not cannibalise one merchant for another.
3. **Ship safely, in layers.** No single gate is trusted. The edit loop
   has its own QA gate, and publish has a second, independent gate that
   re-checks policy, identity, and a stricter quality floor. Layers
   overlap on purpose (the Swiss-cheese pattern): a failure that slips
   past one layer should be caught by the next.
4. **Every decision is measured.** The router is evaluated as a
   classifier (confusion matrix, precision, recall). The guardrail
   metric is recall on the "needs enhancement" class: approving a bad
   photo as-is is worse than enhancing a good one, because the bad
   photo stays on the menu. The edit loop is measured as pass@K: the
   share of attempts passing QA by iteration K.
5. **Diversity is a feature.** One shared prompt for every photo would
   collapse the marketplace into a single look. Prompts are generated
   per photo from that photo's description and its QA feedback, and a
   diversity check proves they differ.
6. **Never guess a count.** If the menu claims eight pieces and the
   photo shows six -- or the count cannot be verified at all -- the
   system must not invent items to match the menu. Enhancement is
   withheld (a coverage hit) and the original photo is kept.
7. **Log first, optimise second.** Every run produces one flat JSON
   record holding each agent's inputs, outputs, and decisions, plus an
   aggregate rollup. Without that log there is nothing to diagnose, no
   aggregate to learn from, and no feedback loop to build later.
8. **Cost is a routing dimension.** Photos are routed to edit tiers
   that trade cost against latency against quality. Tier prices in
   this repo are illustrative demo prices for fake tiers, not vendor
   prices, and cost inputs reject negatives.

## What "better" means

A pairwise judge compares input and output on four criteria --
faithful (nothing invented), complete (nothing removed), natural (not
genericised, colours still believable), realistic (physically coherent,
no occluded sauce) -- plus whether quality actually improved by a
meaningful margin. Verdicts are yes, no, or unsure. "Unsure" covers two
honest cases: the change is too small to count (a nugatory change), and
fidelity cannot be confirmed (an unverifiable count). Neither is
reported as a win.

## Known failure modes, kept as tests

- Added object (faithfulness), removed object (completeness).
- Oversteering: a creative edit is rejected, the next iteration falls
  back to a generic look -- pixels differ, nothing meaningful improves.
- Object incoherence: a plate drawn over the sauce it should accompany.
- Count uncertainty: the item count cannot be verified, so the photo
  is rejected rather than "completed" by invention.
- Good photo sent for enhancement: wasted compute plus degradation
  risk -- the router's false positives.
- Bad photo approved as-is: the recall miss, the guardrail failure.
