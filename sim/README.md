# ロルカナ簡易シミュレーター v2

環境デッキ（日本の上位14型＋自作・第14弾版）同士を、Bot同士で自動対戦させるツール。

## できること
| コマンド | 内容 |
|---|---|
| `python3 run.py --list` | デッキ一覧 |
| `python3 run.py -a blue_lock -b as_song14 -n 200` | 1対1を200試合 |
| `python3 run.py -a blue_lock -b as_song14 --log 1` | 1試合目のログを表示 |
| `python3 league.py -n 100` | 全デッキの総当たり → `results/league.json` |
| `python3 optimize.py blue_lock --minutes 60` | 環境相手に勝率が上がる入れ替えを自動で探す → `results/opt_blue_lock.json` |
| `python3 report.py` | 結果を `results/REPORT.md` にまとめる |

## 仕組み
- `cards.py`：カードデータ（`data/cards.json`、171種類）とキーワードの読み取り
- `engine.py`：ルール処理（インク・プレイ・歌・変身・チャレンジ・クエスト・移動・ロケーション・アイテム）
- `effects.py`：カードごとの効果
- `ai.py`：Bot。行動を1つずつ試して盤面を評価し、一番良くなる行動を選ぶ（移動・起動能力は2手先まで）
- `decks.py`：デッキリストとデッキごとの方針（マリガン・インク・温存するカード）
- `PLAYBOOK.md`：方針の根拠（公式コラム・大会インタビューのまとめ）

## 注意
- Botは人より単純なので、勝率は目安。**デッキ同士・入れ替え前後の比較**に使う。
- 自動改良はBotの使い方に合わせた改良になる（例：Botが上手く使えないロック役が抜けやすい）。採用前に人の目で確認する。
