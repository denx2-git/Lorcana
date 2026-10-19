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


# Shadawx氏の黄青ハリケーン（X・2026/10）と、魔除けのアリス（頼れる船乗り）入り
_BS_STORM = """
4 Aurora - Holding Court
4 Hamm - Piggy Bank
4 Grandmother Willow - Ancient Advisor
4 Belle - Snowfield Strategist
4 Cinderella - Dream Come True
4 Moana - Curious Explorer
4 Stitch - Carefree Surfer
4 Cinderella - Unintentional Icon
4 Hades - Infernal Schemer
4 Minnie Mouse - Urban Visionary
4 Besties, Assemble!
4 Develop Your Brain
4 Raging Storm
2 Let It Go
"""
DECKS["bs_storm"] = {"name": "黄青ハリケーン（Shadawx氏）", "pair": "amber,sapphire", "source": "Shadawx氏（X）",
                     "list_text": _BS_STORM + "1 The Black Cauldron\n2 Ohana Means Family\n3 The Horseman Strikes!\n"}
DECKS["bs_storm_alice"] = {"name": "黄青ハリケーン＋アリス4（-Ohana2 -騎士1 -大釜1）", "pair": "amber,sapphire", "source": "自作",
                           "list_text": _BS_STORM + "4 Alice - Savvy Sailor\n2 The Horseman Strikes!\n"}

# スクショで共有されたデッキ・黄緑ドッグの比較用（2026/10/14 追加）
DECKS["ae_nokida"] = {"name": "黄緑ドッグ（キーダなし・わいけー選手）", "pair": "amber,emerald", "source": "わいけー選手（セットチャンピオンシップ優勝）", "list_text": """
4 Ursula - Deceiver
4 Elinor - Renowned Diplomat
4 Aurora - Holding Court
2 Go Go Tomago - Darting Dynamo
2 Dale - Ready for His Shot
4 Tramp - Enterprising Dog
3 Tramp - Street-Smart Dog
4 Nani - Stage Manager
2 Pluto - Friendly Pooch
1 The Horned King - Merciless Master
4 Bobby Zimuruski - Spray Cheese Kid
2 Mike Wazowski - Heroic Climber
2 Mushu - Stealthy Dragon
3 Rhino - One-Sixteenth Wolf
1 Rapunzel - Gifted with Healing
4 Lilo - Escape Artist
2 Rex - Protective Dinosaur
2 Lady - Miss Park Avenue
4 Lady - Decisive Dog
4 Grandmother Willow - Ancient Advisor
2 Under the Sea
"""}
DECKS["es_items14"] = {"name": "青緑アイテム（第14弾・ニシオカ選手）", "pair": "emerald,sapphire", "source": "ニシオカ選手（スクショ）", "list_text": """
4 Pawpsicle
4 Prototype Chem Ball
4 Blinding Chem Ball
4 Sail the Azurite Sea
4 Inkrunner
4 Hidden Inkcaster
4 Honey Lemon - Testing the Limits
4 Belle - Apprentice Inventor
4 Baymax - Lab Assistant
4 Ariel - Collector of Oddities
4 Tamatoa - Happy as a Clam
2 Hades - Infernal Schemer
4 Milo Thatch - Getting His Hands Dirty
2 Lucky Dime
4 Stegmutt - Clumsy Dinosaur
4 Under the Sea
"""}
DECKS["est_aggro14"] = {"name": "緑鋼アグロ（第14弾・拓さん）", "pair": "emerald,steel", "source": "拓さん（スクショ）", "list_text": """
4 Cursed Merfolk - Ursula's Handiwork
4 Mulan - Disguised Soldier
4 Gantu - Hamsterviel's Accomplice
4 Rapunzel - Escaping the Tower
4 You Broke My Smolder
4 Doc - Bold Knight
4 Scrooge McDuck - S.H.U.S.H. Agent
4 Look What You've Done
4 Mother Gothel - Evil as Ever
4 Toulouse - Rough and Tumble
4 Flash - Efficient Clerk
2 Jaq - Connoisseur of Climbing
2 Lenny - Toy Binoculars
4 Flynn Rider - High-Climbing Rogue
4 Dr. Bushroot - Evil Botanist
4 Rapunzel & Flynn Rider - Unlikely Pair
"""}
DECKS["re_farewell"] = {"name": "赤緑お別れマキシマス（第14弾・ニシオカ選手）", "pair": "emerald,ruby", "source": "ニシオカ選手（スクショ）", "list_text": """
4 Rivera Family Photo
4 Jebidiah Farnsworth - Cookie
4 Another Tale to Spin
4 Though I Have to Say Goodbye
4 Strike a Good Match
4 Max Goof - Karaoke Star
4 Firefly Swarm
4 The Torn Corner
4 Land of the Dead - Marigold Bridge
4 The Return of Hercules
4 Maui - Half-Shark
4 Maximus - Team Champion
4 The Leviathan - Guardian of Atlantis
4 Heffalumps and Woozles
4 Be Prepared
"""}
DECKS["ae_dog14"] = {"name": "黄緑ドッグ（第14弾入り・自作）", "pair": "amber,emerald", "source": "自作（いつわ選手の優勝リスト＋第14弾）", "list_text": """
4 Under the Sea
4 Ursula - Deceiver
4 Elinor - Renowned Diplomat
4 Aurora - Holding Court
4 Kida - Protector of Atlantis
4 Tramp - Enterprising Dog
4 Tramp - Street-Smart Dog
4 Nani - Stage Manager
4 Meilin Lee - Lead Vocalist
4 Lilo - Escape Artist
4 Lady - Decisive Dog
4 Grandmother Willow - Ancient Advisor
3 Lady - Relaxed and Rested
3 Bobby Zimuruski - Spray Cheese Kid
2 Mike Wazowski - Heroic Climber
2 Lady - Miss Park Avenue
2 Nick Wilde - Toy Drive Officer
"""}

DECKS["stam_drop"] = {"name": "鋼紫インク・ドロップ（第14弾・自作）", "pair": "amethyst,steel", "source": "自作", "list_text": """
4 Madam Mim - Bauble Chaser
2 Marie - Caught in the Act
4 Arthur - Novice Blacksmith
4 Baloo - Delivery Pilot
3 Khan Transport Delivery
1 Keep the Ancient Ways
4 Merlin - Bauble Expert
4 Sir Pellinore - Tougher Than He Looks
4 Pete - Games Referee
2 Archimedes - Messenger Owl
3 Jousting Match
2 Inkcaster Skates
4 Merlin - Profoundly Curious
2 Shere Khan - Khan Industries CEO
2 Ink Explosion
3 Sir Kay - Determined to Win
3 Arthur - Jousting Knight
2 Tia Victoria - Disapproving Ancestor
2 Higitus Figitus
3 Merlin - Ink Drop Tinkerer
2 Madam Mim - Resourceful Trickster
"""}

DECKS["bmx_official"] = {"name": "緑青ベイマックス（公式コラム・第14弾のみ）", "pair": "emerald,sapphire", "source": "https://www.takaratomy.co.jp/products/disneylorcana/news/column/128360/", "list_text": """
4 Leaning Tower of Cheese-a
4 Blinding Chem Ball
4 Prototype Chem Ball
2 Hiro Hamada - Versatile Inventor
2 Another Tale to Spin
3 Chemical Reaction
4 Upgraded Chem Purse
2 Institute of Technology - Honey Lemon's Lab
4 Honey Lemon - Testing the Limits
4 A Dark Age No More
4 Spyglass Hat
4 Baymax - Lab Assistant
2 Fred - Big Stomper
4 Ariel - Collector of Oddities
4 Above the Crowd
3 Honey Lemon - Ingenious Researcher
2 Baymax - Amped Up
4 Shere Khan - Ruthless Entrepreneur
"""}
DECKS["bmx_v1"] = {"name": "緑青ベイマックス（強化案1・モーリスの工房）", "pair": "emerald,sapphire", "source": "自作（公式コラムのリストを既存カードで強化）", "list_text": """
4 Leaning Tower of Cheese-a
4 Blinding Chem Ball
4 Prototype Chem Ball
3 Chemical Reaction
2 Another Tale to Spin
4 Upgraded Chem Purse
2 Institute of Technology - Honey Lemon's Lab
4 Honey Lemon - Testing the Limits
4 A Dark Age No More
4 Spyglass Hat
2 Triton - Discerning King
2 Maurice's Workshop
4 Baymax - Lab Assistant
2 Hiram Flaversham - Toymaker
4 Ariel - Collector of Oddities
4 Above the Crowd
3 Honey Lemon - Ingenious Researcher
1 Baymax - Amped Up
3 Shere Khan - Ruthless Entrepreneur
"""}
DECKS["bmx_v1_belle"] = {"name": "緑青ベイマックス（強化案1・ベル入り）", "pair": "emerald,sapphire", "source": "自作（公式コラムのリストを既存カードで強化）", "list_text": """
4 Leaning Tower of Cheese-a
4 Blinding Chem Ball
4 Prototype Chem Ball
3 Chemical Reaction
2 Another Tale to Spin
4 Upgraded Chem Purse
2 Institute of Technology - Honey Lemon's Lab
4 Honey Lemon - Testing the Limits
4 A Dark Age No More
4 Spyglass Hat
2 Triton - Discerning King
4 Baymax - Lab Assistant
2 Hiram Flaversham - Toymaker
4 Ariel - Collector of Oddities
4 Above the Crowd
3 Honey Lemon - Ingenious Researcher
2 Shere Khan - Ruthless Entrepreneur
2 Belle - Exceptional Writer
2 Belle - Apprentice Inventor
"""}
DECKS["bmx_v2"] = {"name": "緑青ベイマックス（強化案2・公式おすすめ3種）", "pair": "emerald,sapphire", "source": "自作（公式コラムのリストを既存カードで強化）", "list_text": """
4 Leaning Tower of Cheese-a
4 Blinding Chem Ball
4 Prototype Chem Ball
2 Chemical Reaction
2 Another Tale to Spin
3 Upgraded Chem Purse
2 Institute of Technology - Honey Lemon's Lab
4 Honey Lemon - Testing the Limits
3 A Dark Age No More
4 Spyglass Hat
4 Baymax - Lab Assistant
4 Ariel - Collector of Oddities
3 Above the Crowd
3 Honey Lemon - Ingenious Researcher
2 Baymax - Amped Up
2 Shere Khan - Ruthless Entrepreneur
2 Inkrunner
2 Hidden Inkcaster
2 Under the Sea
2 Triton - Discerning King
2 Hiram Flaversham - Toymaker
"""}
DECKS["bmx_v2_belle"] = {"name": "緑青ベイマックス（強化案2・ベル入り）", "pair": "emerald,sapphire", "source": "自作（公式コラムのリストを既存カードで強化）", "list_text": """
4 Leaning Tower of Cheese-a
4 Blinding Chem Ball
4 Prototype Chem Ball
2 Chemical Reaction
2 Another Tale to Spin
3 Upgraded Chem Purse
2 Institute of Technology - Honey Lemon's Lab
4 Honey Lemon - Testing the Limits
3 A Dark Age No More
4 Spyglass Hat
4 Baymax - Lab Assistant
4 Ariel - Collector of Oddities
2 Above the Crowd
3 Honey Lemon - Ingenious Researcher
1 Baymax - Amped Up
2 Shere Khan - Ruthless Entrepreneur
2 Inkrunner
2 Hidden Inkcaster
2 Under the Sea
2 Triton - Discerning King
2 Belle - Exceptional Writer
2 Belle - Apprentice Inventor
"""}

DECKS["stam_drop_v1"] = {"name": "鋼紫インク・ドロップ（アグロ対策版）", "pair": "amethyst,steel", "source": "自作（400試合ずつの確認で57.0%→72.3%）", "list_text": """
4 Arthur - Novice Blacksmith
4 Baloo - Delivery Pilot
4 Madam Mim - Bauble Chaser
4 Merlin - Bauble Expert
4 Merlin - Profoundly Curious
4 Pete - Games Referee
4 Sir Pellinore - Tougher Than He Looks
3 Jousting Match
3 Khan Transport Delivery
3 Merlin - Ink Drop Tinkerer
3 Sir Kay - Determined to Win
2 Archimedes - Messenger Owl
2 Arthur - Jousting Knight
2 Higitus Figitus
2 Ink Explosion
2 Madam Mim - Resourceful Trickster
1 Belle - Accomplished Mystic
3 Calhoun - Marine Sergeant
2 Grab Your Sword
2 Let the Storm Rage On
2 Flash - Efficient Clerk
"""}

DECKS["ae_hl"] = {"name": "黄緑ドッグ＋ハニー・レモン（自作）", "pair": "amber,emerald", "source": "自作（黄緑ドッグ第14弾入りにハニー・レモンとピザの斜塔）", "list_text": """
4 Under the Sea
4 Ursula - Deceiver
4 Elinor - Renowned Diplomat
4 Aurora - Holding Court
4 Kida - Protector of Atlantis
4 Tramp - Enterprising Dog
4 Tramp - Street-Smart Dog
4 Nani - Stage Manager
4 Meilin Lee - Lead Vocalist
4 Lilo - Escape Artist
4 Lady - Decisive Dog
4 Grandmother Willow - Ancient Advisor
2 Lady - Relaxed and Rested
2 Lady - Miss Park Avenue
4 Honey Lemon - Testing the Limits
4 Leaning Tower of Cheese-a
"""}
DECKS["es_hl"] = {"name": "緑鋼ロック＋ハニー・レモン（自作）", "pair": "emerald,steel", "source": "自作（緑鋼ロックにハニー・レモンとピザの斜塔）", "list_text": """
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
1 Cinderella - Stouthearted
1 Flash - Efficient Clerk
1 Fred - Big Stomper
1 Lilo - Bundled Up
1 Malicious, Mean, and Scary
1 Prince John - Greediest of All
1 Shere Khan - Opportunistic Tycoon
4 Honey Lemon - Testing the Limits
4 Leaning Tower of Cheese-a
"""}

DECKS["es_items14_hl"] = {"name": "青緑アイテム（ニシオカ選手のリストを自動改良・ハニー・レモン固定）", "pair": "emerald,sapphire", "source": "自作（自動改良・最終確認 54.3%→56.5%）", "list_text": """
4 Ariel - Collector of Oddities
4 Baymax - Lab Assistant
4 Blinding Chem Ball
4 Hidden Inkcaster
4 Honey Lemon - Testing the Limits
4 Milo Thatch - Getting His Hands Dirty
4 Pawpsicle
4 Prototype Chem Ball
4 Sail the Azurite Sea
4 Stegmutt - Clumsy Dinosaur
4 Tamatoa - Happy as a Clam
4 Under the Sea
3 Belle - Apprentice Inventor
3 Inkrunner
2 Hades - Infernal Schemer
1 Go Go Tomago - Darting Dynamo
1 Hiram Flaversham - Toymaker
1 Mushu - Stealthy Dragon
1 Tamatoa - So Shiny!
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

CONFIG["ae_dog14"] = dict(CONFIG["ae-mike"], keep=CONFIG["ae-mike"]["keep"] | {"Lady - Relaxed and Rested"})
CONFIG["ae_nokida"] = dict(CONFIG["ae-mike"], keep=CONFIG["ae-mike"]["keep"] | {"Rhino - One-Sixteenth Wolf", "Pluto - Friendly Pooch"},
                           ship={"Tramp - Street-Smart Dog", "Lady - Miss Park Avenue", "The Horned King - Merciless Master"})
CONFIG["es_items14"] = {
    "keep": {"Pawpsicle", "Prototype Chem Ball", "Blinding Chem Ball", "Inkrunner", "Hidden Inkcaster",
             "Honey Lemon - Testing the Limits", "Sail the Azurite Sea"},
    "ship": {"Stegmutt - Clumsy Dinosaur", "Lucky Dime", "Hades - Infernal Schemer", "Milo Thatch - Getting His Hands Dirty"},
    "never_ink": {"Honey Lemon - Testing the Limits", "Ariel - Collector of Oddities", "Lucky Dime"},
    "key": {"Ariel - Collector of Oddities": 0.5, "Honey Lemon - Testing the Limits": 0.5, "Under the Sea": 0.6},
    "ink_cap": 8,
}
CONFIG["est_aggro14"] = {
    "keep": {"Cursed Merfolk - Ursula's Handiwork", "Mulan - Disguised Soldier", "Gantu - Hamsterviel's Accomplice",
             "Rapunzel - Escaping the Tower", "Toulouse - Rough and Tumble", "Flash - Efficient Clerk",
             "Mother Gothel - Evil as Ever", "Scrooge McDuck - S.H.U.S.H. Agent"},
    "ship": {"Dr. Bushroot - Evil Botanist"},
    "never_ink": {"Toulouse - Rough and Tumble", "Rapunzel & Flynn Rider - Unlikely Pair"},
    "key": {"Toulouse - Rough and Tumble": 0.4, "Rapunzel & Flynn Rider - Unlikely Pair": 0.5},
    "ink_cap": 6,
}
CONFIG["re_farewell"] = {
    "keep": {"Rivera Family Photo", "Jebidiah Farnsworth - Cookie", "Strike a Good Match", "Max Goof - Karaoke Star",
             "Though I Have to Say Goodbye", "Another Tale to Spin"},
    "ship": {"The Leviathan - Guardian of Atlantis", "Be Prepared", "Maui - Half-Shark", "Maximus - Team Champion"},
    "never_ink": {"Rivera Family Photo", "The Torn Corner", "Land of the Dead - Marigold Bridge", "Maui - Half-Shark",
                  "The Leviathan - Guardian of Atlantis", "Maximus - Team Champion"},
    "key": {"Maui - Half-Shark": 0.6, "Rivera Family Photo": 0.4, "Be Prepared": 0.5, "Firefly Swarm": 0.3},
    "ink_cap": 8,
}
CONFIG["stam_drop"] = {
    "keep": {"Arthur - Novice Blacksmith", "Baloo - Delivery Pilot", "Khan Transport Delivery", "Madam Mim - Bauble Chaser",
             "Merlin - Bauble Expert", "Sir Pellinore - Tougher Than He Looks", "Marie - Caught in the Act"},
    "ship": {"Madam Mim - Resourceful Trickster", "Merlin - Ink Drop Tinkerer", "Higitus Figitus", "Tia Victoria - Disapproving Ancestor"},
    "never_ink": {"Pete - Games Referee", "Madam Mim - Resourceful Trickster", "Merlin - Ink Drop Tinkerer"},
    "key": {"Pete - Games Referee": 0.4, "Merlin - Profoundly Curious": 0.3},
    "ink_cap": 8,
}
CONFIG["stam_drop_v1"] = CONFIG["stam_drop"]
CONFIG["emerald_lock_v1"] = CONFIG["emerald_lock"]
CONFIG["stitch14_rs"] = dict(CONFIG["stitch14"], key={"Lilo & Stitch - Fun-Loving Friends": 0.8, "Stitch - Rock Star": 1.0},
                             never_ink=CONFIG["stitch14"]["never_ink"] | {"Stitch - Rock Star"})

CONFIG["bmx_official"] = {
    "keep": {"Honey Lemon - Testing the Limits", "Prototype Chem Ball", "Blinding Chem Ball", "Leaning Tower of Cheese-a",
             "Baymax - Lab Assistant", "Upgraded Chem Purse", "Inkrunner", "Hidden Inkcaster", "Belle - Apprentice Inventor"},
    "ship": {"Shere Khan - Ruthless Entrepreneur", "Honey Lemon - Ingenious Researcher", "Baymax - Amped Up", "Under the Sea"},
    "never_ink": {"Honey Lemon - Testing the Limits", "Ariel - Collector of Oddities", "Triton - Discerning King",
                  "Honey Lemon - Ingenious Researcher", "Belle - Exceptional Writer"},
    "key": {"Ariel - Collector of Oddities": 0.5, "Honey Lemon - Testing the Limits": 0.5, "Under the Sea": 0.6,
            "Triton - Discerning King": 0.6, "Shere Khan - Ruthless Entrepreneur": 0.3},
    "ink_cap": 8,
    "post_quest_pass": True,
}
for _k in ("bmx_v1", "bmx_v1_belle", "bmx_v2", "bmx_v2_belle"):
    CONFIG[_k] = CONFIG["bmx_official"]

CONFIG["ae_hl"] = dict(CONFIG["ae_dog14"], keep=CONFIG["ae_dog14"]["keep"] | {"Honey Lemon - Testing the Limits", "Leaning Tower of Cheese-a"})
CONFIG["es_hl"] = dict(CONFIG["emerald_lock"], keep=CONFIG["emerald_lock"]["keep"] | {"Honey Lemon - Testing the Limits"})

CONFIG["es_items14_hl"] = CONFIG["es_items14"]

CONFIG["bs_storm"] = {
    "keep": {"Aurora - Holding Court", "Hamm - Piggy Bank", "Grandmother Willow - Ancient Advisor", "Besties, Assemble!",
             "Develop Your Brain", "Belle - Snowfield Strategist", "Cinderella - Dream Come True", "Alice - Savvy Sailor"},
    "ship": {"Raging Storm", "Minnie Mouse - Urban Visionary", "Hades - Infernal Schemer"},
    "never_ink": {"Moana - Curious Explorer", "Stitch - Carefree Surfer"},
    "key": {"Raging Storm": 0.8, "Let It Go": 0.4, "Stitch - Carefree Surfer": 0.3},
    "ink_cap": 11,
    "post_quest_pass": True,
}
CONFIG["bs_storm_alice"] = CONFIG["bs_storm"]

WIPES = {"Be Prepared": 1.0, "Raging Storm": 1.0, "Under the Sea": 0.8, "Grab Your Sword": 0.6, "Sisu - Empowered Sibling": 0.7,
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
