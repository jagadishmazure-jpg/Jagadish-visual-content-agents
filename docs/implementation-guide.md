# Implementation guide

## Run it

```bash
python3 -m pytest tests -q        # full suite
python3 scripts/render_demo.py    # demo numbers (copy into README, never hand-edit)
python3 scripts/count_tests.py    # real test total
python3 scripts/brand_check.py    # fictional-names guard (hashed blocklist)
```

Stdlib only. No keys, no network, no model calls. Python 3.12.

## Add a new photo fixture

1. Add an `ImageDescriptor` in `visual_content/fixtures.py` with a
   hand-assigned gold route and gold tier. If you disagree with the
   router rubric, say so in a comment -- boundary disagreements are
   the point of the eval, not noise to hide.
2. Run the demo and update the README numbers from its output.
3. If the photo exercises a new failure mode, add a taxonomy test
   with a failing fixture and a passing control.

## Add a new QA dimension

1. Add the dimension in `qa_gate` with a pass/fail reason and a
   failure class.
2. Add pass, fail, and missing-data (fail-closed) tests.
3. If publish QA should also check it, add it there independently --
   publish QA never trusts QA's verdict.

## Add a new edit tier

Add a `ModelTier` to `TIERS` with a non-negative cost and latency.
Costs are validated: negative cost or latency raises `ValueError`.
Update the tier-matrix test expectations from the demo output.

## Extend the pipeline

- Change `max_iterations` (default 3) to move the pass@K curve.
- The editor only moves scores listed in `DIRECTIVE_FIELDS`. A
  directive with no field (like `verify_count`) is deliberately a
  no-op: some things must not be "fixed" by editing.
- Publish QA's stricter floor (`PUBLISH_FLOOR = 0.75` vs QA's `0.70`)
  is what creates the measurable leakage band. Do not collapse the
  two floors without removing the leakage measurement too.
