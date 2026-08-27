/**
 * prompt — art spec 切片 → 文生图提示词（v0.2.4）
 *
 * 组装策略（对齐 Z-Image Turbo prompt 工程，comfyui-t2i skill §7）：
 *   - 风格关键词放最前（attention 机制）
 *   - 正向 = 风格锚点（前置）+ PURPOSE + ART BRIEF 各维度指导 + MUST-HAVE + 氛围
 *   - 负向 = FORBIDDEN 禁忌 + 通用负向词
 *   - ⚠️ Z-Image Turbo cfg=1 时负向 prompt 不生效（notes 中提示）
 */

import { readFileSync } from "node:fs";
import { parseMd, tableToMap } from "./parse-md.mjs";

const DEFAULT_NEGATIVE = "low quality, bad anatomy, extra digits, missing fingers, worst quality, watermark, text";

/** 解析 art spec 切片 → 结构化字段 */
export function parseArtSpec(filePath) {
  const md = readFileSync(filePath, "utf8");
  const sections = parseMd(md);
  const get = (en) => sections.find((s) => s.en.toUpperCase().includes(en));

  const purposeSec = get("PURPOSE");
  const purpose = purposeSec
    ? purposeSec.lines.map((l) => l.text.replace(/^>\s*/, "").trim()).filter(Boolean).join("；")
    : "";

  const anchors = tableToMap(get("STYLE ANCHORS")?.tables[0]);
  const brief = (get("ART BRIEF")?.tables[0]?.rows ?? [])
    .map((r) => ({ dim: r.cells[0] ?? "", guide: r.cells[1] ?? "", anchor: r.cells[2] ?? "" }))
    .filter((b) => b.dim);
  const spec = tableToMap(get("SPEC")?.tables[0]);
  const mustHave = (get("MUST-HAVE")?.lines ?? [])
    .map((l) => l.text.match(/^\s*-\s+(.+)/)?.[1])
    .filter(Boolean);
  const forbidden = (get("FORBIDDEN")?.tables[0]?.rows ?? [])
    .map((r) => r.cells[0]).filter(Boolean);

  return { purpose, anchors, brief, spec, mustHave, forbidden };
}

/**
 * 组装正/负提示词
 * @returns { prompt, negativePrompt, notes }
 */
export function buildPrompts(spec, { negativeExtra = DEFAULT_NEGATIVE } = {}) {
  const parts = [];

  // 风格锚点前置（attention）
  const styleKw = spec.anchors["风格关键词"];
  if (styleKw) parts.push(styleKw);
  const styleRef = spec.anchors["参考作品/艺术家"];
  if (styleRef) parts.push(`in the style of ${styleRef}`);
  if (spec.anchors["色彩倾向"]) parts.push(spec.anchors["色彩倾向"]);
  if (spec.anchors["氛围基调"]) parts.push(spec.anchors["氛围基调"]);

  // PURPOSE（主体/用途）
  if (spec.purpose) parts.push(spec.purpose);

  // ART BRIEF 各维度指导（guide 优先，其次锚点）
  for (const b of spec.brief) {
    const g = (b.guide || b.anchor).trim();
    if (g) parts.push(`${b.dim}: ${g}`);
  }

  // MUST-HAVE 必备要素
  for (const m of spec.mustHave) parts.push(m);

  const prompt = parts.filter(Boolean).join(", ");

  // 负向：FORBIDDEN 禁忌 + 通用负向
  const negParts = [...spec.forbidden, negativeExtra].filter(Boolean);
  const negativePrompt = negParts.join(", ");

  const notes = [
    "Z-Image Turbo（cfg=1）对负向 prompt 不敏感；如需回避某要素，建议在正向里写“no X”或换非 Turbo 模型。",
  ];

  return { prompt, negativePrompt, notes };
}
