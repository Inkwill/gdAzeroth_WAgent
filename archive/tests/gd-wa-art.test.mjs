/**
 * gd-wa art 美术需求规格单测（v0.2.3）
 * Node 原生 test runner：`node --test`
 * 固定产物路径的用例自带清理，可重复运行无残留。
 */
import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync, existsSync, rmSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const root = join(here, "..", "..");
const skeletonPath = join(root, "templates", "art-spec.yaml");
const cliPath = join(root, "tools", "gd-wa.mjs");

test("art-spec.yaml 存在且可解析", () => {
  assert.ok(existsSync(skeletonPath), `骨架文件缺失：${skeletonPath}`);
  const text = readFileSync(skeletonPath, "utf8");
  assert.match(text, /^slice_type:\s*art-spec/m);
  assert.match(text, /^version:\s*1/m);
});

test("art new 生成 6 块骨架产物", async () => {
  const { spawnSync } = await import("node:child_process");
  const outPath = join(root, "tests", "out-art.md");
  rmSync(outPath, { force: true }); // 自清理：可重复运行
  const r = spawnSync(process.execPath, [
    cliPath, "art", "new", "hero-concept",
    "--project", "test-proj",
    "--out", outPath,
  ], { encoding: "utf8" });
  assert.equal(r.status, 0, `CLI exit=${r.status}\nstdout=${r.stdout}\nstderr=${r.stderr}`);
  try {
    const out = readFileSync(outPath, "utf8");
    // 标题为美术需求规格（区别于世界观切片）
    assert.match(out, /^# 美术需求规格 · hero-concept/m);
    // 6 块标题
    assert.match(out, /## 需求定位（PURPOSE）/);
    assert.match(out, /## 风格锚点（STYLE ANCHORS）/);
    assert.match(out, /## 美术简报（ART BRIEF）/);
    assert.match(out, /## 规格（SPEC）/);
    assert.match(out, /## 必备要素（MUST-HAVE）/);
    assert.match(out, /## 禁忌（FORBIDDEN）/);
    // ART BRIEF 表头：维度/指导/自洽锚点
    assert.match(out, /\| 维度 \| 指导 \| 自洽锚点 \|/);
    // FORBIDDEN 表头
    assert.match(out, /\| 禁忌项 \| 原因 \|/);
  } finally {
    rmSync(outPath, { force: true }); // 用后即清，无残留
  }
});

test("art new 产物含切片类型 art-spec", async () => {
  const { spawnSync } = await import("node:child_process");
  const outPath = join(root, "tests", "out-art2.md");
  rmSync(outPath, { force: true });
  try {
    spawnSync(process.execPath, [cliPath, "art", "new", "city-bg", "--project", "p", "--out", outPath], { encoding: "utf8" });
    const out = readFileSync(outPath, "utf8");
    assert.match(out, /切片类型：art-spec/);
  } finally {
    rmSync(outPath, { force: true });
  }
});

test("art new 拒绝非法切片名", async () => {
  const { spawnSync } = await import("node:child_process");
  const r = spawnSync(process.execPath, [cliPath, "art", "new", "Bad Art!", "--project", "p"], { encoding: "utf8" });
  assert.notEqual(r.status, 0);
  assert.match(r.stderr, /切片名非法/);
});

test("art new 拒绝覆盖已存在文件", async () => {
  const { spawnSync } = await import("node:child_process");
  const out = join(root, "tests", "dup-art.md");
  rmSync(out, { force: true });
  try {
    spawnSync(process.execPath, [cliPath, "art", "new", "dup-art", "--project", "p", "--out", out], { encoding: "utf8" });
    const r = spawnSync(process.execPath, [cliPath, "art", "new", "dup-art", "--project", "p", "--out", out], { encoding: "utf8" });
    assert.notEqual(r.status, 0);
    assert.match(r.stderr, /目标已存在/);
  } finally {
    rmSync(out, { force: true });
  }
});
