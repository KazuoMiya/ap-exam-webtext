#!/usr/bin/env python3
"""ブラウザでの動作テスト（Playwright と Chrome が必要）。先に python3 build.py を実行しておく。
  python3 tools/functest.py
確かめる内容: 全画面の表示、初見の正答率が解き直しで上がらないこと、同じ日の正解では定着にならないこと、
別の日の正解で定着になること、解き直しで選択肢が並べ替えられること、旧形式の記録の読込み。
"""
import asyncio, json, pathlib, sys
from playwright.async_api import async_playwright
ROOT = pathlib.Path(__file__).resolve().parent.parent
URL = "file://" + str(ROOT / "dist/index.html")
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
        pg = await b.new_page(viewport={"width": 1200, "height": 900}); errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.goto(URL); await pg.wait_for_timeout(300)
        chs = await pg.evaluate("DATA.chapters.map(c=>c.id)"); ids = await pg.evaluate("DATA.kamokub.map(k=>k.id)")
        for h in ["home", "info", "howto", "b-method", "kamoku-b", "progress", "practice", "exam"] + ["ch-" + c for c in chs] + ["b-" + i for i in ids]:
            await pg.goto(URL + "#" + h); await pg.wait_for_timeout(40)
            assert await pg.inner_text("#main"), h
        store = lambda: pg.evaluate("JSON.parse(localStorage.getItem('apweb-v1')||'{}')")
        async def run_ch1(answer_correct):
            """第1章の基本を先頭から3問解く。answer_correct が偽なら、わざと間違える。並びを返す。"""
            await pg.goto(URL + "#ch-01"); await pg.wait_for_timeout(100)
            await pg.click("button[data-start='01|1']"); await pg.wait_for_timeout(150); orders = []
            for _ in range(3):
                ks = await pg.eval_on_selector_all("button.choice", "els=>els.map(e=>+e.dataset.k)"); orders.append(ks)
                qa = await pg.evaluate("(()=>{const m=location.hash; const el=document.querySelector('.qcard .num'); return null})()")
                title = await pg.inner_text(".q-body")
                a = await pg.evaluate("t=>DATA.questions.find(q=>{const d=document.createElement('div');d.innerHTML=q.q;return d.textContent.trim()===t.trim()}).a", title)
                pick = a if answer_correct else (a + 1) % 4
                await pg.click(f"button.choice[data-k='{pick}']"); await pg.wait_for_timeout(60)
                await pg.click("button[data-act='next']"); await pg.wait_for_timeout(80)
            return orders
        # 1回目: 3問とも間違える
        o1 = await run_ch1(False); s = await store(); recs = list(s["h"].values())
        assert all(r[3] == 0 and r[2] == 0 for r in recs), recs
        assert all(o == [0, 1, 2, 3] for o in o1), "初回は並べ替えない"
        # 2回目（同じ日）: 3問とも正解。初見の正答率は0%のまま、定着もしない
        o2 = await run_ch1(True); s = await store(); recs = list(s["h"].values())
        assert all(r[3] == 0 and r[2] == 1 and len(r[4]) == 1 for r in recs), recs
        assert all(o != [0, 1, 2, 3] for o in o2), "解き直しは並べ替える"
        await pg.goto(URL + "#progress"); await pg.wait_for_timeout(100); txt = await pg.inner_text("#main")
        assert "初見の正答率" in txt and "0%" in txt
        tiles = await pg.eval_on_selector_all(".tile b", "els=>els.map(e=>e.textContent)")
        assert tiles[1] == "0%" and tiles[2] == "0" and tiles[3] == "3", tiles
        # 別の日に正解したことにして、もう一度正解すると定着になる
        await pg.evaluate("(()=>{const m=JSON.parse(localStorage.getItem('apweb-v1'));for(const k in m.h)m.h[k][4]=['2000-1-1'];localStorage.setItem('apweb-v1',JSON.stringify(m));})()")
        await pg.reload(); await run_ch1(True)
        await pg.goto(URL + "#progress"); await pg.wait_for_timeout(100)
        tiles = await pg.eval_on_selector_all(".tile b", "els=>els.map(e=>e.textContent)")
        assert tiles[1] == "0%" and tiles[2] == "3" and tiles[3] == "0", tiles
        # 旧形式（3要素）の記録を読み込める
        await pg.evaluate("localStorage.setItem('apweb-v1',JSON.stringify({h:{'02-01':[2,2,1],'02-02':[3,1,1]},b:{}}))")
        await pg.reload(); await pg.goto(URL + "#progress"); await pg.wait_for_timeout(100)
        tiles = await pg.eval_on_selector_all(".tile b", "els=>els.map(e=>e.textContent)")
        assert tiles[0].startswith("2 /") and tiles[1] == "50%" and tiles[2] == "0", tiles
        # 模擬試験: 章別の配分
        await pg.goto(URL + "#exam"); await pg.wait_for_timeout(100)
        print("画面", 8 + len(chs) + len(ids), "/ エラー", errs); assert not errs
        await b.close(); print("動作テスト: 問題なし")
asyncio.run(main())
