"""Fetch the KITTI-tracking Open3DSOT test subset (Velodyne scenes 0019, 0020)
by HTTP range from the official zip, plus label/calib/oxts zips. Verifies each
extracted file against the zip's CRC-32 and size (PREREG V2). Resumable: files
already present with the right size and CRC are skipped.

Usage: python scripts/fetch_kitti_subset.py /workspace/ic001/data/kitti
"""
import io, os, struct, sys, time, urllib.request, zipfile, zlib
from concurrent.futures import ThreadPoolExecutor

BASE = "https://s3.eu-central-1.amazonaws.com/avg-kitti/"
VELO = BASE + "data_tracking_velodyne.zip"
SMALL = ["data_tracking_label_2.zip", "data_tracking_calib.zip", "data_tracking_oxts.zip"]
SCENES = ("0019", "0020")
MAX_TOTAL = 4.2e9  # hard stop (brief: about 4 GB)


def get(url, start=None, end=None, tries=6):
    for k in range(tries):
        try:
            h = {"Range": f"bytes={start}-{end}"} if start is not None else {}
            with urllib.request.urlopen(urllib.request.Request(url, headers=h), timeout=120) as r:
                return r.read()
        except Exception as e:  # retry with backoff
            if k == tries - 1:
                raise
            time.sleep(2 ** k)


class Ranged(io.RawIOBase):
    def __init__(s, u):
        s.u, s.pos = u, 0
        s.size = int(urllib.request.urlopen(urllib.request.Request(u, method="HEAD")).headers["Content-Length"])
    def seekable(s): return True
    def readable(s): return True
    def tell(s): return s.pos
    def seek(s, o, w=0):
        s.pos = o if w == 0 else (s.pos + o if w == 1 else s.size + o); return s.pos
    def readinto(s, b):
        n = min(len(b), s.size - s.pos)
        if n <= 0: return 0
        d = get(s.u, s.pos, s.pos + n - 1); b[:len(d)] = d; s.pos += len(d); return len(d)


def crc_file(p):
    c = 0
    with open(p, "rb") as f:
        for ch in iter(lambda: f.read(1 << 20), b""):
            c = zlib.crc32(ch, c)
    return c & 0xFFFFFFFF


def fetch_entry(info, out_root):
    rel = info.filename.split("training/", 1)[1]
    dst = os.path.join(out_root, rel)
    if os.path.isfile(dst) and os.path.getsize(dst) == info.file_size and crc_file(dst) == info.CRC:
        return rel, 0, "skip"
    assert info.compress_type == 0, info.filename
    span = 30 + len(info.filename.encode()) + 1024 + info.compress_size
    blob = get(VELO, info.header_offset, info.header_offset + span - 1)
    sig, *_ = struct.unpack("<I", blob[:4]); assert sig == 0x04034B50, info.filename
    nlen, xlen = struct.unpack("<HH", blob[26:30])
    data = blob[30 + nlen + xlen: 30 + nlen + xlen + info.compress_size]
    assert len(data) == info.file_size, (info.filename, len(data))
    assert zlib.crc32(data) & 0xFFFFFFFF == info.CRC, "CRC mismatch " + info.filename
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    tmp = dst + ".part"
    with open(tmp, "wb") as f:
        f.write(data)
    os.replace(tmp, dst)
    return rel, len(blob), "ok"


def main(out_root):
    os.makedirs(out_root, exist_ok=True)
    z = zipfile.ZipFile(io.BufferedReader(Ranged(VELO), buffer_size=1 << 20))
    sel = [i for i in z.infolist() if not i.is_dir() and any(
        i.filename.startswith(f"training/velodyne/{s}/") for s in SCENES)]
    total = sum(i.compress_size for i in sel)
    print(f"velodyne entries {len(sel)}, bytes {total}", flush=True)
    if total > MAX_TOTAL:
        sys.exit(f"STOP: {total} B exceeds cap")
    # small zips (whole) -> keep zip + extract training/*
    zdir = os.path.join(os.path.dirname(out_root.rstrip("/")), "zips")
    os.makedirs(zdir, exist_ok=True)
    for name in SMALL:
        zp = os.path.join(zdir, name)
        if not os.path.isfile(zp):
            open(zp, "wb").write(get(BASE + name))
        with zipfile.ZipFile(zp) as sz:
            for i in sz.infolist():
                if i.filename.startswith("training/") and not i.is_dir():
                    dst = os.path.join(out_root, i.filename.split("training/", 1)[1])
                    os.makedirs(os.path.dirname(dst), exist_ok=True)
                    with open(dst, "wb") as f:
                        f.write(sz.read(i))  # zipfile checks CRC on read
        print("small zip ok", name, os.path.getsize(zp), flush=True)
    done = 0
    with ThreadPoolExecutor(6) as ex:
        for k, (rel, n, st) in enumerate(ex.map(lambda i: fetch_entry(i, out_root), sel)):
            done += n
            if k % 100 == 0:
                print(f"{k}/{len(sel)} {rel} {st} fetched {done/1e9:.2f} GB", flush=True)
    with open(os.path.join(out_root, "velodyne_zip_entries.tsv"), "w") as f:
        f.write("path\tsize\tcrc32\n")
        for i in sel:
            f.write(f"{i.filename.split('training/',1)[1]}\t{i.file_size}\t{i.CRC:08x}\n")
    print("DONE all CRC-32 verified", flush=True)


if __name__ == "__main__":
    main(sys.argv[1])
