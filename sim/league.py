"""総当たり戦で相性表を作る。

  python3 league.py -n 100            # 全デッキ総当たり（各組み合わせ100試合）
  python3 league.py -n 100 --decks blue_lock,emerald_lock,as_song14
"""
import argparse
import itertools
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from decks import DECKS, NAMES_JP  # noqa: E402
from run import matchup, summarize  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-n", type=int, default=100)
    ap.add_argument("--decks")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "results", "league.json"))
    args = ap.parse_args()
    keys = args.decks.split(",") if args.decks else list(DECKS)
    table = {a: {} for a in keys}
    t0 = time.time()
    for a, b in itertools.combinations(keys, 2):
        s = summarize(matchup(a, b, args.n, args.seed))
        table[a][b] = s["winrate"]
        table[b][a] = 1 - s["winrate"] - s["draw"] / s["games"]
        print(f"{NAMES_JP[a]} vs {NAMES_JP[b]}: {s['winrate']:.0%}", flush=True)
    avg = {a: sum(table[a].values()) / max(1, len(table[a])) for a in keys}
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    json.dump({"games_per_pair": args.n, "table": table, "avg": avg,
               "names": {k: NAMES_JP[k] for k in keys}, "seconds": time.time() - t0},
              open(args.out, "w"), ensure_ascii=False, indent=1)
    print("\n平均勝率")
    for a in sorted(keys, key=lambda k: -avg[k]):
        print(f"  {NAMES_JP[a]:30s} {avg[a]:.1%}")


if __name__ == "__main__":
    main()
