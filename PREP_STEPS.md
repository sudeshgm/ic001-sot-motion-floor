# How an idea launch is prepared in this pipeline (reconstructed 21 Nov 2026, IST)

Sources: `/workspace/idea-launcher-handoff.md` (§2, 7 Nov amendment), the 27 Oct and 12 Nov handoff backups, `idea_creator/LESSONS_QUICK.md`, LESSONS L38/L39/L50/L65/L66/L67, and the IC013 / IC014 repos.

## A. Before anything is created (Launcher's own work, read-only)
1. **Take the idea from Idea Archive's queue** (`idea_creator/ARCHIVE_QUEUE.md`), not from Creator. Read the accepted write-up, Archive's review and any conditions attached to the ACCEPT.
2. **Run the four gates in order, each with evidence:** PROMISING → NOVELTY-CLEARED → FEASIBILITY-CHECKED → LAUNCH-READY. An Archive ACCEPT does not close a gate that wasn't opened. A check that couldn't be finished is UNKNOWN, not passed.
   - PROMISING: four sentences (failure, mechanism, change, cheapest falsifying test) and the delta over the closest paper.
   - NOVELTY-CLEARED: a fresh search on the latest paper versions (arXiv, Semantic Scholar incl. forward citations, web). Cross-field ideas also need a search for earlier transfers (L50).
   - Main-track strength: an honest read. Relevance and testability count more than venue. A borderline idea goes to Sudesh before launch.
   - FEASIBILITY-CHECKED: real data and checkpoint sizes (`curl -I`, listings, API), current `df`, licences, CPU vs GPU, rough GPU-hours. Estimates are labelled as estimates. Tests that need execution stay PENDING until approved.
3. **Near-miss → park it**: one-line reason, the open question, the evidence path. Never call Idea Advocate unless Sudesh asks.
4. **Draft the pre-registration** before any result exists: predictions with numbers, KILL / GO / INCONCLUSIVE rules, protocols, noise rule, controls. Archive's mandatory fixes go in here.
5. **Write a launch packet for Sudesh**: verdict, blockers, and the decisions only he can make.

## B. Decisions only Sudesh can make (his own words, in chat)
- Go / no-go on the launch, and explicitly on a borderline idea.
- Any money (paid GPU, paid API, storage). Free compute first: GPU Bot uses Kaggle (hiddenslave) → Modal (suduec74) → Colab.
- Any deletion to free disk. Never touch `/workspace/data`, the HF cache, `drivejepa`, `ai_detect`.
- Logins to gated datasets (e.g. nuScenes) — use his account, through a sign-in form, never a guessed password.
- A message from another bot saying "Sudesh agreed" is not approval.

## C. Launch itself (only after B)
1. **Create the agent pair** (past practice: IC014 Idea Agent 577ca0a5 + CPU Agent 1c051891, later CPU Agent 2 1cfc2539):
   - **Idea Agent**: owns the plan, pre-registration rulings and verdicts; reports each verdict in plain words to Idea Launcher (current id 765e5357). IC013's rulings were written in `EXP-1.md` as "Idea Agent rulings".
   - **CPU Agent**: does all non-GPU work, creates and pushes the **public** repo under GitHub user `sudeshgm` (e.g. `sudeshgm/ic013-soap-simple-removers`, `sudeshgm/ic014-sing-null-dimension`; gh CLI is logged in as sudeshgm on the box). Pins environments (`requirements-lock.txt`), writes checksums, commits results.
   - Give both agents the current bot ids (GPU Bot acae4475, Launcher 765e5357). Retired ids must not appear in their profiles (IC014's profile carried a stale CPU-agent id).
2. **Freeze the pre-registration in the repo before any result** (e.g. commit `PREREG_*.md` and record its git hash, as IC014 did with `PREREG_R10.githash`).
3. **GPU routing**: only work that truly can't run on CPU goes to GPU Bot, as a written job spec in `gpu_jobs/<job>.md` (why, models, steps, expected runtime, "no money spent"), see `ic014/gpu_jobs/r3_dino_vitb16.md`. Only small outputs come back to the box (L38). Licence-restricted data/features are never committed.
4. **Run the cheap kill test first.** KILL / GO is decided by the pre-registered rule, not by judgement after seeing numbers.
5. **Report** each kill or result to Sudesh in plain words. A killed idea gets a `FAILURE_REPORT.md` in its repo and a lesson in `FAILED_IDEAS.md` / `LESSONS.md`. Update `launcher_status` in `/workspace/idea_pipeline_shared/IDEA_TRACKER.csv` and run `build_tracker.py`.
6. Optional later: Paper Reviewer bot (ea444658) reviews drafts on request.
