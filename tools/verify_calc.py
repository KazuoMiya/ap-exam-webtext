#!/usr/bin/env python3
"""計算、進数変換、SQL、トレースの問題について、答えを実際に計算して、正解の選択肢と照合する。
  python3 tools/verify_calc.py      食い違いがあれば終了コード1
各項目は「問題ID: 期待する値を返す関数」。数値は、正解の選択肢の小数のけた数に丸めて比べる。
文字列は、空白と読点を除いて、正解の選択肢に含まれるかどうかを調べる。
"""
import re, sys, math, sqlite3, ipaddress, statistics, itertools, pathlib
from fractions import Fraction as Fr
from math import comb, log2, ceil, sqrt
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import tell

def bits(v, n): return format(v & (2**n - 1), "0%db" % n)
def s8(v): v &= 0xFF; return v - 256 if v >= 128 else v
def lru(refs, n):
    fr, f = [], 0
    for p in refs:
        if p in fr: fr.remove(p); fr.append(p)
        else:
            f += 1
            if len(fr) == n: fr.pop(0)
            fr.append(p)
    return f
def fifo(refs, n):
    fr, f = [], 0
    for p in refs:
        if p not in fr:
            f += 1
            if len(fr) == n: fr.pop(0)
            fr.append(p)
    return f
def probe(keys, size, target):
    t = [None] * size
    for k in keys:
        i = k % size
        while t[i] is not None: i = (i + 1) % size
        t[i] = k
    return t.index(target)
def shortest(edges, s, g):
    nodes = {x for e in edges for x in e[:2]}; d = {n: math.inf for n in nodes}; d[s] = 0
    for _ in nodes:
        for a, b, w in edges:
            d[b] = min(d[b], d[a] + w); d[a] = min(d[a], d[b] + w)
    return d[g]
def cpm(tasks):
    ef = {}
    def f(t):
        if t not in ef: ef[t] = tasks[t][0] + max([f(p) for p in tasks[t][1]] or [0])
        return ef[t]
    for t in tasks: f(t)
    return ef
def rpn(expr):
    st = []
    for tk in expr.split():
        if tk in "+-*/": b, a = st.pop(), st.pop(); st.append(eval(f"{a}{tk}{b}"))
        else: st.append(int(tk))
    return st[0]
def fibcalls(n): return 1 if n <= 1 else 1 + fibcalls(n - 1) + fibcalls(n - 2)
def inversions(a): return sum(1 for i in range(len(a)) for j in range(i + 1, len(a)) if a[i] > a[j])
def collatz(n):
    c = 0
    while n != 1: n = n // 2 if n % 2 == 0 else 3 * n + 1; c += 1
    return c
def bsearch_count(a, key):
    lo, hi, c = 1, len(a), 0
    while lo <= hi:
        mid = (lo + hi) // 2; c += 1
        if a[mid - 1] == key: return c
        if a[mid - 1] < key: lo = mid + 1
        else: hi = mid - 1
def rr(times, q):
    rem = list(times); done = [0] * len(times); t = 0; queue = list(range(len(times)))
    while queue:
        i = queue.pop(0); run = min(q, rem[i]); t += run; rem[i] -= run
        if rem[i]: queue.append(i)
        else: done[i] = t
    return sum(done) / len(done)
def lp_max(obj, cons, lim=200): return max(obj(x, y) for x in range(lim) for y in range(lim) if all(c(x, y) for c in cons))
def heap_pop(a):
    a = a[:]; a[0] = a.pop(); i = 0
    while True:
        l, r = 2 * i + 1, 2 * i + 2; m = i
        if l < len(a) and a[l] > a[m]: m = l
        if r < len(a) and a[r] > a[m]: m = r
        if m == i: return a
        a[i], a[m] = a[m], a[i]; i = m
def automaton(s):
    T = {"S0": {"0": "S0", "1": "S1"}, "S1": {"0": "S2", "1": "S1"}, "S2": {"0": "S0", "1": "S1"}}; st = "S0"
    for ch in s: st = T[st][ch]
    return st == "S2"
EMP = [(1, "青木", "営業", 300), (2, "井上", "営業", 500), (3, "上田", "開発", 400), (4, "江藤", "開発", 600), (5, "小川", "総務", 350)]
def sql(q, setup=None):
    c = sqlite3.connect(":memory:")
    c.execute("create table 社員(社員番号 int, 氏名 text, 部署 text, 給与 int)"); c.executemany("insert into 社員 values(?,?,?,?)", EMP)
    if setup: c.executescript(setup)
    return c.execute(q).fetchall()
DEPT = """create table 部署(部署コード text, 部署名 text); insert into 部署 values('D1','営業'),('D2','開発'),('D3','総務');
create table 社員2(社員番号 int, 氏名 text, 部署コード text); insert into 社員2 values(1,'佐藤','D1'),(2,'鈴木','D2'),(3,'高橋',NULL),(4,'田中','D1');"""
net = ipaddress.ip_network

CHECKS = {
 "01-01": lambda: 0x3A, "01-02": lambda: bits(-1, 8), "01-03": lambda: int("101", 2) / 8, "01-05": lambda: comb(6, 2),
 "01-10": lambda: (12 * 3 / 60) / (1 - 12 * 3 / 60) * 3, "01-11": lambda: 0.5 * 1 + 0.25 * 2 + 0.125 * 3 * 2,
 "01-13": lambda: bits(0b00010110 << 2, 8), "01-15": lambda: 40 / (40 + 20), "01-17": lambda: s8(0b01100100 + 0b00110010),
 "01-18": lambda: -20 >> 2, "01-19": lambda: (0.8 / 0.2) / (0.5 / 0.5), "01-20": lambda: "0110" if automaton("0110") else "受理されない",
 "01-22": lambda: "0." + bits(int(0.6875 * 16), 4), "01-23": lambda: log2(32), "01-27": lambda: str(1 - Fr(5, 6) ** 3),
 "01-28": lambda: str(Fr(comb(7, 2), comb(10, 2))), "01-29": lambda: statistics.pstdev([2, 4, 4, 4, 5, 5, 7, 9]),
 "01-30": lambda: (20 * 2 / 60) / (1 - 20 * 2 / 60) * 2, "01-34": lambda: 2400 * 4, "01-36": lambda: 0.4 * 0.025 / (0.6 * 0.01 + 0.4 * 0.025),
 "01-38": lambda: 2 - (2 * 2 - 2) / (2 * 2), "01-41": lambda: bits(0b1010 ^ 0b0110, 4), "01-42": lambda: 0xA8 / 256,
 "01-43": lambda: -(0.5 * log2(0.5) + 2 * 0.25 * log2(0.25)), "01-45": lambda: rpn("3 4 + 2 * 7 -"), "01-47": lambda: bits(0b1011 ^ (0b1011 >> 1), 4),
 "01-49": lambda: (100 - 95.4) / 2, "01-50": lambda: "A1B" if re.fullmatch(r"[ABC][ABC012]*", "A1B") else "不一致",
 "01-51": lambda: lp_max(lambda x, y: 3 * x + 2 * y, [lambda x, y: 2 * x + y <= 8, lambda x, y: x + 2 * y <= 10], 20), "01-52": lambda: oct(0b110101)[2:],
 "02-04": lambda: sum(range(1, 11, 3)), "02-05": lambda: ceil(log2(1000 + 1)), "02-06": lambda: probe([15, 22, 8, 29], 7, 29), "02-07": lambda: math.gcd(1071, 462),
 "02-10": lambda: (10000 / 1000) ** 2, "02-13": lambda: inversions([5, 3, 4, 1, 2]), "02-14": lambda: fibcalls(5), "02-16": lambda: "2,4,3",
 "02-18": lambda: ",".join(map(str, sorted([5, 3, 8, 1, 4]))), "02-21": lambda: bsearch_count([3, 7, 11, 15, 19, 23, 27, 31], 23), "02-22": lambda: sum(range(7, 0, -2)),
 "02-24": lambda: 2 ** 5 - 1, "02-25": lambda: comb(6, 2), "02-28": lambda: collatz(6), "02-30": lambda: shortest([("A", "B", 2), ("A", "C", 5), ("B", "C", 1), ("B", "D", 4), ("C", "D", 1)], "A", "D"),
 "02-36": lambda: "1,2", "02-38": lambda: sum(1 for k in [12, 7, 22, 15] if k % 5 == 2), "02-40": lambda: 7 // 2,
 "02-42": lambda: __import__("functools").reduce(lambda x, i: x + i if i % 2 == 1 else x * 2, range(1, 6), 0),
 "02-43": lambda: max(itertools.accumulate(1 if c == "(" else -1 for c in "(()())")),
 "02-45": lambda: shortest([("A", "B", 2), ("A", "C", 5), ("B", "C", 2), ("B", "D", 6), ("C", "D", 1)], "A", "D"), "02-47": lambda: 6 * 4 * 2 * 1,
 "02-48": lambda: ",".join(map(str, heap_pop([9, 7, 8, 3, 5]))),
 "03-05": lambda: 1600 / (2 * 0.6 + 5 * 0.4), "03-06": lambda: 0.9 * 10 + 0.1 * 60, "03-07": lambda: (5 + 100 - 1) * 2, "03-12": lambda: 1 / (0.2 + 0.8 / 4),
 "03-13": lambda: (110 - 20) / (110 - 10), "03-14": lambda: 8 + (60000 / 6000) / 2 + 4000 / 50000 * (60000 / 6000), "03-20": lambda: "78563412",
 "03-21": lambda: 4e9 / 100e6, "03-22": lambda: 77 % 16, "03-24": lambda: 4 / 2e9 * 1e9, "03-27": lambda: 1 / 0.1,
 "03-28": lambda: (0.2 * 4 + 0.8 * 2) / (0.2 * 10 + 0.8 * 2) * 100, "03-29": lambda: 50 / (0.95 * 2 + 0.05 * 50), "03-34": lambda: (4 * 1000) / (4 + 1000 - 1),
 "03-35": lambda: 0.9 * 1 + 0.1 * (0.8 * 10 + 0.2 * 100),
 "04-01": lambda: 900 / 1000, "04-06": lambda: (1 - 0.1 ** 2) * 0.95, "04-07": lambda: 2 * (4 - 1), "04-10": lambda: 1 / (2 / 1000),
 "04-13": lambda: 0.9 ** 3 + 3 * 0.9 ** 2 * 0.1, "04-14": lambda: 90 / (90 + 5), "04-17": lambda: 0.9 ** 3, "04-21": lambda: 8760 * 0.001,
 "04-22": lambda: (8760 - 40) / 4, "04-23": lambda: 1 - 0.2 ** 3, "04-24": lambda: 400e6 / 2e6 * 0.8, "04-25": lambda: 6 / 2,
 "04-29": lambda: ceil(900 / (150 * 0.6)) + 1, "04-34": lambda: 1 - sqrt(1 - 0.99), "04-37": lambda: (196 / 200) ** 2,
 "04-38": lambda: next(n for n in range(1, 10) if 1 - 0.1 ** n >= 0.999 - 1e-12), "04-41": lambda: 4 * (1000 / 20) * 0.7,
 "05-06": lambda: lru([1, 2, 3, 1, 4, 1, 2, 5], 3), "05-12": lambda: format({0: 3, 1: 7, 2: 5, 3: 1}[0x2A30 >> 12] << 12 | 0x2A30 & 0xFFF, "X"),
 "05-13": lambda: (2 + 6 + 12) / 3, "05-19": lambda: fifo([1, 2, 3, 1, 4, 1, 2, 5], 3), "05-20": lambda: min(x for x in [30, 10, 50, 20] if x >= 15),
 "05-26": lambda: rr([4, 2, 3], 2), "05-27": lambda: 100 + 10e6 / 10000, "05-30": lambda: lru([4, 1, 2, 4, 3, 1], 3), "05-35": lambda: (0 + 2 + 7) / 3, "05-39": lambda: 32 - 12,
 "06-05": lambda: 8000 * 1 * 60, "06-06": lambda: 44.1 if 44.1 >= 2 * 20 else None, "06-07": lambda: 0.25 / 1 * 100, "06-16": lambda: 5000 / 2 ** 8,
 "06-17": lambda: 44100 * 2 * 2 * 60 / 1e6, "06-18": lambda: 90 / 1.8, "06-19": lambda: 2000 / 0.5 / 24, "06-25": lambda: 16 / 2 ** 4, "06-27": lambda: 0.8 ** 2 * 0.5,
 "07-04": lambda: 1920 * 1080 * 3 * 30 / 1e6, "07-13": lambda: int(2 ** 24 / 1e4), "07-14": lambda: 1024 * 768 * 1 / 1024, "07-15": lambda: (4 + 7 + 2 + 5) % 10,
 "07-17": lambda: (600 * 2) * (600 * 3) * 3 / 1e6,
 "08-08": lambda: len(sql("select 部署.部署名, 社員2.氏名 from 部署 left outer join 社員2 on 部署.部署コード = 社員2.部署コード", DEPT)),
 "08-19": lambda: 3 * 4, "08-23": lambda: len(sql("select 部署, avg(給与) from 社員 group by 部署 having count(*) >= 2")),
 "08-24": lambda: len(sql("select 氏名 from 社員 where 給与 > (select avg(給与) from 社員)")),
 "08-25": lambda: "5、3、20" if sqlite3.connect(":memory:").execute("with t(x) as (values(10),(null),(20),(null),(30)) select count(*), count(x), avg(x) from t").fetchone() == (5, 3, 20.0) else "不一致",
 "08-32": lambda: len(sql("select 氏名 from 社員 S1 where 給与 = (select max(給与) from 社員 S2 where S2.部署 = S1.部署)")),
 "08-37": lambda: ceil(math.log(1e6, 100) - 1e-9), "08-40": lambda: len(sql("select 氏名 from 社員 where 給与 between 350 and 500")),
 "08-41": lambda: len(sql("select 氏名 from 社員 where 氏名 like '%上%'")),
 "08-45": lambda: len(sql("select 部署, max(給与) - min(給与) from 社員 group by 部署 having max(給与) - min(給与) >= 200")),
 "09-04": lambda: "172.20.1.1" if ipaddress.ip_address("172.20.1.1").is_private else "不一致", "09-06": lambda: net("192.168.10.0/26").num_addresses - 2,
 "09-07": lambda: str(ipaddress.ip_interface("172.16.45.130/255.255.255.128").network.network_address), "09-08": lambda: 30 * 8 / (100 * 0.6),
 "09-14": lambda: str(list(ipaddress.collapse_addresses([net("192.168.%d.0/24" % i) for i in range(4)]))[0]), "09-15": lambda: 65536 * 8 / 0.05 / 1e6,
 "09-22": lambda: "/" + str(net("0.0.0.0/255.255.255.240").prefixlen), "09-23": lambda: str(ipaddress.ip_interface("10.1.2.200/27").network.broadcast_address),
 "09-24": lambda: "172.16.10.126" if ipaddress.ip_address("172.16.10.126") in list(ipaddress.ip_interface("172.16.10.100/255.255.255.192").network.hosts()) else "不一致",
 "09-26": lambda: max(((net(n), h) for n, h in [("192.168.0.0/16", "R1"), ("192.168.5.0/24", "R2"), ("192.168.5.128/25", "R3"), ("0.0.0.0/0", "R4")] if ipaddress.ip_address("192.168.5.130") in net(n)), key=lambda x: x[0].prefixlen)[1],
 "09-33": lambda: 1000 * 8 * 2000 / 100e6 * 100, "09-34": lambda: (64000 * 0.02 / 8 + 40) * 8 * (1 / 0.02) / 1000, "09-35": lambda: ceil((4000 - 20) / (1500 - 20)),
 "09-40": lambda: net("192.168.1.64/30").num_addresses - 2, "09-41": lambda: str(ipaddress.ip_interface("192.168.1.77/28").network.network_address),
 "09-45": lambda: 100 * 2 * 0.3, "09-50": lambda: 90 * 8 / (20 * 0.6),
 "11-07": lambda: 2, "11-12": lambda: 2 ** 3, "11-28": lambda: 40 / (16 / 20) - 40, "11-34": lambda: 3 + 1, "11-35": lambda: 2 ** 3,
 "12-05": lambda: (4 + 4 * 7 + 16) / 6, "12-07": lambda: comb(8, 2) - comb(5, 2),
 "12-10": lambda: max(cpm({"A": (3, []), "B": (5, []), "C": (4, ["A"]), "D": (6, ["A"]), "E": (2, ["B", "C"]), "F": (3, ["D"]), "G": (4, ["E"])})[k] for k in "FG"),
 "12-11": lambda: 13 - cpm({"A": (3, []), "D": (6, ["A"]), "F": (3, ["D"])})["F"], "12-12": lambda: 1000 / (400 / 500), "12-13": lambda: -0.3 * 200 + 0.2 * 100,
 "12-18": lambda: 60 / (1.5 * 8), "12-19": lambda: 0.4 * 80 + 0.6 * 40, "12-22": lambda: 24 / 4 - 4, "12-30": lambda: (10 + 4 * 13 + 22) / 6, "12-31": lambda: comb(10, 2),
 "12-33": lambda: max(cpm({"A": (4, []), "B": (3, []), "C": (6, ["A", "B"]), "D": (5, ["C"]), "E": (2, ["C"]), "F": (4, ["E"])})[k] for k in "DF"),
 "12-35": lambda: (16 - 4) / 6, "12-39": lambda: comb(9, 2) - comb(6, 2),
 "13-05": lambda: 30 * 24 * 60 * 0.001, "13-09": lambda: (12 * 20 - 3) / (12 * 20) * 100, "13-15": lambda: 480 + 20, "13-19": lambda: 18 * 30 * 0.005,
 "13-25": lambda: (720 - 3.6) / 720 * 100, "13-30": lambda: 600 * 0.005,
 "15-06": lambda: 1000 / 300, "15-19": lambda: (1500 - 1000) / 1000 * 100, "15-24": lambda: next(i + 1 for i, v in enumerate(itertools.accumulate([200, 400, 600, 600])) if v >= 1200),
 "16-19": lambda: 20 / 10, "17-04": lambda: 50 * 2 - 30 - 20, "17-18": lambda: (100 * 2 - 50) * 3 - 100,
 "18-05": lambda: 10000 - 6000 - 2500 + 300 - 200, "18-06": lambda: 300 / (1 - 600 / 1000), "18-07": lambda: 60 / 500 * 100, "18-08": lambda: 500 / 5,
 "18-09": lambda: 5 * 120 + 10 * 130, "18-12": lambda: lp_max(lambda x, y: 3 * x + 2 * y, [lambda x, y: 2 * x + y <= 100, lambda x, y: x + y <= 80], 101),
 "18-13": lambda: (300 + 100) / 0.4, "18-14": lambda: sqrt(2 * 1800 * 1000 / 40), "18-20": lambda: 100 + 500 - 150, "18-21": lambda: (1000 - 750) / 1000 * 100,
 "18-23": lambda: 1000 * (1 - 0.4) * 0.4, "18-25": lambda: 100 + 0.3 * (120 - 100), "18-27": lambda: 500 + 200 - 300 + 100, "18-28": lambda: 600 / 0.3 - 600 / 0.4,
 "18-31": lambda: 2000000 / (1000 - 600), "18-32": lambda: (90 + 110 + 100) / 3, "18-36": lambda: (600 + 200) / 0.4, "18-37": lambda: 600 / 300 * 100,
 "18-38": lambda: (10 * 100 + 10 * 120) / 20 * 5, "18-39": lambda: 5 * 1.2 * 2,
}

def norm(s): return re.sub(r"[\s、,，]", "", re.sub(r"<[^>]+>", "", s)).replace("−", "-")
def main():
    qs = {q["id"]: q for q in tell.load()}; bad = 0
    for i, f in CHECKS.items():
        if i not in qs: print("NG", i, "問題が見つからない"); bad += 1; continue
        ans = qs[i]["c"][qs[i]["a"]]; v = f()
        if isinstance(v, str): ok = norm(v) in norm(ans)
        else:
            m = re.search(r"-?\d+(?:\.\d+)?", norm(ans)); 
            if not m: ok = False
            else:
                t = m.group(0); dec = len(t.split(".")[1]) if "." in t else 0
                ok = abs(round(float(v) + 1e-9, dec) - float(t)) < 1e-9
        if not ok: print("NG", i, "計算した値", v, "/ 正解の選択肢", ans); bad += 1
    print(f"照合 {len(CHECKS)}問  食い違い {bad}")
    sys.exit(1 if bad else 0)
if __name__ == "__main__": main()
