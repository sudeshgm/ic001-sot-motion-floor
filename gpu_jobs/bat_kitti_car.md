# GPU job: SECONDARY BAT on KITTI Car (free Kaggle T4)

**Status: SECONDARY.** Not part of the frozen GO / KILL decision, the frozen floor, or V1. Specified in `SECONDARY_ANALYSES.md` #2 (progress anchor / R_progress). Do not apply the V1 stop rule. Label every log line and returned file SECONDARY.

**Why GPU:** same Open3DSOT `pointnet2_ops` CUDA kernels as M2-Track. Inference only; official BAT checkpoint, no retraining.

**No money spent** — free Kaggle T4 only; stop rather than use paid compute. Private dataset only; never make the dataset public.

**Report back to** Idea Launcher (`765e5357-6f2b-4cee-a644-4b9b60b148a5`) **and** IC001 CPU Agent (`d742d08d-3e45-4576-83c9-b477690cb3b5`): raw per-frame CSV, overall Success/Precision (both protocols). Per-bin Success/Precision (for R_progress) is computed on the CPU side from that CSV. Do not return point clouds, features, or dataset files.

## Inputs

- Code: `https://github.com/Ghostish/Open3DSOT` (MIT), **same commit as the M2-Track first test:** `f08451ddf133d40c9bfadd6358040c569b5f71a9`. Check out exactly this commit.
- Official Open3DSOT BAT checkpoint, in the repo at that commit. **Liveness checked 21 Nov 2026 by GitHub API + 1-byte HTTP range request (HTTP 206); do not re-download just to check, and never download a substitute.**

  | File | Size (B) | Open3DSOT README (Reproduction table) |
  |---|---|---|
  | `pretrained_models/bat_kitti_car.ckpt` | 17,834,967 | Success **65.37** / Precision 78.88 |
  | `pretrained_models/bat_kitti_pedestrian.ckpt` | 17,835,145 | 45.74 / 74.53 (informational; not required) |
  | `pretrained_models/bat_nuscenes_car.ckpt` | 17,835,348 | 40.73 / 43.29 (phase 2 only) |

  Permalink: `https://raw.githubusercontent.com/Ghostish/Open3DSOT/f08451ddf133d40c9bfadd6358040c569b5f71a9/pretrained_models/bat_kitti_car.ckpt` (and the pedestrian / nuScenes names in the same folder). Record SHA-256. If a file is unreachable or the size does not match the table: stop and report; never substitute weights.
- Data: private Kaggle dataset `ic001-kitti-0019-0020` (see `gpu_jobs/README.md`; verify the SHA-256 manifest first).
- IC001 repo branch `cpu-agent` → `gpu_jobs/dump_open3dsot.py` (the uncompensated Open3DSOT harness; BAT uses `MatchingBaseModel.build_input_dict` unchanged). `--method bat`.

## Kaggle notebook settings

GPU T4 x1, Internet ON (for git/pip), Persistence off. Add the **private** dataset as input. **Same environment as M2-Track** (`m2track_first_test.md`).

## Setup (cells)

Same as `m2track_first_test.md`, then:

```bash
sha256sum pretrained_models/bat_kitti_car.ckpt
# optional, if running pedestrian in this notebook:
# sha256sum pretrained_models/bat_kitti_pedestrian.ckpt
cd /kaggle/input/ic001-kitti-0019-0020/kitti && sha256sum -c kitti_sha256.txt --quiet && cd -
```

**CUDA caveat (Open3DSOT README):** "In order to reproduce the reported results with the provided checkpoints of BAT, please use CUDA 10.x." A Kaggle T4 is CUDA 11/12 and may drift. Report the reproduced overall Success/Precision and use BAT only as a relative anchor. This is **not** a V1 fail; do not retune, and do not switch CUDA/toolkit just to chase 65.37.

## Steps (KITTI Car; required)

1. In `cfgs/BAT_Car.yaml` set `path: /kaggle/input/ic001-kitti-0019-0020/kitti` and keep `category_name: Car` (leave everything else: `coordinate_mode: velodyne`, `up_axis [0,0,1]`, `IoU_space: 3`, `test_split: test`, `search_bb_scale: 1.25`, `search_bb_offset: 2`, `reference_BB: previous_result`, `shape_aggregation: firstandprevious`, `degrees: True`).
2. **Optional repo self-check (not a V1 gate):** `python main.py --cfg cfgs/BAT_Car.yaml --checkpoint pretrained_models/bat_kitti_car.ckpt --test --workers 2` → record Success/Precision against the README value 65.37 (informational; drift is allowed and must be reported).
3. **Per-frame dump (the job):**
   ```bash
   python /kaggle/working/ic001/gpu_jobs/dump_open3dsot.py \
       --cfg cfgs/BAT_Car.yaml \
       --checkpoint pretrained_models/bat_kitti_car.ckpt \
       --category Car --method bat --protocols ope reinit \
       --path /kaggle/input/ic001-kitti-0019-0020/kitti \
       --out /kaggle/working/bat_kitti_car.csv
   ```
   The printed `ope` Success must equal step 2 if step 2 was run (±0.01); otherwise report the mismatch. CSV `method` must be `bat`.

Pedestrian (`cfgs/BAT_Pedestrian.yaml`, `bat_kitti_pedestrian.ckpt`, informational README 45.74) may be run in the same notebook if time remains; it is not required for #2.

## Phase 2 (nuScenes Car) — only when the private nuScenes dataset exists

`cfgs/BAT_CAR_NUSCENES.yaml`: `path:` = nuScenes root, `version: v1.0-trainval`, `test_split: val`, `key_frame_only: True`; `pip install nuscenes-devkit`; dump with the same harness to `bat_nuscenes_car.csv`, `--method bat`. README anchor 40.73 is informational. Do not start phase 2 until the CPU agent says the private dataset is ready.

## Return

`bat_kitti_car.csv` (and `bat_kitti_pedestrian.csv` only if that optional run was done), step-2 logs if run, harness printouts (overall Success/Precision for `ope` and `reinit`), `pip freeze`, `nvidia-smi`, checkpoint SHA-256s, Open3DSOT commit, wall times, list of environment deviations (including the CUDA version vs the README's 10.x request). Label the report **SECONDARY / not part of the frozen decision**. Nothing else.

## Expected runtime (estimate)

KITTI Car 6,424 frames × 2 protocols: ~5–15 min of inference on a T4; setup ~15 min if the M2-Track env is not reused. **≈ 0.3 T4-h** for the required Car run (about 0.2 T4-h if the environment is already built). Optional Pedestrian would add a similar amount; stay on the free T4 session and stop rather than pay.
