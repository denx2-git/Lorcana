# -*- coding: utf-8 -*-
"""タカラトミー公式カードリストの検索APIから全カードを取得し data/card_catalog_ja.json に保存する。

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

    ink_en = {"アンバー": "Amber", "アメジスト": "Amethyst", "エメラルド": "Emerald",
              "ルビー": "Ruby", "サファイア": "Sapphire", "スティール": "Steel"}
    cards.sort(key=lambda c: (c.get("release_date") or 0, c.get("sets_order") or 0, c.get("collector_number") or 0))
    out, seen = [], set()
    for c in cards:
        # 再録・エンチャンテッド版は同じカードとして1つにまとめる
        name = c["card_name"].strip() + (" — " + c["version"].strip() if c.get("version") else "")
        if name in seen:
            continue
        seen.add(name)
        out.append({"name": name, "ink": ink_en.get(c.get("ink_color") or ""), "ink2": ink_en.get(c.get("ink_color2") or ""),
                    "cost": c.get("ink_cost"), "set": c.get("sets"), "num": c.get("collector_number"), "source": "takaratomy.co.jp"})
    path = os.path.join(ROOT, "data/card_catalog_ja.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=0)
    print(f"{path}: {len(out)} 種類")


if __name__ == "__main__":
    main()
