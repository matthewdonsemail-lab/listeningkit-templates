import struct, json, glob, os, sys

def parse(path):
    b = open(path, "rb").read()
    # split on tdmn param-name chunks
    parts = b.split(b"\x74\x64\x6d\x6e\x00\x00\x00(")  # "tdmn" + len 0x28 + "("
    out = []
    for seg in parts[1:]:
        name = seg[:40].split(b"\x00")[0].decode("latin1", "replace").strip()
        if not name.startswith("PESS2-"):
            continue
        # find next cdat within this segment
        ci = seg.find(b"cdat")
        if ci < 0:
            continue
        clen = struct.unpack(">I", seg[ci+4:ci+8])[0]
        raw = seg[ci+8:ci+8+clen]
        vals = []
        for i in range(0, len(raw) - (len(raw) % 4), 4):
            vals.append(round(struct.unpack(">f", raw[i:i+4])[0], 4))
        out.append((name, vals))
    return out

# human param name lookup by PESS2 index (from stack order observed)
HUMAN = {
 "PESS2-0000":"?", "PESS2-0002":"Angle", "PESS2-0004":"Distance", "PESS2-0005":"Softness",
 "PESS2-0006":"Color", "PESS2-0016":"Distance2", "PESS2-0017":"Softness2", "PESS2-0018":"Opacity2",
 "PESS2-0008":"Opacity Start", "PESS2-0009":"Opacity End", "PESS2-0027":"Source Opacity",
 "PESS2-0028":"Offset Shadow", "PESS2-0012":"Ease", "PESS2-0011":"EaseMode", "PESS2-0007":"Blend",
 "PESS2-0011 ":"x"
}

files = sorted(glob.glob("*.ffx") + glob.glob("AES Shadow Studio 2 v1.3.4/Presets/*.ffx"))
res = {}
for f in files:
    res[os.path.basename(f)] = parse(f)
print(json.dumps(res, indent=1))
