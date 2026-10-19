# -*- coding: utf-8 -*-
"""日本語のカード名一覧を作り data/card_catalog_ja.json に保存する（公式サイトが使えないとき用）。

- 日本語名: disneylorcana.jp（日本語のファンサイト）の弾ごとのカード一覧。画像ファイル名に弾番号とカード番号が入っている
  （例: 216_DLCS1_TinkerBell_GiantFairy_JA → 第1弾の216番）
- コスト・インク: Lorcast API（英語版のカードデータ）を弾番号とカード番号で突き合わせる

使い方: python3 tools/fetch_cards_fansite.py
"""
import html
import json
import os
import re
import time
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FAN = "https://disneylorcana.jp/cardlist/"
LORCAST = "https://api.lorcast.com/v0/"
FAN_DELAY = 2


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (lorcana inventory)"})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.read().decode("utf-8")
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            print(f"{url}: HTTP {e.code}, retry", flush=True)
            time.sleep(30 * (attempt + 1))
    raise SystemExit(f"{url} を取得できませんでした")


def lorcast_cards():
    """(弾番号, カード番号) -> {cost, ink, ink2}。数字の弾（本編）だけ使う。"""
    out = {}
    for s in json.loads(get(LORCAST + "sets"))["results"]:
        if not s["code"].isdigit():
            continue
        for c in json.loads(get(f"{LORCAST}sets/{s['code']}/cards")):
            inks = c.get("inks") or ([c["ink"]] if c.get("ink") else [])
            num = re.sub(r"\D", "", str(c.get("collector_number") or ""))
            if num:
                out[(int(s["code"]), int(num))] = {"cost": c.get("cost"), "ink": inks[0] if inks else None,
                                                   "ink2": inks[1] if len(inks) > 1 else None, "en": c.get("name")}
        time.sleep(0.2)
    print(f"Lorcast: {len(out)} cards", flush=True)
    return out


ITEM = re.compile(r'<article class="card-item.*?href="(https://disneylorcana\.jp/cardlist/[^"]+/(\d+)/)".*?src="[^"]*/([^"/]+)"[^>]*alt="([^"]*)"', re.S)
FILE = re.compile(r"^(\d+)_DLCS(\d+)_")


def fansite_cards():
    cards = {}
    top = get(FAN)
    sets = sorted(set(re.findall(r"cardlist/set/([a-z0-9-]+)/", top)))
    for slug in sets:
        page, last = 1, None
        while True:
            url = f"{FAN}set/{slug}/" + (f"page/{page}/" if page > 1 else "")
            text = get(url)
            if text is None:
                break
            if last is None:
                nums = [int(n) for n in re.findall(rf"cardlist/set/{slug}/page/(\d+)/", text)]
                last = max(nums) if nums else 1
            items = ITEM.findall(text)
            for url, pid, img, alt in items:
                m = FILE.match(img)
                cards[pid] = {"name": html.unescape(alt).strip(), "url": url,
                              "set": int(m.group(2)) if m else None, "num": int(m.group(1)) if m else None}
            print(f"{slug} {page}/{last}: {len(cards)}", flush=True)
            if page >= last or not items:
                break
            page += 1
            time.sleep(FAN_DELAY)
    return list(cards.values())


def main():
    lc = lorcast_cards()
    fan = fansite_cards()
    out, seen, nomatch = [], set(), 0
    for c in sorted(fan, key=lambda c: (c["set"] or 99, c["num"] or 9999)):
        info = lc.get((c["set"], c["num"])) if c["set"] else None
        if info is None:
            nomatch += 1
            info = {}
        if c["name"] in seen:
            continue
        seen.add(c["name"])
        out.append({"name": c["name"], "ink": info.get("ink"), "ink2": info.get("ink2"), "cost": info.get("cost"),
                    "set": c["set"], "num": c["num"], "source": "disneylorcana.jp"})
    path = os.path.join(ROOT, "data/card_catalog_ja.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=0)
    print(f"{path}: {len(out)} 種類（コスト・インク不明 {sum(1 for x in out if x['cost'] is None)}、番号で突き合わせできなかった掲載 {nomatch}）")


if __name__ == "__main__":
    main()
