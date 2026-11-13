#!/usr/bin/env python3
"""科目B演習の数値、SQL、プログラムのトレースを実際に計算して、解答の記載と照合する。
  python3 tools/verify_b.py      食い違いがあれば終了コード1
各項目は「ファイル, 解答に書かれているはずの文字列」。文字列は計算した値から組み立てる。
"""
import sys, math, sqlite3, pathlib, collections
ROOT = pathlib.Path(__file__).resolve().parent.parent
def n(v, d=0):
    s = f"{v:,.{d}f}"
    return s
C = []   # (file, expected string)
def add(f, s): C.append((f, s))

# 02-3 スポーツジム
life = 1 / 0.04; margin = 8000 - 2000
add("02-3", f"**{n(life)}か月**"); add("02-3", f"**{n(margin * life / 1e4)}万円**")
add("02-3", f"**{n(6e6 / 200 / 1e4)}万円**、**{n(6e6 / 200 / margin)}か月**"); add("02-3", f"**{n(margin / 0.03 / 1e4)}万円**")
add("02-3", f"**約{n(round(170 / 0.03, -2))}人**")
# 02-4 ネットスーパー
cm = 5000 * 0.25 - 250 - 600; add("02-4", f"**{n(cm)}円**"); add("02-4", f"**{n(2.4e6 / cm)}件**"); add("02-4", f"**{n((2.4e6 - 4500 * cm) / 1e4)}万円の赤字**")
cmA = 6000 * 0.25 - 850; pA = 4500 * 0.9 * cmA - 2.4e6; add("02-4", f"**{n(cmA)}円**"); add("02-4", f"**{pA / 1e4:g}万円の黒字**")
cmB = cm + 300; add("02-4", f"**{n(cmB)}円**"); add("02-4", f"**{(4500 * 0.8 * cmB - 2.4e6) / 1e4:g}万円の黒字**"); add("02-4", f"**約{n(12e6 / pA)}か月**")
# 03-4 幅優先探索
maze = [[0, 0, 1, 0], [0, 1, 1, 0], [0, 0, 0, 1], [1, 0, 0, 0]]
def bfs():
    dist = [[-1] * 4 for _ in range(4)]; q = collections.deque([(0, 0)]); dist[0][0] = 0; order = []; enq = 1
    while q:
        r, c = q.popleft(); order.append((r + 1, c + 1))
        if (r, c) == (3, 3): return dist[r][c], order, enq
        for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < 4 and 0 <= nc < 4 and maze[nr][nc] == 0 and dist[nr][nc] == -1:
                dist[nr][nc] = dist[r][c] + 1; q.append((nr, nc)); enq += 1
    return -1, order, enq
d, order, enq = bfs()
add("03-4", "、".join(f"({r}, {c})" for r, c in order[:4])); add("03-4", f"**{d}**"); add("03-4", f"**{enq}回**")
# 03-5 2分探索
A = [2, 4, 4, 4, 7, 9, 9]
def lb(key, hi0=None, minus=False):
    lo, hi, mids = 1, (len(A) + 1 if hi0 is None else hi0), []
    while lo < hi:
        mid = (lo + hi) // 2; mids.append(mid)
        if A[mid - 1] < key: lo = mid + 1
        else: hi = mid - 1 if minus else mid
    return lo, mids
r, m = lb(4); add("03-5", "mid：**" + "、".join(map(str, m)) + f"**　戻り値：**{r}**")
add("03-5", f"lowerBound(A, 7, 5)：**{lb(5)[0]}**　countKey(A, 7, 4)：**{lb(5)[0] - lb(4)[0]}**"); add("03-5", f"戻り値：**{lb(10)[0]}**")
add("03-5", f"lowerBound(A, 7, 10)：**{lb(10, 7)[0]}**　countKey(A, 7, 9)：**{lb(10, 7)[0] - lb(9, 7)[0]}**"); add("03-5", f"（2）戻り値：**{lb(4, minus=True)[0]}**")
it, s = 0, 1000000
while s > 0: s //= 2; it += 1
add("03-5", f"**{it}回**")
# 04-2 クラウド移行
add("04-2", f"**{n(2000 * 0.1 * 3 / 60)}件**"); add("04-2", f"**{math.ceil(10 * 0.2 / 0.5 / 2)}台**"); add("04-2", f"**{1 - 0.01 ** 3:.6f}**"); add("04-2", f"**{1 - 0.005 ** 2:.6f}**")
tot = 0.9999 * (1 - 0.01 ** 3) * (1 - 0.005 ** 2); add("04-2", f"≒ {tot:.5f}"); add("04-2", f"約{n((1 - tot) * 365 * 24 * 60)}分")
# 04-3 メッセージキュー
back = (50 - 30) * 600; add("04-3", f"**{n(back)}件**"); add("04-3", f"**{n(back / (30 - 10) / 60)}分**"); add("04-3", f"**約{n(back / 30)}秒**"); add("04-3", f"**{math.ceil(50 / 30 * 10) / 10}倍以上**")
# 05-3 負荷分散
add("05-3", f"**約{5 * 3}秒**"); add("05-3", f"**{n(500 * 200e3 * 8 / 1e6)}Mビット/秒**"); add("05-3", f"**{n(500 * 200e3 * 8 / 1e6 * 0.3)}Mビット/秒**")
# 05-4 NAPT
add("05-4", f"**{n(900 * 40)}個**"); add("05-4", f"ポートの数：**{n(1800 * 40)}個**　グローバルIPアドレス：**{math.ceil(1800 * 40 / 60000)}個**")
add("05-4", f"帯域：**{n(1800 * 0.2)}Mビット/秒**　使用率：**{n(1800 * 0.2 / 500 * 100)}％**"); add("05-4", f"**{math.ceil(1800 * 0.2 / 0.7)}Mビット/秒**")
# 06-3 ポイント
c = sqlite3.connect(":memory:")
c.executescript("""create table 会員(会員番号 text, 氏名 text); insert into 会員 values('M1','青木'),('M2','井上'),('M3','上田');
create table ポイント履歴(履歴番号 int, 会員番号 text, 区分 text, ポイント int);
insert into ポイント履歴 values(1,'M1','付与',500),(2,'M1','利用',200),(3,'M2','付与',300),(4,'M1','付与',100),(5,'M2','利用',300);""")
rows = dict(c.execute("""select 会員.氏名, coalesce(sum(case when ポイント履歴.区分='付与' then ポイント履歴.ポイント else -ポイント履歴.ポイント end),0)
 from 会員 left outer join ポイント履歴 on 会員.会員番号=ポイント履歴.会員番号 group by 会員.会員番号, 会員.氏名""").fetchall())
add("06-3", f"青木：**{rows['青木']}**　井上：**{rows['井上']}**　上田：**{rows['上田']}**")
raw = c.execute("select sum(case when 区分='付与' then ポイント else -ポイント end) from 会員 left outer join ポイント履歴 on 会員.会員番号=ポイント履歴.会員番号 where 会員.氏名='上田'").fetchone()[0]
add("06-3", "（3）**NULL**" if raw is None else "不一致")
# 06-4 在庫
c = sqlite3.connect(":memory:")
c.executescript("""create table 商品(商品番号 text, 商品名 text, 発注点 int); insert into 商品 values('P1','ボールペン',100),('P2','ノート',50),('P3','付箋',30),('P4','ファイル',40);
create table 在庫(商品番号 text, 倉庫番号 text, 数量 int); insert into 在庫 values('P1','W1',60),('P1','W2',30),('P2','W1',40),('P2','W2',20),('P3','W1',10);""")
r1 = c.execute("select 商品.商品番号, sum(在庫.数量) from 商品 inner join 在庫 on 商品.商品番号=在庫.商品番号 group by 商品.商品番号, 商品.発注点 having sum(在庫.数量) < 商品.発注点").fetchall()
add("06-4", "**" + "、".join(f"{a}（合計{b}）" for a, b in r1) + "**")
r2 = c.execute("select 商品.商品番号 from 商品 left outer join 在庫 on 商品.商品番号=在庫.商品番号 group by 商品.商品番号, 商品.発注点 having coalesce(sum(在庫.数量),0) < 商品.発注点").fetchall()
add("06-4", f"（1）**{sorted(set(x[0] for x in r2) - set(a for a, _ in r1))[0]}**")
u = lambda k: c.execute("update 在庫 set 数量=数量-? where 商品番号='P2' and 倉庫番号='W1' and 数量>=?", (k, k)).rowcount
a50, a30 = u(50), u(30); left = c.execute("select 数量 from 在庫 where 商品番号='P2' and 倉庫番号='W1'").fetchone()[0]
add("06-4", f"50個の出庫：**{'できる' if a50 else 'できない'}**　30個の出庫：**{'できる' if a30 else 'できない'}**　実行後の数量：**{left}**")
# 07-2 精算機
add("07-2", f"**約{10 * 3}ミリ秒**"); add("07-2", f"**{2 * 3}秒**"); add("07-2", f"**約{n(2 ** 16 / 1000)}秒**")
# 07-3 給湯器
add("07-3", f"温度：**{587 * 0.1:.1f}℃**"); add("07-3", f"**約{0.1 * 8:.1f}秒**"); j = 2000 * 4.2 * 40
add("07-3", f"**{n(j / 1000)}キロジュール**"); add("07-3", f"**{n(j / 1000)}秒**")
# 08-2 重複の判定（時刻は分で表す）
ov = lambda s, e, ge=False: (s < 660) and ((e >= 600) if ge else (e > 600))
cases = {1: (540, 600), 2: (660, 720), 3: (630, 690), 4: (540, 720)}
add("08-2", "c：**%s**　d：**%s**　e：**%s**" % ("真" if 540 < 660 else "偽", "真" if 720 > 600 else "偽", "登録できない" if ov(540, 720) else "登録できる"))
add("08-2", "番号：**" + "、".join(str(k) for k, (s, e) in cases.items() if ov(s, e) != ov(s, e, True)) + "**")
# 08-3 スクラム
v = (18 + 22 + 20) / 3; add("08-3", f"（1）**{n(v)}**"); add("08-3", f"**{n(120 / v)}スプリント**、**{n(120 / v * 2)}週間**"); add("08-3", f"完成できる：**{n(5 * v)}ポイント**　含められない：**{n(120 - 5 * v)}ポイント**")
# 09-3 CCPM
net = [10 - 4, 8 - 3, 12 - 5]; buf = (4 + 3 + 5) / 2
add("09-3", f"（1）**{10 + 8 + 12}日**"); add("09-3", f"プロジェクトバッファ：**{n(buf)}日**　全体：**{n(sum(net) + buf)}日**")
add("09-3", f"合流バッファ：**{n(2 / 2)}日**　着手：**{n(net[0] + net[1] - 2 / 2 - (6 - 2))}日が経過した時点**")
rem = 3 + net[2]; add("09-3", f"（1）**{round((sum(net) - rem) / sum(net) * 100)}％**")
add("09-3", f"完了の見込み：**{12 + rem}日が経過した時点**　バッファ消費率：**{round((12 + rem - sum(net)) / buf * 100)}％**")
# 09-4 リスク
add("09-4", f"R1：**{n(1000 * 0.3)}万円**　R2：**{n(500 * 0.2)}万円**　R3：**{n(2000 * 0.1)}万円**"); add("09-4", f"（1）**{n(1000 * 0.1)}万円**"); add("09-4", f"効果：**{n(1000 * 0.3 - 1000 * 0.1 - 100)}万円**")
# 10-2 キャパシティ
add("10-2", f"到達：**{n((800 - 600) / 25)}か月後**　発注：**{n((800 - 600) / 25 - 3)}か月後まで**"); t = 3 + (800 - (600 + 75)) / 50
add("10-2", f"（2）**{t:.1f}か月後**"); add("10-2", f"（3）**{t - 3:.1f}か月後まで**"); add("10-2", f"（1）**{n(1.2e6 / 200 / 60)}分**")
add("10-2", f"（2）**{next(k for k in range(1, 99) if (120 + 5 * k) * 1e4 / 200 > 7200)}か月後**"); add("10-2", f"そのまま：**{n(1.8e6 / 200 / 60)}分**　D主任の案：**{n(0.9e6 / 200 / 60)}分**")
# 10-3 災害対策
add("10-3", f"（1）**{2 + 4 + 1 + 0.5 + 1}時間**、**{'満たす' if 8.5 <= 8 else '満たさない'}**"); add("10-3", f"（2）**{4}本**"); add("10-3", f"（1）**{n(0.5 + 0.5 + 1)}時間**")
# 11-3 監査
add("11-3", f"**{30 * 24 * 60 * 0.001:.1f}分**")

# ---- 以前に作成した問題 ----
# 02-1 通信販売への参入
m = 3000 - 1800; add("02-1", f"（1）**{n(24e6 / m)}セット**"); add("02-1", f"（2）**{n((24e6 + 6e6) / m)}セット**"); add("02-1", f"（1）**{n(4 * 3000 * 0.4 * 2.5)}円**")
# 02-2 事業ポートフォリオ
add("02-2", f"**{n(120 / 1500 * 100)}％**"); add("02-2", f"**{1500 / 1000:g}回**"); add("02-2", f"**{n(60 / 400 * 100)}％**")
# 03-1 ランレングス符号化（プログラムを実行）
def encode(s):
    res, i, inc = "", 0, 0
    while i < len(s):
        c, cnt = s[i], 1
        while i + cnt < len(s) and s[i + cnt] == c: cnt += 1; inc += 1
        res += c + str(cnt); i += cnt
    return res, inc
r, inc = encode("WWWWBBW"); add("03-1", f"（1）**{r}**"); add("03-1", f"（2）**{inc}回**")
add("03-1", f"（1）**{len(encode('ABCDE')[0])}文字**（戻り値は {encode('ABCDE')[0]}）"); add("03-1", f"（1）**{encode('1112')[0]}**")
# 03-2 最長共通部分列（表とたどり方を実行）
s_, t_ = "ABCB", "BCAB"; L = [[0] * 5 for _ in range(5)]
for i in range(1, 5):
    for j in range(1, 5):
        L[i][j] = L[i - 1][j - 1] + 1 if s_[i - 1] == t_[j - 1] else max(L[i - 1][j], L[i][j - 1])
add("03-2", f"- ア：**{L[2][4]}**"); add("03-2", f"- イ：**{L[3][2]}**"); add("03-2", f"- ウ：**{L[4][3]}**")
row = lambda i: " | ".join(map(str, L[i]))
add("03-2", f"| 1（A） | {row(1)} |"); add("03-2", f"| 3（C） | {L[3][0]} | {L[3][1]} | イ | {L[3][3]} | {L[3][4]} |"); add("03-2", f"| 4（B） | {L[4][0]} | {L[4][1]} | {L[4][2]} | ウ | {L[4][4]} |")
i, j, res = 4, 4, ""
while i > 0 and j > 0:
    if s_[i - 1] == t_[j - 1]: res = s_[i - 1] + res; i -= 1; j -= 1
    elif L[i - 1][j] >= L[i][j - 1]: i -= 1
    else: j -= 1
add("03-2", f"（2）**{res}**")
# 03-3 最小ヒープ（プログラムを実行）
heap, swaps = [None], 0
def hadd(x):
    global swaps
    heap.append(x); k = len(heap) - 1
    while k > 1 and heap[k // 2] > heap[k]: heap[k // 2], heap[k] = heap[k], heap[k // 2]; k //= 2; swaps += 1
def hpoll():
    top = heap[1]; heap[1] = heap[-1]; heap.pop(); size = len(heap) - 1; k = 1
    while 2 * k <= size:
        c = 2 * k
        if c + 1 <= size and heap[c + 1] < heap[c]: c += 1
        if heap[k] <= heap[c]: break
        heap[k], heap[c] = heap[c], heap[k]; k = c
    return top
for x in (7, 4, 9, 2, 6, 1): hadd(x)
add("03-3", "（1）**" + ", ".join(map(str, heap[1:])) + "**"); add("03-3", f"（2）**{swaps}回**")
p1, p2 = hpoll(), hpoll(); add("03-3", f"1回目：**{p1}**　2回目：**{p2}**"); add("03-3", "（2）**" + ", ".join(map(str, heap[1:])) + "**")
# 04-1 可用性と処理能力
web = 1 - 0.05 ** 2; add("04-1", f"（1）**{0.99 * web * 0.98:.3f}**"); add("04-1", f"（2）**{0.99 * web * (1 - 0.02 ** 2):.3f}**"); add("04-1", f"**{math.ceil(120 / (50 * 0.7))}台**")
# 05-1 サブネット
import ipaddress
nw = ipaddress.ip_network("192.168.20.0/26"); hosts = list(nw.hosts())
add("05-1", f"**{len(hosts)}**"); add("05-1", f"**{hosts[0]}**"); add("05-1", f"{hosts[0]}〜{hosts[-1]}"); add("05-1", f"ブロードキャストアドレスはホスト部をすべて1にした {nw.broadcast_address}")
# 06-1 研修の受講管理
c = sqlite3.connect(":memory:")
c.executescript("""create table 研修(研修コード text, 研修名 text, 定員 int); insert into 研修 values('T01','情報セキュリティ基礎',3),('T02','SQL入門',2),('T03','リーダシップ研修',2);
create table 受講(研修コード text, 社員番号 text); insert into 受講 values('T01','E001'),('T01','E002'),('T02','E001'),('T02','E003');""")
q = "select 研修.研修コード, 研修.定員 - {cnt} from 研修 {join} 受講 on 研修.研修コード=受講.研修コード group by 研修.研修コード, 研修.研修名, 研修.定員 having {cnt} < 研修.定員"
ok = dict(c.execute(q.format(cnt="count(受講.社員番号)", join="left outer join")).fetchall())
inner = dict(c.execute(q.format(cnt="count(受講.社員番号)", join="inner join")).fetchall()); star = dict(c.execute(q.format(cnt="count(*)", join="left outer join")).fetchall())
add("06-1", "正しいSQL文の結果は、" + "と ".join(f"{k}（残席{v}）" for k, v in sorted(ok.items())).replace("）と", "）と"))
add("06-1", f"（3）研修コード：**{sorted(set(ok) - set(inner))[0]}**"); add("06-1", f"（4）残席数：**{star['T03']}**")
# 06-2 チケット予約
c = sqlite3.connect(":memory:")
c.executescript("""create table 会員(会員番号 text, 氏名 text); insert into 会員 values('M1','青木'),('M2','井上'),('M3','上田'),('M4','江藤');
create table 予約(予約番号 int, 会員番号 text, 公演番号 text, 状態 text); insert into 予約 values(1,'M1','K1','確定'),(2,'M1','K2','確定'),(3,'M2','K1','取消'),(4,'M3','K1','確定'),(5,'M2','K2','確定');
create table 予約明細(予約番号 int, 明細番号 int, 公演番号 text, 座席番号 text, 料金 int);
insert into 予約明細 values(1,1,'K1','A1',8000),(1,2,'K1','A2',8000),(2,1,'K2','B1',12000),(2,2,'K2','B2',12000),(3,1,'K1','A3',8000),(4,1,'K1','A3',8000),(5,1,'K2','B3',12000);""")
r = c.execute("""select 会員.氏名, sum(予約明細.料金) as 合計 from 会員 inner join 予約 on 会員.会員番号=予約.会員番号 inner join 予約明細 on 予約.予約番号=予約明細.予約番号
 where 予約.状態='確定' group by 会員.会員番号, 会員.氏名 having sum(予約明細.料金)>=10000 order by 合計 desc""").fetchall()
add("06-2", "（2）" + "、".join(f"**{a} {b:,}**" for a, b in r))
shown = {x[0] for x in c.execute("select 会員.氏名 from 会員 left outer join 予約 on 会員.会員番号=予約.会員番号 where 予約.状態='確定' group by 会員.会員番号, 会員.氏名")}
add("06-2", "（1）氏名：**" + "、".join(sorted({"青木", "井上", "上田", "江藤"} - shown)) + "**")
fixed = c.execute("select count(*) from (select 会員.会員番号 from 会員 left outer join 予約 on 会員.会員番号=予約.会員番号 and 予約.状態='確定' group by 会員.会員番号)").fetchone()[0]
assert fixed == 4, "06-2 修正後のSQL文で全会員が表示されない"
# 07-1 換気制御
add("07-1", f"（1）**{n(2046 / 1023)}ppm**"); add("07-1", f"（2）**{n(450 * 2046 / 1023)}ppm**"); clk = 1e6 / 8
add("07-1", f"設定値：**{n(0.01 * clk)}**　最長の周期：**約{n(2 ** 16 / clk * 1000)}ミリ秒**")
add("07-1", f"（1）**{next(k for k in range(1, 6) if (900 * (5 - k) + 1600 * k) / 5 >= 1500)}回目**")
# 09-1 進捗管理（EVM）
add("09-1", f"**{2000 / 2400:.2f}**"); add("09-1", f"**{2000 / 2200:.2f}**"); add("09-1", f"（1）**{n(4800 / (2000 / 2200))}万円**"); add("09-1", f"（2）**{n(2200 + (4800 - 2000))}万円**")
# 09-2 スケジュール短縮
pa, pb = 10 + 15 + 10 + 8, 10 + 20 + 12 + 8; add("09-2", f"**{max(pa, pb)}日**"); add("09-2", f"**{abs(pa - pb)}日**"); add("09-2", f"**{15 * 2 + 20 * 3}万円**")
# 10-1 サービスレベル
down = 90 + 60 + 90; add("10-1", f"**{n(down / 3)}分**"); add("10-1", f"**{(264 - down / 60) / 264 * 100:.1f}％**"); add("10-1", f"264 × 0.01 ＝ {264 * 0.01}時間（約{n(264 * 0.01 * 60)}分）")

bad = 0
for f, s in C:
    t = (ROOT / "src/kamokub" / (f + ".md")).read_text(encoding="utf-8")
    if s not in t: print("NG", f, "解答に見つからない:", s); bad += 1
print(f"照合 {len(C)}項目（{len(set(f for f, _ in C))}題）  食い違い {bad}")
sys.exit(1 if bad else 0)
