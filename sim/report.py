"""results/ の結果から日本語のレポート（results/REPORT.md）を作る。"""
import glob
import json
import os
import time

HERE = os.path.dirname(os.path.abspath(__file__))
R = os.path.join(HERE, "results")


def main():
    lines = [f"# シミュレーター結果レポート", "", f"更新: {time.strftime('%Y-%m-%d %H:%M')}", ""]
    lines += ["> Botは「1手先を読んで盤面評価が一番良くなる行動を選ぶ」単純な思考です。",
              "> 勝率は人同士の対戦より極端になりやすいので、**デッキ同士の比較・入れ替えの良し悪しの目安**として見てください。", ""]
    lg = os.path.join(R, "league.json")
    if os.path.exists(lg):
        d = json.load(open(lg, encoding="utf-8"))
        names, avg, table = d["names"], d["avg"], d["table"]
        lines += [f"## 総当たりの平均勝率（各組み合わせ {d['games_per_pair']} 試合）", "", "| 順位 | デッキ | 平均勝率 |", "|---|---|---|"]
        order = sorted(avg, key=lambda k: -avg[k])
        for i, k in enumerate(order, 1):
            lines.append(f"| {i} | {names[k]} | {avg[k]:.1%} |")
        lines += ["", "## 相性表（行のデッキから見た勝率）", ""]
        short = {k: names[k].split("（")[0][:10] for k in order}
        lines.append("| | " + " | ".join(short[k] for k in order) + " |")
        lines.append("|---" * (len(order) + 1) + "|")
        for a in order:
            row = [short[a]] + ["—" if a == b else f"{table[a].get(b, 0):.0%}" for b in order]
            lines.append("| " + " | ".join(row) + " |")
        lines.append("")
    for f in sorted(glob.glob(os.path.join(R, "opt_*.json"))):
        o = json.load(open(f, encoding="utf-8"))
        lines += [f"## 自動改良：{o['name']}", ""]
        if "verify_before" in o:
            lines.append(f"- 環境勝率（確認用の別の乱数）: **{o['verify_before']:.1%} → {o['verify_after']:.1%}**")
        lines.append(f"- 試した入れ替え: {o['tries']}通り / 採用: {len(o['swaps'])}回")
        lines += ["", "| 抜いた | 入れた | 勝率 |", "|---|---|---|"]
        from cards import db
        cdb = db()
        for s in o["swaps"]:
            lines.append(f"| {cdb[s['out']].jp} | {cdb[s['in']].jp} | {s['before']:.1%}→{s['after']:.1%} |")
        lines += ["", "改良後のリスト（Duels.ink形式）:", "", "```", o["list"], "```", ""]
    open(os.path.join(R, "REPORT.md"), "w", encoding="utf-8").write("\n".join(lines))
    print("\n".join(lines[:40]))


if __name__ == "__main__":
    import sys
    sys.path.insert(0, HERE)
    main()
