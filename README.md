# gdAzeroth_WAgent — gd 套件 · 分控 B（肌肤 · 外在感性包装）

> 在文化、语言、美术等玩家可感知层面，建构"统一自洽"的游戏世界。

## 身份

| 项 | 值 |
|----|-----|
| 代号 | WAgent |
| 拟人 | 肌肤 |
| 逻辑层面 | 外在感性包装 |
| 仓库 | `git@github.com:Inkwill/gdAzeroth_WAgent.git` |
| 注册 | 总控布局注册（`gd.layout.yaml`，经 `~/.gd/gdmain.yaml` 引导） |
| 版本 | 见 `VERSION`（单一事实源） |

## 在 gd 套件中的定位

```
总控 gdMain（大脑 + 唯一入口）
   │ 接口契约（能力声明 capabilities.yaml + 控制协议）
   ▼
本分控（黑盒交付 · 信任专家）
   ▼
projects/<项目>/WAgent/   ← 世界观与表现切片（共享工作区）
```

- **总控只管"要什么 → 该提供什么"**；怎么给、给什么样的算合适，由本分控自行判断。
- 本分控与 DAgent（骨架）、PLAgent（能动性）并列，按**逻辑层面**切分，非功能模块。
- 协作规范（SOP / 协议 / mail / 路径解析）单一入口：`.pi/skills/gd-producer/SKILL.md`。

## 管辖范围

**含：**
- 世界观 / 叙事文本 / 文化语言
- 美术风格 / 美术需求与参考资源
- 音频
- UI 的**美学部分**

**不含：**
- UI 交互（归 PLAgent）
- 数值逻辑（归 DAgent）

## 产出与协作

- **切片输出**：世界观与表现内容设计（世界观切片）→ 共享工作区 `projects/<项目>/WAgent/`
- **直达互调**：表现素材可被其他分控按需**只读**引用，无需总控中转
- **独立演进**：本仓库自主开发，通过接口契约与总控连接

---

# 能力与工具（本仓库）

一套通用、可扩展的 AI 辅助**游戏世界观构建及美术参考资源生成**的开发基础设施，用于更智能化进行：

- 游戏世界观架构
- 角色、场景设定
- 任务、剧情、包装等设计
- 生成美术需求及参考图与调优

覆盖"感性包装"全流程：世界观架构与设定文档 / 角色·场景·阵营·文化设定 / 叙事与剧情包装 / 美术需求规格与参考图生成 / 音频·UI 美学的风格指导。

## 快速开始

- **能力工具链 CLI**：`gd-wa worldview new/check · art new/gen · slice export …`（详见 `docs/cli.md`）
- **单测**：`npm test`
- **版本路线图**：`docs/roadmap.md`
- 当前里程碑：v0.1.0 契约 ✅ · **v0.2.0 能力工具链 ✅（v0.2.1-v0.2.5）**

---

# 文档导航（30 秒定位）

| 文档 | 路径 | 一句话 |
|------|------|--------|
| 协作规范（单一入口） | `.pi/skills/gd-producer/SKILL.md` | 任务触发时加载：铁律 + 五步法 + 高频命令 |
| 任务处理 SOP | `.pi/skills/gd-producer/reference/sop.md` | 感知→拉取→处理→登记→回写全流程与检查点 |
| 控制协议（gd CLI） | `.pi/skills/gd-producer/reference/protocol.md` | 分控高频指令、参数语义与边界 |
| mail 感知层协议 | `.pi/skills/gd-producer/reference/mail-protocol.md` | 与总控的通知/澄清通道及边界 |
| 路径解析 | `.pi/skills/gd-producer/reference/layout.md` | 引导→布局→任务包→产出→跨分控引用 |
| 渐进式披露规范 | `.pi/skills/gd-producer/reference/progressive-disclosure.md` | 本文档与 AGENTS.md 的分层写作规范 |
| 提交规范（速览） | `CONTRIBUTING.md` | 源在 gdMain/CONTRIBUTING.md（单一事实源） |
| 版本号 | `VERSION` | 当前版本（单一事实源） |
| 能力声明 | `capabilities.yaml` | 接口契约 0.4.6 自持声明（已落盘） |
| 能力工具链 CLI | `docs/cli.md` | `gd-wa worldview new/check · art new/gen · slice export …` 切片生成 / 一致性检查 / 美术规格 / 参考图 / 装配导出 |
| 生图实战手册 | `docs/artgen-playbook.md` | ComfyUI 生图方法论：调用链/环境前置/排障/prompt 工程/筛种 |
| 设计意图层 | `blueprint/README.md` | 身份与语义蓝图目录定位 |
