"""1対1の対戦を何試合も回す。

  python3 run.py -a blue_lock -b as_song14 -n 200
  python3 run.py -a blue_lock -b as_song14 --log 1
  python3 run.py --list                    # デッキ一覧
"""
import argparse
import json
import os
import statistics
import sys
from multiprocessing import Pool

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from decks import DECKS, NAMES_JP, make_policy  # noqa: E402
from engine import run_game  # noqa: E402


def play_one(args):
    a, b, i, seed, list_a, list_b, log = args
    pa = make_policy(a, b, list_a, list_b)
    pb = make_policy(b, a, list_b, list_a)
    lists = {}
    if list_a:
        lists[0] = list_a
    if list_b:
        lists[1] = list_b
    g = run_game(a, b, pa, pb, i % 2, seed * 1_000_003 + i, log=log, lists=lists)
    return {"winner": g.winner, "first": i % 2, "turns": g.turn, "lore": [g.players[0].lore, g.players[1].lore],
            "lines": g.lines if log else None}


def matchup(a, b, n, seed=0, list_a=None, list_b=None, procs=4, log=0):
    jobs = [(a, b, i, seed, list_a, list_b, i < log) for i in range(n)]
    if procs > 1 and n >= 8:
        with Pool(procs) as pool:
            res = pool.map(play_one, jobs, chunksize=max(1, n // (procs * 4)))
    else:
        res = [play_one(j) for j in jobs]
    return res


def summarize(res):
    n = len(res)
    w = sum(1 for r in res if r["winner"] == 0)
    l = sum(1 for r in res if r["winner"] == 1)
    on_play = [r for r in res if r["first"] == 0]
    on_draw = [r for r in res if r["first"] == 1]
    return {
        "games": n, "win": w, "loss": l, "draw": n - w - l, "winrate": w / n if n else 0,
        "on_play": sum(1 for r in on_play if r["winner"] == 0) / max(1, len(on_play)),
        "on_draw": sum(1 for r in on_draw if r["winner"] == 0) / max(1, len(on_draw)),
        "avg_turns": statistics.mean(r["turns"] for r in res) if res else 0,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-a", default="blue_lock")
    ap.add_argument("-b", default="as_song14")
    ap.add_argument("-n", type=int, default=200)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--log", type=int, default=0)
    ap.add_argument("--procs", type=int, default=4)
    ap.add_argument("--list-a")
    ap.add_argument("--list-b")
    ap.add_argument("--list", action="store_true")
    args = ap.parse_args()
    if args.list:
        for k, v in DECKS.items():
            print(f"{k:16s} {v['name']}（{v['pair']}）")
        return
    la = open(args.list_a, encoding="utf-8").read() if args.list_a else None
    lb = open(args.list_b, encoding="utf-8").read() if args.list_b else None
    res = matchup(args.a, args.b, args.n, args.seed, la, lb, args.procs, args.log)
    for r in res:
        if r["lines"]:
            print("\n".join(r["lines"]))
            print(f"勝者 P{r['winner']}  ロア {r['lore']}\n")
    s = summarize(res)
    print(f"{NAMES_JP[args.a]} vs {NAMES_JP[args.b]}  {s['games']}試合")
    print(f"  勝率 {s['winrate']:.1%}（先攻 {s['on_play']:.1%} / 後攻 {s['on_draw']:.1%}）引き分け {s['draw']}  平均{s['avg_turns']:.1f}ターン")
    print(json.dumps(s, ensure_ascii=False))


if __name__ == "__main__":
    main()
