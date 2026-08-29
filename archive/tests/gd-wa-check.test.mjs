/**
 * gd-wa worldview check 一致性检查器单测（v0.2.2）
 * Node 原生 test runner：`node --test`
 * 全部用例在临时目录构造项目，用后即清，无残留。
 */
import { test } from "node:test";
import assert from "node:assert/strict";
import { mkdtempSync, rmSync, mkdirSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { spawnSync } from "node:child_process";

const cliPath = join(dirname(fileURLToPath(import.meta.url)), "..", "..", "tools", "gd-wa.mjs");

// ── 工具 ───────────────────────────────────────────────────────────────────
function mkProject(t) {
  const dir = mkdtempSync(join(tmpdir(), "gdwa-check-"));
  mkdirSync(join(dir, "WAgent"), { recursive: true });
  t.after(() => rmSync(dir, { recursive: true, force: true }));
  return dir;
}

function mkSlice(dir, name, { aspects = [], terms = [], body = "" } = {}) {
  const aspectRows = aspects.map(([l, s, a]) => `| ${l} | ${s} | ${a} |`).join("\n");
  const termRows = terms.map(([t, d, b]) => `| ${t} | ${d} | ${b} |`).join("\n");
  const md = `# 世界观切片 · ${name}\n\n## 高概念（HIGH-CONCEPT）\n${body}\n\n## 核心设定骨架（ASPECTS）\n\n| 层面 | 设定 | 自洽锚点 |\n|------|------|----------|\n${aspectRows}\n\n## 术语表（TERMINOLOGY）\n\n| 术语 | 定义 | 禁止混用 |\n|------|------|----------|\n${termRows}\n`;
  writeFileSync(join(dir, "WAgent", `${name}.md`), md, "utf8");
}

function runCheck(dir, project = dir) {
  return spawnSync(process.execPath, [cliPath, "worldview", "check", "--project", project], { encoding: "utf8" });
}

// ── 用例 ───────────────────────────────────────────────────────────────────
test("干净项目：术语一致、无混用、锚点一致 → 通过", (t) => {
  const dir = mkProject(t);
  mkSlice(dir, "slice-a", {
    aspects: [["世界观", "海洋文明", "以海洋为中心"]],
    terms: [["魂晶", "灵魂能量的结晶", "灵魂水晶"]],
    body: "> 一片以海洋为中心的文明。",
  });
  mkSlice(dir, "slice-b", {
    aspects: [["世界观", "海洋文明", "以海洋为中心"]],
    terms: [["魂晶", "灵魂能量的结晶", "灵魂水晶"]],
    body: "> 魂晶是重要的能量来源。",
  });
  const r = runCheck(dir);
  assert.equal(r.status, 0, `exit=${r.status}\nstdout=${r.stdout}\nstderr=${r.stderr}`);
  assert.match(r.stdout, /全部通过/);
  assert.doesNotMatch(r.stdout, /❌|⚠️/);
});

test("跨切片同一术语定义表述不同 → 警告（不阻塞）", (t) => {
  const dir = mkProject(t);
  mkSlice(dir, "slice-a", { terms: [["魂晶", "灵魂能量的结晶", ""]] });
  mkSlice(dir, "slice-b", { terms: [["魂晶", "一种诅咒矿物", ""]] });
  const r = runCheck(dir);
  assert.equal(r.status, 0);
  assert.match(r.stdout, /TERM_DEF_DIVERGE/);
  assert.match(r.stdout, /⚠️/);
});

test("同切片内术语重名且定义不一致 → 错误（exit 1）", (t) => {
  const dir = mkProject(t);
  mkSlice(dir, "slice-a", {
    terms: [
      ["魂晶", "灵魂能量的结晶", ""],
      ["魂晶", "诅咒矿物", ""],
    ],
  });
  const r = runCheck(dir);
  assert.notEqual(r.status, 0);
  assert.match(r.stdout, /TERM_DUP_DEF/);
  assert.match(r.stdout, /❌/);
});

test("禁止混用词出现在正文 → 错误（exit 1）+ 行号定位", (t) => {
  const dir = mkProject(t);
  mkSlice(dir, "slice-a", {
    terms: [["魂晶", "灵魂能量的结晶", "灵魂水晶，水晶"]],
    body: "> 大陆深处埋藏着灵魂水晶。",
  });
  const r = runCheck(dir);
  assert.notEqual(r.status, 0);
  assert.match(r.stdout, /BANNED_TERM_USED/);
  assert.match(r.stdout, /第 \d+ 行/);
  assert.match(r.stdout, /❌/);
});

test("禁止混用词在术语表声明处（表格行）不误报", (t) => {
  const dir = mkProject(t);
  mkSlice(dir, "slice-a", {
    terms: [["魂晶", "灵魂能量的结晶", "灵魂水晶"]],
    body: "> 一切正常。",
  });
  const r = runCheck(dir);
  assert.equal(r.status, 0, `exit=${r.status}\nstdout=${r.stdout}`);
  assert.match(r.stdout, /全部通过/);
});

test("ASPECTS 同层面自洽锚点表述分歧 → 警告（不阻塞）", (t) => {
  const dir = mkProject(t);
  mkSlice(dir, "slice-a", { aspects: [["世界观", "海洋文明", "以海洋为中心"]] });
  mkSlice(dir, "slice-b", { aspects: [["世界观", "沙漠文明", "以沙漠为中心"]] });
  const r = runCheck(dir);
  assert.equal(r.status, 0);
  assert.match(r.stdout, /ASPECT_ANCHOR_DIVERGE/);
});

test("同切片内同层面出现多行 → 错误（exit 1）", (t) => {
  const dir = mkProject(t);
  mkSlice(dir, "slice-a", {
    aspects: [
      ["世界观", "海洋文明", "以海洋为中心"],
      ["世界观", "天空文明", "以浮空岛为中心"],
    ],
  });
  const r = runCheck(dir);
  assert.notEqual(r.status, 0);
  assert.match(r.stdout, /ASPECT_DUP_LEVEL/);
});

test("空骨架（未填内容）→ 不误报，通过", (t) => {
  const dir = mkProject(t);
  mkSlice(dir, "slice-a", { aspects: [["世界观", "", ""]], terms: [["", "", ""]] });
  const r = runCheck(dir);
  assert.equal(r.status, 0);
  assert.match(r.stdout, /全部通过/);
});

test("无切片可检查 → 提示信息（exit 0）", (t) => {
  const dir = mkProject(t);
  const r = runCheck(dir, join(dir, "no-such-dir"));
  assert.equal(r.status, 0);
  assert.match(r.stdout, /没有可检查的切片/);
});
