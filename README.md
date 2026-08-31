# gdAzeroth_WAgent — gd 套件 · WAgent（世界 · 概念层）

> 设计游戏的"概念层"——定义**世界是什么**（世界观 / 文化 / 资产）与**世界怎么运作**（玩法规则 / 核心循环）。
>
> 三隐喻体系（v0.5.0）：**DAgent = 规律** · **WAgent = 世界** · **PLAgent = 能动性**；总控 = 治理（Govern）。
> 与旧定位对比：旧版为"外在感性包装"（肌肤），仅覆盖呈现层；0.5.0 起扩展为整个概念层，玩法规则设计划归此处。

## 身份

| 项 | 值 |
|----|-----|
| 代号 | WAgent（World Agent） |
| 拟人 | 世界 |
| 逻辑层面 | 概念层（含玩法规则） |
| 仓库 | `git@github.com:Inkwill/gdAzeroth_WAgent.git` |
| 注册 | 总控布局注册（`gd.layout.yaml`，经 `~/.gd/gdmain.yaml` 引导） |
| 版本 | 见 `.pi/APPEND_SYSTEM.md`（当前版本：0.2.0） |

## 在 gd 套件中的定位

```
总控 gdMain（治理 Govern）—— 只做登记/匹配/状态/验收，不干预设计
  └─ 三隐喻：DAgent=规律（规律层）/ WAgent=世界（概念层）/ PLAgent=能动性（游戏性呈现）

治理 Govern（唯一入口）
   │ 接口契约（能力声明 capabilities.yaml + 控制协议）
   ▼
本分控（黑盒交付 · 设计自治）
   ▼
reqs/<需求id>/deliver_wa/   ← 概念层切片（display + rule）需求级交付目录
```

- **总控只管"要什么 → 该提供什么"**；怎么给、给什么样的算合适，由本分控自行判断（黑盒交付，总控不干预设计）。
- 本分控与 DAgent（规律）、PLAgent（能动性）并列，按**逻辑层面**切分，非功能模块。
- 协作规范（SOP / 协议 / mail / 路径解析）单一入口：`.pi/skills/gd-producer/SKILL.md`。

## 管辖范围

**含：**
- 世界观 / 叙事文本 / 文化语言
- 美术风格 / 美术需求与参考资源
- **玩法规则**：核心循环 / 玩家行为框架 / 胜负判定（不含具体数值公式）
- **图文演示游戏设计**（storyboard，文字+图片的纯演示型游戏——单文件 HTML demo，按需求驱动，非项目默认交付）

**不含：**
- UI 交互（归 PLAgent）
- 具体数值公式与平衡曲线（归 DAgent）
- 玩家具体操作与交互细节（归 PLAgent / DAgent）

## 产出与协作

- **切片输出**：概念层切片（display + rule）→ 需求级交付目录 `reqs/<需求id>/deliver_wa/`
  - display：世界观/叙事/文化/美术呈现层
  - rule：玩法规则（`deliver_wa/rules/`，核心循环 / 玩家行为框架 / 胜负判定）
  - storyboard：图文演示游戏（`deliver_wa/<name>.html`，按需求驱动整合 display + rule）
- **消费锚点**：`assets/manifest.yaml`（资源清单，供 PLAgent 桥收录；无实素材时标 `placeholder: true`）
- **直达互调**：切片可被其他分控按需**只读**引用（DAgent 引用 display + rule 作数值建模输入；PLAgent 引用 display + rule + storyboard 作原型资源与规则来源），无需总控中转
- **独立演进**：本仓库自主开发，通过接口契约与总控连接；**无固定依赖**，按需求驱动消费链

---

# 能力与工具（本仓库）

一套通用、可扩展的 AI 辅助**游戏概念层设计**的开发基础设施（世界是什么 + 怎么运作），用于更智能化进行：

- 游戏世界观架构（display）
- 玩法规则设计：核心循环 / 玩家行为框架 / 胜负判定（rule）
- 角色、场景设定、任务、剧情、包装等设计（display）
- 生成美术需求及参考图与调优（display）
- 图文演示游戏设计（storyboard，按需求驱动）

覆盖概念层全流程：世界观架构与设定文档 / 角色·场景·阵营·文化设定 / 叙事与剧情包装 / 玩法规则（核心循环 / 行为框架 / 胜负判定）/ 文字规则集整合 / 美术需求规格与参考图生成。

## 快速开始

- **能力工具链 CLI**：`gd-wa worldview new/check · art new/gen · slice export …`（详见 `docs/cli.md`）
- **单测**：`npm test`
- **版本路线图**：`roadmap.md`（工作视图）；历史明细 `archive/version-history.md`
- 当前里程碑：v0.1.0 契约 ✅ · v0.2.0 能力工具链 ✅（v0.2.1-v0.2.5）· **下一步 v0.3.0 能力深化**

---

# 文档导航（30 秒定位）

| 文档 | 路径 | 一句话 |
|------|------|--------|
| 协作规范（单一入口） | gdMain `skills/gd-producer/SKILL.md`（经 `.pi/settings.json` 引用） | 任务触发时加载：铁律 + 五步法 + 高频命令 |
| 任务处理 SOP | gdMain `skills/gd-producer/reference/sop.md` | 感知→认领→处理→登记→回写全流程与检查点（0.5.0 认领制） |
| 控制协议（gd CLI） | gdMain `skills/gd-producer/reference/protocol.md` | 分控高频指令、参数语义与边界 |
| mail 感知层协议 | gdMain `skills/gd-producer/reference/mail-protocol.md` | 与总控的通知/澄清通道及边界 |
| 路径解析 | gdMain `skills/gd-producer/reference/layout.md` | 引导→布局→task-list 认领→产出→跨分控引用 |
| 渐进式披露规范 | `.pi/skills/gd-producer/reference/progressive-disclosure.md` | 本文档与 AGENTS.md 的分层写作规范 |
| 提交规范 | pi-commit 扩展（git commit 时自动注入） | 规范源 ~/.pi/agent/extensions/pi-commit/COMMITTING.md |
| 版本号 | `.pi/APPEND_SYSTEM.md` | 当前版本（当前：0.2.0） |
| 能力声明 | `capabilities.yaml` | 接口契约 0.4.6 自持声明（已落盘；display-design / rule-design / storyboard-design 三主能力 + display 子能力） |
| 能力工具链 CLI | `docs/cli.md` | `gd-wa worldview new/check · art new/gen · narrative new · cultural-language new · slice export · storyboard new/render …` 切片生成 / 一致性检查 / 美术规格 / 参考图 / 叙事 / 文化语言 / 装配导出 / 图文演示游戏 |
| 生图实战手册 | `docs/artgen-playbook.md` | ComfyUI 生图方法论：调用链/环境前置/排障/prompt 工程/筛种 |
| 立项书撰写手册 | `docs/l0-proposal-playbook.md` | 立项书方法论 v1：10 章结构/三重使命/逐章要点/验收自检/常见坑（案例：T-gt-01 重构版） |
