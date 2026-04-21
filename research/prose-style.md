---
alwaysApply: false
---
# Prose Style Guide — writing for skim-readers

Companion to `style.md` (which covers matplotlib). This file covers
the *words* in `log.md`, orbit Issue comments, and milestone reviews.

## Audience

**A human researcher skimming the campaign.** They have 60 seconds per
orbit. They want the hypothesis, the number, and the implication —
then a figure to confirm it. If they read more, it's because the first
60 seconds earned their attention.

Not a mini-paper. Not an LLM-parseable info dump. Treat every
paragraph as pressure to be shorter and clearer.

## Lead with result

The **first three lines** of `log.md` body answer:

1. What was the hypothesis? (1 sentence)
2. What was the measured metric? (1 line — number + direction + one
   comparison: baseline, parent, or target)
3. What does this mean for the next hypothesis? (1 sentence)

No warmup, no background, no motivation paragraph. The reader came
here knowing the campaign already.

## Length targets

| Kind of orbit | Body words (excluding frontmatter, code, figure captions) |
|---|---|
| Negative result / ablation | **150–400** |
| Positive result with new mechanism | **400–800** |
| Landmark / graduation candidate | **800–1500** |
| Above 1500 | Justify at the top: "This is long because X — skim the **Result** and **Why it matters** sections." |

Word-count is not a rule against depth; it's a rule against
ceremony. Two pages of boilerplate don't beat half a page of
mechanism.

## Voice

- **Declarative past tense** for what happened: *"Q(v) = 10·exp(+v)
  blew up at v = -3 under dt = 0.01."*
- **Present tense** for interpretation and implication: *"The
  instability comes from |p|²/Q amplification, so smaller α or an
  asymmetric Q could recover stability."*
- **First-person plural** (*we*) or subject-less (*"blew up at..."*)
  — never first-person singular, never passive without a reason.
- **No hedging theatre.** *"suggests"*, *"appears to"* are fine when
  real; don't stack three of them in one sentence.
- **No exclamation marks. No emphasis on numbers** (~~"massive 24%
  improvement!"~~) — the number speaks; describing it as "massive"
  tells the skim-reader not to trust it.

## Before / after vs. parent

If the orbit's frontmatter has `parents:`, the body **must** include
one explicit numeric comparison to each parent: `orbit/<parent>:
<metric> → this orbit: <metric> (Δ=<signed>)`. If no parent, compare
to the named baseline in `config.yaml`.

One sentence is enough. The skim-reader needs to know whether this
orbit beat what came before.

## Conclusion sentence

The **last line** of the body says what the next orbit should try, or
why the line of inquiry is dead. One sentence. Example:

> *"Next: test whether clamping |∂ᵥ log Q| ≤ 0.5 lets α rise above
> 1.0 without losing stability (candidate for orbit 06)."*

This line is what campaign-reviewer harvests at milestones and what
`build_re_complete.py` surfaces in the `## Conclusion & next step`
section of the consolidated Issue comment.

## Equations

Include an equation only when it **changes the reader's
understanding**. If a sentence describing the equation would do, skip
the LaTeX.

- ✅ Equation shows a scaling law the reader can't guess
- ✅ Equation defines the new object the orbit tested
- ❌ Re-stating the evaluator's definition
- ❌ Standard integrator you're just naming (reference it:
  *"BAOAB splitting, Leimkuhler & Matthews 2013"*)

## Abbreviations & glossary

Every 2–4 letter uppercase acronym must be either:
1. Expanded on first use — *"Nose-Hoover Chain (NHC)"*, **or**
2. Listed in a `## Glossary` section at the end.

The orbit-reviewer scans for undefined abbreviations and emits
`[UNDEFINED ABBREVIATION]` findings. Don't make the reader guess.

## Citations

- Inline hyperlinks on first mention: *"Tao's T_c-invariant scaling
  [(arXiv:2310.05678)](https://arxiv.org/abs/2310.05678)"*.
- A full `## References` section is required only when the orbit
  makes a novelty claim. A negative-result orbit cites its parent
  and stops.
- Add new references to `research/references/registry.yaml` — don't
  duplicate across orbits.

## Figure captions in `log.md`

- One sentence per figure. State what to look at, not what's plotted.
  - ✅ *"Panel (c) shows the tail thickens by 2× under α = +1 but
    collapses under α = +5."*
  - ❌ *"Panel (c): v-marginal histogram with viridis colormap."*
- Reference panel labels `(a)`, `(b)`, `(c)` — the style guide
  requires them on `results.png`.

## What the reviewer looks for

`orbit-reviewer` grades the body against:

- `leads_with_result` — first 3 lines have hypothesis + metric + implication
- `length_appropriate` — within target range for orbit type
- `before_after_comparison` — numeric Δ vs parent or baseline
- `conclusion_sentence` — last line says what's next
- `glossary_coverage_ok` — no undefined acronyms

The output is advisory, not gated. But a `WEAK` prose score
surfaces in the consolidated `RE:COMPLETE` comment where the
skim-reader will see it.
