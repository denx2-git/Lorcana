"""デッキの自動改良（山登り法）。

環境デッキの組み合わせ（ガントレット）を相手に勝率を測り、
「1枚抜いて、同じ色の別のカードを1枚入れる」を試して、勝率が上がった入れ替えだけを残す。
同じ乱数（シード）で比べるので、少ない試合数でも差が出やすい。

  python3 optimize.py blue_lock --minutes 60
  python3 optimize.py emerald_lock --minutes 30 --games 24
"""
import argparse
import json
import os
import random
import sys
import time
from multiprocessing import Pool

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cards import db  # noqa: E402
from decks import DECKS, NAMES_JP  # noqa: E402
from run import play_one  # noqa: E402

# 環境のデッキ分布：タカラトミー公式「最新デッキ情報局 Vol.35」（トリオクエスト上位16チーム、2026/10/09）の色別使用率を、
# 同じ色のデッキに割り振った目安。黄緑27%・黄鋼23%・赤青15%・緑鋼12.5%・緑青6%・黄赤4%・紫赤4%・紫青2%・青鋼2%。
FIELD = {
    "ae-mike": 0.16, "ae-queen": 0.11,
    "as-std": 0.07, "as_song14": 0.08, "as-naveen": 0.03, "as-lilo-aggro": 0.03, "stitch14": 0.02,
    "rs-basil": 0.09, "rs-inkrunner": 0.06,
    "es-fergus": 0.08, "es-location": 0.025, "emerald_lock": 0.02,
    "esa-mickey": 0.06, "ar-sugar": 0.04, "amr-evasive": 0.04, "ams-hades": 0.02,
    "er-leviathan": 0.02, "blue_lock": 0.01,
}


def parse_counts(text):
    d = {}
    for line in text.strip().splitlines():
        line = line.strip()
        if line:
            n, name = line.split(" ", 1)
            d[name] = d.get(name, 0) + int(n)
    return d


def to_text(counts):
    return "\n".join(f"{n} {c}" for c, n in sorted(counts.items(), key=lambda x: (-x[1], x[0])) if n > 0)


def pool_for(key):
    colors = set(DECKS[key]["pair"].split(","))
    return sorted(n for n, c in db().items() if set(_ink(n)) and set(_ink(n)) <= colors)


def _ink(name):
    import json as _j
    global _INK
    try:
        return _INK[name]
    except NameError:
        _INK = {n: v["ink"] for n, v in _j.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "cards.json"), encoding="utf-8")).items()}
        return _INK[name]


def gauntlet_score(key, text, games_per_opp, seed, pool, field):
    jobs = []
    for opp, w in field.items():
        if opp == key:
            continue
        k = max(2, round(games_per_opp * w / max(field.values())))
        for i in range(k):
            jobs.append((key, opp, i, seed + hash(opp) % 1000, text, None, False))
    res = pool.map(play_one, jobs, chunksize=4)
    by = {}
    for j, r in zip(jobs, res):
        by.setdefault(j[1], []).append(1.0 if r["winner"] == 0 else 0.0)
    total = sum(field[o] for o in by)
    score = sum(field[o] * (sum(v) / len(v)) for o, v in by.items()) / total
    return score, {o: sum(v) / len(v) for o, v in by.items()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("deck")
    ap.add_argument("--minutes", type=float, default=30)
    ap.add_argument("--games", type=int, default=30, help="一番多い相手との試合数（他は環境分布に比例）")
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--procs", type=int, default=4)
    ap.add_argument("--out")
    args = ap.parse_args()
    key = args.deck
    rng = random.Random(args.seed)
    cur = parse_counts(DECKS[key]["list_text"])
    candidates = pool_for(key)
    t_end = time.time() + args.minutes * 60
    history = []
    with Pool(args.procs) as pool:
        base, detail = gauntlet_score(key, to_text(cur), args.games, args.seed, pool, FIELD)
        start = base
        print(f"開始: {NAMES_JP[key]} 環境勝率 {base:.1%}", flush=True)
        tries = 0
        while time.time() < t_end:
            tries += 1
            out_c = rng.choice([c for c, n in cur.items() if n > 0])
            in_c = rng.choice([c for c in candidates if cur.get(c, 0) < 4 and c != out_c])
            new = dict(cur)
            new[out_c] -= 1
            new[in_c] = new.get(in_c, 0) + 1
            # 同じシードで比較（共通乱数）
            s, d = gauntlet_score(key, to_text(new), args.games, args.seed, pool, FIELD)
            if s > base + 0.015:
                # 別のシードでも確認してから採用
                s2, _ = gauntlet_score(key, to_text(new), args.games, args.seed + 1000 + tries, pool, FIELD)
                b2, _ = gauntlet_score(key, to_text(cur), args.games, args.seed + 1000 + tries, pool, FIELD)
                if s2 >= b2 + 0.005:
                    history.append({"out": out_c, "in": in_c, "before": base, "after": s, "check": [b2, s2]})
                    print(f"  採用: -{db()[out_c].jp} +{db()[in_c].jp}  {base:.1%} → {s:.1%}（確認 {b2:.1%}→{s2:.1%}）", flush=True)
                    cur, base, detail = new, s, d
        # 最終確認：別の乱数で、改良前と改良後を大きめの試合数で比べ直す
        orig = parse_counts(DECKS[key]["list_text"])
        vs = args.seed + 99991
        v_before, _ = gauntlet_score(key, to_text(orig), args.games * 4, vs, pool, FIELD)
        v_after, v_detail = gauntlet_score(key, to_text(cur), args.games * 4, vs, pool, FIELD)
        print(f"最終確認（別の乱数・4倍の試合数）: {v_before:.1%} → {v_after:.1%}", flush=True)
    result = {"deck": key, "name": NAMES_JP[key], "start": start, "end": base, "tries": tries,
              "verify_before": v_before, "verify_after": v_after, "verify_detail": v_detail,
              "swaps": history, "list": to_text(cur), "detail": detail}
    out = args.out or os.path.join(os.path.dirname(os.path.abspath(__file__)), "results", f"opt_{key}.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    json.dump(result, open(out, "w"), ensure_ascii=False, indent=1)
    print(f"終了: {start:.1%} → {base:.1%}（{tries}通り試行）")
    print(to_text(cur))


if __name__ == "__main__":
    main()
