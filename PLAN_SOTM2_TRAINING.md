# SOT-M2 training plan (added 23 Nov 2026 at Sudesh's request)

Idea: SOT-M2, a 20 Hz recurrent LiDAR tracker with keyframe-only loss and a self-aligned target-frame buffer.
Seeded by IC001 findings. Parked after a THINK MORE review (round 1).

## Evidence so far
Inference-only 5-arm kill test, nuScenes v1.0-mini, 215 Car tracklets.
Prereg sha256 c71fee2d...0cd8; files from the SOT-M2 kill-test run.

| | M2-Track | TrackAny3D |
|---|---|---|
| Oracle-aligned buffer E-A, pts<10 | +11.14 [+8.20, +14.24] | +5.33 [+0.31, +9.95] |
| Self-aligned D - ego 10-sweep C, pts<10 | -4.50 | -3.65 |
| Self-aligned D - ego 10-sweep C, moving | +17.65 | +17.48 |
| Naive sweep-rate B-A, overall | -14.55 | -13.12 |
| Verdict | GO(c) | INCONCLUSIVE |

Headroom exists only when alignment is good. The open question is whether **training** learns that alignment.
An inference-only test cannot answer that.

## Arms (both stages)
- C: ego-frame 10-sweep accumulation, retrained (STTracker 2306.17440 style). This is a binding baseline.
- I: sweep-rate training on devkit-interpolated boxes, causal at test time. This is a binding baseline.
- D: self-aligned target-frame buffer + recurrence, keyframe-only loss (truncated BPTT). This is the method.
- Reference arms: A (public checkpoint), CV at sweep rate, freeze-if-static, IC001 motion floor.

Bins are fixed from single-sweep keyframe GT, as in the kill test.
Stats: paired tracklet bootstrap, 10k resamples, 95% CI, every effect >= 2x SE.

## Stage 1: small pilot (go/no-go, soft evidence)
- **Data:** about 30-50 nuScenes train_track scenes; download only their LIDAR_TOP sweeps.
  Evaluate on mini's 9 non-train_track scenes, plus a held-out val slice if the download allows.
- **Training:** fine-tune the existing M2-Track nuScenes Car checkpoint for a few epochs, with the same budget for C, I and D.
- **Compute:** rough guess 10-20 free T4-h. The first go/no-go chunk must stay at <= ~2 T4-h; run M2-Track only.
  Free GPU only (Kaggle, then Modal, then Colab).
- **Pre-register before running:**
  - GO: D - max(C, I) >= +2 Success on pts<10 or moving, lower CI > 0.
  - KILL: D <= max(C, I) + 0.5 on both cells with CI upper < +2.
  - Anything else is INCONCLUSIVE.
- **Caveat:** small data and few epochs can understate a method that must learn alignment. A KILL here is soft.

## Stage 2: full study (only if Stage 1 is GO and Sudesh approves)
- **Data:** full nuScenes train_track sweeps, about 90-100 GB raw.
  Alternatively, stream the official blobs (~300 GB transfer) and keep target-region crops (a few GB).
- **Trackers:** 3 (M2-Track, TrackAny3D, plus one more such as MBPTrack). Each runs arms C, I and D from the standard schedule.
- **Generality:** label-subsampled KITTI/Waymo arm. Fix the scoring frames and a small-gap rule (gap < ~2 Success = noise) in advance.
- **Compute:** rough 150-250 T4-h; this is an estimate only.
- **Report:** cost per keyframe and FPS at 20 Hz.

## Rules
- Usage: at >= 60% weekly usage, start nothing until Sudesh says yes.
- No paid compute or closed models without Sudesh's explicit approval.
- nuScenes-derived outputs stay private.
