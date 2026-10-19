# Lorcana

ディズニー・ロルカナTCGの環境・デッキ・相性のまとめ。

- `index.html` — 第13弾「ヴァインズ・アタック！」環境のデッキ解説（色別・型別の動き、キーカード、対面の注意点、勝率を上げる動き）、相性表、全体除去の早見表（2026-09-25 時点）
- `data/vine_decklists.json` — disneylorcana.jp に掲載された同シーズンのデッキレシピ80件（インク構成別、アーキタイプ付き）
- `data/official_text_ja.json` — 公式カードリストの日本語テキスト（キーカード）
- `data/cardtext.json` — 採用カードの英語名・コスト・能力（Lorcast API）
- `tools/guide_data.py` — 型の分類と解説、相性データ、出典
- `tools/build.py` + `tools/template.html` — `python3 tools/build.py` で `index.html` を生成
- `inventory.html` — 2人で共有するカード在庫帳（所持枚数・デッキで使用中の枚数・残り）。`python3 tools/build_inventory.py` で `tools/inventory_template.html` にカード候補とレシピを埋め込んで生成。保存は claude.ai Artifact の共有DBを使う
