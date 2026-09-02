# -*- coding: utf-8 -*-
"""单人参考图 alara_3.jpg → P-02 denoise=0.35 + P-03 kref 各一张"""
import json, time, urllib.request
from pathlib import Path
from datetime import datetime

API = "http://127.0.0.1:8188"
OUT = Path("C:/Users/inkse/gdAzeroth_WAgent/projects/green-tide/assets/gt_character_test001")

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
"oversaturated, flat shading without depth, no 3D rendering")

ALARA = (
    "stylized 3D cartoon character portrait, full body, centered, "
    "vertical 3:5 portrait composition, character sheet pose, NOT 2D flat illustration. "
    "34-year-old female ecologist, 5-head-body realistic proportions, "
    "shoulder-length hair with post-apocalyptic braids woven with green vines, "
    "old damaged research goggles (lens cracked with plant overgrowth), "
    "white lab coat remnants with visible pockets and badge traces, "
    "plant fiber scarf, laboratory blue and plant green color scheme, "
    "white undershirt, brown utility belt with tools, sturdy boots. "
    "P14: 姿态干练，一手轻扶腰间工具，仰眸望向远方；肩上与手臂袖口处有自然植物融合；"
    "表情克制内敛，眼神带负罪感与守护感，嘴角微抿温柔. " + STYLE)

W, H = 614, 1024
REF = "alara_3.jpg"


def post(url, payload):
    req = urllib.request.Request(url, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


def get(url):
    with urllib.request.urlopen(url, timeout=30) as r:
        return json.loads(r.read())


def submit_wait(wf, tag, save_name, timeout=480):
    t0 = time.time()
    try:
        resp = post(API + "/prompt", {"prompt": wf, "client_id": f"gt-single-{int(t0)}"})
    except Exception as e:
        print(f"[{tag}] FAIL: {e}")
        return None
    pid = resp.get("prompt_id")
    if not pid:
        print(f"[{tag}] no pid")
        return None
    print(f"[{tag}] submitted pid={pid}")
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
                print(f"[{tag}] error: {h[pid].get('status',{}).get('messages')}")
                return None
        time.sleep(3)
    print(f"[{tag}] TIMEOUT")
    return None


def write_meta(name, **fields):
    lines = [f"{k}: {v}" for k, v in fields.items()]
    (OUT / name.replace(".png", ".yaml")).write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    # P-02 denoise 0.35
    wf_p02 = {
        "1": {"class_type": "LoadImage", "inputs": {"image": REF}},
        "2": {"class_type": "UNETLoader", "inputs": {"unet_name": "krea2_turbo_int8_convrot.safetensors", "weight_dtype": "default"}},
        "3": {"class_type": "CLIPLoader", "inputs": {"clip_name": "qwen3vl_4b_fp8_scaled.safetensors", "type": "krea2"}},
        "4": {"class_type": "VAELoader", "inputs": {"vae_name": "qwen_image_vae.safetensors"}},
        "5": {"class_type": "CLIPTextEncode", "inputs": {"text": ALARA, "clip": ["3", 0]}},
        "6": {"class_type": "CLIPTextEncode", "inputs": {"text": NEG, "clip": ["3", 0]}},
        "7": {"class_type": "ImageScale", "inputs": {"image": ["1", 0], "upscale_method": "lanczos", "width": W, "height": H, "crop": "center"}},
        "8": {"class_type": "VAEEncode", "inputs": {"pixels": ["7", 0], "vae": ["4", 0]}},
        "9": {"class_type": "KSampler", "inputs": {"seed": 2026095001, "steps": 28, "cfg": 1.0, "sampler_name": "euler", "scheduler": "simple", "denoise": 0.35, "model": ["2", 0], "positive": ["5", 0], "negative": ["6", 0], "latent_image": ["8", 0]}},
        "10": {"class_type": "VAEDecode", "inputs": {"samples": ["9", 0], "vae": ["4", 0]}},
        "11": {"class_type": "SaveImage", "inputs": {"filename_prefix": "alara_P02_single", "images": ["10", 0]}},
    }

    print("=== P-02 denoise=0.35 ===")
    r = submit_wait(wf_p02, "P02-single", "alara_P02_single.png")
    if r:
        write_meta("alara_P02_single.png",
                   需求="gt_character_test001", 图名="alara", 管线="P02",
                   迭代="single", 批次="b01",
                   seed=2026095001, steps=28, cfg=1.0, denoise=0.35,
                   尺寸=f"{W}x{H}",
                   生成耗时_s=round(r["duration"], 1),
                   提交时间=datetime.now().isoformat(timespec="seconds"),
                   参考图=REF,
                   参考图来源="alara_3.jpg (单人艾拉拉官方参考)")

    # P-03 kref
    wf_p03 = {
        "1": {"class_type": "LoadImage", "inputs": {"image": REF}},
        "2": {"class_type": "UNETLoader", "inputs": {"unet_name": "krea2_turbo_int8_convrot.safetensors", "weight_dtype": "default"}},
        "3": {"class_type": "CLIPLoader", "inputs": {"clip_name": "qwen3vl_4b_fp8_scaled.safetensors", "type": "krea2"}},
        "4": {"class_type": "VAELoader", "inputs": {"vae_name": "qwen_image_vae.safetensors"}},
        "5": {"class_type": "EmptyLatentImage", "inputs": {"width": W, "height": H, "batch_size": 1}},
        "6": {"class_type": "Krea2StyleReference", "inputs": {"vae": ["4", 0], "target_latent": ["5", 0], "reference_image": ["1", 0], "fit": "crop", "upscale_method": "lanczos"}},
        "7": {"class_type": "CLIPTextEncode", "inputs": {"text": ALARA, "clip": ["3", 0]}},
        "8": {"class_type": "CLIPTextEncode", "inputs": {"text": NEG, "clip": ["3", 0]}},
        "9": {"class_type": "Krea2StyleTransfer", "inputs": {"model": ["2", 0], "reference_latent": ["6", 0], "ref_conditioning": ["7", 0], "mode": "recommended", "style_strength": 1.0, "value_adain_strength": 0.65, "ref_value_mix": 1.0, "ref_k_strength": 1.06, "rf_mode": "flowturbo_pc", "gamma": 0.5, "beta": 2.5, "high_scale_start": 1.04, "high_scale_end": 0.0, "low_scale_start": 1.0, "low_scale_end": 1.1, "adain_strength": 0.85, "blocks": "7-27"}},
        "10": {"class_type": "KSampler", "inputs": {"seed": 2026095002, "steps": 28, "cfg": 1.0, "sampler_name": "euler", "scheduler": "simple", "denoise": 1.0, "model": ["9", 0], "positive": ["7", 0], "negative": ["8", 0], "latent_image": ["5", 0]}},
        "11": {"class_type": "VAEDecode", "inputs": {"samples": ["10", 0], "vae": ["4", 0]}},
        "12": {"class_type": "SaveImage", "inputs": {"filename_prefix": "alara_P03_single", "images": ["11", 0]}},
    }

    print("\n=== P-03 kref 风格参考 ===")
    r = submit_wait(wf_p03, "P03-single", "alara_P03_single.png", timeout=600)
    if r:
        write_meta("alara_P03_single.png",
                   需求="gt_character_test001", 图名="alara", 管线="P03",
                   迭代="single", 批次="b01",
                   seed=2026095002, steps=28, cfg=1.0, denoise=1.0,
                   尺寸=f"{W}x{H}",
                   生成耗时_s=round(r["duration"], 1),
                   提交时间=datetime.now().isoformat(timespec="seconds"),
                   参考图=REF,
                   参考图来源="alara_3.jpg (单人艾拉拉官方参考)")

    print("\n完成")
