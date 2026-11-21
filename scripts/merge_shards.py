"""Merge floor shard CSVs (written with --shard k/n) back into the unsharded
tracklet order: tracklet i lives in shard i % n at position i // n."""
import csv, sys
out, shards = sys.argv[1], sys.argv[2:]
n = len(shards)
per = []
for p in shards:
    rows = list(csv.reader(open(p)))
    header, body = rows[0], rows[1:]
    order, groups = [], {}
    for r in body:
        if r[2] not in groups:
            order.append(r[2]); groups[r[2]] = []
        groups[r[2]].append(r)
    per.append([groups[t] for t in order])
with open(out, "w", newline="") as f:
    w = csv.writer(f); w.writerow(header)
    i = 0
    while True:
        k, j = i % n, i // n
        if j >= len(per[k]): break
        w.writerows(per[k][j]); i += 1
print("tracklets", i)
