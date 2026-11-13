#!/usr/bin/env python3
"""選択肢の長さの偏りを検出する。
見て分かる手がかり: 正解が単独で最長で、2番目より15%以上かつ6字以上長い。
  python3 tools/tell.py        集計（手がかりが1件でもあれば終了コード1）
  python3 tools/tell.py -v     該当する問題を表示
"""
import re, sys, glob, pathlib, collections
ROOT = pathlib.Path(__file__).resolve().parent.parent
KEYS = "アイウエ"
def plain(s): return re.sub(r"\s+", "", re.sub(r"<[^>]+>", "", s))
def load():
    out = []
    for p in sorted(glob.glob(str(ROOT / "src/questions/*.txt"))):
        for b in open(p, encoding="utf-8").read().split("\n---\n"):
            m = re.search(r"^ID: (\S+)", b, re.M)
            if not m: continue
            out.append(dict(id=m.group(1), file=p, block=b,
                lv=int(re.search(r"^LV: (\d)", b, re.M).group(1)),
                q=re.search(r"^Q: (.*?)(?=^ア: )", b, re.M | re.S).group(1).strip(),
                c=[re.search(r"^" + k + r": (.*)$", b, re.M).group(1) for k in KEYS],
                a=KEYS.index(re.search(r"^正解: (.)", b, re.M).group(1))))
    return out
def is_tell(q):
    l = [len(plain(x)) for x in q["c"]]; s = sorted(l, reverse=True)
    return l[q["a"]] == s[0] and s[0] > s[1] and l[q["a"]] >= s[1] * 1.15 and l[q["a"]] - s[1] >= 6
def main():
    qs = load(); lv = collections.Counter(); longest = collections.Counter(); shortest = collections.Counter(); tells = []
    for q in qs:
        l = [len(plain(x)) for x in q["c"]]; lv[q["lv"]] += 1
        if l[q["a"]] == max(l) and l.count(max(l)) == 1: longest[q["lv"]] += 1
        if l[q["a"]] == min(l) and l.count(min(l)) == 1: shortest[q["lv"]] += 1
        if is_tell(q): tells.append(q)
    n = len(qs)
    for L in (1, 2, 3):
        print(f"Lv{L}: {lv[L]}問  正解が単独最長 {longest[L]} ({round(longest[L]/lv[L]*100)}%)  単独最短 {shortest[L]} ({round(shortest[L]/lv[L]*100)}%)")
    print(f"合計 {n}問  正解が単独最長 {sum(longest.values())} ({round(sum(longest.values())/n*100)}%)  単独最短 {sum(shortest.values())} ({round(sum(shortest.values())/n*100)}%)")
    # 「長い順で k 番目を選ぶ」だけの解き方が、どれだけ当たるか（4択の偶然は25%）
    rank = []
    for k in range(4):
        ok = 0
        for q in qs:
            l = [len(plain(x)) for x in q["c"]]; order = sorted(range(4), key=lambda i: -l[i]); ok += order[k] == q["a"]
        rank.append(round(ok / n * 100))
    print("長い順で k 番目を選んだときの正答率:", " / ".join(f"{k+1}番目 {v}%" for k, v in enumerate(rank)))
    print(f"見て分かる長さの手がかり: {len(tells)} / {n}")
    if max(rank) > 33: print("NG 長さの順位だけで33%を超えて正解できる"); sys.exit(1)
    if "-v" in sys.argv:
        for q in tells:
            print("\n" + q["id"], "LV", q["lv"]); print("Q:", plain(q["q"])[:150])
            for i, x in enumerate(q["c"]): print(("*" if i == q["a"] else " ") + KEYS[i], len(plain(x)), x)
    sys.exit(1 if tells else 0)
if __name__ == "__main__": main()
