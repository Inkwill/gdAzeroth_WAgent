/**
 * export — 切片装配导出（v0.2.5）
 *
 * 扫描 projects/<项目>/WAgent/*.md 全部切片，装配为索引文档 index.md：
 *   - 切片清单（类型/摘要）
 *   - 项目级术语词典（跨切片汇总术语表——一致性检查的副产物，未来 ontology 种子）
 *
 * 产出供其他分控**只读引用**（v0.4.0 直达互调的基础）：一份文档看全项目表现切片。
 */

import { readdirSync, readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { join, basename } from "node:path";
import { parseMd } from "./parse-md.mjs";

/** 扫描项目切片目录，返回切片元数据列表；目录不存在/无切片返回 null */
export function scanSlices(projectDir) {
  const sliceDir = join(projectDir, "WAgent");
  let files;
  try {
    files = readdirSync(sliceDir).filter((f) => f.endsWith(".md") && f !== "index.md");
  } catch {
    return null;
  }
  if (files.length === 0) return null;
  return files.map((f) => parseSlice(join(sliceDir, f)));
}

function parseSlice(path) {
  const md = readFileSync(path, "utf8");
  const sections = parseMd(md);
  const first = sections[0];

  // 类型：切片头 meta `切片类型：xxx`；fallback 首 section en
  const type = md.match(/切片类型：([^\s·]+)/)?.[1]
    ?? (first?.en ?? "unknown").toLowerCase();

  // 摘要：首 section 正文第一行（去 > 前缀、去占位符 <...>）
  const lines = (first?.lines ?? [])
    .map((l) => l.text.replace(/^>\s*/, "").trim())
    .filter((l) => l && !l.startsWith("<"));
  const summary = lines[0] ?? "";

  // 术语表（如有）
  const terms = [];
  const termSec = sections.find((s) => s.en.toUpperCase().includes("TERMINOLOGY"));
  for (const r of termSec?.tables[0]?.rows ?? []) {
    if (r.cells[0]) terms.push({ term: r.cells[0], def: r.cells[1] ?? "" });
  }

  return { name: basename(path, ".md"), path, type, summary, terms };
}

/** 渲染索引 Markdown */
export function renderIndex(projectId, slices) {
  const terms = [];
  for (const s of slices) {
    for (const t of s.terms) terms.push({ ...t, from: s.name });
  }

  const out = [];
  out.push(`# 项目 ${projectId} · 世界观与表现切片索引`);
  out.push("");
  out.push(`> 生成时间：${new Date().toISOString().slice(0, 10)} · 切片 ${slices.length} 个 · 由 \`gd-wa slice export\` 生成`);
  out.push("");
  out.push("## 切片清单");
  out.push("");
  out.push("| 切片 | 类型 | 摘要 |");
  out.push("|------|------|------|");
  for (const s of slices) {
    out.push(`| ${s.name} | ${s.type} | ${s.summary || "—"} |`);
  }
  out.push("");
  out.push("## 项目级术语词典（跨切片汇总）");
  out.push("");
  if (terms.length === 0) {
    out.push("> 暂无术语条目（各切片未填术语表）");
  } else {
    out.push("| 术语 | 定义 | 来源切片 |");
    out.push("|------|------|----------|");
    for (const t of terms) out.push(`| ${t.term} | ${t.def || "—"} | ${t.from} |`);
  }
  out.push("");
  return out.join("\n");
}

/**
 * 装配导出：扫描 → 渲染 → 写 index.md
 * @returns { outPath, slices, terms } 或 null（无切片）
 */
export function exportProject({ projectId, projectDir, outPath }) {
  const slices = scanSlices(projectDir);
  if (!slices) return null;
  const content = renderIndex(projectId, slices);
  mkdirSync(projectDir && join(projectDir, "WAgent"), { recursive: true });
  writeFileSync(outPath, content, "utf8");
  const terms = [];
  for (const s of slices) terms.push(...s.terms.map((t) => ({ ...t, from: s.name })));
  return { outPath, slices, terms };
}
