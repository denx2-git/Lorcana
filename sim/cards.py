"""シミュレーターで使うカードの定義（青鋼ロック・黄鋼ソングで使う分のみ）。

効果のあるカードは engine.py 側で名前を見て処理する。
ここでは数値とキーワードだけを持つ。
"""
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Card:
    name: str            # 英語名（Duels.ink表記）
    jp: str              # 日本語名
    cost: int
    kind: str            # 'char' / 'action' / 'song'
    inkable: bool
    str_: int = 0
    wp: int = 0
    lore: int = 0
    singer: int = 0      # 歌声N（0なら無し）
    resist: int = 0
    bodyguard: bool = False
    evasive: bool = False
    alert: bool = False
    ward: bool = False
    sing_together: int = 0
    shift: int = 0       # 変身コスト（0なら無し）
    shift_base: str = ""  # 変身元の名前（キャラ名部分）
    tags: tuple = field(default_factory=tuple)

    @property
    def base(self):
        return self.name.split(" - ")[0]


C = Card
CARDS = {c.name: c for c in [
    # ---- 青鋼ロック ----
    C("Fergus - King of DunBroch", "ファーガス", 2, "char", True, 3, 2, 1, bodyguard=True),
    C("Toulouse - Rough and Tumble", "トゥルーズ", 2, "char", True, 1, 2, 1, tags=("lock",)),
    C("Priscilla - Efficient Clerk", "プリシラ", 3, "char", True, 0, 4, 2),
    C("Pete - Games Referee", "ピート", 3, "char", True, 3, 3, 1, tags=("lock",)),
    C("Go Go Tomago - Working Late", "ゴー・ゴー・トマゴ", 3, "char", True, 2, 6, 1),
    C("Bellwether - Highly Qualified", "ベルウェザー", 4, "char", False, 2, 2, 2),
    C("Wildcat - Unconventional Mechanic", "ワイルドキャット", 3, "char", True, 4, 3, 1),
    C("Doug - Lying in Wait", "羊のダグ", 4, "char", True, 3, 4, 2, ward=True),
    C("Carl Fredricksen - Wilderness Guide", "カール", 6, "char", True, 5, 6, 3),
    C("Clarabelle - Out for a Stroll", "クララベル", 6, "char", True, 5, 7, 2),
    C("Hades - Infernal Schemer", "ハデス", 7, "char", False, 3, 6, 2),
    C("Chief Bogo - Police Commissioner", "ボゴ署長", 7, "char", True, 6, 6, 3),
    C("Minnie Mouse - Urban Visionary", "ミニーマウス", 8, "char", True, 6, 6, 3, ward=True),
    C("Scram!", "消えっちまえ！", 1, "action", True),
    C("Keep the Ancient Ways", "昔ながらのこの営み", 2, "song", True, tags=("lock",)),
    C("Let the Storm Rage On", "風よ吹け", 3, "song", False),
    C("Hot Potato", "あぶなイモの", 3, "action", True),
    C("Ink Explosion", "インク爆発", 4, "action", False),
    C("Let It Go", "LET IT GO", 5, "song", True),
    C("Grab Your Sword", "剣をふるえ！", 5, "song", False),
    # ---- 黄鋼ソング ----
    C("Cinderella - Ballroom Sensation", "シンデレラ（舞踏会）", 1, "char", True, 1, 2, 1, singer=3),
    C("Miguel Rivera - Street Musician", "ミゲル（街角）", 1, "char", True, 1, 2, 1),
    C("Ursula - Vanessa", "アースラ（ヴァネッサ）", 2, "char", True, 1, 4, 1, singer=4),
    C("The Troubadour - Musical Narrator", "トルバドール", 2, "char", True, 1, 3, 1, singer=4, resist=1),
    C("Angel - Siren Singer", "エンジェル", 2, "char", True, 2, 2, 1, singer=3),
    C("Ariel - Spectacular Singer", "アリエル（歌姫）", 3, "char", True, 2, 3, 1, singer=5),
    C("Strength of a Raging Fire", "持つんだ熱い心", 3, "song", True),
    C("Akood et Emuti", "アークーデテムーティ", 3, "song", False),
    C("Meilin Lee - Losing Control", "メイ・リー（暴走）", 3, "char", True, 2, 3, 1),
    C("Aurora - Delightful Musician", "オーロラ", 3, "char", True, 2, 3, 1),
    C("And Then Along Came Zeus", "そこに登場、ゼウス！", 4, "song", False),
    C("Beast - Tragic Hero", "野獣（悲劇）", 5, "char", True, 3, 5, 2),
    C("Powerline - Megastar", "パワーライン", 6, "char", True, 4, 6, 1, singer=9),
    C("Cinderella - Stouthearted", "シンデレラ（剛胆）", 7, "char", True, 5, 5, 3, resist=2,
      shift=5, shift_base="Cinderella"),
    C("Beyond the Horizon", "ビヨンド・ザ・ホライズン", 7, "song", False, sing_together=7),
]}


def parse_list(text):
    deck = []
    for line in text.strip().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        n, name = line.split(" ", 1)
        if name not in CARDS:
            raise KeyError(f"未実装のカード: {name}")
        deck += [CARDS[name]] * int(n)
    return deck


DECKS = {
    "blue_lock": """
4 Fergus - King of DunBroch
4 Toulouse - Rough and Tumble
4 Priscilla - Efficient Clerk
4 Pete - Games Referee
1 Go Go Tomago - Working Late
4 Bellwether - Highly Qualified
3 Wildcat - Unconventional Mechanic
4 Doug - Lying in Wait
3 Carl Fredricksen - Wilderness Guide
2 Clarabelle - Out for a Stroll
3 Hades - Infernal Schemer
2 Chief Bogo - Police Commissioner
2 Minnie Mouse - Urban Visionary
4 Scram!
4 Keep the Ancient Ways
3 Let the Storm Rage On
2 Hot Potato
1 Ink Explosion
4 Let It Go
2 Grab Your Sword
""",
    "amber_steel_song": """
4 Cinderella - Ballroom Sensation
4 Miguel Rivera - Street Musician
4 Ursula - Vanessa
4 The Troubadour - Musical Narrator
2 Angel - Siren Singer
4 Ariel - Spectacular Singer
4 Let the Storm Rage On
4 Strength of a Raging Fire
4 Pete - Games Referee
4 Akood et Emuti
4 Meilin Lee - Losing Control
4 Aurora - Delightful Musician
4 And Then Along Came Zeus
3 Beast - Tragic Hero
2 Powerline - Megastar
2 Cinderella - Stouthearted
3 Beyond the Horizon
""",
}

DECK_NAMES_JP = {"blue_lock": "青鋼ロック", "amber_steel_song": "黄鋼ソング"}
