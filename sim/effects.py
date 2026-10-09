"""カードごとの効果。

engine.py から各タイミングで呼ばれる。対象を選ぶ効果は TARGETS で候補の出し方を定義し、
Bot（ai.py）が候補ごとに先読みして選ぶ。
簡略化した効果には「簡略化」とコメントを付けている。
"""

# ---------------------------------------------------------------- 補助


def chars_named(p, base):
    return [x for x in p.chars() if x.card.base == base or (x.card.base == "Mickey Mouse & Minnie Mouse" and base in ("Mickey Mouse", "Minnie Mouse"))]


def has_class(p, cls, exclude=None):
    return any(cls in x.card.classes for x in p.chars() if x is not exclude)


def song_in_discard(p):
    return any(c.is_song for c in p.discard)


def threat(g, x):
    from ai import threat as th
    return th(g, x)


def best_opp(g, p, pred=lambda x: True, ward_ok=False):
    o = g.opp(p)
    cs = [x for x in o.chars() if pred(x) and (ward_ok or not x.card.ward)]
    return max(cs, key=lambda x: threat(g, x)) if cs else None


def choose_discard(g, p, n=1):
    for _ in range(n):
        if not p.hand:
            return
        c = p.policy.discard_choice(g, p)
        g.discard_from_hand(g_player(g, p), c)


def g_player(g, p):
    return p


def opp_discard_choice(g, p, o, pred):
    """p が o の手札を見て、pred に合うカードを1枚選んで捨てさせる。"""
    cands = [c for c in o.hand if pred(c)]
    if not cands:
        return
    c = max(cands, key=lambda c: c.cost + (2 if c.kind != "char" else 0))
    g.discard_from_hand(o, c)


def look_take(g, p, n, pred, take=1):
    top = p.deck[:n]
    del p.deck[:n]
    picks = []
    for _ in range(take):
        cands = [c for c in top if pred(c) and c not in picks]
        if not cands:
            break
        picks.append(max(cands, key=lambda c: p.policy.card_value(g, p, c)))
    for c in picks:
        top.remove(c)
        p.hand.append(c)
    p.deck += top
    return picks


def to_inkwell_from_hand(g, p, exerted=True):
    if not p.hand:
        return
    c = p.policy.ink_choice(g, p, any_card=True)
    if c is None:
        return
    p.hand.remove(c)
    g.put_card_in_inkwell(p, c, exerted=exerted)


# ---------------------------------------------------------------- 静的な数値


def strength(g, x):
    c = x.card
    s = c.str + x.tmp_str
    p = g.players[x.owner]
    n = c.name
    if n == "Diablo - Stone Servant" and has_class(p, "Villain", x):
        s += 2
    elif n == "Namaari - Single-Minded Rival":
        s += len(p.discard)
    for kind, _pid in g.global_mods:
        if kind == "kida":
            s -= 3
    s -= x.flags.get("priya", 0)
    if x.loc is not None:
        loc = g.find(x.loc)
        if loc is not None and loc.card.name == "The Beanstalk - Onward and Upward":
            s += 1
    return s


def lore(g, x):
    c = x.card
    v = c.lore + x.tmp_lore
    p = g.players[x.owner]
    o = g.opp(p)
    n = c.name
    if n == "Miguel Rivera - Street Musician" and song_in_discard(p):
        v += 1
    elif n == "Powerline - Megastar":
        v += sum(1 for y in p.chars() if y is not x and singer_value(g, y, raw=True) and (y.card.singer or y.card.name == "Miguel Rivera - Street Musician"))
    elif n == "Lady - Decisive Dog" and strength(g, x) >= 3:
        v += 2
    elif n == "Lilo - Snow Artist" and chars_named(p, "Stitch"):
        v += 1
    elif n == "Piglet - Pooh Pirate Captain" and len(p.chars()) >= 3:
        v += 2
    elif n == "Diablo - Stone Servant" and has_class(p, "Villain", x):
        v += 1
    elif n == "Henry J. Waternoose III - Chief Executive Officer" and p.ink > o.ink:
        v += 2
    elif n == "The Queen - Devious Disguise" and o.lore > p.lore:
        v += 2
    elif n == "Tamatoa - So Shiny!":
        v += len(p.items())
    elif n == "Don Karnage - Debonair Pirate":
        pass
    # ドン・カルナージ（華麗なる海賊）がエグザートしている間、ダメージを受けた相手キャラはロア-1
    for y in o.chars():
        if y.card.name == "Don Karnage - Debonair Pirate" and y.exerted and x.damage > 0:
            v -= 1
    return v


def singer_value(g, x, raw=False):
    c = x.card
    p = g.players[x.owner]
    if c.name == "Miguel Rivera - Street Musician":
        return 3 if song_in_discard(p) else (0 if raw else c.cost)
    return c.singer or (0 if raw else c.cost)


def can_sing(g, x):
    return x.card.name != "Meilin Lee - Lead Vocalist" and not x.card.reckless or x.card.reckless


def flash_in_play(g):
    return any(y.card.name == "Flash - Efficient Clerk" for q in g.players for y in q.chars())


def has_rush(g, x):
    p = g.players[x.owner]
    if flash_in_play(g):
        return False
    if x.card.evasive and any(y.card.name == "Peter Pan - Shadow Finder" and y is not x for y in p.chars()):
        return True
    return False


def gains_evasive(g, x):
    if x.loc is not None:
        loc = g.find(x.loc)
        if loc is not None and loc.card.name == "The Beanstalk - Onward and Upward":
            return True
    return False


def loc_evasive(g, loc):
    return bool(loc.flags.get("evasive"))


def cant_be_challenged(g, x):
    p = g.players[x.owner]
    if "Villain" in x.card.classes:
        for y in p.chars():
            if y.card.name == "Diablo - Stone Servant" and y.exerted:
                return True
    return False


def challenger_bonus(g, att):
    return att.card.challenger + att.flags.get("challenger", 0)


def no_damage_from_challenge(g, att):
    return att.card.name == "Beast - Snowfield Troublemaker" and att.loc is not None


def modify_damage(g, x, n, src, ignore_resist):
    if not ignore_resist:
        n -= x.card.resist + x.flags.get("resist", 0)
    if x.card.name == "Minnie Mouse - Busy Go-Getter" and g.active != x.owner:
        n -= 2
    if x.card.name == "Lilo - Bundled Up" and g.active != x.owner and not x.flags.get("layer_used"):
        x.flags["layer_used"] = g.turn
        return 0
    return n


# ---------------------------------------------------------------- コスト


def cost_for(g, p, card):
    c = card.cost
    n = card.name
    if card.kind == "char":
        if card.underdog and p.t.get("first_turn") and g.first != p.pid and not p.t.get("played_any"):
            c -= 1
        if n == "Pudge - Controls the Weather" and chars_named(p, "Lilo"):
            return 0
        if n == "Tramp - Enterprising Dog" and chars_named(p, "Lady"):
            c -= 1
        if n == "Tramp - Street-Smart Dog":
            c -= len(p.chars())
        willows = sum(1 for x in p.chars() if x.card.name == "Grandmother Willow - Ancient Advisor")
        c -= max(0, willows - p.t.get("willow_used", 0))
        c -= p.t.get("akood", 0)
        if ("Princess" in card.classes or "Queen" in card.classes):
            c -= p.t.get("aurora_disc", 0)
    elif card.kind == "location":
        c -= p.t.get("elsa_loc", 0)
    return max(0, c)


def consume_discounts(g, p, card):
    if card.kind != "char":
        return
    willows = sum(1 for x in p.chars() if x.card.name == "Grandmother Willow - Ancient Advisor")
    if willows > p.t.get("willow_used", 0):
        p.t["willow_used"] = willows
    p.t["akood"] = 0
    if "Princess" in card.classes or "Queen" in card.classes:
        p.t["aurora_disc"] = 0
    p.t["played_any"] = True


def shift_cost(g, p, card):
    return card.shift


def shift_bases(g, p, card):
    """変身先の候補（Perm のリストのリスト）。"""
    if card.duo_shift:
        morph = [x for x in p.chars() if x.card.name == "Morph - Space Goo"]
        mk = [x for x in p.chars() if x.card.base == "Mickey Mouse"]
        mn = [x for x in p.chars() if x.card.base == "Minnie Mouse"]
        out = []
        if mk and mn:
            out.append([mk[0], mn[0]])
        if morph and mn:
            out.append([morph[0], mn[0]])
        if morph and mk:
            out.append([morph[0], mk[0]])
        if len(morph) >= 2:
            out.append(morph[:2])
        return out[:2]
    if not card.shift:
        return []
    out = []
    for x in p.chars():
        if x.card.name == card.name:
            continue
        if x.card.base in card.shift_names or x.card.name == "Morph - Space Goo":
            out.append([x])
    return out


def alt_play_options(g, p, card):
    """通常以外のプレイ方法：[(mode, extra)]"""
    n = card.name
    out = []
    if n == "Belle - Apprentice Inventor":
        for it in p.items():
            out.append(("alt", ("banish_item", it.uid)))
    if n == "Scrooge Mcduck - Resourceful Miser":
        ready = [it for it in p.items() if not it.exerted]
        if len(ready) >= 4:
            out.append(("alt", ("exert_items", tuple(it.uid for it in ready[:4]))))
    return out


def pay_alt(g, p, card, extra):
    if not extra:
        return
    kind = extra[0]
    if kind == "banish_item":
        it = g.find(extra[1])
        if it:
            g.banish(it)
    elif kind == "exert_items":
        for u in extra[1]:
            it = g.find(u)
            if it:
                it.exerted = True


def move_cost(g, p, x, loc):
    return loc.card.move


# ---------------------------------------------------------------- 対象の候補

def _opp_chars(pred=lambda g, x: True, ward_ok=False):
    def f(g, p):
        o = g.opp(p)
        return [x.uid for x in o.chars() if (ward_ok or not x.card.ward) and pred(g, x)]
    return f


def _own_chars(pred=lambda g, x: True):
    def f(g, p):
        return [x.uid for x in p.chars() if pred(g, x)]
    return f


def _opp_items_locs(g, p):
    o = g.opp(p)
    return [x.uid for x in o.perms if x.card.kind in ("item", "location")]


def _opp_chars_locs(g, p):
    o = g.opp(p)
    return [x.uid for x in o.perms if (x.card.kind == "char" and not x.card.ward) or x.card.kind == "location"]


def _all_items(g, p):
    return [x.uid for pl in g.players for x in pl.items()]


TARGETS = {
    # 必須対象（候補がなくてもプレイはできる＝空振り）
    "Scram!": _opp_chars(lambda g, x: x.card.cost <= 2),
    "Let It Go": _opp_chars(),
    "Let the Storm Rage On": _opp_chars(),
    "Hot Potato": lambda g, p: _opp_chars()(g, p) + _all_items(g, p),
    "Ink Explosion": _opp_chars(),
    "Strength of a Raging Fire": _opp_chars(),
    "And Then Along Came Zeus": _opp_chars_locs,
    "Brawl": _opp_chars(lambda g, x: g.char_str(x) <= 2),
    "Teeth and Ambitions": _opp_chars(),
    "Hide Away": _opp_items_locs,
    "Sabotage": _opp_items_locs,
    "You Came Back": _own_chars(lambda g, x: x.exerted),
    "Undermine": _own_chars(),
    # キャラの登場時（任意効果は None も候補に入る）
    "Bellwether - Highly Qualified": _opp_chars(lambda g, x: x.card.cost <= 2),
    "Hades - Infernal Schemer": _opp_chars(),
    "Kit Cloudkicker - Tough Guy": _opp_chars(lambda g, x: g.char_str(x) <= 2),
    "Sisu - Daring Visitor": _opp_chars(lambda g, x: g.char_str(x) <= 1),
    "Elsa - The Fifth Spirit": _opp_chars(lambda g, x: not x.exerted),
    "Milo Thatch - Getting His Hands Dirty": _opp_chars(),
    "Tramp - Enterprising Dog": _own_chars(),
    "Belle - Accomplished Mystic": _opp_chars(),
    "Wildcat - Unconventional Mechanic": _all_items,
    "Clarabelle - Out for a Stroll": _all_items,
    "Clarabelle - Clumsy Guest": _all_items,
    "Fred - Big Stomper": lambda g, p: [x.uid for x in g.opp(p).locs()],
    "Berlioz - Tiny Rascal": _opp_chars(),
    "Priya Mangal - Immovable Fan": _opp_chars(),
    "Jousting Match": _opp_chars(),
}
OPTIONAL = {"Bellwether - Highly Qualified", "Hades - Infernal Schemer", "Kit Cloudkicker - Tough Guy",
            "Milo Thatch - Getting His Hands Dirty", "Wildcat - Unconventional Mechanic",
            "Clarabelle - Out for a Stroll", "Clarabelle - Clumsy Guest", "Fred - Big Stomper",
            "Belle - Accomplished Mystic", "Tramp - Enterprising Dog", "Elsa - The Fifth Spirit",
            "Sisu - Daring Visitor", "Berlioz - Tiny Rascal", "Priya Mangal - Immovable Fan"}


def target_options(g, p, card):
    f = TARGETS.get(card.name)
    if f is None:
        return [None]
    opts = f(g, p)
    if card.name in OPTIONAL or not opts:
        opts = list(opts) + [None]
    return opts


# ---------------------------------------------------------------- アクション・歌


def resolve_spell(g, p, card, target, extra):
    o = g.opp(p)
    n = card.name
    t = g.find(target) if target is not None else None
    if t is not None and t.owner != p.pid and t.card.vanish:
        g.banish(t)
        t = None
    if n == "Scram!" or n == "Let It Go":
        if t:
            g.leave_play(t, "inkwell")
    elif n == "Keep the Ancient Ways":
        o.action_locked = True
        o.item_locked = True
    elif n == "Let the Storm Rage On":
        if t:
            g.deal(t, 2)
        g.draw(p)
    elif n == "Hot Potato":
        if t:
            if t.card.kind == "item":
                g.banish(t)
            else:
                g.deal(t, 2)
    elif n == "Ink Explosion":
        if t:
            g.deal(t, 4)
        p.drops += 1
    elif n == "Grab Your Sword":
        for x in list(o.chars()):
            g.deal(x, 2)
    elif n == "Strength of a Raging Fire":
        if t:
            g.deal(t, len(p.chars()))
    elif n == "And Then Along Came Zeus":
        if t:
            g.deal(t, 5)
    elif n == "Akood et Emuti":
        p.t["akood"] = 2
        g.draw(p)
    elif n == "Beyond the Horizon":
        players = extra if extra else [p.pid]
        for pid in players:
            q = g.players[pid]
            for c in list(q.hand):
                q.hand.remove(c)
                g.to_discard_card(q, c)
            on_discard(g, q, 0)
            g.draw(q, 3)
    elif n == "A Whole New World":
        for q in g.players:
            k = len(q.hand)
            for c in list(q.hand):
                q.hand.remove(c)
                g.to_discard_card(q, c)
            on_discard(g, q, k)
            g.draw(q, 7)
    elif n == "A Pirate's Life":
        g.lose_lore(o, 2)
        g.gain_lore(p, 2)
    elif n == "Be Prepared":
        for q in g.players:
            for x in list(q.chars()):
                g.banish(x)
    elif n == "Brawl":
        if t:
            g.banish(t)
    elif n == "Friends on the Other Side":
        g.draw(p, 2)
    elif n == "Grab Your Bow":
        for _ in range(2):
            x = best_opp(g, p, lambda x: g.char_str(x) <= 2)
            if x:
                g.banish(x)
    elif n == "Hide Away":
        if t:
            g.leave_play(t, "inkwell")
    elif n == "Hypnotize":
        if o.hand:
            c = o.policy.discard_choice(g, o)
            g.discard_from_hand(o, c)
        g.draw(p)
    elif n == "I Find 'Em, I Flatten 'Em":
        for q in g.players:
            for x in list(q.items()):
                g.banish(x)
    elif n == "Look at This Family":
        look_take(g, p, 5, lambda c: c.kind == "char", take=2)
    elif n == "Malicious, Mean, and Scary":
        for x in list(o.chars()):
            x.damage += 1
            if x.damage >= x.card.wp:
                g.banish(x)
    elif n == "Sabotage":
        if t:
            same = [x for q in g.players for x in q.perms if x.card.name == t.card.name]
            for x in same:
                g.banish(x)
    elif n == "Sail the Azurite Sea":
        p.t["extra_ink"] = p.t.get("extra_ink", 0) + 1
        g.draw(p)
    elif n == "Strike A Good Match":
        g.draw(p, 2)
        choose_discard(g, p, 1)
    elif n == "Sudden Chill":
        if o.hand:
            g.discard_from_hand(o, o.policy.discard_choice(g, o))
    elif n == "Teeth and Ambitions":
        own = [x for x in p.chars() if x.left() > 2] or p.chars()
        if own and t:
            src = max(own, key=lambda x: x.left())
            g.deal(src, 2)
            g.deal(t, 2)
    elif n == "The Bare Necessities":
        opp_discard_choice(g, p, o, lambda c: c.kind != "char")
    elif n == "The Family Scattered":
        cs = sorted(o.chars(), key=lambda x: threat(g, x))[:3]
        if cs:
            cs.sort(key=lambda x: -threat(g, x))
            dests = ["hand", "deck_bottom", "deck_top"]
            for x, d in zip(cs, dests):
                g.leave_play(x, d)
    elif n == "The Islands I Pulled From the Sea":
        locs = [c for c in p.deck if c.kind == "location"]
        if locs:
            c = locs[0]
            p.deck.remove(c)
            p.hand.append(c)
            g.rng.shuffle(p.deck)
    elif n == "The Return of Hercules":
        for q in (p, o):
            cs = [c for c in q.hand if c.kind == "char"]
            if cs:
                c = max(cs, key=lambda c: c.cost)
                g.play_card(q, c, mode="free", target=auto_target(g, q, c))
    elif n == "Touch the Sky":
        locs = p.locs()
        movers = [x for x in p.chars() if x.loc is None]
        if locs and movers:
            loc = max(locs, key=lambda l: l.card.lore)
            x = max(movers, key=lambda x: x.card.lore)
            prev = x.loc
            x.loc = loc.uid
            on_move(g, p, x, loc, prev)
            g.draw(p, loc_lore(g, loc))
    elif n == "Under the Sea":
        for x in list(o.chars()):
            if g.char_str(x) <= 2:
                g.leave_play(x, "deck_bottom")
    elif n == "Undermine":
        if o.hand:
            g.discard_from_hand(o, o.policy.discard_choice(g, o))
        if t:
            t.tmp_str += 2
    elif n == "Vision of the Future":
        look_take(g, p, 5, lambda c: True)
    elif n == "You Broke My Smolder":
        k = len(p.hand)
        for c in list(p.hand):
            p.hand.remove(c)
            g.to_discard_card(p, c)
        on_discard(g, p, k)
        g.draw(p, 2)
    elif n == "You Came Back":
        if t:
            t.exerted = False
    elif n == "Khan Transport Delivery":
        g.draw(p)
        p.drops += 1
    elif n == "Jousting Match":
        dmg = 2
        if p.drops > 0 and p.ink_used > 0:
            # インク・ドロップで支払ったことにする
            p.drops -= 1
            p.ink_used -= 1
            dmg = 5
        if t:
            g.deal(t, dmg)


def after_spell(g, p, card, singers):
    o = g.opp(p)
    for x in p.chars():
        n = x.card.name
        if n == "Maui - Half-Shark":
            g.gain_lore(p, 1)
        elif n == "Lenny - Toy Binoculars" and not p.t.get("lenny_" + str(x.uid)):
            if x.exerted:
                x.exerted = False
                p.t["lenny_" + str(x.uid)] = True
    if not card.is_song:
        return
    for x in p.chars():
        n = x.card.name
        if n == "The Muses - Proclaimers of Heroes":
            t = best_opp(g, p, lambda y: g.char_str(y) <= 2)
            if t:
                g.leave_play(t, "hand")
        elif n == "Cinderella - Stouthearted":
            x.flags["challenge_ready"] = True
        elif n == "Powerline - Megastar" and not p.t.get("powerline"):
            back = [c for c in p.discard if c.kind == "char" and (c.singer or c.name == "Miguel Rivera - Street Musician")]
            if back:
                c = max(back, key=lambda c: c.cost)
                p.discard.remove(c)
                p.hand.append(c)
                p.t["powerline"] = True
    if singers and any(s.card.name == "Ursula - Deceiver of All" for s in singers) and not p.t.get("doa_replay"):
        if card in p.discard:
            p.t["doa_replay"] = True
            p.discard.remove(card)
            g.log(f"  七つの海の騙し屋: {card.jp} をもう一度")
            resolve_spell(g, p, card, auto_target(g, p, card), None)
            p.deck.append(card)
            p.t["doa_replay"] = False


def auto_target(g, p, card):
    opts = target_options(g, p, card)
    if len(opts) <= 1:
        return opts[0] if opts else None
    from ai import pick_target
    return pick_target(g, p, card, opts)


# ---------------------------------------------------------------- キャラの登場時


def on_play_char(g, p, x, target, extra):
    o = g.opp(p)
    n = x.card.name
    t = g.find(target) if target is not None else None
    if n in ("Pete - Games Referee", "Toulouse - Rough and Tumble"):
        o.action_locked = True
    elif n == "Priscilla - Efficient Clerk":
        x.exerted = True
    elif n == "Bellwether - Highly Qualified":
        if t:
            g.leave_play(t, "inkwell")
    elif n == "Hades - Infernal Schemer":
        if t:
            g.leave_play(t, "inkwell_ready")
    elif n in ("Ariel - Spectacular Singer",):
        look_take(g, p, 4, lambda c: c.is_song)
    elif n == "Meilin Lee - Losing Control":
        look_take(g, p, 4, lambda c: c.is_song or "Red Panda" in c.classes)
    elif n == "Aurora - Delightful Musician":
        cands = [c for c in p.t.get("spells", []) if c.is_song and c.cost <= 3 and c in p.discard]
        if cands:
            c = max(cands, key=lambda c: c.cost)
            p.discard.remove(c)
            p.hand.append(c)
    elif n == "Belle - Accomplished Mystic":
        own = [y for y in p.chars() if y.damage > 0]
        if own and t:
            src = max(own, key=lambda y: y.damage)
            k = min(3, src.damage)
            src.damage -= k
            t.damage += k
            if t.damage >= t.card.wp:
                g.banish(t)
    elif n == "Bobby Zimuruski - Spray Cheese Kid":
        g.draw(p)
        choose_discard(g, p, 1)
    elif n == "Clarabelle - Clumsy Guest":
        if t and p.ink_free() >= 2:
            p.pay(2)
            g.banish(t)
    elif n in ("Wildcat - Unconventional Mechanic",):
        if t:
            g.banish(t)
    elif n == "Clarabelle - Out for a Stroll":
        if t:
            owner = g.players[t.owner]
            g.banish(t)
            if owner.deck:
                owner.deck.pop(0)
                g.put_card_in_inkwell(owner, None)
    elif n == "Doc - Bold Knight":
        if len(p.hand) <= 1:
            k = len(p.hand)
            for c in list(p.hand):
                p.hand.remove(c)
                g.to_discard_card(p, c)
            on_discard(g, p, k)
            g.draw(p, 2)
    elif n == "Elsa - Concerned Sister":
        p.t["elsa_loc"] = 2
    elif n == "Elsa - The Fifth Spirit":
        if t:
            t.exerted = True
    elif n == "Fix-It Felix, Jr. - Delighted Sightseer":
        if p.locs():
            g.draw(p)
    elif n == "Kida - Protector of Atlantis":
        g.global_mods.append(("kida", p.pid))
    elif n == "Kit Cloudkicker - Tough Guy":
        if t:
            g.leave_play(t, "hand")
    elif n == "Lady - Miss Park Avenue":
        cs = sorted([c for c in p.discard if c.kind == "char" and c.cost <= 2], key=lambda c: -p.policy.card_value(g, p, c))[:2]
        for c in cs:
            p.discard.remove(c)
            p.hand.append(c)
    elif n == "Lenny - Toy Binoculars":
        opp_discard_choice(g, p, o, lambda c: c.kind == "action")
    elif n == "Madam Mim - Fox":
        others = [y for y in p.chars() if y is not x]
        if others:
            y = min(others, key=lambda y: threat(g, y))
            g.leave_play(y, "hand")
        else:
            g.banish(x)
    elif n == "Max Goof - Rebellious Teen":
        songs = [c for c in p.discard if c.is_song and c.cost <= 3]
        if songs and p.ink_free() >= 1:
            p.pay(1)
            c = max(songs, key=lambda c: p.policy.card_value(g, p, c))
            p.discard.remove(c)
            p.hand.append(c)
    elif n == "Merlin - Crab":
        pass  # 簡略化：挑戦者+3の付与は省略
    elif n == "Mickey Mouse - Detective":
        if p.deck:
            p.deck.pop(0)
            g.put_card_in_inkwell(p, None)
    elif n == "Mike Wazowski - Heroic Climber":
        mike_reveal(g, p)
    elif n == "Milo Thatch - Getting His Hands Dirty":
        if t and p.hand:
            choose_discard(g, p, 1)
            g.leave_play(t, "hand")
    elif n == "Mor'du - Savage Cursed Prince":
        for y in p.chars():
            if y is not x:
                y.exerted = True
    elif n == "Mother Gothel - Withered and Wicked":
        x.damage = 3
    elif n == "Mufasa - Ruler of Pride Rock":
        p.ink_used = p.ink
        k = min(2, p.ink)
        p.ink -= k
        p.ink_used = p.ink
        for _ in range(k):
            if p.deck:
                p.hand.append(p.deck.pop())  # 簡略化：インクのカードの代わりに山札の下から
    elif n == "Namaari - Single-Minded Rival":
        g.draw(p)
        choose_discard(g, p, 1)
    elif n == "Nani - Stage Manager":
        look_take(g, p, 4, lambda c: c.kind == "char" and c.cost <= 2)
    elif n == "Prince Naveen - Ukulele Player":
        songs = [c for c in p.hand if c.is_song and c.cost <= 6 and not p.action_locked]
        if songs:
            c = max(songs, key=lambda c: c.cost)
            g.play_card(p, c, mode="free", target=auto_target(g, p, c))
    elif n == "Randall Boggs - Scary Smart":
        others = [y for y in p.chars() if y is not x]
        if others:
            y = min(others, key=lambda y: threat(g, y))
            g.leave_play(y, "inkwell")
    elif n == "Rapunzel - Gifted with Healing":
        own = [y for y in p.chars() if y.damage > 0]
        if own:
            y = max(own, key=lambda y: y.damage)
            k = min(3, y.damage)
            y.damage -= k
            g.draw(p, k)
    elif n == "Scrooge Mcduck - Resourceful Miser":
        look_take(g, p, 4, lambda c: c.kind == "item")
    elif n == "Sisu - Daring Visitor":
        if t:
            g.banish(t)
    elif n == "Sisu - Empowered Sibling":
        for y in list(o.chars()):
            if g.char_str(y) <= 2:
                g.banish(y)
    elif n == "Taffyta Muttonfudge - Crowd Favorite":
        if p.locs():
            g.lose_lore(o, 1)
    elif n == "Tamatoa - Happy as a Clam":
        its = [c for c in p.discard if c.kind == "item"][:2]
        for c in its:
            p.discard.remove(c)
            p.hand.append(c)
    elif n == "Tamatoa - So Shiny!":
        its = [c for c in p.discard if c.kind == "item"][:1]
        for c in its:
            p.discard.remove(c)
            p.hand.append(c)
    elif n == "The Leviathan - Guardian of Atlantis":
        if p.t.get("discarded", 0) >= 2:
            budget = 10
            for y in sorted(o.chars(), key=lambda y: -threat(g, y)):
                s = g.char_str(y)
                if not y.card.ward and s <= budget:
                    budget -= s
                    g.banish(y)
    elif n == "The Queen - Devious Disguise":
        if o.lore <= 15:
            g.draw(p)
            g.gain_lore(o, 2)
    elif n == "Tipo - Growing Son":
        to_inkwell_from_hand(g, p)
    elif n == "Tramp - Enterprising Dog":
        if t:
            t.tmp_str += len(p.chars()) - 1
    elif n == "Tramp - Street-Smart Dog":
        k = len(p.chars()) - 1
        g.draw(p, k)
        choose_discard(g, p, k)
    elif n == "Don Karnage - Debonair Pirate":
        for y in list(o.chars()):
            g.deal(y, 1, ignore_resist=True)
    elif n == "Fred - Big Stomper":
        if t:
            g.banish(t)
    elif n == "Shere Khan - Opportunistic Tycoon":
        if o.hand and len(o.hand) >= 3:
            g.discard_from_hand(o, o.policy.discard_choice(g, o))
        else:
            p.drops += 1
    elif n == "Ursula - Deceiver":
        opp_discard_choice(g, p, o, lambda c: c.is_song)
    elif n == "Tod - Clever Fox":
        g.draw(p, 2)
        choose_discard(g, p, 1)
    elif n == "Cinderella - Homespun Dressmaker":
        if p.deck and p.deck[0].cost > p.ink + 2:
            p.deck.append(p.deck.pop(0))
    elif n == "Berlioz - Tiny Rascal":
        if t:
            g.deal(t, 1)
    elif n == "Priya Mangal - Immovable Fan":
        if t:
            t.flags["priya"] = 2
            t.flags["priya_until"] = p.pid
    elif n == "Pocahontas - Guiding the Tribe":
        ones = [c for c in p.hand if c.kind == "char" and c.cost == 1]
        if ones:
            c = max(ones, key=lambda c: p.policy.card_value(g, p, c))
            g.play_card(p, c, mode="free", target=auto_target(g, p, c))


def after_char_played(g, p, x):
    if x.card.cost <= 2 and x in p.perms and not x.exerted:
        stars = sum(1 for y in p.chars() if y.card.name == "Stitch - Rock Star" and y is not x)
        if stars:
            x.exerted = True
            g.draw(p, stars)
    for y in p.chars():
        n = y.card.name
        if n == "Lady - Decisive Dog":
            y.tmp_str += 1
        elif n == "Magic Broom - Illuminary Keeper" and y is not x and y.exerted:
            g.banish(y)
            g.draw(p)


def mike_reveal(g, p):
    for q in g.players:
        if q.deck:
            c = q.deck.pop(0)
            if c.kind == "char":
                q.hand.append(c)
            else:
                q.deck.append(c)


# ---------------------------------------------------------------- アイテム・ロケーション


def on_play_perm(g, p, x, target, extra):
    n = x.card.name
    if n == "Pawpsicle" or n == "Inkrunner":
        g.draw(p)
    elif n == "Bunch of Balloons":
        locs = p.locs()
        if locs:
            locs[0].flags["evasive"] = True
    if x.card.kind == "item":
        for y in p.items():
            if y is not x and y.card.name == "Maurice's Workshop" and p.ink_free() >= 1:
                p.pay(1)
                g.draw(p)


def loc_lore(g, loc):
    p = g.players[loc.owner]
    v = loc.card.lore
    if loc.card.name == "Paradise Falls - Exotic Destination" and any(c.loc == loc.uid for c in p.chars()):
        v += 3
    return v


def on_move(g, p, x, loc, prev):
    n = x.card.name
    if n == "Taffyta Muttonfudge - Sour Speedster" and not p.t.get("taffyta_" + str(x.uid)):
        p.t["taffyta_" + str(x.uid)] = True
        g.gain_lore(p, 2)
    if loc.card.name == "Sugar Rush Speedway - Finish Line" and prev is not None:
        g.banish(loc)
        g.gain_lore(p, 3)
        g.draw(p, 3)


# ---------------------------------------------------------------- 起動型能力
# activations(g, p) -> [(label, uid, idx, target)]  /  activate(g, p, uid, idx, target)


def activations(g, p):
    out = []
    o = g.opp(p)
    free = p.ink_free()
    for x in p.perms:
        n = x.card.name
        if n == "Basil's Magnifying Glass" and not x.exerted and free >= 2:
            out.append((x.uid, 0, None))
        elif n == "Fishbone Quill" and not x.exerted and p.hand:
            out.append((x.uid, 0, None))
        elif n == "Junior Woodchuck Guidebook" and not x.exerted and free >= 1:
            out.append((x.uid, 0, None))
        elif n == "Lucky Dime" and not x.exerted and free >= 2 and p.chars():
            best = max(p.chars(), key=lambda c: g.char_lore(c))
            out.append((x.uid, 0, best.uid))
        elif n == "Pawpsicle":
            dmg = [c for c in p.chars() if c.damage > 0]
            if dmg:
                out.append((x.uid, 0, max(dmg, key=lambda c: c.damage).uid))
        elif n == "Vitalisphere" and free >= 1:
            for c in p.chars():
                if not c.exerted:
                    out.append((x.uid, 0, c.uid))
        elif n == "Croquet Mallet":
            for c in p.chars():
                if c.dry and not c.exerted:
                    out.append((x.uid, 0, c.uid))
        elif n == "Dumbo - Ninth Wonder of the Universe" or (
                x.card.kind == "char" and x.card.evasive and any(y.card.name == "Dumbo - Ninth Wonder of the Universe" for y in p.chars())):
            if x.card.kind == "char" and not x.exerted and not x.dry and free >= 1:
                out.append((x.uid, 1, None))
        if n == "Elsa - Fierce Protector" and free >= 1 and p.hand:
            for c in o.chars():
                if not c.exerted and not c.card.ward:
                    out.append((x.uid, 0, c.uid))
        elif n == "Chief Bogo - Police Commissioner" and free >= 6:
            for c in o.chars():
                if not c.card.ward and c.flags.get("cant_challenge_until") is None:
                    out.append((x.uid, 0, c.uid))
        elif n == "Carl's House - Flying High" and not p.t.get("carlhouse_" + str(x.uid)):
            here = [c for c in p.chars() if c.loc == x.uid]
            others = [l for l in p.locs() if l is not x]
            if here and others:
                out.append((x.uid, 0, None))
        elif n == "Sugar Rush Speedway - Starting Line" and not p.t.get("srstart"):
            here = [c for c in p.chars() if c.loc == x.uid and not c.exerted and c.left() > 1]
            others = [l for l in p.locs() if l is not x]
            if here and others:
                out.append((x.uid, 0, None))
    return out


def activate(g, p, uid, idx, target):
    x = g.find(uid)
    if x is None:
        return
    n = x.card.name
    t = g.find(target) if target is not None else None
    o = g.opp(p)
    g.log(f"  起動: {x.card.jp}")
    if n == "Basil's Magnifying Glass":
        x.exerted = True
        p.pay(2)
        look_take(g, p, 3, lambda c: c.kind == "item")
    elif n == "Fishbone Quill":
        x.exerted = True
        to_inkwell_from_hand(g, p, exerted=False)
    elif n == "Junior Woodchuck Guidebook":
        p.pay(1)
        g.banish(x)
        g.draw(p, 2)
    elif n == "Lucky Dime":
        x.exerted = True
        p.pay(2)
        if t:
            g.gain_lore(p, g.char_lore(t))
    elif n == "Pawpsicle":
        g.banish(x)
        if t:
            t.damage = max(0, t.damage - 2)
    elif n == "Vitalisphere":
        p.pay(1)
        g.banish(x)
        if t:
            t.flags["rush"] = True
            t.tmp_str += 2
    elif n == "Croquet Mallet":
        g.banish(x)
        if t:
            t.flags["rush"] = True
    elif idx == 1:  # ダンボの能力
        x.exerted = True
        p.pay(1)
        g.draw(p)
        g.gain_lore(p, 1)
    elif n == "Elsa - Fierce Protector":
        p.pay(1)
        choose_discard(g, p, 1)
        if t:
            t.exerted = True
    elif n == "Chief Bogo - Police Commissioner":
        p.pay(6)
        if t:
            t.flags["cant_challenge_until"] = p.pid
    elif n == "Carl's House - Flying High":
        p.t["carlhouse_" + str(x.uid)] = True
        here = [c for c in p.chars() if c.loc == x.uid]
        others = [l for l in p.locs() if l is not x]
        c = max(here, key=lambda c: c.card.lore)
        dest = max(others, key=lambda l: (l.card.name == "Sugar Rush Speedway - Finish Line", l.card.lore))
        c.loc = dest.uid
        g.gain_lore(p, 1)
        on_move(g, p, c, dest, x.uid)
    elif n == "Sugar Rush Speedway - Starting Line":
        p.t["srstart"] = True
        here = [c for c in p.chars() if c.loc == x.uid and not c.exerted and c.left() > 1]
        others = [l for l in p.locs() if l is not x]
        c = max(here, key=lambda c: c.card.lore)
        dest = max(others, key=lambda l: (l.card.name == "Sugar Rush Speedway - Finish Line", l.card.lore))
        c.exerted = True
        c.damage += 1
        c.loc = dest.uid
        on_move(g, p, c, dest, x.uid)


# ---------------------------------------------------------------- その他の誘発


def on_draw(g, p):
    if g.sim and False:
        return
    o = g.opp(p)
    if g.active != p.pid:
        return
    for x in o.chars():
        if x.card.name == "Diablo - Devoted Herald" and x.exerted and o.deck:
            o.hand.append(o.deck.pop(0))


def on_discard(g, p, n):
    o = g.opp(p)
    if n <= 0:
        return
    for x in o.chars():
        if x.card.name == "Prince John - Greediest of All":
            g.draw(o, n)


def on_ink(g, p):
    for x in p.perms:
        n = x.card.name
        if n == "Minnie Mouse - Pirate Lookout" and not p.t.get("minnie_pl") and g.active == p.pid:
            locs = [c for c in p.discard if c.kind == "location"]
            if locs:
                p.discard.remove(locs[0])
                p.hand.append(locs[0])
                p.t["minnie_pl"] = True
        elif n == "Sapphire Coil" and g.active == p.pid:
            t = best_opp(g, p, lambda y: not y.exerted)
            if t:
                t.tmp_str -= 2


def on_leave(g, x, dest):
    pass


def replace_banish(g, x):
    if x.card.name == "Mickey Mouse & Minnie Mouse - Adventuring Duo":
        g.leave_play(x, "inkwell")
        return True
    return False


def on_banished(g, x, by_challenge):
    p = g.players[x.owner]
    n = x.card.name
    if n == "Diablo - Obedient Raven":
        g.draw(p)
    elif n == "Rex - Protective Dinosaur" and g.active != x.owner:
        g.gain_lore(p, 1)


def on_challenge(g, p, att, tgt):
    if att.card.name == "Maui - Half-Shark":
        acts = [c for c in p.discard if c.kind == "action"]
        if acts:
            c = max(acts, key=lambda c: c.cost)
            p.discard.remove(c)
            p.hand.append(c)


def on_challenged(g, o, tgt, att):
    if tgt.card.name == "Dr. Bushroot - Evil Botanist":
        p = g.players[att.owner]
        if p.hand:
            g.discard_from_hand(p, p.policy.discard_choice(g, p))


def on_banish_in_challenge(g, p, att, tgt):
    if att.card.name == "Calhoun - Marine Sergeant" and g.active == p.pid and att in p.perms:
        g.gain_lore(p, 2)
    if att.card.name == "Scar - Vicious Cheater" and g.active == p.pid and att in p.perms:
        att.exerted = False
        att.flags["no_quest"] = g.turn


def on_quest(g, p, x):
    o = g.opp(p)
    n = x.card.name
    if n == "Priscilla - Efficient Clerk" and len(p.deck) >= 2:
        top = p.deck[:2]
        del p.deck[:2]
        keep = max(top, key=lambda c: p.policy.card_value(g, p, c))
        top.remove(keep)
        p.hand.append(keep)
        g.put_card_in_inkwell(p, top[0])
    elif n == "Gaetan Moliere - Clever Burrower":
        g.draw(p, 2)
        choose_discard(g, p, 2)
    elif n == "Mike Wazowski - Heroic Climber":
        mike_reveal(g, p)
    elif n == "Daisy Duck - Donald's Date":
        if o.deck:
            c = o.deck.pop(0)
            if c.kind == "char":
                o.hand.append(c)
            else:
                o.deck.append(c)
    elif n == "Minnie Mouse - Practical Traveler":
        if p.t.get("chars_played", 0) > (1 if x.played_turn == g.turn else 0):
            g.gain_lore(p, 1)
    elif n == "Aurora - Holding Court":
        p.t["aurora_disc"] = p.t.get("aurora_disc", 0) + 1
    elif n == "Mufasa - Ruler of Pride Rock":
        p.ink_used = 0
    elif n == "Tamatoa - Happy as a Clam":
        its = [c for c in p.hand if c.kind == "item"]
        if its and not p.item_locked:
            c = max(its, key=lambda c: c.cost)
            g.play_card(p, c, mode="free")
    elif n == "Tamatoa - So Shiny!":
        its = [c for c in p.discard if c.kind == "item"][:1]
        for c in its:
            p.discard.remove(c)
            p.hand.append(c)


def start_of_turn_pre(g, p):
    for loc in p.locs():
        g.gain_lore(p, loc_lore(g, loc))
        if loc.card.name == "The Queen's Castle - Mirror Chamber":
            here = sum(1 for c in p.chars() if c.loc == loc.uid)
            p.t["castle_draw"] = p.t.get("castle_draw", 0) + here
    mordu = any(x.card.name == "Mor'du - Savage Cursed Prince" for x in p.chars())
    for x in p.chars():
        if mordu and x.card.name != "Mor'du - Savage Cursed Prince":
            x.flags["cant_ready"] = True
        else:
            x.flags.pop("cant_ready", None)


def start_of_turn_post(g, p):
    if p.t.get("castle_draw"):
        g.draw(p, p.t["castle_draw"])
    for x in list(p.chars()):
        n = x.card.name
        if n == "Beast - Tragic Hero":
            if x.damage == 0:
                g.draw(p)
            else:
                x.tmp_str += 4
        elif n == "Namaari - Single-Minded Rival":
            g.draw(p)
            choose_discard(g, p, 1)
    # リロ（抜け出し名人）：ターン開始時、捨て札にあればコストを払ってプレイできる（エグザートで登場）。複数枚あればそれぞれ。
    for c in list(p.discard):
        if c.name == "Lilo - Escape Artist":
            cost = cost_for(g, p, c)
            if p.ink_free() < cost:
                continue
            p.pay(cost)
            consume_discounts(g, p, c)
            p.discard.remove(c)
            x = g.new_perm(c, p.pid)
            x.exerted = True
            p.perms.append(x)
            g.log(f"  リロ（抜け出し名人）が捨て札から戻る（{cost}インク）")


def end_of_turn(g, p):
    o = g.opp(p)
    sang = any(c.is_song for c in p.t.get("spells", []))
    for x in list(p.chars()):
        n = x.card.name
        if n == "Elinor - Renowned Diplomat":
            if sum(1 for y in p.chars() if y.exerted) >= 3:
                t = best_opp(g, p)
                if t:
                    g.deal(t, 1)
                g.gain_lore(p, 1)
                g.draw(p)
        elif n == "Aurora - Delightful Musician" and sang:
            g.gain_lore(p, 1)
        elif n == "Mr. Smee - Bumbling Mate":
            if x.exerted and not has_class(p, "Captain"):
                g.deal(x, 1)
        elif n == "Randall Boggs - Scary Smart":
            if p.ink_used >= p.ink:
                g.gain_lore(p, 1)
        elif n == "Clarabelle - Light on Her Hooves":
            diff = len(o.hand) - len(p.hand)
            if diff > 0:
                g.draw(p, diff)
        elif n == "Cinderella - Unintentional Icon":
            if len(p.deck) >= 2:
                top = p.deck[:2]
                del p.deck[:2]
                keep = max(top, key=lambda c: p.policy.card_value(g, p, c))
                top.remove(keep)
                p.deck.insert(0, keep)
                g.put_card_in_inkwell(p, top[0])
        elif n == "Mickey Mouse - Best in Town":
            if x.exerted:
                for q in g.players:
                    q.drops += 1
        elif n == "Milo Thatch - Getting His Hands Dirty":
            if p.t.get("discarded", 0) >= 2:
                g.draw(p)
        if g.winner is not None:
            return
