# IC001 results

**Final decision after the single re-application with TrackAny3D (22 November 2026): INCONCLUSIVE.** See "Final decision (with TrackAny3D)" directly below. The first-test record that follows is unchanged.

## Final decision (with TrackAny3D)

The first test returned INCONCLUSIVE, so PREREG §8 adds TrackAny3D and re-applies the same rule **once**. This is that re-application. Nothing else changed: same headline class (Car), protocol a (OPE), floor (`cv_snap`), single-axis bins, eligibility (≥ 20% of binned frames and ≥ 30 tracklets), tracklet bootstrap (10,000 draws, seed 0), and `ic001` Success / Precision. Learned in a bin = the best of M2-Track, MBPTrack and TrackAny3D by point estimate, chosen before the bootstrap. The same code restricted to M2-Track + MBPTrack reproduces the recorded first-test cells exactly (max |Δ| = 0). Full tables: `results/trackany3d_final/tables.md`; log: `results/trackany3d_final/RUNLOG.md`.

**V1 (dated addendum).** TrackAny3D KITTI Car: ic001 Success **73.40** / Precision 85.21 (official test 73.417 / 85.239 over 6,424 frames) vs paper 73.4 → **PASS**. nuScenes Car (informational): **59.29** / 66.45 (official test 59.291 / 66.448 over 64,159 frames) vs paper 59.30 → PASS.

**KITTI yaw convention.** The dump harness takes yaw from the camera box's length axis rotated into the velodyne frame. ic001 GT uses −(rotation_y + π/2). The two differ by ≤ 7.97e-3 rad (0.46°), the same issue recorded for MBPTrack. TrackAny3D KITTI yaw is converted to the GT convention by a closed-form, calibration-only inverse (`ic001/kitti_yaw.py`; no GT, no scores). On the MBPTrack dump it reproduces the raw-quaternion GT-convention yaw to 1e-14 rad, and it brings the frame-0 yaw error to 4e-16 rad. With it, ic001 scores TrackAny3D KITTI Car OPE at 73.40 vs the tracker's own 73.42 (as-dumped yaw: 73.33). nuScenes needs no correction.

| Dataset | Bin | Best family | Gap | 95% CI | Share of binned frames | Tracklets | Status |
|---|---|---|---:|---|---:|---:|---|
| KITTI | pts <50 | TrackAny3D | 33.47 | [25.97, 40.56] | 37.2% | 99 | KILL cell |
| KITTI | pts 50–199 | MBPTrack | 61.28 | [50.41, 68.48] | 26.8% | 107 | KILL cell |
| KITTI | pts ≥200 | TrackAny3D | 61.47 | [50.54, 71.02] | 36.0% | 91 | KILL cell |
| KITTI | motion <0.5 m | TrackAny3D | 49.69 | [41.86, 56.49] | 75.4% | 115 | KILL cell |
| KITTI | motion ≥0.5 m | MBPTrack | 54.40 | [27.82, 69.19] | 24.6% | 17 | not eligible (<30 tracklets) |
| nuScenes | pts <10 | MBPTrack | 9.64 | [7.97, 11.29] | 59.4% | 3,304 | eligible; neither GO nor KILL |
| nuScenes | pts 10–24 | MBPTrack | 42.99 | [40.96, 44.96] | 13.2% | 1,989 | not eligible (<20% of frames) |
| nuScenes | pts ≥25 | MBPTrack | 46.83 | [44.57, 49.09] | 27.5% | 1,601 | KILL cell |
| nuScenes | motion <2.5 m | MBPTrack | 24.94 | [23.26, 26.58] | 84.9% | 3,087 | KILL cell |
| nuScenes | motion ≥2.5 m | MBPTrack | 20.35 | [17.93, 22.83] | 15.1% | 759 | not eligible (<20% of frames) |

TrackAny3D does not displace MBPTrack anywhere on nuScenes Car. In the deciding cell (fewer than 10 points), Success is MBPTrack 52.43, TrackAny3D 48.69, M2-Track 44.28, floor 42.80. TrackAny3D alone is 5.90 [4.29, 7.49] above the floor there; this per-family value is not used by the rule. On KITTI, TrackAny3D is best in three of the four eligible bins, and every eligible KITTI bin stays a KILL cell. In the <50-point bin TrackAny3D leads MBPTrack by only 0.01 Success. With the as-dumped yaw MBPTrack would lead instead, but the gap (33.47) and its KILL status are the same.

**Verdict.** KITTI meets the KILL condition on every eligible bin. nuScenes does not, because the fewer-than-10-points bin has a gap of 9.64 [7.97, 11.29]. No GO cell exists on either dataset. The rule therefore returns **INCONCLUSIVE**. This was the single re-application §8 allows, so the rule is not applied again. INCONCLUSIVE is not a kill, but the rule also gives no GO.

**TrackAny3D licence and citation.** The TrackAny3D repository (pinned commit `2f01dc84`) has no licence file. Its code and checkpoints were used for evaluation only and are not redistributed: no code, weights or per-frame outputs are in this repository, only aggregate scores. Citation: M. Wang, H. Wang, Y. Li, X. Kong, J. Du, G. Shen, F. Xia, *TrackAny3D: Transferring Pretrained 3D Models for Category-unified 3D Point Cloud Tracking*, ICCV 2025, arXiv:2507.19908.

**Run deviations.** Official-test configs used `eval_cfg.num_workers = 0` (torch 1.8 DataLoader workers segfaulted). The single allowed source patch was `RECON.py` `map_location` `cuda:1` → `cpu`. Neither change affects the model or the metric.

**Formal first-test decision (22 November 2026): INCONCLUSIVE.** Headline class **Car**, protocol a (standard one-pass evaluation). The frozen rule is applied on both KITTI and nuScenes.

On KITTI, every eligible Car decision bin meets the KILL cell condition (learned − floor Success > 10 and a 95% lower bound > 5). On nuScenes, the same holds for the ≥25-point bin and the low-motion bin, but **not** for the largest bin: cars with fewer than 10 LiDAR points (59.4% of binned frames, 35,909 frames, 3,304 tracklets). There the best learned family (MBPTrack) minus the floor is **9.64** Success, 95% CI **[7.97, 11.29]**. That is neither a KILL cell (the gap is not greater than 10) nor a GO cell (the gap is not ≤ 5, and the upper bound is not ≤ 10). The GO clause does not fire: KITTI has no GO cell, including none with ≥ 40% of frames. Per the frozen pre-registration, TrackAny3D is to be added and the same rule re-applied once.

- Pre-registration: `PREREG.md`, frozen at `e31629c` (`PREREG.githash`). This file does not edit it.
- V1 tolerance: dated addendum `PREREG_ADDENDUM_2026-11-21.md` (this file does not edit the addendum either).
- Protocol: standard one-pass evaluation (protocol a / `ope`), headline class **Car**.
- Floor: pre-registered `cv_snap` in `results/kitti/` and `results/nuscenes/` (unchanged).
- Learned boxes were re-scored with `ic001` metrics (PREREG §6). KITTI MBPTrack uses the GT-convention yaw (`mbptrack_yawalt`); see the recorded KITTI deviation below. nuScenes frame-0 boxes already match the index GT (centres exact; yaw error ≤ 4.4e-16 rad), so no yaw correction was applied there.
- Aggregate tables: `results/kitti_decision/` and `results/nuscenes_decision/`. Per-frame CSVs are dataset-derived and are **not** committed.

## Formal first-test decision (PREREG §8, Car, protocol a)

Decision bins are single-axis. nuScenes: point bins `<10`, `10–24`, `≥25` and motion bins `<2.5 m`, `≥2.5 m`. KITTI bins are unchanged from the record below. Frame 0 is excluded from every per-bin score. No point-bin merge on either dataset (GT censuses already recorded). Learned in a bin = the best family by point-estimate Success in that bin, chosen before the bootstrap. Gap = learned − floor (`cv_snap`), tracklet bootstrap 10,000 resamples, seed 0, percentile 95% CI. Cells with fewer than 30 tracklets, or with fewer than 20% of binned frames, cannot drive GO / KILL.

**KILL** requires the cell conditions on every eligible bin of **both** datasets. **GO** requires a qualifying close-gap cell on each dataset, or one KITTI bin with ≥ 40% of frames. Anything else is **INCONCLUSIVE**.

### nuScenes Car — best learned − floor (headline half)

Shares are of the 60,499 binned Car frames. Best family is MBPTrack in every bin.

| Bin | Best family | Floor | Learned | Gap | 95% CI | n frames | Share | n tracklets | Eligible? |
|---|---|---:|---:|---:|---|---:|---:|---:|---|
| pts0 (<10) | MBPTrack | 42.80 | 52.43 | 9.64 | [7.97, 11.29] | 35909 | 59.4% | 3304 | yes (≥40%); neither GO nor KILL cell |
| pts1 (10–24) | MBPTrack | 24.09 | 67.08 | 42.99 | [40.96, 44.96] | 7961 | 13.2% | 1989 | **no** (<20% of frames) |
| pts2 (≥25) | MBPTrack | 27.06 | 73.90 | 46.83 | [44.57, 49.09] | 16629 | 27.5% | 1601 | yes (≥20%); KILL cell |
| motLo (<2.5 m) | MBPTrack | 41.13 | 66.08 | 24.94 | [23.26, 26.58] | 51375 | 84.9% | 3087 | yes (≥40%); KILL cell |
| motHi (≥2.5 m) | MBPTrack | 7.17 | 27.52 | 20.35 | [17.93, 22.83] | 9124 | 15.1% | 759 | **no** (<20% of frames) |

The pts0 bin is why nuScenes is not a KILL half: the gap is 9.64, just under the threshold of 10, and the confidence interval crosses 10.

### Same bins, each family separately (nuScenes Car)

| Family | Bin | Floor | Learned | Gap | 95% CI | Eligible? |
|---|---|---:|---:|---:|---|---|
| M2-Track | pts0 | 42.80 | 44.28 | 1.49 | [−0.29, 3.24] | yes; would be a GO cell |
| M2-Track | pts1 | 24.09 | 63.27 | 39.18 | [37.14, 41.18] | no |
| M2-Track | pts2 | 27.06 | 73.09 | 46.03 | [43.85, 48.23] | yes; KILL cell |
| M2-Track | motLo | 41.13 | 59.54 | 18.41 | [16.59, 20.18] | yes; KILL cell |
| M2-Track | motHi | 7.17 | 27.42 | 20.25 | [17.66, 22.89] | no |
| MBPTrack | pts0 | 42.80 | 52.43 | 9.64 | [7.97, 11.29] | yes; neither GO nor KILL cell |
| MBPTrack | pts1 | 24.09 | 67.08 | 42.99 | [40.96, 44.96] | no |
| MBPTrack | pts2 | 27.06 | 73.90 | 46.83 | [44.57, 49.09] | yes; KILL cell |
| MBPTrack | motLo | 41.13 | 66.08 | 24.94 | [23.26, 26.58] | yes; KILL cell |
| MBPTrack | motHi | 7.17 | 27.52 | 20.35 | [17.93, 22.83] | no |

M2-Track is within about 1.5 Success of the floor on the <10-point bin, and that per-family interval would meet the GO cell condition. It does **not** enter the formal rule, because MBPTrack is the better family in that bin (52.43 vs 44.28).

Other classes are reported in `results/nuscenes_decision/tables.md` and do not drive the headline. Pedestrian, Truck, and Trailer have KILL cells on every eligible bin. Bus does not: its <10-point bin has gap 11.91 but a 95% lower bound of 4.65, which is not greater than 5.

### Secondary ratio R (nuScenes)

R = (share of gain from the floor to the best learned tracker in primary-hard frames) / (share of frames that are primary-hard). Best learned overall on nuScenes Car is MBPTrack.

**R = 0.490**, 95% CI **[0.445, 0.532]**. Total gain is well above 2 Success, so R is defined. The interval is entirely below 1, and P5 (R > 1.2 with the CI excluding 1) is **not** supported. R is secondary and is not a GO / KILL claim.

SECONDARY analysis #2 (R_progress from BAT to the best learned tracker) is **not computed** on nuScenes: BAT was not run on this dataset.

### Predicted effects (nuScenes Car; not the decision rule)

- P3 (<25-point frames: learned − floor ≥ 15): 43,870 frames (72.5% of binned, 3,385 tracklets); floor 39.40, MBPTrack 55.09, gap **15.69**. P3 holds as a point estimate.
- P4 (frames where floor ≈ learned, per-frame gap ≤ 5, should be ≤ 30%): 27,598 / 60,499 binned frames (**45.6%**). P4 does not hold.

Primary easy (33.6% of binned frames): floor 29.49, MBPTrack 78.22, gap 48.74. Primary hard (66.4%): floor 39.31, MBPTrack 51.19, gap 11.88.

## nuScenes scores (val, keyframes, LIDAR_TOP)

Floor numbers below are the already-frozen `cv_snap` results in `results/nuscenes/` (commit `38d18f1`); re-scoring the same floor CSVs against the index reproduced them exactly (max |Δ| = 0). Learned numbers are ic001 re-scores of the v3 learned-tracker dumps. They match the run-dir `eval_bins_nuscenes_*.json` exactly (max |Δ| = 0). Offsets versus the tracker-native dump-log headlines are at most 0.01 and come from rounding of those native figures, not from a rescore mismatch.

### Overall Success / Precision (protocol a, includes frame 0)

| Class | Tracklets / frames | last_box | Floor (cv_snap) | M2-Track | MBPTrack |
|---|---|---:|---:|---:|---:|
| Car | 3,660 / 64,159 | 57.39 / 63.57 | 39.59 / 42.16 | 57.21 / 65.73 | 62.46 / 70.41 |
| Pedestrian | 1,858 / 33,227 | 21.42 / 33.32 | 16.97 / 29.70 | — | 45.38 / 74.06 |
| Truck | 608 / 13,587 | 62.67 / 63.20 | 34.14 / 30.40 | — | 62.16 / 63.24 |
| Trailer | 152 / 3,352 | 73.88 / 71.17 | 39.16 / 31.76 | — | 65.07 / 61.30 |
| Bus | 120 / 2,953 | 44.02 / 40.35 | 26.98 / 20.48 | — | 55.08 / 51.34 |

M2-Track has an official nuScenes checkpoint for Car only. Bicycle and Motorcycle have a frozen floor but no first-test learned checkpoint.

Car re-init (diagnostic, not the headline): floor 83.79 / 88.54, constant velocity 90.36 / 92.94, last box 78.16 / 78.05, M2-Track 78.83 / 84.87, MBPTrack 79.80 / 84.94.

### Informational V1 (nuScenes Car, protocol a)

V1 still gates on KITTI Car only (both gates already PASS; see below). nuScenes Car uses the same dated-addendum tolerance and is informational.

| Tracker | Our Success / Precision | Paper | Δ paper | Documented checkpoint | Δ ckpt | Informational |
|---|---:|---:|---:|---:|---:|---|
| M2-Track | **57.21 / 65.73** | 55.85 / 65.09 | 1.36 (not within 1.0) | 57.22 / 65.72 (Open3DSOT README, `mmtrack_nuscenes_car.ckpt`) | **0.01** (within 1.0) | **PASS** (via the checkpoint reference) |
| MBPTrack | **62.46 / 70.41** | 62.47 / 70.41 | **0.01** (within 1.0) | none (paper value only) | — | **PASS** |

Verification of the learned-tracker dumps: every SHA-256 in `SHA256SUMS_outputs.txt`, `SHA256SUMS_all.txt` (files present in the run directory), and `SHA256SUMS_eval.txt` matched. Dump keys match the frozen nuScenes index exactly (Car 128,318 rows = 64,159 frames × 2 protocols, for both families; Pedestrian 66,454; Truck 27,174; Trailer 6,704; Bus 5,906; missing = 0, extra = 0). `run_meta`: rc=0, wall_s=23082, paid=0, finished 22 Nov 2026, 09:38:06 IST. An earlier failed run tree (v1, rc=3, no dumps) was not used. Code pins recorded in the run: ic001 `38d18f1`, Open3DSOT `f08451d`, MBPTrack3D `e5670d1`.

## V1 reproduction (KITTI Car, protocol a)


V1 still gates on KITTI Car only. Under the approved addendum, a tracker **passes** if its ic001-rescored Success is within **1.0** of *either* the paper value *or* a documented official-checkpoint value. MBPTrack is checked against its paper value only (no documented checkpoint Success distinct from the paper was identified). Precision is recorded and is not a gate.

### M2-Track — PASS (V1 gate)

| | |
|---|---|
| Our Success / Precision | **67.42 / 81.01** |
| Paper (Zheng et al., CVPR 2022, Table 1) | 65.5 / 80.8 |
| \|Δ\| vs paper | 1.92 (not within 1.0) |
| Documented checkpoint (Open3DSOT README, `mmtrack_kitti_car.ckpt`) | 67.43 / 81.04 |
| \|Δ\| vs checkpoint | **0.01** (within 1.0) |
| **V1 outcome** | **PASS** (via the checkpoint reference) |

### MBPTrack — PASS (V1 gate)

Primary scores use the GT-convention yaw rescore (see deviation).

| | |
|---|---|
| Our Success / Precision | **73.66 / 85.16** |
| Paper (Xu et al., ICCV 2023, Table 1) | 73.4 / 84.8 |
| \|Δ\| vs paper | **0.26** (within 1.0) |
| Documented checkpoint | none (paper value only) |
| **V1 outcome** | **PASS** |

The harness-yaw overall (73.57 / 85.16) would also pass (Δ = 0.17 vs 73.4). It is not the V1 figure used here.

### Informational (same ±1.0 rule; not a V1 gate)

| Tracker | Class | Our S / P | Paper | Δ paper | Checkpoint | Δ ckpt | Informational |
|---|---|---:|---:|---:|---:|---:|---|
| M2-Track | Pedestrian | 60.60 / 89.37 | 61.5 / 88.2 | 0.90 | 60.61 / 89.39 | 0.01 | PASS |
| MBPTrack (GT-convention yaw) | Pedestrian | 65.99 / 90.91 | 68.6 / 93.9 | 2.61 | — | — | FAIL |

The Pedestrian MBPTrack informational miss is recorded; it does not stop the study (V1 gates on KITTI Car only, and both gates passed).

## Recorded deviation: MBPTrack yaw convention

The MBPTrack harness camera→velodyne self-check **failed**: frame-0 yaw max error **7.75e-3–7.97e-3 rad** (reported as **7.8e-3 rad**) versus a **1e-4** rad tolerance. **Centres match exactly.** The harness CSV was left unchanged. Primary MBPTrack numbers in this file use the GT-convention yaw rescore `yaw = -(rotation_y + π/2)` from the raw camera boxes (`mbptrack_yawalt`).

GPU Bot stated that this rescore changes results by at most 0.2. That holds for every overall score (largest |Δ Success| = 0.088 on Car ope) and for every Car group (largest |Δ Success| = 0.172). Precision is unchanged. Three tiny non-headline cells exceed 0.2: Pedestrian high-motion (6 frames, ΔS = −0.83), Pedestrian grid p2 / high-motion (4 frames, ΔS = −1.25), and Cyclist <50-point (19 frames, ΔS = +0.26). Details: `results/kitti_decision/mbptrack_yaw_deviation.json`.

## Match to GPU Bot's numbers

ic001 Success / Precision on every reported group, for M2-Track, MBPTrack harness yaw, and MBPTrack GT-convention yaw, **match GPU Bot's `eval_bins_kitti_*.json` exactly** (max \|Δ\| = 0).

GPU Bot's headline Car native numbers (the tracker's own IoU) were **M2-Track 67.43 / 81.04** and **MBPTrack 73.67 / 85.19**. Our ic001 figures differ from those natives by at most 0.10 Success / 0.03 Precision on Car (M2-Track and yawalt: −0.01 / −0.03; harness yaw: −0.10 / −0.03). GPU Bot already attributed offsets of ≤ 0.1 to IoU-implementation differences. That is not a mismatch against GPU Bot's ic001 rescore.

## KITTI side of the decision rule (Car, protocol a)

Decision bins are single-axis (point bins `<50`, `50–199`, `≥200` and motion bins `<0.5 m`, `≥0.5 m`). Frame 0 is excluded from every per-bin score. No point-bin merge (GT census, already in `results/kitti/RUNLOG.md`). Learned in a bin = the best family by point-estimate Success in that bin, chosen before the bootstrap (M2-Track vs MBPTrack GT-convention yaw). Gap = learned − floor, tracklet bootstrap 10,000 resamples, seed 0, percentile 95% CI. Cells with fewer than 30 tracklets cannot drive GO / KILL. Shares are of the 6,304 binned Car frames.

### Best learned − floor (headline)

| Bin | Best family | Floor | Learned | Gap | 95% CI | n frames | Share | n tracklets | Eligible? |
|---|---|---:|---:|---:|---|---:|---:|---:|---|
| pts0 (<50) | MBPTrack | 26.60 | 60.07 | 33.46 | [25.90, 40.63] | 2344 | 37.2% | 99 | yes (≥20%) |
| pts1 (50–199) | MBPTrack | 17.59 | 78.87 | 61.28 | [50.41, 68.48] | 1691 | 26.8% | 107 | yes (≥20%) |
| pts2 (≥200) | MBPTrack | 21.80 | 82.52 | 60.72 | [50.32, 69.76] | 2269 | 36.0% | 91 | yes (≥20%) |
| motLo (<0.5 m) | MBPTrack | 24.64 | 74.18 | 49.54 | [41.90, 56.12] | 4751 | 75.4% | 115 | yes (≥40%) |
| motHi (≥0.5 m) | MBPTrack | 15.77 | 70.17 | 54.40 | [27.82, 69.19] | 1553 | 24.6% | 17 | **no** (under-powered) |

Every eligible bin has gap > 10 and 95% lower bound > 5, so it meets the KILL cell condition. No eligible bin meets the GO cell condition (gap ≤ 5 and 95% upper bound ≤ 10), including the 75.4% low-motion bin.

### Same bins, each family separately (KITTI only)

M2-Track − floor and MBPTrack − floor both meet the KILL cell condition on every eligible Car decision bin; MBPTrack is the best family in every bin. High-motion remains under-powered for both.

| Family | Bin | Gap | 95% CI | Eligible? |
|---|---|---:|---|---|
| M2-Track | pts0 | 27.99 | [21.87, 34.00] | yes |
| M2-Track | pts1 | 54.90 | [44.00, 61.95] | yes |
| M2-Track | pts2 | 53.46 | [42.06, 63.95] | yes |
| M2-Track | motLo | 43.45 | [35.17, 50.88] | yes |
| M2-Track | motHi | 47.19 | [23.88, 62.76] | no (17 tracklets) |
| MBPTrack | pts0 | 33.46 | [25.90, 40.63] | yes |
| MBPTrack | pts1 | 61.28 | [50.41, 68.48] | yes |
| MBPTrack | pts2 | 60.72 | [50.32, 69.76] | yes |
| MBPTrack | motLo | 49.54 | [41.90, 56.12] | yes |
| MBPTrack | motHi | 54.40 | [27.82, 69.19] | no (17 tracklets) |

### Predicted effects (not the decision rule; Car, protocol a)

- P1 (easy primary holds ≥ 40% of frames and best-family − floor ≤ 5): easy primary is 51.2% of binned frames (3,227 frames, 112 tracklets) but the gap is **58.80** (floor 21.52, MBPTrack 80.32). P1 does not hold.
- P2 (hard primary: learned − floor ≥ 10): hard primary is 48.8% of binned frames (3,077 frames, 101 tracklets); gap **42.28** (floor 23.44, MBPTrack 65.71). P2 holds as a point estimate.

### Secondary ratio R (Car)

R = (share of gain from the floor to the best learned tracker in primary-hard frames) / (share of frames that are primary-hard). Best learned overall is MBPTrack (GT-convention yaw).

**R = 0.833**, 95% CI **[0.612, 0.987]**. Total gain is well above 2 Success, so R is defined. The interval is entirely below 1, and P5 (R > 1.2 with the CI excluding 1) is **not** supported: on KITTI Car the gap is large on easy frames as well as hard ones. R is secondary and is not a GO / KILL claim. The point × motion grid is also secondary; see `results/kitti_decision/tables.md`.

Pedestrian (not headline): eligible bins pts1, pts2, and motLo also all meet the KILL cell condition, for both families. Van (16 tracklets) and Cyclist (8 tracklets) are under-powered in every bin.

## KITTI-side verdict

**KITTI side of rule: KILL conditions hold on every eligible decision bin** (each bin with ≥ 20% of binned frames and ≥ 30 tracklets has learned − floor Success > 10 and a 95% lower bound > 5). The GO conditions do not hold on KITTI (no eligible bin, including the ≥ 40% low-motion bin, has gap ≤ 5 and a 95% upper bound ≤ 10).

**This KITTI-side result is unchanged.** Combined with the nuScenes half below, the formal first-test decision is **INCONCLUSIVE**.

## Files

- `results/nuscenes_decision/tables.md` — nuScenes aggregate tables (overall, informational V1, per-bin and per-family gaps with CIs, R, formal decision).
- `results/nuscenes_decision/v1_nuscenes.json`, `decision_nuscenes.json`, `summary.json`, `verification.json`.
- `results/nuscenes_decision/nuscenes_{Car,Pedestrian,Truck,Trailer,Bus}_eval.json` — aggregate eval only.
- `results/nuscenes/` — frozen nuScenes floor and controls (unchanged).
- `results/kitti_decision/tables.md` — KITTI aggregate tables (overall, V1, per-bin and per-family gaps with CIs, secondary grid, R).
- `results/kitti_decision/v1_kitti.json`, `decision_kitti.json`, `summary.json`, `mbptrack_yaw_deviation.json`.
- `results/kitti_decision/kitti_{Car,Pedestrian,Van,Cyclist}_eval.json` — aggregate eval only.
- `results/kitti/RUNLOG.md` and `results/nuscenes/RUNLOG.md` — run log entries.
- `results/trackany3d_final/` — TrackAny3D V1, yaw-convention probe, decision cells with TrackAny3D, final verdict (`tables.md`, `summary.json`, `*_eval.json`, `yaw_probe.json`, `RUNLOG.md`, `checksums.txt`). Aggregate only.
- `results/kitti_secondary/` — SECONDARY analyses (KITTI Car): oxts-compensated M2-Track and BAT; see the section below. Does not change the formal decision.

## Secondary analyses (KITTI) — labelled SECONDARY

**This section is SECONDARY / post-primary. It does not change the formal first-test decision (INCONCLUSIVE), the frozen floor, or V1.** Spec: `SECONDARY_ANALYSES.md` #1 and #2. Full tables: `results/kitti_secondary/tables.md`.

GPU Bot's oxts-compensated M2-Track and BAT KITTI Car outputs (`/workspace/gpubot/ic001-sot-kitti/outputs/sec_v1/`) were SHA-256 verified (every brief hash and every `SHA256SUMS_all.txt` entry matched) and re-scored with the same `ic001` path as the primary decision (same bins, Open3DSOT Success, 10,000 tracklet bootstrap, seed 0). Per-frame CSVs are not in the repo. Our scores match GPU Bot's `eval_bins_kitti_Car_secondary.json` exactly (max |Δ| = 0).

Overall (protocol a / ope): M2-Track-oxts **66.45 / 79.05** (native 66.46 / 79.08); BAT **63.17 / 76.07** (native 63.18 / 76.09). Informational only, not a V1 gate: BAT vs paper 60.5 is +2.67 Success; vs the Open3DSOT README checkpoint 65.37 is −2.20 (the README asks for CUDA 10.x; this run was on a free Kaggle T4).

### Gaps vs the floor (Car, ope)

Gap = method − floor (`cv_snap`). High-motion is under-powered (17 tracklets), as in the primary record.

| Method | Bin | Gap | 95% CI | n frames | Share | n tracklets | Eligible for a claim? |
|---|---|---:|---|---:|---:|---:|---|
| M2-Track-oxts | pts0 (<50) | 26.49 | [19.62, 33.83] | 2344 | 37.2% | 99 | yes |
| M2-Track-oxts | pts1 (50–199) | 54.74 | [42.16, 63.10] | 1691 | 26.8% | 107 | yes |
| M2-Track-oxts | pts2 (≥200) | 52.40 | [40.87, 63.02] | 2269 | 36.0% | 91 | yes |
| M2-Track-oxts | motLo (<0.5 m) | 42.33 | [33.85, 49.98] | 4751 | 75.4% | 115 | yes |
| M2-Track-oxts | motHi (≥0.5 m) | 46.64 | [17.70, 64.54] | 1553 | 24.6% | 17 | no |
| BAT | pts0 (<50) | 28.05 | [22.03, 33.96] | 2344 | 37.2% | 99 | yes |
| BAT | pts1 (50–199) | 53.40 | [41.33, 62.45] | 1691 | 26.8% | 107 | yes |
| BAT | pts2 (≥200) | 42.49 | [31.17, 54.33] | 2269 | 36.0% | 91 | yes |
| BAT | motLo (<0.5 m) | 38.66 | [31.56, 45.78] | 4751 | 75.4% | 115 | yes |
| BAT | motHi (≥0.5 m) | 44.29 | [18.39, 61.70] | 1553 | 24.6% | 17 | no |

No eligible bin has a gap near zero. The smallest eligible gap is M2-Track-oxts in the sparse (<50 point) bin, still **+26.49** with a 95% lower bound of 19.62.

Giving M2-Track the ego pose at crop time does not close that gap, or even shrink it reliably: M2-Track-oxts minus plain M2-Track is **−0.96** overall [−4.18, 1.09], **−1.50** in pts<50 [−5.09, 1.81], **−0.55** in high motion (under-powered), and **−0.34** in ego-only frames [−2.65, 1.53]. The intervals cover 0 or sit slightly below it.

### #1 Ego-motion split — NO-GO

The pre-specified test uses Δgap = (uncompensated M2-Track − floor) in ego-only frames minus the same in static/static frames, plus the oxts-compensated gain. Ego cells match the 21 Nov GT census (BEV world × BEV sensor, 0.5 m): static/static 2,474 frames / 36 tracklets; ego-only 2,282 / 98. Co-moving and both-moving stay under-powered.

**Δgap = −0.41**, 95% CI **[−12.74, 14.71]** (|Δgap| < 2; the interval covers 0). The oxts-compensated M2-Track gain on ego-only frames is **−0.34** (<1; overall −0.96). Under the pre-specified rule this is **NO-GO**: ego pose is not the source of the learned−floor gap, which also defuses the fairness objection (the floor uses `oxts`, the learned crop usually does not). The validity check holds: the no-ego floor (frozen control 3) collapses in ego-only frames (floor − no-ego = **+11.07** [7.27, 15.17]) and barely differs in static/static (+1.96, interval covers 0).

### #2 BAT progress anchor (R_progress) — KITTI only, diagnostic

R_progress = (share of the BAT → best-learned gain in primary-hard frames) / (share of frames that are primary-hard), using the frozen P5 formula. Best learned remains MBPTrack (GT-convention yaw).

**R_progress = 0.497**, 95% CI **[0.173, 0.882]**. Total binned gain is 10.69 Success (>2, so R is defined). The interval is entirely below 1, so on KITTI the later gains are not concentrated in hard frames (H-refine direction; H-hard is not supported). This is KITTI-only. SECONDARY #2 also asks for BAT on nuScenes Car; that run is not available, so the pre-specified informative/uninformative call (CI excludes 1 on at least one dataset vs covers 1 on both) is not completed. Floor → best R on these KITTI frames remains **0.833** [0.612, 0.987], matching the primary KITTI record.

