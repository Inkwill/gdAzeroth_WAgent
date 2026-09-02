# -*- coding: utf-8 -*-
"""gt_scene_test001 · P-01 + P-04 各 3 张 · #16 末世小镇（16:9 1024×576）"""
import json, time, urllib.request
from pathlib import Path
from datetime import datetime

API = "http://127.0.0.1:8188"
OUT = Path("C:/Users/inkse/gdAzeroth_WAgent/projects/green-tide/assets/gt_scene_test001")
OUT.mkdir(parents=True, exist_ok=True)

STYLE = ("3D Pixar-style render, stylized 3D cartoon scene design, NOT 2D flat illustration, "
"PBR materials with cel-shading hybrid, soft volumetric lighting, "
"cinematic three-point lighting, depth of field with foreground sharp and background hazy, "
"warm orange healing green cozy brown color palette with #90EE90 healing green accents, "
"post-apocalyptic wasteland transforming into vibrant lush green oasis, "
"cozy hopeful healing atmosphere with hint of hope, NOT horror, NOT cold color palette")

NEG = ("2D flat illustration, 2D anime, line art, chibi, chibi style, deformed body proportions, "
"realistic photographic style, horror, gore, dark mood, text, watermark, logo, "
"deformed hands, extra fingers, low quality, blurry, ugly, cold color palette, neon green, "
"oversaturated, flat shading without depth, no 3D rendering, \"蜕变\"")

PROMPT = (
    "stylized 3D cartoon illustration, cinematic wide establishing shot, "
    "16:9 composition, low-angle upward dramatic view, NOT 2D flat illustration. "
    "post-apocalyptic wasteland small town. "
    "Crumbled buildings with cracked walls and collapsed roofs, broken windows, tilted rusty signs. "
    "Mutated vines overgrowing facades, giant mushrooms sprouting from windows and chimneys, "
    "roots cracking the sidewalk pavement. "
    "Cracked streets with abandoned vehicle wreckage, garbage and fallen leaves piled up. "
    "3 survivors standing at the town entrance near an old damaged iron gate, "
    "wearing survival gear: backpacks, bandages, goggles, dust masks, improvised tools, "
    "exhausted but alert expressions, huddled close together for warmth. "
    "Improvised barricades, sandbags, hanging help-seeking cloth banners. "
    "Small faded town name sign visible on the gate arch. "
    "Foreground figures clear → midground buildings slightly hazy → background gray hazy sky. "
    "Hint of hope, beginning of healing journey. "
    + STYLE
)

W, H = 1024, 576


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


def wf_p04(seed, prefix):
    return {
        "1": {"class_type": "UNETLoader", "inputs": {"unet_name": "z_image_turbo_bf16.safetensors", "weight_dtype": "default"}},
        "2": {"class_type": "CLIPLoader", "inputs": {"clip_name": "qwen_3_4b.safetensors", "type": "lumina2", "device": "default"}},
        "3": {"class_type": "VAELoader", "inputs": {"vae_name": "ae.safetensors"}},
        "4": {"class_type": "CLIPTextEncode", "inputs": {"text": PROMPT, "clip": ["2", 0]}},
        "5": {"class_type": "CLIPTextEncode", "inputs": {"text": NEG, "clip": ["2", 0]}},
        "6": {"class_type": "EmptySD3LatentImage", "inputs": {"width": W, "height": H, "batch_size": 1}},
        "7": {"class_type": "ModelSamplingAuraFlow", "inputs": {"shift": 3.0, "model": ["1", 0]}},
        "8": {"class_type": "KSampler", "inputs": {"seed": seed, "steps": 8, "cfg": 1.0, "sampler_name": "res_multistep", "scheduler": "simple", "denoise": 1.0, "model": ["7", 0], "positive": ["4", 0], "negative": ["5", 0], "latent_image": ["6", 0]}},
        "9": {"class_type": "VAEDecode", "inputs": {"samples": ["8", 0], "vae": ["3", 0]}},
        "10": {"class_type": "SaveImage", "inputs": {"filename_prefix": prefix, "images": ["9", 0]}},
    }


def submit_wait(wf, tag, save_name, timeout=300):
    t0 = time.time()
    try:
        resp = post(API + "/prompt", {"prompt": wf, "client_id": f"gt-town-{int(t0)}"})
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

    # P-01 三张
    print("=== P-01 末世小镇 × 3 ===")
    for i, sd in enumerate([2026096001, 2026096002, 2026096003], 1):
        name = f"wasteland_town_P01_v1_b{i:02d}.png"
        r = submit_wait(wf_p01(sd, f"wasteland_town_P01_v1_b{i:02d}"), f"P01-b{i:02d}", name)
        if r:
            results[name] = r
            write_meta(name,
                       需求="gt_scene_test001", 图名="wasteland_town", 管线="P01",
                       迭代="v1", 批次=f"b{i:02d}",
                       seed=sd, steps=30, cfg=1.0, denoise=1.0, 尺寸=f"{W}x{H}",
                       生成耗时_s=round(r["duration"], 1),
                       提交时间=datetime.now().isoformat(timespec="seconds"),
                       提示词来源="ART-REQUIREMENTS.md P2 #16 + concept-art-prompts.md §1+§4.4")

    # P-04 三张
    print("\n=== P-04 末世小镇 × 3 ===")
    for i, sd in enumerate([2026096004, 2026096005, 2026096006], 1):
        name = f"wasteland_town_P04_v1_b{i:02d}.png"
        r = submit_wait(wf_p04(sd, f"wasteland_town_P04_v1_b{i:02d}"), f"P04-b{i:02d}", name)
        if r:
            results[name] = r
            write_meta(name,
                       需求="gt_scene_test001", 图名="wasteland_town", 管线="P04",
                       迭代="v1", 批次=f"b{i:02d}",
                       seed=sd, steps=8, cfg=1.0, denoise=1.0, 尺寸=f"{W}x{H}",
                       生成耗时_s=round(r["duration"], 1),
                       提交时间=datetime.now().isoformat(timespec="seconds"),
                       提示词来源="ART-REQUIREMENTS.md P2 #16 + concept-art-prompts.md §1+§4.4")

    print(f"\n=== 汇总 ({len(results)}/6) ===")
    total = sum(v["duration"] for v in results.values())
    for k, v in results.items():
        print(f"  {k}  {v['duration']:.1f}s")
    print(f"总耗时: {total:.1f}s")
    print(f"落盘: {OUT}")
