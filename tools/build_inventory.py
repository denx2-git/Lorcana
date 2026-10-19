# -*- coding: utf-8 -*-
"""日本語カード名一覧（data/card_catalog_ja.json）と環境デッキレシピを埋め込んで inventory.html（2人用の在庫帳）を生成する。

使い方: python3 tools/build_inventory.py
（カード名一覧の更新は先に python3 tools/fetch_official_cards.py か tools/fetch_cards_fansite.py）
"""
import json
import os
import re
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CATALOG = os.path.join(ROOT, "data/card_catalog_ja.json")

catalog_src = json.load(open(CATALOG, encoding="utf-8"))
decks_by_pair = json.load(open(os.path.join(ROOT, "data/vine_decklists.json"), encoding="utf-8"))


def norm(s):
    s = s.lower().replace("’", "'")
    return re.sub(r"[\s・–—\-‐~〜《》『』「」、。,.!！?？'\"()（）]", "", s)


cards, seen = [], {}
for c in catalog_src:
    k = norm(c["name"])
    if k in seen:
        continue
    seen[k] = len(cards)
    row = [c["name"], c.get("ink"), c.get("cost")]
    if c.get("ink2"):
        row.append(c["ink2"])
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

fetched = time.strftime("%Y-%m-%d", time.localtime(os.path.getmtime(CATALOG)))
source = catalog_src[0].get("source", "") if catalog_src else ""
catalog = json.dumps({"cards": cards, "recipes": recipes, "fetched": fetched, "source": source}, ensure_ascii=False, separators=(",", ":"))
catalog = catalog.replace("</", "<\\/")

tpl = open(os.path.join(ROOT, "tools/inventory_template.html"), encoding="utf-8").read()
out = tpl.replace("/*__CATALOG__*/{}", catalog)
open(os.path.join(ROOT, "inventory.html"), "w", encoding="utf-8").write(out)
print(f"inventory.html: {len(cards)} cards ({source}), {len(recipes)} recipes")
if unmatched:
    print("公式リストと名前が一致しなかったレシピのカード:", *sorted(unmatched), sep="\n  ")
