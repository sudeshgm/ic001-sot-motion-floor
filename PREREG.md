# IC001 pre-registration — FROZEN v1 (21 Nov 2026)

**Status: FROZEN.** Approved by Sudesh in his own words ("ok for default", 21 Nov 2026, in Idea Launcher's chat, relayed and verified by Idea Launcher), with final choices (a)–(p) below. Frozen before any tracker output or floor score on real data exists. The commit that adds this file is recorded in `PREREG.githash`; real-data scoring in `ic001/run.py` is blocked until that file exists (`ic001/guard.py`).
Source: `PREREG_DRAFT.md` (draft v0), which itself carries Idea Archive's mandatory fixes (a) ground filter, (b) concentration ratio, (c) families/Car headline. Everything in the draft not changed below is kept unchanged.
Code implementing this: branch `cpu-agent`, package `ic001/` at the commit recorded in `PREREG.githash`.

## 1. Question
On the standard Open3DSOT LiDAR 3D-SOT protocol, how much of learned Success does a training-free motion floor already reach on GT-defined easy frames, and how concentrated is the remaining gap in hard frames?

## 2. Data and splits
- KITTI tracking, Open3DSOT test split = scenes 0019–0020 (Velodyne + label_02 + calib + oxts). Classes Car / Pedestrian / Van / Cyclist; Van + Cyclist pooled as "Other". **Car is the headline class.**
- nuScenes v1.0-trainval **val** split, keyframes only (`key_frame_only: True`), LIDAR_TOP only. Mini is not allowed.
- Splits, class lists and `min_points` filters exactly as each tracker's official config (Open3DSOT nuScenes test: `min_points = 1` on the first box). Any deviation is written in RUNLOG before scoring.
- **(o)** KITTI is treated as uniform 10 Hz (the tracking release has no per-frame timestamps). nuScenes uses keyframe timestamps.

## 3. Methods scored
- **Floor (training-free, CPU):** world-frame constant velocity of the box centre (KITTI: ego-compensated with oxts poses; nuScenes: global frame as in Open3DSOT). Frame 2 = zero-velocity copy; from frame 3 the velocity is the difference of the floor's own last two centres (scaled by the timestamp ratio).
  - **(o)** Ego-compensation is yaw-only for box orientation: centres are mapped with the full oxts pose; the box keeps only the yaw part of the rotation (boxes stay upright).
  - **(k)** Heading = the previous box's yaw, always (no velocity-based heading rule). Under OPE this is the frame-1 GT yaw throughout.
  - Box size: OPE keeps the frame-1 GT size. **(j)** One-step re-init uses the previous GT box (centre, yaw and size).
- **Offset-preserving snap (translation only):** o = R_{t−1}^{−1}(C_{t−1} − G_{t−1}); predict; G_t = centroid of non-ground points in the predicted box; if ≥ 5 points, C_t = G_t + R_t·o; else keep the CV box and the previous offset (no snap until an offset exists).
  - **(i)** Point collection box for both G_{t−1} (previous box) and G_t (predicted box): expanded by 0.5 m in BEV (length and width, each side), **no height expansion**.
  - **[FIX a] Ground filter:** non-ground = points **more than 0.25 m above the bottom of the box used at that step** (centre_z − h/2).
- **Controls:** (1) last box (zero velocity, no snap); (2) CV without snap — **(d)** reported under protocol (b) re-init only: under OPE it is identical to last box by construction (frame 2 is a zero-velocity copy and velocity comes from the tracker's own centres, which then never move); (3) KITTI only: floor without ego-compensation.
- **(p)** The ICP-yaw sensitivity variant is dropped.
- **Learned families [FIX c]:** first test = M2-Track (Open3DSOT checkpoints: KITTI Car, Pedestrian; nuScenes Car) + MBPTrack (official checkpoints, all listed classes). BEVTrack dropped (OneDrive 403). TrackAny3D only if the first test is INCONCLUSIVE, and in the full study. Headline three-family claims on Car only.

## 4. Bins (GT attributes only)
- Point count inside the GT box — KITTI: counted from the Velodyne scan in the GT box (no margin); **(h)** nuScenes: the annotation's `num_lidar_pts`.
  - nuScenes: <10, 10–24, ≥25. KITTI: <50, 50–199, ≥200.
- Motion (GT world-frame centre displacement between consecutive frames): KITTI <0.5 m vs ≥0.5 m; nuScenes <2.5 m vs ≥2.5 m (both 5 m/s).
- KITTI occlusion (0 vs 1–2): secondary only.
- **(e) Primary hard** = lowest point bin (KITTI <50, nuScenes <10) ∪ high motion; easy = complement. **Secondary hard** = <200 (KITTI) / <25 (nuScenes) ∪ high motion.
- **(f) Decision bins are single-axis**: the point bins and the motion bins, each on its own. The point × motion grid is SECONDARY (reported, not used for GO/KILL).
- **(g) Frame 0** (given GT box, motion undefined) counts in the overall Success/Precision (Open3DSOT convention) and is **excluded from every per-bin score**.
- **(l) Merge rule, per dataset:** if any point bin of a headline class (Car, Pedestrian) in a dataset holds < 30 distinct tracklets, that dataset's point bins merge to two (KITTI <200 / ≥200; nuScenes <25 / ≥25) for all classes. If a merged headline bin still has < 30 tracklets, KITTI point bins become tertiles of the per-tracklet median GT point count over the KITTI **train** split (Open3DSOT scenes 0000–0016). Merges are decided from GT only, before any score is seen, and recorded in RUNLOG.

## 5. Protocols
- **(a) Standard OPE — headline.** Frame-1 GT only.
- **(b) One-step re-init — diagnostic.** At every frame the tracker gets the GT box at t−1 (and t−2 for the floor's velocity). **(j)** For MBPTrack, the memory is reset from the GT box (memory frames' boxes/targetness from GT). If (a) and (b) disagree on a bin, both are reported and the bin is not claimed as a hard-frame advantage from (a) alone.

## 6. Metrics
- Success = AUC (×100) of the fraction of frames with 3D IoU ≥ th, th ∈ linspace(0, 1, 21). Precision = AUC (×100) of the fraction with centre distance ≤ th, th ∈ linspace(0, 2 m, 21). Exactly as Open3DSOT `TorchSuccess` / `TorchPrecision`.
- **(n)** 3D IoU keeps Open3DSOT's height quirk (vertical extent taken as [centre_z − h, centre_z]).
- Scoring frame: KITTI Velodyne frame of each frame; nuScenes global frame. Learned boxes are re-scored by `ic001` against the same GT.

## 7. Predicted effects (numbers, before data)
KITTI (Car + Pedestrian):
- P1. Easy (primary) holds ≥ 40% of frames, and there best-family Success − floor Success ≤ 5.
- P2. Hard (primary): learned − floor ≥ 10 Success.
nuScenes:
- P3. <25-point frames: learned − floor ≥ 15 Success.
- P4. Frames where floor ≈ learned (gap ≤ 5): ≤ 30%.
Gain concentration — **(a) SECONDARY, no P2B claim:**
- P5 (secondary). G = gain from the floor to the best learned tracker (best by overall Success point estimate). R = (share of G in primary-hard frames) / (share of frames that are primary-hard) > 1.2 with the tracklet-bootstrap 95% CI excluding 1. Share of G in hard = Σ_hard n_b·ΔS_b / Σ_b n_b·ΔS_b. R is not reported if the total gain is ≤ 2 Success.

## 8. Decision rule for the first test (unchanged from the draft except bins = single-axis)
- **KILL:** on both datasets, every decision bin holding ≥ 20% of frames has learned − floor Success > 10 **and** a 95% lower bound > 5.
- **GO:** at least one such bin on each dataset, or one KITTI bin with ≥ 40% of frames, has gap ≤ 5 **and** 95% upper bound ≤ 10.
- **INCONCLUSIVE:** anything else → add TrackAny3D, re-apply the same rule once. Not a kill.
- **(m)** "Learned" in a bin = the best family by point-estimate Success in that bin, chosen before the bootstrap.
- Applied per class with the Car result as headline; protocol (a).

## 9. Noise rule
- **(b)** Tracklet-level bootstrap (resample tracklets with replacement), **10,000 resamples, seed 0**, percentile 95% CIs.
- ≥ 30 tracklets per (class, bin) for any GO / KILL / share claim; smaller cells reported as under-powered and cannot drive GO / KILL.
- Always report raw frame and tracklet counts per cell.

## 10. Validity checks (must pass before scores count)
- **V1 Reproduction (c):** M2-Track and MBPTrack under protocol (a) on KITTI Car, each within **1.0 Success of its paper's published value**. If not: stop and report (no tuning).

  | Tracker | Dataset / class | Published Success / Precision | Source |
  |---|---|---|---|
  | M2-Track | KITTI Car | **65.5** / 80.8 | Zheng et al., "Beyond 3D Siamese Tracking: A Motion-Centric Paradigm…", CVPR 2022, arXiv:2203.01730v1, Table 1 (also Table 5 last row: 65.49 / 80.81) |
  | MBPTrack | KITTI Car | **73.4** / 84.8 | Xu et al., "MBPTrack: Improving 3D Point Cloud Tracking with Memory Networks and Box Priors", ICCV 2023, arXiv:2303.05071v1, Table 1 |
  | M2-Track | nuScenes Car | 55.85 / 65.09 | arXiv:2203.01730v1, Table 2 (same value in arXiv:2303.05071v1 Table 3) |
  | MBPTrack | nuScenes Car | 62.47 / 70.41 | arXiv:2303.05071v1, Table 3 |
  | M2-Track | KITTI Pedestrian | 61.5 / 88.2 | arXiv:2203.01730v1, Table 1 |
  | MBPTrack | KITTI Pedestrian | 68.6 / 93.9 | arXiv:2303.05071v1, Table 1 |

  V1 gates on KITTI Car (as in the draft). The nuScenes Car and KITTI Pedestrian values are recorded and the same ±1.0 comparison is reported, labelled informational. (M2-Track's Open3DSOT README lists higher checkpoint values, e.g. KITTI Car 67.43; those are NOT the V1 reference.)
- **V2 Data integrity:** ranged-extracted KITTI files match the zip's CRC-32 and central-directory sizes; SHA-256 of every input file recorded in `data_manifest/`.
- **V3 Floor determinism:** two CPU runs give identical outputs (byte-identical per-frame CSV).
- **V4 Ground-filter sanity:** on 20 random frames (seed 0), print the fraction of in-box points (GT box, 0.5 m BEV expansion) removed by FIX (a); report it, do not tune it.

## 11. Not allowed after freezing
Changing bins, thresholds, heading rule, snap rule, families, protocols, splits or the decision rule after any score is seen. Any post-hoc analysis is labelled post hoc in RESULTS.md.
