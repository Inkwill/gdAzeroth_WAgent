# gd-wa CLI · 使用指南

> v0.2.1 起（check 子命令 v0.2.2）。`gd-wa`（gd- 前缀 + WAgent 缩写）是分控内 CLI，遵循 main@gd 命名规范：硬前缀 `gd-` + 分控代号缩写（wa），三层 `<bin> <能力id> <动作>`。
> 与总控 `gd` 命令无冲突（本工具仅作用于切片生成）。
> **0.5.0 衔接**：本工具默认在本地 `projects/<项目>/WAgent/` 生成切片（本地工作区）；交付时用 `gd deliverable add --deliverable "deliver_wa/xxx|kind|desc"` 登记到需求级 `reqs/<需求id>/deliver_wa/`（或用 `--out` 直接指向需求级路径）。

---

## 安装

```bash
# 仓库根执行（CLI 已全局注册为 `gd-wa`）
npm link             # 全局链接（开发期常用）
# 或一次性执行：
npx gd-wa --help
```

## worldview new — 生成世界观切片骨架

```bash
gd-wa worldview new <切片名> --project <项目id> [--out <路径>]
```

### 参数

| 参数 | 必填 | 说明 |
|------|------|------|
| `<切片名>` | ✅ | kebab-case（小写字母/数字/连字符） |
| `--project <项目id>` | ✅ | 目标项目 id（与总控 `gd project` 一致） |
| `--out <路径>` | ❌ | 输出路径（相对 cwd 或绝对路径）；默认 `projects/<项目id>/WAgent/<切片名>.md` |

### 行为

- 读取 `templates/worldview-skeleton.yaml`（4 块骨架声明）
- 按骨架渲染 Markdown 切片到目标路径
- 拒绝覆盖已存在文件（防止误覆盖已创作内容）
- 拒绝非法切片名（非 kebab-case）

### 切片结构（4 块，对齐骨架声明）

1. **高概念（HIGH-CONCEPT）** —— 一段话核心隐喻与卖点
2. **基调（TONE & FEEL）** —— 视觉 / 叙事张力两维
3. **核心设定骨架（ASPECTS）** —— 世界观 / 文化 / 语言 / 美术 各一行，含自洽锚点
4. **术语表（TERMINOLOGY）** —— 定义 + 禁止混用（一致性检查器消费结构）

### 示例

```bash
# 在 demo-foo 项目下生成 lore-slice 切片
gd-wa worldview new lore-slice --project demo-foo
# 产物：CWD/projects/demo-foo/WAgent/lore-slice.md

# 自定义输出路径
gd-wa worldview new special-lore --project demo-foo --out ./scratch/lore.md
```

### 后续工作流

```bash
# 1. 编辑切片内容（填高概念/设定/术语）
$EDITOR projects/demo-foo/WAgent/lore-slice.md

# 2. 总控侧登记交付（v0.5.0 端到端演练）
gd deliverable add <任务id> --req <需求id> \
  --deliverable "projects/demo-foo/WAgent/lore-slice.md|doc|世界观切片：lore-slice"

# 3. 状态回写
gd task status <任务id> done --req <需求id>
```

## worldview check — 一致性检查（v0.2.2）

```bash
gd-wa worldview check --project <项目id>
```

扫描 `projects/<项目id>/WAgent/*.md` 全部切片，执行两类检查：

### 术语表一致性

| 检查 | 级别 | 说明 |
|------|------|------|
| 同切片内术语重名但定义不同 | ❌ 错误 | 文件内自相矛盾 |
| 跨切片同一术语定义表述不同 | ⚠️ 警告 | 可能补充/矛盾，人工确认 |
| 声明禁止混用的词仍在正文出现 | ❌ 错误 | 报切片 + 行号 |

### 设定矛盾检测（ASPECTS）

| 检查 | 级别 | 说明 |
|------|------|------|
| 同层面自洽锚点表述分歧 | ⚠️ 警告 | 可能互补/矛盾，人工确认 |
| 同切片内同层面多行 | ❌ 错误 | 骨架应为每层面一行 |

### 行为

- 空单元格（骨架未填）一律跳过，不误报
- 术语表声明行本身不触发禁止混用误报
- 输出分级报告；存在 ❌ 错误 → exit 1（可接入 CI / 交付前自检）

### 示例

```bash
# 交付前自检：确认无术语混用、无设定矛盾（仓库根执行）
gd-wa worldview check --project demo-foo
# → 一致性检查：项目 demo-foo
#   切片 2 个：lore-a.md、lore-b.md
#   术语词典 1 条 · 错误 2 · 警告 2
#   ❌ [BANNED_TERM_USED] … 正文第 8 行仍在使用（lore-a.md）
#   ⚠️ [ASPECT_ANCHOR_DIVERGE] …
```

> 演进预留：术语表条目未来可扩展 `同义词` / `上位词` / `相关` 字段，
> 升级路径：受控词表 → 词典 → taxonomy → ontology（见 roadmap v0.2.2）。

## art new — 生成美术需求规格切片（v0.2.3）

```bash
gd-wa art new <切片名> --project <项目id> [--out <路径>]
```

对齐 **art-style** 能力声明（美术风格定位与参考资源）。

### 切片结构（6 块，对齐骨架声明）

1. **需求定位（PURPOSE）** —— 服务对象（场景/角色/道具/UI）+ 交付物类型
2. **风格锚点（STYLE ANCHORS）** —— 风格关键词 / 参考作品 / 色彩倾向 / 氛围基调
3. **美术简报（ART BRIEF）** —— 色彩/光照/材质/构图/笔触 各带自洽锚点
4. **规格（SPEC）** —— 尺寸/数量/格式/分辨率
5. **必备要素（MUST-HAVE）** —— 必须出现的视觉要素
6. **禁忌（FORBIDDEN）** —— 禁止出现的内容（禁忌项+原因，与术语表禁止混用同思路，供一致性检查扩展）

### 示例

```bash
gd-wa art new hero-concept --project demo-foo
# 产物：CWD/projects/demo-foo/WAgent/hero-concept.md
```

> 边界：本命令只生成规格骨架，**不做参考图生成**（→ v0.2.4 参考图管线）；
> 参考资源是“参考”而非最终美术资产，避免越界 PLAgent 原型资产。

## art gen — 生成参考图（v0.2.4）

```bash
gd-wa art gen <切片名> --project <项目id> [--seed 42] [--provider comfy|dry-run]
```

从 art spec 切片组装提示词，调本机 **ComfyUI**（127.0.0.1:8188）真实出图。

### 流程

1. 解析 art spec（PURPOSE / STYLE ANCHORS / ART BRIEF / MUST-HAVE / FORBIDDEN）
2. 组装提示词：正向 = 风格锚点（前置）+ 维度指导 + 必备要素；负向 = 禁忌 + 通用负向
3. 提交 ComfyUI（工作流 `templates/t2i-z-image-v1.json`，Z-Image Turbo 8 步 cfg=1）→ 轮询 → 下载 PNG
4. 落盘 `projects/<项目>/WAgent/<切片>/ref-<seed>.png` + `refs.json`（元数据：prompt/负向/seed/model，可追溯复现）

### 参数

| 参数 | 说明 |
|------|------|
| `--seed 42` | 种子（默认 42）；`--seed "42,43,44"` 批量筛种 |
| `--provider comfy` | 真实生成（默认，探活失败自动降级 dry-run） |
| `--provider dry-run` | 只落 prompt 文本，不调 ComfyUI |
| `--api <url>` | ComfyUI 地址（默认 http://127.0.0.1:8188） |

### 示例

```bash
gd-wa art gen hero-concept --project demo-foo --seed 42
# → 参考图已生成：projects/demo-foo/WAgent/hero-concept/ref-42.png + refs.json

# 批量筛种：3 个种子各出一张挑
 gd-wa art gen hero-concept --project demo-foo --seed "42,43,44"
```

### 已知限制

- Z-Image Turbo（cfg=1）对负向 prompt 不敏感（FORBIDDEN 仍写入负向 + 元数据标注）
- 模型总重约 19G，8G 显存需 ComfyUI 以 `--lowvram` 运行（否则 CUDA OOM）

## slice export — 切片装配导出（v0.2.5）

```bash
gd-wa slice export --project <项目id> [--out <路径>]
```

扫描 `projects/<项目id>/WAgent/*.md` 全部切片，装配为索引 `index.md`（默认输出）：

- **切片清单**：切片名 / 类型（worldview / art-spec）/ 摘要（首 section 正文首行）
- **项目级术语词典**：跨切片汇总全部术语表（含来源切片）

**用途**：其他分控可只读引用此索引——一份文档看全项目表现切片（v0.4.0 直达互调基础）。

### 示例

```bash
gd-wa slice export --project demo-foo
# → 切片索引已导出：projects/demo-foo/WAgent/index.md
#   切片 2 个：demo-lore(worldview)、hero-concept(art-spec)
#   术语词典 1 条（跨切片汇总）
```

> 生成物约定：`index.md` 为导出产物，每次重新生成覆盖；不参与一致性检查（scanSlices 自动排除）。

## narrative new — 生成叙事切片骨架（v0.3.2）

```bash
gd-wa narrative new <切片名> --project <项目id> [--out <路径>]
```

行为同 worldview new（骨架渲染 / 拒绝覆盖 / 拒绝非法名），读 `templates/narrative-skeleton.yaml`（6 块）。

### 切片结构（6 块）

1. **叙事核心（NARRATIVE CORE）** —— 核心冲突 / 主题 / 情感弧线（带自洽锚点）
2. **剧情结构（STRUCTURE）** —— 三幕/章节 + 关键节拍
3. **角色（CHARACTERS）** —— 角色 / 动机 / 弧线
4. **关键事件（EVENTS）** —— 事件 / 触发 / 结果
5. **叙事文本（TEXT）** —— 开场旁白 / 关键台词 / 结局文本
6. **术语表（TERMINOLOGY）** —— 自动纳入一致性检查（A1/A2/A3）与装配导出术语词典

### 复用既有工具链（无需新代码）

- `gd-wa worldview check --project <项目id>` —— 术语表自动纳入一致性检查（禁止混用等）
- `gd-wa slice export --project <项目id>` —— 类型识别为 narrative + 术语词典跨切片汇总

## cultural-language new — 生成文化语言切片骨架（v0.3.3）

```bash
gd-wa cultural-language new <切片名> --project <项目id> [--out <路径>]
```

行为同 worldview new（骨架渲染 / 拒绝覆盖 / 拒绝非法名），读 `templates/cultural-language-skeleton.yaml`（6 块）。

### 切片结构（6 块）

1. **文化核心（CULTURAL CORE）** —— 文明起源 / 价值观 / 社会结构（带自洽锚点）
2. **语言体系（LANGUAGE）** —— 语言风格 / 命名规则 / 口癖
3. **习俗礼仪（CUSTOMS）** —— 习俗 / 场合 / 意义
4. **禁忌戒律（TABOOS）** —— 禁忌项 / 原因 / 后果（与 art-spec FORBIDDEN 同思路）
5. **文化文本（TEXT）** —— 谚语 / 常用语 / 敬语
6. **术语表（TERMINOLOGY）** —— 自动纳入一致性检查与装配导出术语词典

### 复用既有工具链（同 narrative）

- `gd-wa worldview check --project <项目id>` —— 术语表自动纳入一致性检查
- `gd-wa slice export --project <项目id>` —— 类型识别为 cultural-language + 术语词典汇总

## storyboard new — 生成故事板骨架（v0.3.1）

```bash
gd-wa storyboard new <切片名> --project <项目id> [--out <路径>]
```

行为同 worldview new（骨架渲染 / 拒绝覆盖 / 拒绝非法名），读 `templates/storyboard-skeleton.yaml`（3 块：元信息 / 场景示例 / 规则摘要）。

### 切片结构（多场景由用户复制 `## 场景 · start` 块扩展）

- **元信息（META）**：标题 / 简介 / 起始场景 id
- **场景（SCENE）**：每个 `## 场景 · <id>` 块 = 一个 Ink knot——`标题` / `背景图`（引用路径）/ `文案`（代码块）/ `选项`（每行 `文字 -> 目标场景 id`）
- **规则摘要（RULES）**（可选）：胜负判定 / 核心循环

## storyboard render — 故事板 → 单文件 HTML demo（v0.3.1）

```bash
gd-wa storyboard render <切片名> --project <项目id> [--out <路径>]
```

### 行为

1. 读切片 → 解析场景
2. 转 Ink 源码（顶层 `-> 起始场景` + 每个场景一个 knot + 选项 divert）
3. 调 inkjs CLI 编译 → BOM-free JSON
4. 生成单文件 HTML（内嵌 inkjs runtime 128KB + JSON + 启动脚本，Blob URL 模式）

### 产出

- 默认 `projects/<项目id>/WAgent/<切片名>.html`——单文件，可本地双击打开或部署到任意静态服务器
- 图片仅引用路径（不打包、不复制）

### 已知限制

- 正文/选项含 `${` 会与 Ink 插值语法冲突（编译报错含友好提示，请改写为文字描述）
- MVP 纯线性 + 选项跳转；变量/分支/状态后续版本

## 不做的事（边界）

- ❌ 不生成内容（高概念/设定/术语是创作产物，模板只生成空骨架）
- ❌ 不与总控 `gd` 命令冲突（命名硬约束 `gd-` 前缀，但本工具走 npm bin，不污染总控 CLI）
- ❌ 不做美术参考图生成（→ v0.2.4）
- ❌ 不做切片装配/索引（→ v0.2.5）
- ❌ storyboard 不做变量/分支/存档（→ rule-design 主能力领地，后续看情况）

## 骨架源（机器可读）

`templates/worldview-skeleton.yaml` 是骨架的机器可读定义（slice_type/version/sections[*].template）。CLI 渲染时直接消费；后续 v0.2.2 一致性检查器可读取同一文件校验切片结构。