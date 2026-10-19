# Lorcana

ディズニー・ロルカナTCGの環境・デッキ・相性のまとめ。

- `index.html` — 第13弾「ヴァインズ・アタック！」環境のデッキ解説（色別・型別の動き、キーカード、対面の注意点、勝率を上げる動き）、相性表、全体除去の早見表（2026-09-25 時点）
- `data/vine_decklists.json` — disneylorcana.jp に掲載された同シーズンのデッキレシピ80件（インク構成別、アーキタイプ付き）
- `data/official_text_ja.json` — 公式カードリストの日本語テキスト（キーカード）
- `data/cardtext.json` — 採用カードの英語名・コスト・能力（Lorcast API）
- `tools/guide_data.py` — 型の分類と解説、相性データ、出典
- `tools/build.py` + `tools/template.html` — `python3 tools/build.py` で `index.html` を生成
- `inventory.html` — 2人で共有するカード在庫帳（2人共通の所持枚数・それぞれのデッキで使用中の枚数・残り）。保存は claude.ai Artifact の共有DBを使う
- `data/card_catalog_ja.json` — 日本語のカード名一覧（全2,494種類、再録の番号つき）。`python3 tools/fetch_cards_fansite.py` で disneylorcana.jp の日本語名と Lorcast のコスト・インクから作る。`tools/fetch_official_cards.py`（タカラトミー公式）も同じ形式で作れるが、続けて取ると一時的に403になる
- `tools/build_inventory.py` + `tools/inventory_template.html` — `python3 tools/build_inventory.py` でカード名一覧と環境レシピを埋め込んで `inventory.html` を生成
