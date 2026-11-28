# ⚠️ DRAFT: NOT THE FROZEN PRE-REGISTRATION ⚠️
**IC001 pre-registration, draft v0 (21 Nov 2026, IST), for Sudesh to review.** It becomes binding only after Sudesh approves it and it is committed with a recorded git hash, **before any tracker output or floor score is seen**. Nothing here authorizes downloads, GPU use or runs.
Source text: `idea_writeup_v2.md` §2–§9 (16 Nov) with the three mandatory review fixes (16 Nov ACCEPT, round 2) applied. Changes from v2 are marked **[FIX a/b/c]** or **[NEW]**.

## 1. Question
On the standard Open3DSOT LiDAR 3D-SOT protocol, how much of learned Success does a training-free motion floor already reach on GT-defined easy frames, and how concentrated is the remaining gap (and the published leaderboard gain) in hard frames?

## 2. Data and splits
- KITTI tracking, Open3DSOT test split = scenes 0019–0020 (Car 6,424 / Pedestrian 6,088 / Van 1,248 / Cyclist 308 frames, as cited in v2). Velodyne + label_02 + calib + oxts.
- nuScenes v1.0-trainval **val** split, keyframes only (`key_frame_only: True`, as in Open3DSOT's M2-Track config). Mini is not allowed.
- Splits, class lists and `min_points` filters exactly as each tracker's official config. Any deviation is listed in RUNLOG before scoring.

## 3. Methods scored
- **Floor** (training-free, CPU): world-frame constant velocity of the box centre (KITTI: ego-compensated with oxts; nuScenes: Open3DSOT already global), frame-1 GT size fixed, heading rule (keep previous yaw unless world speed > 1.0 m/s, then yaw = atan2(v_y, v_x)), frame 2 = zero-velocity copy, velocity from the floor's own last two centres from frame 3.
- **Offset-preserving snap** (translation only): object-frame offset o = R_{t-1}^{-1}(C_{t-1} − G_{t-1}); predict; collect non-ground points in the predicted box expanded by 0.5 m in BEV; if ≥5 points, C_t = G_t + R_t·o; else keep CV box and previous offset.
  - **[FIX a] Ground filter:** "non-ground" = points **more than 0.25 m above the GT box bottom** (box bottom = centre_z − h/2 of the box used at that step: the previous box for G_{t−1}, the predicted box for G_t). This replaces v2's backwards "not more than 0.3 m below" rule.
- **Controls:** (1) zero-velocity copy, no snap; (2) CV without snap; (3) KITTI only: CV + snap without ego-compensation.
- **Sensitivity (not headline):** ICP yaw instead of the heading rule.
- **Learned families [FIX c]:** first test = **M2-Track** (Open3DSOT checkpoints: KITTI Car, Pedestrian; nuScenes Car) + **MBPTrack** (official checkpoints, all listed classes). BEVTrack is dropped from the first test (OneDrive 403). TrackAny3D is added only if the first test is INCONCLUSIVE, and in the full study. UniKPT is published context only (no code).
- **Headline three-family claims on Car only [FIX c]**; Pedestrian/other classes are reported per family where checkpoints exist.

## 4. Bins (GT attributes only, fixed now)
- Point count inside GT box. nuScenes: <10, 10–24, ≥25 (merge to <25 / ≥25 if a cell has <30 tracklets). KITTI: <50, 50–199, ≥200 (merge to <200 / ≥200; then tracklet-level tertiles computed before scores are seen).
- Motion (GT world-frame centre displacement between consecutive frames): KITTI <0.5 m vs ≥0.5 m; nuScenes <2.5 m vs ≥2.5 m (both 5 m/s).
- KITTI occlusion (0 vs 1–2): secondary only.
- **Hard** = low-point ∪ high-motion cells; **Easy** = the complement.

## 5. Protocols
- **(a) Standard OPE (headline).** Frame-1 GT only.
- **(b) One-step re-init (diagnostic).** GT box at t−1 (and t−2 for the floor's velocity) at every frame. If (a) and (b) disagree on a bin, both are reported and the bin is not claimed as a hard-frame advantage from (a) alone.

## 6. Predicted effects (numbers, before data)
KITTI (Car + Pedestrian):
- P1. Easy bins hold ≥40% of frames, and there best-scored-family Success − floor Success ≤ 5.
- P2. Hard bins: learned − floor ≥ 10 Success.
nuScenes:
- P3. <25-point bin: learned − floor ≥ 15 Success.
- P4. Frames where floor ≈ learned (gap ≤ 5): ≤30%.
Leaderboard gain concentration **[FIX b]**:
- P5. For the gain G from the earlier to the later tracker, **concentration ratio R = (share of G in hard bins) / (share of frames in hard bins) > 1.2, with the tracklet-bootstrap 95% CI excluding 1.**
  - Share of G in hard bins = Σ_{b∈hard} n_b·(S_late,b − S_early,b) / Σ_b n_b·(S_late,b − S_early,b), n_b = frames in bin b. Share of frames = Σ_{b∈hard} n_b / Σ_b n_b.
  - v2 named P2B → TrackAny3D. **[NEW] Open question for Sudesh:** Open3DSOT ships no P2B checkpoint (BAT is there). Choose before freezing: (i) find an official P2B checkpoint, (ii) use BAT → TrackAny3D, or (iii) in the first test use floor → best learned as G (labelled secondary). Not decidable after seeing numbers.
  - If the denominator gain Σ is ≤ 2 Success points in total, R is not reported (undefined).

## 7. Decision rule for the first test
- **KILL:** on both datasets, every GT-defined bin holding ≥20% of frames has learned − floor Success > 10 **and** a 95% lower bound > 5.
- **GO:** at least one such bin on each dataset, or one KITTI bin with ≥40% of frames, has gap ≤ 5 **and** 95% upper bound ≤ 10.
- **INCONCLUSIVE:** anything else → add TrackAny3D, then re-apply the same rule once. Not a kill.
- "Learned" in a cell = best Success among families actually scored in that cell.

## 8. Noise rule
- Tracklet-level bootstrap (resample tracklets), 95% CIs, **[NEW] 10,000 resamples, seed 0** (draft choice, adjustable before freezing).
- ≥30 tracklets per (class, bin) cell for any GO / KILL / share claim; smaller cells reported as under-powered.
- Van + Cyclist pooled as "Other" on KITTI; headline classes Car and Pedestrian.
- Always report raw frame and tracklet counts per cell.

## 9. Validity checks (must pass before scores count) [NEW]
- V1 Reproduction: M2-Track on KITTI Car 0019–0020 under (a) within 1.0 Success of its published value (draft tolerance, set before freezing); MBPTrack likewise on its published KITTI Car value. If not, stop and report (no tuning).
- V2 Data integrity: ranged-extracted KITTI files match the zip's CRC-32 and the central-directory sizes; record SHA-256 of every input archive/subset list.
- V3 Floor determinism: two CPU runs give identical boxes.
- V4 Ground-filter sanity: on 20 random frames, print the fraction of in-box points removed by FIX (a); report it, do not tune it.

## 10. Not allowed after this is frozen
Changing bins, thresholds, heading rule, snap rule, families, protocols or splits after any score is seen. Any post-hoc analysis is labelled post hoc in RESULTS.md.
