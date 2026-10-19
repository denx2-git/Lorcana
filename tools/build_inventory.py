# -*- coding: utf-8 -*-
"""data/ のカード名とデッキレシピを埋め込んで inventory.html（2人用の在庫帳）を生成する。

使い方: python3 tools/build_inventory.py
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

cardtext = json.load(open(os.path.join(ROOT, "data/cardtext.json"), encoding="utf-8"))
decks_by_pair = json.load(open(os.path.join(ROOT, "data/vine_decklists.json"), encoding="utf-8"))

names = sorted(cardtext)
index = {n: i for i, n in enumerate(names)}
cards = [[n, cardtext[n].get("ink"), cardtext[n].get("cost")] for n in names]

recipes = []
for pair, ds in decks_by_pair.items():
    for d in ds:
        recipes.append([d["title"], d.get("archetype") or "", pair, [[index[c[0]], c[1]] for c in d["cards"]]])

catalog = json.dumps({"cards": cards, "recipes": recipes}, ensure_ascii=False, separators=(",", ":"))
catalog = catalog.replace("</", "<\\/")

tpl = open(os.path.join(ROOT, "tools/inventory_template.html"), encoding="utf-8").read()
out = tpl.replace("/*__CATALOG__*/{}", catalog)
open(os.path.join(ROOT, "inventory.html"), "w", encoding="utf-8").write(out)
print(f"inventory.html: {len(cards)} cards, {len(recipes)} recipes")
