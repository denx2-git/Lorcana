"""デッキリストと、デッキごとのBotの方針。

方針の根拠：PLAYBOOK.md（タカラトミー公式コラム・大会インタビューなどのまとめ）。
- keep: マリガンで必ず残す / ship: 必ず戻す
- never_ink: インクに置かない
- key: 手札に持っておく価値の上乗せ（大きいほど手放さない）
- ink_cap: これ以上インクを伸ばさない
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))

_meta = json.load(open(os.path.join(HERE, "data", "meta_decks.json"), encoding="utf-8"))


def _text(lines):
    return "\n".join(f"{q} {n}" for q, n in lines)


DECKS = {}
for key, d in _meta.items():
    DECKS[key] = {"name": d["name"], "pair": d["pair"], "source": d.get("source"), "list_text": _text(d["list"])}

DECKS["blue_lock"] = {"name": "青鋼ロック", "pair": "sapphire,steel", "source": "自作", "list_text": """
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
"""}

DECKS["emerald_lock"] = {"name": "緑鋼ロック", "pair": "emerald,steel", "source": "自作（自動改良後・500試合ずつで確認 53.7%→61.6%）", "list_text": """
4 Diablo - Devoted Herald
4 Elinor - Renowned Diplomat
4 Keep the Ancient Ways
4 Let the Storm Rage On
4 Pete - Games Referee
4 Sudden Chill
4 Toulouse - Rough and Tumble
4 Ursula - Deceiver
3 Diablo - Stone Servant
3 Don Karnage - Debonair Pirate
3 Strength of a Raging Fire
2 Diablo - Maleficent's Spy
2 Don Karnage - Khan's Courier
2 Fergus - King of DunBroch
2 Lenny - Toy Binoculars
2 Max Goof - Rebellious Teen
2 Sabotage
1 Cinderella - Stouthearted
1 Flash - Efficient Clerk
1 Fred - Big Stomper
1 Lilo - Bundled Up
1 Malicious, Mean, and Scary
1 Prince John - Greediest of All
1 Shere Khan - Opportunistic Tycoon
"""}

DECKS["emerald_lock_v1"] = {"name": "緑鋼ロック（改良前）", "pair": "emerald,steel", "source": "自作", "list_text": """
2 Diablo - Maleficent's Spy
2 Don Karnage - Khan's Courier
4 Ursula - Deceiver
3 Diablo - Stone Servant
2 Fergus - King of DunBroch
4 Toulouse - Rough and Tumble
4 Diablo - Devoted Herald
4 Pete - Games Referee
2 Lenny - Toy Binoculars
2 Max Goof - Rebellious Teen
2 Prince John - Greediest of All
2 Shere Khan - Opportunistic Tycoon
4 Elinor - Renowned Diplomat
1 Fred - Big Stomper
3 Don Karnage - Debonair Pirate
4 Keep the Ancient Ways
4 Sudden Chill
4 Let the Storm Rage On
3 Strength of a Raging Fire
2 Malicious, Mean, and Scary
2 Sabotage
"""}

DECKS["as_song14"] = {"name": "黄鋼ソング（第14弾）", "pair": "amber,steel", "source": "同志Vさんのリスト", "list_text": """
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
"""}

_STITCH_BASE = """
4 Stitch - New Dog
4 Stitch - Protector of Frogs
3 Lilo - Snow Artist
4 Mickey Mouse - Best in Town
4 Pocahontas - Guiding the Tribe
4 Pudge - Controls the Weather
4 Grandmother Willow - Ancient Advisor
3 Lilo - Bundled Up
3 Lilo - Escape Artist
3 Toulouse - Rough and Tumble
2 Flash - Efficient Clerk
4 Pete - Games Referee
4 Lilo & Stitch - Fun-Loving Friends
3 Strength of a Raging Fire
2 Keep the Ancient Ways
2 Mike Wazowski - Heroic Climber
2 Rex - Protective Dinosaur
"""
DECKS["stitch14"] = {"name": "黄鋼スティッチ（第14弾・ロックスターなし）", "pair": "amber,steel", "source": "自作",
                     "list_text": _STITCH_BASE + "2 Nani - Stage Manager\n2 Grab Your Sword\n1 The Bare Necessities\n"}
DECKS["stitch14_rs"] = {"name": "黄鋼スティッチ（第14弾・ロックスターあり）", "pair": "amber,steel", "source": "自作",
                        "list_text": _STITCH_BASE + "4 Stitch - Rock Star\n1 The Bare Necessities\n"}

DECKS["esa_priscilla"] = {"name": "緑青ミキミニ・プリシラ型（第14弾）", "pair": "emerald,sapphire", "source": "チェルシーさんのリスト（X）", "list_text": """
4 Minnie Mouse - Practical Traveler
4 Minnie Mouse - Curious Adventurer
4 The Beanstalk - Onward and Upward
4 Morph - Space Goo
4 Vision of the Future
4 Sail the Azurite Sea
4 Minnie Mouse - Busy Go-Getter
4 Cinderella - Homespun Dressmaker
4 Mickey Mouse - Detective
4 You Came Back
4 Tod - Clever Fox
4 Priscilla - Efficient Clerk
4 Mickey Mouse & Minnie Mouse - Adventuring Duo
4 Cinderella - Unintentional Icon
4 Minnie Mouse - Urban Visionary
"""}

NAMES_JP = {k: v["name"] for k, v in DECKS.items()}

LOCKS = {"Pete - Games Referee", "Toulouse - Rough and Tumble", "Keep the Ancient Ways"}

CONFIG = {
    "default": {"keep": set(), "ship": set(), "never_ink": set(), "key": {}, "ink_cap": 9},
    "ae-mike": {
        "keep": {"Grandmother Willow - Ancient Advisor", "Lady - Decisive Dog", "Kida - Atlantean",
                 "Bobby Zimuruski - Spray Cheese Kid", "Aurora - Holding Court"},
        "ship": {"Tramp - Street-Smart Dog", "Lady - Miss Park Avenue", "Kida - Protector of Atlantis"},
        "never_ink": {"Grandmother Willow - Ancient Advisor", "Elinor - Renowned Diplomat"},
        "key": {"Under the Sea": 0.6, "Lilo - Escape Artist": 0.3, "Elinor - Renowned Diplomat": 0.4},
        "ink_cap": 6,
    },
    "as-std": {
        "keep": {"Ariel - Spectacular Singer", "Meilin Lee - Losing Control", "Pete - Games Referee",
                 "Cinderella - Ballroom Sensation", "Angel - Siren Singer"},
        "ship": {"Beyond the Horizon", "Cinderella - Stouthearted"},
        "never_ink": {"Pete - Games Referee", "Prince Naveen - Ukulele Player"},
        "key": {"And Then Along Came Zeus": 0.5, "Let the Storm Rage On": 0.4},
        "ink_cap": 7,
    },
    "as_song14": {
        "keep": {"Ariel - Spectacular Singer", "Meilin Lee - Losing Control", "Miguel Rivera - Street Musician",
                 "Cinderella - Ballroom Sensation", "Pete - Games Referee", "Let the Storm Rage On"},
        "ship": {"Beyond the Horizon", "Cinderella - Stouthearted", "Powerline - Megastar"},
        "never_ink": {"Pete - Games Referee", "Aurora - Delightful Musician"},
        "key": {"And Then Along Came Zeus": 0.5, "Let the Storm Rage On": 0.4},
        "ink_cap": 7,
    },
    "as-naveen": {
        "keep": {"Ariel - Spectacular Singer", "Pete - Games Referee", "Cinderella - Ballroom Sensation"},
        "ship": {"A Whole New World", "Beast - Tragic Hero"},
        "never_ink": {"Prince Naveen - Ukulele Player", "Pete - Games Referee"},
        "key": {"Prince Naveen - Ukulele Player": 1.0, "A Whole New World": 0.3},
        "ink_cap": 7,
    },
    "as-lilo-aggro": {
        "keep": {"Lilo - Snow Artist", "Pudge - Controls the Weather", "Grandmother Willow - Ancient Advisor",
                 "Stitch - New Dog", "Stitch - Protector of Frogs"},
        "never_ink": {"Pudge - Controls the Weather", "Grandmother Willow - Ancient Advisor"},
        "ink_cap": 6,
    },
    "es-fergus": {
        "keep": {"Diablo - Maleficent's Spy", "Ursula - Deceiver", "Diablo - Stone Servant", "Sudden Chill",
                 "Diablo - Devoted Herald"},
        "never_ink": {"Diablo - Devoted Herald", "Ursula - Deceiver"},
        "key": {"Keep the Ancient Ways": 0.4, "Pete - Games Referee": 0.3},
        "ink_cap": 7,
    },
    "es-location": {
        "keep": {"Diablo - Maleficent's Spy", "Ursula - Deceiver", "Diablo - Stone Servant", "Paradise Falls - Exotic Destination"},
        "never_ink": {"Diablo - Devoted Herald", "Touch the Sky"},
        "ink_cap": 7,
    },
    "rs-basil": {
        "keep": {"Basil's Magnifying Glass", "Pawpsicle", "Jebidiah Farnsworth - Cookie", "Liquidator - Iced Over",
                 "Brawl", "Sail the Azurite Sea"},
        "ship": {"Tamatoa - So Shiny!", "Lucky Dime"},
        "never_ink": {"Be Prepared", "Sisu - Empowered Sibling", "Maurice's Workshop"},
        "key": {"Be Prepared": 1.0, "Brawl": 0.3},
        "ink_cap": 9,
    },
    "rs-inkrunner": {
        "keep": {"Inkrunner", "Pawpsicle", "Jebidiah Farnsworth - Cookie", "Liquidator - Iced Over", "Brawl"},
        "never_ink": {"Be Prepared", "Sisu - Empowered Sibling", "Maurice's Workshop"},
        "key": {"Be Prepared": 1.0},
        "ink_cap": 9,
    },
    "er-leviathan": {
        "keep": {"Sudden Chill", "Diablo - Maleficent's Spy", "Jebidiah Farnsworth - Cookie", "Ursula - Deceiver",
                 "Strike A Good Match"},
        "never_ink": {"The Return of Hercules"},
        "key": {"The Return of Hercules": 0.8, "The Leviathan - Guardian of Atlantis": 0.3},
        "ink_cap": 10,
    },
    "ar-sugar": {
        "keep": {"Sugar Rush Speedway - Finish Line", "Carl's House - Flying High", "Elsa - Concerned Sister",
                 "Minnie Mouse - Pirate Lookout"},
        "never_ink": {"Sugar Rush Speedway - Finish Line", "Minnie Mouse - Pirate Lookout", "Carl's House - Flying High"},
        "key": {"Carl's House - Flying High": 0.8, "Sugar Rush Speedway - Finish Line": 0.5},
        "ink_cap": 7,
    },
    "amr-evasive": {"ink_cap": 7},
    "esa-mickey": {
        "keep": {"Morph - Space Goo", "Mickey Mouse - Detective", "Minnie Mouse - Curious Adventurer",
                 "Minnie Mouse - Practical Traveler", "Mickey Mouse & Minnie Mouse - Adventuring Duo"},
        "never_ink": {"Mickey Mouse & Minnie Mouse - Adventuring Duo", "Morph - Space Goo", "You Came Back"},
        "key": {"Mickey Mouse & Minnie Mouse - Adventuring Duo": 1.5},
        "ink_cap": 8,
    },
    "ams-hades": {
        "keep": {"Tipo - Growing Son", "Sail the Azurite Sea", "Merryweather - Feisty Fairy", "Elsa - The Fifth Spirit"},
        "ink_cap": 10,
    },
    "stitch14": {
        "keep": {"Stitch - New Dog", "Stitch - Protector of Frogs", "Lilo - Snow Artist", "Mickey Mouse - Best in Town",
                 "Pocahontas - Guiding the Tribe", "Grandmother Willow - Ancient Advisor", "Pudge - Controls the Weather",
                 "Lilo & Stitch - Fun-Loving Friends"},
        "never_ink": {"Pudge - Controls the Weather", "Grandmother Willow - Ancient Advisor", "Lilo & Stitch - Fun-Loving Friends"},
        "key": {"Lilo & Stitch - Fun-Loving Friends": 0.8},
        "ink_cap": 6,
    },
    "esa_priscilla": {
        "keep": {"Morph - Space Goo", "Mickey Mouse - Detective", "Minnie Mouse - Curious Adventurer",
                 "Minnie Mouse - Practical Traveler", "Mickey Mouse & Minnie Mouse - Adventuring Duo", "Priscilla - Efficient Clerk"},
        "never_ink": {"Mickey Mouse & Minnie Mouse - Adventuring Duo", "Morph - Space Goo", "You Came Back", "Priscilla - Efficient Clerk"},
        "key": {"Mickey Mouse & Minnie Mouse - Adventuring Duo": 1.5, "You Came Back": 0.5},
        "ink_cap": 9,
    },
    "blue_lock": {
        "keep": {"Toulouse - Rough and Tumble", "Pete - Games Referee", "Keep the Ancient Ways", "Scram!",
                 "Priscilla - Efficient Clerk", "Fergus - King of DunBroch", "Doug - Lying in Wait"},
        "ship": {"Carl Fredricksen - Wilderness Guide", "Clarabelle - Out for a Stroll", "Chief Bogo - Police Commissioner",
                 "Minnie Mouse - Urban Visionary", "Ink Explosion"},
        "never_ink": {"Pete - Games Referee", "Toulouse - Rough and Tumble", "Keep the Ancient Ways",
                      "Priscilla - Efficient Clerk", "Let It Go"},
        "key": {"Keep the Ancient Ways": 0.6, "Pete - Games Referee": 0.4, "Toulouse - Rough and Tumble": 0.3,
                "Let It Go": 0.5},
        "ink_cap": 9,
    },
    "emerald_lock": {
        "keep": {"Toulouse - Rough and Tumble", "Pete - Games Referee", "Ursula - Deceiver", "Diablo - Maleficent's Spy",
                 "Diablo - Stone Servant", "Sudden Chill", "Keep the Ancient Ways"},
        "never_ink": {"Pete - Games Referee", "Toulouse - Rough and Tumble", "Keep the Ancient Ways",
                      "Diablo - Devoted Herald"},
        "key": {"Keep the Ancient Ways": 0.6, "Pete - Games Referee": 0.4},
        "ink_cap": 7,
    },
}

CONFIG["emerald_lock_v1"] = CONFIG["emerald_lock"]
CONFIG["stitch14_rs"] = dict(CONFIG["stitch14"], key={"Lilo & Stitch - Fun-Loving Friends": 0.8, "Stitch - Rock Star": 1.0},
                             never_ink=CONFIG["stitch14"]["never_ink"] | {"Stitch - Rock Star"})

WIPES = {"Be Prepared": 1.0, "Under the Sea": 0.8, "Grab Your Sword": 0.6, "Sisu - Empowered Sibling": 0.7,
         "The Leviathan - Guardian of Atlantis": 0.7, "Malicious, Mean, and Scary": 0.3,
         "Don Karnage - Debonair Pirate": 0.4, "A Whole New World": 0.0}


def wipe_level(list_text):
    lv = 0.0
    for line in list_text.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        n, name = line.split(" ", 1)
        lv += WIPES.get(name, 0) * int(n) / 4
    return min(lv, 1.5)


def make_policy(key, opp_key, list_override=None, opp_list_override=None):
    from ai import Policy
    base = dict(CONFIG["default"])
    base.update(CONFIG.get(key, {}))
    cfg = {k: (set(v) if isinstance(v, set) else (dict(v) if isinstance(v, dict) else v)) for k, v in base.items()}
    opp_text = opp_list_override or DECKS[opp_key]["list_text"]
    cfg["_opp_wipe"] = wipe_level(opp_text)
    from cards import parse_list
    od = parse_list(opp_text)
    cfg["_opp_action_ratio"] = sum(1 for c in od if c.kind == "action") / len(od)
    cfg["_opp_item_ratio"] = sum(1 for c in od if c.kind == "item") / len(od)
    counts = {}
    for c in od:
        counts[c.name] = counts.get(c.name, 0) + 1
    cfg["_opp_counts"] = counts
    return Policy(cfg)
