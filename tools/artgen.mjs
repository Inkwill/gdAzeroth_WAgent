/**
 * artgen — 美术参考图生成管线（v0.2.4）
 *
 * 调用链：gd-wa art gen → 本模块 → ComfyUI HTTP API（127.0.0.1:8188）→ PNG 落盘
 * 工作流模板：templates/t2i-z-image-v1.json（Z-Image Turbo，8 步 cfg=1，v1 API 格式）
 *
 * provider 抽象：
 *   - comfy    ：真实生成（本机 ComfyUI）
 *   - dry-run  ：降级模式，不调 API，落 prompt 文本 + 占位（服务不可达时自动降级）
 *
 * 产出：<outDir>/ref-<seed>.png（或 prompt-<seed>.txt）+ refs.json（元数据，可追溯可复现）
 */

import { readFileSync, writeFileSync, mkdirSync, existsSync } from "node:fs";
import { join, basename } from "node:path";
import { fileURLToPath } from "node:url";
import { buildPrompts, parseArtSpec } from "./prompt.mjs";

const DEFAULT_API = "http://127.0.0.1:8188";
const WORKFLOW_PATH = fileURLToPath(new URL("../templates/t2i-z-image-v1.json", import.meta.url));
const POLL_MS = 500;
const OUTPUT_NODE_TYPES = new Set(["SaveImage", "PreviewImage", "SaveAnimatedPNG"]);

// ── 探活 ───────────────────────────────────────────────────────────────────
export async function checkComfy(api = DEFAULT_API) {
  try {
    const r = await fetch(`${api}/queue`, { signal: AbortSignal.timeout(3000) });
    return r.ok;
  } catch {
    return false;
  }
}

// ── 工作流 patch（v1 格式：直接改节点 inputs） ─────────────────────────────
function patchWorkflow(workflow, { prompt, negativePrompt, seed }) {
  const clips = [];
  for (const n of Object.values(workflow)) {
    if (n.class_type === "CLIPTextEncode") clips.push(n);
    if (n.class_type === "KSampler") {
      if (seed !== undefined) n.inputs.seed = seed;
    }
  }
  if (prompt && clips[0]) clips[0].inputs.text = prompt;
  if (negativePrompt && clips[1]) clips[1].inputs.text = negativePrompt;
  return workflow;
}

// ── ComfyUI 提交/轮询/下载 ─────────────────────────────────────────────────
async function submitAndPoll(workflow, api, timeout = 600) {
  const res = await fetch(`${api}/prompt`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ prompt: workflow }),
    signal: AbortSignal.timeout(30_000),
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok || !data.prompt_id) {
    throw new Error(`ComfyUI 拒绝提交（HTTP ${res.status}）：${JSON.stringify(data).slice(0, 300)}`);
  }
  const id = data.prompt_id;
  const t0 = Date.now();
  while (Date.now() - t0 < timeout * 1000) {
    const h = await (await fetch(`${api}/history/${id}`, { signal: AbortSignal.timeout(10_000) })).json();
    if (h[id]?.outputs) return { id, outputs: h[id].outputs };
    await new Promise((r) => setTimeout(r, POLL_MS));
  }
  throw new Error(`ComfyUI 在 ${timeout}s 内未完成（prompt_id=${id}）`);
}

async function downloadImage(api, img) {
  const q = new URLSearchParams({ filename: img.filename, type: img.type });
  if (img.subfolder) q.set("subfolder", img.subfolder);
  const r = await fetch(`${api}/view?${q}`, { signal: AbortSignal.timeout(60_000) });
  if (!r.ok) throw new Error(`下载图片失败（HTTP ${r.status}）`);
  return Buffer.from(await r.arrayBuffer());
}

/** 真实生成：返回 [{file, promptId}] */
export async function genWithComfy({ prompt, negativePrompt, seed, outDir, api = DEFAULT_API, timeout = 600 }) {
  const workflow = patchWorkflow(JSON.parse(readFileSync(WORKFLOW_PATH, "utf8")), { prompt, negativePrompt, seed });
  const { id, outputs } = await submitAndPoll(workflow, api, timeout);
  const saved = [];
  for (const node of Object.values(outputs)) {
    for (const img of node?.images ?? []) {
      const raw = await downloadImage(api, img);
      const file = `ref-${seed}.png`;
      writeFileSync(join(outDir, file), raw);
      saved.push({ file, promptId: id });
    }
  }
  if (saved.length === 0) throw new Error(`ComfyUI 完成但无图片输出（prompt_id=${id}）`);
  return saved;
}

/** 降级：只落 prompt 文本 + 占位说明 */
export async function genDryRun({ prompt, negativePrompt, seed, outDir }) {
  const file = `prompt-${seed}.txt`;
  const body = [
    `# 参考图请求（dry-run 降级，未调 ComfyUI）`,
    `## 正向 prompt`,
    prompt,
    ``,
    `## 负向 prompt`,
    negativePrompt,
    ``,
    `> 本文件为占位。将内容贴入 ComfyUI/其他生图工具即可出图；`,
    `> 或启动 ComfyUI 后用 \`gd-wa art gen --provider comfy\` 真实生成。`,
    ``,
  ].join("\n");
  writeFileSync(join(outDir, file), body, "utf8");
  return [{ file, promptId: "dry-run" }];
}

// ── refs.json 元数据 ───────────────────────────────────────────────────────
function writeRefs(outDir, meta) {
  writeFileSync(join(outDir, "refs.json"), JSON.stringify(meta, null, 2), "utf8");
}

// ── 主入口 ──────────────────────────────────────────────────────────────────
/**
 * @param {object} o
 * @param {string} o.specPath    art spec 切片路径（projects/<项目>/WAgent/<切片>.md）
 * @param {string} o.project     项目 id
 * @param {number[]} o.seeds     seed 列表（批量筛种）
 * @param {string} [o.outDir]    输出目录（默认 projects/<项目>/WAgent/<切片>/）
 * @param {string} [o.provider]  comfy | dry-run（缺省自动：探活）
 * @param {string} [o.api]       ComfyUI 地址
 */
export async function genArt({ specPath, project, seeds, outDir, provider, api = DEFAULT_API, timeout = 600 }) {
  api = api || DEFAULT_API; // 兼容显式传 null（默认参数仅对 undefined 生效）
  if (!existsSync(specPath)) throw new Error(`切片不存在：${specPath}（先 \`gd-wa art new\`）`);
  const spec = parseArtSpec(specPath);
  const { prompt, negativePrompt, notes } = buildPrompts(spec);

  const sliceName = basename(specPath, ".md");
  const dir = outDir || join("projects", project, "WAgent", sliceName);
  mkdirSync(dir, { recursive: true });

  // provider 决定：显式 > 探活
  const activeProvider = provider || (await checkComfy(api) ? "comfy" : "dry-run");

  const refs = [];
  for (const seed of seeds) {
    const gen = activeProvider === "comfy" ? genWithComfy : genDryRun;
    const saved = await gen({ prompt, negativePrompt, seed, outDir: dir, api, timeout });
    for (const s of saved) {
      refs.push({ file: s.file, seed, promptId: s.promptId, model: activeProvider === "comfy" ? "z-image-turbo" : "dry-run", created: new Date().toISOString() });
    }
  }

  const meta = {
    slice: sliceName,
    project,
    provider: activeProvider,
    workflow: "t2i-z-image-v1",
    prompt,
    negative_prompt: negativePrompt,
    notes,
    refs,
  };
  writeRefs(dir, meta);

  return { outDir: dir, provider: activeProvider, prompt, negativePrompt, notes, refs };
}
