# -*- coding: utf-8 -*-
"""公式カードリスト（data/official_cards.json）と環境デッキレシピを埋め込んで inventory.html（2人用の在庫帳）を生成する。

使い方: python3 tools/build_inventory.py
（カードリストの更新は先に python3 tools/fetch_official_cards.py）
"""
import json
import os
import re
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OFFICIAL = os.path.join(ROOT, "data/official_cards.json")

official = json.load(open(OFFICIAL, encoding="utf-8"))
decks_by_pair = json.load(open(os.path.join(ROOT, "data/vine_decklists.json"), encoding="utf-8"))

INK_EN = {"アンバー": "Amber", "アメジスト": "Amethyst", "エメラルド": "Emerald",
          "ルビー": "Ruby", "サファイア": "Sapphire", "スティール": "Steel"}


def norm(s):
    s = s.lower().replace("’", "'")
    return re.sub(r"[\s・–—\-‐~〜《》『』「」、。,.!！?？'\"()（）]", "", s)


# 再録・エンチャンテッド版は同じカードとして1つにまとめる（最初に出た版の情報を使う）
cards, seen = [], {}
for c in sorted(official, key=lambda c: (c.get("release_date") or 0, c.get("sets_order") or 0, c.get("collector_number") or 0)):
    name = c["card_name"].strip()
    if c.get("version"):
        name += " — " + c["version"].strip()
    k = norm(name)
    if k in seen:
        continue
    seen[k] = len(cards)
    ink2 = INK_EN.get(c.get("ink_color2") or "")
    row = [name, INK_EN.get(c.get("ink_color") or ""), c.get("ink_cost")]
    if ink2:
        row.append(ink2)
    cards.append(row)


def to_official(name):
    """data/vine_decklists.json のカード名（「日本語 — English」形式もある）を公式の表記にそろえる。"""
    parts = name.split(" — ")
    if len(parts) > 1 and re.fullmatch(r"[\x00-\x7F’]+", parts[-1]):
        parts = parts[:-1]
    i = seen.get(norm(" — ".join(parts)))
    return cards[i][0] if i is not None else name


recipes, unmatched = [], set()
for pair, ds in decks_by_pair.items():
    for d in ds:
        lst = []
        for n, k, _ in d["cards"]:
            o = to_official(n)
            if o == n and norm(n) not in seen:
                unmatched.add(n)
            lst.append([o, k])
        recipes.append([d["title"], d.get("archetype") or "", pair, lst])

fetched = time.strftime("%Y-%m-%d", time.localtime(os.path.getmtime(OFFICIAL)))
catalog = json.dumps({"cards": cards, "recipes": recipes, "fetched": fetched}, ensure_ascii=False, separators=(",", ":"))
catalog = catalog.replace("</", "<\\/")

tpl = open(os.path.join(ROOT, "tools/inventory_template.html"), encoding="utf-8").read()
out = tpl.replace("/*__CATALOG__*/{}", catalog)
open(os.path.join(ROOT, "inventory.html"), "w", encoding="utf-8").write(out)
print(f"inventory.html: {len(cards)} cards (公式 {len(official)} 件から重複を除外), {len(recipes)} recipes")
if unmatched:
    print("公式リストと名前が一致しなかったレシピのカード:", *sorted(unmatched), sep="\n  ")
