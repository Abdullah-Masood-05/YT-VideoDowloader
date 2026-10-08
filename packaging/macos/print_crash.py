"""Print the crashing thread's backtrace from a macOS .ips crash report (CI aid)."""
import json
import sys

header, body = open(sys.argv[1], encoding="utf-8").read().split("\n", 1)
rep = json.loads(body)
print(json.dumps(rep.get("exception"), indent=1), rep.get("termination"))
imgs = rep.get("usedImages", [])
for t in rep.get("threads", []):
    if t.get("triggered"):
        for f in t.get("frames", [])[:40]:
            i = f.get("imageIndex")
            img = imgs[i] if i is not None and i < len(imgs) else {}
            print(img.get("name", "?"), f.get("symbol", hex(f.get("imageOffset", 0))))
