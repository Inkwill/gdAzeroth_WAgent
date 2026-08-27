/**
 * gd-wa worldview 骨架渲染单测（v0.2.1）
 * 用 Node 原生 test runner（Node 20+）：`node --test`
 * 固定产物路径的用例自带清理，可重复运行无残留
 */
import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync, existsSync, rmSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const root = join(here, "..");
const skeletonPath = join(root, "templates", "worldview-skeleton.yaml");
const cliPath = join(root, "tools", "gd-wa.mjs");

test("skeleton.yaml 存在且可解析", () => {
  assert.ok(existsSync(skeletonPath), `骨架文件缺失：${skeletonPath}`);
  const text = readFileSync(skeletonPath, "utf8");
  assert.match(text, /^slice_type:\s*worldview/m);
  assert.match(text, /^version:\s*1/m);
});

test("骨架结构：4 块（high-concept / tone-feel / aspects / terminology）", async () => {
  // 动态 import gd-wa 的 parseSimpleYaml 需导出；此处用 spawn 调用 CLI 验证
  const { spawnSync } = await import("node:child_process");
  const outPath = join(root, "tests", "out-slice.md");
  rmSync(outPath, { force: true }); // 自清理：可重复运行
  const r = spawnSync(process.execPath, [
    cliPath,
    "worldview", "new", "test-slice",
    "--project", "test-proj",
    "--out", outPath,
  ], { encoding: "utf8" });
  assert.equal(r.status, 0, `CLI exit=${r.status}\nstdout=${r.stdout}\nstderr=${r.stderr}`);
  try {
    const out = readFileSync(outPath, "utf8");
    assert.match(out, /## 高概念（HIGH-CONCEPT）/);
    assert.match(out, /## 基调（TONE & FEEL）/);
    assert.match(out, /## 核心设定骨架（ASPECTS）/);
    assert.match(out, /## 术语表（TERMINOLOGY）/);
    // ASPECTS 表头 4 行（世界观/文化/语言/美术）
    assert.match(out, /\| 世界观 \|/);
    assert.match(out, /\| 文化 \|/);
    assert.match(out, /\| 语言 \|/);
    assert.match(out, /\| 美术 \|/);
    // TERMINOLOGY 表头 1 行
    assert.match(out, /\| 术语 \| 定义 \| 禁止混用 \|/);
  } finally {
    rmSync(outPath, { force: true }); // 用后即清，无残留
  }
});

test("CLI 拒绝非法切片名", async () => {
  const { spawnSync } = await import("node:child_process");
  const r = spawnSync(process.execPath, [
    cliPath, "worldview", "new", "Bad Name!", "--project", "p",
  ], { encoding: "utf8" });
  assert.notEqual(r.status, 0);
  assert.match(r.stderr, /切片名非法/);
});

test("CLI 拒绝覆盖已存在文件", async () => {
  const { spawnSync } = await import("node:child_process");
  // 第一次：成功（沿用上一测试的产出）
  // 第二次：拒绝
  const out = join(root, "tests", "dup-slice.md");
  rmSync(out, { force: true }); // 自清理：可重复运行
  try {
    spawnSync(process.execPath, [cliPath, "worldview", "new", "dup-slice", "--project", "p", "--out", out], { encoding: "utf8" });
    const r = spawnSync(process.execPath, [cliPath, "worldview", "new", "dup-slice", "--project", "p", "--out", out], { encoding: "utf8" });
    assert.notEqual(r.status, 0);
    assert.match(r.stderr, /目标已存在/);
  } finally {
    rmSync(out, { force: true }); // 用后即清，无残留
  }
});

test("CLI 未知命令拒绝", async () => {
  const { spawnSync } = await import("node:child_process");
  const r = spawnSync(process.execPath, [cliPath, "foo", "bar"], { encoding: "utf8" });
  assert.notEqual(r.status, 0);
  assert.match(r.stderr, /未知命令/);
});