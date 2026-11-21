# IC001 gate check — "How much of 3D LiDAR single-object tracking is just motion?"
Checked 21 Nov 2026, ~12:45–13:15 IST (Asia/Calcutta), by Idea Launcher's executor. Read-only plus two tiny HTTP reads (HEAD requests and a 2.2 MB zip-directory read). No data, weights or code were downloaded. Nothing was run on GPU.
Canonical evidence: `/workspace/idea_creator/scratch/frozen_rerun_IC001_010_20261116/IC001/idea_writeup_v2.md` (v2), Archive review `/workspace/idea_archive/scratch/ic001_rerun/REVIEW.md` + `r2/`, queue row 18 in `/workspace/idea_creator/ARCHIVE_QUEUE.md`. New evidence from this check: `evidence/` in this folder.

| Gate | Verdict |
|---|---|
| PROMISING | **PASS** |
| NOVELTY-CLEARED | **PASS (re-confirmed 21 Nov; L51 = 3)**, with an R8 scoop risk that keeps growing |
| Main-track strength | **BORDERLINE** — realistic venue RA-L / IROS / ICRA / D&B track; CVPR/ICCV only if the floor ties on ≥50% of frames |
| FEASIBILITY-CHECKED | **PARTIAL** — KITTI part now verified feasible on current disk; nuScenes needs Sudesh's login; execution-dependent checks PENDING |
| LAUNCH-READY | **NOT YET** (borderline + pending decisions; see LAUNCH_PACKET.md) |

## 1. PROMISING — PASS
1. **Failure.** Open3DSOT leaderboards (KITTI, nuScenes) report only frame-weighted mean Success/Precision, and recent papers (TrajTrack 2509.11453, BEVTrack 2309.02185, UniKPT CVPR 2026) attribute their gains to hard (sparse/occluded) frames without any training-free reference point — so nobody knows how much of the score is just motion.
2. **Mechanism.** Most frames are easy (dense points, slow motion), where a constant-velocity box plus a snap to the visible points is already nearly right; frame-weighting mixes this large motion floor with the smaller set of frames where learning actually matters.
3. **Change.** Report a training-free floor (ego-compensated constant velocity + offset-preserving cluster snap, frame-1 GT size) and per-bin gaps on GT-defined point-count × motion bins, plus a released hard-frame split.
4. **Cheapest falsifying test.** On KITTI scenes 0019–0020 and nuScenes val keyframes, run the floor (CPU) and released M2-Track + MBPTrack checkpoints (≤2 T4-h inference). KILL if on both datasets every bin with ≥20% of frames has learned − floor Success > 10 with the 95% lower bound > 5.
- Beyond a trivial ablation: the per-bin share of 2020–25 leaderboard gain is not readable from any paper (no published per-bin P2B vs TrackAny3D table on KITTI/nuScenes). The outcome is genuinely uncertain: TrackAny3D Table 3 (Waymo) shows the largest gain on *Easy*, opposite to the belief.
- Cross-field (L50): not applicable; it is an in-field audit, no imported mechanism.

## 2. NOVELTY-CLEARED — PASS (re-confirmed)
Searches run 21 Nov (files in `evidence/`):
- Semantic Scholar keyword search, 2025–2026, five queries: three returned results (111 unique hits), two stayed rate-limited (HTTP 429) after a retry — their 174-byte error files are kept in `s2_*.json`. The arXiv and citation searches below cover the same ground.
- arXiv API, newest first, five queries: `ax1.xml`–`ax5.xml`. **Newest LiDAR-SOT paper on arXiv is 2609.16695 / 2609.16662 (15 Sep 2026). Nothing in 3D SOT after 16 Nov 2026 was returned.**
- S2 forward citations of LiDAR-SOT 2103.06028 (47), M2-Track 2203.01730 (111), TrackAny3D 2507.19908 (7), TFTrack 2609.07738 (2), GSOT3D 2412.02129 (first call returned 2 citers; the only one dated Aug 2026 or later was PGL-3D 2609.33558, an unrelated 3D visual-query paper; a retry hit HTTP 429 and overwrote the saved file). Citers dated Sep–Nov 2026 are all new trackers: SAVTrack 2609.16662, MAETrack 2609.16695, TFTrack, RP2Track (ACM MM, 9 Nov 2026, no arXiv id), AMPTrack (1 Nov 2026, no arXiv id).
- Two web searches (training-free / constant-velocity baselines for LiDAR SOT).

Closest priors (unchanged from Archive's 16 Nov list; none new):
| Paper | What it shows | Threat |
|---|---|---|
| LiDAR-SOT / SOTracker, Pang et al., IROS 2021, **arXiv:2103.06028** | Training-free tracker ≈ detector+Kalman on the easy third of Waymo vehicle tracklets, much worse on medium/hard (Table I) | Closest tested prior; other scope (Waymo, not learned SOT, own metrics) |
| TFTrack, **arXiv:2609.07738** (7 Sep 2026) | "previous bounding box center encodes sufficient historical context"; M2-Track loses <1% Success with 80% template masking | Newest overlap on the message; learned tracker, not a training-free floor |
| DMT, **arXiv:2203.04232** | Constant-velocity / LSTM motion-only centre gets 37% Precision on KITTI Car vs 79.4 with learned voting | Foreshadows that CV without snap is weak |
| TrajTrack **2509.11453**, BEVTrack **2309.02185**, KITTI-HV **2408.02049**, GSOT3D **2412.02129** | Hard subsets / stratification tools | Tools, no floor |
| Self-Supervised Point Cloud SOT (ICRA 2026, no arXiv id) | Label-free tracker using motion cues + predictive filter | Different claim (a new label-free method); abstract only, already in Creator's work folder |
| RP2Track, AMPTrack (Nov 2026) | New learned trackers | Abstract only; no floor claimed |

What is left (the contribution): the per-bin learned-vs-floor gap on the standard Open3DSOT KITTI/nuScenes Success protocol, against ≥2–3 released learned families, under OPE and one-step re-init, with the normalised share of leaderboard gain that sits in hard bins, and a released hard split.
Limits: new Sep–Nov 2026 papers were checked by abstract only (RP2Track/AMPTrack/Self-Supervised SOT full text not opened). Some S2 calls hit HTTP 429; two keyword queries and the GSOT3D citer retry stayed unanswered. **Scoop risk (R8):** TFTrack's message is close; a training-free floor from another group would scoop the shared message, so speed matters.

## 3. Main-track strength — BORDERLINE
- For: the problem is relevant to every LiDAR-SOT paper; it is cheap and decisive to test; a positive result changes reporting practice (floor + hard split), which is the A2 "simple baseline is the finding" case adopted on 14 Nov.
- Against: it is an audit of one task (old L34/L37 warning, and the reason it was killed on 3 Nov); LiDAR-SOT already predicts the direction; M2-Track already made "motion matters" mainstream. Archive itself rated the venue RA-L / IROS / ICRA or a datasets-and-benchmarks track, with CVPR/ICCV only if the floor ties on ≥50% of frames.
- Honest read: **workshop-plus / RA-L / TMLR-level as expected; main-track only in the strong-positive outcome.** Under the standing rule "ask Sudesh before launching a borderline idea", this needs his explicit go.

## 4. FEASIBILITY-CHECKED — PARTIAL
**Disk (df -h /workspace, 21 Nov 12:4x IST):** 125 G size, 100 G used, **20 G free** (84%).

**KITTI tracking (verified 21 Nov):**
- `data_tracking_velodyne.zip` Content-Length 36,829,852,418 B, **`Accept-Ranges: bytes`**, last modified 11 May 2018.
- Read only the zip central directory over HTTP ranges (2,163,958 B fetched; script `evidence/zip_listing.py`, listing `evidence/kitti_tracking_velodyne_zip_listing.tsv`): 19,151 entries, **all stored uncompressed (method 0)**.
  - `training/velodyne/0019`: 1,060 files, 2,068,608,624 B.
  - `training/velodyne/0020`: 838 files, 1,595,339,312 B.
  - **Total for the Open3DSOT test split: 3,663,947,936 B ≈ 3.66 GB**, which fits in the 20 GB free.
- Labels 2,259,128 B, calib 89,829 B, oxts 8,352,970 B (separate zips).
- So the 16 Nov blocker ("36.8 GB vs ~11 GB free") is resolved *in principle*: a ranged download of just those 1,898 entries is possible. Actually doing it (a 3.7 GB download) is not done here and needs Sudesh's go.
- No public pre-extracted KITTI-tracking 0019–0020 mirror was found (Archive/Creator 16 Nov; not re-searched).

**nuScenes (partly verified):**
- Needs a free nuScenes account + licence acceptance (non-commercial). Open3DSOT's M2-Track nuScenes config uses `version: v1.0-trainval`, `key_frame_only: True`; the loader walks `sample_annotation` → keyframe `LIDAR_TOP`, so **only keyframe LIDAR_TOP + metadata are needed, no sweeps or cameras**.
- Size: an unofficial HF copy (`lanhe1124/data_lidar`, approval-gated) lists all 40,157 keyframe LIDAR_TOP files (trainval + test) as 27,885,183,360 B. With 6,019 val keyframes, val ≈ 6,019 × 694 kB ≈ **4.2 GB (estimate)**, plus trainval metadata (size not checked).
- Catch: the official packs are split by scene into 10 `v1.0-trainval0X_keyframes`/`_blobs` archives, so pulling only val files from the official site may mean downloading larger archives and discarding the rest — exact sizes UNKNOWN until logged in. The HF copy needs owner approval and is still under the nuScenes licence.
- The official mini split is not a substitute (breaks the regime).

**Code and checkpoints (verified via GitHub API / landing pages, nothing downloaded):**
| Family | Code / licence | Checkpoints |
|---|---|---|
| M2-Track | Ghostish/Open3DSOT, MIT | In repo: `mmtrack_kitti_car` 27,073,362 B, `mmtrack_kitti_pedestrian` 27,073,489 B, `mmtrack_nuscenes_car` 27,073,489 B. No Van/Cyclist/nuScenes-Ped checkpoints. (BAT checkpoints also in repo; **no P2B checkpoint**.) |
| MBPTrack | slothfulxtx/MBPTrack3D, **no licence file** (counts as a family under L39) | Google Drive folder lists `mbptrack_kitti_{car,ped,van,cyc}` + nuScenes car/ped/truck/trailer/bus; sizes and download liveness not checked |
| TrackAny3D | sallymmx/TrackAny3D, no licence file | Drive `kitti.ckpt`, `nuscenes.ckpt` (+ RECON backbone) |
| BEVTrack | xmm-prio/BEVTrack | OneDrive returned 403 on 16 Nov → not in first test (Archive fix (c)) |

**CPU vs GPU:**
- CPU (this box: 8 cores, 15 GB RAM, no GPU, no torch installed): the floor, the 3 controls, bin assignment, Success/Precision, bootstrap. Minutes to hours.
- GPU: Open3DSOT requires `pointnet2_ops` (erikwijmans Pointnet2_PyTorch CUDA kernels); MBPTrack pins torch 1.8 + CUDA 11.1 + pytorch3d 0.6.2. So learned-tracker inference is **true GPU work** → GPU Bot on free Kaggle T4. A CPU port of the CUDA ops would change the checkpoints' numbers and is not recommended.
- GPU estimate (Archive's, unverified): first test ≤2 T4-h; full study 6–10 T4-h. **Cost on free Kaggle: $0.** Environment setup for old torch/CUDA pins is the main risk (Archive estimate 1–2 days for 3 envs).

**Still PENDING (need execution, not authorized here):** ranged extraction actually works and matches checksums; checkpoints download and load; Open3DSOT M2-Track reproduces its published KITTI Car Success on 0019–0020 (identity/reproduction test); MBPTrack env builds on Kaggle; nuScenes download path and size.
