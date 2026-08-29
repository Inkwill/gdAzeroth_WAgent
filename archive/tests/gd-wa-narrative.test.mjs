/**
 * gd-wa narrative 单测（v0.3.2）
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
const skeletonPath = join(root, "templates", "narrative-skeleton.yaml");
const cliPath = join(root, "tools", "gd-wa.mjs");

import { checkProject } from "../../tools/check.mjs";
import { scanSlices } from "../../tools/export.mjs";

// ── 骨架 ─────────────────────────────────────────────────────────────
test("narrative-skeleton.yaml 存在且可解析", () => {
  assert.ok(existsSync(skeletonPath), `骨架文件缺失：${skeletonPath}`);
  const text = readFileSync(skeletonPath, "utf8");
  assert.match(text, /^slice_type:\s*narrative/m);
  assert.match(text, /^version:\s*1/m);
});

test("骨架结构：6 块（core / structure / characters / events / text / terminology）", () => {
  const sk = readFileSync(skeletonPath, "utf8");
  for (const id of ["narrative-core", "structure", "characters", "events", "text", "terminology"]) {
    assert.match(sk, new RegExp(`id:\\s*${id}`), `缺少块：${id}`);
  }
  // 术语表必须用 TERMINOLOGY（一致性检查器消费）
  assert.match(sk, /en:\s*TERMINOLOGY/);
});

// ── CLI: narrative new ───────────────────────────────────────────────
test("CLI: narrative new 生成骨架产物（6 块 + 类型 meta）", () => {
  const tmpOut = join(tmpdir(), `gdwa-narr-${Date.now()}.md`);
  rmSync(tmpOut, { force: true });
  const r = spawnSync(process.execPath, [
    cliPath, "narrative", "new", "demo-story", "--project", "tmp-proj", "--out", tmpOut,
  ], { encoding: "utf8" });
  assert.equal(r.status, 0, `CLI 退出码非 0：${r.stderr}`);
  const content = readFileSync(tmpOut, "utf8");
  assert.match(content, /切片类型：narrative/);
  for (const en of ["NARRATIVE CORE", "STRUCTURE", "CHARACTERS", "EVENTS", "TEXT", "TERMINOLOGY"]) {
    assert.match(content, new RegExp(en), `缺块：${en}`);
  }
  rmSync(tmpOut, { force: true });
});

test("CLI: narrative new 拒绝非法切片名", () => {
  const r = spawnSync(process.execPath, [
    cliPath, "narrative", "new", "Bad Name!", "--project", "tmp-proj",
  ], { encoding: "utf8" });
  assert.notEqual(r.status, 0);
  assert.match(r.stderr + r.stdout, /非法/);
});

// ── 一致性检查覆盖（复用 check.mjs，术语表自动纳入） ──────────────────
test("narrative 术语表纳入一致性检查（A3 禁止混用 → error）", () => {
  // 构造一个含禁止混用违规的 narrative 切片项目
  const tmpDir = mkdtempSync(join(tmpdir(), "gdwa-narr-check-"));
  const sliceDir = join(tmpDir, "WAgent");
  mkdirSync(sliceDir, { recursive: true });
  const md = `# 叙事 · demo\n\n> 切片类型：narrative\n\n## 术语表（TERMINOLOGY）\n\n| 术语 | 定义 | 禁止混用 |\n|------|------|----------|\n| 帝国 | 统治大陆的政权 | 王国 |\n\n## 叙事文本（TEXT）\n\n- 开场旁白：帝国崛起，王国覆灭。\n`;
  writeFileSync(join(sliceDir, "demo-story.md"), md, "utf8");
  const result = checkProject(tmpDir);
  assert.ok(result, "checkProject 应返回结果");
  const hasBanned = result.issues.some((i) => i.code === "BANNED_TERM_USED");
  assert.ok(hasBanned, "应检出禁止混用词「王国」在正文出现");
  rmSync(tmpDir, { recursive: true, force: true });
});

test("narrative 术语表纳入装配导出（export.mjs 术语词典）", () => {
  const tmpDir = mkdtempSync(join(tmpdir(), "gdwa-narr-export-"));
  const sliceDir = join(tmpDir, "WAgent");
  mkdirSync(sliceDir, { recursive: true });
  const md = `# 叙事 · demo\n\n> 切片类型：narrative\n\n## 术语表（TERMINOLOGY）\n\n| 术语 | 定义 | 禁止混用 |\n|------|------|----------|\n| 帝国 | 统治大陆的政权 | 王国 |\n`;
  writeFileSync(join(sliceDir, "demo-story.md"), md, "utf8");
  const slices = scanSlices(tmpDir);
  assert.ok(slices, "scanSlices 应识别切片");
  assert.equal(slices[0].type, "narrative");
  assert.equal(slices[0].terms[0].term, "帝国");
  rmSync(tmpDir, { recursive: true, force: true });
});