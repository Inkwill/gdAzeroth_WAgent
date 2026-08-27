/**
 * parse-md — 轻量 Markdown 结构化解析（v0.2.4 抽公共）
 *
 * 服务对象：世界观切片 / 美术需求规格等结构化切片文档。
 * 能力：
 *   - section 划分：`## 标题（EN）`
 *   - 表格解析：连续 `|` 行视为一个表格（跳过分隔行 `|---|`），行号保留
 *
 * 限制：仅支持本套件切片的简单子集，不做通用 Markdown 解析。
 */

const SECTION_RE = /^##\s+(.+?)（([^）]+)）\s*$/;

/**
 * 解析 Markdown → sections
 * @returns [{ title, en, lines:[{text,lineNo}], tables:[{header, headerLine, rows:[{cells,lineNo}]}] }]
 */
export function parseMd(md) {
  const rawLines = md.split(/\r?\n/);
  const sections = [];
  let cur = null;
  let table = null;

  const commitTable = () => {
    if (table && cur) cur.tables.push(table);
    table = null;
  };

  for (let i = 0; i < rawLines.length; i++) {
    const text = rawLines[i];
    const lineNo = i + 1;

    const m = text.match(SECTION_RE);
    if (m) {
      commitTable();
      cur = { title: m[1].trim(), en: m[2].trim(), lines: [], tables: [] };
      sections.push(cur);
      continue;
    }

    if (text.trim().startsWith("|")) {
      const cells = text.split("|").slice(1, -1).map((c) => c.trim());
      if (cells.every((c) => /^:?-{2,}:?$/.test(c))) continue; // 分隔行
      if (!table) table = { header: cells, headerLine: lineNo, rows: [] };
      else table.rows.push({ cells, lineNo });
      continue;
    }

    commitTable();
    if (cur) cur.lines.push({ text, lineNo });
  }
  commitTable();

  return sections;
}

/** 把 section 表格行转成键值对象（第一列表头做 key） */
export function tableToMap(table) {
  const map = {};
  for (const r of table?.rows ?? []) {
    if (r.cells.length >= 2 && r.cells[0]) map[r.cells[0]] = r.cells[1];
  }
  return map;
}
