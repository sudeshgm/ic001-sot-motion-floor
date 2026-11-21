"""Raw val counts (scenes, samples, LIDAR_TOP keyframes, vehicle.car instances/annotations) for a table dir."""
import json, sys, os, gc
d = sys.argv[1]; val = set(open(os.path.join(os.path.dirname(__file__), "..", "ic001", "data", "nuscenes_val_scenes.txt")).read().split())
L = lambda t: json.load(open(os.path.join(d, t + ".json")))
scenes = [s for s in L("scene") if s["name"] in val]; st = {s["token"] for s in scenes}
samples = {s["token"] for s in L("sample") if s["scene_token"] in st}
sd = L("sample_data"); cs = {c["token"]: c["sensor_token"] for c in L("calibrated_sensor")}
lidar = {s["token"] for s in L("sensor") if s["channel"] == "LIDAR_TOP"}
kf = sum(1 for x in sd if x["is_key_frame"] and x["sample_token"] in samples and cs[x["calibrated_sensor_token"]] in lidar); del sd; gc.collect()
car = {c["token"] for c in L("category") if c["name"] == "vehicle.car"}
inst = {i["token"] for i in L("instance") if i["category_token"] in car}
ann = [a for a in L("sample_annotation") if a["sample_token"] in samples and a["instance_token"] in inst]
print(json.dumps({"dir": d, "scenes": len(scenes), "samples": len(samples), "lidar_top_keyframes": kf,
                  "car_instances": len({a["instance_token"] for a in ann}), "car_annotations": len(ann)}))
