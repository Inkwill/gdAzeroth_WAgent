/**
 * gd-wa storyboard 单测（v0.3.1）
 * 用 Node 原生 test runner（Node 20+）：`node --test archive/tests/*.test.mjs`
 * 固定产物路径的用例自带清理，可重复运行无残留
 */

import { test } from "node:test";
import assert from "node:assert/strict";
import { existsSync, rmSync, readFileSync, writeFileSync, mkdirSync, statSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { tmpdir } from "node:os";

const here = dirname(fileURLToPath(import.meta.url));
const root = join(here, "..", "..");
const skeletonPath = join(root, "templates", "storyboard-skeleton.yaml");
const cliPath = join(root, "tools", "gd-wa.mjs");

import { parseStoryboard, toInk, compileInk, renderHtml } from "../../tools/storyboard.mjs";

// ── 工具：构造一个最小但完整的切片样本 ─────────────────────────────────
function mkSampleSlice() {
  return `# 故事板 · sample

> 测试用切片

## 元信息（META）

| 字段 | 值 |
|------|-----|
| 标题 | 森林序章 |
| 简介 | 一个 30 秒可玩完的演示 |
| 起始场景 | start |

## 场景 · start

- 标题：开场
- 背景图：assets/ref-01.png
- 文案：

\`\`\`
你醒来，发现自己在森林深处。
\`\`\`

- 选项：

\`\`\`
向北走 -> north
向南走 -> south
\`\`\`

## 场景 · north

- 标题：北路
- 文案：

\`\`\`
你看到一只狐狸。
\`\`\`

- 选项：

\`\`\`
继续 -> end
\`\`\`

## 场景 · south

- 标题：南路
- 文案：

\`\`\`
你找到出路。
\`\`\`

## 场景 · end

- 标题：终点
- 文案：

\`\`\`
通关。
\`\`\`

## 规则摘要（RULES）

- 胜负判定：抵达 end 即通关
- 核心循环：阅读 → 选择 → 跳转
`;
}

// ── 骨架 ─────────────────────────────────────────────────────────────
test("storyboard-skeleton.yaml 存在且可解析", () => {
  assert.ok(existsSync(skeletonPath), `骨架文件缺失：${skeletonPath}`);
  const text = readFileSync(skeletonPath, "utf8");
  assert.match(text, /^slice_type:\s*storyboard/m);
  assert.match(text, /^version:\s*1/m);
});

test("骨架结构：3 块（meta / scene / rules）", () => {
  const skeleton = readFileSync(skeletonPath, "utf8");
  assert.match(skeleton, /id:\s*meta/);
  assert.match(skeleton, /id:\s*scene/);
  assert.match(skeleton, /id:\s*rules/);
});

// ── parseStoryboard ───────────────────────────────────────────────────
test("parseStoryboard 解析元信息表格", () => {
  const sb = parseStoryboard(mkSampleSlice());
  assert.equal(sb.meta.title, "森林序章");
  assert.equal(sb.meta.synopsis, "一个 30 秒可玩完的演示");
  assert.equal(sb.meta.start_scene, "start");
});

test("parseStoryboard 提取 4 个场景（含 id/title/image/body/choices）", () => {
  const sb = parseStoryboard(mkSampleSlice());
  assert.equal(sb.scenes.length, 4);
  const start = sb.scenes.find((s) => s.id === "start");
  assert.ok(start, "start 场景缺失");
  assert.equal(start.title, "开场");
  assert.equal(start.image, "assets/ref-01.png");
  assert.match(start.body, /你醒来/);
  assert.equal(start.choices.length, 2);
  assert.deepEqual(start.choices[0], { text: "向北走", target: "north" });
});

test("parseStoryboard 终止场景（无选项）→ choices=[]", () => {
  const sb = parseStoryboard(mkSampleSlice());
  const end = sb.scenes.find((s) => s.id === "end");
  assert.equal(end.choices.length, 0);
});

test("parseStoryboard 占位符 <...> 视为空（不污染数据）", () => {
  const md = `## 元信息（META）

| 字段 | 值 |
| 标题 | <填写> |
| 简介 | <一句话> |
| 起始场景 | start |

## 场景 · start

- 标题：<场景显示标题>
- 背景图：<可选>
- 文案：

\`\`\`
身体
\`\`\`

- 选项：

\`\`\`
走 -> end
\`\`\`

## 场景 · end

- 文案：

\`\`\`
完。
\`\`\`
`;
  const sb = parseStoryboard(md);
  assert.equal(sb.meta.title, "");
  assert.equal(sb.meta.synopsis, "");
  const start = sb.scenes[0];
  assert.equal(start.title, "");
  assert.equal(start.image, "");
  assert.equal(start.body.trim(), "身体");
});

test("parseStoryboard 规则摘要（可选）", () => {
  const sb = parseStoryboard(mkSampleSlice());
  assert.ok(sb.rules);
  assert.match(sb.rules.victory, /抵达 end/);
  assert.match(sb.rules.loop, /阅读.*选择.*跳转/);
});

// ── toInk ────────────────────────────────────────────────────────────
test("toInk 生成 Ink 源码（knot + choice + divert）", () => {
  const sb = parseStoryboard(mkSampleSlice());
  const ink = toInk(sb);
  assert.match(ink, /=== start ===/);
  assert.match(ink, /=== end ===/);
  assert.match(ink, /\* \[向北走\] -> north/);
  assert.match(ink, /\* \[向南走\] -> south/);
});

test("toInk 嵌入图片用直接 HTML 标签", () => {
  const sb = parseStoryboard(mkSampleSlice());
  const ink = toInk(sb);
  assert.match(ink, /<div class='storyboard-img'>/);
  assert.match(ink, /<img src='assets\/ref-01\.png'/);
});

test("toInk 终止场景用 -> END", () => {
  const sb = parseStoryboard(mkSampleSlice());
  const ink = toInk(sb);
  // end 场景没有选项 → 应输出 -> END
  assert.match(ink, /=== end ===[\s\S]*?-> END/);
});

// ── compileInk ────────────────────────────────────────────────────────
test("compileInk 通过 inkjs CLI 产出 BOM-free JSON", () => {
  const sb = parseStoryboard(mkSampleSlice());
  const ink = toInk(sb);
  const json = compileInk(ink);
  assert.ok(json.length > 0);
  assert.ok(json.startsWith("{"), `JSON 应以 { 开头：${json.slice(0, 50)}`);
  assert.doesNotMatch(json, /^\uFEFF/, "JSON 不应有 BOM");
  const obj = JSON.parse(json);
  assert.ok(obj.inkVersion, "JSON 应含 inkVersion 字段");
});

// ── renderHtml ───────────────────────────────────────────────────────
test("renderHtml 生成单文件 HTML（含 inkjs runtime + JSON + 启动脚本）", () => {
  const sb = parseStoryboard(mkSampleSlice());
  const json = compileInk(toInk(sb));
  const html = renderHtml(sb, json);
  // 基础结构
  assert.match(html, /<!doctype html>/i);
  assert.match(html, /<title>森林序章<\/title>/);
  // 内嵌 inkjs runtime 关键字（inkjs 内部有 InkObject / Story 等标识）
  assert.ok(html.length > 100_000, `HTML 应内嵌 inkjs runtime，实际 ${html.length} 字节`);
  // 内嵌 JSON（经 JSON.stringify 转义，所以是 \"inkVersion\"）
  assert.ok(html.includes('\\"inkVersion\\"') || html.includes('"inkVersion"'));
  // 启动脚本标记
  assert.match(html, /<script type="module">/);
  assert.match(html, /new Story\(STORY_JSON\)/);
  assert.match(html, /ChooseChoiceIndex/);
});

test("renderHtml 模板字符串转义正确（运行时无语法错误）", () => {
  // 含特殊字符（反引号/引号/反斜杠/HTML 标签）但避免 \${ 的切片
  const md = `## 元信息（META）

| 标题 | \`特殊\` & <字符> 测试 "引号" |
| 简介 | 含 \\ 反斜杠文本 |
| 起始场景 | start |

## 场景 · start

- 标题：\`特殊\`场景
- 文案：

\`\`\`
测试 \`反引号\` 与特殊符号
\`\`\`

- 选项：

\`\`\`
继续 -> end
\`\`\`

## 场景 · end

- 文案：

\`\`\`
完。
\`\`\`
`;
  const sb = parseStoryboard(md);
  const json = compileInk(toInk(sb));
  const html = renderHtml(sb, json);
  // 不应抛错；输出应是非空 HTML
  assert.ok(html.length > 1000);
  assert.match(html, /<title>/);
});

test("compileInk 对含 \${ 的正文给出友好错误", () => {
  // Ink 语法冲突：正文含 \${ 会编译失败，应报友好提示
  const md = `## 元信息（META）

| 标题 | t |
| 简介 | x |
| 起始场景 | start |

## 场景 · start

- 文案：

\`\`\`
支付 \${cost} 金币
\`\`\`

- 选项：

\`\`\`
继续 -> end
\`\`\`

## 场景 · end

- 文案：

\`\`\`
完。
\`\`\`
`;
  const sb = parseStoryboard(md);
  const ink = toInk(sb);
  assert.throws(
    () => compileInk(ink),
    /\$\{|Ink 插值语法冲突/
  );
});

// ── CLI 集成：gd-wa storyboard new ────────────────────────────────────
test("CLI: storyboard new 生成骨架产物", async () => {
  const { spawnSync } = await import("node:child_process");
  const tmpOut = join(tmpdir(), `gdwa-storyboard-${Date.now()}.md`);
  rmSync(tmpOut, { force: true });
  const r = spawnSync(process.execPath, [
    cliPath, "storyboard", "new", "demo-sb", "--project", "tmp-proj", "--out", tmpOut,
  ], { encoding: "utf8" });
  assert.equal(r.status, 0, `CLI 退出码非 0：${r.stderr}`);
  assert.ok(existsSync(tmpOut), `产物未生成：${tmpOut}`);
  const content = readFileSync(tmpOut, "utf8");
  assert.match(content, /切片类型：storyboard/);
  assert.match(content, /## 元信息/);
  assert.match(content, /## 场景 · start/);
  assert.match(content, /## 规则摘要/);
  rmSync(tmpOut, { force: true });
});

test("CLI: storyboard new 拒绝非法切片名", async () => {
  const { spawnSync } = await import("node:child_process");
  const r = spawnSync(process.execPath, [
    cliPath, "storyboard", "new", "Bad Name!", "--project", "tmp-proj",
  ], { encoding: "utf8" });
  assert.notEqual(r.status, 0);
  assert.match(r.stderr + r.stdout, /非法/);
});

test("CLI: storyboard new 拒绝覆盖已存在文件", async () => {
  const { spawnSync } = await import("node:child_process");
  const tmpOut = join(tmpdir(), `gdwa-sb-dup-${Date.now()}.md`);
  writeFileSync(tmpOut, "占位", "utf8");
  const r = spawnSync(process.execPath, [
    cliPath, "storyboard", "new", "demo-sb", "--project", "tmp-proj", "--out", tmpOut,
  ], { encoding: "utf8" });
  assert.notEqual(r.status, 0);
  assert.match(r.stderr + r.stdout, /已存在|拒绝/);
  rmSync(tmpOut, { force: true });
});