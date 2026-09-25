# -*- coding: utf-8 -*-
"""data/ と tools/guide_data.py から index.html を生成する。

使い方: python3 tools/build.py
"""
import collections
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import guide_data as G  # noqa: E402

decks_by_pair = json.load(open(os.path.join(ROOT, "data/vine_decklists.json"), encoding="utf-8"))
cardtext = json.load(open(os.path.join(ROOT, "data/cardtext.json"), encoding="utf-8"))
official = json.load(open(os.path.join(ROOT, "data/official_text_ja.json"), encoding="utf-8"))

deck_by_id = {}
for pair, ds in decks_by_pair.items():
    for d in ds:
        d["pair"] = pair
        deck_by_id[d["id"]] = d


def norm(s):
    s = s.lower().replace("’", "'")
    return re.sub(r"[\s・–—\-‐《》『』「」、。,.!！?？'\"()（）]", "", s)


official_norm = {norm(k): v for k, v in official.items()}


def find_official(name):
    cands = [name] + [p.strip() for p in name.split(" — ")]
    for c in cands:
        v = official_norm.get(norm(c))
        if v:
            return v
    return None


TYPE_JA = {"Character": "キャラ", "Action": "アクション", "Song": "歌", "Item": "アイテム", "Location": "ロケーション"}
INK_JA = {"Amber": "アンバー", "Amethyst": "アメジスト", "Emerald": "エメラルド", "Ruby": "ルビー", "Sapphire": "サファイア", "Steel": "スティール"}


def card_info(name):
    ct = cardtext.get(name, {})
    off = find_official(name)
    types = ct.get("type") or []
    kind = "song" if "Song" in types else ("char" if "Character" in types else ("item" if "Item" in types else ("loc" if "Location" in types else "act")))
    stat = ""
    if "Character" in types and ct.get("strength") is not None:
        stat = f"{ct['strength']}/{ct['willpower']}・ロア{ct['lore']}"
    elif "Location" in types:
        stat = f"移動{ct.get('move_cost')}・W{ct.get('willpower')}"
    return {
        "cost": ct.get("cost"),
        "kind": kind,
        "type": "・".join(TYPE_JA.get(t, t) for t in types if t != "Action" or "Song" not in types),
        "ink": INK_JA.get(ct.get("ink") or "", ""),
        "inkable": ct.get("inkwell"),
        "stat": stat,
        "official": off["text"] if off else None,
        "summary": G.EFFECTS.get(name),
        "en": ct.get("en"),
        "url": ct.get("url"),
    }


def deck_stats(ids):
    n = len(ids)
    acc = collections.Counter()
    for i in ids:
        d = deck_by_id[i]
        for name, k, _ in d["cards"]:
            info = cardtext.get(name, {})
            t = info.get("type") or []
            c = info.get("cost") or 0
            acc["cards"] += k
            acc["cost"] += c * k
            if "Character" in t:
                acc["char"] += k
            if "Song" in t:
                acc["song"] += k
            elif "Action" in t:
                acc["act"] += k
            if "Item" in t:
                acc["item"] += k
            if "Location" in t:
                acc["loc"] += k
            if c <= 2:
                acc["low"] += k
    r = lambda x: round(acc[x] / n, 1)
    return {"avg": round(acc["cost"] / max(acc["cards"], 1), 2), "char": r("char"), "song": r("song"), "act": r("act"), "item": r("item"), "loc": r("loc"), "low": r("low")}


def adoption(ids):
    cnt = collections.Counter()
    tot = collections.Counter()
    for i in ids:
        for name, k, _ in deck_by_id[i]["cards"]:
            cnt[name] += 1
            tot[name] += k
    return {name: {"in": cnt[name], "avg": round(tot[name] / cnt[name], 1)} for name in cnt}


PLACE_RE = re.compile(r"【(.+?)】\s*(.+?)選手")


def deck_label(d):
    m = PLACE_RE.search(d["title"])
    if m:
        return {"event": m.group(1), "player": m.group(2)}
    return {"event": "サイト掲載", "player": d["title"]}


cards_used = set()
variants = []
for v in G.VARIANTS:
    ids = [i for i in v["decks"] if i in deck_by_id]
    ad = adoption(ids)
    keys = []
    for k in v["keys"]:
        cards_used.add(k)
        keys.append({"name": k, "adopt": ad.get(k)})
    rep = deck_by_id[v["rep"]]
    replist = []
    for name, k, _ in rep["cards"]:
        cards_used.add(name)
        replist.append({"name": name, "n": k})
    decks = []
    for i in ids:
        d = deck_by_id[i]
        lab = deck_label(d)
        decks.append({"id": i, "url": f"https://disneylorcana.jp/deck/{i}/", **lab, "arch": d.get("archetype", [])})
    variants.append({**{k: v[k] for k in ("id", "pair", "name", "arch", "tag", "summary", "diff", "plan", "watch", "beat")},
                     "stats": deck_stats(ids), "count": len(ids), "keys": keys,
                     "rep": {"id": rep["id"], **deck_label(rep), "url": f"https://disneylorcana.jp/deck/{rep['id']}/", "cards": replist},
                     "decks": decks})

for t in G.THREATS:
    cards_used.add(t[0])

cards = {name: card_info(name) for name in sorted(cards_used)}

pairs = []
for p in G.PAIRS:
    pairs.append({**p, "count": len(decks_by_pair.get(p["key"], []))})

mu = {f"{a}|{b}": {"v": v, "c": c, "why": why, "tip": tip} for (a, b), (v, c, why, tip) in G.MU.items()}

data = {
    "pairs": pairs,
    "variants": variants,
    "cards": cards,
    "casual": G.CASUAL,
    "threats": [{"name": t[0], "who": t[1], "what": t[2], "note": t[3]} for t in G.THREATS],
    "meta": [dict(zip(["pair", "kobe", "jnc", "top8", "scs1", "scs2", "site", "results", "tier"], m)) for m in G.META],
    "kobe": G.KOBE_TOP64,
    "muDecks": G.MU_DECKS,
    "muLabel": G.MU_LABEL,
    "mu": mu,
    "sources": G.SOURCES,
}

tpl = open(os.path.join(ROOT, "tools/template.html"), encoding="utf-8").read()
html = tpl.replace("/*__DATA__*/null", json.dumps(data, ensure_ascii=False, separators=(",", ":")))
open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(html)
missing = [n for n, c in cards.items() if not c["official"] and not c["summary"]]
print(f"index.html: {len(html)//1024}KB, variants {len(variants)}, cards {len(cards)}, key cards without text: {len([k for v in variants for k in v['keys'] if not cards[k['name']]['official'] and not cards[k['name']]['summary']])}")
