"""カードデータの読み込みとキーワード解析。"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))


class Card:
    __slots__ = ("name", "jp", "cost", "inkable", "kind", "str", "wp", "lore", "move", "classes", "text",
                 "base", "singer", "shift", "shift_names", "resist", "challenger", "bodyguard", "evasive",
                 "ward", "rush", "reckless", "support", "alert", "underdog", "sing_together", "vanish",
                 "duo_shift", "is_song", "adventurous")

    def __init__(self, name, d):
        self.name = name
        self.jp = d["jp"]
        self.cost = d["cost"]
        self.inkable = d["inkable"]
        types = d["types"]
        self.is_song = "Song" in types
        if "Character" in types:
            self.kind = "char"
        elif "Item" in types:
            self.kind = "item"
        elif "Location" in types:
            self.kind = "location"
        else:
            self.kind = "action"
        self.str = d["str"] or 0
        self.wp = d["wp"] or 0
        self.lore = d["lore"] or 0
        self.move = d["move"] or 0
        self.classes = frozenset(d["classes"])
        self.text = d["text"]
        self.base = name.split(" - ")[0]
        t = self.text

        def num(pat):
            m = re.search(pat, t)
            return int(m.group(1)) if m else 0
        self.singer = num(r"Singer (\d+)")
        self.shift = num(r"(?<!Duo )Shift (\d+)")
        self.duo_shift = "Duo Shift" in t
        self.resist = num(r"(?:^|/ )Resist \+(\d+) \(")
        self.challenger = num(r"(?:^|/ )Challenger \+(\d+) \(")
        self.sing_together = num(r"Sing Together (\d+)")
        def own(kw):
            return bool(re.search(r"(^|/ )" + kw + r"( \+\d+)?( \{I\})?( \(| /|$)", t))
        self.bodyguard = own("Bodyguard")
        self.evasive = own("Evasive")
        self.ward = own("Ward")
        self.rush = own("Rush")
        self.reckless = own("Reckless")
        self.support = own("Support")
        self.alert = own("Alert")
        self.underdog = "UNDERDOG" in t
        self.vanish = own("Vanish")
        self.adventurous = own("Adventurous")
        self.shift_names = (self.base,)
        m = re.search(r"characters named ([^.)]+?)\.\)", t)
        if self.shift and m:
            self.shift_names = tuple(x.strip() for x in re.split(r" or ", m.group(1)))

    def __repr__(self):
        return self.name


_DB = None


def db():
    global _DB
    if _DB is None:
        raw = json.load(open(os.path.join(HERE, "data", "cards.json"), encoding="utf-8"))
        _DB = {n: Card(n, d) for n, d in raw.items()}
        # 手動補正
        fix = _DB.get("Lady - Miss Park Avenue")
        if fix:
            fix.shift_names = ("Lady",)
        for n in ("Diablo - Devoted Herald",):
            if n in _DB:
                _DB[n].evasive = True
    return _DB


def parse_list(text):
    cards = db()
    deck = []
    for line in text.strip().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        n, name = line.split(" ", 1)
        key = next((k for k in cards if k.lower() == name.lower()), None)
        if key is None:
            raise KeyError(f"カードデータにない: {name}")
        deck += [cards[key]] * int(n)
    return deck
