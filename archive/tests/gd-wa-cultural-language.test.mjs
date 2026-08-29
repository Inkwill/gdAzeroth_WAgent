/**
 * gd-wa cultural-language 单测（v0.3.3）
 * 用 Node 原生 test runner（Node 20+）：`node --test archive/tests/*.test.mjs`
 */

import { test } from "node:test";
import assert from "node:assert/strict";
import { existsSync, rmSync, readFileSync, writeFileSync, mkdtempSync, mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { tmpdir } from "node:os";
import { spawnSync } from "node:child_process";

const here = dirname(fileURLToPath(import.meta.url));
const root = join(here, "..", "..");
const skeletonPath = join(root, "templates", "cultural-language-skeleton.yaml");
const cliPath = join(root, "tools", "gd-wa.mjs");

import { checkProject } from "../../tools/check.mjs";
import { scanSlices } from "../../tools/export.mjs";

// ── 骨架 ─────────────────────────────────────────────────────────────
test("cultural-language-skeleton.yaml 存在且可解析", () => {
  assert.ok(existsSync(skeletonPath), `骨架文件缺失：${skeletonPath}`);
  const text = readFileSync(skeletonPath, "utf8");
  assert.match(text, /^slice_type:\s*cultural-language/m);
  assert.match(text, /^version:\s*1/m);
});

test("骨架结构：6 块（core / language / customs / taboos / text / terminology）", () => {
  const sk = readFileSync(skeletonPath, "utf8");
  for (const id of ["cultural-core", "language", "customs", "taboos", "text", "terminology"]) {
    assert.match(sk, new RegExp(`id:\\s*${id}`), `缺少块：${id}`);
  }
  assert.match(sk, /en:\s*TERMINOLOGY/);
});

// ── CLI: cultural-language new ───────────────────────────────────────
test("CLI: cultural-language new 生成骨架产物（6 块 + 类型 meta）", () => {
  const tmpOut = join(tmpdir(), `gdwa-cl-${Date.now()}.md`);
  rmSync(tmpOut, { force: true });
  const r = spawnSync(process.execPath, [
    cliPath, "cultural-language", "new", "demo-culture", "--project", "tmp-proj", "--out", tmpOut,
  ], { encoding: "utf8" });
  assert.equal(r.status, 0, `CLI 退出码非 0：${r.stderr}`);
  const content = readFileSync(tmpOut, "utf8");
  assert.match(content, /切片类型：cultural-language/);
  for (const en of ["CULTURAL CORE", "LANGUAGE", "CUSTOMS", "TABOOS", "TEXT", "TERMINOLOGY"]) {
    assert.match(content, new RegExp(en), `缺块：${en}`);
  }
  rmSync(tmpOut, { force: true });
});

test("CLI: cultural-language new 拒绝非法切片名", () => {
  const r = spawnSync(process.execPath, [
    cliPath, "cultural-language", "new", "Bad Name!", "--project", "tmp-proj",
  ], { encoding: "utf8" });
  assert.notEqual(r.status, 0);
  assert.match(r.stderr + r.stdout, /非法/);
});

// ── 复用：一致性检查 + 装配导出 ──────────────────────────────────────
test("cultural-language 术语表纳入一致性检查（A3 禁止混用 → error）", () => {
  const tmpDir = mkdtempSync(join(tmpdir(), "gdwa-cl-check-"));
  const sliceDir = join(tmpDir, "WAgent");
  mkdirSync(sliceDir, { recursive: true });
  const md = `# 文化 · demo\n\n> 切片类型：cultural-language\n\n## 术语表（TERMINOLOGY）\n\n| 术语 | 定义 | 禁止混用 |\n|------|------|----------|\n| 精灵 | 森林的守望者 | 妖精 |\n\n## 文化文本（TEXT）\n\n- 谚语：精灵从不向妖精低头。\n`;
  writeFileSync(join(sliceDir, "demo-culture.md"), md, "utf8");
  const result = checkProject(tmpDir);
  assert.ok(result, "checkProject 应返回结果");
  assert.ok(result.issues.some((i) => i.code === "BANNED_TERM_USED"), "应检出禁止混用词「妖精」在正文出现");
  rmSync(tmpDir, { recursive: true, force: true });
});

test("cultural-language 术语表纳入装配导出（类型识别 + 术语词典）", () => {
  const tmpDir = mkdtempSync(join(tmpdir(), "gdwa-cl-export-"));
  const sliceDir = join(tmpDir, "WAgent");
  mkdirSync(sliceDir, { recursive: true });
  const md = `# 文化 · demo\n\n> 切片类型：cultural-language\n\n## 术语表（TERMINOLOGY）\n\n| 术语 | 定义 | 禁止混用 |\n|------|------|----------|\n| 精灵 | 森林的守望者 | 妖精 |\n`;
  writeFileSync(join(sliceDir, "demo-culture.md"), md, "utf8");
  const slices = scanSlices(tmpDir);
  assert.ok(slices, "scanSlices 应识别切片");
  assert.equal(slices[0].type, "cultural-language");
  assert.equal(slices[0].terms[0].term, "精灵");
  rmSync(tmpDir, { recursive: true, force: true });
});