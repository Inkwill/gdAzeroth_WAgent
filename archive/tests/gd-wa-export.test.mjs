/**
 * gd-wa slice export 切片装配导出单测（v0.2.5）
 * Node 原生 test runner：`node --test`
 * 全部用例在临时目录构造，用后即清，无残留。
 */
import { test } from "node:test";
import assert from "node:assert/strict";
import { mkdtempSync, rmSync, mkdirSync, writeFileSync, readFileSync, existsSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { spawnSync } from "node:child_process";

import { scanSlices, renderIndex } from "../../tools/export.mjs";

const cliPath = join(dirname(fileURLToPath(import.meta.url)), "..", "..", "tools", "gd-wa.mjs");

// ── 构造切片 ─────────────────────────────────────────────────────────────────
function mkProject(t) {
  const dir = mkdtempSync(join(tmpdir(), "gdwa-export-"));
  mkdirSync(join(dir, "WAgent"), { recursive: true });
  t.after(() => rmSync(dir, { recursive: true, force: true }));
  return dir;
}

function mkWorldview(dir, name, { summary, terms = [] } = {}) {
  const rows = terms.map(([t, d]) => `| ${t} | ${d} |  |`).join("\n");
  const md = `# 世界观切片 · ${name}\n\n> 任务所属项目：demo · 切片类型：worldview · 生成时间：2026-08-27\n\n## 高概念（HIGH-CONCEPT）\n\n> ${summary}\n\n## 术语表（TERMINOLOGY）\n\n| 术语 | 定义 | 禁止混用 |\n|------|------|----------|\n${rows}\n`;
  writeFileSync(join(dir, "WAgent", `${name}.md`), md, "utf8");
}

function mkArtSpec(dir, name, { summary }) {
  const md = `# 美术需求规格 · ${name}\n\n> 任务所属项目：demo · 切片类型：art-spec · 生成时间：2026-08-27\n\n## 需求定位（PURPOSE）\n\n> ${summary}\n`;
  writeFileSync(join(dir, "WAgent", `${name}.md`), md, "utf8");
}

// ── 用例 ─────────────────────────────────────────────────────────────────────
test("scanSlices 识别类型与摘要（worldview + art-spec）", (t) => {
  const dir = mkProject(t);
  mkWorldview(dir, "lore-a", { summary: "一片以海洋为中心的文明。", terms: [["魂晶", "灵魂能量的结晶"]] });
  mkArtSpec(dir, "hero", { summary: "主角立绘：用于角色介绍页的概念图" });
  const slices = scanSlices(dir);
  assert.equal(slices.length, 2);
  const lore = slices.find((s) => s.name === "lore-a");
  assert.equal(lore.type, "worldview");
  assert.match(lore.summary, /海洋/);
  assert.equal(lore.terms[0].term, "魂晶");
  const hero = slices.find((s) => s.name === "hero");
  assert.equal(hero.type, "art-spec");
  assert.match(hero.summary, /主角立绘/);
});

test("renderIndex 装配切片清单 + 跨切片术语词典", (t) => {
  const dir = mkProject(t);
  mkWorldview(dir, "lore-a", { summary: "海洋文明。", terms: [["魂晶", "灵魂能量的结晶"]] });
  mkArtSpec(dir, "hero", { summary: "主角立绘。" });
  const index = renderIndex("demo", scanSlices(dir));
  assert.match(index, /切片 2 个/);
  assert.match(index, /\| lore-a \| worldview \| 海洋文明。/);
  assert.match(index, /\| hero \| art-spec \| 主角立绘。/);
  assert.match(index, /\| 魂晶 \| 灵魂能量的结晶 \| lore-a \|/);
});

test("无术语表 → 提示暂无术语条目", (t) => {
  const dir = mkProject(t);
  mkArtSpec(dir, "hero", { summary: "主角立绘。" });
  const index = renderIndex("demo", scanSlices(dir));
  assert.match(index, /暂无术语条目/);
});

test("CLI: slice export 生成 index.md（真实流程）", (t) => {
  const dir = mkProject(t);
  mkWorldview(dir, "lore-a", { summary: "海洋文明。", terms: [["魂晶", "灵魂能量的结晶"]] });
  mkArtSpec(dir, "hero", { summary: "主角立绘。" });
  const r = spawnSync(process.execPath, [cliPath, "slice", "export", "--project", dir], { encoding: "utf8" });
  assert.equal(r.status, 0, `exit=${r.status}\nstdout=${r.stdout}\nstderr=${r.stderr}`);
  assert.match(r.stdout, /切片索引已导出/);
  const idx = readFileSync(join(dir, "WAgent", "index.md"), "utf8");
  assert.match(idx, /切片 2 个/);
  assert.match(idx, /\| 魂晶 \|/);
});

test("CLI: 无切片 → 提示信息（exit 0）", (t) => {
  const dir = mkProject(t);
  const r = spawnSync(process.execPath, [cliPath, "slice", "export", "--project", join(dir, "void")], { encoding: "utf8" });
  assert.equal(r.status, 0);
  assert.match(r.stdout, /没有可装配的切片/);
});
