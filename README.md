# IC001 — How much of LiDAR 3D single-object tracking is just motion?

**Status: preparation on this branch; experimental work lives on `cpu-agent`.** This `main` branch holds the launch-preparation documents plus the 21 November 2026 addendum and secondary-analysis plan. The frozen pre-registration (`PREREG.md`) is on branch `cpu-agent` at commit `e31629c` and is not edited here.

A training-free "motion floor" (world-frame constant velocity + an offset-preserving snap to the visible points, frame-1 ground-truth box size) is compared with released learned trackers (M2-Track, MBPTrack; TrackAny3D if needed) on the standard Open3DSOT KITTI and nuScenes protocol, per ground-truth-defined bin (points in box × motion). The question: how much of reported Success is already reached by motion alone on easy frames, and how much of the 2020–25 leaderboard gain sits in hard frames?

## Files
- `PREP_STEPS.md` — how a launch is prepared in this pipeline.
- `GATES.md` — gate check (promising, novelty, main-track strength, feasibility), 21 Nov 2026.
- `PREREG_DRAFT.md` — **DRAFT** pre-registration for review. Not the frozen pre-registration.
- `LAUNCH_PACKET.md` — one-page summary and open decisions.
- `evidence/` — search outputs and the KITTI zip directory listing used in `GATES.md` (small text/JSON only).

## Addendum and secondary analyses (21 November 2026)
- [`PREREG_ADDENDUM_2026-11-21.md`](PREREG_ADDENDUM_2026-11-21.md) — dated addendum to the frozen pre-registration. Restates the V1 reproduction tolerance: pass if within 1.0 Success of either the paper's published value or the released checkpoint's documented value. Does not edit `PREREG.md`.
- [`SECONDARY_ANALYSES.md`](SECONDARY_ANALYSES.md) — secondary analyses (ego-motion decomposition, BAT progress anchor, SOTracker rung, nuScenes fast-start floor, floor-gated hybrid). None of these is part of the frozen GO / KILL rule.

Closest prior work: LiDAR-SOT (arXiv:2103.06028), TFTrack (arXiv:2609.07738), DMT (arXiv:2203.04232).

- [SOT-M2 training plan (small pilot + full study)](PLAN_SOTM2_TRAINING.md), added 23 Nov 2026.
