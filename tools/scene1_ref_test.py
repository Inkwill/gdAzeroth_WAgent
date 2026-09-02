# -*- coding: utf-8 -*-
"""gt_scene_test001 · scene_1.jpg 视角参考 · P-02 img2ref + P-03 kref 各一张
竖版 576×1024（匹配 scene_1.jpg 9:16 构图）· 美术风格用 v4 设定"""
import json, time, urllib.request
from pathlib import Path
from datetime import datetime

API = "http://127.0.0.1:8188"
OUT = Path("C:/Users/inkse/gdAzeroth_WAgent/projects/green-tide/assets/gt_scene_test001")
REF = "scene_1.jpg"

# 美术风格（v4 提炼）：3D Pixar + cel-shading，末世破败
STYLE = (
    "3D Pixar-style render, stylized 3D cartoon character design, NOT 2D flat illustration, "
    "PBR materials with cel-shading hybrid, soft volumetric lighting, "
    "subsurface scattering on skin, cinematic three-point lighting, "
    "realistic body proportions with stylized 3D characters, "
    "NOT horror, NOT low poly, NOT low-poly background"
)

NEG = (
    "2D flat illustration, 2D anime, line art, chibi, chibi style, deformed body proportions, "
    "realistic photographic style, horror, gore, dark mood, text, watermark, logo, "
    "deformed hands, extra fingers, low quality, blurry, ugly, "
    "vibrant saturated colors, bright cheerful palette, sunny blue sky, "
    "lush green vegetation, neon green, oversaturated, "
    "low-poly, low poly, low-poly trees, low-poly background, low-poly vegetation, "
    "flat shading without depth, no 3D rendering, \"蜕变\""
)

# 末世设定（弱化具体布局/视角描述——由参考图主导构图）
PROMPT = (
    "Muted desaturated wasteland color palette, "
    "weathered gray-brown and faded olive tones, dusty atmosphere of decay and abandonment, "
    "small warm color accents from survivor details only. "
    "Stylized 3D cartoon illustration with full 3D Pixar-style render, "
    "PBR materials with cel-shading hybrid, soft volumetric lighting, cinematic three-point lighting. "
    "Post-apocalyptic small town scene with heavy decay: "
    "building walls deeply cracked and stained, roofs caved in with gaping holes, "
    "windows shattered with broken frames, signs tilted and rusted. "
    "Mutated vines overgrowing facades aggressively like a green tide, "
    "climbing walls and rooftops, tangling around chimneys. "
    "Giant mutant mushrooms (oversized, clustered) sprouting from windows and chimneys, "
    "pushing through broken walls. "
    "Thick mutant roots cracking and upheaving the pavement into jagged shards, "
    "roots bursting up through street cracks. "
    "Cracked streets with debris, abandoned vehicle wreckage, fallen leaves piling up. "
    "Survivors wearing survival gear: backpacks, bandages, goggles, dust masks, "
    "exhausted but alert, huddled close together. "
    "Improvised barricades, sandbags, hanging help-seeking cloth banners. "
    "Fully 3D stylized cartoon trees with PBR materials in background, not low-poly. "
    "Cozy hopeful healing atmosphere with hint of hope for restoration, "
    + STYLE
)

W, H = 576, 1024  # 竖版 9:16 匹配参考图


def post(url, payload):
    req = urllib.request.Request(url, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())

def get(url):
    with urllib.request.urlopen(url, timeout=30) as r:
        return json.loads(r.read())

def submit_wait(wf, tag, save_name, timeout=600):
    t0 = time.time()
    try:
        resp = post(API + "/prompt", {"prompt": wf, "client_id": f"gt-scene1-{int(t0)}"})
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

    # P-02 img2ref（denoise 0.45 多保留参考构图视角）
    wf_p02 = {
        "1": {"class_type": "LoadImage", "inputs": {"image": REF}},
        "2": {"class_type": "UNETLoader", "inputs": {"unet_name": "krea2_turbo_int8_convrot.safetensors", "weight_dtype": "default"}},
        "3": {"class_type": "CLIPLoader", "inputs": {"clip_name": "qwen3vl_4b_fp8_scaled.safetensors", "type": "krea2"}},
        "4": {"class_type": "VAELoader", "inputs": {"vae_name": "qwen_image_vae.safetensors"}},
        "5": {"class_type": "CLIPTextEncode", "inputs": {"text": PROMPT, "clip": ["3", 0]}},
        "6": {"class_type": "CLIPTextEncode", "inputs": {"text": NEG, "clip": ["3", 0]}},
        "7": {"class_type": "ImageScale", "inputs": {"image": ["1", 0], "upscale_method": "lanczos", "width": W, "height": H, "crop": "center"}},
        "8": {"class_type": "VAEEncode", "inputs": {"pixels": ["7", 0], "vae": ["4", 0]}},
        "9": {"class_type": "KSampler", "inputs": {"seed": 2026098001, "steps": 28, "cfg": 1.0, "sampler_name": "euler", "scheduler": "simple", "denoise": 0.45, "model": ["2", 0], "positive": ["5", 0], "negative": ["6", 0], "latent_image": ["8", 0]}},
        "10": {"class_type": "VAEDecode", "inputs": {"samples": ["9", 0], "vae": ["4", 0]}},
        "11": {"class_type": "SaveImage", "inputs": {"filename_prefix": "scene1_P02_v1_b01", "images": ["10", 0]}},
    }
    print("=== P-02 img2ref denoise=0.45（继承 scene_1.jpg 视角）===")
    r = submit_wait(wf_p02, "P02", "scene1_P02_v1_b01.png")
    if r:
        results["scene1_P02_v1_b01.png"] = r
        write_meta("scene1_P02_v1_b01.png",
                   需求="gt_scene_test001", 图名="scene1", 管线="P02",
                   迭代="v1", 批次="b01",
                   seed=2026098001, steps=28, cfg=1.0, denoise=0.45, 尺寸=f"{W}x{H}",
                   生成耗时_s=round(r["duration"], 1),
                   提交时间=datetime.now().isoformat(timespec="seconds"),
                   参考图=REF,
                   参考图来源="gdMain/.../reference/scene_1.jpg (竖版视角)",
                   提示词状态="v4 美术风格+末世设定")

    # P-03 kref 风格参考
    wf_p03 = {
        "1": {"class_type": "LoadImage", "inputs": {"image": REF}},
        "2": {"class_type": "UNETLoader", "inputs": {"unet_name": "krea2_turbo_int8_convrot.safetensors", "weight_dtype": "default"}},
        "3": {"class_type": "CLIPLoader", "inputs": {"clip_name": "qwen3vl_4b_fp8_scaled.safetensors", "type": "krea2"}},
        "4": {"class_type": "VAELoader", "inputs": {"vae_name": "qwen_image_vae.safetensors"}},
        "5": {"class_type": "EmptyLatentImage", "inputs": {"width": W, "height": H, "batch_size": 1}},
        "6": {"class_type": "Krea2StyleReference", "inputs": {"vae": ["4", 0], "target_latent": ["5", 0], "reference_image": ["1", 0], "fit": "crop", "upscale_method": "lanczos"}},
        "7": {"class_type": "CLIPTextEncode", "inputs": {"text": PROMPT, "clip": ["3", 0]}},
        "8": {"class_type": "CLIPTextEncode", "inputs": {"text": NEG, "clip": ["3", 0]}},
        "9": {"class_type": "Krea2StyleTransfer", "inputs": {"model": ["2", 0], "reference_latent": ["6", 0], "ref_conditioning": ["7", 0], "mode": "recommended", "style_strength": 1.0, "value_adain_strength": 0.65, "ref_value_mix": 1.0, "ref_k_strength": 1.06, "rf_mode": "flowturbo_pc", "gamma": 0.5, "beta": 2.5, "high_scale_start": 1.04, "high_scale_end": 0.0, "low_scale_start": 1.0, "low_scale_end": 1.1, "adain_strength": 0.85, "blocks": "7-27"}},
        "10": {"class_type": "KSampler", "inputs": {"seed": 2026098002, "steps": 28, "cfg": 1.0, "sampler_name": "euler", "scheduler": "simple", "denoise": 1.0, "model": ["9", 0], "positive": ["7", 0], "negative": ["8", 0], "latent_image": ["5", 0]}},
        "11": {"class_type": "VAEDecode", "inputs": {"samples": ["10", 0], "vae": ["4", 0]}},
        "12": {"class_type": "SaveImage", "inputs": {"filename_prefix": "scene1_P03_v1_b01", "images": ["11", 0]}},
    }
    print("\n=== P-03 kref 风格参考 ===")
    r = submit_wait(wf_p03, "P03", "scene1_P03_v1_b01.png", timeout=600)
    if r:
        results["scene1_P03_v1_b01.png"] = r
        write_meta("scene1_P03_v1_b01.png",
                   需求="gt_scene_test001", 图名="scene1", 管线="P03",
                   迭代="v1", 批次="b01",
                   seed=2026098002, steps=28, cfg=1.0, denoise=1.0, 尺寸=f"{W}x{H}",
                   生成耗时_s=round(r["duration"], 1),
                   提交时间=datetime.now().isoformat(timespec="seconds"),
                   参考图=REF,
                   参考图来源="gdMain/.../reference/scene_1.jpg (竖版视角)",
                   提示词状态="v4 美术风格+末世设定")

    print(f"\n=== 汇总 ({len(results)}/2) ===")
    for k, v in results.items():
        print(f"  {k}  {v['duration']:.1f}s")
