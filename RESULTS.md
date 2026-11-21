# IC001 results — KITTI only (21 November 2026)

**Scope: KITTI only.** Open3DSOT test scenes 0019–0020. The frozen decision rule is defined on both KITTI and nuScenes. The nuScenes floor and learned scores have not been run, so this file records the V1 outcomes and the **KITTI side** of the rule. It does not declare a formal KILL, GO, or INCONCLUSIVE for the first test.

- Pre-registration: `PREREG.md`, frozen at `e31629c` (`PREREG.githash`). This file does not edit it.
- V1 tolerance: approved addendum `PREREG_ADDENDUM_2026-11-21.md` (this file does not edit the addendum either).
- Protocol: standard one-pass evaluation (protocol a / `ope`), headline class **Car**.
- Floor: pre-registered `cv_snap` in `results/kitti/` (unchanged).
- Learned boxes: GPU Bot primary outputs in `/workspace/gpubot/ic001-sot-kitti/outputs/v1/`, SHA-256 verified against `SHA256SUMS_outputs.txt` (all OK). Re-scored with `ic001` metrics (PREREG §6). MBPTrack uses the GT-convention yaw (`mbptrack_yawalt`); see the recorded deviation below.
- Aggregate tables and JSON: `results/kitti_decision/`. Per-frame CSVs are KITTI-derived and are **not** committed.

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

**A formal KILL needs the same on nuScenes, which has not been run.** This is not a formal first-test decision.

## Files

- `results/kitti_decision/tables.md` — all aggregate tables (overall, V1, per-bin and per-family gaps with CIs, secondary grid, R).
- `results/kitti_decision/v1_kitti.json`, `decision_kitti.json`, `summary.json`, `mbptrack_yaw_deviation.json`.
- `results/kitti_decision/kitti_{Car,Pedestrian,Van,Cyclist}_eval.json` — aggregate eval only.
- `results/kitti/RUNLOG.md` — run log entry for this scoring pass.
