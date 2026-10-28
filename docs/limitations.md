# Limitations and known failures

- **No real images, no real models.** The vision backend and the
  editor are deterministic fakes over synthetic descriptors. Nothing
  here measures how a real image model would perform, and no photo
  quality claim should be read off this repo.
- **Gold labels are hand-assigned.** The router eval's "human labels"
  are labels written in `visual_content/fixtures.py`, not labels
  collected from labellers under guidelines. The eval is a regression
  check on 13 fixtures; precision 0.889 / recall 0.889 describe that
  set, not real traffic.
- **Thresholds are hand-set.** The rubric bar (0.60), QA floor (0.70),
  publish floor (0.75), edit step (0.20), and meaningful-delta bar
  (0.05) are design choices, not tuned values. Change them and every
  demo number moves; that is expected.
- **The editor only moves scores.** It cannot fix composition problems
  that are really about staging, cannot repair counts, and cannot
  make an unrealistic presentation realistic. Those photos become
  coverage hits by design.
- **Publish QA on originals checks policy, not beauty.** A bad
  original photo that passes policy is still published, because the
  alternative is no photo. The repo does not solve "bad original,
  unfixable edit" beyond counting it.
- **No human-label loop yet.** Drift sampling, a diagnoser across
  feedback sources, and config autotuning belong to the planned
  companion repo. This repo's flat run log is designed as its input.
- **Tier prices are illustrative.** The lite/standard/pro prices are
  demo numbers for fake tiers, not vendor prices, and carry no
  as-of date for that reason.
- **Small fixture set.** Thirteen fixtures cannot resolve fine
  thresholds. Treat all rates as regression checks with wide
  uncertainty, not as measured quality.
