# IC001 launch packet (one page), 21 Nov 2026, IST
**Idea:** a training-free motion floor (constant velocity + offset-preserving snap) for LiDAR 3D single-object tracking, and per-bin gaps against released learned trackers on KITTI / nuScenes: how much of the leaderboard is just motion?
**Status:** Archive ACCEPTED 16 Nov (conditional, queue row 18). **Not launched.** Details: `GATES.md`, `PREREG_DRAFT.md`, `PREP_STEPS.md`.

## Overall verdict: BORDERLINE, not LAUNCH-READY yet
It is promising and still novel, and the data blocker is much smaller than recorded, but its main-track strength is borderline and three decisions only Sudesh can make are open.

| Gate | Verdict |
|---|---|
| PROMISING | PASS |
| NOVELTY-CLEARED | PASS (re-checked 21 Nov; nothing new after 16 Nov; closest LiDAR-SOT 2103.06028, TFTrack 2609.07738, DMT 2203.04232) |
| Main-track | BORDERLINE (expected RA-L / IROS / ICRA / D&B; CVPR/ICCV only if floor ties on ≥50% of frames) |
| FEASIBILITY-CHECKED | PARTIAL (KITTI verified; nuScenes needs login; run-time checks pending) |

## What changed since 16 Nov
- **KITTI blocker mostly gone.** The 36.8 GB zip supports byte ranges and stores files uncompressed. The test scenes 0019+0020 are **3.66 GB** (1,898 files), fetchable alone. Free disk is now **20 GB** (was ~11 GB). No deletion is needed.
- **nuScenes:** only val keyframe LiDAR + metadata are needed (≈4.2 GB estimated), but it needs a nuScenes login, and the official archives may force larger downloads (exact size unknown until logged in).

## Plan if Sudesh says go
1. Use the public repo `sudeshgm/ic001-sot-motion-floor` for floor, controls, and metrics on CPU, and for pre-registration rulings and verdicts.
2. Freeze `PREREG_DRAFT.md` (after Sudesh's edits) in the repo with its git hash, before any output.
3. Ranged-download KITTI 0019–0020 + labels/calib/oxts (~3.7 GB) into a local data directory (not /tmp), checksum, run floor + controls.
4. Free Kaggle T4: M2-Track + MBPTrack inference, protocols (a) and (b), ≤2 T4-h estimated. Only per-frame boxes/scores come back. **$0.**
5. Apply the KILL / GO / INCONCLUSIVE rule; report in plain words.

## Decisions needed from Sudesh
1. **Launch despite borderline main-track strength?** (yes / no / park)
2. **Pre-registration:** approve `PREREG_DRAFT.md`, especially the P2B question (no P2B checkpoint in Open3DSOT: use an official P2B checkpoint, BAT → TrackAny3D, or floor → best learned for the first test), and the draft numbers (10,000 bootstrap resamples, V1 reproduction tolerance 1.0 Success).
3. **Data:** OK to download ~3.7 GB of KITTI to the box? Should nuScenes go ahead (needs **your nuScenes account login**), or start KITTI-only and decide nuScenes after the KITTI result? (The KILL/GO rule needs both datasets, so KITTI-only gives an interim read only.)
4. **GPU:** OK to use a free Kaggle T4 (≤2 h first test; ~6–10 h full study). No paid compute is requested.
5. **Repo:** OK to create the public GitHub repo `sudeshgm/ic001-sot-motion-floor` now (prep files only) or at launch.
- Deletion: **none needed.** If space is ever needed, the largest other project folders on the machine (about 18 G and 11 G) should not be touched without your yes. Existing datasets, the Hugging Face cache, and other project data stay.

## Risks
Scoop risk from TFTrack-style work (speed matters); old torch/CUDA pins (MBPTrack torch 1.8 + pytorch3d 0.6.2) may cost 1–2 days of environment setup on Kaggle; MBPTrack/TrackAny3D Drive links not tested for download; MBPTrack and TrackAny3D repos have no licence file.
