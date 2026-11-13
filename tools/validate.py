#!/usr/bin/env python3
"""問題データの整合性を調べる。
  python3 tools/validate.py     問題があれば終了コード1
調べる内容: IDの重複、レベル、選択肢の欠落や重複、解説の有無、正解位置の分布、
同じ章の中でほぼ同じ文面の設問（重複の疑い）。
"""
import re, sys, glob, pathlib, collections, difflib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent)); import tell
ROOT = pathlib.Path(__file__).resolve().parent.parent
qs = tell.load(); bad = []
seen = collections.Counter(q["id"] for q in qs)
bad += [f"IDの重複 {i}" for i, c in seen.items() if c > 1]
for q in qs:
    if q["lv"] not in (1, 2, 3): bad.append(f"{q['id']} レベルが不正")
    if not re.fullmatch(r"\d\d-\d+", q["id"]): bad.append(f"{q['id']} IDの形式が不正")
    if any(not x.strip() for x in q["c"]): bad.append(f"{q['id']} 空の選択肢")
    if len(set(tell.plain(x) for x in q["c"])) < 4: bad.append(f"{q['id']} 同じ選択肢がある")
    m = re.search(r"^解説: (.+)", q["block"], re.M)
    if not m or len(m.group(1)) < 15: bad.append(f"{q['id']} 解説がない、または短い")
by = collections.defaultdict(list)
for q in qs: by[q["id"][:2]].append(q)
for ch, lst in by.items():
    for i, a in enumerate(lst):
        for b in lst[:i]:
            if difflib.SequenceMatcher(None, tell.plain(a["q"]), tell.plain(b["q"])).ratio() >= 0.93 and tell.plain(a["c"][a["a"]]) == tell.plain(b["c"][b["a"]]):
                bad.append(f"重複の疑い {b['id']} と {a['id']}")
pos = collections.Counter(q["a"] for q in qs); lv = collections.Counter(q["lv"] for q in qs)
print(f"合計 {len(qs)}問  基本 {lv[1]} / 標準 {lv[2]} / 上級 {lv[3]}")
print("正解の位置:", " ".join(f"{tell.KEYS[i]}{pos[i]}" for i in range(4)))
if max(pos.values()) - min(pos.values()) > len(qs) * 0.03: bad.append("正解の位置が偏っている（tools/rebalance.py --write を実行する）")
# 字数の制限がない解答例を含む設問（機械的な判定の対象から外す）
NO_LIMIT = {("10-1.md", "4")}
kb = sorted(glob.glob(str(ROOT / "src/kamokub/*.md")))
for p in kb:
    t = open(p, encoding="utf-8").read()
    nq, na = len(re.findall(r"^---設問 \d+", t, re.M)), len(re.findall(r"^---解答 \d+", t, re.M))
    if nq != na or nq == 0: bad.append(f"{pathlib.Path(p).name} 設問と解答の数が合わない")
    parts = re.split(r"^---(設問|解答) (\d+)\n", t, flags=re.M); lim = {}
    for i in range(1, len(parts), 3):
        kind, num, body = parts[i], parts[i + 1], parts[i + 2]
        if kind == "設問": lim[num] = [int(x) for x in re.findall(r"(\d+)字以内", body)]
        elif lim.get(num):
            head = re.split(r"採点のポイント|解説：", body)[0]
            if (pathlib.Path(p).name, num) in NO_LIMIT: continue
            for a in re.findall(r"(?:解答例：|^- )\*\*(.+?)\*\*", head, re.M):
                if len(a) > max(lim[num]): bad.append(f"{pathlib.Path(p).name} 設問{num} の解答例が制限字数を超えている（{len(a)}字）")
print(f"科目B {len(kb)}題")
for b in bad: print("NG", b)
print("問題なし" if not bad else f"問題 {len(bad)}件")
sys.exit(1 if bad else 0)
