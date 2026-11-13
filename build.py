#!/usr/bin/env python3
"""応用情報技術者試験 Webテキストのビルドスクリプト。

src/chapters/NN.md   章本文（先頭にヘッダ、--- 以降が本文Markdown）
src/questions/NN.txt 科目A形式の四肢択一問題
src/kamokub/NN.md    科目B形式の記述式問題
src/pages/*.md       その他のページ
template.html        アプリ本体（/*__DATA__*/ にデータを埋め込む）
"""
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
EXT = ["tables", "fenced_code", "md_in_html", "attr_list", "sane_lists"]

errors = []


def md(text):
    html = markdown.markdown(text.strip(), extensions=EXT, output_format="html")
    return html.replace("<table>", '<div class="tw"><table>').replace("</table>", "</table></div>")


def md_inline(text):
    html = md(text)
    m = re.fullmatch(r"<p>(.*)</p>", html, flags=re.S)
    return m.group(1) if m else html


def split_header(raw):
    head, _, body = raw.partition("\n---\n")
    meta = defaultdict(list)
    for line in head.strip().splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()].append(v.strip())
    return meta, body


def add_section_ids(html, prefix):
    secs = []
    count = [0]

    def rep(m):
        count[0] += 1
        sid = f"{prefix}-s{count[0]}"
        title = re.sub(r"<[^>]+>", "", m.group(1))
        secs.append({"id": sid, "title": title})
        return f'<h2 id="{sid}">{m.group(1)}</h2>'

    html = re.sub(r"<h2>(.*?)</h2>", rep, html)
    return html, secs


def load_chapters():
    chapters = []
    for p in sorted((SRC / "chapters").glob("[0-9][0-9].md")):
        meta, body = split_header(p.read_text(encoding="utf-8"))
        cid = p.stem
        # NN-*.md は補講（ヘッダなし）。番号順に本文の後ろへつなぐ
        for extra in sorted((SRC / "chapters").glob(cid + "-*.md")):
            body += "\n\n" + extra.read_text(encoding="utf-8")
        html, secs = add_section_ids(md(body), f"c{cid}")
        chapters.append({
            "id": cid,
            "no": int(cid),
            "title": meta["title"][0],
            "area": meta["area"][0],
            "syllabus": meta.get("syllabus", [""])[0],
            "goals": meta.get("goal", []),
            "html": html,
            "sections": secs,
        })
    return chapters


KEYS = ["ID", "LV", "Q", "ア", "イ", "ウ", "エ", "正解", "解説"]
KEY_RE = re.compile(r"^(ID|LV|Q|ア|イ|ウ|エ|正解|解説):\s?(.*)$")


def parse_question_block(block, src):
    fields = {}
    cur = None
    for line in block.splitlines():
        m = KEY_RE.match(line)
        if m:
            cur = m.group(1)
            fields[cur] = m.group(2)
        elif cur:
            fields[cur] += "\n" + line
    missing = [k for k in KEYS if k not in fields]
    if missing:
        errors.append(f"{src}: {fields.get('ID', '?')} に {missing} がありません")
        return None
    q = {k: v.strip() for k, v in fields.items()}
    if q["正解"] not in "アイウエ" or len(q["正解"]) != 1:
        errors.append(f"{src}: {q['ID']} の正解が不正です: {q['正解']}")
    if q["LV"] not in ("1", "2", "3"):
        errors.append(f"{src}: {q['ID']} のLVが不正です: {q['LV']}")
    return q


def load_questions(chapter_ids):
    out = []
    seen = set()
    for p in sorted((SRC / "questions").glob("*.txt")):
        ch = p.stem[:2]
        if ch not in chapter_ids:
            errors.append(f"{p.name}: 対応する章がありません")
        raw = p.read_text(encoding="utf-8")
        blocks = [b for b in re.split(r"^---\s*$", raw, flags=re.M) if b.strip()]
        for b in blocks:
            q = parse_question_block(b, p.name)
            if not q:
                continue
            if q["ID"] in seen:
                errors.append(f"ID重複: {q['ID']}")
            seen.add(q["ID"])
            out.append({
                "id": q["ID"],
                "ch": ch,
                "lv": int(q["LV"]),
                "q": md(q["Q"]),
                "c": [md_inline(q[k]) for k in "アイウエ"],
                "a": "アイウエ".index(q["正解"]),
                "e": md(q["解説"]),
            })
    return out


def load_kamokub():
    out = []
    for p in sorted((SRC / "kamokub").glob("*.md")):
        raw = p.read_text(encoding="utf-8")
        parts = re.split(r"^---(本文|設問|解答)\s*(\d*)\s*$", raw, flags=re.M)
        meta = {}
        for line in parts[0].strip().splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip()
        body = ""
        qs = {}
        i = 1
        while i < len(parts):
            kind, num, text = parts[i], parts[i + 1], parts[i + 2]
            if kind == "本文":
                body = md(text)
            elif kind == "設問":
                qs.setdefault(num, {})["q"] = md(text)
            elif kind == "解答":
                qs.setdefault(num, {})["a"] = md(text)
            i += 3
        items = []
        for num in sorted(qs, key=int):
            it = qs[num]
            if "q" not in it or "a" not in it:
                errors.append(f"{p.name}: 設問{num} の設問か解答が欠けています")
                continue
            items.append({"no": int(num), "q": it["q"], "a": it["a"]})
        out.append({
            "id": p.stem,
            "title": meta.get("TITLE", ""),
            "field": meta.get("FIELD", ""),
            "slot": meta.get("SLOT", ""),
            "level": meta.get("LEVEL", ""),
            "time": meta.get("TIME", "30"),
            "lead": meta.get("LEAD", ""),
            "body": body,
            "items": items,
        })
    return out


def load_pages():
    pages = {}
    for p in sorted((SRC / "pages").glob("*.md")):
        meta, body = split_header(p.read_text(encoding="utf-8"))
        html, secs = add_section_ids(md(body), f"p{p.stem}")
        pages[p.stem] = {"title": meta["title"][0], "lead": meta.get("lead", [""])[0], "html": html, "sections": secs}
    return pages


def main():
    chapters = load_chapters()
    ids = {c["id"] for c in chapters}
    questions = load_questions(ids)
    kb = load_kamokub()
    pages = load_pages()

    if errors:
        print("\n".join(errors))
        sys.exit(1)

    data = {"chapters": chapters, "questions": questions, "kamokub": kb, "pages": pages}
    js = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    tpl = (ROOT / "template.html").read_text(encoding="utf-8")
    out = tpl.replace("/*__DATA__*/null", js)
    (ROOT / "dist").mkdir(exist_ok=True)
    (ROOT / "dist" / "index.html").write_text(out, encoding="utf-8")

    # 統計
    per = defaultdict(Counter)
    for q in questions:
        per[q["ch"]][q["lv"]] += 1
    print(f"章 {len(chapters)} / 問題 {len(questions)} / 科目B {len(kb)} / ページ {len(pages)}")
    for c in chapters:
        cnt = per[c["id"]]
        print(f"  {c['id']} {c['title'][:14]:<14} 基本{cnt[1]:>3} 標準{cnt[2]:>3} 上級{cnt[3]:>3} 計{sum(cnt.values()):>3}")
    lv = Counter(q["lv"] for q in questions)
    ans = Counter("アイウエ"[q["a"]] for q in questions)
    area = Counter(next(c["area"] for c in chapters if c["id"] == q["ch"]) for q in questions)
    print("レベル別", dict(sorted(lv.items())), "正解分布", dict(sorted(ans.items())), "系別", dict(area))
    print(f"出力 {len(out) // 1024} KB")


if __name__ == "__main__":
    main()
