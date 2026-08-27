# 版本路线图 · Roadmap

> gdAzeroth (WAgent) 自身的版本演进规划（肌肤 · 外在感性包装）。
> V1 双层版本体系下，本文件是 **Azeroth** 的路线图；gdMain 路线图见其 `blueprint/roadmap.md`。
> 版本号单一事实源：仓库根 `VERSION`（当前登记版号以 `VERSION` 为准，本文件只列规划与进度）。
> 目录定位：本文件属 **docs/**（工程事实层——演进计划/进度）；**blueprint/** 为设计意图层（身份与语义），见 `blueprint/README.md`。

---

## 版本速览

| 版本 | 主题 | 状态 | 关键交付 |
|------|------|------|----------|
| **v0.1.0** | 契约落地 · 能力声明自持 | ✅ 已完成 | `capabilities.yaml` 自持落盘 + 校验通过 + 轻量接包演练全流程（无残留） |
| **v0.2.0** | 能力工具链初版 | ✅ 已完成 | 世界观工具链 + 美术参考管线（v0.2.1-v0.2.5 全部落地） |
| **v0.3.0** | 能力深化 · 跨分控互调 | ⏳ 规划中 | 叙事/文化语言/UI 美学落地 + PLAgent 直达引用 |
| **v0.4.0** | 里程碑对齐 🏁 | ⏳ 目标 | 能力全量可用 + 对齐 gdMain v0.5.0 |
| **v0.5.0** | 端到端可交付 · 接包闭环 | ⏳ 后推待命 | 真实任务包处理闭环 + mail 感知实战 + 三切片汇聚就绪（由原 v0.2.0 后推，对齐总控 0.4.8 发布节奏） |

> 🎯 **当前所在**：v0.1.0 ✅ → v0.2.0 ✅ 工具链完成（v0.2.1-v0.2.5）→ **v0.3.0 能力深化 · 跨分控互调（规划中）** → …

---

## 背景与定位

**我是谁**：WAgent（肌肤 · 外在感性包装）——在文化、语言、美术等玩家可感知层面，建构"统一自洽"的游戏世界。

**管辖**：世界观 / 叙事文本 / 文化语言 / 美术风格与参考资源 / 音频 / UI 美学部分。
**不管辖**：UI 交互（PLAgent）、数值逻辑（DAgent）。

**当前差距**（对照 gdMain roadmap 分控侧待办）：

| 差距项 | 现状 |
|--------|------|
| 能力声明自持 | 仓库根无 `capabilities.yaml`（总控 `blueprint/agents/` 为遗留同步副本）→ 0.4.7 契约检查将对 azeroth 报错 |
| 协作文档（AGENTS/README/skill） | ✅ 已就位 |
| SOP 接包能力 | ✅ 规范就位，未实战验证 |
| 能力工具链 | 5 项能力声明全标 stable 但工具链零实现（README 自述"初始框架"） |
| 版本登记 | manifest 中 azeroth = 0.0.0（forge=0.4.0，greymaze=0.4.5），三分控中落后 |

---

## v0.1.0 — 契约落地（✅ 已完成 · 2026-08-27）

**目标**：补硬缺口——能力声明自持落盘并通过机器校验，SOP 接包全流程实战跑通一次。

| # | 内容 | 可验收 |
|---|------|--------|
| 1 | `capabilities.yaml` 自持落盘仓库根（基线对齐总控副本，规范 v1 约束） | 文件就位；`gd agent capabilities azeroth --check` 通过（exit 0） |
| 2 | 契约一致性核对：capabilities ↔ manifest（agent id / output_dir / capabilities_path） | 无不一致项；`gd agent capabilities azeroth` 概览正常 |
| 3 | 轻量接包演练：建临时项目 → 需求 → 任务 → 分发 → 本分控处理产出 → `gd deliverable add` → `gd task status` 回写 → `req check` → 清理 | 全流程跑通；演练数据无残留 |
| 4 | `VERSION` 登记推进（0.0.0 → 0.1.0） | ✅ VERSION = 0.1.0 |

**验收结果（2026-08-27）**：

- `capabilities.yaml` 自持落盘（基线对齐总控副本，updated 2026-08-27）；`gd agent capabilities azeroth --check` exit 0，确认读取自持文件（`C:\Users\inkse\gdAzeroth_WAgent\capabilities.yaml`）
- 契约一致性核对通过：agent id / output_dir（WAgent）/ capabilities_path 均匹配
- 轻量接包演练全流程跑通（demo-wsim）：project new → req new → task gen（v2 契约包）→ task dispatch → 产出 `WAgent/worldview-slice.md` → `gd deliverable add`（kind=doc）→ in_progress → done（需求自动派生 review）→ `req check` 通过 → req/project 清理，**无残留**
- 演练附带验证：状态机拦截非法流转（dispatched 直跳 done 被拒，符合 0.3.0 协议）
- 待总控侧同步：manifest.yaml 中 azeroth version 登记（0.0.0 → 0.1.0，总控维护）

**验收线**：✅ 契约健康、SOP 实战可用、无残留。

## v0.2.0 — 能力工具链初版（✅ 已完成 · 2026-08-27）

> ⚠️ 由原 v0.3.0 前移（版本重排 2026-08-27）：不依赖总控的自主工作提前，端到端（原 v0.2.0）后推至 v0.5.0。

**目标**：优先落地独立能力（worldview-design、art-style）的工具链，让能力声明"可声明即可用"。

- **世界观构建工具链**：世界观架构模板 / 设定文档骨架 / 一致性检查（术语表、设定矛盾检测）
- **美术参考资源管线**：美术需求规格模板 + 参考图生成与调优

> 完成路线：v0.2.1 骨架模板 → v0.2.2 一致性检查器 → v0.2.3 art spec → v0.2.4 参考图管线（真实出图 ✅）→ v0.2.5 装配导出。

### v0.2.1 — 世界观切片骨架模板（✅ 已完成 · 2026-08-27）

**目标**：把世界观切片产出从"自由 Markdown"固化为"结构化模板生成"——为后续 0.2.2 一致性检查器、0.2.5 装配导出铺路。

**交付**：

| # | 内容 | 可验收 |
|---|------|--------|
| 1 | `templates/worldview-skeleton.yaml`（4 块骨架声明，机器可读） | 文件存在；解析为 4 sections |
| 2 | `tools/gd-wa.mjs`（CLI 入口 + 极简 YAML 解析 + 切片渲染） | `gd-wa worldview new …` 可执行 |
| 3 | `tests/gd-wa-worldview.test.mjs`（5 项单测：骨架存在/结构/非法名/覆盖/未知命令） | `npm test` 5/5 绿 |
| 4 | `docs/cli.md`（CLI 使用指南） | 文档存在 |
| 5 | `package.json`（`bin: gd-wa`，npm test 脚本） | `npm link` 后 `gd-wa` 可用 |
| 6 | 文档对齐（README 快速开始/文档导航 + `.gitignore` 补 `projects/`） | 文档与实现一致 |
| 7 | CLI 演示：生成 1 个真实骨架产物并清理 | 产物结构完整（4 块标题 + 表头） |

**设计要点**：

- **命名规范**（main@gd 即时确认）：硬约束 `gd-` 前缀 + 分控代号缩写（wa），三层 `<gd-wa> <能力id> <动作>`
- **骨架结构**：4 块——高概念 / 基调 / 核心设定骨架 / 术语表
- **模板引擎**：极简 YAML 解析 + 字符串拼接，无重型依赖（风险≈0）
- **演练策略**：本版不走端到端演练（0.2.3 后统一走一遍）
- **CLI 暂不登记** gdMain manifest：待 0.4.2 控制协议统一聚合

**验收线**：✅ `npm test` 5/5；✅ CLI 演示产物结构完整；✅ 命名规范已 main@gd 确认。

### v0.2.2 — 一致性检查器（✅ 已完成 · 2026-08-27）

**定位**：给世界观切片的“命名规范与设定自洽”装自动检查岗——是 ontology 工程最轻量的前置形态（受控词表维护），**不引入 OWL/RDF 等重型形式化体系**（延续 v0.2.1 无重型依赖原则）。

**检查项**（全部落地）：

- 术语表一致性：
  - 同切片内术语重名但定义不同 → ❌ 错误（TERM_DUP_DEF）
  - 跨切片同一术语定义归一化后不同 → ⚠️ 警告（TERM_DEF_DIVERGE）
  - 禁止混用词仍在正文出现 → ❌ 错误（BANNED_TERM_USED，报切片+行号）
- 设定矛盾检测：
  - 同层面自洽锚点表述分歧 → ⚠️ 警告（ASPECT_ANCHOR_DIVERGE）
  - 同切片内同层面多行 → ❌ 错误（ASPECT_DUP_LEVEL）

**输出**：分级报告（✅ 通过 / ⚠️ 警告 / ❌ 错误+定位）；存在 ❌ → exit 1（可接入 CI / 交付前自检）

**交付**：

| # | 内容 | 可验收 |
|---|------|--------|
| 1 | `tools/check.mjs`（检查模块：表格/切片解析 + 5 项检查 + 报告渲染） | 文件存在；`checkProject()` 可调用 |
| 2 | `gd-wa worldview check --project <项目id>`（与 new 产物路径对称） | 空骨架通过；违规 exit 1 |
| 3 | `tests/gd-wa-check.test.mjs`（9 项单测：通过/冲突/混用/误报豁免/锚点/空骨架/无切片） | `npm test` 14/14 绿 |
| 4 | `docs/cli.md` check 章节 | 文档存在 |

**验收结果（2026-08-27）**：

- `npm test` 14/14 全绿（新增 9 项 + 原有 5 项）
- 端到端冒烟：`worldview new` 生成 2 切片 → 填充术语/正文/锚点 → `worldview check` 检出 2 ❌（禁止混用 ×2，含行号）+ 2 ⚠️（定义分歧 + 锚点分歧），exit 1；空骨架不误报；演示数据已清理
- 设计要点：空单元格一律跳过（骨架未填不误报）；术语表声明行不触发混用误报；归一化比对（去空白/标点/全角差异）

**演进预留（本版未做）**：

- 术语表条目字段可扩展：`同义词`（等价）/ `上位词`（分类）/ `相关`（关系）——后续可让混用检测更聪明
- 升级路径：受控词表（术语表）→ 词典（+同义词/上位词）→ 分类体系 taxonomy（概念层级）→ ontology（+关系+约束，可推理）→ 如需跨分控共享设定语义/机器推理，届时启用
- 术语词典（检查器的副产物）即未来 ontology 工程的种子数据

### v0.2.3 — art spec 模板（✅ 已完成 · 2026-08-27）

**目标**：美术需求规格模板（对齐 art-style 能力声明），延续“骨架机器可读 + 自洽锚点 + 禁忌表”设计理念。

**交付**：

| # | 内容 | 可验收 |
|---|------|--------|
| 1 | `templates/art-spec.yaml`（6 块骨架：PURPOSE / STYLE ANCHORS / ART BRIEF / SPEC / MUST-HAVE / FORBIDDEN） | 文件存在；解析为 6 sections |
| 2 | `gd-wa art new <切片名> --project <项目id>`（renderSlice 泛化，worldview/art 共用） | 产物标题“美术需求规格”、slice_type=art-spec、6 块结构 |
| 3 | `tests/gd-wa-art.test.mjs`（5 项单测：骨架存在/6 块产物/类型/非法名/覆盖） | `npm test` 19/19 绿 |
| 4 | `docs/cli.md` art 章节 | 文档存在 |

**设计要点**：

- ART BRIEF 各维度带“自洽锚点”列（延续 ASPECTS 锚点理念，供一致性检查）
- FORBIDDEN 禁忌表（禁忌项|原因）与术语表“禁止混用”同思路，为检查器扩展铺路
- 边界明确：只生成规格骨架，**不做参考图生成**（→ v0.2.4）；参考资源≠最终美术资产，避免越界 PLAgent 原型资产
- 产出路径与能力声明 output_dir: WAgent 对齐

**验收线**：✅ `npm test` 19/19；✅ CLI 冒烟产物 6 块结构完整；✅ 演示数据无残留。

### v0.2.4 — 参考图管线（✅ 已完成 · 2026-08-27）

**目标**：art spec → 提示词工程化 → 本机 ComfyUI 真实出图，产出可追溯参考图（参考资源，非最终美术资产）。

**交付**：

| # | 内容 | 可验收 |
|---|------|--------|
| 1 | `templates/t2i-z-image-v1.json`（v0.3→v1 转换生成，10 节点 Z-Image Turbo 工作流） | 可 POST /prompt |
| 2 | `tools/parse-md.mjs`（抽公共 Markdown 解析：section + 表格 + 行号） | 可解析切片 |
| 3 | `tools/prompt.mjs`（art spec → 正/负提示词，风格前置 + FORBIDDEN 转负向） | 组装正确 |
| 4 | `tools/artgen.mjs`（provider 抽象：comfy 真实生成 / dry-run 降级 + refs.json 元数据） | 全链路可跑 |
| 5 | `gd-wa art gen <切片名> --project <项目id> [--seed] [--provider] [--api]` | CLI 可用 |
| 6 | `tests/gd-wa-gen.test.mjs`（7 项单测） | `npm test` 26/26 绿 |
| 7 | `docs/cli.md` art gen 章节 | 文档存在 |

**验收结果（2026-08-27）**：

- `npm test` 26/26 全绿（新增 7 项：解析/正向前置/负向禁忌/dry-run 全流程/探活降级/缺失报错/CLI 报错）
- 端到端：art new → 填充 → art gen 提交 ComfyUI 成功（prompt_id 返回、执行链路通）
- **真实出图 ✅（--lowvram 后）**：模型总重 19.3G（z_image_turbo_bf16 11.5G + qwen_3_4b 7.5G + ae 0.3G）远超 8G 显存，默认模式 CUDA OOM → 以 `--lowvram` 重启 ComfyUI 后端（Start-Process 后台，同 extra-model-paths-config）→ `art gen --seed 42` 一次通过：`ref-42.png`（1.39MB）+ `refs.json`（含 prompt/负向/seed/prompt_id/model）
- 演示数据已清理；ComfyUI 现以 `--lowvram` 运行中（桌面版 UI 若断连需重连/重开）
- 降级保障：dry-run 模式不依赖 ComfyUI，管线全流程可验证可交付

**设计要点**：

- Prompt 工程对齐 Z-Image Turbo（风格关键词前置 + 5 要素法，comfyui-t2i skill §7）
- FORBIDDEN 禁忌 → 负向 prompt（cfg=1 时不生效，notes + 元数据标注，双写策略留演进）
- refs.json 记录 prompt/负向/seed/model/prompt_id，可追溯可复现（批量筛种 → 挑优）
- 产出边界：参考图是“参考资源”非最终美术资产，避免越界 PLAgent 原型资产
- 无重型依赖：node fetch 直调 ComfyUI API（不依赖 python/requests）

**待推进**：批量筛种（`--seed "42,43,44"`）实战验证；FORBIDDEN 禁忌在 Turbo 模型下不生效的进阶处理（双写策略）。

**验收线**：✅ 管线全链路可跑；✅ 真实 PNG 出图（--lowvram 环境）。

### v0.2.5 — 切片装配导出（✅ 已完成 · 2026-08-27）

**目标**：多切片装配为项目级索引文档（消费 skeleton.yaml 的结构化定义），供其他分控只读引用。

**交付**：

| # | 内容 | 可验收 |
|---|------|--------|
| 1 | `tools/export.mjs`（scanSlices 扫描/类型识别/摘要提取 + renderIndex 装配 + 术语词典汇总） | 可导出 index.md |
| 2 | `gd-wa slice export --project <项目id> [--out]`（默认 projects/<项目>/WAgent/index.md） | CLI 可用 |
| 3 | `tests/gd-wa-export.test.mjs`（5 项单测） | `npm test` 31/31 绿 |
| 4 | `docs/cli.md` slice export 章节 | 文档存在 |

**设计要点**：

- 切片类型识别：切片头 meta `切片类型：xxx`（worldview / art-spec）
- 摘要提取：首 section（high-concept / PURPOSE）正文首行，占位符 `<...>` 自动跳过
- 术语词典：跨切片汇总（一致性检查的副产物，未来 ontology 种子）
- index.md 为生成物，scanSlices 自动排除自身；不参与一致性检查

**验收结果（2026-08-27）**：

- `npm test` 31/31 全绿（新增 5 项：类型/摘要识别、装配清单+术语词典、空术语表提示、CLI 真实流程、无切片提示）
- 真实冒烟：仓库 demo 项目（demo-lore worldview + hero-concept art-spec）→ `slice export` 装配 index.md：清单 2 切片 + 术语词典 1 条

**验收线**：✅ 装配导出可用；✅ 术语词典跨切片汇总；✅ 无残留。

## v0.3.0 — 能力深化 · 跨分控互调（⏳ 规划中）

> ⚠️ 由原 v0.4.0 前移（版本重排 2026-08-27）。

- narrative-design、cultural-language、ui-aesthetic 落地（依赖 worldview 先行）
- 与 PLAgent **直达互调**落地：表现素材可被原型按需引用（无需总控中转）
- 音频 / UI 美学的风格指导产出物标准化

## v0.4.0 — 里程碑对齐 🏁（⏳ 目标）

> ⚠️ 由原 v0.5.0 前移（版本重排 2026-08-27）。

- 5 项能力全部"可声明即可用"（声明不再虚标）
- README / 能力声明 / 版本号全链路对齐
- 支持 gdMain v0.5.0 里程碑验收（三切片汇聚落盘）

## v0.5.0 — 端到端可交付 · 接包闭环（⏳ 后推待命 · 依赖总控）

> ⚠️ **由原 v0.2.0 后推至此**（版本重排 2026-08-27）：端到端闭环依赖总控 0.4.8（端到端演练 + tag）与真实派单，后推对齐总控发布节奏；总控 0.4.8 发布后即可启动。

**目标**：真实任务包处理闭环（非演练），mail 感知层实战，三切片汇聚就绪。

**已完成（2026-08-27）**：

- mail 感知层就绪验证：身份 azeroth@gd 在线、通讯录 4 联系人就位（含 main@gd）、收件箱可查；历史邮件（0.4.9 时代）链路完好
- 切片产出路径验证：`projects/<项目>/WAgent/` 产出 + 登记路径在 v0.1.0 演练中实测可用

**待推进（依赖总控）**：

- 真实任务处理：需总控真实派单（当前无在途任务）
- question 澄清通道实战：随真实任务触发（先澄清后拒绝）
- gdMain 0.4.8 端到端演练参与（总控未发布，规划中）

| # | 内容 | 可验收 |
|---|------|--------|
| 1 | 真实任务处理：收 review_request 邮件 → 拉任务包 → 处理 → 登记 → 回写 | 一次真实需求闭环完成 |
| 2 | mail 感知闭环实战（review_request 收件 / question 澄清通道） | 通知-澄清闭环可用 |
| 3 | 三切片汇聚就绪：`projects/<项目>/WAgent/` 产出规范落盘并被他控只读引用 | 切片可被引用 |
| 4 | 参与 gdMain 0.4.8 端到端演练（若总控就绪） | 演练通过、无残留 |

**验收线**：真实闭环跑通、演练通过、无残留。

---

## 讨论待办（v0.2.0 拆分）

- [x] v0.2.0 拆分草案已出（见下方章节）——逐项讨论中
- [x] v0.2.1（世界观骨架模板）讨论完成+实施完成（2026-08-27）
- [x] v0.2.2（一致性检查器）实施完成（2026-08-27）
- [x] v0.2.3（art spec 模板）实施完成（2026-08-27）
- [x] v0.2.4（参考图管线）实施完成（2026-08-27；真实出图 ✅ 经 --lowvram 环境）
- [x] v0.2.5（切片装配导出）实施完成（2026-08-27）

## 依赖与风险

| 项 | 说明 |
|----|------|
| ⚠️ 顺序依赖 | v0.1.0 必须先行——0.4.7 契约检查会因缺 capabilities.yaml 报错，拖累总控健康度 |
| ⏸ 等待总控 | gdMain 0.4.7（contract check）/ 0.4.8（端到端演练）未发布；v0.5.0（原 v0.2.0 端到端）依赖 0.4.8 发布 + 真实派单 |
| 🎨 能力独特性 | 美术参考图生成是"参考资源"而非最终美术资产——管线要明确边界，避免越界 PLAgent 原型资产 |
| 🤝 协作依赖 | v0.3.0 直达互调需 PLAgent 侧配合（greymaze bridge-spec §4.5，触发条件待满足） |

---

## 变更记录

| 日期 | 变更 |
|------|------|
| 2026-08-27 | 首版落盘：v0.1.0 → v0.5.0 规划（粗略版）；v0.1.0 启动 |
| 2026-08-27 | v0.1.0 完成：capabilities.yaml 自持 + 校验通过 + 接包演练无残留；VERSION → 0.1.0；v0.2.0 转进行中（mail 感知就绪，待总控派单/0.4.8）；v0.3.0 拆分草案出 |
| 2026-08-27 | skill 多副本漂移问题提出 → main@gd 实施方案 A：单一事实源（gdMain `skills/`）+ 4 仓库 `.pi/settings.json` 引用，`.pi/` 策略统一为不入库；我仓库验证通过 |
| 2026-08-27 | v0.2.1 世界观切片骨架模板完成（原 v0.3.1 号段）：4 块骨架 + `gd-wa` CLI（命名规范 main 确认：gd- 前缀 + wa 缩写）+ 5/5 单测 + `docs/cli.md` + `package.json` bin 注册；演练延后到 0.2.3 后 |
| 2026-08-27 | **版本重排（对齐总控节奏）**：原 v0.2.0（端到端，依赖总控 0.4.8）后推为 v0.5.0；原 v0.3.x（工具链，自主可推进）前移为 v0.2.x；原 v0.4.0→v0.3.0；原 v0.5.0→v0.4.0。VERSION 维持 0.1.0（v0.1.0 未变）。同步更新 docs/cli.md、README、skeleton.yaml、gd-wa.mjs、单测注释 |
| 2026-08-27 | v0.2.2 一致性检查器完成：`tools/check.mjs` + `gd-wa worldview check`（与 new 路径对称）+ 9 项新单测（`npm test` 14/14）+ `docs/cli.md` check 章节；端到端冒烟检出 2❌/2⚠️ 带行号，空骨架不误报；讨论确认定位：ontology 工程最轻量前置形态（不引入 OWL/RDF，预留同义词/上位词演进路径） |
| 2026-08-27 | v0.2.3 art spec 模板完成：`templates/art-spec.yaml`（6 块：PURPOSE/STYLE ANCHORS/ART BRIEF/SPEC/MUST-HAVE/FORBIDDEN）+ `gd-wa art new`（renderSlice 泛化，worldview/art 共用）+ 5 项新单测（`npm test` 19/19）+ `docs/cli.md` art 章节；ART BRIEF 带自洽锚点列、FORBIDDEN 禁忌表为检查器扩展铺路；边界：不做参考图生成（→ v0.2.4） |
| 2026-08-27 | v0.2.4 参考图管线主体完成：`templates/t2i-z-image-v1.json`（v0.3→v1 转换）+ `tools/parse-md.mjs`（抽公共解析）+ `tools/prompt.mjs`（art spec→正/负提示词）+ `tools/artgen.mjs`（provider：comfy 直调 fetch/dry-run 降级 + refs.json）+ `gd-wa art gen` + 7 项新单测（`npm test` 26/26）；API 链路验证通（提交/执行）；真实出图阻塞于显存：模型 19.3G vs 8G 显存 CUDA OOM，需 ComfyUI `--lowvram` 重启后联调；dry-run 兜底可交付 |
| 2026-08-27 | v0.2.4 真实出图联调 ✅：ComfyUI 以 `--lowvram` 重启（Start-Process 后台，日志 comfy-lowvram*.log 已 gitignore）→ `art gen --seed 42` 一次通过，`ref-42.png`（1.39MB）+ refs.json 元数据完整；演示清理；ComfyUI 现以 lowvram 模式运行（桌面版 UI 断连需重连） |
| 2026-08-27 | 方法论沉淀：新增 `docs/artgen-playbook.md`（生图实战手册——调用链/环境前置/排障手册含 6 个实测坑/prompt 工程/可追溯筛种/边界/演进），README 文档导航同步 |
| 2026-08-27 | v0.2.5 切片装配导出完成：`tools/export.mjs`（scanSlices/renderIndex/术语词典汇总）+ `gd-wa slice export` + 5 项新单测（`npm test` 31/31）+ docs/cli.md 章节；冒烟装配 demo 项目 2 切片+1 术语；**v0.2.0 全部子版本完成 → VERSION/package.json → 0.2.0；v0.2.0 转 ✅ 已完成** |
