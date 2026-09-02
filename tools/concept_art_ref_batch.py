# -*- coding: utf-8 -*-
"""gt_character_test001 · P-02 img2ref 补充 + P-04 Z-Image 补充
- P-02: 双人参考图 Crop 裁单人区域 → img2ref denoise 0.55（3:5 614×1024）
- P-04: Z-Image turbo 快速草稿（诺亚 1 张）
"""
import json, time, urllib.request, urllib.error, os, subprocess
from pathlib import Path
from datetime import datetime
from PIL import Image
import io

API = "http://127.0.0.1:8188"
ROOT = Path("C:/Users/inkse/gdAzeroth_WAgent")
OUT_DIR = ROOT / "projects/green-tide/assets/gt_character_test001"
OUT_DIR.mkdir(parents=True, exist_ok=True)

REF_SRC = Path("C:/Users/inkse/gdMain_GAgent/projects/green-tide/structured/art/reference/gt_character_reference.png")

# ---- 提示词（同 concept_art_batch.py）----
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

W, H = 614, 1024  # 3:5


def upload_image(img_path):
    """上传图片到 ComfyUI（curl multipart），返回 image name"""
    # img_path 需是绝对路径字符串，resolve 后传给 curl
    abs_path = str(Path(img_path).resolve())
    proc = subprocess.run(
        ['curl', '-s', '-X', 'POST',
         f'http://127.0.0.1:8188/upload/image',
         '-F', f'image=@{abs_path};type=image/png'],
        capture_output=True, text=True, timeout=30
    )
    resp = json.loads(proc.stdout)
    # 返回格式: {"name": "xxx.png", "subfolder": "", "type": "input"}
    return resp.get("name", resp.get("image", resp.get("filename")))


def post(url, payload):
    req = urllib.request.Request(url, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())

def get(url):
    with urllib.request.urlopen(url, timeout=30) as r:
        return json.loads(r.read())

def crop_single_refs():
    """Crop 双人参考图 → 艾拉拉左单人 + 诺亚右单人"""
    img = Image.open(REF_SRC).convert("RGB")
    src_w, src_h = img.size  # 应为 1024x1024
    print(f"  参考图尺寸: {src_w}x{src_h}")

    # 双人图左艾拉拉右诺亚，各占约 50% 宽
    # 留一点边距避免切脸
    margin = int(src_w * 0.05)  # 5% 边距
    half = src_w // 2

    # 艾拉拉：左侧 5%~50%
    alara_crop = img.crop((margin, 0, half - margin, src_h))
    # 诺亚：右侧 50%~95%
    noah_crop = img.crop((half + margin, 0, src_w - margin, src_h))

    alara_path = OUT_DIR / "ref_alara_crop.png"
    noah_path = OUT_DIR / "ref_noah_crop.png"
    alara_crop.save(alara_path)
    noah_crop.save(noah_path)
    print(f"  裁剪完成: alara={alara_crop.size}, noah={noah_crop.size}")
    return str(alara_path), str(noah_path)


def wf_p02(ref_image_name, prefix, seed, prompt):
    """P-02: img2ref denoise 0.55"""
    return {
        "1": {"class_type": "LoadImage", "inputs": {"image": ref_image_name}},
        "2": {"class_type": "UNETLoader", "inputs": {"unet_name": "krea2_turbo_int8_convrot.safetensors", "weight_dtype": "default"}},
        "3": {"class_type": "CLIPLoader", "inputs": {"clip_name": "qwen3vl_4b_fp8_scaled.safetensors", "type": "krea2"}},
        "4": {"class_type": "VAELoader", "inputs": {"vae_name": "qwen_image_vae.safetensors"}},
        "5": {"class_type": "CLIPTextEncode", "inputs": {"text": prompt, "clip": ["3", 0]}},
        "6": {"class_type": "CLIPTextEncode", "inputs": {"text": NEG, "clip": ["3", 0]}},
        "7": {"class_type": "ImageScale", "inputs": {"image": ["1", 0], "upscale_method": "lanczos", "width": W, "height": H, "crop": "center"}},
        "8": {"class_type": "VAEEncode", "inputs": {"pixels": ["7", 0], "vae": ["4", 0]}},
        "9": {"class_type": "KSampler", "inputs": {"seed": seed, "steps": 28, "cfg": 1.0, "sampler_name": "euler", "scheduler": "simple", "denoise": 0.55, "model": ["2", 0], "positive": ["5", 0], "negative": ["6", 0], "latent_image": ["8", 0]}},
        "10": {"class_type": "VAEDecode", "inputs": {"samples": ["9", 0], "vae": ["4", 0]}},
        "11": {"class_type": "SaveImage", "inputs": {"filename_prefix": prefix, "images": ["10", 0]}},
    }

def wf_p04(prefix, seed, prompt):
    """P-04: Z-Image turbo（8 steps 快速草稿）"""
    return {
        "1": {"class_type": "UNETLoader", "inputs": {"unet_name": "z_image_turbo_bf16.safetensors", "weight_dtype": "default"}},
        "2": {"class_type": "CLIPLoader", "inputs": {"clip_name": "qwen_3_4b.safetensors", "type": "lumina2", "device": "default"}},
        "3": {"class_type": "VAELoader", "inputs": {"vae_name": "ae.safetensors"}},
        "4": {"class_type": "CLIPTextEncode", "inputs": {"text": prompt, "clip": ["2", 0]}},
        "5": {"class_type": "CLIPTextEncode", "inputs": {"text": NEG, "clip": ["2", 0]}},
        "6": {"class_type": "EmptySD3LatentImage", "inputs": {"width": W, "height": H, "batch_size": 1}},
        "7": {"class_type": "ModelSamplingAuraFlow", "inputs": {"shift": 3.0, "model": ["1", 0]}},
        "8": {"class_type": "KSampler", "inputs": {"seed": seed, "steps": 8, "cfg": 1.0, "sampler_name": "res_multistep", "scheduler": "simple", "denoise": 1.0, "model": ["7", 0], "positive": ["4", 0], "negative": ["5", 0], "latent_image": ["6", 0]}},
        "9": {"class_type": "VAEDecode", "inputs": {"samples": ["8", 0], "vae": ["3", 0]}},
        "10": {"class_type": "SaveImage", "inputs": {"filename_prefix": prefix, "images": ["9", 0]}},
    }


def run_one(wf, tag, save_name, timeout=420):
    t0 = time.time()
    try:
        resp = post(API + "/prompt", {"prompt": wf, "client_id": "gt-char-p02p04"})
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
                    print(f"[{tag}] success 但无图")
                    return None
                src = images[0]
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
    print(f"[{tag}] TIMEOUT")
    return None


def write_meta(meta_path, **fields):
    lines = [f"{k}: {v}" for k, v in fields.items()]
    meta_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    try:
        q = get(API + "/queue")
        print(f"queue: running={len(q.get('queue_running', []))}, pending={len(q.get('queue_pending', []))}")
    except Exception as e:
        print(f"⚠ ComfyUI 查询失败: {e}")

    results = {}

    # ---- 0) Crop 参考图 ----
    print("\n=== Crop 参考图 ===")
    alara_crop, noah_crop = crop_single_refs()

    # ---- 0b) 上传裁剪图到 ComfyUI ----
    print("\n=== 上传裁剪图 ===")
    alara_img = upload_image(alara_crop)
    noah_img = upload_image(noah_crop)
    print(f"  alara_img={alara_img}, noah_img={noah_img}")

    # ---- 1) warmup P-02 ----
    print("\n=== P-02 warmup (alara) ===")
    r = run_one(wf_p02(alara_img, "alara_P02_warmup", 2026092099, ALARA), "P02-warmup", "alara_P02_warmup.png")
    if r:
        write_meta(OUT_DIR / "alara_P02_warmup.yaml",
                   需求="gt_character_test001", 图名="alara", 管线="P02",
                   类型="warmup", seed=2026092099, steps=28, cfg=1.0, denoise=0.55,
                   尺寸=f"{W}x{H}", 生成耗时_s=r["duration"],
                   comfy_filename=r["comfy_filename"],
                   提交时间=datetime.now().isoformat(timespec="seconds"),
                   提示词来源="concept-art-prompts.md §1+§2 + ART-REQUIREMENTS P14 #02",
                   参考图=alara_img)

    # ---- 2) P-02 艾拉拉 3 张 ----
    print("\n=== P-02 艾拉拉 3 张 ===")
    for i, sd in enumerate([2026092201, 2026092202, 2026092203], 1):
        name = f"alara_P02_v1_b{i:02d}.png"
        r = run_one(wf_p02(alara_img, f"alara_P02_v1_b{i:02d}", sd, ALARA), f"alara-P02-b{i:02d}", name)
        if not r:
            continue
        results[name] = r
        write_meta(OUT_DIR / f"alara_P02_v1_b{i:02d}.yaml",
                   需求="gt_character_test001", 图名="alara", 管线="P02",
                   迭代="v1", 批次=f"b{i:02d}",
                   seed=sd, steps=28, cfg=1.0, denoise=0.55,
                   尺寸=f"{W}x{H}", 生成耗时_s=r["duration"],
                   comfy_filename=r["comfy_filename"],
                   提交时间=datetime.now().isoformat(timespec="seconds"),
                   提示词来源="concept-art-prompts.md §1+§2 + ART-REQUIREMENTS P14 #02",
                   参考图=alara_img)

    # ---- 3) P-02 诺亚 3 张 ----
    print("\n=== P-02 诺亚 3 张 ===")
    for i, sd in enumerate([2026092301, 2026092302, 2026092303], 1):
        name = f"noah_P02_v1_b{i:02d}.png"
        r = run_one(wf_p02(noah_img, f"noah_P02_v1_b{i:02d}", sd, NOAH), f"noah-P02-b{i:02d}", name)
        if not r:
            continue
        results[name] = r
        write_meta(OUT_DIR / f"noah_P02_v1_b{i:02d}.yaml",
                   需求="gt_character_test001", 图名="noah", 管线="P02",
                   迭代="v1", 批次=f"b{i:02d}",
                   seed=sd, steps=28, cfg=1.0, denoise=0.55,
                   尺寸=f"{W}x{H}", 生成耗时_s=r["duration"],
                   comfy_filename=r["comfy_filename"],
                   提交时间=datetime.now().isoformat(timespec="seconds"),
                   提示词来源="concept-art-prompts.md §1+§2 + ART-REQUIREMENTS P14 #03",
                   参考图=noah_img)

    # ---- 4) warmup P-04 ----
    print("\n=== P-04 warmup (noah) ===")
    r = run_one(wf_p04("noah_P04_warmup", 2026092098, NOAH), "P04-warmup", "noah_P04_warmup.png")
    if r:
        write_meta(OUT_DIR / "noah_P04_warmup.yaml",
                   需求="gt_character_test001", 图名="noah", 管线="P04",
                   类型="warmup", seed=2026092098, steps=8, cfg=1.0, denoise=1.0,
                   尺寸=f"{W}x{H}", 生成耗时_s=r["duration"],
                   comfy_filename=r["comfy_filename"],
                   提交时间=datetime.now().isoformat(timespec="seconds"),
                   提示词来源="concept-art-prompts.md §1+§2 + ART-REQUIREMENTS P14 #03")

    # ---- 5) P-04 诺亚 1 张 ----
    print("\n=== P-04 诺亚 1 张 ===")
    name = "noah_P04_v1_b01.png"
    r = run_one(wf_p04("noah_P04_v1_b01", 2026092401, NOAH), "noah-P04-b01", name)
    if r:
        results[name] = r
        write_meta(OUT_DIR / "noah_P04_v1_b01.yaml",
                   需求="gt_character_test001", 图名="noah", 管线="P04",
                   迭代="v1", 批次="b01",
                   seed=2026092401, steps=8, cfg=1.0, denoise=1.0,
                   尺寸=f"{W}x{H}", 生成耗时_s=r["duration"],
                   comfy_filename=r["comfy_filename"],
                   提交时间=datetime.now().isoformat(timespec="seconds"),
                   提示词来源="concept-art-prompts.md §1+§2 + ART-REQUIREMENTS P14 #03")

    print(f"\n=== 汇总 ({len(results)} 张成功) ===")
    total = sum(v["duration"] for v in results.values())
    for k, v in results.items():
        print(f"  {k}  {v['duration']}s  {v['size_kb']}KB")
    print(f"总耗时: {total:.1f}s")
    print(f"落盘目录: {OUT_DIR}")
