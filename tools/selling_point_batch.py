# -*- coding: utf-8 -*-
"""selling_point_graphic · P3 三核卖点（#08 ASMR修复 / #09 避难所经营 / #10 双人羁绊）
P-01 × 3 + P-04 × 3（4:3 1024×768）· 项目标准暖色风格"""
import json, time, urllib.request
from pathlib import Path
from datetime import datetime

API = "http://127.0.0.1:8188"
OUT = Path("C:/Users/inkse/gdAzeroth_WAgent/projects/green-tide/assets/selling_point_graphic")
OUT.mkdir(parents=True, exist_ok=True)

# 项目标准风格块（卖点图 · 治愈暖调）
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
    "low-poly, low poly, flat shading without depth, no 3D rendering, \"蜕变\""
)

# ---- 三个卖点提示词（ART-REQUIREMENTS P3）----
# #08 ASMR 修复：修剪枯藤特写/微距
P08 = (
    "stylized 3D cartoon illustration, extreme close-up macro shot, "
    "hands with pruning shears cutting through thick charred-black mutated dead vine "
    "wrapped around a ruined wall corner, "
    "crisp satisfying clean cut line, "
    "scorched black leaves peeling off and drifting down as dynamic falling motion, "
    "fresh clean surface revealed beneath the cut, small green sprout emerging at the cut edge, "
    "macro texture detail on vine fibers and wood, "
    "cinematic lighting, shallow depth of field with soft bokeh, "
    + STYLE
)

# #09 避难所经营：核心场所横向全景
P09 = (
    "stylized 3D cartoon illustration, wide shot with horizontal narrative composition, "
    "NOT 2D flat illustration. "
    "Cozy shelter core facilities scene at warm dusk: "
    "glass greenhouse dome glowing with warm light and green plants inside, "
    "small clinic building with red cross sign, "
    "hand-pump water well in courtyard, "
    "all three facilities visible in one horizontal composition, facilities fill over 60 percent of frame, "
    "life details: cooking smoke rising from chimney, clothes hanging on a line, "
    "child figure playing in front, "
    "warm lanterns and glowing windows, "
    + STYLE
)

# #10 双人羁绊：艾拉拉替诺亚缝补破衣（大特写，沿用基准验证提示词）
P10 = (
    "stylized 3D cartoon illustration, extreme close-up shot, "
    "hands and fabric fill 60-80 percent of the frame, NOT 2D flat illustration. "
    "Alara's gentle hands sewing a torn patchwork jacket for Noah, "
    "needle and thread passing through frayed worn fabric, "
    "visible mending stitches with tiny vine patterns, "
    "Alara's fingertips in frame, Noah's shoulder barely entering frame edge, "
    "soft warm smile on his half-visible face, "
    "very shallow depth of field f/1.4 effect, background heavily blurred into warm bokeh light spots, "
    "cozy indoor shelter interior by warm fireplace, "
    "handcrafted wooden furniture, soft wool blankets, patchwork clothes hanging near hearth, "
    "warm color temperature, "
    + STYLE
)

W, H = 1024, 768  # 4:3


def post(url, payload):
    req = urllib.request.Request(url, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())

def get(url):
    with urllib.request.urlopen(url, timeout=30) as r:
        return json.loads(r.read())

def wf_p01(seed, prompt, prefix):
    return {
        "1": {"class_type": "UNETLoader", "inputs": {"unet_name": "krea2_turbo_int8_convrot.safetensors", "weight_dtype": "default"}},
        "2": {"class_type": "CLIPLoader", "inputs": {"clip_name": "qwen3vl_4b_fp8_scaled.safetensors", "type": "krea2"}},
        "3": {"class_type": "VAELoader", "inputs": {"vae_name": "qwen_image_vae.safetensors"}},
        "4": {"class_type": "CLIPTextEncode", "inputs": {"text": prompt, "clip": ["2", 0]}},
        "5": {"class_type": "CLIPTextEncode", "inputs": {"text": NEG, "clip": ["2", 0]}},
        "6": {"class_type": "EmptyLatentImage", "inputs": {"width": W, "height": H, "batch_size": 1}},
        "7": {"class_type": "KSampler", "inputs": {"seed": seed, "steps": 30, "cfg": 1.0, "sampler_name": "euler", "scheduler": "simple", "denoise": 1.0, "model": ["1", 0], "positive": ["4", 0], "negative": ["5", 0], "latent_image": ["6", 0]}},
        "8": {"class_type": "VAEDecode", "inputs": {"samples": ["7", 0], "vae": ["3", 0]}},
        "9": {"class_type": "SaveImage", "inputs": {"filename_prefix": prefix, "images": ["8", 0]}},
    }

def wf_p04(seed, prompt, prefix):
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

def submit_wait(wf, tag, save_name, timeout=300):
    t0 = time.time()
    try:
        resp = post(API + "/prompt", {"prompt": wf, "client_id": f"gt-spg-{int(t0)}"})
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
    # 需求 → (图名, 提示词, 需求号)
    jobs = [
        ("asmr_repair", P08, "#08 卖点图·ASMR修复"),
        ("shelter_life", P09, "#09 卖点图·避难所经营"),
        ("bond", P10, "#10 卖点图·双人羁绊"),
    ]
    results = {}

    # P-01 三张
    print("=== P-01 三核卖点 × 3 ===")
    for i, (fname, prompt, reqdesc) in enumerate(jobs, 1):
        sd = 2026099000 + i
        name = f"{fname}_P01_v1_b01.png"
        r = submit_wait(wf_p01(sd, prompt, f"{fname}_P01_v1_b01"), f"P01-{fname}", name)
        if r:
            results[name] = r
            write_meta(name,
                       需求="selling_point_graphic", 图名=fname, 管线="P01",
                       迭代="v1", 批次="b01",
                       seed=sd, steps=30, cfg=1.0, denoise=1.0, 尺寸=f"{W}x{H}",
                       生成耗时_s=round(r["duration"], 1),
                       提交时间=datetime.now().isoformat(timespec="seconds"),
                       需求来源=f"ART-REQUIREMENTS.md P3 {reqdesc}")

    # P-04 三张
    print("\n=== P-04 三核卖点 × 3 ===")
    for i, (fname, prompt, reqdesc) in enumerate(jobs, 1):
        sd = 2026099100 + i
        name = f"{fname}_P04_v1_b01.png"
        r = submit_wait(wf_p04(sd, prompt, f"{fname}_P04_v1_b01"), f"P04-{fname}", name)
        if r:
            results[name] = r
            write_meta(name,
                       需求="selling_point_graphic", 图名=fname, 管线="P04",
                       迭代="v1", 批次="b01",
                       seed=sd, steps=8, cfg=1.0, denoise=1.0, 尺寸=f"{W}x{H}",
                       生成耗时_s=round(r["duration"], 1),
                       提交时间=datetime.now().isoformat(timespec="seconds"),
                       需求来源=f"ART-REQUIREMENTS.md P3 {reqdesc}")

    print(f"\n=== 汇总 ({len(results)}/6) ===")
    total = sum(v["duration"] for v in results.values())
    for k, v in results.items():
        print(f"  {k}  {v['duration']:.1f}s")
    print(f"总耗时: {total:.1f}s")
    print(f"落盘: {OUT}")
