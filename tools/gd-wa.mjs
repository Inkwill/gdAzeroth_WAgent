#!/usr/bin/env node
/**
 * gd-wa — gdAzeroth (WAgent) 分控内 CLI（v0.2.3）
 * 命名规范：`gd-` 前缀 + 分控代号缩写（wa = WAgent），三层 `<bin> <能力id> <动作>`
 * 当前子命令：
 *   worldview new <切片名> --project <项目id> [--out <路径>]  世界观切片骨架（v0.2.1）
 *   worldview check --project <项目id>                       一致性检查（v0.2.2）
 *   art new <切片名> --project <项目id> [--out <路径>]        美术需求规格（v0.2.3）
 *   art gen <切片名> --project <项目id> [--seed 42] [--provider comfy|dry-run]
 *                                                            参考图生成（v0.2.4）
 *
 * 不做：内容生成（高概念/设定/术语是创作产物）；不与总控 gd 命令冲突。
 */

import { readFileSync, writeFileSync, existsSync, mkdirSync } from "node:fs";
import { dirname, join, isAbsolute } from "node:path";
import { fileURLToPath } from "node:url";
import { checkProject, renderReport } from "./check.mjs";
import { genArt } from "./artgen.mjs";

// ── 极简 YAML 解析（仅支持 v0.2.1 skeleton.yaml 所需子集） ──────────────
// 支持：2 空格缩进 / map / list of map / block scalar (`|` `>`) / 行尾注释 / 引号
// 不支持：flow style、anchor、tag、复杂 key
function parseSimpleYaml(text) {
  const lines = text.split(/\r?\n/);
  const root = {};
  // stack: [{ indent, container: object_or_array, type: 'map'|'list' }]
  const stack = [{ indent: -1, container: root, type: 'map' }];
  const top = () => stack[stack.length - 1];

  function popToIndent(indent) {
    while (stack.length > 1) {
      const t = stack[stack.length - 1];
      if (t.indent <= indent) break; // 只弹更深的；同 indent 与更浅的全部保留
      stack.pop();
    }
  }

  for (let i = 0; i < lines.length; i++) {
    const raw = lines[i];
    if (!raw.trim() || raw.trim().startsWith('#')) continue;
    const indent = raw.match(/^ */)[0].length;
    const trimmed = raw.slice(indent);
    popToIndent(indent);

    if (trimmed.startsWith('- ')) {
      const t = top();
      if (t.type !== 'list') throw new Error(`unexpected list item at line ${i + 1}`);
      const itemContent = trimmed.slice(2);
      const newItem = {};
      t.container.push(newItem);
      // item 子字段缩进 = list item 缩进 + 2
      stack.push({ indent: indent + 2, container: newItem, type: 'map' });
      // 处理 `- key: value` 同行情形
      if (itemContent.includes(':')) {
        const colonIdx = itemContent.indexOf(':');
        const k = itemContent.slice(0, colonIdx).trim();
        let v = itemContent.slice(colonIdx + 1).trim();
        if ((v.startsWith('"') && v.endsWith('"')) || (v.startsWith("'") && v.endsWith("'"))) v = v.slice(1, -1);
        newItem[k] = v;
      }
    } else {
      const t = top();
      if (t.type !== 'map') throw new Error(`expected list item at line ${i + 1}, got map`);
      const colonIdx = trimmed.indexOf(':');
      if (colonIdx < 0) continue;
      const key = trimmed.slice(0, colonIdx).trim();
      let value = trimmed.slice(colonIdx + 1).trim();

      if (value === '') {
        const next = lines[i + 1];
        if (next === undefined) { t.container[key] = null; }
        else {
          const nextIndent = next.match(/^ */)[0].length;
          const nextTrim = next.slice(nextIndent);
          if (nextIndent > indent && nextTrim.startsWith('- ')) {
            t.container[key] = [];
            stack.push({ indent: nextIndent, container: t.container[key], type: 'list' });
          } else if (nextIndent > indent) {
            t.container[key] = {};
            stack.push({ indent: nextIndent, container: t.container[key], type: 'map' });
          } else {
            t.container[key] = null;
          }
        }
      } else if (value === '|' || value === '>') {
        const blockIndent = lines[i + 1]?.match(/^ */)[0].length ?? (indent + 2);
        const buf = [];
        let j = i + 1;
        while (j < lines.length) {
          const l = lines[j];
          if (!l.trim()) { buf.push(''); j++; continue; }
          const ind = l.match(/^ */)[0].length;
          if (ind < blockIndent) break;
          buf.push(l.slice(blockIndent));
          j++;
        }
        t.container[key] = buf.join('\n').replace(/\n+$/, '');
        i = j - 1;
      } else {
        if ((value.startsWith('"') && value.endsWith('"')) || (value.startsWith("'") && value.endsWith("'"))) value = value.slice(1, -1);
        t.container[key] = value;
      }
    }
  }
  return root;
}

// ── 切片渲染（v0.2.1 泛化：worldview / art 共用） ─────────────────────────
function renderSlice(skeleton, meta, opts = {}) {
  const {
    cmdLabel = "worldview new",
    title = "世界观切片",
    skeletonFile = "templates/worldview-skeleton.yaml",
    version = "v0.2.1",
  } = opts;
  const header = `# ${title} · ${meta.name}\n\n> 任务所属项目：${meta.project} · 切片类型：${skeleton.slice_type} · 生成时间：${meta.date}\n> 由 \`gd-wa ${cmdLabel}\` 生成（${version}），骨架版本 ${skeleton.version}。\n\n`;
  const body = skeleton.sections.map((s) => s.template).join("\n");
  const footer = `\n---\n\n> 本切片为 ${version} 模板生成的结构化骨架——内容由创作填入，骨架结构由 \`${skeletonFile}\` 定义（机器可读，供 \`gd-wa worldview check\` 一致性检查）。\n`;
  return header + body + footer;
}

// ── CLI 入口 ──────────────────────────────────────────────────────────────
function usage() {
  const here = fileURLToPath(import.meta.url);
  console.log(`gd-wa — gdAzeroth (WAgent) 分控内 CLI（v0.2.4）\n\n用法：\n  gd-wa worldview new <切片名> --project <项目id> [--out <路径>]\n  gd-wa worldview check --project <项目id>\n  gd-wa art new <切片名> --project <项目id> [--out <路径>]\n  gd-wa art gen <切片名> --project <项目id> [--seed 42] [--provider comfy|dry-run]\n\n示例：\n  gd-wa worldview new demo-lore --project demo-foo\n  # 产物：CWD/projects/demo-foo/WAgent/demo-lore.md\n  gd-wa worldview check --project demo-foo\n  # 一致性检查：术语混用/定义冲突/设定锚点分歧\n  gd-wa art new hero-concept --project demo-foo\n  # 美术需求规格：CWD/projects/demo-foo/WAgent/hero-concept.md\n  gd-wa art gen hero-concept --project demo-foo --seed 42\n  # 参考图生成（ComfyUI）；--seed "42,43,44" 批量筛种\n\n位置：${here}`);
}

function parseArgs(argv) {
  const args = { _: [], project: null, out: null, seeds: null, provider: null, api: null };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === "--project") { args.project = argv[++i]; continue; }
    if (a === "--out") { args.out = argv[++i]; continue; }
    if (a === "--seed") { args.seeds = argv[++i]; continue; }
    if (a === "--provider") { args.provider = argv[++i]; continue; }
    if (a === "--api") { args.api = argv[++i]; continue; }
    if (a === "-h" || a === "--help") { args.help = true; continue; }
    args._.push(a);
  }
  return args;
}

function main() {
  const argv = process.argv.slice(2);
  const args = parseArgs(argv);

  if (args.help || argv.length === 0) { usage(); process.exit(0); }

  const [cmd, action, ...rest] = args._;
  const name = rest[0];
  const supported = "worldview new | worldview check | art new | art gen";
  const unknown = () => {
    console.error(`✗ 未知命令：${[cmd, action, ...rest].filter(Boolean).join(" ")}\n  当前支持：${supported}`);
    usage();
    process.exit(1);
  };

  // worldview check — 一致性检查（v0.2.2）
  if (cmd === "worldview" && action === "check") {
    if (!args.project) { console.error("✗ 缺少 --project <项目id>"); usage(); process.exit(1); }
    // 与 worldview new 默认产物路径对称：--project <项目id> → projects/<项目id>/WAgent/
    const projectDir = isAbsolute(args.project) ? args.project : join("projects", args.project);
    const result = checkProject(projectDir);
    console.log(renderReport(args.project, result));
    const errs = result ? result.issues.filter((i) => i.level === "error") : [];
    process.exit(errs.length > 0 ? 1 : 0);
  }

  // art gen — 参考图生成（v0.2.4）
  if (cmd === "art" && action === "gen") {
    if (!name) { console.error("✗ 缺少 <切片名>"); usage(); process.exit(1); }
    if (!args.project) { console.error("✗ 缺少 --project <项目id>"); usage(); process.exit(1); }
    const seeds = (args.seeds ?? "42").split(",").map((s) => Number(s.trim())).filter((n) => Number.isFinite(n));
    if (seeds.length === 0) { console.error("✗ --seed 参数非法（示例：42 或 42,43,44）"); process.exit(1); }
    if (args.provider && !["comfy", "dry-run"].includes(args.provider)) {
      console.error("✗ --provider 仅支持 comfy | dry-run"); process.exit(1);
    }
    const specPath = isAbsolute(name) ? name : join("projects", args.project, "WAgent", `${name}.md`);
    genArt({ specPath, project: args.project, seeds, outDir: args.out, provider: args.provider, api: args.api })
      .then((r) => {
        console.log(`✅ 参考图已生成：${r.outDir}`);
        console.log(`   provider: ${r.provider}${r.provider === "comfy" ? "（z-image-turbo）" : "（降级，未调 ComfyUI）"}`);
        console.log(`   切片: ${name} · seeds: [${seeds.join(", ")}]`);
        console.log(`   文件: ${r.refs.map((x) => x.file).join(", ")}`);
        for (const n of r.notes) console.log(`   ⚠️ ${n}`);
        console.log(`   元数据: refs.json（可追溯：prompt/seed/model）`);
        if (r.provider === "dry-run") console.log(`   提示: 启动 ComfyUI 后重跑可真实出图`);
      })
      .catch((e) => { console.error(`✗ ${e.message}`); process.exit(1); });
    return;
  }

  // new 类命令：worldview new / art new（共享切片生成）
  const NEW = {
    worldview: { template: "templates/worldview-skeleton.yaml", title: "世界观切片", cmdLabel: "worldview new" },
    art:       { template: "templates/art-spec.yaml",           title: "美术需求规格", cmdLabel: "art new" },
  };
  if (action === "new") {
    const spec = NEW[cmd];
    if (!spec) return unknown();
    if (!name) { console.error("✗ 缺少 <切片名>"); usage(); process.exit(1); }
    if (!args.project) { console.error("✗ 缺少 --project <项目id>"); usage(); process.exit(1); }
    if (!/^[a-z][a-z0-9-]*$/.test(name)) { console.error(`✗ 切片名非法（kebab-case）：${name}`); process.exit(1); }

    // 加载骨架
    const here = dirname(fileURLToPath(import.meta.url));
    const skeletonPath = join(here, "..", spec.template);
    if (!existsSync(skeletonPath)) { console.error(`✗ 骨架文件缺失：${skeletonPath}`); process.exit(1); }
    const skeleton = parseSimpleYaml(readFileSync(skeletonPath, "utf8"));
    if (!skeleton.sections || skeleton.sections.length < 1) {
      console.error(`✗ 骨架结构异常：sections 缺失（${spec.template}）`);
      process.exit(1);
    }

    // 输出路径（与能力声明 output_dir: WAgent 对齐）
    const outRel = args.out ?? join("projects", args.project, "WAgent", `${name}.md`);
    const outAbs = isAbsolute(outRel) ? outRel : join(process.cwd(), outRel);
    if (existsSync(outAbs)) { console.error(`✗ 目标已存在，拒绝覆盖：${outAbs}`); process.exit(1); }

    // 渲染 + 落盘
    const content = renderSlice(skeleton, {
      name,
      project: args.project,
      date: new Date().toISOString().slice(0, 10),
    }, { cmdLabel: spec.cmdLabel, title: spec.title, skeletonFile: spec.template, version: "v0.2.3" });
    mkdirSync(dirname(outAbs), { recursive: true });
    writeFileSync(outAbs, content, "utf8");

    console.log(`✅ ${spec.title}已生成：${outAbs}`);
    console.log(`   骨架版本：v${skeleton.version} · 块数：${skeleton.sections.length}（${skeleton.sections.map((s) => s.en).join(" / ")}）`);
    console.log(`   下一步：编辑内容 → \`gd deliverable add\` 登记 → \`gd task status done\` 回写`);
    return;
  }

  return unknown();
}

main();