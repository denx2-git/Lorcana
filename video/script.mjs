// 解説動画「ロイヤルドッグの回し方」の台本。
// steps の1要素が動画の1カット。caption が字幕（ナレーション原稿）になる。
// 盤面は play / quest などの操作で組み立て、カットごとにスナップショットを取る。

export const CARDS = {
  lady:   { name: "レディ", sub: "凛々しいお嬢さん", cost: 1, s: 0, w: 3, l: 1, inks: ["amber", "emerald"], ink: true },
  willow: { name: "柳の木のおばあさん", sub: "古き善き相談相手", cost: 2, s: 1, w: 2, l: 1, inks: ["amber"], ink: false },
  tramp1: { name: "トランプ", sub: "切れ者の犬", cost: 2, s: 1, w: 3, l: 1, inks: ["emerald"], ink: true },
  elinor: { name: "エリノア", sub: "名高い外交家", cost: 4, s: 3, w: 4, l: 1, inks: ["emerald"], ink: false },
  tramp2: { name: "トランプ", sub: "裏路地暮らしの犬", cost: 7, s: 2, w: 6, l: 2, inks: ["amber", "emerald"], ink: true },
  bobby:  { name: "ボビー", sub: "スプレーチーズ小僧", cost: 1, s: 1, w: 2, l: 1, inks: ["emerald"], ink: true },
  aurora: { name: "オーロラ", sub: "姫のお披露目", cost: 1, s: 1, w: 2, l: 1, inks: ["amber"], ink: true },
  lilo:   { name: "リロ", sub: "抜け出し名人", cost: 2, s: 1, w: 2, l: 2, inks: ["amber"], ink: true },
  kida:   { name: "キーダ", sub: "アトランティスの守護者", cost: 5, s: 3, w: 5, l: 2, inks: ["amber"], ink: true },
  uts:    { name: "アンダー・ザ・シー", sub: "歌（合唱8）", cost: 8, inks: ["emerald"], ink: false, song: true },
  mike:   { name: "マイク・ワゾウスキ", sub: "トップを目指すヒーロー", cost: 2, s: 0, w: 4, l: 1, inks: ["amber"], ink: false },
  ursula: { name: "アースラ", sub: "騙し屋", cost: 2, s: 1, w: 3, l: 1, inks: ["emerald"], ink: true },
  kit:    { name: "キット", sub: "タフガイ", cost: 3, s: 2, w: 2, l: 1, inks: ["emerald"], ink: true },
};

// カード紹介で使う効果の要約（公式日本語テキストを短くしたもの）
export const EFFECT = {
  lady: "キャラを出すたび、このターン S+1。S3以上の間ロア+2（合計3ロア）",
  willow: "自分のターンに1回、次に出すキャラのコストが1減る",
  tramp1: "レディがいればコスト-1。登場時、自分のキャラ1体を「他のキャラの数」だけ S+",
  elinor: "ターン終了時、横向きの自分のキャラが3体以上なら、相手キャラに1ダメージ・1ロア・1ドロー",
  tramp2: "場の自分のキャラの数だけコストが減る。登場時、他のキャラの数だけ引いて同じ数を捨てられる",
  lilo: "自分のターン開始時、捨て札にあれば横向きで場に出せる",
  kida: "登場時、全てのキャラ（自分のキャラも）が次の自分のターン開始まで S-3",
  uts: "場のキャラのコスト合計8で無料で歌える。相手のS2以下のキャラを全てデッキの下へ",
};

function makeState() {
  return { turn: 0, ink: 0, used: 0, lore: 0, board: [], discard: [], drop: null };
}

function snapshot(st) {
  return JSON.parse(JSON.stringify(st));
}

export function buildSteps() {
  const steps = [];
  const st = makeState();
  const find = (k) => st.board.find((c) => c.key === k);
  const add = (extra) => steps.push({ layout: "turn", state: snapshot(st), ...extra });
  const clearMarks = () => st.board.forEach((c) => { c.hl = false; c.tag = null; });

  const play = (key, opts = {}) => {
    // レディは「キャラを出すたび S+1」
    const lady = find("lady");
    if (lady && key !== "lady") lady.bonus += 1;
    st.board.push({ key, bonus: 0, exerted: !!opts.exerted, fresh: true, hl: true, tag: opts.tag || "登場" });
    st.used += opts.pay ?? CARDS[key].cost;
  };
  const quest = (keys) => {
    for (const k of keys) {
      const c = find(k);
      c.exerted = true;
      c.hl = true;
      const lore = loreOf(c);
      c.tag = `+${lore}ロア`;
      st.lore += lore;
    }
  };
  const newTurn = (n, inkCard) => {
    st.turn = n;
    st.used = 0;
    st.ink += 1;
    st.drop = inkCard;
    st.board.forEach((c) => { c.exerted = false; c.fresh = false; c.bonus = 0; c.hl = false; c.tag = null; });
  };

  // ---------------- オープニング
  steps.push({ layout: "title", caption: "ロルカナ初心者向け。第13弾環境で一番使われている「ロイヤルドッグ」の回し方を、1ターンずつ解説します。" });
  steps.push({
    layout: "bullets", heading: "どんなデッキ？", sub: "アンバー × エメラルド（ロイヤルドッグ）",
    bullets: ["小さいキャラを毎ターン並べる", "相手より先に 20ロア を集めて勝つ", "主役はレディ・トランプ・エリノア"],
    caption: "このデッキは、コストの小さいキャラを毎ターン並べて、相手より先に20ロアを集める速攻デッキです。",
  });
  steps.push({
    layout: "bullets", heading: "最初に覚える3つのルール", sub: "ここだけ押さえればOK",
    bullets: ["インクは 1ターンに1枚 だけ置ける", "出したターンのキャラは クエストできない", "クエスト＝キャラを横にして ロアを得る"],
    caption: "まずルールのおさらい。インクは1ターンに1枚だけ。出したばかりのキャラはインクが乾いていないので、そのターンはクエストできません。",
  });
  steps.push({
    layout: "bullets", heading: "最初に覚える3つのルール", sub: "ここだけ押さえればOK",
    bullets: ["インクは 1ターンに1枚 だけ置ける", "出したターンのキャラは クエストできない", "クエスト＝キャラを横にして ロアを得る"],
    emph: 2,
    caption: "クエストはキャラを横向きにしてロアを得ること。キャラの下にある◆の数だけロアがもらえます。",
  });

  // ---------------- 主役カード
  steps.push({ layout: "cards", heading: "主役カード ①", cards: ["lady", "willow", "tramp1"],
    caption: "主役のカードを紹介します。レディは、キャラを出すたびに強くなり、Sが3以上になると1回のクエストで3ロア取れます。" });
  steps.push({ layout: "cards", heading: "主役カード ①", cards: ["lady", "willow", "tramp1"], focus: 1,
    caption: "柳の木のおばあさんは、次に出すキャラを1コスト安くしてくれます。トランプ – 切れ者の犬は、レディを一気に強くできます。" });
  steps.push({ layout: "cards", heading: "主役カード ②", cards: ["elinor", "tramp2", "lilo"],
    caption: "エリノアは、ターン終了時に横向きのキャラが3体いれば、毎ターン1ダメージ・1ロア・1ドロー。" });
  steps.push({ layout: "cards", heading: "主役カード ②", cards: ["elinor", "tramp2", "lilo"], focus: 1,
    caption: "トランプ – 裏路地暮らしの犬は、場のキャラが多いほど安くなります。リロは捨て札から自分で戻ってきます。" });

  // ---------------- マリガン
  steps.push({
    layout: "hand", heading: "最初の手札（マリガン）",
    hand: [["lady", "keep"], ["willow", "keep"], ["tramp1", "keep"], ["elinor", "keep"], ["bobby", "keep"], ["kida", "keep"], ["uts", "back"]],
    caption: "最初の7枚が配られたら、序盤に使わないカードはデッキに戻して引き直せます。これをマリガンと言います。",
  });
  steps.push({
    layout: "hand", heading: "最初の手札（マリガン）",
    hand: [["lady", "keep"], ["willow", "keep"], ["tramp1", "keep"], ["elinor", "keep"], ["bobby", "keep"], ["kida", "keep"], ["uts", "back"]],
    marks: true,
    caption: "1〜2コストのキャラとエリノアは残します。コスト8のアンダー・ザ・シーは序盤に使えずインクにも置けないので戻します。",
  });
  steps.push({
    layout: "bullets", heading: "インクに置くカードの選び方", sub: "コストのまわりに枠（動画では金色）があるカードだけ置けます",
    bullets: ["置けない：柳の木・エリノア・マイク・アンダー・ザ・シー", "置いてOK：すぐ使わないキーダ・アースラ・キット", "1〜2コストのキャラはなるべく残す"],
    caption: "インクに置くカードも大事です。柳の木やエリノアは置けません。すぐ使わないキーダやアースラをインクにして、軽いキャラは手札に残しましょう。",
  });

  // ---------------- 1ターン目
  newTurn(1, "kida");
  add({ chapter: "1ターン目", caption: "1ターン目（先攻）。まずインクを1枚置きます。今回はすぐには使わないキーダをインクにします。" });
  st.drop = null;
  play("lady");
  add({ chapter: "1ターン目", caption: "1インクで、レディ – 凛々しいお嬢さんを出します。後からキャラを並べるほど強くなるので、1ターン目に出したいカードです。",
    point: "1ターン目はレディが最優先" });
  clearMarks();
  add({ chapter: "1ターン目", caption: "出したばかりのレディはクエストできません。これで1ターン目は終わりです。" });

  // ---------------- 2ターン目
  newTurn(2, "ursula");
  add({ chapter: "2ターン目", caption: "2ターン目。カードを1枚引き、アースラをインクに置いて2インク。レディはクエストできますが、まだしません。",
    point: "クエストは最後にする" });
  st.drop = null;
  play("willow");
  add({ chapter: "2ターン目", caption: "柳の木のおばあさんを2インクで出します。レディはキャラが出たので S+1。" });
  clearMarks();
  play("tramp1", { pay: 0 });
  add({ chapter: "2ターン目", caption: "次にトランプ – 切れ者の犬。レディがいるので1安く、柳の木でさらに1安く、0インクで出せます！",
    calc: "コスト2 − レディ1 − 柳の木1 ＝ 0" });
  clearMarks();
  find("lady").bonus += 2;
  find("lady").hl = true;
  find("lady").tag = "S+2";
  add({ chapter: "2ターン目", caption: "トランプの能力でレディを選びます。他のキャラが2体いるので S+2。レディのSは4になりました。" });
  clearMarks();
  quest(["lady"]);
  add({ chapter: "2ターン目", caption: "Sが3以上のレディはロアが3。ここで初めてクエスト！一気に3ロア獲得です。",
    point: "キャラを出してからクエスト" });

  // ---------------- 3ターン目
  newTurn(3, "kit");
  add({ chapter: "3ターン目", caption: "3ターン目。ターンの始めにキャラは縦向きに戻ります。キットをインクに置いて3インク。" });
  st.drop = null;
  play("elinor", { pay: 3 });
  add({ chapter: "3ターン目", caption: "柳の木の割引を使って、コスト4のエリノアを3インクで出します。",
    calc: "コスト4 − 柳の木1 ＝ 3" });
  clearMarks();
  quest(["lady", "willow", "tramp1"]);
  add({ chapter: "3ターン目", caption: "レディ、柳の木、トランプの3体でクエスト。レディのSは1なので、それぞれ1ロアずつで3ロア。" });
  clearMarks();
  st.lore += 1;
  find("elinor").hl = true;
  find("elinor").tag = "+1ロア";
  add({ chapter: "3ターン目", caption: "ターン終了時、横向きのキャラが3体いるのでエリノアの能力が発動。相手キャラに1ダメージ、1ロア、1ドロー。",
    point: "エリノアを出したら3体でクエスト" });

  // ---------------- 4ターン目
  newTurn(4, "kida");
  add({ chapter: "4ターン目", caption: "4ターン目。2枚目のキーダをインクに置いて4インク。場のキャラは4体です。" });
  st.drop = null;
  play("tramp2", { pay: 2 });
  add({ chapter: "4ターン目", caption: "トランプ – 裏路地暮らしの犬はコスト7。でも場のキャラ4体で4安く、柳の木でさらに1安く、2インクで出せます。",
    calc: "コスト7 − キャラ4体 − 柳の木1 ＝ 2" });
  clearMarks();
  st.discard.push("lilo");
  find("tramp2").hl = true;
  find("tramp2").tag = "4枚引いて4枚捨てる";
  add({ chapter: "4ターン目", caption: "登場時、4枚引いて4枚捨てられます。引いたリロはあえて捨てます。リロは次のターン、捨て札から戻ってくるからです。",
    point: "リロは捨ててもOK" });
  clearMarks();
  play("bobby");
  play("aurora");
  add({ chapter: "4ターン目", caption: "残りの2インクでボビーとオーロラを出します。このターン3体出したので、レディのSは3になりました。" });
  clearMarks();
  quest(["lady", "willow", "tramp1", "elinor"]);
  add({ chapter: "4ターン目", caption: "レディ、柳の木、トランプ、エリノアでクエスト。レディは3ロアなので、合計6ロアです。" });
  clearMarks();
  st.lore += 1;
  find("elinor").hl = true;
  find("elinor").tag = "+1ロア";
  add({ chapter: "4ターン目", caption: "ターン終了時、エリノアでさらに1ロア。これで14ロアです。" });

  // ---------------- 5ターン目
  newTurn(5, null);
  st.discard = [];
  play("lilo", { exerted: true, pay: 0, tag: "捨て札から" });
  add({ chapter: "5ターン目", caption: "5ターン目の始め。捨て札のリロが、横向きで場に戻ってきます。インクを払わずにキャラが1体増えました。" });
  clearMarks();
  quest(["lady", "willow", "tramp1", "elinor", "tramp2", "bobby", "aurora"]);
  add({ chapter: "5ターン目", caption: "全員でクエストすると、1+1+1+1+2+1+1で8ロア。合計22ロアで、20を超えたので勝利です！",
    point: "相手の妨害がない場合の最速の流れ" });

  // ---------------- 実戦での注意
  steps.push({
    layout: "cards", heading: "届かないときの切り札", cards: ["kida", "uts"],
    caption: "実際は相手も除去やチャレンジで邪魔してきます。届かないときは、キーダで全キャラのSを3下げて、相手のチャレンジを止めます。",
  });
  steps.push({
    layout: "cards", heading: "届かないときの切り札", cards: ["kida", "uts"], focus: 1,
    caption: "アンダー・ザ・シーは、場のキャラのコスト合計8で無料で歌えます。相手のS2以下のキャラをまとめてデッキの下に送れます。",
  });
  steps.push({
    layout: "bullets", heading: "キーダを出す順番に注意", sub: "キーダは自分のキャラのSも下げます",
    bullets: ["先にレディでクエスト（3ロア）", "そのあとキーダを出す", "逆にするとレディが1ロアになる"],
    caption: "キーダは自分のキャラのSも3下げます。レディで3ロア取りたいときは、先にクエストしてからキーダを出しましょう。",
  });

  // ---------------- まとめ
  steps.push({
    layout: "summary", heading: "まとめ",
    bullets: ["1ターン目はレディ", "キャラを出してから、最後にクエスト", "3ターン目はエリノア＋3体でクエスト", "裏路地トランプはキャラが多いほど安い"],
    caption: "まとめです。1ターン目はレディ。キャラを出してから最後にクエスト。3ターン目はエリノアと3体クエスト。裏路地トランプはキャラを並べてから。",
  });
  steps.push({
    layout: "end",
    caption: "除去されたキャラは、マイクやナニ、リロで補充しながら20ロアを目指しましょう。ご視聴ありがとうございました。",
  });
  return steps;
}

export function loreOf(c) {
  const base = CARDS[c.key];
  if (c.key === "lady" && base.s + c.bonus >= 3) return base.l + 2;
  return base.l;
}
