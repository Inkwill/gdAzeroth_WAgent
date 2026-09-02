# ComfyUI 生图能力扩充计划（v0.2 · P0 已完成）

> 分控：azeroth（WAgent）· 日期：2026-09-01 · 状态：P0 7 项产图完成，待风格确认/交付
> 目标：接入本地 ComfyUI，使 azeroth 具备概念图生成能力，支撑 T-gt-03 美术风格概念图的落地产出（立项会 15 项配图，P0 7 项阻塞）。

---

## 1. 现状盘点（侦察结论）

| 项 | 状态 |
|---|---|
| ComfyUI 安装 | `D:/Comfy-Desktop/ComfyUI-Installs/ComfyUI/ComfyUI/`（Comfy Desktop 版）✓ |
| 模型目录 | `D:/Comfy-Desktop/ComfyUI-Shared/models`（settings.json `modelsDirs` 已配置）✓ |
| 图像 checkpoint | `sulphur_dev_fp8mixed.safetensors`；`PinkCherry_FineTune_Q5_K_M_v18_LTX23.gguf` |
| 视频 checkpoint | `ltx-2.3-22b-dev-fp8.safetensors`（LTX-2.3 22B） |
| Lora | LTX 蒸馏系 / minimax_h3 音频 / krea2_style_reference / gemma-3 |
| Custom nodes | ComfyUI-GGUF / videohelpersuite / minimax-h3-audio / websocket_image_save |
| **API 服务** | **未运行**（8188 无响应；8377=MCP UI、8765=404，均非 ComfyUI API） |
| 历史产出 | `D:/Pictures/green-tide/` 有 ComfyUI 图 2 张 + Gemini 图 2 张（8-28），命名 ComfyUI_00013/00015 |

**关键判断：**
- 机器主打 LTX-2.3（视频）+ minimax（音频）；图像模型仅 Sulphur，**美式卡通风格匹配度未知**——需实测或补模型
- ComfyUI API 未启动，连接层是第一步

---

## 2. 三层扩充

### 层一：连接层（启动 ComfyUI API）

| 步骤 | 动作 | 产出 |
|---|---|---|
| 1.1 | 启动 ComfyUI API 服务（方式 A：Comfy Desktop GUI 勾选 API 端口；方式 B：命令行 `python main.py --port 8188 --listen 127.0.0.1`） | 8188 端口 /system_stats 返回 JSON |
| 1.2 | 验证接口：`/system_stats`（GPU/内存）、`/object_info`（节点清单）、`/prompt`（提交） | 连通性报告 |
| 1.3 | 接入 Pi：优先 HTTP API 直连（无需 MCP）；可选配置 comfyui MCP 服务器（mcp.json） | 生图可调用 |

### 层二：能力层（capabilities.yaml 扩充）

新增能力条目（拟，待拍板）：

```yaml
  - id: concept-art-generation
    name: 概念图生成（ComfyUI）
    description: 基于本地 ComfyUI 生成游戏概念图（checkpoint + 提示词 + workflow），输出 PNG/JPG；风格对齐 T-gt-03 美术风格概念
    input_kind: brief
    output_kind: image
    prerequisites: "azeroth:art-style"
    status: draft
```

归属：作为 `art-style`（美术风格）子能力的实施能力；`output_kind: image`（新产出类型）。

### 层三：Skill 层（新增 comfyui-concept-art skill）

新 skill 文档（拟 `.pi/skills/comfyui-concept-art/SKILL.md`，项目级 skill 位置），内容：

1. **环境速查**：安装路径 / 模型清单 / 启动命令 / 端口 / 共享模型映射
2. **Workflow 模板**：checkpoint → CLIP Text Encode（正/负）→ KSampler → VAE Decode → Save Image；参数基准（steps/sampler/CFG/seed 控制）
3. **提示词工程**：
   - 风格锚点词库（美式卡通 Stylized Post-Apocalyptic Cartoon / 鲜艳绿洲 / #90EE90 治愈绿系，源自 T-gt-03）
   - 每类图模板：角色立绘 / 场景 16:9 / ASMR 动作特写 / 前后对比
   - 负面提示词模板（畸形肢体/文本水印/照片写实过度等）
   - 角色一致性：seed 固定 + 参考图 + 角色锚点词复用（艾拉拉/诺亚视觉锚点）
4. **产图 SOP**（对接 ART-REQUIREMENTS.md 15 项）：
   - 优先级：P0（01 封面 → 02/03 双主角 → 04/05/06 ASMR 三阶段）→ P1 → P2
   - 每项：需求要点 → 提示词 → 参数 → 生成 → 自检（与 §4.4/§6.1/§6.3 口径差=0）
   - 命名：`GT_<编号>_<图名>.png`（规范）；输出路径按交付规范
5. **验收锚点**：与 T-gt-01 §10.2 一致；双主角视觉锚点（实验室残留/机械义肢✌️）；ASMR 三阶段（枯藤断裂/白泡/返绿）
6. **交付对接**：产出图交付 gdBard assets/（deck 同目录），Bard 侧替换占位

---

## 3. 产图执行路线（P0 7 项阻塞立项会）

```
P0-1 启动 ComfyUI API（连接层 1.1-1.3）
P0-2 实测 Sulphur 出图质量（美式卡通风格匹配度）→ 不匹配则决策补模型
P0-3 01 封面主视觉 16:9 → 02/03 双主角立绘 4:5 → 04/05/06 ASMR 三阶段 4:3
P0-4 自检（口径/风格/命名）→ 交付 gdBard assets/
```

---

## 4. 风险与决策点（需拍板）

| # | 风险/决策 | 建议 |
|---|---|---|
| R1 | Sulphur 可能非美式卡通风格，产出与 T-gt-03 风格基准有偏差 | 实测 1-2 张样张后决策；不匹配则**允许下载专用卡通 checkpoint**（需确认网络/磁盘） |
| R2 | API 启动方式：headless 命令行 vs Comfy Desktop GUI | 推荐 headless（可自动化）；GPU 占用需确认 |
| R3 | 双主角跨图一致性（艾拉拉/诺亚 15 项中多次出现） | seed 固定 + 锚点词复用 + 首图定稿后作参考图 |
| R4 | 透明底立绘（4:5 PNG）需背景抠除 | 用 background_removal 模型（共享目录已有）或生成后处理 |
| R5 | 15 项全部产图 vs 先 P0 7 项 | 先 P0 7 项阻塞立项会，P1/P2 视立项会结论 |

---

## 5. 执行顺序（拍板后）

1. 用户确认本计划（或调整）
2. 启动 ComfyUI API（层一）→ 连通验证
3. capabilities.yaml 新增 `concept-art-generation`（层二）
4. 写 `.pi/skills/comfyui-concept-art/SKILL.md`（层三）
5. 实测样张（R1 决策点）→ 定稿风格参数
6. P0 7 项产图 → 自检 → 交付 gdBard

---

*本计划为草案，待用户拍板后执行。*
