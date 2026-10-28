# ADR 001: Fake vision/edit backends over synthetic descriptors

## Status

Accepted.

## Context

This repo demonstrates routing, QA gating, pairwise eval, publish
gating, and loop measurement for marketplace photo enhancement. Real
image models would need API keys, per-call spend, and non-deterministic
outputs, which would make the suite unreproducible and the numbers
unverifiable in CI.

## Decision

- Photos are represented by synthetic descriptors (scores, counts,
  objects, brand tokens, style flags).
- The vision backend derives descriptions from descriptor fields.
- The editor applies bounded score steps per directive and never
  touches identity, objects, counts, style, or brand.
- All demo numbers come from running this deterministic code.

## Consequences

- The suite is fully reproducible offline with stdlib only.
- The repo proves pipeline machinery, not photo-editing quality.
  That boundary is stated in the README, the limitations doc, and the
  interview points, and must stay stated if real-model adapters are
  ever added (planned, optional, needs key and cost approval).
- Failure modes that only real models exhibit (hallucinated texture,
  distorted text) are represented by crafted fixtures, not observed.
