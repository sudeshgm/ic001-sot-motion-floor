"""Write train_track, LIDAR_TOP-only nuScenes tables for prep_train_crops.py (tables loaded one at a time).

Kept: scene/sample of the given scenes; sample_data rows of channel LIDAR_TOP (keyframes and sweeps) of those
samples; referenced ego_pose rows; sample_annotation of those samples; instances referenced; calibrated_sensor and
category unchanged. Originals are not modified.

    python -m gpu_jobs.sotm2.slim_meta SRC_ROOT DST_ROOT SCENE_LIST [version]
"""
import gc, json, os, sys


def main(src_root, dst_root, scene_list, version="v1.0-trainval"):
    src = os.path.join(src_root, version); dst = os.path.join(dst_root, version); os.makedirs(dst, exist_ok=True)
    L = lambda n: json.load(open(os.path.join(src, n + ".json")))

    def W(n, rows):
        json.dump(rows, open(os.path.join(dst, n + ".json"), "w")); print(n, len(rows), flush=True)
    names = {l.strip() for l in open(scene_list) if l.strip() and not l.startswith("#")}
    scene = [s for s in L("scene") if s["name"] in names]; W("scene", scene)
    st = {s["token"] for s in scene}
    sample = [s for s in L("sample") if s["scene_token"] in st]; W("sample", sample)
    sa = {s["token"] for s in sample}
    cs_lidar = {c["token"] for c in L("calibrated_sensor")
                if c["sensor_token"] in {s["token"] for s in L("sensor") if s["channel"] == "LIDAR_TOP"}}
    sd = [r for r in L("sample_data") if r["sample_token"] in sa and r["calibrated_sensor_token"] in cs_lidar]
    gc.collect(); W("sample_data", sd)
    ep = {r["ego_pose_token"] for r in sd}
    W("ego_pose", [r for r in L("ego_pose") if r["token"] in ep]); gc.collect()
    ann = [a for a in L("sample_annotation") if a["sample_token"] in sa]; W("sample_annotation", ann); gc.collect()
    it = {a["instance_token"] for a in ann}
    W("instance", [i for i in L("instance") if i["token"] in it])
    for n in ("calibrated_sensor", "category", "sensor"):
        W(n, L(n))


if __name__ == "__main__":
    main(*sys.argv[1:])
