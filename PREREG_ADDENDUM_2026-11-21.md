# IC001 pre-registration addendum, 21 November 2026

**Status: dated addendum to the frozen pre-registration.** This file does **not** edit `PREREG.md`. The frozen pre-registration remains `PREREG.md` on branch `cpu-agent` at commit `e31629c99566bd989094d3a3922374863f0ac163` (hash also recorded in `PREREG.githash` on that branch).

This addendum changes only the **V1 reproduction tolerance** in frozen §10. It does not change bins, thresholds, heading, snap, families, protocols, splits, or the GO / KILL decision rule.

## When this was written

Written on 21 November 2026, **before any learned-tracker output exists**. The GPU jobs for M2-Track and MBPTrack have been specified but have not yet returned scores. A training-free floor has already been scored on KITTI (see branch `cpu-agent`); those scores are not learned-tracker outputs and are not used in V1.

Sudesh approved adding this addendum, and the other paper-strengthening documents in this commit, on 21 November 2026.

## Why the tolerance is being restated

Frozen V1 requires M2-Track and MBPTrack under protocol (a) on KITTI Car to land within **1.0 Success of each paper's published value**. For M2-Track the paper value is **65.5**. The study stops with no tuning if that check fails.

The official Open3DSOT release states that its provided checkpoints "achieve **better** performances than those reported in our main paper," and the README Reproduction table lists M2-Track KITTI Car at **67.43 / 81.04** for `pretrained_models/mmtrack_kitti_car.ckpt`. That is 1.93 Success away from 65.5, so a correct run of the released checkpoint would most likely fail frozen V1 on a technicality. Frozen §10 already noted the 67.43 figure and said it was **not** the V1 reference. This addendum supersedes that choice.

Independent evidence that the released checkpoint scores at the README level, not the paper level: TFTrack (arXiv:2609.07738v1, Table I) reports M2-Track nuScenes Car at 0% masking as **57.21 / 65.73**, which matches the README checkpoint value (**57.22 / 65.72**), not the paper value (**55.85 / 65.09**).

## Verification of 67.43 (and related checkpoint values)

Verified on 21 November 2026 by fetching the Open3DSOT README:

- Live file: https://github.com/Ghostish/Open3DSOT/blob/main/README.md
- Raw fetch: https://raw.githubusercontent.com/Ghostish/Open3DSOT/main/README.md
- Permalink to the last commit that touched that README (9 October 2023): https://github.com/Ghostish/Open3DSOT/blob/f08451ddf133d40c9bfadd6358040c569b5f71a9/README.md

The Reproduction table in that file, checked today, lists:

| Model | Category | Success | Precision | Checkpoint |
|---|---|---|---|---|
| M2Track-KITTI | Car | **67.43** | **81.04** | `pretrained_models/mmtrack_kitti_car.ckpt` |
| M2Track-KITTI | Pedestrian | **60.61** | **89.39** | `pretrained_models/mmtrack_kitti_pedestrian.ckpt` |
| M2Track-NuScenes | Car | **57.22** | **65.72** | `pretrained_models/mmtrack_nuscenes_car.ckpt` |

The README also states that reported checkpoint results were produced on 3090/3080 Ti GPUs and that other GPUs may show minor differences due to precision.

## Restated V1 rule

V1 still gates on **KITTI Car** under protocol (a), as in the frozen pre-registration. The nuScenes Car and KITTI Pedestrian comparisons remain informational and use the same tolerance.

**Pass:** a tracker's reproduced Success is within **1.0** of *either*

1. the paper's published Success, *or*
2. the released checkpoint's documented Success, when such a documented value exists.

**Fail:** the reproduced Success is more than 1.0 away from both references (or from the paper value alone, if no documented checkpoint value exists). Then stop and report; no tuning, as in frozen §10.

Precision figures are recorded below for context and are not a V1 gate.

## Reference values

| Tracker | Dataset / class | Paper Success / Precision | Paper source | Documented checkpoint Success / Precision | Checkpoint source | Role |
|---|---|---|---|---|---|---|
| M2-Track | KITTI Car | **65.5** / 80.8 | Zheng et al., CVPR 2022, arXiv:2203.01730v1, Table 1 (also Table 5 last row: 65.49 / 80.81) | **67.43** / 81.04 | Open3DSOT README Reproduction table, `mmtrack_kitti_car.ckpt` (verified 21 Nov 2026; permalink above) | **V1 gate** |
| MBPTrack | KITTI Car | **73.4** / 84.8 | Xu et al., ICCV 2023, arXiv:2303.05071v1, Table 1 | none found as a separate number | Official README (https://github.com/slothfulxtx/MBPTrack3D, fetched 21 Nov 2026) says pretrained models are provided "to reproduce the performance reported in our paper" and does not list a different Success | **V1 gate** (paper value only, unless a documented checkpoint value later appears) |
| M2-Track | nuScenes Car | 55.85 / 65.09 | arXiv:2203.01730v1, Table 2 | **57.22** / 65.72 | Open3DSOT README, `mmtrack_nuscenes_car.ckpt` (verified as above) | Informational |
| MBPTrack | nuScenes Car | 62.47 / 70.41 | arXiv:2303.05071v1, Table 3 | none found as a separate number | Same MBPTrack README statement as above | Informational |
| M2-Track | KITTI Pedestrian | 61.5 / 88.2 | arXiv:2203.01730v1, Table 1 | **60.61** / 89.39 | Open3DSOT README, `mmtrack_kitti_pedestrian.ckpt` (verified as above) | Informational |
| MBPTrack | KITTI Pedestrian | 68.6 / 93.9 | arXiv:2303.05071v1, Table 1 | none found as a separate number | Same MBPTrack README statement as above | Informational |

For MBPTrack, V1 therefore remains "within 1.0 of the paper value" unless a documented official-checkpoint Success, distinct from the paper, is identified before scoring. If one is, the either-or rule applies in the same way as for M2-Track.

## What this addendum does not do

It does not weaken or alter the GO / KILL rule, the floor definition, or any other frozen choice (a)–(p). Secondary analyses are specified separately in `SECONDARY_ANALYSES.md` and are not part of V1 or of the decision rule.
