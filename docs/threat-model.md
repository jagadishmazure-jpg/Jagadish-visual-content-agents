# Threat model (lightweight)

Applies to the pipeline as built, not to a production deployment.

## Assets

- Merchant photos and brand identity (brand tokens, dish identity).
- Menu truth: dish names, item counts, prices are out of scope here
  except counts, which the pipeline treats as safety-critical.
- The run log: every agent decision, used for diagnosis and tuning.

## Threats and controls

- **Fabricated dish content (spoofing / fraud).** An edit that adds,
  removes, or restyles items misleads customers. Controls: QA
  faithfulness and completeness dimensions, count dimension, publish
  QA brand/dish/overlay checks. Tests: taxonomy fixtures for each.
- **Gate bypass.** Publishing without QA, or with a forged QA pass.
  Control: publish QA takes no QA verdict parameter and derives
  every check itself; the pipeline has no QA-override path. Tests:
  forged-verdict absence (signature test), missing-candidate
  fail-closed, QA-missed brand change caught at publish.
- **Brand impersonation.** An edit that swaps merchant brand tokens.
  Control: brand-token equality at publish QA; editor never touches
  brand tokens. Test: brand-change fixture.
- **Misleading menu text.** An edit that adds promotional overlay
  text. Control: publish QA rejects overlay text the original did
  not have. Test: overlay fixture.
- **Silent quality regression.** A config or threshold change that
  loosens gates. Control: demo numbers are rendered from real runs
  and asserted in tests (router P/R, pass@K, coverage, leakage);
  a loosened gate moves those numbers and fails the suite.
- **Real-company name leakage into the portfolio.** Control:
  `scripts/brand_check.py` scans all repo files against a hashed
  blocklist; a test asserts the blocklist is non-empty and the scan
  is clean.

## Out of scope here

Prompt injection via merchant-supplied text (descriptors carry no free
merchant text in this design), PII in photos (synthetic descriptors
carry none), and any real-model risk (no models run). A production
version would need all three assessed separately.
