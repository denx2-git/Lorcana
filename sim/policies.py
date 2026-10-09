"""Botの思考ロジック。

共通の流れ：インク → 盤面に効くプレイを点数順に繰り返す → 有利なチャレンジ → 残りでクエスト。
デッキごとの違い（インクの優先順位・マリガン・ロック重視度など）はサブクラスで設定する。
"""
from engine import WIN_LORE


class Policy:
    ink_pref = {}          # 大きいほどインクに置きやすい
    mull_back = set()      # マリガンで戻すカード
    lock_value = 0.0       # 相手のアクションを封じる価値
    ink_cap = 8            # これ以上はインクを伸ばさない
    special = {}           # キャラの追加価値（相手から見た脅威度にも使う）

    def __init__(self, **opts):
        self.opts = opts

    # ---------- 評価 ----------
    def threat(self, g, owner, ch):
        v = g.char_lore(owner, ch) * 2.0 + ch.str_() * 0.3 + ch.card.cost * 0.3
        v += THREAT_BONUS.get(ch.name, 0)
        return v

    def card_value(self, g, p, card):
        return 10 - self.ink_pref.get(card.name, 2)

    def pick_song(self, g, p, songs):
        return max(songs, key=lambda c: self.card_value(g, p, c))

    def mulligan(self, g, p):
        back = [c for c in p.hand if c.name in self.mull_back]
        return back

    # ---------- インク ----------
    def choose_ink(self, g, p):
        if p.ink_total >= self.ink_cap:
            return None
        cands = [c for c in p.hand if c.inkable]
        if not cands:
            return None
        counts = {}
        for c in p.hand:
            counts[c.name] = counts.get(c.name, 0) + 1

        def pref(c):
            v = self.ink_pref.get(c.name, 2)
            if counts[c.name] >= 2:
                v += 1.5
            # 当分出せない重いカードは置きやすく
            if c.cost >= p.ink_total + 4:
                v += 1
            return v
        return max(cands, key=pref)

    # ---------- 標的選び ----------
    def targets(self, g, p, pred):
        o = g.opp(p)
        return [ch for ch in o.board if not ch.card.ward and pred(ch)]

    def best_kill(self, g, p, dmg):
        o = g.opp(p)
        ks = self.targets(g, p, lambda ch: dmg - ch.card.resist >= ch.left())
        if not ks:
            return None, 0
        t = max(ks, key=lambda ch: self.threat(g, o, ch))
        return t, self.threat(g, o, t)

    def best_any(self, g, p, pred=lambda ch: True):
        o = g.opp(p)
        ts = self.targets(g, p, pred)
        if not ts:
            return None, 0
        t = max(ts, key=lambda ch: self.threat(g, o, ch))
        return t, self.threat(g, o, t)

    # ---------- 歌い手選び ----------
    def find_singers(self, g, p, song):
        ready = [ch for ch in p.board if not ch.exerted and not ch.dry]
        if song.sing_together:
            ready.sort(key=lambda ch: g.char_lore(p, ch))
            chosen, tot = [], 0
            for ch in ready:
                chosen.append(ch)
                tot += g.singer_value(p, ch)
                if tot >= song.sing_together:
                    return chosen
            return None
        ok = [ch for ch in ready if g.singer_value(p, ch) >= song.cost]
        if not ok:
            return None
        return [min(ok, key=lambda ch: (g.char_lore(p, ch), ch.card.cost))]

    # ---------- 効果の点数 ----------
    def spell_effect(self, g, p, card):
        """(点数, kwargs) を返す。0以下なら使わない。"""
        o = g.opp(p)
        n = card.name
        if n in ("Scram!",):
            t, v = self.best_any(g, p, lambda ch: ch.card.cost <= 2)
            return (v - 0.5, {"target": t}) if t else (0, {})
        if n == "Let It Go":
            t, v = self.best_any(g, p)
            return (v - 1.0, {"target": t}) if t and v >= 3.5 else (0, {})
        if n == "Keep the Ancient Ways":
            return (self.lock_value + 0.3 if not o.action_locked else 0, {})
        if n == "Let the Storm Rage On":
            t, v = self.best_kill(g, p, 2)
            if t:
                return v + 1.5, {"target": t}
            t, v = self.best_any(g, p)
            return (1.6, {"target": t}) if t else (1.3, {})
        if n == "Hot Potato":
            t, v = self.best_kill(g, p, 2)
            return (v - 0.5, {"target": t}) if t else (0, {})
        if n == "Ink Explosion":
            t, v = self.best_kill(g, p, 4)
            return (v - 0.5, {"target": t}) if t else (0, {})
        if n == "Grab Your Sword":
            tot = sum(self.threat(g, o, ch) for ch in o.board if 2 - ch.card.resist >= ch.left())
            return (tot - 3.0, {})
        if n == "Strength of a Raging Fire":
            t, v = self.best_kill(g, p, len(p.board))
            return (v, {"target": t}) if t else (0, {})
        if n == "And Then Along Came Zeus":
            t, v = self.best_kill(g, p, 5)
            return (v - 0.5, {"target": t}) if t else (0, {})
        if n == "Akood et Emuti":
            after = p.ink_avail() - (0 if self._singing else card.cost)
            chars = [c for c in p.hand if c.kind == "char" and c.cost >= 3 and c.cost - 2 <= after]
            return (2.5 if chars else 1.0, {})
        if n == "Beyond the Horizon":
            if len(p.hand) <= 2 and len(o.hand) >= 3:
                return (3.0, {"players": [p, o]})
            if len(p.hand) <= 1:
                return (2.0, {"players": [p]})
            return (0, {})
        return (0, {})

    def char_effect(self, g, p, card):
        o = g.opp(p)
        n = card.name
        v = card.lore * 1.6 + card.wp * 0.15 + card.str_ * 0.15 + card.cost * 0.35
        kw = {}
        if card.name in ("Pete - Games Referee", "Toulouse - Rough and Tumble") and not o.action_locked:
            v += self.lock_value
        if n == "Bellwether - Highly Qualified":
            t, tv = self.best_any(g, p, lambda ch: ch.card.cost <= 2)
            if t:
                v += tv
                kw["target"] = t
        if n == "Hades - Infernal Schemer":
            t, tv = self.best_any(g, p)
            if t:
                v += tv
                kw["target"] = t
        if n == "Miguel Rivera - Street Musician" and any(c.kind == "song" for c in p.discard):
            v += 1.5
        if n == "Aurora - Delightful Musician":
            if any(c.cost <= 3 for c in p.songs_this_turn):
                v += 2.5
            else:
                v -= 1.5  # 歌を使った後に出したい
        if n == "Powerline - Megastar":
            v += sum(1 for ch in p.board if ch.card.singer) * 1.2
        v += self.special.get(n, 0)
        return v, kw

    # ---------- メイン ----------
    def main(self, g, p):
        o = g.opp(p)
        self._singing = False
        c = self.choose_ink(g, p)
        if c:
            g.ink(p, c)
        if self.lethal(g, p):
            self.quest_all(g, p)
            return
        for _ in range(30):
            if g.winner is not None:
                return
            best = None
            seen = set()
            for card in list(p.hand):
                if card.name in seen:
                    continue
                seen.add(card.name)
                if card.kind == "char":
                    cost = g.card_cost(p, card)
                    if p.ink_avail() >= cost:
                        v, kw = self.char_effect(g, p, card)
                        cand = (v, "char", card, None, kw)
                        if best is None or cand[0] > best[0]:
                            best = cand
                    if card.shift:
                        bases = [ch for ch in p.board if ch.card.base == card.shift_base and ch.card.name != card.name]
                        if bases and p.ink_avail() >= card.shift:
                            v, kw = self.char_effect(g, p, card)
                            base = max(bases, key=lambda ch: ch.dry is False)
                            v += 2.0 + (0 if base.dry else 1.5)
                            cand = (v, "shift", card, base, kw)
                            if best is None or cand[0] > best[0]:
                                best = cand
                else:
                    if p.action_locked:
                        continue
                    singers = self.find_singers(g, p, card) if card.kind == "song" else None
                    if singers:
                        self._singing = True
                        v, kw = self.spell_effect(g, p, card)
                        v += self.song_synergy(g, p) if v > 0 else 0
                        self._singing = False
                        v -= sum(g.char_lore(p, s) for s in singers) * 0.9
                        cand = (v, "sing", card, singers, kw)
                        if best is None or cand[0] > best[0]:
                            best = cand
                    if p.ink_avail() >= card.cost:
                        v, kw = self.spell_effect(g, p, card)
                        if card.kind == "song" and v > 0:
                            v += self.song_synergy(g, p)
                        v -= card.cost * 0.25
                        cand = (v, "pay", card, None, kw)
                        if best is None or cand[0] > best[0]:
                            best = cand
            if best is None or best[0] <= 0.5:
                break
            v, how, card, extra, kw = best
            if how == "char":
                g.play_char(p, card, **kw)
            elif how == "shift":
                g.play_char(p, card, shift_onto=extra, **kw)
            elif how == "sing":
                g.play_spell(p, card, singers=extra, **kw)
            else:
                g.play_spell(p, card, **kw)
            if self.lethal(g, p):
                break
        if g.winner is not None:
            return
        if not self.lethal(g, p):
            self.do_challenges(g, p)
        self.quest_all(g, p)

    def song_synergy(self, g, p):
        """このターン最初の歌を使うことで得られるおまけの価値。"""
        v = 0.0
        first = not any(c.kind == "song" for c in p.songs_this_turn)
        if first and any(ch.name == "Aurora - Delightful Musician" for ch in p.board):
            v += 2.0  # ターン終了時に1ロア
        if not any(c.kind == "song" for c in p.discard) and any(
                ch.name == "Miguel Rivera - Street Musician" for ch in p.board):
            v += 1.5  # ミゲルがロア2・歌声3に
        if not p.powerline_used and any(ch.name == "Powerline - Megastar" for ch in p.board) and any(
                c.kind == "char" and c.singer for c in p.discard):
            v += 1.5
        return v

    def lethal(self, g, p):
        ready = [ch for ch in p.board if not ch.exerted and not ch.dry]
        return p.lore + sum(g.char_lore(p, ch) for ch in ready) >= WIN_LORE

    def do_challenges(self, g, p):
        o = g.opp(p)
        for att in sorted(p.board, key=lambda ch: -ch.str_()):
            if g.winner is not None or att not in p.board:
                continue
            if att.exerted or att.dry:
                continue
            best, bv = None, 0
            quest_v = g.char_lore(p, att) * 1.3
            for t in list(o.board):
                if not g.can_challenge(p, att, t):
                    continue
                kill = att.str_() - t.card.resist >= t.left()
                if not kill:
                    continue
                die = t.str_() - att.card.resist >= att.left()
                sc = self.threat(g, o, t) - (self.threat(g, p, att) if die else 0)
                if sc > bv:
                    best, bv = t, sc
            if best is not None and bv > quest_v:
                g.challenge(p, att, best)

    def quest_all(self, g, p):
        for ch in list(p.board):
            if g.winner is not None:
                return
            if ch in p.board and not ch.exerted and not ch.dry and g.char_lore(p, ch) > 0:
                g.quest(p, ch)


THREAT_BONUS = {
    "Powerline - Megastar": 4, "Aurora - Delightful Musician": 2.5, "Beast - Tragic Hero": 2,
    "Cinderella - Stouthearted": 2, "Miguel Rivera - Street Musician": 1.0, "Ariel - Spectacular Singer": 0.5,
    "Priscilla - Efficient Clerk": 2.5, "Minnie Mouse - Urban Visionary": 2, "Bellwether - Highly Qualified": 0,
    "Pete - Games Referee": 0.5, "Toulouse - Rough and Tumble": 0.3, "Chief Bogo - Police Commissioner": 1,
    "Cinderella - Ballroom Sensation": 0.8,  # 剛胆シンデレラの変身元
}


class BlueLock(Policy):
    lock_value = 4.0
    ink_cap = 9
    ink_pref = {
        "Wildcat - Unconventional Mechanic": 6, "Clarabelle - Out for a Stroll": 5, "Go Go Tomago - Working Late": 4,
        "Hot Potato": 3.5, "Carl Fredricksen - Wilderness Guide": 3, "Chief Bogo - Police Commissioner": 3,
        "Fergus - King of DunBroch": 3, "Minnie Mouse - Urban Visionary": 2.5, "Doug - Lying in Wait": 2,
        "Scram!": 2, "Pete - Games Referee": 0.5, "Toulouse - Rough and Tumble": 0.5,
        "Priscilla - Efficient Clerk": 0, "Keep the Ancient Ways": 0, "Let It Go": 0,
    }
    mull_back = {
        "Carl Fredricksen - Wilderness Guide", "Clarabelle - Out for a Stroll", "Hades - Infernal Schemer",
        "Chief Bogo - Police Commissioner", "Minnie Mouse - Urban Visionary", "Grab Your Sword",
        "Ink Explosion", "Wildcat - Unconventional Mechanic",
    }
    special = {"Priscilla - Efficient Clerk": 2.0}


class AmberSteelSong(Policy):
    lock_value = 2.5
    ink_cap = 7
    ink_pref = {
        "Powerline - Megastar": 2.5, "Beast - Tragic Hero": 3, "Cinderella - Stouthearted": 3,
        "Angel - Siren Singer": 3, "Pete - Games Referee": 2, "Strength of a Raging Fire": 2.5,
        "Ursula - Vanessa": 2, "The Troubadour - Musical Narrator": 2, "Meilin Lee - Losing Control": 2,
        "Cinderella - Ballroom Sensation": 1.5, "Ariel - Spectacular Singer": 1, "Aurora - Delightful Musician": 1,
        "Miguel Rivera - Street Musician": 1,
    }
    mull_back = {"Powerline - Megastar", "Cinderella - Stouthearted", "Beyond the Horizon", "Beast - Tragic Hero"}
    special = {"Ariel - Spectacular Singer": 1.0, "Meilin Lee - Losing Control": 0.8}


POLICIES = {"blue_lock": BlueLock, "amber_steel_song": AmberSteelSong}
