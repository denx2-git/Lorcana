"""使い方:
  python3 run.py                         # 青鋼ロック vs 黄鋼ソング を2000試合
  python3 run.py -n 10000 --seed 1
  python3 run.py --log 1                 # 1試合目のログを表示
"""
import argparse
import json
import statistics
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine import run_game  # noqa: E402
from policies import POLICIES  # noqa: E402
from cards import DECK_NAMES_JP  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-a", default="blue_lock")
    ap.add_argument("-b", default="amber_steel_song")
    ap.add_argument("-n", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--log", type=int, default=0, help="最初のN試合のログを表示")
    ap.add_argument("--json", help="結果をJSONで保存")
    ap.add_argument("--list-a", help="Aのデッキを上書きするリストファイル（Duels.ink形式）")
    ap.add_argument("--list-b", help="Bのデッキを上書きするリストファイル（Duels.ink形式）")
    args = ap.parse_args()

    from cards import DECKS
    if args.list_a:
        DECKS[args.a] = open(args.list_a, encoding="utf-8").read()
    if args.list_b:
        DECKS[args.b] = open(args.list_b, encoding="utf-8").read()
    pa, pb = POLICIES[args.a](), POLICIES[args.b]()
    wins = [0, 0]
    wins_first = [[0, 0], [0, 0]]  # [先攻側pid][勝者pid]
    games_first = [0, 0]
    lengths, lore_loser = [], []
    draws = 0
    lock_turns = 0
    for i in range(args.n):
        first = i % 2
        g = run_game(args.a, args.b, pa, pb, first, args.seed * 1_000_003 + i, log=i < args.log)
        if i < args.log:
            print(f"===== 試合{i + 1}（先攻: {'A' if first == 0 else 'B'}）=====")
            print("\n".join(g.lines))
            print(f"勝者: {g.winner}  ロア {g.players[0].lore}-{g.players[1].lore}\n")
        games_first[first] += 1
        if g.winner is None:
            draws += 1
            continue
        wins[g.winner] += 1
        wins_first[first][g.winner] += 1
        lengths.append(g.turn_no)
        lore_loser.append(g.players[1 - g.winner].lore)
        lock_turns += g.stats["lock_turns"][0]

    na, nb = DECK_NAMES_JP.get(args.a, args.a), DECK_NAMES_JP.get(args.b, args.b)
    n = args.n
    res = {
        "A": na, "B": nb, "games": n,
        "A_winrate": wins[0] / n, "B_winrate": wins[1] / n, "draws": draws,
        "A_winrate_on_play": wins_first[0][0] / max(1, games_first[0]),
        "A_winrate_on_draw": wins_first[1][0] / max(1, games_first[1]),
        "avg_turns": statistics.mean(lengths) if lengths else 0,
        "avg_loser_lore": statistics.mean(lore_loser) if lore_loser else 0,
        "A_lock_turns_per_game": lock_turns / n,
    }
    print(f"{na} vs {nb}  {n}試合")
    print(f"  {na} 勝率 {res['A_winrate']:.1%}（先攻 {res['A_winrate_on_play']:.1%} / 後攻 {res['A_winrate_on_draw']:.1%}）")
    print(f"  {nb} 勝率 {res['B_winrate']:.1%}  引き分け {draws}")
    print(f"  平均ターン数 {res['avg_turns']:.1f}  負けた側の平均ロア {res['avg_loser_lore']:.1f}")
    print(f"  {na} が相手のターンを封じた回数（1試合平均） {res['A_lock_turns_per_game']:.1f}")
    if args.json:
        json.dump(res, open(args.json, "w"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
