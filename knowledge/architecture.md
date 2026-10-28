# Architecture

## End-to-end pipeline

```mermaid
flowchart LR
    P["merchant photo\n(synthetic descriptor)"]
    D["describe agent\n(fake vision backend)"]
    R["router\nrubric grade -> enhance / skip"]
    G["prompt generator\nimage-specific prompt"]
    E["edit agent\nbounded fake edit"]
    Q["QA gate\nplating, faithfulness, colors,\ncompleteness, naturalness, count,\nremediation"]
    PQ["publish QA\npolicy, brand, dish, overlay,\ncount, stricter floor"]
    PUB["menu publish"]
    LOG["flat JSON run log\n+ aggregate rollup"]

    P --> D --> R
    R -->|"skip"| PQ
    R -->|"enhance"| G --> E --> Q
    Q -->|"pass"| PQ
    Q -->|"fail, feedback"| G
    Q -->|"K iterations, still failing\n(coverage hit)"| PQ
    PQ -->|"publish"| PUB
    PQ -->|"reject enhanced\n-> original"| PQ
    R --> LOG
    Q --> LOG
    PQ --> LOG
```

## Edit loop (detail)

```mermaid
flowchart LR
    A["router directives\n+ QA feedback"] --> B["prompt generator"]
    B --> C["edit agent\n+0.20 per targeted dimension,\ncapped at 0.95"]
    C --> D["QA gate"]
    D -->|"pass"| E["candidate -> publish QA"]
    D -->|"fail"| A
```

Notes:

- The loop is bounded by K iterations (default 3). A candidate that
  never passes is withheld; the original photo goes to publish QA.
- The editor never changes dish identity, objects, counts, plating
  style, or brand tokens. Those are exactly the things QA and publish
  QA verify, so a "fix" cannot be a fabrication.
- Publish QA never trusts the QA gate's verdict: it takes only
  (original, candidate) and derives every check itself. There is no
  verdict parameter to forge, so skipping QA cannot be papered over.

## Flat run log

One record per run, one level of keys: route, tier, iterations,
QA pass iteration, pairwise verdict, publish decision, published
variant, reasons, and failure classes. The rollup aggregates routes,
pass@K, coverage hits, leakage (candidates that passed QA but failed
publish QA), published variants, and failure-class counts.
