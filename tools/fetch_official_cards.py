# -*- coding: utf-8 -*-
"""タカラトミー公式カードリストの検索APIから全カードを取得し data/official_cards.json に保存する。

使い方: python3 tools/fetch_official_cards.py
（新弾が出たら実行し直して tools/build_inventory.py で在庫帳を作り直す）
"""
import http.cookiejar
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = "https://www.takaratomy.co.jp/products/disneylorcana/api1.0/card-search/"
REFERER = "https://www.takaratomy.co.jp/products/disneylorcana/cardlist/"
PER_PAGE = 50
# 短時間に続けて取得すると IP 単位でしばらく 403 になるので、ゆっくり取る
DELAY = 20
WAIT_ON_403 = 300

opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))


def post(path, data=None, token=None):
    headers = {"Content-Type": "application/x-www-form-urlencoded", "Referer": REFERER, "User-Agent": "Mozilla/5.0"}
    if token:
        headers["X-CSRF-Token"] = token
    body = urllib.parse.urlencode(data or {}).encode()
    req = urllib.request.Request(BASE + path, data=body, headers=headers, method="POST")
    with opener.open(req, timeout=30) as r:
        return json.load(r)


def main():
    token = post("token.json")["csrf"]
    cards, page, total = [], 1, None
    while total is None or len(cards) < total:
        params = {"freeword": "", "ink_type": "すべて", "search_sort": "リリース順", "posts_per_page": PER_PAGE, "page": page}
        for attempt in range(8):
            try:
                res = post("result", params, token)
                break
            except urllib.error.HTTPError as e:
                # 短時間に送りすぎると 403 になるので、待ってトークンを取り直す
                print(f"page {page}: HTTP {e.code}, {WAIT_ON_403}秒待って再試行", flush=True)
                time.sleep(WAIT_ON_403)
                token = post("token.json")["csrf"]
        else:
            raise SystemExit(f"page {page} を取得できませんでした")
        total = res["count"]
        if not res["cards"]:
            break
        cards.extend(res["cards"])
        print(f"page {page}: {len(cards)}/{total}", flush=True)
        page += 1
        time.sleep(DELAY)

    keep = ["id", "card_name", "version", "rubi", "ink_color", "ink_color2", "card_type", "ink_cost", "inkwell",
            "rarity", "sets", "sets_order", "collector_number", "card_group", "release_date"]
    out = [{k: c.get(k) for k in keep} for c in cards]
    path = os.path.join(ROOT, "data/official_cards.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=0)
    print(f"{path}: {len(out)} cards")


if __name__ == "__main__":
    main()
