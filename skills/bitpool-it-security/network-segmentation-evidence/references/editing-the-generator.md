# Editing this skill and its generator

Relocated from the skill's main file. Read it before changing any script, or any part of the
process (where the pack goes, what is archived, what recurs, what the emitters write).

**Everything the pack says about itself is a claim an auditor can test, and the generator's prose
blocks are where those claims rot.** `scripts/render.py` holds standing statements about how this
evidence is produced, stored and reviewed — the `INTRO` and `PIPE_TMPL` constants and the "What this
unlocks" block. Two rules follow, and both were earned the same way: a change landed in one file and
the prose asserting the old behaviour was never swept.

- **No sentence in a generated artefact may assert a fact about the estate unless it is derived from
  the dump on that run.** If a clause cannot be computed, it does not belong in the output. The
  opening verdict card once conceded a scope gap Bitpool did not have, because the count recomputed
  and the words around it did not; a sibling deliverable claimed full coverage on the same run. See
  the docstring on `verdict()` in `render.py` for the pattern and the reasoning.
- **Never retype code into the generator's prose.** Any code the pack displays must be read out of
  the module that actually runs it at render time — see `_tier_src()` in `scripts/render.py`. A
  hand-copied block is correct on the day it is written and silently wrong from the first change
  afterwards, and the page's whole argument is that nothing on it was produced by hand. The
  displayed copy of `subnet_tier()` had drifted from the real one in six ways, including a tier it
  did not mention at all.

The same obligation runs the other way: **any change to the process — where the pack goes, what is
archived, what recurs, what the emitters write — requires re-reading the skill's main file, its
references and the generator's prose in the same pass.** A process decision recorded in the skill on
2026-09-01 left `render.py` asserting a repo archive that no longer existed, and the two sat in
contradiction for fifteen days in the same directory. The pack is read by an external auditor; a
stale claim there costs more than a stale claim in the skill.

After any script edit, run `python test_model.py` from the `scripts/` folder before rendering.
