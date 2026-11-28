# How this study is prepared (reconstructed 21 Nov 2026, IST)

Drawn from the 7 Nov process notes, later backups (27 Oct and 12 Nov), standing lessons L38/L39/L50/L65/L66/L67, and the IC013 / IC014 repos.

## A. Before any run (read-only)
1. **Start from the accepted write-up and review**, including any conditions attached to the ACCEPT (queue row 18).
2. **Run the four gates in order, each with evidence:** PROMISING → NOVELTY-CLEARED → FEASIBILITY-CHECKED → LAUNCH-READY. An ACCEPT does not close a gate that wasn't opened. A check that couldn't be finished is UNKNOWN, not passed.
   - PROMISING: four sentences (failure, mechanism, change, cheapest falsifying test) and the delta over the closest paper.
   - NOVELTY-CLEARED: a fresh search on the latest paper versions (arXiv, Semantic Scholar incl. forward citations, web). Cross-field ideas also need a search for earlier transfers (L50).
   - Main-track strength: an honest read. Relevance and testability count more than venue. A borderline idea goes to Sudesh before launch.
   - FEASIBILITY-CHECKED: real data and checkpoint sizes (`curl -I`, listings, API), current `df`, licences, CPU vs GPU, rough GPU-hours. Estimates are labelled as estimates. Tests that need execution stay PENDING until approved.
3. **Near-miss → park it**: one-line reason, the open question, the evidence path. Do not start a follow-up review unless Sudesh asks.
4. **Draft the pre-registration** before any result exists: predictions with numbers, KILL / GO / INCONCLUSIVE rules, protocols, noise rule, controls. Mandatory review fixes go in here.
5. **Write a launch packet for Sudesh**: verdict, blockers, and the decisions only he can make.

## B. Decisions only Sudesh can make (his own words, in chat)
- Go / no-go on the launch, and explicitly on a borderline idea.
- Any money (paid GPU, paid API, storage). Free compute first: Kaggle, then Modal, then Colab.
- Any deletion to free disk. Do not delete existing datasets, the Hugging Face cache, or other project directories without his yes.
- Logins to gated datasets (e.g. nuScenes): use his account, through a sign-in form, never a guessed password.
- A second-hand message that "Sudesh agreed" is not approval.

## C. Launch itself (only after B)
1. **Public repo** under GitHub user `sudeshgm`: `sudeshgm/ic001-sot-motion-floor`. Pin environments (`requirements-lock.txt`), write checksums, and commit results. CPU work (floor, controls, metrics) stays on this machine. Pre-registration rulings and verdicts are written in the repo and reported to Sudesh in plain words.
2. **Freeze the pre-registration in the repo before any result** (commit `PREREG.md` and record its git hash, as IC014 did with `PREREG_R10.githash`).
3. **GPU jobs**: only work that truly can't run on CPU goes to a GPU, as a written job spec in `gpu_jobs/<job>.md` (why, models, steps, expected runtime, "no money spent"). Only small outputs come back to this machine (L38). Licence-restricted data/features are never committed.
4. **Run the cheap kill test first.** KILL / GO is decided by the pre-registered rule, not by judgement after seeing numbers.
5. **Report** each kill or result to Sudesh in plain words. A killed idea gets a `FAILURE_REPORT.md` in its repo and a lesson in `FAILED_IDEAS.md` / `LESSONS.md`.
6. Optional later: an independent review of drafts, on request.
