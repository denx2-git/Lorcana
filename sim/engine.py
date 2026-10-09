"""ロルカナ簡易シミュレーター v2：対戦の進行（ルール処理）。

カード個別の効果は effects.py、Botの判断は ai.py。
"""
import random

from cards import parse_list

WIN_LORE = 20
MAX_TURNS = 50


class Perm:
    """場のカード（キャラ・アイテム・ロケーション）。"""
    __slots__ = ("uid", "card", "owner", "damage", "exerted", "dry", "loc", "tmp_str", "tmp_lore",
                 "flags", "played_turn")

    def __init__(self, uid, card, owner, turn):
        self.uid = uid
        self.card = card
        self.owner = owner
        self.damage = 0
        self.exerted = False
        self.dry = card.kind == "char"
        self.loc = None
        self.tmp_str = 0
        self.tmp_lore = 0
        self.flags = {}
        self.played_turn = turn

    def clone(self):
        p = Perm.__new__(Perm)
        p.uid, p.card, p.owner, p.damage = self.uid, self.card, self.owner, self.damage
        p.exerted, p.dry, p.loc, p.tmp_str, p.tmp_lore = self.exerted, self.dry, self.loc, self.tmp_str, self.tmp_lore
        p.flags = dict(self.flags) if self.flags else {}
        p.played_turn = self.played_turn
        return p

    @property
    def name(self):
        return self.card.name

    @property
    def kind(self):
        return self.card.kind

    def left(self):
        return self.card.wp - self.damage


class Player:
    def __init__(self, pid, deck_key, deck, policy):
        self.pid = pid
        self.deck_key = deck_key
        self.deck = deck
        self.policy = policy
        self.hand = []
        self.ink = 0
        self.ink_used = 0
        self.drops = 0
        self.perms = []
        self.discard = []
        self.lore = 0
        self.action_locked = False
        self.item_locked = False
        self.t = {}  # このターンだけの情報

    def clone(self):
        q = Player.__new__(Player)
        q.pid, q.deck_key, q.policy = self.pid, self.deck_key, self.policy
        q.deck = list(self.deck)
        q.hand = list(self.hand)
        q.ink, q.ink_used, q.drops = self.ink, self.ink_used, self.drops
        q.perms = [p.clone() for p in self.perms]
        q.discard = list(self.discard)
        q.lore = self.lore
        q.action_locked, q.item_locked = self.action_locked, self.item_locked
        q.t = {k: (list(v) if isinstance(v, list) else v) for k, v in self.t.items()}
        return q

    def chars(self):
        return [p for p in self.perms if p.card.kind == "char"]

    def items(self):
        return [p for p in self.perms if p.card.kind == "item"]

    def locs(self):
        return [p for p in self.perms if p.card.kind == "location"]

    def ink_free(self):
        return self.ink - self.ink_used + self.drops

    def pay(self, n):
        n = max(0, n)
        free = self.ink - self.ink_used
        use = min(free, n)
        self.ink_used += use
        self.drops -= (n - use)
        assert self.drops >= 0


class Game:
    def __init__(self, deck_a, deck_b, pol_a, pol_b, first=0, seed=None, log=False, lists=None):
        import effects  # noqa: F401  効果の登録
        self.rng = random.Random(seed)
        self.logging = log
        self.lines = []
        self.uid = 0
        self.players = []
        from decks import DECKS
        lists = lists or {}
        for pid, (key, pol) in enumerate([(deck_a, pol_a), (deck_b, pol_b)]):
            cards = parse_list(lists.get(pid) or DECKS[key]["list_text"])
            self.rng.shuffle(cards)
            self.players.append(Player(pid, key, cards, pol))
        self.turn = 0
        self.active = first
        self.first = first
        self.winner = None
        self.reason = None
        self.global_mods = []   # [(種類, 期限のpid)]
        self.sim = False        # Botの先読み中か

    # ----- 複製（Botの先読み用） -----
    def clone(self):
        g = Game.__new__(Game)
        g.rng = random.Random()
        g.rng.setstate(self.rng.getstate())
        g.logging = False
        g.lines = []
        g.uid = self.uid
        g.players = [p.clone() for p in self.players]
        g.turn, g.active, g.first = self.turn, self.active, self.first
        g.winner, g.reason = self.winner, self.reason
        g.global_mods = list(self.global_mods)
        g.sim = True
        return g

    def log(self, s):
        if self.logging:
            self.lines.append(s)

    def opp(self, p):
        return self.players[1 - p.pid]

    def find(self, uid):
        for pl in self.players:
            for x in pl.perms:
                if x.uid == uid:
                    return x
        return None

    def new_perm(self, card, owner):
        self.uid += 1
        return Perm(self.uid, card, owner, self.turn)

    # ----- 基本処理 -----
    def end(self, pid, why):
        if self.winner is None:
            self.winner = pid
            self.reason = why

    def draw(self, p, n=1):
        import effects
        for _ in range(n):
            if self.winner is not None:
                return
            if not p.deck:
                self.end(1 - p.pid, "deckout")
                return
            p.hand.append(p.deck.pop(0))
            effects.on_draw(self, p)

    def gain_lore(self, p, n):
        if n <= 0 or self.winner is not None:
            return
        p.lore += n
        if p.lore >= WIN_LORE:
            self.end(p.pid, "lore")

    def lose_lore(self, p, n):
        p.lore = max(0, p.lore - n)

    def to_discard_card(self, p, card):
        p.discard.append(card)
        p.t["discarded"] = p.t.get("discarded", 0) + 1

    def discard_from_hand(self, p, card):
        import effects
        p.hand.remove(card)
        self.to_discard_card(p, card)
        effects.on_discard(self, p, 1)

    def leave_play(self, x, dest="discard"):
        """x を場から離す。dest: discard / hand / inkwell / deck_bottom / deck_top"""
        import effects
        owner = self.players[x.owner]
        if x not in owner.perms:
            return
        if x.card.kind == "location":
            for c in owner.chars():
                if c.loc == x.uid:
                    c.loc = None
        owner.perms.remove(x)
        if dest == "discard":
            self.to_discard_card(owner, x.card)
        elif dest == "hand":
            owner.hand.append(x.card)
        elif dest == "inkwell":
            owner.ink += 1
            owner.ink_used += 1
        elif dest == "inkwell_ready":
            owner.ink += 1
        elif dest == "deck_bottom":
            owner.deck.append(x.card)
        elif dest == "deck_top":
            owner.deck.insert(0, x.card)
        effects.on_leave(self, x, dest)

    def banish(self, x, by_challenge=False):
        import effects
        if effects.replace_banish(self, x):
            return
        self.log(f"  {x.card.jp} が退場")
        self.leave_play(x, "discard")
        effects.on_banished(self, x, by_challenge)

    def deal(self, x, n, src=None, ignore_resist=False):
        """ダメージを与える。退場したら True。"""
        import effects
        if x is None or x.card.kind == "item":
            return False
        if n <= 0:
            return False
        if x.card.kind == "char":
            n = effects.modify_damage(self, x, n, src, ignore_resist)
        if n <= 0:
            return False
        x.damage += n
        if x.damage >= x.card.wp:
            self.banish(x, by_challenge=src == "challenge")
            return True
        return False

    def char_str(self, x):
        import effects
        return max(0, effects.strength(self, x))

    def char_lore(self, x):
        import effects
        return max(0, effects.lore(self, x))

    def singer_value(self, x):
        import effects
        return effects.singer_value(self, x)

    # ----- ゲーム進行 -----
    def setup(self):
        for p in self.players:
            self.draw(p, 7)
            back = p.policy.mulligan(self, p)
            for c in back:
                p.hand.remove(c)
            p.deck += back
            self.draw(p, len(back))
            self.rng.shuffle(p.deck)
            self.log(f"P{p.pid}（{p.deck_key}）マリガン{len(back)}枚")

    def play_game(self):
        self.setup()
        while self.winner is None and self.turn < MAX_TURNS:
            self.turn += 1
            self.take_turn(self.players[self.active])
            self.active = 1 - self.active
        return self.winner

    def start_turn(self, p):
        import effects
        o = self.opp(p)
        o.action_locked = False
        o.item_locked = False
        self.global_mods = [m for m in self.global_mods if m[1] != p.pid]
        for x in o.perms:
            if x.flags.get("cant_challenge_until") == p.pid:
                del x.flags["cant_challenge_until"]
        p.t = {"first_turn": self.turn <= 2}
        p.ink_used = 0
        effects.start_of_turn_pre(self, p)   # ロケーションのロア・野獣など
        if self.winner is not None:
            return
        for x in p.perms:
            if x.card.kind == "char" and x.flags.get("cant_ready"):
                pass
            else:
                x.exerted = False
            x.dry = False
            x.tmp_str = 0
            x.tmp_lore = 0
            for k in ("rush", "alert", "challenger", "challenge_ready"):
                x.flags.pop(k, None)
        if self.turn != 1:
            self.draw(p)
        effects.start_of_turn_post(self, p)

    def take_turn(self, p):
        import effects
        self.log(f"--- T{self.turn} P{p.pid}（{p.deck_key}）ロア 自{p.lore} 相{self.opp(p).lore} インク{p.ink}")
        self.start_turn(p)
        if self.winner is not None:
            return
        p.policy.play_turn(self, p)
        if self.winner is not None:
            return
        effects.end_of_turn(self, p)
        for x in p.perms:
            x.tmp_str = 0
            x.tmp_lore = 0

    # ----- 行動 -----
    def can_ink(self, p, card):
        extra = p.t.get("extra_ink", 0)
        return card.inkable and p.t.get("inked", 0) < 1 + extra

    def do_ink(self, p, card):
        import effects
        p.hand.remove(card)
        p.ink += 1
        p.t["inked"] = p.t.get("inked", 0) + 1
        self.log(f"  インク: {card.jp}")
        effects.on_ink(self, p)

    def put_card_in_inkwell(self, p, card, exerted=True):
        import effects
        p.ink += 1
        if exerted:
            p.ink_used += 1
        effects.on_ink(self, p)

    def char_cost(self, p, card):
        import effects
        return effects.cost_for(self, p, card)

    def play_card(self, p, card, mode="normal", base=None, target=None, singers=None, extra=None):
        """手札のカードをプレイ。mode: normal / shift / free / alt"""
        import effects
        o = self.opp(p)
        p.hand.remove(card)
        if card.kind == "char":
            if mode == "shift":
                p.pay(effects.shift_cost(self, p, card))
            elif mode in ("free", "alt"):
                effects.pay_alt(self, p, card, extra)
            else:
                p.pay(self.char_cost(p, card))
                effects.consume_discounts(self, p, card)
            x = self.new_perm(card, p.pid)
            if mode == "shift" and base is not None:
                bases = base if isinstance(base, (list, tuple)) else [base]
                b0 = bases[0]
                x.damage, x.exerted, x.dry, x.loc = b0.damage, b0.exerted, b0.dry, b0.loc
                idx = p.perms.index(b0)
                p.perms[idx] = x
                for b in bases[1:]:
                    p.perms.remove(b)
                x.flags["under"] = len(bases)
            else:
                p.perms.append(x)
            p.t["chars_played"] = p.t.get("chars_played", 0) + 1
            self.log(f"  プレイ: {card.jp}" + ("（変身）" if mode == "shift" else ""))
            effects.on_play_char(self, p, x, target, extra)
            effects.after_char_played(self, p, x)
            return x
        if card.kind in ("item", "location"):
            if mode not in ("free",):
                p.pay(self.char_cost(p, card))
            x = self.new_perm(card, p.pid)
            p.perms.append(x)
            self.log(f"  プレイ: {card.jp}")
            effects.on_play_perm(self, p, x, target, extra)
            return x
        # アクション・歌
        if singers:
            for s in singers:
                s.exerted = True
            self.log(f"  {card.jp}（歌う: {'・'.join(s.card.jp for s in singers)}）")
        elif mode == "free":
            self.log(f"  {card.jp}（無料）")
        else:
            p.pay(card.cost)
            self.log(f"  {card.jp}（{card.cost}インク）")
        effects.resolve_spell(self, p, card, target, extra)
        if card in p.hand:
            pass
        self.to_discard_card(p, card)
        p.t.setdefault("spells", []).append(card)
        effects.after_spell(self, p, card, singers)
        return None

    def can_challenge(self, p, att, tgt):
        import effects
        o = self.opp(p)
        if att.card.kind != "char" or att.exerted:
            return False
        if att.dry and not (att.card.rush or att.flags.get("rush") or effects.has_rush(self, att)):
            return False
        if att.flags.get("cant_challenge_until") is not None:
            return False
        if tgt.owner == p.pid:
            return False
        if tgt.card.kind == "location":
            if effects.loc_evasive(self, tgt) and not (att.card.evasive or att.card.alert or att.flags.get("alert")):
                return False
            return True
        if tgt.card.kind != "char":
            return False
        if not tgt.exerted and not att.flags.get("challenge_ready"):
            return False
        if (tgt.card.evasive or effects.gains_evasive(self, tgt)) and not (
                att.card.evasive or att.card.alert or att.flags.get("alert") or effects.gains_evasive(self, att)):
            return False
        if effects.cant_be_challenged(self, tgt):
            return False
        guards = [c for c in o.chars() if c.card.bodyguard and c.exerted and c is not tgt
                  and not effects.cant_be_challenged(self, c)]
        if guards and not tgt.card.bodyguard:
            # 護衛を選べるなら護衛を選ばなければならない（回避などで選べない場合は除く）
            ok_guards = [gd for gd in guards if not (gd.card.evasive and not (att.card.evasive or att.card.alert))]
            if ok_guards:
                return False
        return True

    def challenge(self, p, att, tgt):
        import effects
        o = self.opp(p)
        att.exerted = True
        self.log(f"  チャレンジ: {att.card.jp} → {tgt.card.jp}")
        effects.on_challenge(self, p, att, tgt)
        a = self.char_str(att) + effects.challenger_bonus(self, att)
        if tgt.card.kind == "location":
            self.deal(tgt, a, src="challenge")
            return
        d = self.char_str(tgt)
        effects.on_challenged(self, o, tgt, att)
        tgt_alive_before = tgt in o.perms
        killed = self.deal(tgt, a, src="challenge") if tgt_alive_before else False
        if not effects.no_damage_from_challenge(self, att):
            self.deal(att, d, src="challenge")
        if killed:
            effects.on_banish_in_challenge(self, p, att, tgt)

    def quest(self, p, x):
        import effects
        x.exerted = True
        n = self.char_lore(x)
        self.log(f"  クエスト: {x.card.jp}（+{n}）")
        self.gain_lore(p, n)
        if self.winner is None:
            effects.on_quest(self, p, x)

    def move(self, p, x, loc):
        import effects
        cost = effects.move_cost(self, p, x, loc)
        p.pay(cost)
        prev = x.loc
        x.loc = loc.uid
        self.log(f"  移動: {x.card.jp} → {loc.card.jp}")
        effects.on_move(self, p, x, loc, prev)

    def singers_for(self, p, card):
        """歌える組み合わせの候補（最大数通り）。"""
        import effects
        ready = [x for x in p.chars() if not x.exerted and not x.dry and effects.can_sing(self, x)]
        if card.sing_together:
            ready_all = [x for x in p.chars() if not x.exerted and not x.dry]
            ready_all.sort(key=lambda x: (self.char_lore(x), x.card.cost))
            chosen, tot = [], 0
            for x in ready_all:
                v = self.singer_value(x)
                chosen.append(x)
                tot += v
                if tot >= card.sing_together:
                    return [chosen]
            return []
        ok = [x for x in ready if self.singer_value(x) >= card.cost]
        if not ok:
            return []
        ok.sort(key=lambda x: (self.char_lore(x), x.card.cost))
        return [[ok[0]]]


def run_game(deck_a, deck_b, pol_a, pol_b, first, seed, log=False, lists=None):
    g = Game(deck_a, deck_b, pol_a, pol_b, first=first, seed=seed, log=log, lists=lists)
    g.play_game()
    return g
