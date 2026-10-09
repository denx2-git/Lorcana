"""Bot：行動を1つずつ試して盤面を評価し、一番良くなる行動を選ぶ（1手先読みの貪欲法）。

デッキごとの方針（マリガン・インク・温存するカードなど）は decks.py の設定を使う。
"""
from engine import WIN_LORE
import effects

W_LORE = 1.6
W_HAND = 0.85
W_INK_EARLY = 1.4
W_INK_LATE = 0.25
W_DROP = 0.6

ENGINE_BONUS = {
    # 場にいるだけで価値が出続けるキャラ（相手から見れば優先して除去したい）
    "Diablo - Devoted Herald": 2.5, "Elinor - Renowned Diplomat": 2.5, "Tamatoa - Happy as a Clam": 2.0,
    "Tamatoa - So Shiny!": 2.0, "Powerline - Megastar": 2.5, "Aurora - Delightful Musician": 1.5,
    "Beast - Tragic Hero": 1.5, "Priscilla - Efficient Clerk": 1.5, "Maui - Half-Shark": 2.0,
    "Prince John - Greediest of All": 1.5, "Gaetan Moliere - Clever Burrower": 1.0,
    "Ursula - Deceiver of All": 1.5, "Lady - Decisive Dog": 0.8, "Grandmother Willow - Ancient Advisor": 1.0,
    "Mike Wazowski - Heroic Climber": 0.8, "Mickey Mouse & Minnie Mouse - Adventuring Duo": 3.0,
    "Dumbo - Ninth Wonder of the Universe": 2.0, "Minnie Mouse - Pirate Lookout": 1.5,
    "Taffyta Muttonfudge - Sour Speedster": 1.5, "Namaari - Single-Minded Rival": 1.0,
    "Cinderella - Stouthearted": 1.5, "The Muses - Proclaimers of Heroes": 1.5,
    "Henry J. Waternoose III - Chief Executive Officer": 1.0, "Lenny - Toy Binoculars": 0.3,
    "Stitch - Rock Star": 2.0, "Calhoun - Marine Sergeant": 0.8, "Scar - Vicious Cheater": 1.0,
}
ITEM_VALUE = {
    "Maurice's Workshop": 3.0, "Fishbone Quill": 2.5, "Basil's Magnifying Glass": 1.8, "Lucky Dime": 3.5,
    "Sapphire Coil": 1.2, "Pawpsicle": 0.8, "Vitalisphere": 0.9, "Inkrunner": 0.6, "Croquet Mallet": 0.6,
    "Junior Woodchuck Guidebook": 1.5, "Bunch of Balloons": 0.8,
}


LOC_BONUS = {"Sugar Rush Speedway - Finish Line": 2.5, "Carl's House - Flying High": 1.5,
             "Sugar Rush Speedway - Starting Line": 1.0}


def combo_ready(g, x):
    """ゴールラインが場にあり、別のロケーションにいるキャラ＝次に移動して3ロア・3ドローできる。"""
    if x.loc is None:
        return 0.0
    p = g.players[x.owner]
    fl = [l for l in p.locs() if l.card.name == "Sugar Rush Speedway - Finish Line"]
    if fl and all(l.uid != x.loc for l in fl):
        return 2.0
    return 0.0


def threat(g, x):
    """キャラ・アイテム・ロケーションの価値（持ち主から見た価値＝相手から見た脅威）。"""
    c = x.card
    if c.kind == "item":
        return ITEM_VALUE.get(c.name, 1.0)
    if c.kind == "location":
        owner = g.players[x.owner]
        first = next((l for l in owner.locs() if l.card.name == c.name), x) is x
        return effects.loc_lore(g, x) * 1.8 + 0.8 + (LOC_BONUS.get(c.name, 0) if first else -0.5)
    lo = 0 if c.reckless else g.char_lore(x)
    v = 0.8 + lo * 1.7 + g.char_str(x) * 0.3 + max(0, x.left()) * 0.18
    v += ENGINE_BONUS.get(c.name, 0)
    v += combo_ready(g, x)
    if c.ward:
        v += 0.4
    if c.evasive:
        v += 0.4
    return v


def can_be_killed_next(g, x):
    """x（自分の場）が相手の次のターンにチャレンジで倒されそうか。"""
    owner = g.players[x.owner]
    o = g.opp(owner)
    if effects.cant_be_challenged(g, x):
        return False
    guards = [c for c in owner.chars() if c.card.bodyguard and c.exerted and c is not x]
    if guards and not x.card.bodyguard:
        return False
    for a in o.chars():
        if a.flags.get("cant_challenge_until") is not None or a.flags.get("cant_ready"):
            continue
        if x.card.evasive and not (a.card.evasive or a.card.alert):
            continue
        dmg = effects.strength(g, a) + a.card.challenger - x.card.resist
        for kind, pid in g.global_mods:
            if kind == "kida" and pid == x.owner:
                pass
        if dmg >= x.left():
            return True
    return False


def evaluate(g, pid):
    p = g.players[pid]
    o = g.opp(p)
    if g.winner is not None:
        return 1e6 if g.winner == pid else -1e6
    s = 0.0
    # ロア（20に近いほど重く）
    s += W_LORE * (p.lore - o.lore)
    s += 0.06 * (max(0, p.lore - 12) ** 2 - max(0, o.lore - 12) ** 2)
    # 盤面
    for x in p.perms:
        v = threat(g, x)
        if x.card.kind == "char" and x.exerted and g.active == pid and can_be_killed_next(g, x):
            v *= 0.78
        s += v
    for x in o.perms:
        s -= threat(g, x)
    # 捨て札から戻ってくるカード（リロ・抜け出し名人）は除去しても価値が残る
    for q, sign in ((p, 1), (o, -1)):
        if any(c.name == "Lilo - Escape Artist" for c in q.discard):
            s += sign * 2.5
    # 手札
    s += sum(p.policy.hand_value(g, p, c) for c in p.hand)
    s -= W_HAND * len(o.hand)
    # インク
    s += _ink_value(p.ink) - _ink_value(o.ink)
    s += W_DROP * (p.drops - o.drops)
    # 相手の次のターンのアクション・アイテムによる損失の見込み（封じていれば0）
    if g.active == pid and not Policy._busy:
        th = p.policy.opp_threat(g, p)
        if not o.action_locked:
            s -= th["action"] * p.policy.cfg.get("lock_mult", 1.0)
        if not o.item_locked:
            s -= th["item"]
    # 全体除去への出しすぎ
    s -= p.policy.overextend_penalty(g, p)
    return s


def _ink_value(n):
    early = min(n, 7)
    return early * W_INK_EARLY + max(0, n - 7) * W_INK_LATE


# ---------------------------------------------------------------- 行動の列挙


def legal_actions(g, p):
    acts = []
    seen = set()
    for card in p.hand:
        if card.name in seen:
            continue
        seen.add(card.name)
        if g.can_ink(p, card):
            acts.append(("ink", card.name))
        if card.kind == "char":
            if p.ink_free() >= g.char_cost(p, card):
                for t in effects.target_options(g, p, card):
                    acts.append(("play", card.name, "normal", None, t, None))
            if p.ink_free() >= effects.shift_cost(g, p, card) and (card.shift or card.duo_shift):
                for bases in effects.shift_bases(g, p, card):
                    for t in effects.target_options(g, p, card):
                        acts.append(("play", card.name, "shift", tuple(b.uid for b in bases), t, None))
            for mode, extra in effects.alt_play_options(g, p, card):
                for t in effects.target_options(g, p, card):
                    acts.append(("play", card.name, mode, None, t, extra))
        elif card.kind in ("item", "location"):
            if card.kind == "item" and p.item_locked:
                continue
            if p.ink_free() >= g.char_cost(p, card):
                acts.append(("play", card.name, "normal", None, None, None))
        else:
            if p.action_locked:
                continue
            extras = [None]
            if card.name == "Beyond the Horizon":
                extras = [(p.pid,), (p.pid, 1 - p.pid)]
            tgts = effects.target_options(g, p, card)
            if card.is_song:
                for singers in g.singers_for(p, card):
                    for t in tgts:
                        for e in extras:
                            acts.append(("sing", card.name, tuple(s.uid for s in singers), t, e))
            if p.ink_free() >= card.cost:
                for t in tgts:
                    for e in extras:
                        acts.append(("cast", card.name, t, e))
    for (uid, idx, t) in effects.activations(g, p):
        acts.append(("act", uid, idx, t))
    # 移動
    for loc in p.locs():
        for x in p.chars():
            if x.loc != loc.uid and p.ink_free() >= effects.move_cost(g, p, x, loc):
                acts.append(("move", x.uid, loc.uid))
    # チャレンジ
    o = g.opp(p)
    for a in p.chars():
        if a.exerted:
            continue
        for t in o.perms:
            if t.card.kind in ("char", "location") and g.can_challenge(p, a, t):
                acts.append(("challenge", a.uid, t.uid))
    return acts


def card_in_hand(p, name):
    for c in p.hand:
        if c.name == name:
            return c
    return None


def apply(g, p, act):
    kind = act[0]
    if kind == "ink":
        g.do_ink(p, card_in_hand(p, act[1]))
    elif kind == "play":
        _, name, mode, bases, t, extra = act
        card = card_in_hand(p, name)
        b = [g.find(u) for u in bases] if bases else None
        g.play_card(p, card, mode=mode, base=b, target=t, extra=extra)
    elif kind == "sing":
        _, name, singer_uids, t, e = act
        card = card_in_hand(p, name)
        singers = [g.find(u) for u in singer_uids]
        g.play_card(p, card, singers=singers, target=t, extra=e)
    elif kind == "cast":
        _, name, t, e = act
        g.play_card(p, card_in_hand(p, name), target=t, extra=e)
    elif kind == "act":
        effects.activate(g, p, act[1], act[2], act[3])
    elif kind == "move":
        g.move(p, g.find(act[1]), g.find(act[2]))
    elif kind == "challenge":
        g.challenge(p, g.find(act[1]), g.find(act[2]))
    elif kind == "quest":
        g.quest(p, g.find(act[1]))


LOOKAHEAD_KINDS = ("move", "act")
LOCK_CARDS = {"Pete - Games Referee", "Toulouse - Rough and Tumble", "Keep the Ancient Ways"}


def try_action(g, p, act, depth=0):
    h = g.clone()
    hp = h.players[p.pid]
    try:
        apply(h, hp, act)
    except (AssertionError, ValueError, AttributeError, TypeError):
        return -1e9
    v = evaluate(h, p.pid)
    # 移動・ロケーション・起動能力は「次の一手」とセットで価値が出るので、もう1手だけ先を読む
    combo = act[0] in LOOKAHEAD_KINDS or (act[0] == "play" and _is_location(hp, act[1]))
    if combo and depth == 0 and h.winner is None:
        for a2 in legal_actions(h, hp):
            if a2[0] in ("move", "act"):
                v2 = try_action(h, hp, a2, depth=1)
                if v2 > v:
                    v = v2 - 0.05
    return v


def _is_location(p, name):
    from cards import db
    c = db().get(name)
    return c is not None and c.kind == "location"


def pick_target(g, p, card, opts):
    best, bv = opts[0], -1e18
    for t in opts:
        h = g.clone()
        hp = h.players[p.pid]
        try:
            effects.resolve_spell(h, hp, card, t, None) if card.kind == "action" else None
        except Exception:
            continue
        v = evaluate(h, p.pid)
        if v > bv:
            best, bv = t, v
    return best


class Policy:
    def __init__(self, cfg):
        self.cfg = cfg

    # ----- 評価の部品 -----
    def hand_value(self, g, p, c):
        cfg = self.cfg
        v = W_HAND + cfg.get("key", {}).get(c.name, 0)
        if c.name in LOCK_CARDS and not Policy._busy:
            # ロック役は「次のターン以降に使える封じ」として手札に残す価値がある
            v += 0.35 * self.opp_threat(g, p)["action"]
        if c.cost > p.ink + 3:
            v -= 0.25
        return v

    def card_value(self, g, p, c):
        return self.hand_value(g, p, c) + (0.3 if c.cost <= p.ink + 1 else 0)

    def lock_bonus(self, g, o, kind):
        """相手のアクション（アイテム）を封じた価値。

        「相手が次のターンに使えそうなアクション」を相手のデッキリストから洗い出し、
        それぞれ実際に使われた場合に自分の盤面評価がどれだけ下がるかを先読みして、
        手札にある確率を掛けた期待損失（上位2枚分）を封じた価値とする。相手の手札は覗かない。
        """
        p = g.opp(o)
        t = self.opp_threat(g, p)
        return t["action"] if kind == "action" else t["item"]

    _busy = False

    def opp_threat(self, g, p):
        o = g.opp(p)
        key = (g.turn, p.pid, p.lore, o.lore, len(o.hand), o.ink,
               tuple((x.card.name, x.damage, x.exerted) for x in p.perms),
               tuple((x.card.name, x.damage, x.exerted) for x in o.perms))
        cache = self.__dict__.setdefault("_threat_cache", {})
        if key in cache:
            return cache[key]
        if Policy._busy:
            return {"action": 0.0, "item": 0.0}
        Policy._busy = True
        try:
            res = self._compute_threat(g, p)
        finally:
            Policy._busy = False
        if len(cache) > 5000:
            cache.clear()
        cache[key] = res
        return res

    def _compute_threat(self, g, p):
        from cards import db
        o = g.opp(p)
        counts = dict(self.cfg.get("_opp_counts", {}))
        for c in o.discard:
            if c.name in counts:
                counts[c.name] -= 1
        for x in o.perms:
            if x.card.name in counts:
                counts[x.card.name] -= 1
        pool = sum(max(0, v) for v in counts.values()) or 1
        hand = len(o.hand)
        if hand == 0:
            return {"action": 0.0, "item": 0.0}
        ink_next = o.ink + 1 + o.drops
        singers = [x for x in o.chars() if not x.card.reckless]
        base = evaluate(g, p.pid)
        acts, items = [], []
        cdb = db()
        for name, n in counts.items():
            if n <= 0:
                continue
            card = cdb[name]
            prob = min(1.0, hand * n / pool)
            if card.kind == "item":
                if card.cost <= ink_next:
                    items.append(prob * ITEM_VALUE.get(name, 1.0))
                continue
            if card.kind != "action":
                continue
            castable = card.cost <= ink_next
            if card.is_song and not castable:
                if card.sing_together:
                    castable = sum(g.singer_value(x) for x in singers) >= card.sing_together
                else:
                    castable = any(g.singer_value(x) >= card.cost for x in singers)
            if not castable:
                continue
            h = g.clone()
            ho = h.players[o.pid]
            h.active = o.pid
            try:
                tgt = effects.auto_target(h, ho, card)
                effects.resolve_spell(h, ho, card, tgt, None)
                if card.is_song:
                    ho.t.setdefault("spells", []).append(card)
                effects.after_spell(h, ho, card, None)
            except Exception:
                continue
            # 歌を使うと得をする相手のキャラ（オーロラのターン終了時ロアなど）も損失に含める
            if card.is_song and not ho.t.get("_sang"):
                if any(x.card.name == "Aurora - Delightful Musician" for x in ho.chars()):
                    h.gain_lore(ho, 1)
            h.active = p.pid
            loss = base - evaluate(h, p.pid)
            if loss > 0:
                acts.append(prob * loss)
        acts.sort(reverse=True)
        items.sort(reverse=True)
        return {"action": sum(acts[:2]), "item": 0.2 + sum(items[:2])}

    def overextend_penalty(self, g, p):
        o = g.opp(p)
        wipe = self.cfg.get("_opp_wipe", 0)
        if not wipe:
            return 0.0
        n = len(p.chars())
        if n <= 4:
            return 0.0
        return (n - 4) * 0.5 * wipe * (1.0 if o.ink >= 5 else 0.3)

    # ----- 選択 -----
    def discard_choice(self, g, p):
        return min(p.hand, key=lambda c: self.card_value(g, p, c))

    def ink_choice(self, g, p, any_card=False):
        never = self.cfg.get("never_ink", set())
        cands = [c for c in p.hand if any_card or c.inkable]
        if not any_card and p.ink >= 4:
            cands = [c for c in cands if c.name not in never]
        if not cands:
            return None

        def score(c):
            v = self.card_value(g, p, c)
            if c.name in never:
                v += 3
            if sum(1 for d in p.hand if d.name == c.name) >= 2:
                v -= 0.3
            return v
        return min(cands, key=score)

    def mulligan(self, g, p):
        cfg = self.cfg
        keep = cfg.get("keep", set())
        ship = cfg.get("ship", set())
        back = []
        for c in p.hand:
            if c.name in keep:
                continue
            if c.name in ship or (c.cost >= 5 and c.name not in keep):
                back.append(c)
        low = sum(1 for c in p.hand if c not in back and c.cost <= 3)
        if low < 2:
            back = [c for c in p.hand if c.cost >= 4 and c.name not in keep]
        inkable = sum(1 for c in p.hand if c not in back and c.inkable)
        if inkable < 2:
            extra = [c for c in p.hand if c not in back and not c.inkable and c.name not in keep]
            back += extra[:2 - inkable]
        return back

    # ----- ターン -----
    def play_turn(self, g, p):
        # インク
        if self.cfg.get("ink_cap", 9) > p.ink:
            c = self.ink_choice(g, p)
            if c is not None and g.can_ink(p, c):
                g.do_ink(p, c)
        for _ in range(25):
            if g.winner is not None:
                return
            if self.lethal(g, p):
                break
            acts = [a for a in legal_actions(g, p) if a[0] != "ink" or g.can_ink(p, card_in_hand(p, a[1]))]
            if not acts:
                break
            base = evaluate(g, p.pid)
            best, bv = None, base + 0.15
            for a in acts:
                v = try_action(g, p, a)
                if v > bv:
                    best, bv = a, v
            if best is None:
                break
            apply(g, p, best)
        if g.winner is not None:
            return
        self.reckless_challenges(g, p)
        self.quests(g, p)

    def lethal(self, g, p):
        ready = [x for x in p.chars() if not x.exerted and not x.dry and not x.card.reckless]
        return p.lore + sum(g.char_lore(x) for x in ready) >= WIN_LORE

    def reckless_challenges(self, g, p):
        o = g.opp(p)
        for a in list(p.chars()):
            if not a.card.reckless or a.exerted or a not in p.perms:
                continue
            ts = [t for t in o.perms if t.card.kind in ("char", "location") and g.can_challenge(p, a, t)]
            if ts:
                best = max(ts, key=lambda t: try_action(g, p, ("challenge", a.uid, t.uid)))
                g.challenge(p, a, best)
                if g.winner is not None:
                    return

    def quests(self, g, p):
        cands = [x for x in p.chars() if not x.exerted and not x.dry and not x.card.reckless
                 and x.flags.get("no_quest") != g.turn]
        must = self.lethal(g, p)
        for x in sorted(cands, key=lambda x: -g.char_lore(x)):
            if g.winner is not None:
                return
            if x not in p.perms or x.exerted:
                continue
            if must or x.card.adventurous:
                g.quest(p, x)
                continue
            base = evaluate(g, p.pid)
            v = try_action(g, p, ("quest", x.uid))
            if v >= base - 0.05 or g.char_lore(x) >= 2:
                g.quest(p, x)
