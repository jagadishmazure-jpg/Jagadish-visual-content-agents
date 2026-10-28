# Interview points

Sixty-second talk tracks for this repo. Every number below comes from
`scripts/render_demo.py` over the 13-fixture demo set.

## "Why not just enhance every photo?"

Because a good photo sent for enhancement costs compute and can come
back worse. The router exists to skip good photos: on the demo set it
skips 4 of 13 and enhances 9. Its guardrail metric is recall on the
"needs enhancement" class (0.889 here) -- a bad photo approved as-is
stays on the menu, while an unnecessary edit only wastes one edit.

## "How do you know the edit loop works?"

Pass@K: the share of enhanced attempts passing QA by iteration K.
Demo: 0.111 at K=1, 0.556 at K=2, 0.667 at K=3. The curve rises
because QA feedback accumulates into the next prompt. The attempts
that never pass are not forced through: 3 coverage hits, and the
original photo is published instead.

## "What stops a bad edit from reaching customers?"

Two independent gates. The QA gate checks plating, faithfulness,
colors, completeness, naturalness, count, and remediation. Publish QA
re-checks policy, brand, dish identity, overlay text, count, and a
stricter quality floor -- without trusting QA's verdict. Demo
leakage (passed QA, failed publish QA) is 2, both in the 0.70-0.75
band between the two floors, and published-bad is 0.

## "What is the one failure you refuse to fix by editing?"

Counts. If the menu says eight pieces and the photo shows six, or
the count cannot be verified, the system withholds enhancement
rather than inventing items. Editing cannot repair a count mismatch;
only a new photo can.

## Honest boundaries (say these before being asked)

- No real vision models run here. The vision and edit backends are
  deterministic fakes over synthetic descriptors, so this repo proves
  routing, QA, eval, and loop machinery -- not photo editing quality.
- Gold labels are hand-assigned in the fixture file, not collected
  from human labellers. The eval is a regression check on 13
  fixtures, not a quality claim about real photos.
- Tier prices are illustrative demo prices for fake tiers.
