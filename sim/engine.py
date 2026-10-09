"""ロルカナ簡易シミュレーター（デッキ限定・ヒューリスティックBot）。

対応していないルール（今回の2デッキに関係しないもの）：
ロケーション、アイテム、移動、チームプレイ、一部の任意効果の細かい選択。
Botは「そこそこ」のプレイをする前提で、勝率は目安として使う。
"""
import random
from dataclasses import dataclass, field

from cards import CARDS, Card, parse_list, DECKS

WIN_LORE = 20
MAX_TURNS = 60


@dataclass
class Char:
    card: Card
    damage: int = 0
    exerted: bool = False
    dry: bool = True          # True = このターンに出た（クエスト・チャレンジ・歌えない）
    temp_str: int = 0
    cant_challenge: bool = False

    @property
    def name(self):
        return self.card.name

    def str_(self):
        return self.card.str_ + self.temp_str

    def left(self):
        return self.card.wp - self.damage


@dataclass
class Player:
    pid: int
    deck_name: str
    policy: "Policy"
    deck: list
    hand: list = field(default_factory=list)
    ink_total: int = 0
    ink_used: int = 0
    drops: int = 0
    board: list = field(default_factory=list)
    discard: list = field(default_factory=list)
    lore: int = 0
    action_locked: bool = False
    item_locked: bool = False
    inked_this_turn: bool = False
    songs_this_turn: list = field(default_factory=list)
    powerline_used: bool = False
    akood_discount: int = 0
    first_turn: bool = True

    def ink_avail(self):
        return self.ink_total - self.ink_used + self.drops

    def pay(self, n):
        free = self.ink_total - self.ink_used
        use = min(free, n)
        self.ink_used += use
        rest = n - use
        assert rest <= self.drops
        self.drops -= rest


class Game:
    def __init__(self, deck_a, deck_b, policy_a, policy_b, first=0, seed=None, log=False):
        self.rng = random.Random(seed)
        self.logging = log
        self.lines = []
        self.players = []
        for pid, (dn, pol) in enumerate([(deck_a, policy_a), (deck_b, policy_b)]):
            cards = parse_list(DECKS[dn])
            self.rng.shuffle(cards)
            self.players.append(Player(pid, dn, pol, cards))
        self.turn_no = 0
        self.active = first
        self.first = first
        self.winner = None
        self.stats = {"lock_turns": [0, 0]}

    # ---------- 共通処理 ----------
    def log(self, msg):
        if self.logging:
            self.lines.append(msg)

    def opp(self, p):
        return self.players[1 - p.pid]

    def draw(self, p, n=1):
        for _ in range(n):
            if not p.deck:
                self.end(self.opp(p), "deckout")
                return
            p.hand.append(p.deck.pop(0))

    def gain_lore(self, p, n):
        if n <= 0 or self.winner is not None:
            return
        p.lore += n
        if p.lore >= WIN_LORE:
            self.end(p, "lore")

    def end(self, p, why):
        if self.winner is None:
            self.winner = p.pid
            self.win_reason = why

    def to_discard(self, owner, ch):
        owner.board.remove(ch)
        owner.discard.append(ch.card)

    def deal(self, target_owner, ch, n):
        dmg = max(0, n - ch.card.resist)
        ch.damage += dmg
        if ch.left() <= 0:
            self.log(f"  {ch.card.jp} が退場")
            self.to_discard(target_owner, ch)
            return True
        return False

    def to_inkwell(self, owner, ch):
        owner.board.remove(ch)
        owner.ink_total += 1
        owner.ink_used += 1  # 裏向き・エグザートで置く
        self.log(f"  {ch.card.jp} が相手のインクへ")

    def singer_value(self, p, ch):
        if ch.name == "Miguel Rivera - Street Musician":
            return 3 if any(c.kind == "song" for c in p.discard) else 0
        return ch.card.singer or ch.card.cost

    def char_lore(self, p, ch):
        lore = ch.card.lore
        if ch.name == "Miguel Rivera - Street Musician" and any(c.kind == "song" for c in p.discard):
            lore += 1
        if ch.name == "Powerline - Megastar":
            lore += sum(1 for o in p.board if o is not ch and (o.card.singer or (
                o.name == "Miguel Rivera - Street Musician" and any(c.kind == "song" for c in p.discard))))
        return lore

    # ---------- ゲーム進行 ----------
    def setup(self):
        for p in self.players:
            self.draw(p, 7)
            back = p.policy.mulligan(self, p)
            for c in back:
                p.hand.remove(c)
            p.deck += back
            self.draw(p, len(back))
            self.rng.shuffle(p.deck)
            self.log(f"P{p.pid}（{p.deck_name}）マリガン {len(back)}枚")

    def play(self):
        self.setup()
        while self.winner is None and self.turn_no < MAX_TURNS:
            self.turn_no += 1
            self.take_turn(self.players[self.active])
            self.active = 1 - self.active
        return self.winner

    def take_turn(self, p):
        o = self.opp(p)
        self.log(f"--- T{self.turn_no} P{p.pid}（{p.deck_name}） ロア {p.lore}-{o.lore}")
        # 相手にかけていたロックはこのターン開始時に解除
        o.action_locked = False
        o.item_locked = False
        for ch in o.board:
            ch.cant_challenge = False
        # レディ
        p.ink_used = 0
        for ch in p.board:
            ch.exerted = False
            ch.dry = False
            ch.temp_str = 0
        p.inked_this_turn = False
        p.songs_this_turn = []
        p.powerline_used = False
        p.akood_discount = 0
        # ドロー（先攻1ターン目以外）
        if not (self.turn_no == 1):
            self.draw(p)
        if self.winner is not None:
            return
        # 野獣
        for ch in list(p.board):
            if ch.name == "Beast - Tragic Hero":
                if ch.damage == 0:
                    self.draw(p)
                else:
                    ch.temp_str += 4
        p.policy.main(self, p)
        if self.winner is not None:
            return
        # ターン終了時
        if any(c.kind == "song" for c in p.songs_this_turn):
            for ch in p.board:
                if ch.name == "Aurora - Delightful Musician":
                    self.gain_lore(p, 1)
        if o.action_locked:
            self.stats["lock_turns"][p.pid] += 1
        p.first_turn = False

    # ---------- 行動 ----------
    def ink(self, p, card):
        assert card.inkable and not p.inked_this_turn
        p.hand.remove(card)
        p.ink_total += 1
        p.inked_this_turn = True
        self.log(f"  インク: {card.jp}")

    def can_play(self, p, card, cost=None):
        if card.kind in ("action", "song") and p.action_locked:
            return False
        return p.ink_avail() >= (card.cost if cost is None else cost)

    def card_cost(self, p, card):
        cost = card.cost
        if card.name == "Angel - Siren Singer" and p.first_turn and self.first != p.pid:
            cost -= 1
        if card.kind == "char" and p.akood_discount:
            cost = max(0, cost - p.akood_discount)
        return cost

    def play_char(self, p, card, shift_onto=None, **kw):
        o = self.opp(p)
        if shift_onto is not None:
            cost = card.shift
        else:
            cost = self.card_cost(p, card)
        p.pay(cost)
        if card.kind == "char" and p.akood_discount:
            p.akood_discount = 0
        p.hand.remove(card)
        if shift_onto is not None:
            idx = p.board.index(shift_onto)
            ch = Char(card, damage=shift_onto.damage, exerted=shift_onto.exerted, dry=shift_onto.dry)
            p.board[idx] = ch  # 変身元のカードは下に重なる（簡略化のため保持しない）
        else:
            ch = Char(card)
            p.board.append(ch)
        self.log(f"  プレイ: {card.jp}（{cost}）")
        n = card.name
        if n == "Priscilla - Efficient Clerk":
            ch.exerted = True
        elif n in ("Pete - Games Referee", "Toulouse - Rough and Tumble"):
            o.action_locked = True
        elif n == "Bellwether - Highly Qualified":
            t = kw.get("target")
            if t is not None and t in o.board:
                self.to_inkwell(o, t)
        elif n == "Hades - Infernal Schemer":
            t = kw.get("target")
            if t is not None and t in o.board:
                o.board.remove(t)
                o.ink_total += 1
                self.log(f"  {t.card.jp} が相手のインクへ")
        elif n in ("Ariel - Spectacular Singer", "Meilin Lee - Losing Control"):
            top = p.deck[:4]
            songs = [c for c in top if c.kind == "song"]
            pick = p.policy.pick_song(self, p, songs) if songs else None
            rest = [c for c in top if c is not pick]
            del p.deck[:4]
            if pick:
                p.hand.append(pick)
                self.log(f"  {pick.jp} を手札へ")
            p.deck += rest
        elif n == "Aurora - Delightful Musician":
            cands = [c for c in p.songs_this_turn if c.cost <= 3 and c in p.discard]
            if cands:
                c = max(cands, key=lambda c: p.policy.card_value(self, p, c))
                p.discard.remove(c)
                p.hand.append(c)
                self.log(f"  {c.jp} を回収")
        return ch

    def play_spell(self, p, card, singers=None, **kw):
        """アクション・歌をプレイ。singers を渡すと歌って無料。"""
        o = self.opp(p)
        if singers:
            for s in singers:
                s.exerted = True
            how = "歌う: " + "・".join(s.card.jp for s in singers)
        else:
            p.pay(card.cost)
            how = f"{card.cost}インク"
        p.hand.remove(card)
        self.log(f"  {card.jp}（{how}）")
        n = card.name
        t = kw.get("target")
        if n == "Scram!" or n == "Let It Go":
            if t is not None and t in o.board:
                self.to_inkwell(o, t)
        elif n == "Keep the Ancient Ways":
            o.action_locked = True
            o.item_locked = True
        elif n == "Let the Storm Rage On":
            if t is not None and t in o.board:
                self.deal(o, t, 2)
            self.draw(p)
        elif n == "Hot Potato":
            if t is not None and t in o.board:
                self.deal(o, t, 2)
        elif n == "Ink Explosion":
            if t is not None and t in o.board:
                self.deal(o, t, 4)
            p.drops += 1
        elif n == "Grab Your Sword":
            for ch in list(o.board):
                self.deal(o, ch, 2)
        elif n == "Strength of a Raging Fire":
            if t is not None and t in o.board:
                self.deal(o, t, len(p.board))
        elif n == "And Then Along Came Zeus":
            if t is not None and t in o.board:
                self.deal(o, t, 5)
        elif n == "Akood et Emuti":
            p.akood_discount = 2
            self.draw(p)
        elif n == "Beyond the Horizon":
            for q in kw.get("players", [p]):
                q.discard += q.hand
                q.hand = []
                self.draw(q, 3)
        p.discard.append(card)
        if card.kind == "song":
            p.songs_this_turn.append(card)
            if not p.powerline_used and any(c.name == "Powerline - Megastar" for c in p.board):
                back = [c for c in p.discard if c.kind == "char" and (c.singer or c.name.startswith("Miguel"))]
                if back:
                    c = max(back, key=lambda c: c.cost)
                    p.discard.remove(c)
                    p.hand.append(c)
                    p.powerline_used = True
                    self.log(f"  パワーライン: {c.jp} を回収")

    def can_challenge(self, p, att, tgt):
        o = self.opp(p)
        if att.exerted or att.dry or att.cant_challenge:
            return False
        ready_ok = att.name == "Cinderella - Stouthearted" and p.songs_this_turn
        if not tgt.exerted and not ready_ok:
            return False
        if tgt.card.evasive and not (att.card.evasive or att.card.alert):
            return False
        guards = [c for c in o.board if c.card.bodyguard and c.exerted and c is not tgt]
        if guards and not tgt.card.bodyguard:
            return False
        return True

    def challenge(self, p, att, tgt):
        o = self.opp(p)
        att.exerted = True
        self.log(f"  チャレンジ: {att.card.jp} → {tgt.card.jp}")
        a_str, t_str = att.str_(), tgt.str_()
        self.deal(o, tgt, a_str)
        self.deal(p, att, t_str)

    def quest(self, p, ch):
        ch.exerted = True
        n = self.char_lore(p, ch)
        self.log(f"  クエスト: {ch.card.jp}（+{n}）")
        self.gain_lore(p, n)
        if ch.name == "Priscilla - Efficient Clerk" and p.deck:
            top = p.deck[:2]
            del p.deck[:2]
            if len(top) == 2:
                keep = max(top, key=lambda c: p.policy.card_value(self, p, c))
                other = top[1] if keep is top[0] else top[0]
                p.hand.append(keep)
                p.ink_total += 1
                p.ink_used += 1
            else:
                p.hand += top


def run_game(deck_a, deck_b, pol_a, pol_b, first, seed, log=False):
    g = Game(deck_a, deck_b, pol_a, pol_b, first=first, seed=seed, log=log)
    g.play()
    return g
