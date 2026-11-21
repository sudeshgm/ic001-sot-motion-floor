# IC001 — How much of LiDAR 3D single-object tracking is just motion?

**Status: preparation, not launched.** No experiments have been run. No data, weights or results are in this repo.

A training-free "motion floor" (world-frame constant velocity + an offset-preserving snap to the visible points, frame-1 ground-truth box size) is compared with released learned trackers (M2-Track, MBPTrack; TrackAny3D if needed) on the standard Open3DSOT KITTI and nuScenes protocol, per ground-truth-defined bin (points in box × motion). The question: how much of reported Success is already reached by motion alone on easy frames, and how much of the 2020–25 leaderboard gain sits in hard frames?

## Files
- `PREP_STEPS.md` — how a launch is prepared in this pipeline.
- `GATES.md` — gate check (promising, novelty, main-track strength, feasibility), 21 Nov 2026.
- `PREREG_DRAFT.md` — **DRAFT** pre-registration for review. Not the frozen pre-registration.
- `LAUNCH_PACKET.md` — one-page summary and open decisions.
- `evidence/` — search outputs and the KITTI zip directory listing used in `GATES.md` (small text/JSON only).

Closest prior work: LiDAR-SOT (arXiv:2103.06028), TFTrack (arXiv:2609.07738), DMT (arXiv:2203.04232).
