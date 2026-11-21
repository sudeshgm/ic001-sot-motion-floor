"""UNTESTED harness (no GPU on the CPU box). Run from the MBPTrack3D repo root:

  python /path/to/ic001/gpu_jobs/dump_mbptrack.py configs/mbptrack_kitti_car_cfg.yaml \
      --ckpt pretrained/mbptrack_kitti_car.ckpt --data-root /kaggle/input/ic001-kitti-0019-0020/kitti \
      --category Car --out mbptrack_kitti_car.csv

Protocol 'ope'   : MBPTrack's own ``forward_on_tracklet`` on the full tracklet.
Protocol 'reinit': for every t >= 1, ``forward_on_tracklet([frame t-1, frame t])``
                   -> memory reset from GT_{t-1} (mask from the GT box), lwh and
                   base box from GT_{t-1} (PREREG choice j); keep the prediction for t.
KITTI boxes come out in MBPTrack's camera frame; they are converted to the
Open3DSOT velodyne frame (centre via inv(Tr_velo_cam), yaw from the rotated
length axis). Self-check: converted frame-0 GT must equal the velodyne GT that
Open3DSOT/ic001 build (max error printed; must be < 1e-4 m / 1e-4 rad).
"""
import argparse
import csv
import logging

import numpy as np
import torch
import yaml
from addict import Dict

from tasks import create_task
from utils.metrics import TorchPrecision, TorchSuccess, estimateAccuracy, estimateOverlap

FIELDS = ["dataset", "category", "tracklet_id", "frame_idx", "protocol", "method",
          "cx", "cy", "cz", "w", "l", "h", "yaw"]


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


def main():
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
    task = create_task(cfg, log)
    sd = torch.load(a.ckpt, map_location="cpu")
    missing, unexpected = task.load_state_dict(sd.get("state_dict", sd), strict=False)
    print("missing keys:", missing, "unexpected:", unexpected)
    assert not missing, "checkpoint does not match the model"
    task = task.cuda().eval()
    assert "KITTI" in cfg.dataset_cfg.dataset_type, "nuScenes: see mbptrack_first_test.md step N"
    from datasets.kitti_mem import KITTIMem
    ds = KITTIMem("test", cfg.dataset_cfg, log)
    max_err = 0.0
    with open(a.out, "w", newline="") as f, torch.no_grad():
        w = csv.writer(f); w.writerow(FIELDS)
        for proto in a.protocols:
            succ, prec = TorchSuccess(), TorchPrecision()
            for i in range(ds.num_tracklets()):
                tr = [ds.get_frame(i, j) for j in range(ds.num_tracklet_frames(i))]
                annos = ds.tracklet_annotations[i]
                scene, tid = int(annos[0]["scene"]), int(annos[0]["track_id"])
                calib = ds.calibration_info.get(scene) or ds._read_calibration_file(
                    "%s/calib/%04d.txt" % (a.data_root, scene))
                v2c = np.vstack((calib["Tr_velo_cam"], [0, 0, 0, 1]))
                if proto == "ope":
                    preds, gts = task.forward_on_tracklet(tr)
                else:
                    preds, gts = [tr[0]["bbox"]], [tr[0]["bbox"]]
                    for t in range(1, len(tr)):
                        p, g = task.forward_on_tracklet([tr[t - 1], tr[t]])
                        preds.append(p[1]); gts.append(g[1])
                ov = [estimateOverlap(g, p, dim=cfg.eval_cfg.iou_space, up_axis=cfg.dataset_cfg.up_axis)
                      for p, g in zip(preds, gts)]
                ac = [estimateAccuracy(g, p, dim=cfg.eval_cfg.iou_space, up_axis=cfg.dataset_cfg.up_axis)
                      for p, g in zip(preds, gts)]
                succ(torch.tensor(ov)); prec(torch.tensor(ac))
                c0, _, y0 = cam_box_to_velo(gts[0], v2c)
                cg, yg = velo_gt(annos[0], v2c)
                dy = abs((y0 - yg + np.pi) % (2 * np.pi) - np.pi)
                max_err = max(max_err, float(np.abs(c0 - cg).max()), dy)
                for k, b in enumerate(preds):
                    c, wlh, yaw = cam_box_to_velo(b, v2c)
                    w.writerow(["kitti", a.category, "%04d_%d" % (scene, tid), k, proto,
                                "mbptrack", *map(float, c), *map(float, wlh), yaw])
            print(f"{proto}: Success {float(succ.compute()):.2f} Precision {float(prec.compute()):.2f}")
    print(f"frame-0 camera->velodyne self-check max error: {max_err:.2e} (must be < 1e-4)")


if __name__ == "__main__":
    main()
