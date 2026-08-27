# 参考图生成实战手册 · ArtGen Playbook

> 本机 ComfyUI 文生图全链路方法论（v0.2.4 实战沉淀）。
> 场景：`gd-wa art gen` 从 art spec 切片 → 提示词 → ComfyUI → 参考图。
> 前置文档：`docs/cli.md`（命令用法）· `templates/t2i-z-image-v1.json`（工作流）。

---

## 1. 架构与调用链（一图流）

```
art spec 切片 (.md)
   │  parse-md.mjs 解析 6 块（PURPOSE/STYLE ANCHORS/ART BRIEF/SPEC/MUST-HAVE/FORBIDDEN）
   ▼
prompt.mjs 组装
   正向 = 风格锚点(前置) + PURPOSE + 维度指导 + MUST-HAVE
   负向 = FORBIDDEN禁忌 + 通用负向
   ▼
artgen.mjs（node fetch 直调，零 python 依赖）
   POST /prompt → GET /history/<id> 轮询 → GET /view 下载
   ▼
projects/<项目>/WAgent/<切片>/ref-<seed>.png + refs.json（元数据）
```

**设计要点**：
- node 原生 fetch 直调 ComfyUI HTTP API，不依赖 python/requests/websocket（跨环境零依赖）
- 工作流模板 `t2i-z-image-v1.json` 为 **v1 API 格式**（ComfyUI 0.27+ /prompt 唯一接受的格式；0.33 不接 v0.3 export 的 `widgets_values_named`）
- provider 抽象：`comfy`（真实）/ `dry-run`（降级，服务不可达时自动切换，管线永不阻塞）

## 2. 环境前置（一次性，但关键）

| 项 | 要求 | 说明 |
|----|------|------|
| ComfyUI 服务 | 127.0.0.1:8188 | `curl /queue` 返回 `{"queue_running":[],"queue_pending":[]}` |
| 模型 | Z-Image Turbo 全套 | `diffusion_models/z_image_turbo_bf16` + `text_encoders/qwen_3_4b` + `vae/ae.safetensors` |
| **显存** | ⚠️ 8G 必须 `--lowvram` | 模型总重 19.3G（unet 11.5 + 编码器 7.5 + vae 0.3），默认 auto 模式 CUDA OOM |

**启动规范（本机实测）**：
```powershell
# cwd 必须是 install root（不是源码目录！）
cd D:\Comfy-Desktop\ComfyUI-Installs\ComfyUI
D:\Comfy-Desktop\ComfyUI-Installs\ComfyUI\ComfyUI\.venv\Scripts\python.exe -s ComfyUI\main.py `
  --lowvram `
  --extra-model-paths-config "C:\Users\inkse\AppData\Roaming\Comfy Desktop\instance-model-paths\inst-1786904307072.yaml" `
  --input-directory D:\Comfy-Desktop\ComfyUI-Shared\input `
  --output-directory D:\Comfy-Desktop\ComfyUI-Shared\output
```
> 模型在 `ComfyUI-Shared/models`（共享目录），必须带 extra-model-paths-config 映射。

## 3. 排障手册（本次实战踩过的坑）

| 现象 | 根因 | 解法 |
|------|------|------|
| **CUDA out of memory**（CLIPTextEncode 阶段） | 模型 19.3G > 8G 显存，默认模式不 offload | 重启加 `--lowvram`（权重分片加载，显存+系统 RAM 换入换出） |
| 提交成功但 outputs 空 | 执行 error（见 /history 的 status_str=error） | 查 `GET /history/<id>` 的 `execution_error`（node_type/node_id/exception） |
| 探活失败误降级 dry-run | API 参数传 null（默认参数只对 undefined 生效） | `api = api \|\| DEFAULT_API` 兼容 null |
| Start-Process 报 `FileNotFoundError`（路径带空格） | ArgumentList 含空格项被拆断 | 内嵌引号 `'\"C:\...\Comfy Desktop\...\"'` |
| 启动报 `can't open file ...ComfyUI\ComfyUI\ComfyUI\main.py` | WorkingDirectory 层级错误 | cwd 用 install root（`...\Installs\ComfyUI`），main.py 相对路径 `ComfyUI\main.py` |
| 探活/提交 | 服务没起 | 先 `curl /queue`；WSL 内 127.0.0.1 是 WSL 自己，须从 Windows 侧访问 |

## 4. Prompt 工程（Z-Image Turbo 专属，comfyui-t2i skill §7 对齐）

- **风格关键词放最前**（attention 机制）：`anime RPG game style, cel shading, ...`
- **5 要素法**：风格 + 主体 + 细节 + 场景 + 技术修饰
- **权重语法**：`(word:1.3)` 加强 / `(word:0.7)` 减弱
- **⚠️ cfg=1 负向不生效**（Turbo 特性）——FORBIDDEN 禁忌写入负向但**不保证生效**，需回避的元素建议正向写 "no X"；元数据 notes 已标注
- **主题不准 → 改 prompt；细节不准 → 换 seed**（seed 探索优先于死磕 prompt）
- **采样参数**：8 步足够（Turbo）；常规模型 30-50 步

## 5. 可追溯与筛种

- **refs.json**：每个 ref 记录 file/seed/prompt/negative_prompt/prompt_id/model/created——任何一张图可复现（同 prompt+seed 重跑即同图）
- **批量筛种**：`--seed "42,43,44"` 一次出多张 → 人工挑优 → 记录选中 seed 回写
- **prompt_id** 留档便于回查 ComfyUI /history 执行详情

## 6. 边界（红线）

- 产出是**参考资源**（风格定位/概念参考），**非最终美术资产**——最终资产归 PLAgent 原型
- 不做图生图/视频等扩展（img2img 复用同 API，留待演进）
- 降级策略：无 ComfyUI 时 dry-run 仍交付完整管线价值（prompt 文本可贴外部工具）

## 7. 演进预留

- FORBIDDEN 禁忌双写策略（正向 "no X" + 负向）在非 Turbo 模型（cfg>1）上可完整生效——provider 换模型时启用
- 模型可换：krea2/minimax/ltx 已在本机（换模型 = 换工作流模板 + prompt 风格调整）
