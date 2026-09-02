# -*- coding: utf-8 -*-
"""selling_point_graphic · #10 患难合作（新设计）· P-01 ×3 + P-02(img2ref 双人参考) ×3
4:3 1024×768 · 中景双人左右分工修复避难所"""
import json, time, urllib.request
from pathlib import Path
from datetime import datetime

API = "http://127.0.0.1:8188"
OUT = Path("C:/Users/inkse/gdAzeroth_WAgent/projects/green-tide/assets/selling_point_graphic")
REF = "gt_character_reference.png"  # 双人概念图（左艾拉拉右诺亚）

STYLE = (
    "3D Pixar-style render, stylized 3D cartoon character design, NOT 2D flat illustration, "
    "PBR materials with cel-shading hybrid, soft volumetric lighting, "
    "subsurface scattering on skin, cinematic three-point lighting, "
    "realistic body proportions with stylized 3D characters, "
    "warm orange healing green cozy brown color palette with #90EE90 healing green accents, "
    "cozy hopeful healing atmosphere, NOT horror, NOT cold color palette, "
    "NOT chibi, NOT 2D line art, NOT anime, NOT low poly"
)

NEG = (
    "2D flat illustration, 2D anime, line art, chibi, chibi style, deformed body proportions, "
    "realistic photographic style, horror, gore, dark mood, text, watermark, logo, "
    "deformed hands, extra fingers, low quality, blurry, ugly, "
    "cold color palette, neon green, oversaturated, "
    "low-poly, low poly, flat shading without depth, no 3D rendering, "
    "extreme close-up, hand close-up, face close-up, \"蜕变\""
)

# #10 患难合作（ART-REQUIREMENTS P3 更新版）
PROMPT = (
    "stylized 3D cartoon illustration, medium shot wide scene with two characters, "
    "NOT 2D flat illustration, NOT extreme close-up. "
    "Two survivors repairing their ruined shelter together, side by side left and right, "
    "each focused on own task, no eye contact, no physical contact. "
    "LEFT SIDE: Alara, a 34-year-old woman ecologist with 5-head-body realistic proportions, "
    "shoulder-length hair with braids woven with green vines, white lab coat remnants with tool belt, "
    "seen from side or back, crouching before overgrown mutant vines, "
    "hands gently parting the vines or holding pruning shears cutting charred dead vines, "
    "vines glowing soft emerald light where she touches them. "
    "RIGHT SIDE: Noah, a 17-year-old boy mechanic prodigy with 4.5-head-body proportions, "
    "wild short hair with green and blue dyed streaks, patchwork wasteland streetwear, "
    "mechanical prosthetic right arm, seen from side or back, "
    "crouching before an opened old water pump and pipes, "
    "prosthetic arm holding a welding torch or wrench repairing the pump, small warm sparks flying. "
    "CENTER between them: the core object awaiting repair clearly visible as focal point - "
    "an old stone water well with a hand pump, partially cleaned, "
    "forming natural left-and-right composition pointing toward the center. "
    "Environment: shelter mid-restoration with strong contrast - "
    "one half already bright green oasis with tamed vines, glowing water purifier, warm window lights, "
    "the other half still desolate ruins with dead vines wrapping walls, broken walls, gray-brown tones. "
    "Single warm light source illuminating the workspace. "
    "Each character occupies about 25 percent of frame on their side, center open for repair target, "
    "no overlapping figures. "
    "Quiet focused working mood, cooperation, companionship, "
    "simple clear action silhouettes, "
    "vine zone on Alara side separated from metal machine zone on Noah side, "
    "no hand close-ups. "
    + STYLE
)

W, H = 1024, 768


def post(url, payload):
    req = urllib.request.Request(url, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())

def get(url):
    with urllib.request.urlopen(url, timeout=30) as r:
        return json.loads(r.read())

def wf_p01(seed, prefix):
    return {
        "1": {"class_type": "UNETLoader", "inputs": {"unet_name": "krea2_turbo_int8_convrot.safetensors", "weight_dtype": "default"}},
        "2": {"class_type": "CLIPLoader", "inputs": {"clip_name": "qwen3vl_4b_fp8_scaled.safetensors", "type": "krea2"}},
        "3": {"class_type": "VAELoader", "inputs": {"vae_name": "qwen_image_vae.safetensors"}},
        "4": {"class_type": "CLIPTextEncode", "inputs": {"text": PROMPT, "clip": ["2", 0]}},
        "5": {"class_type": "CLIPTextEncode", "inputs": {"text": NEG, "clip": ["2", 0]}},
        "6": {"class_type": "EmptyLatentImage", "inputs": {"width": W, "height": H, "batch_size": 1}},
        "7": {"class_type": "KSampler", "inputs": {"seed": seed, "steps": 30, "cfg": 1.0, "sampler_name": "euler", "scheduler": "simple", "denoise": 1.0, "model": ["1", 0], "positive": ["4", 0], "negative": ["5", 0], "latent_image": ["6", 0]}},
        "8": {"class_type": "VAEDecode", "inputs": {"samples": ["7", 0], "vae": ["3", 0]}},
        "9": {"class_type": "SaveImage", "inputs": {"filename_prefix": prefix, "images": ["8", 0]}},
    }

def wf_p02(seed, prefix, denoise=0.55):
    return {
        "1": {"class_type": "LoadImage", "inputs": {"image": REF}},
        "2": {"class_type": "UNETLoader", "inputs": {"unet_name": "krea2_turbo_int8_convrot.safetensors", "weight_dtype": "default"}},
        "3": {"class_type": "CLIPLoader", "inputs": {"clip_name": "qwen3vl_4b_fp8_scaled.safetensors", "type": "krea2"}},
        "4": {"class_type": "VAELoader", "inputs": {"vae_name": "qwen_image_vae.safetensors"}},
        "5": {"class_type": "CLIPTextEncode", "inputs": {"text": PROMPT, "clip": ["3", 0]}},
        "6": {"class_type": "CLIPTextEncode", "inputs": {"text": NEG, "clip": ["3", 0]}},
        "7": {"class_type": "ImageScale", "inputs": {"image": ["1", 0], "upscale_method": "lanczos", "width": W, "height": H, "crop": "center"}},
        "8": {"class_type": "VAEEncode", "inputs": {"pixels": ["7", 0], "vae": ["4", 0]}},
        "9": {"class_type": "KSampler", "inputs": {"seed": seed, "steps": 28, "cfg": 1.0, "sampler_name": "euler", "scheduler": "simple", "denoise": denoise, "model": ["2", 0], "positive": ["5", 0], "negative": ["6", 0], "latent_image": ["8", 0]}},
        "10": {"class_type": "VAEDecode", "inputs": {"samples": ["9", 0], "vae": ["4", 0]}},
        "11": {"class_type": "SaveImage", "inputs": {"filename_prefix": prefix, "images": ["10", 0]}},
    }

def submit_wait(wf, tag, save_name, timeout=400):
    t0 = time.time()
    try:
        resp = post(API + "/prompt", {"prompt": wf, "client_id": f"gt-bond2-{int(t0)}"})
    except Exception as e:
        print(f"[{tag}] FAIL: {e}")
        return None
    pid = resp.get("prompt_id")
    if not pid:
        print(f"[{tag}] no pid")
        return None
    print(f"[{tag}] submitted pid={pid[:8]}")
    while time.time() - t0 < timeout:
        try:
            h = get(f"{API}/history/{pid}")
        except Exception:
            h = {}
        if pid in h:
            st = h[pid].get("status", {}).get("status_str")
            if st == "success":
                dt = time.time() - t0
                imgs = [i for o in h[pid].get("outputs", {}).values() for i in o.get("images", [])]
                if not imgs:
                    print(f"[{tag}] no images")
                    return None
                src = imgs[0]
                tgt = OUT / save_name
                view_url = f"{API}/view?filename={src['filename']}&type={src.get('type','output')}&subfolder={src.get('subfolder','')}"
                with urllib.request.urlopen(view_url, timeout=60) as r:
                    tgt.write_bytes(r.read())
                sz = tgt.stat().st_size // 1024
                print(f"[{tag}] OK | {dt:.1f}s | {save_name} ({sz}KB)")
                return {"duration": dt}
            elif st == "error":
                print(f"[{tag}] error")
                return None
        time.sleep(3)
    print(f"[{tag}] TIMEOUT")
    return None

def write_meta(name, **fields):
    lines = [f"{k}: {v}" for k, v in fields.items()]
    (OUT / name.replace(".png", ".yaml")).write_text("\n".join(lines) + "\n", encoding="utf-8")

if __name__ == "__main__":
    results = {}

    # P-01 三张（v2 迭代，旧版 #10 缝补已是 v1）
    print("=== P-01 患难合作 × 3 ===")
    for i, sd in enumerate([2026100001, 2026100002, 2026100003], 1):
        name = f"bond_P01_v2_b{i:02d}.png"
        r = submit_wait(wf_p01(sd, f"bond_P01_v2_b{i:02d}"), f"P01-b{i:02d}", name)
        if r:
            results[name] = r
            write_meta(name,
                       需求="selling_point_graphic", 图名="bond", 管线="P01",
                       迭代="v2", 批次=f"b{i:02d}",
                       seed=sd, steps=30, cfg=1.0, denoise=1.0, 尺寸=f"{W}x{H}",
                       生成耗时_s=round(r["duration"], 1),
                       提交时间=datetime.now().isoformat(timespec="seconds"),
                       需求来源="ART-REQUIREMENTS.md P3 #10 患难合作（更新版）")

    # P-02 三张（img2ref 双人参考图）
    print("\n=== P-02 患难合作 × 3（ref=gt_character_reference.png）===")
    for i, sd in enumerate([2026100101, 2026100102, 2026100103], 1):
        name = f"bond_P02_v1_b{i:02d}.png"
        r = submit_wait(wf_p02(sd, f"bond_P02_v1_b{i:02d}"), f"P02-b{i:02d}", name)
        if r:
            results[name] = r
            write_meta(name,
                       需求="selling_point_graphic", 图名="bond", 管线="P02",
                       迭代="v1", 批次=f"b{i:02d}",
                       seed=sd, steps=28, cfg=1.0, denoise=0.55, 尺寸=f"{W}x{H}",
                       生成耗时_s=round(r["duration"], 1),
                       提交时间=datetime.now().isoformat(timespec="seconds"),
                       参考图=REF,
                       参考图来源="gdMain/.../reference/gt_character_reference.png (双人概念图)",
                       需求来源="ART-REQUIREMENTS.md P3 #10 患难合作（更新版）")

    print(f"\n=== 汇总 ({len(results)}/6) ===")
    total = sum(v["duration"] for v in results.values())
    for k, v in results.items():
        print(f"  {k}  {v['duration']:.1f}s")
    print(f"总耗时: {total:.1f}s")
    print(f"落盘: {OUT}")
