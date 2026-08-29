/**
 * storyboard — 故事板管线（v0.3.1）
 *
 * 职责：故事板切片（Markdown）→ Ink 源码 → inkjs 编译 → 单文件 HTML demo
 *
 * 范围（MVP）：纯线性 + 简单选项跳转（变量/状态后续看情况）。
 * 不做：变量/分支（rule-design 领地）；真实资产复制（仅引用图片路径）。
 */

import { spawnSync } from "node:child_process";
import { mkdtempSync, writeFileSync, readFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const compilerBin = join(here, "..", "node_modules", "inkjs", "bin", "inkjs-compiler.js");
const inkRuntimePath = join(here, "..", "node_modules", "inkjs", "dist", "ink.mjs");

// ── 1. 解析切片 ─────────────────────────────────────────────────────────
export function parseStoryboard(mdText) {
  const lines = mdText.split(/\r?\n/);
  const meta = { title: "", synopsis: "", start_scene: "" };
  const scenes = [];
  let rules = null;

  let i = 0;
  while (i < lines.length) {
    const line = lines[i];

    if (/^##\s+元信息/.test(line)) {
      i++;
      while (i < lines.length && !lines[i].startsWith("## ")) {
        const m = lines[i].match(/^\|\s*(标题|简介|起始场景)\s*\|\s*(.*?)\s*\|\s*$/);
        if (m) {
          const key = m[1] === "标题" ? "title" : m[1] === "简介" ? "synopsis" : "start_scene";
          const v = stripPlaceholder(m[2]);
          if (v) meta[key] = v;
        }
        i++;
      }
      continue;
    }

    const sceneMatch = line.match(/^##\s+场景\s*·\s*(.+?)\s*$/);
    if (sceneMatch) {
      const scene = { id: sceneMatch[1].trim(), title: "", image: "", body: "", choices: [] };
      i++;
      while (i < lines.length && !lines[i].startsWith("## ")) {
        const l = lines[i];
        const titleM = l.match(/^-\s*标题[：:]\s*(.+?)\s*$/);
        const imageM = l.match(/^-\s*背景图[：:]\s*(.+?)\s*$/);
        if (titleM) scene.title = stripPlaceholder(titleM[1]);
        else if (imageM) scene.image = stripPlaceholder(imageM[1]);
        else if (/^-\s*文案[：:]/.test(l)) {
          const bodyLines = [];
          i++;
          while (i < lines.length && !/^-\s*选项[：:]/.test(lines[i]) && !lines[i].startsWith("## ")) {
            bodyLines.push(lines[i]);
            i++;
          }
          scene.body = extractCodeOrText(bodyLines);
          continue;
        } else if (/^-\s*选项[：:]/.test(l)) {
          i++;
          while (i < lines.length && !lines[i].startsWith("## ") && !/^-\s/.test(lines[i])) {
            const c = lines[i].match(/^(.+?)\s*->\s*(.+?)\s*$/);
            if (c) {
              const txt = stripPlaceholder(c[1]);
              const tgt = stripPlaceholder(c[2]);
              if (txt && tgt) scene.choices.push({ text: txt, target: tgt });
            }
            i++;
          }
          continue;
        }
        i++;
      }
      scenes.push(scene);
      continue;
    }

    if (/^##\s+规则摘要/.test(line)) {
      i++;
      const r = { victory: "", loop: "" };
      while (i < lines.length && !lines[i].startsWith("## ")) {
        const vM = lines[i].match(/^-\s*胜负判定[：:]\s*(.+?)\s*$/);
        const lM = lines[i].match(/^-\s*核心循环[：:]\s*(.+?)\s*$/);
        if (vM) r.victory = stripPlaceholder(vM[1]);
        else if (lM) r.loop = stripPlaceholder(lM[1]);
        i++;
      }
      rules = r;
      continue;
    }

    i++;
  }

  if (!meta.start_scene && scenes.length > 0) meta.start_scene = scenes[0].id;
  return { meta, scenes, rules };
}

function stripPlaceholder(s) {
  if (!s) return "";
  const t = s.trim();
  if (!t) return "";
  if (/^<.*>$/.test(t)) return "";
  return t;
}

function extractCodeOrText(lines) {
  const text = lines.join("\n").replace(/^\s*\n/, "").trim();
  const fenceM = text.match(/^```[^\n]*\n([\s\S]*?)\n?```\s*$/);
  if (fenceM) return fenceM[1].trim();
  return text;
}

// ── 2. 转 Ink 源码 ─────────────────────────────────────────────────────
export function toInk(sb) {
  const startId = sb.meta.start_scene || (sb.scenes.length > 0 ? sb.scenes[0].id : "");
  const parts = ["// Auto-generated from storyboard slice (v0.3.1)", ""];
  // 顶层 divert 到起始场景（Ink 默认从 root 开始，必须显式进入 knot）
  if (startId) {
    parts.push(`-> ${startId}`);
    parts.push("");
  }
  for (const scene of sb.scenes) {
    parts.push(`=== ${scene.id} ===`);
    parts.push("");
    if (scene.image) {
      parts.push(`<div class='storyboard-img'><img src='${esc(scene.image)}' alt='${esc(scene.title || scene.id)}'></div>`);
      parts.push("");
    }
    if (scene.title) {
      parts.push(`# title: ${scene.title}`);
    }
    if (scene.body) {
      parts.push(scene.body);
      parts.push("");
    }
    if (scene.choices.length === 0) {
      parts.push("-> END");
    } else {
      for (const c of scene.choices) parts.push(`* [${c.text}] -> ${c.target}`);
    }
    parts.push("");
  }
  return parts.join("\n");
}

function esc(s) {
  return String(s)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

// ── 3. 编译 Ink → BOM-free JSON（CLI 子进程路径） ─────────────────────
export function compileInk(inkSource) {
  const tmpDir = mkdtempSync(join(tmpdir(), "gdwa-"));
  const inkPath = join(tmpDir, "story.ink");
  const jsonPath = join(tmpDir, "story.json");
  try {
    writeFileSync(inkPath, inkSource, "utf8");
    const r = spawnSync(process.execPath, [compilerBin, "-o", jsonPath, inkPath], { encoding: "utf8" });
    if (r.status !== 0) {
      const msg = (r.stderr || r.stdout || "(no output)").trim();
      // 友好提示：常见 Ink 语法冲突
      if (/\$\{/.test(inkSource)) {
        throw new Error(`inkjs compile failed: ${msg}\n提示：正文/选项含 \`\${\` 会与 Ink 插值语法冲突，请改写（如把 \`\$\{value\}\` 换成文字描述）`);
      }
      throw new Error(`inkjs compile failed: ${msg}`);
    }
    return readFileSync(jsonPath, "utf8").replace(/^\uFEFF/, "");
  } finally {
    rmSync(tmpDir, { recursive: true, force: true });
  }
}

// ── 4. 渲染单文件 HTML（JSON.stringify 嵌入 runtime + JSON） ────────────
export function renderHtml(sb, inkJson) {
  const inkRuntime = readFileSync(inkRuntimePath, "utf8");
  const title = sb.meta.title || "Storyboard Demo";
  // 用 JSON.stringify 把源码/JSON 转成 JS 字符串字面量：
  // 反引号 / ${ / 反斜杠 / 引号 全部正确转义，避免模板字符串陷阱
  const runtimeLiteral = JSON.stringify(inkRuntime);
  const jsonLiteral = JSON.stringify(inkJson);
  return `<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<title>${esc(title)}</title>
<style>
  body { font-family: -apple-system, "PingFang SC", "Microsoft YaHei", sans-serif; max-width: 720px; margin: 2rem auto; padding: 0 1rem; line-height: 1.7; color: #222; background: #fafafa; }
  #app { background: #fff; padding: 2rem; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,.08); }
  h1 { margin-top: 0; font-size: 1.4rem; }
  .storyboard-img img { max-width: 100%; height: auto; border-radius: 4px; display: block; margin: 0 auto 1rem; }
  #text { white-space: pre-wrap; margin-bottom: 1.5rem; min-height: 3em; }
  #choices { display: flex; flex-direction: column; gap: .5rem; }
  #choices button { padding: .75rem 1rem; border: 1px solid #ddd; border-radius: 4px; background: #f5f5f5; cursor: pointer; font: inherit; text-align: left; }
  #choices button:hover { background: #e8e8e8; }
  #choices button:focus { outline: 2px solid #66f; outline-offset: 2px; }
  #meta { color: #888; font-size: .85rem; margin-bottom: 1rem; }
</style>
</head>
<body>
<div id="app">
  <h1>${esc(title)}</h1>
  <div id="meta">${esc(sb.meta.synopsis || "")}</div>
  <div id="text"></div>
  <div id="choices"></div>
</div>
<script type="module">
const INK_RUNTIME = ${runtimeLiteral};
const STORY_JSON = ${jsonLiteral};
const blob = new Blob([INK_RUNTIME], { type: "text/javascript" });
const url = URL.createObjectURL(blob);
const { Story } = await import(url);
const story = new Story(STORY_JSON);
const textEl = document.getElementById("text");
const choicesEl = document.getElementById("choices");
function render() {
  textEl.innerHTML = "";
  choicesEl.innerHTML = "";
  while (story.canContinue) {
    textEl.insertAdjacentHTML("beforeend", story.Continue());
  }
  for (const c of story.currentChoices) {
    const btn = document.createElement("button");
    btn.textContent = c.text;
    btn.onclick = () => { story.ChooseChoiceIndex(c.index); render(); };
    choicesEl.appendChild(btn);
  }
}
render();
</script>
</body>
</html>`;
}