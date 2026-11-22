"""UNTESTED harness (no GPU on the CPU box). Run from the TrackAny3D repo root
after the one-line RECON.py map_location patch (gpu_jobs/trackany3d.md) and with
pretrained/base.pth plus the dataset checkpoint in place:

  python /path/to/ic001/gpu_jobs/dump_trackany3d.py configs/trackany_kitti_all_cfg.yaml \
      --ckpt pretrained/kitti.ckpt --data-root /kaggle/input/ic001-kitti-0019-0020/kitti \
      --category Car --out trackany3d_kitti_car.csv

  python /path/to/ic001/gpu_jobs/dump_trackany3d.py configs/trackany_nuscenes_kitti_all_cfg.yaml \
      --ckpt pretrained/nuscenes.ckpt --data-root /kaggle/working/nuscenes_root \
      --category Car --out trackany3d_nuscenes_car.csv

Protocol 'ope'   : TrackAny3D's own ``forward_on_tracklet`` on the full tracklet.
Protocol 'reinit': for every t >= 1, ``forward_on_tracklet([frame t-1, frame t])``
                   -> memory reset from GT_{t-1} (mask from the GT box), lwh and
                   base box from GT_{t-1} (PREREG choice j); keep the prediction for t.

KITTI boxes come out in the official camera frame; they are converted to the
Open3DSOT velodyne frame (centre via inv(Tr_velo_cam), yaw from the rotated
length axis). Self-check: converted frame-0 GT must equal the velodyne GT that
Open3DSOT/ic001 build (max error printed; must be < 1e-4 m / 1e-4 rad).

nuScenes (NuscenesKITTIMem): boxes are already in the nuScenes **global** frame
(no camera->velodyne conversion). tracklet_id = instance_token. Self-check:
emitted frame-0 boxes vs ic001.data.nuscenes.index_nuscenes GT (centres and yaw);
per-tracklet frame counts are also compared. A failing self-check is reported
and is not silently "fixed".
"""
import argparse
import csv
import logging

import numpy as np

FIELDS = ["dataset", "category", "tracklet_id", "frame_idx", "protocol", "method",
          "cx", "cy", "cz", "w", "l", "h", "yaw"]

METHOD = "trackany3d"


def cam_box_to_velo(b, velo_to_cam):
    Tinv = np.linalg.inv(velo_to_cam)
    c = Tinv[:3, :3] @ np.asarray(b.center) + Tinv[:3, 3]
    R = Tinv[:3, :3] @ b.orientation.rotation_matrix
    yaw = float(np.arctan2(R[1, 0], R[0, 0]))  # direction of the box length axis
    return c, b.wlh, yaw


def velo_gt(anno, velo_to_cam):
    cc = np.array([anno["x"], anno["y"] - anno["height"] / 2, anno["z"], 1.0])
    c = (np.linalg.inv(velo_to_cam) @ cc)[:3]
    yaw = -(anno["rotation_y"] + np.pi / 2)
    return c, float((yaw + np.pi) % (2 * np.pi) - np.pi)


def global_box(b):
    """Emit a TrackAny3D / nuScenes BoundingBox already in the global frame."""
    yaw = float(b.orientation.yaw_pitch_roll[0])
    return np.asarray(b.center, dtype=float), np.asarray(b.wlh, dtype=float), yaw


def _wrap(d):
    return float((d + np.pi) % (2 * np.pi) - np.pi)


def load_nuscenes_index(data_root, category):
    """Load ic001 index_nuscenes (min_points=1, val keyframes). PYTHONPATH must include the ic001 repo root."""
    from ic001.data.nuscenes import index_nuscenes
    trs = index_nuscenes(data_root, category=category, min_points=1, key_frame_only=True)
    return {tr.tracklet_id: tr for tr in trs}


def _run_tracklet(task, tr, proto):
    if proto == "ope":
        return task.forward_on_tracklet(tr)
    preds, gts = [tr[0]["bbox"]], [tr[0]["bbox"]]
    for t in range(1, len(tr)):
        p, g = task.forward_on_tracklet([tr[t - 1], tr[t]])
        preds.append(p[1])
        gts.append(g[1])
    return preds, gts


def main():
    import torch
    import yaml
    from addict import Dict

    from tasks import create_task
    from utils.metrics import TorchPrecision, TorchSuccess, estimateAccuracy, estimateOverlap

    ap = argparse.ArgumentParser()
    ap.add_argument("config")
    ap.add_argument("--ckpt", required=True)
    ap.add_argument("--data-root", required=True)
    ap.add_argument("--category", required=True)
    ap.add_argument("--protocols", nargs="+", default=["ope", "reinit"])
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    cfg = Dict(yaml.load(open(a.config), Loader=yaml.FullLoader))
    cfg.dataset_cfg.data_root_dir = a.data_root
    cfg.dataset_cfg.category_name = a.category
    cfg.phase, cfg.debug, cfg.dataset_cfg.debug, cfg.save_test_result = "test", False, False, False
    log = logging.getLogger("ic001")
    # Constructor loads pretrained/base.pth (hardcoded path, CWD = TrackAny3D root).
    # Official load is strict=False: the frozen Recon backbone may be absent from
    # kitti.ckpt / nuscenes.ckpt and is already filled from base.pth.
    task = create_task(cfg, log)
    sd = torch.load(a.ckpt, map_location="cpu")
    missing, unexpected = task.load_state_dict(sd.get("state_dict", sd), strict=False)
    print("missing keys:", missing)
    print("unexpected keys:", unexpected)
    task = task.cuda().eval()

    dtype = cfg.dataset_cfg.dataset_type
    is_nusc = "Nuscenes" in dtype or "nuscenes" in str(dtype).lower()
    if is_nusc:
        from datasets.nuscenes_kitti_mem import NuscenesKITTIMem
        ds = NuscenesKITTIMem("test", cfg.dataset_cfg, log)
        gt_index = load_nuscenes_index(a.data_root, a.category)
        print(f"index_nuscenes: {len(gt_index)} tracklets for category={a.category}")
        print(f"NuscenesKITTIMem: {ds.num_tracklets()} tracklets")
        max_err = 0.0
        n_missing = 0
        n_count_mismatch = 0
        count_mismatch_examples = []
        with open(a.out, "w", newline="") as f, torch.no_grad():
            w = csv.writer(f)
            w.writerow(FIELDS)
            for proto in a.protocols:
                succ, prec = TorchSuccess(), TorchPrecision()
                for i in range(ds.num_tracklets()):
                    tr = [ds.get_frame(i, j) for j in range(ds.num_tracklet_frames(i))]
                    annos = ds.tracklet_annotations[i]
                    tid = annos[0]["box_anno"]["instance_token"]
                    n_ds = len(tr)
                    gt_tr = gt_index.get(tid)
                    if gt_tr is None:
                        n_missing += 1
                        if n_missing <= 5:
                            print(f"WARNING: instance_token {tid} not in index_nuscenes")
                    elif len(gt_tr) != n_ds:
                        n_count_mismatch += 1
                        if len(count_mismatch_examples) < 8:
                            count_mismatch_examples.append((tid, n_ds, len(gt_tr)))
                    preds, gts = _run_tracklet(task, tr, proto)
                    ov = [estimateOverlap(g, p, dim=cfg.eval_cfg.iou_space, up_axis=cfg.dataset_cfg.up_axis)
                          for p, g in zip(preds, gts)]
                    ac = [estimateAccuracy(g, p, dim=cfg.eval_cfg.iou_space, up_axis=cfg.dataset_cfg.up_axis)
                          for p, g in zip(preds, gts)]
                    succ(torch.tensor(ov))
                    prec(torch.tensor(ac))
                    c0, _, y0 = global_box(gts[0])
                    if gt_tr is not None:
                        gbox = gt_tr.frames[0].gt
                        cg = np.asarray(gbox.center, dtype=float)
                        yg = float(gbox.yaw)
                        dy = abs(_wrap(y0 - yg))
                        dc = float(np.abs(c0 - cg).max())
                        max_err = max(max_err, dc, dy)
                    for k, b in enumerate(preds):
                        c, wlh, yaw = global_box(b)
                        w.writerow(["nuscenes", a.category, tid, k, proto,
                                    METHOD, *map(float, c), *map(float, wlh), yaw])
                print(f"{proto}: Success {float(succ.compute()):.2f} Precision {float(prec.compute()):.2f}")
        print(f"frame-count vs index_nuscenes: missing={n_missing} mismatches={n_count_mismatch}")
        if count_mismatch_examples:
            print("frame-count mismatch examples (instance_token, mem_frames, index_frames):")
            for ex in count_mismatch_examples:
                print("  ", ex)
        print(f"frame-0 global self-check vs index_nuscenes max error: {max_err:.2e} (centres m / yaw rad)")
        return

    assert "KITTI" in dtype, "unknown dataset_type %r (expected KITTI* or NuscenesKITTIMem)" % (dtype,)
    from datasets.kitti_mem import KITTIMem
    ds = KITTIMem("test", cfg.dataset_cfg, log)
    max_err = 0.0
    with open(a.out, "w", newline="") as f, torch.no_grad():
        w = csv.writer(f)
        w.writerow(FIELDS)
        for proto in a.protocols:
            succ, prec = TorchSuccess(), TorchPrecision()
            for i in range(ds.num_tracklets()):
                tr = [ds.get_frame(i, j) for j in range(ds.num_tracklet_frames(i))]
                annos = ds.tracklet_annotations[i]
                scene, tid = int(annos[0]["scene"]), int(annos[0]["track_id"])
                calib = ds.calibration_info.get(scene) or ds._read_calibration_file(
                    "%s/calib/%04d.txt" % (a.data_root, scene))
                v2c = np.vstack((calib["Tr_velo_cam"], [0, 0, 0, 1]))
                preds, gts = _run_tracklet(task, tr, proto)
                ov = [estimateOverlap(g, p, dim=cfg.eval_cfg.iou_space, up_axis=cfg.dataset_cfg.up_axis)
                      for p, g in zip(preds, gts)]
                ac = [estimateAccuracy(g, p, dim=cfg.eval_cfg.iou_space, up_axis=cfg.dataset_cfg.up_axis)
                      for p, g in zip(preds, gts)]
                succ(torch.tensor(ov))
                prec(torch.tensor(ac))
                c0, _, y0 = cam_box_to_velo(gts[0], v2c)
                cg, yg = velo_gt(annos[0], v2c)
                dy = abs(_wrap(y0 - yg))
                max_err = max(max_err, float(np.abs(c0 - cg).max()), dy)
                for k, b in enumerate(preds):
                    c, wlh, yaw = cam_box_to_velo(b, v2c)
                    w.writerow(["kitti", a.category, "%04d_%d" % (scene, tid), k, proto,
                                METHOD, *map(float, c), *map(float, wlh), yaw])
            print(f"{proto}: Success {float(succ.compute()):.2f} Precision {float(prec.compute()):.2f}")
    print(f"frame-0 camera->velodyne self-check max error: {max_err:.2e} (must be < 1e-4)")


if __name__ == "__main__":
    main()
