"""UNTESTED harness (no GPU on the CPU box). Run from the Open3DSOT repo root:

  python /path/to/ic001/gpu_jobs/dump_open3dsot.py --cfg cfgs/M2_track_kitti.yaml \
      --checkpoint pretrained_models/mmtrack_kitti_car.ckpt --category Car \
      --method m2track --protocols ope reinit --out m2track_kitti_car.csv

Writes per-frame boxes in the IC001 schema (gpu_jobs/README.md) and prints
Success/Precision recomputed with Open3DSOT's own metric for the OPE run.
Protocol 'reinit': before each frame the tracker's history is replaced by GT.
"""
import argparse
import csv

import torch
import yaml
from easydict import EasyDict

from datasets import get_dataset
from models import get_model
from utils.metrics import TorchPrecision, TorchSuccess, estimateAccuracy, estimateOverlap

FIELDS = ["dataset", "category", "tracklet_id", "frame_idx", "protocol", "method",
          "cx", "cy", "cz", "w", "l", "h", "yaw"]


def tracklet_id(cfg, seq):
    m = seq[0]["meta"]
    if cfg.dataset == "kitti":
        return "%04d_%d" % (int(m["scene"]), int(m["track_id"]))
    return m["box_anno"]["instance_token"]


def run_sequence(net, seq, protocol):
    ious, dists, out = [], [], []
    for t in range(len(seq)):
        gt = seq[t]["3d_bbox"]
        if t == 0:
            out.append(gt)
        else:
            hist = [s["3d_bbox"] for s in seq[:t]] if protocol == "reinit" else out
            data_dict, ref_bb = net.build_input_dict(seq, t, hist)
            out.append(net.evaluate_one_sample(data_dict, ref_box=ref_bb))
        ious.append(estimateOverlap(gt, out[-1], dim=net.config.IoU_space, up_axis=net.config.up_axis))
        dists.append(estimateAccuracy(gt, out[-1], dim=net.config.IoU_space, up_axis=net.config.up_axis))
    return out, ious, dists


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cfg", required=True)
    ap.add_argument("--checkpoint", required=True)
    ap.add_argument("--category", required=True)
    ap.add_argument("--method", required=True)
    ap.add_argument("--path", default=None, help="dataset root (overrides cfg.path)")
    ap.add_argument("--protocols", nargs="+", default=["ope", "reinit"])
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    cfg = EasyDict(yaml.load(open(a.cfg), Loader=yaml.FullLoader))
    cfg.update(dict(category_name=a.category, preloading=False, test=True, checkpoint=a.checkpoint))
    if a.path:
        cfg.path = a.path
    net = get_model(cfg.net_model).load_from_checkpoint(a.checkpoint, config=cfg).cuda().eval()
    data = get_dataset(cfg, type="test", split=cfg.test_split)
    with open(a.out, "w", newline="") as f, torch.no_grad():
        w = csv.writer(f); w.writerow(FIELDS)
        for proto in a.protocols:
            succ, prec = TorchSuccess(), TorchPrecision()
            for i in range(len(data)):
                seq = data[i]
                boxes, ious, dists = run_sequence(net, seq, proto)
                succ(torch.tensor(ious)); prec(torch.tensor(dists))
                tid = tracklet_id(cfg, seq)
                for k, b in enumerate(boxes):
                    w.writerow([cfg.dataset, a.category, tid, k, proto, a.method,
                                *map(float, b.center), *map(float, b.wlh),
                                float(b.orientation.yaw_pitch_roll[0])])
            print(f"{proto}: Success {succ.compute():.2f} Precision {prec.compute():.2f}")


if __name__ == "__main__":
    main()
