// 解説動画を生成する: node video/build.mjs
// 1. script.mjs の各カットを template.html で描画してPNGに保存
// 2. ffmpeg でクロスフェードしながらつないで MP4 にする
// 3. 字幕ファイル（SRT）とナレーション原稿（タイムスタンプ付き）を書き出す
import { execFileSync } from "node:child_process";
import { existsSync, mkdirSync, rmSync, writeFileSync } from "node:fs";
import { createRequire } from "node:module";
import { dirname, join } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import { buildSteps, CARDS, EFFECT } from "./script.mjs";

const here = dirname(fileURLToPath(import.meta.url));
const require = createRequire(import.meta.url);
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || "playwright");

const NAME = "royal-dog-guide";
const OUT = join(here, "out");
const FRAMES = join(OUT, "frames");
const FONTS = join(here, "fonts");
const FADE = 0.35;

// 字幕を読み切れる長さ（日本語ナレーション 約6.5文字/秒）
const duration = (text) => Math.max(4.5, Math.round(((text || "").length / 6.5 + 1.5) * 10) / 10);

function ensureFonts() {
  mkdirSync(FONTS, { recursive: true });
  for (const w of [500, 800, 900]) {
    const file = join(FONTS, `mplus-${w}.ttf`);
    if (existsSync(file)) continue;
    const css = execFileSync("curl", ["-sS", `https://fonts.googleapis.com/css2?family=M+PLUS+Rounded+1c:wght@${w}`]).toString();
    const url = css.match(/https:\/\/[^)]+\.ttf/)[0];
    execFileSync("curl", ["-sS", "-o", file, url]);
  }
}

async function renderFrames(steps) {
  rmSync(FRAMES, { recursive: true, force: true });
  mkdirSync(FRAMES, { recursive: true });
  const browser = await chromium.launch(
    existsSync("/opt/pw-browsers/chromium") ? { executablePath: "/opt/pw-browsers/chromium" } : {},
  ).catch(() => chromium.launch());
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
  await page.goto(pathToFileURL(join(here, "template.html")).href);
  await page.evaluate(([c, e]) => window.setup(c, e), [CARDS, EFFECT]);
  const files = [];
  for (const [i, step] of steps.entries()) {
    await page.evaluate((s) => window.render(s), step);
    await page.evaluate(() => document.fonts.ready);
    const file = join(FRAMES, `${String(i).padStart(3, "0")}.png`);
    await page.screenshot({ path: file });
    files.push(file);
  }
  await browser.close();
  return files;
}

function encode(files, durs) {
  const args = ["-y", "-hide_banner", "-loglevel", "error"];
  files.forEach((f, i) => args.push("-loop", "1", "-framerate", "30", "-t", String(durs[i]), "-i", f));
  const parts = [];
  let prev = "0:v";
  let offset = 0;
  for (let i = 1; i < files.length; i++) {
    offset += durs[i - 1] - FADE;
    const out = i === files.length - 1 ? "vout" : `v${i}`;
    parts.push(`[${prev}][${i}:v]xfade=transition=fade:duration=${FADE}:offset=${offset.toFixed(2)}[${out}]`);
    prev = out;
  }
  args.push("-filter_complex", parts.join(";"), "-map", "[vout]",
    "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", "-r", "30", "-movflags", "+faststart",
    join(OUT, `${NAME}.mp4`));
  execFileSync("ffmpeg", args, { stdio: "inherit" });
}

const ts = (sec, sep) => {
  const ms = Math.round(sec * 1000);
  const h = Math.floor(ms / 3600000), m = Math.floor(ms / 60000) % 60, s = Math.floor(ms / 1000) % 60;
  const p = (n, w = 2) => String(n).padStart(w, "0");
  return sep ? `${p(h)}:${p(m)}:${p(s)}${sep}${p(ms % 1000, 3)}` : `${p(m)}:${p(s)}`;
};

function writeText(steps, durs) {
  let t = 0;
  const srt = [];
  const md = ["# ロイヤルドッグの回し方 — ナレーション原稿", "",
    "`node video/build.mjs` が書き出す。動画の各カットの開始時刻と、読み上げる文章。", "",
    "| 開始 | 場面 | ナレーション |", "|---|---|---|"];
  steps.forEach((s, i) => {
    const start = t;
    const end = t + durs[i] - (i < steps.length - 1 ? FADE : 0);
    srt.push(String(i + 1), `${ts(start, ",")} --> ${ts(end, ",")}`, s.caption, "");
    md.push(`| ${ts(start)} | ${s.chapter || s.heading || "タイトル"} | ${s.caption} |`);
    t = end;
  });
  writeFileSync(join(here, `${NAME}.srt`), srt.join("\n"));
  writeFileSync(join(here, "narration.md"), md.join("\n") + "\n");
  return t;
}

const steps = buildSteps();
const durs = steps.map((s) => duration(s.caption));
ensureFonts();
mkdirSync(OUT, { recursive: true });
const files = await renderFrames(steps);
if (!process.argv.includes("--frames-only")) encode(files, durs);
const total = writeText(steps, durs);
console.log(`${steps.length} カット / ${Math.floor(total / 60)}分${Math.round(total % 60)}秒 → video/out/${NAME}.mp4`);
