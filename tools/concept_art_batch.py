# -*- coding: utf-8 -*-
"""临时需求 gt_character_test001 · P14 双主角立绘（3:5 · 614×1024）
- P-01 管线（Krea2 标准文本生图）
- 每角色 3 张备选（不同 seed）
- 输出：projects/green-tide/assets/gt_character_test001/
- 命名：图名_管线_v1_b<批次>.png + 同名 .yaml 元数据
"""
import json, time, urllib.request, urllib.error, os
from pathlib import Path
from datetime import datetime

API = "http://127.0.0.1:8188"
ROOT = Path("C:/Users/inkse/gdAzeroth_WAgent")
OUT_DIR = ROOT / "projects/green-tide/assets/gt_character_test001"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ---- 风格基础块（与 concept-art-prompts.md §1 对齐 · v1.2 起强制）----
STYLE = ("3D Pixar-style render, stylized 3D cartoon character design, NOT 2D flat illustration, "
"PBR materials with cel-shading hybrid, soft volumetric lighting, "
"subsurface scattering on skin, cinematic three-point lighting, "
"realistic body proportions with stylized 3D characters, "
"warm orange healing green cozy brown color palette with #90EE90 healing green accents, "
"post-apocalyptic wasteland transforming into vibrant lush green oasis, "
"cozy hopeful healing atmosphere, NOT horror, NOT cold color palette")

NEG = ("2D flat illustration, 2D anime, line art, chibi, chibi style, deformed body proportions, "
"realistic photographic style, horror, gore, dark mood, text, watermark, logo, "
"deformed hands, extra fingers, low quality, blurry, ugly, cold color palette, neon green, "
"oversaturated, flat shading without depth, no 3D rendering, \"蜕变\"")

# ---- P14 角色提示词（艾拉拉 #02 / 诺亚 #03）----
ALARA = (
    "stylized 3D cartoon character portrait, full body, centered, "
    "vertical 3:5 portrait composition, character sheet pose, NOT 2D flat illustration. "
    "34-year-old female ecologist, 5-head-body realistic proportions, "
    "shoulder-length hair with post-apocalyptic braids woven with green vines, "
    "old damaged research goggles (lens cracked with plant overgrowth), "
    "white lab coat remnants with visible pockets and badge traces, "
    "plant fiber scarf, laboratory blue and plant green color scheme, "
    "white undershirt, brown utility belt with tools, sturdy boots. "
    "[P14] 姿态干练：一手轻扶腰间工具，仰眸望向远方；肩上与手臂袖口处有自然植物融合（嫩绿藤蔓与嫩芽攀附）；"
    "实验室外套可见烧灼痕迹与工具徽章印迹；"
    "表情克制内敛，眼神带负罪感与守护感，嘴角微抿温柔。 "
    + STYLE
)

NOAH = (
    "stylized 3D cartoon character portrait, full body, centered, "
    "vertical 3:5 portrait composition, character sheet pose, NOT 2D flat illustration. "
    "17-year-old boy mechanic prodigy, 4.5-head-body realistic proportions, "
    "wild short hair with green and blue dyed streaks, "
    "modded goggles on head, mechanical prosthetic right arm with visible metal joints and bolts, "
    "patchwork wasteland streetwear with metal parts decorations and visible stitches, "
    "energetic orange and modified blue color scheme, "
    "cargo pants with tool pockets, sturdy boots, fingerless gloves. "
    "[P14] 朋克乐观野性：标志性 peace-sign 手势举至面颊旁，露齿自信笑；"
    "机械义肢右手金属光泽与齿轮螺栓细节清晰可见；"
    "改装眼镜反光废土天光；斜侧 3/4 角度增加动感，姿态张扬；"
    "拼接外套 / 机能裤 / 旧军靴等废土穿搭细节丰富。 "
    + STYLE
)

# ---- Workflow: P-01（沿用 benchmark_pipelines.py 范本 · 仅调尺寸/prefix）----
def wf_p01(prefix, seed, width, height, prompt):
    return {
        "1": {"class_type": "UNETLoader", "inputs": {"unet_name": "krea2_turbo_int8_convrot.safetensors", "weight_dtype": "default"}},
        "2": {"class_type": "CLIPLoader", "inputs": {"clip_name": "qwen3vl_4b_fp8_scaled.safetensors", "type": "krea2"}},
        "3": {"class_type": "VAELoader", "inputs": {"vae_name": "qwen_image_vae.safetensors"}},
        "4": {"class_type": "CLIPTextEncode", "inputs": {"text": prompt, "clip": ["2", 0]}},
        "5": {"class_type": "CLIPTextEncode", "inputs": {"text": NEG, "clip": ["2", 0]}},
        "6": {"class_type": "EmptyLatentImage", "inputs": {"width": width, "height": height, "batch_size": 1}},
        "7": {"class_type": "KSampler", "inputs": {"seed": seed, "steps": 30, "cfg": 1.0, "sampler_name": "euler", "scheduler": "simple", "denoise": 1.0, "model": ["1", 0], "positive": ["4", 0], "negative": ["5", 0], "latent_image": ["6", 0]}},
        "8": {"class_type": "VAEDecode", "inputs": {"samples": ["7", 0], "vae": ["3", 0]}},
        "9": {"class_type": "SaveImage", "inputs": {"filename_prefix": prefix, "images": ["8", 0]}},
    }

def post(url, payload):
    req = urllib.request.Request(url, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())

def get(url):
    with urllib.request.urlopen(url, timeout=30) as r:
        return json.loads(r.read())

def run_one(wf, tag, save_name, timeout=300):
    """提交 → 轮询 → 下载到 OUT_DIR/save_name（去 ComfyUI 原生 _NNNNN_ 序号）"""
    t0 = time.time()
    try:
        resp = post(API + "/prompt", {"prompt": wf, "client_id": "gt-char-test001"})
    except urllib.error.URLError as e:
        print(f"[{tag}] SUBMIT FAIL: {e}")
        return None
    pid = resp.get("prompt_id")
    if not pid:
        print(f"[{tag}] SUBMIT FAIL (no prompt_id): {resp}")
        return None
    while time.time() - t0 < timeout:
        try:
            h = get(f"{API}/history/{pid}")
        except Exception:
            h = {}
        if pid in h:
            st = h[pid].get("status", {}).get("status_str")
            if st == "success":
                dt = time.time() - t0
                images = [i for o in h[pid].get("outputs", {}).values() for i in o.get("images", [])]
                if not images:
                    print(f"[{tag}] success 但 outputs 无图: {h[pid]}")
                    return None
                src = images[0]
                # 下载到 OUT_DIR/<save_name>
                target = OUT_DIR / save_name
                with urllib.request.urlopen(f"{API}/view?filename={src['filename']}&type={src.get('type','output')}&subfolder={src.get('subfolder','')}", timeout=60) as r:
                    target.write_bytes(r.read())
                size_kb = target.stat().st_size / 1024
                print(f"[{tag}] ✓ {st} | {dt:.1f}s | {save_name} ({size_kb:.1f}KB)")
                return {"duration": round(dt, 1), "size_kb": round(size_kb, 1), "comfy_filename": src["filename"]}
            elif st == "error":
                print(f"[{tag}] ✗ error: {h[pid].get('status', {}).get('messages')}")
                return None
        time.sleep(3)
    print(f"[{tag}] TIMEOUT ({timeout}s)")
    return None

def write_meta(meta_path, **fields):
    lines = [f"{k}: {v}" for k, v in fields.items()]
    meta_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

if __name__ == "__main__":
    # 队列检查
    try:
        q = get(API + "/queue")
        print(f"queue_running={len(q.get('queue_running', []))}, queue_pending={len(q.get('queue_pending', []))}")
    except Exception as e:
        print(f"⚠ ComfyUI 队列查询失败: {e}")

    W, H = 614, 1024  # 3:5 · 8GB 显存长边上限内
    results = {}

    # ---- 0) warmup（加热模型 + 验证流程）----
    print("\n=== warmup ===")
    r = run_one(wf_p01("warmup_alara", 2026091099, W, H, ALARA), "warmup", "alara_P01_warmup.png")
    if r is None:
        print("warmup 失败，终止")
        raise SystemExit(1)
    write_meta(OUT_DIR / "alara_P01_warmup.yaml",
               需求="gt_character_test001",
               图名="alara",
               管线="P01",
               类型="warmup",
               seed=2026091099, steps=8, cfg=1.0, denoise=1.0,  # warmup steps 实际 = 脚本里的 30（按 bench 习惯跑全量）
               尺寸=f"{W}x{H}",
               生成耗时_s=r["duration"],
               comfy_filename=r["comfy_filename"],
               提交时间=datetime.now().isoformat(timespec="seconds"),
               提示词来源="concept-art-prompts.md §1+§2 + ART-REQUIREMENTS P14 #02")

    # ---- 1) 艾拉拉 3 张备选 ----
    print("\n=== 艾拉拉 3 备选 ===")
    alara_seeds = [2026091201, 2026091202, 2026091203]
    for i, sd in enumerate(alara_seeds, 1):
        name = f"alara_P01_v1_b{i:02d}.png"
        r = run_one(wf_p01(f"alara_P01_v1_b{i:02d}", sd, W, H, ALARA), f"alara-b{i:02d}", name)
        if r is None:
            print(f"  ✗ alara b{i:02d} 失败，跳过")
            continue
        results[name] = r
        write_meta(OUT_DIR / f"alara_P01_v1_b{i:02d}.yaml",
                   需求="gt_character_test001",
                   图名="alara",
                   管线="P01",
                   迭代="v1", 批次=f"b{i:02d}",
                   seed=sd, steps=30, cfg=1.0, denoise=1.0,
                   尺寸=f"{W}x{H}",
                   生成耗时_s=r["duration"],
                   comfy_filename=r["comfy_filename"],
                   提交时间=datetime.now().isoformat(timespec="seconds"),
                   提示词来源="concept-art-prompts.md §1+§2 + ART-REQUIREMENTS P14 #02")

    # ---- 2) 诺亚 3 张备选 ----
    print("\n=== 诺亚 3 备选 ===")
    noah_seeds = [2026091301, 2026091302, 2026091303]
    for i, sd in enumerate(noah_seeds, 1):
        name = f"noah_P01_v1_b{i:02d}.png"
        r = run_one(wf_p01(f"noah_P01_v1_b{i:02d}", sd, W, H, NOAH), f"noah-b{i:02d}", name)
        if r is None:
            print(f"  ✗ noah b{i:02d} 失败，跳过")
            continue
        results[name] = r
        write_meta(OUT_DIR / f"noah_P01_v1_b{i:02d}.yaml",
                   需求="gt_character_test001",
                   图名="noah",
                   管线="P01",
                   迭代="v1", 批次=f"b{i:02d}",
                   seed=sd, steps=30, cfg=1.0, denoise=1.0,
                   尺寸=f"{W}x{H}",
                   生成耗时_s=r["duration"],
                   comfy_filename=r["comfy_filename"],
                   提交时间=datetime.now().isoformat(timespec="seconds"),
                   提示词来源="concept-art-prompts.md §1+§2 + ART-REQUIREMENTS P14 #03")

    # ---- 汇总 ----
    print(f"\n=== 汇总 ({len(results)}/6 张成功) ===")
    total = sum(v["duration"] for v in results.values())
    for k, v in results.items():
        print(f"  {k}  {v['duration']}s  {v['size_kb']}KB")
    print(f"总耗时: {total:.1f}s（不计 warmup）")
    print(f"落盘目录: {OUT_DIR}")
