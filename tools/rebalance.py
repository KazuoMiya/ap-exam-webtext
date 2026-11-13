#!/usr/bin/env python3
"""正解の選択肢の位置（ア〜エ）の偏りをならす。

数値など順序に意味がある選択肢の問題は動かさない。
それ以外は、正解の選択肢と目標位置の選択肢を入れ替え、解説中の記号の参照も入れ替える。
--write を付けたときだけソースを書き換える。
"""
import random
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
QDIR = ROOT / "src" / "questions"
KANA = "アイウエ"
WRITE = "--write" in sys.argv
random.seed(20261110)

NUMERIC = re.compile(r"^[−\-+]?(約)?[0-9０-９.,]")
REF = re.compile(r"(?<![ァ-ヴー・])([アイウエ])(?=[はのやともをでがにへ、。）)」]|\s|$)")
KEEP = {"18-10", "18-11", "10-61", "09-26", "12-26", "16-22"}  # 選択肢が表の行（A〜D）に対応するもの


def blocks(text):
    return re.split(r"(?m)^---\s*$", text)


def field(block, key):
    m = re.search(rf"(?m)^{key}: ?(.*)$", block)
    return m.group(1).strip() if m else None


def is_fixed(qid, choices):
    if qid in KEEP:
        return True
    return all(NUMERIC.match(c) for c in choices)


def main():
    files = sorted(QDIR.glob("*.txt"))
    data = []
    for f in files:
        bs = blocks(f.read_text(encoding="utf-8"))
        data.append((f, bs))

    total = Counter()
    for f, bs in data:
        for b in bs:
            if not b.strip():
                continue
            ch = [field(b, k) for k in KANA]
            qid = field(b, "ID")
            if is_fixed(qid, ch):
                total[field(b, "正解")] += 1

    changes = 0
    for f, bs in data:
        per = Counter()
        out = []
        for b in bs:
            if not b.strip():
                out.append(b)
                continue
            qid = field(b, "ID")
            ch = [field(b, k) for k in KANA]
            ans = field(b, "正解")
            if is_fixed(qid, ch):
                per[ans] += 1
                out.append(b)
                continue
            order = list(KANA)
            random.shuffle(order)
            target = min(order, key=lambda k: (total[k], per[k]))
            total[target] += 1
            per[target] += 1
            if target == ans:
                out.append(b)
                continue
            i, j = KANA.index(ans), KANA.index(target)
            ci, cj = ch[i], ch[j]
            nb = re.sub(rf"(?m)^{ans}: ?.*$", f"{ans}: {cj}", b, count=1)
            nb = re.sub(rf"(?m)^{target}: ?.*$", f"{target}: {ci}", nb, count=1)
            nb = re.sub(r"(?m)^正解: ?.*$", f"正解: {target}", nb, count=1)
            m = re.search(r"(?ms)^解説: ?(.*)$", nb)
            exp = m.group(1)
            swap = {ans: target, target: ans}
            new_exp = REF.sub(lambda mm: swap.get(mm.group(1), mm.group(1)), exp)
            nb = nb[: m.start(1)] + new_exp + nb[m.end(1):]
            if exp != new_exp:
                refs = [x.group(0) + exp[x.end(): x.end() + 3] for x in REF.finditer(exp)]
                print(f"{qid}: {ans}->{target} 解説の参照 {refs}")
            else:
                print(f"{qid}: {ans}->{target}")
            changes += 1
            out.append(nb)
        if WRITE:
            f.write_text("---".join(out), encoding="utf-8")
    print("変更", changes, "件 / 分布", dict(sorted(total.items())))


if __name__ == "__main__":
    main()
