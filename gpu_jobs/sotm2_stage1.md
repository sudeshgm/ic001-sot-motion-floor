# GPU job: SOT-M2 Stage 1 pilot — M2-Track fine-tuning arms C, I, D (+ A_ft) on a free T4

**Why GPU:** fine-tuning M2-Track (four arms × 2,000 steps × batch 100) and causal evaluation of six arms.
**No money spent** — free Kaggle T4 only; stop rather than use paid compute. **Private datasets only**
(nuScenes Terms of Use, CC BY-NC-SA 4.0: no redistribution of nuScenes-derived files).
**Pre-registration:** `PREREG_SOTM2_STAGE1.md` (frozen in the same commit as this spec). Plan: `PLAN_SOTM2_TRAINING.md`.
**Hard cap: chunk 1 ≤ 6,900 s wall on one T4 (1.92 T4-h)**, enforced by `driver.sh` (`CAP=6900`). Only chunk 1 is
part of this spec's compute; a resume chunk is a separate run recorded before it starts.

## Pinned code

| Item | Pin |
|---|---|
| IC001 repo, branch `cpu-agent` | harness `d040ba4` (frozen prereg `3a7894a`); code shipped as `code/ic001_sotm2_code.tgz` = `git archive --format=tar.gz -o ic001_sotm2_code.tgz d040ba4 gpu_jobs/sotm2` |
| Open3DSOT | `f08451d` ("Update README.md"), from the existing bundle `open3dsot_f08451d.tarball` |
| Checkpoint | `mmtrack_nuscenes_car.ckpt`, 27,073,489 B, sha256 `3b19f52cc20c07f3f30cc0bf903c50f3bbd7039315785643b21a8a35332f0270` |
| Harness | `gpu_jobs/sotm2/{train_eval.py, geom.py, decide.py, select_scenes.py, driver.sh}` |

No model-code change. The only CPU-only shim (`Tensor.cuda` → identity) is active only with `--device cpu`.

## Environment

The IC001 Plan A environment already used by the kill test: Python 3.8, torch 1.8.0+cu111, pytorch-lightning 1.5.10,
easydict, pyyaml, nuscenes-devkit, pyquaternion, shapely (from the private bundle dataset `ic001-sot-bundle`:
`ic001env.tgz.part*` + `open3dsot_f08451d.tarball`, checked against `BUNDLE_SHA256SUMS.txt`). M2-Track needs no
custom CUDA ops. Kernel: private, GPU T4, internet off is fine (everything is in the datasets), persistence off.
`eval_cfg`-style fallback: if a DataLoader worker crashes (torch 1.8), the driver drops to `WORKERS=0` and repeats
the block from its last checkpoint (deterministic sample stream, so results are unchanged).

## Data

### Box-side preparation (CPU, $0, before the kernel)

| Step | What | Transfer | Stored |
|---|---|---|---|
| P1 | `v1.0-trainval_meta.tgz` (461,678,030 B): extract `v1.0-trainval/*.json`, then `slim_meta.py` → train_track LIDAR_TOP tables in `meta_tt/` | 0.46 GB | 2.6 GB JSON + slim copy |
| P2 | **`v1.0-trainval07_blobs.tgz` (29,534,216,608 B = 27.5 GiB), streamed by `prep_train_crops.py --url` (HTTP Range reconnect; bytes + sha256 in-stream)**; only `train_track` Car tracklet crops (± 5 m) are written; the archive is never stored | **29.5 GB — above the 1 GB per-download limit; P2 does not start until it is cleared** | **done:** 43 complete scenes, 40 chosen, 1,050 tracklets, 221,943 sweeps, 3,073,795,380 B |
| P3 | `select_scenes.pick`: first 40 ranked complete scenes (stop if < 30); list → `data_manifest/sotm2_stage1_train_scenes.txt` | — | — |
| P4 | checkpoint causal sweep-rate rollout on the training tracklets, 8 CPU shards: `train_eval.py rollout --device cpu --shard i/8` | — | 7.9 MB (done, 1,050 tracklets) |
| P5 | evaluation set = kill-test crops (215 `trk_*.npz`, `index.json`, `bins.csv`, `probe_ref_frames.csv`; 1,534,882,802 B) | — | already on the box |
| P6 | build `SOTM2S1_SHA256SUMS.txt` over every file; record train counts (scenes, tracklets, keyframes, sweeps) | — | — |

Commands (P2, on the box; `MIN_FREE_GB` floor as in `scripts/stream_nuscenes.sh`):

```bash
R=/workspace/ic001/runs/sotm2_stage1; export PYTHONPATH=/opt/ic001env/ov_o3d:/workspace/ic001_launch
/opt/ic001env/bin/python -m gpu_jobs.sotm2.prep_train_crops --meta $R/meta_tt --version v1.0-trainval \
     --scenes data_manifest/sotm2_stage1_train_track_rank.txt --work $R/work --out $R/train \
     --url https://motional-nuscenes.s3.amazonaws.com/public/v1.0/v1.0-trainval07_blobs.tgz
for i in 0 1 2 3 4 5 6 7; do /opt/ic001env/bin/python -m gpu_jobs.sotm2.train_eval rollout --device cpu \
  --o3d <Open3DSOT f08451d> --ckpt <ckpt> --data $R/train --out $R/train/rollout --shard $i/8 & done; wait
```

### Private Kaggle dataset `sotm2-stage1-inputs` (new upload; the earlier nuScenes datasets were deleted)

```
SOTM2S1_SHA256SUMS.txt
eval/   trk_000..214.npz, index.json, bins.csv, probe_ref_frames.csv        1.53 GB
train/  trk_0000..1049.npz, index.json, sotm2_stage1_train_scenes.txt, rollout/rollout_{0..7}of8.npz   3.08 GB
ckpt/   mmtrack_nuscenes_car.ckpt                                            27 MB
code/   ic001_sotm2_code.tgz  (git archive d040ba4 gpu_jobs/sotm2)          16 kB
```

**Upload 4,643,684,006 B (4.64 GB) of data files, 1,280 files + `SOTM2S1_SHA256SUMS.txt` + `MANIFEST.md`; upload-ready at `/workspace/ic001/runs/sotm2_stage1/kaggle_inputs/` (checksums also in `data_manifest/sotm2_stage1_kaggle_inputs_sha256.txt`), private (`isPrivate: true`; anonymous access must return 403).** The val-keyframe dataset
`ic001-nuscenes-val-keyframes` (4.04 GiB) is **not** needed. Reused: `ic001-sot-bundle` (environment; must still
exist). Kaggle output download ≈ 0.4 GB (four `*_last.pt` with Adam state ≈ 80 MB each, CSVs).

Known index sha256: `eval/bins.csv` `fd274b41bd070df761656d6ea68da1594f921259cacf5e34b5476dbbb6c7243e`,
`eval/index.json` `7c02a2fa5697fd9315d0dbe5f3903ef03269b17bcb654a0a31f4bb9d20bbdad5`,
`eval/probe_ref_frames.csv` `3015fb1b4d9d7e5dc4459ea535d69e56c4881cdff210249dc260a8b7f6a74012`.

## Kernel steps (chunk 1; `driver.sh`, `CAP=6900`)

1. Locate and verify inputs (`sha256sum -c SOTM2S1_SHA256SUMS.txt`) and the bundle; unpack env, Open3DSOT, code;
   verify checkpoint sha. Any mismatch → stop (rc 20/21/22).
2. **G1:** `eval --arms A,B --tids 12,13` vs `probe_ref_frames.csv`: 82 rows, max |ΔIoU| ≤ 1e-4 (rc 23).
3. Training, round-robin 500-step blocks C → I → D until each has 2,000 steps; checkpoint `models/<arm>_last.pt`
   after every block (atomic rename). Before each block: `time left − 2,400 s eval reserve ≥ slowest block + 60 s`,
   else stop with rc 5 (PARTIAL, resumable). Then A_ft the same way if time allows (skipped A_ft is not a failure).
4. Evaluation on the 215 kill-test tracklets, arms A, B, I, C, D (+ A_ft): `eval/frames.csv`, `eval/b_sweep_boxes.csv`.
5. Row counts: frames = 4,674 × arms (23,370 for five arms; 28,044 with A_ft); b_sweep_boxes = 44,693 (rc 26).
6. `decide.py` → `decision.json`; **G2:** A overall 53.95 ± 0.1 and B 39.40 ± 0.1 (rc 24).
7. `SHA256SUMS_outputs.txt` and `run_meta.txt` (rc, wall, gpu, paid=0, cap, steps, deviations) are written on exit
   in every case.

```bash
# notebook cell
!mkdir -p /tmp/r && tar -xzf /kaggle/input/sotm2-stage1-inputs/code/ic001_sotm2_code.tgz -C /tmp/r && CAP=6900 bash /tmp/r/gpu_jobs/sotm2/driver.sh
```

**Resume (only if chunk 1 ends with rc 5):** upload chunk-1 `out/models/*_last.pt` as private dataset
`sotm2-stage1-state`, run the same kernel with `STATE=/kaggle/input/sotm2-stage1-state`, `CAP` ≤ 6,900.
Completed blocks are not repeated; the sample stream is indexed by global step, so a resumed run equals an
uninterrupted one.

## Expected runtime (estimate)

Box CPU per sample (this harness): A_ft 3.2 ms, I 3.1 ms, C 5.5 ms, D 6.3 ms. With 4 loader workers and a T4
forward/backward of ≈ 0.1–0.15 s per batch of 100: ≈ 0.15–0.25 s/step → 2,000 steps ≈ 5–9 min per arm.
Evaluation ≈ 107k tracker steps (B and I at sweep rate, others at keyframes) ≈ 15–30 min.

| Part | T4-h |
|---|---|
| setup + G1 + one-time training-point cache (5.3 GB, ≈ 150 s) | 0.2–0.3 |
| C, I, D training | 0.3–0.6 |
| A_ft training | 0.1–0.2 |
| evaluation + decide | 0.3–0.5 |
| **chunk 1 total** | **≈ 1.0–1.7 (cap 1.92)** |
| **Stage 1 total** | **≈ 1–2 (one chunk expected; ≤ 3 chunks / 6 T4-h worst case)** |

The plan's rough 10–20 T4-h assumed longer training; this pre-registration fixes a smaller budget (§5).

## Outputs (small files only; never point clouds or dataset files)

`out/`: `eval/frames.csv` (tid,k,arm,iou,dist,cx,cy,cz,yaw), `eval/b_sweep_boxes.csv`, `eval/eval_meta.json`,
`decision.json`, `g1_probe/frames.csv`, `models/<arm>_{last,final}.pt` + `<arm>_train_log.csv`, `logs/`, `status.txt`,
`env_check.txt`, `run_meta.txt`, `SHA256SUMS_outputs.txt`. Fine-tuned weights are nuScenes-derived: keep private.
On the box, re-run `decide.py` on the downloaded `frames.csv`; it must equal `decision.json`.

## After a verified run

Verify `run_meta` rc = 0, `SHA256SUMS_outputs.txt`, row counts and G1/G2 on the box, then **delete the private
dataset**: `kaggle datasets delete -y <owner>/sotm2-stage1-inputs` (and `sotm2-stage1-state` if created); confirm
403 / absent from `kaggle datasets list --mine`. Keep `ic001-sot-bundle`. If rc = 5 and a resume chunk is planned,
keep the dataset until that chunk is verified.

## Risks

- **P2 needs a 29.5 GB stream** (above the 1 GB per-download limit). Blob membership by scene is inferred (blob 07 added no val
  keyframes), not listed; if < 30 complete `train_track` scenes are found the prep stops and a second blob would be
  needed.
- The full metadata (P1) must be re-extracted; the earlier copy was slimmed to val only.
- `ic001-sot-bundle` must still exist on Kaggle; otherwise rebuild the Plan A env (+0.5–1.5 T4-h, would not fit
  chunk 1 with training).
- Kaggle's 2-batch-GPU-session limit has blocked pushes before; do not push repeatedly unattended.
- torch 1.8 DataLoader workers have segfaulted on another job; the driver falls back to 0 workers (slower: may push
  training past the cap → rc 5, resume).
- RAM: training points are 5.3 GB float32, memory-mapped from a one-time cache in `/tmp/sotm2s1/cache` (`SOTM2_CACHE`), shared by loader workers.
- Point budget: busy scenes with 10-sweep buffers are slower per sample than the scene-0655 timing.
- Small data / short training can understate D (KILL is soft, by pre-registration).
