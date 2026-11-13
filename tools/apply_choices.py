#!/usr/bin/env python3
"""選択肢の差し替えを適用する。入力は「ID|記号|新しい選択肢」の行。
  python3 tools/apply_choices.py patch.txt
"""
import re, sys, glob, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
patches = {}
for f in sys.argv[1:]:
    for line in open(f, encoding="utf-8"):
        line = line.rstrip("\n")
        if not line.strip(): continue
        i, k, t = line.split("|", 2); patches.setdefault(i, {})[k] = t
done = set()
for p in sorted(glob.glob(str(ROOT / "src/questions/*.txt"))):
    blocks = open(p, encoding="utf-8").read().split("\n---\n"); ch = False
    for n, b in enumerate(blocks):
        m = re.search(r"^ID: (\S+)", b, re.M)
        if m and m.group(1) in patches:
            for k, t in patches[m.group(1)].items():
                b, c = re.subn(r"^" + k + r": .*$", lambda _: k + ": " + t, b, flags=re.M); assert c == 1, (m.group(1), k)
            blocks[n] = b; ch = True; done.add(m.group(1))
    if ch: open(p, "w", encoding="utf-8").write("\n---\n".join(blocks))
missing = set(patches) - done
print("適用", len(done), "問", "見つからないID", sorted(missing))
