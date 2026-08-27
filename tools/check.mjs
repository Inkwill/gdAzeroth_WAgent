/**
 * gd-wa worldview check — 一致性检查器（v0.2.2）
 *
 * 扫描 projects/<项目>/WAgent/*.md 世界观切片，执行两类检查：
 *   A. 术语表一致性：
 *      - A1 同切片内术语重名但定义不同      → ❌ error（文件内自相矛盾）
 *      - A2 跨切片同一术语定义归一化后不同  → ⚠️ warn（可能补充/矛盾，人工确认）
 *      - A3 术语表声明"禁止混用"的词仍在正文出现 → ❌ error（报切片+行号）
 *   B. 设定矛盾检测：
 *      - B1 同层面（世界观/文化/语言/美术）自洽锚点表述分歧 → ⚠️ warn（人工确认）
 *      - B2 同切片内同层面出现多行 → ❌ error（骨架应每层面一行）
 *
 * 空单元格（骨架未填）一律跳过，不误报。
 * 输出分级报告（✅/⚠️/❌）；有 ❌ → exit 1，仅 ⚠️ 或通过 → exit 0。
 *
 * 演进预留（v0.2.2 范围外）：术语条目未来可扩展 同义词/上位词/相关 字段，
 * 升级路径：受控词表 → 词典 → taxonomy → ontology。术语词典是本模块副产物，
 * 即未来 ontology 工程的种子数据。
 */

import { readdirSync, readFileSync } from "node:fs";
import { join, basename } from "node:path";

// ── 文本归一化（去空白/标点/全角差异，用于"是否不同"的比对） ──────────────
function norm(s) {
  return (s || "")
    .toLowerCase()
    .replace(/[\s，。、；：（）()·,.;:"'“”‘’!?！？—\-—_/\\[\]【】]+/g, "")
    .trim();
}

// ── 禁止混用列切分（逗号/顿号/分号/换行） ──────────────────────────────────
function splitBanned(s) {
  return (s || "").split(/[,，、;；\n]+/).map((x) => x.trim()).filter(Boolean);
}

// ── 解析一个切片文件 ────────────────────────────────────────────────────────
// 返回 { name, path, lines:[{text,lineNo,inTable}], terms:[{term,def,banned,line}],
//         aspects:[{level,setting,anchor,line}] }
function parseSlice(filePath) {
  const md = readFileSync(filePath, "utf8");
  const rawLines = md.split(/\r?\n/);
  const lines = rawLines.map((text, i) => ({ text, lineNo: i + 1, inTable: false }));

  const terms = [];
  const aspects = [];

  // 当前 section（按 `## 标题（EN）` 划分）
  let curSection = null;
  const sectionRe = /^##\s+.+（([^）]+)）\s*$/;

  // 表格解析状态
  let table = null; // { header, rowStartLine }  —— 连续 | 行视为一个表格

  const commitTermRows = (rows) => {
    for (const r of rows) {
      if (r.cells.length < 3) continue;
      const term = r.cells[0];
      if (!term) continue;
      terms.push({ term, def: r.cells[1] ?? "", banned: r.cells[2] ?? "", line: r.lineNo });
    }
  };
  const commitAspectRows = (rows) => {
    for (const r of rows) {
      if (r.cells.length < 3) continue;
      const level = r.cells[0];
      if (!level) continue;
      aspects.push({ level, setting: r.cells[1] ?? "", anchor: r.cells[2] ?? "", line: r.lineNo });
    }
  };

  for (let i = 0; i < rawLines.length; i++) {
    const text = rawLines[i];
    const lineNo = i + 1;
    const isPipe = text.trim().startsWith("|");

    // section 切换
    const sm = text.match(sectionRe);
    if (sm) {
      // 结束上一表格
      if (table) { commitSectionTable(curSection, table); table = null; }
      curSection = sm[1].toLowerCase().replace(/[\s&-]+/g, "-");
      continue;
    }

    if (isPipe) {
      lines[lineNo - 1].inTable = true;
      const cells = text.split("|").slice(1, -1).map((c) => c.trim());
      // 分隔行（|---| / |:--:|）跳过
      if (cells.every((c) => /^:?-{2,}:?$/.test(c))) continue;
      if (!table) table = { header: cells, rows: [], headerLine: lineNo };
      else table.rows.push({ cells, lineNo });
      continue;
    }

    // 非表格行 → 结束当前表格
    if (table) { commitSectionTable(curSection, table); table = null; }
  }
  if (table) commitSectionTable(curSection, table);

  function commitSectionTable(section, t) {
    if (!section) return;
    if (section === "terminology") commitTermRows(t.rows);
    if (section === "aspects") commitAspectRows(t.rows);
  }

  return {
    name: basename(filePath),
    path: filePath,
    lines,
    terms,
    aspects,
  };
}

// ── 检查执行 ────────────────────────────────────────────────────────────────
// 返回 { issues: [{level, code, msg}], dict: Map<term, entries> }
function runChecks(slices) {
  const issues = [];

  // ── A. 术语表一致性 ──
  const dict = new Map(); // term(lower) -> [{slice, term, def, banned, line}]
  for (const s of slices) {
    for (const t of s.terms) {
      const key = t.term.toLowerCase();
      if (!dict.has(key)) dict.set(key, []);
      dict.get(key).push({ slice: s, ...t });
    }
  }

  for (const [key, entries] of dict) {
    // A1 同切片内重名但定义不同 → error
    const bySlice = new Map();
    for (const e of entries) {
      if (!bySlice.has(e.slice.name)) bySlice.set(e.slice.name, []);
      bySlice.get(e.slice.name).push(e);
    }
    for (const [name, es] of bySlice) {
      const defs = new Set(es.map((e) => norm(e.def)).filter(Boolean));
      if (es.length > 1 && defs.size > 1) {
        issues.push({
          level: "error",
          code: "TERM_DUP_DEF",
          msg: `切片 ${name} 内术语「${es[0].term}」出现 ${es.length} 次且定义不一致（第 ${es.map((e) => e.line).join("/")} 行）`,
        });
      }
    }
    // A2 跨切片定义归一化后不同 → warn
    if (entries.length > 1) {
      const defs = new Set(entries.map((e) => norm(e.def)).filter(Boolean));
      if (defs.size > 1) {
        issues.push({
          level: "warn",
          code: "TERM_DEF_DIVERGE",
          msg: `术语「${entries[0].term}」在 ${entries.length} 个切片中定义表述不同，请人工确认是否矛盾：` +
            entries.map((e) => `${e.slice.name}:${e.line}「${e.def || "(空)"}」`).join("；"),
        });
      }
    }
  }

  // A3 禁止混用词在正文出现 → error（跳过所有表格行，避免术语表声明自身误报）
  for (const s of slices) {
    for (const t of s.terms) {
      for (const bw of splitBanned(t.banned)) {
        const needle = bw.toLowerCase();
        for (const l of s.lines) {
          if (l.inTable) continue;
          if (l.text.toLowerCase().includes(needle)) {
            issues.push({
              level: "error",
              code: "BANNED_TERM_USED",
              msg: `术语「${t.term}」声明禁止混用「${bw}」，但正文第 ${l.lineNo} 行仍在使用（${s.name}）`,
            });
          }
        }
      }
    }
  }

  // ── B. 设定矛盾检测 ──
  const anchors = new Map(); // level -> [{slice, anchor, setting, line}]
  for (const s of slices) {
    for (const a of s.aspects) {
      const key = a.level.toLowerCase();
      if (!anchors.has(key)) anchors.set(key, []);
      anchors.get(key).push({ slice: s, ...a });
    }
  }
  for (const [level, entries] of anchors) {
    // B1 同层面锚点表述分歧 → warn
    const nonEmpty = entries.filter((e) => norm(e.anchor));
    if (nonEmpty.length > 1) {
      const anchorsSet = new Set(nonEmpty.map((e) => norm(e.anchor)));
      if (anchorsSet.size > 1) {
        issues.push({
          level: "warn",
          code: "ASPECT_ANCHOR_DIVERGE",
          msg: `层面「${level}」的自洽锚点在 ${nonEmpty.length} 个切片中表述不同，请人工确认是否矛盾：` +
            nonEmpty.map((e) => `${e.slice.name}:${e.line}「${e.anchor}」`).join("；"),
        });
      }
    }
    // B2 同切片内同层面多行 → error
    const bySlice = new Map();
    for (const e of entries) {
      if (!bySlice.has(e.slice.name)) bySlice.set(e.slice.name, []);
      bySlice.get(e.slice.name).push(e);
    }
    for (const [name, es] of bySlice) {
      if (es.length > 1) {
        issues.push({
          level: "error",
          code: "ASPECT_DUP_LEVEL",
          msg: `切片 ${name} 内层面「${level}」出现 ${es.length} 行（第 ${es.map((e) => e.line).join("/")} 行），骨架应为每层面一行`,
        });
      }
    }
  }

  return { issues, dict };
}

// ── 项目级入口 ──────────────────────────────────────────────────────────────
// 扫描 <projectDir>/WAgent/*.md，返回 { slices, issues, dict } 或 null（无切片）
export function checkProject(projectDir) {
  const sliceDir = join(projectDir, "WAgent");
  let files;
  try {
    files = readdirSync(sliceDir).filter((f) => f.endsWith(".md"));
  } catch {
    return null; // 目录不存在
  }
  if (files.length === 0) return null;

  const slices = files.map((f) => parseSlice(join(sliceDir, f)));
  const { issues, dict } = runChecks(slices);
  return { slices, issues, dict };
}

// ── 报告渲染（纯文本，供 CLI 打印） ─────────────────────────────────────────
export function renderReport(projectId, result) {
  if (!result) {
    return `ℹ 项目 ${projectId} 没有可检查的切片（期望 projects/${projectId}/WAgent/*.md）`;
  }
  const { slices, issues, dict } = result;
  const errs = issues.filter((i) => i.level === "error");
  const warns = issues.filter((i) => i.level === "warn");
  const termCount = [...dict.values()].length;

  const out = [];
  out.push(`一致性检查：项目 ${projectId}`);
  out.push(`  切片 ${slices.length} 个：${slices.map((s) => s.name).join("、")}`);
  out.push(`  术语词典 ${termCount} 条 · 错误 ${errs.length} · 警告 ${warns.length}`);
  for (const i of issues) {
    const tag = i.level === "error" ? "❌" : "⚠️";
    out.push(`  ${tag} [${i.code}] ${i.msg}`);
  }
  if (errs.length === 0) out.push(errs.length === 0 && warns.length === 0 ? "  ✅ 全部通过" : `  ✅ 无错误（${warns.length} 条警告待人工确认）`);
  return out.join("\n");
}
