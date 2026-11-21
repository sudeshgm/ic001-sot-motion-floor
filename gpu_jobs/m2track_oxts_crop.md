# GPU job: SECONDARY oxts-compensated M2-Track crop on KITTI Car (free Kaggle T4)

**Status: SECONDARY.** Not part of the frozen GO / KILL decision, the frozen floor, or V1. Specified in `SECONDARY_ANALYSES.md` #1. Do not apply the V1 stop rule to this run. Label every log line and returned file SECONDARY.

**Why GPU:** same Open3DSOT `pointnet2_ops` CUDA kernels as the first test. Inference only, with an inference-only adapter (no retraining): the previous box and the previous crop are mapped by KITTI `oxts` \(T_t^{-1} \cdot T_{t-1}\) into the current Velodyne scan before cropping. Box orientation is yaw-only (PREREG choice (o)).

**No money spent** — free Kaggle T4 only; stop rather than use paid compute. Private dataset only; never make the dataset public.

**Report back to** Idea Launcher (`765e5357-6f2b-4cee-a644-4b9b60b148a5`) **and** IC001 CPU Agent (`d742d08d-3e45-4576-83c9-b477690cb3b5`): raw per-frame CSV, overall Success/Precision (both protocols). Per-bin Success/Precision and the ego-only vs static/static split are computed on the CPU side from that CSV; include the CSV so they can do that. Do not return point clouds, features, or dataset files.

## Inputs

- Code: `https://github.com/Ghostish/Open3DSOT` (MIT), **same commit as the first test:** `f08451ddf133d40c9bfadd6358040c569b5f71a9`. Check out exactly this commit.
- Checkpoint: **same as the first test,** `pretrained_models/mmtrack_kitti_car.ckpt` (27,073,362 B), in the repo at that commit. Record SHA-256. Never substitute weights.
- Data: private Kaggle dataset `ic001-kitti-0019-0020`. Verify `sha256sum -c kitti_sha256.txt --quiet` from the `kitti/` root first (any mismatch → stop).
  - **oxts is required.** The planned dataset already includes `oxts/*.txt` (`oxts/0019.txt`, `oxts/0020.txt` are in `data_manifest/kitti_sha256.txt`, ~8.4 MB together with the other scenes). Before this job, confirm those two files exist under the dataset root. If a previously uploaded dataset is missing them, add `oxts/` (at least `0019.txt` and `0020.txt`, plus any other `oxts/` paths listed in the manifest) and re-verify the manifest. Do **not** run with a silent uncompensated fallback.
- IC001 repo (public): `https://github.com/sudeshgm/ic001-sot-motion-floor`, branch `cpu-agent` → `gpu_jobs/dump_open3dsot_oxts.py`.

## Kaggle notebook settings

GPU T4 x1, Internet ON (for git/pip), Persistence off. Add the **private** dataset as input. Same environment as `m2track_first_test.md` (reuse that notebook's env if it is still around).

## Setup (cells)

```bash
git clone https://github.com/Ghostish/Open3DSOT && cd Open3DSOT && git checkout f08451ddf133d40c9bfadd6358040c569b5f71a9
git clone -b cpu-agent https://github.com/sudeshgm/ic001-sot-motion-floor /kaggle/working/ic001
python -c "import torch;print(torch.__version__, torch.version.cuda)"   # keep Kaggle's torch
grep -v -iE "^torch|^torchvision" requirement.txt > req_notorch.txt && pip install -r req_notorch.txt
# if pytorch-lightning from requirement.txt fails to import with Kaggle torch, use the nearest 1.x that does; record it
TORCH_CUDA_ARCH_LIST="7.5" pip install "git+https://github.com/erikwijmans/Pointnet2_PyTorch.git#egg=pointnet2_ops&subdirectory=pointnet2_ops_lib"
sha256sum pretrained_models/mmtrack_kitti_car.ckpt
test -f /kaggle/input/ic001-kitti-0019-0020/kitti/oxts/0019.txt && test -f /kaggle/input/ic001-kitti-0019-0020/kitti/oxts/0020.txt
cd /kaggle/input/ic001-kitti-0019-0020/kitti && sha256sum -c kitti_sha256.txt --quiet && cd -
```

## Steps (KITTI Car only)

1. In `cfgs/M2_track_kitti.yaml` set `path: /kaggle/input/ic001-kitti-0019-0020/kitti` and `category_name: Car` (leave everything else: `coordinate_mode: velodyne`, `up_axis [0,0,1]`, `IoU_space: 3`, `test_split: test`, `bb_scale: 1.25`, `bb_offset: 2`).
2. **Do not** treat this run as V1. (The official `main.py --test` path has no oxts adapter; skip it here.)
3. **Per-frame dump (the job):**
   ```bash
   python /kaggle/working/ic001/gpu_jobs/dump_open3dsot_oxts.py \
       --cfg cfgs/M2_track_kitti.yaml \
       --checkpoint pretrained_models/mmtrack_kitti_car.ckpt \
       --category Car --path /kaggle/input/ic001-kitti-0019-0020/kitti \
       --protocols ope reinit \
       --out /kaggle/working/m2track_oxts_kitti_car.csv
   ```
   The harness prints Open3DSOT Success/Precision for each protocol and writes the IC001 CSV (`method=m2track_oxts`). If oxts files are missing it must exit with an error; do not patch that away.

## Return

`m2track_oxts_kitti_car.csv`, harness printouts (overall Success/Precision for `ope` and `reinit`), `pip freeze`, `nvidia-smi`, checkpoint SHA-256, Open3DSOT commit, wall times, list of environment deviations. Label the report **SECONDARY / not part of the frozen decision**. Nothing else.

## Expected runtime (estimate)

KITTI Car 6,424 frames × 2 protocols: ~5–10 min of inference on a T4; setup ~15 min if the first-test env is not reused. **≈ 0.3 T4-h** (about 0.2 T4-h if the environment is already built).
