# Review Solution — Analysis Techniques by Tier

The full technique set behind Step 3's tier table. Run §A always; add §B at N≥3; add §C at N≥7.
Never present a Comparative-tier finding in Statistical-tier language.

---

## §A — Diagnostic (always)

**A1. Attribute tagging.** Build a table: one row per candidate, columns for
its attributes (from each rationale's attribute list) plus every criterion
score and the overall. This is the substrate for everything else. Keep it in
the review output — it's the run's memory.

**A2. Gap reading.** For each criterion below its 8-10 anchor, read the
evaluator's `gap` field. These are already-diagnosed, evidence-backed
statements of what's missing. Most of your directives come straight from here,
weighted by `importance` — a 3-point gap on an importance-9 criterion is worth
more than a 6-point gap on an importance-2 one.

**A3. Gate failures first.** Any `min_score` breach becomes directive #1,
ahead of everything else. Nothing else matters until the gates clear.

**A4. Stall check.** If `overall` has moved less than 2 points across the last
two passes, or a criterion has been flat for two passes, the *approach* is the
constraint, not the execution. Say so, and make directive #1 a structurally
different attempt — different format, structure, or framing — rather than
another round of polish on the same shape. Repeated small edits to a design
that has plateaued is the main way this loop wastes a user's time. Exception:
if the flat delta traces to a verification or tooling gap rather than the
design itself — the previous pass's evidence couldn't be gathered, not that
the design failed to improve — say so explicitly and make directive #1
completing that verification, not a structurally different design attempt.

**A5. Targeted perturbation.** Take the leading candidate and identify 2-3
single-attribute changes worth trying. Where a variant is cheap to draft
inline, draft it and check it against the anchors before committing — that
tells you which dimensions are fragile (small change, big score move) and
which are robust. Where it isn't cheap, hand the perturbation to the next pass
as a directive rather than guessing at its effect.

---

## §B — Comparative (N ≥ 3)

**B1. Attribute-to-score association — qualitatively.** Using the A1 table,
look for attribute values that co-occur with higher scores. Report these as
observations, explicitly hedged: *"both candidates using a table-first layout
scored higher on Scanability (8, 7) than the two using prose (4, 5) — 4 data
points, suggestive not conclusive."* Never state a percentage effect at this
tier.

**B2. Pairwise comparison.** Compare candidates head-to-head rather than by
absolute score alone — "is v3 better than v2 on this criterion?" is a far more
reliable judgement than "is v3 a 7?". Build a simple win/loss ranking. Where
pairwise ranking disagrees with the absolute scores, trust the pairwise result
and flag the disagreement — it means the absolute scoring has drifted, which
`design-evaluation` should be told about in the directives.

**B3. Pareto front.** Compute the set of candidates that no other candidate
beats on *every* criterion simultaneously. Present that set, not just the
top-scoring one. A candidate that is second overall but best on the two
heaviest criteria is usually the better parent for the next attempt than the
one with the highest weighted average.

**B4. Recombination.** Treat the Pareto set as parents. Name, specifically,
which element of which candidate should carry into the next attempt — "v2's
opening structure, v4's evidence density, v1's length" — and which weakest
elements to cull. This only works when the design space is combinatorial;
where the artifact is a single indivisible thing, say so and skip it rather
than forcing it.

---

## §C — Statistical (N ≥ 7)

Only at this tier are the numbers worth reporting as numbers. Still state N
alongside every result, and still treat a coefficient from 8 points as an
indication rather than a finding.

**C1. Regression.** Fit a simple linear regression of `overall` against the
sub-scores and the encoded attribute tags across the full history. Report
which attributes carry real signal versus which are noise, with the effect
size and the sample it rests on.

**C2. Bradley-Terry ranking.** Fit a Bradley-Terry model over the pairwise
comparisons from B2, across every candidate in the run's history rather than
just the current batch, so new candidates are ranked against past
high-scorers and quality compounds instead of resetting each pass. Cross-run
comparison is valid only where the runs share an identical rubric — check
before merging histories.

**C3. Generation-parameter search.** Treat "batch quality vs. generation
settings" as an unknown function and search it. The genuinely tunable
parameters here are: how the generation prompt is structured, how many
constraints are given at once, which reference examples are shown, and how
much context is provided. Track which settings produced which scores and move
deliberately toward the promising region — a full Gaussian-process /
acquisition-function treatment is only meaningful once there are enough
observations to fit one, which in practice means a long-running or
cross-session loop.
