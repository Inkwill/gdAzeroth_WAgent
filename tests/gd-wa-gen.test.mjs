/**
 * gd-wa art gen 参考图管线单测（v0.2.4）
 * Node 原生 test runner：`node --test`
 * dry-run 全流程在临时目录构造，用后即清，无残留。
 */
import { test } from "node:test";
import assert from "node:assert/strict";
import { mkdtempSync, rmSync, readFileSync, writeFileSync, mkdirSync, existsSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

import { parseArtSpec, buildPrompts } from "../tools/prompt.mjs";
import { genArt } from "../tools/artgen.mjs";

const here = dirname(fileURLToPath(import.meta.url));

// ── 构造 art spec 切片 ─────────────────────────────────────────────────────
function mkArtSpec(dir, name) {
  const md = `# 美术需求规格 · ${name}

## 需求定位（PURPOSE）

> 主角立绘：用于角色介绍页的概念图
> 交付物类型：概念图

## 风格锚点（STYLE ANCHORS）

| 锚点 | 值 |
|------|-----|
| 风格关键词 | anime RPG game style, cel shading |
| 参考作品/艺术家 | Studio Ghibli |
| 色彩倾向 | warm palette, golden hour |
| 氛围基调 | heroic, nostalgic |

## 美术简报（ART BRIEF）

| 维度 | 指导 | 自洽锚点 |
|------|------|----------|
| 色彩 | 暖色主导 | 金色调 |
| 光照 | 逆光轮廓 | golden hour |

## 规格（SPEC）

| 项 | 值 |
|----|----|
| 尺寸 | 1024x1024 |
| 数量 | 1 |

## 必备要素（MUST-HAVE）

- 手持长剑
- 蓝色披风

## 禁忌（FORBIDDEN）

| 禁忌项 | 原因 |
|--------|------|
| 血迹 | 世界观禁止 |
| 现代服饰 | 时代不符 |
`;
  const p = join(dir, "WAgent", `${name}.md`);
  writeFileSync(p, md, "utf8");
  return p;
}

// ── 用例 ───────────────────────────────────────────────────────────────────
test("parseArtSpec 解析 6 块结构", (t) => {
  const dir = mkdtempSync(join(tmpdir(), "gdwa-gen-"));
  t.after(() => rmSync(dir, { recursive: true, force: true }));
  mkdirSync(join(dir, "WAgent"), { recursive: true });
  const p = mkArtSpec(dir, "hero");
  const spec = parseArtSpec(p);
  assert.match(spec.purpose, /主角立绘/);
  assert.equal(spec.anchors["风格关键词"], "anime RPG game style, cel shading");
  assert.equal(spec.anchors["色彩倾向"], "warm palette, golden hour");
  assert.ok(spec.brief.some((b) => b.dim === "色彩" && b.guide === "暖色主导"));
  assert.ok(spec.mustHave.includes("手持长剑"));
  assert.ok(spec.forbidden.includes("血迹"));
  assert.equal(spec.spec["尺寸"], "1024x1024");
});

test("buildPrompts 正向：风格锚点前置 + 维度指导 + MUST-HAVE", (t) => {
  const dir = mkdtempSync(join(tmpdir(), "gdwa-gen-"));
  t.after(() => rmSync(dir, { recursive: true, force: true }));
  mkdirSync(join(dir, "WAgent"), { recursive: true });
  const { prompt } = buildPrompts(parseArtSpec(mkArtSpec(dir, "hero")));
  const idx = {
    style: prompt.indexOf("anime RPG game style"),
    color: prompt.indexOf("warm palette"),
    purpose: prompt.indexOf("主角立绘"),
    sword: prompt.indexOf("手持长剑"),
  };
  // 风格关键词最前
  assert.ok(idx.style < idx.color && idx.style < idx.purpose && idx.style < idx.sword, `风格应前置：${prompt}`);
  assert.ok(idx.sword > idx.purpose, "MUST-HAVE 应在主体之后");
});

test("buildPrompts 负向：FORBIDDEN 禁忌 + 通用负向", (t) => {
  const dir = mkdtempSync(join(tmpdir(), "gdwa-gen-"));
  t.after(() => rmSync(dir, { recursive: true, force: true }));
  mkdirSync(join(dir, "WAgent"), { recursive: true });
  const { negativePrompt, notes } = buildPrompts(parseArtSpec(mkArtSpec(dir, "hero")));
  assert.match(negativePrompt, /血迹/);
  assert.match(negativePrompt, /现代服饰/);
  assert.match(negativePrompt, /low quality/);
  assert.ok(notes.some((n) => n.includes("cfg=1")), "应提示 Turbo 负向不生效");
});

test("genArt dry-run：refs.json + prompt 文本落盘，provider=dry-run", async (t) => {
  const dir = mkdtempSync(join(tmpdir(), "gdwa-gen-"));
  t.after(() => rmSync(dir, { recursive: true, force: true }));
  mkdirSync(join(dir, "WAgent"), { recursive: true });
  const p = mkArtSpec(dir, "hero");
  const r = await genArt({ specPath: p, project: "demo", seeds: [42, 43], provider: "dry-run", outDir: join(dir, "out") });
  assert.equal(r.provider, "dry-run");
  assert.equal(r.refs.length, 2);
  assert.ok(existsSync(join(dir, "out", "prompt-42.txt")));
  assert.ok(existsSync(join(dir, "out", "refs.json")));
  const meta = JSON.parse(readFileSync(join(dir, "out", "refs.json"), "utf8"));
  assert.equal(meta.slice, "hero");
  assert.equal(meta.refs[0].seed, 42);
  assert.match(meta.prompt, /anime RPG game style/);
  assert.match(meta.negative_prompt, /血迹/);
  assert.ok(meta.notes.length > 0);
  // 占位文本内容
  const txt = readFileSync(join(dir, "out", "prompt-42.txt"), "utf8");
  assert.match(txt, /正向 prompt/);
});

test("genArt comfy 不可达 → 自动降级 dry-run", async (t) => {
  const dir = mkdtempSync(join(tmpdir(), "gdwa-gen-"));
  t.after(() => rmSync(dir, { recursive: true, force: true }));
  mkdirSync(join(dir, "WAgent"), { recursive: true });
  const p = mkArtSpec(dir, "hero");
  // 127.0.0.1:1 必然不可达 → 探活失败 → dry-run
  const r = await genArt({ specPath: p, project: "demo", seeds: [7], api: "http://127.0.0.1:1", outDir: join(dir, "out") });
  assert.equal(r.provider, "dry-run");
});

test("genArt 切片不存在 → 报错", async (t) => {
  await assert.rejects(
    genArt({ specPath: join(here, "no-such-slice.md"), project: "demo", seeds: [1], provider: "dry-run", outDir: join(tmpdir(), "gdwa-void") }),
    /切片不存在/
  );
});

test("CLI: art gen 对不存在切片报错（exit 1）", async (t) => {
  const { spawnSync } = await import("node:child_process");
  const cliPath = join(here, "..", "tools", "gd-wa.mjs");
  const dir = mkdtempSync(join(tmpdir(), "gdwa-gen-"));
  t.after(() => rmSync(dir, { recursive: true, force: true }));
  const r = spawnSync(process.execPath, [cliPath, "art", "gen", "ghost", "--project", "p", "--provider", "dry-run"], { encoding: "utf8", cwd: dir });
  assert.notEqual(r.status, 0);
  assert.match(r.stderr, /切片不存在/);
});
