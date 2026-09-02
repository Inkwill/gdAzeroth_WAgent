# -*- coding: utf-8 -*-
"""全管线基准测试：P-01~P-04 各 1 次，模型热缓存后取纯生成耗时。
需求：#10 卖点图 · 双人羁绊（4:3 · 1024×768）· 命名 GT_10_bond_P<ID>
用法：D:/Comfy-Desktop/ComfyUI-Installs/ComfyUI/standalone-env/python.exe tools/benchmark_pipelines.py
"""
import json, time, urllib.request

API = "http://127.0.0.1:8188"
POS = ("3D Pixar-style render, stylized 3D cartoon character design, NOT 2D flat illustration, "
"PBR materials with cel-shading hybrid, soft volumetric lighting, subsurface scattering on skin, "
"cinematic three-point lighting, realistic body proportions with stylized 3D characters, "
"extreme close-up shot, hands and fabric fill 60-80 percent of the frame, "
"very shallow depth of field f/1.4 effect, background heavily blurred into warm bokeh light spots, "
"Alara's gentle hands sewing a torn patchwork jacket for Noah, "
"needle and thread passing through frayed worn fabric, visible mending stitches with tiny vine patterns, "
"Alara's fingertips in frame, Noah's shoulder barely entering frame edge, "
"soft warm smile on his half-visible face, "
"cozy indoor shelter interior, living room by warm fireplace, blurred cozy background, "
"handcrafted wooden furniture, soft wool blankets, patchwork clothes hanging near hearth, "
"warm color temperature, cozy hopeful healing atmosphere, "
"warm orange healing green cozy brown color palette with #90EE90 healing green accents, "
"soft volumetric light, NOT horror, NOT cold color palette, NOT chibi, NOT 2D line art, NOT anime")
NEG = ("2D flat illustration, 2D anime, line art, chibi, chibi style, deformed body proportions, "
"realistic photographic style, horror, gore, dark mood, text, watermark, logo, "
"deformed hands, extra fingers, low quality, blurry, ugly, cold color palette, neon green, "
"oversaturated, flat shading without depth, no 3D rendering")

def post(url, payload):
    req = urllib.request.Request(url, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())

def get(url):
    with urllib.request.urlopen(url, timeout=30) as r:
        return json.loads(r.read())

def run(wf, tag, timeout=2400):
    t0 = time.time()
    resp = post(API + "/prompt", {"prompt": wf, "client_id": "bench-" + str(int(t0))})
    pid = resp.get("prompt_id")
    if not pid:
        print(f"[{tag}] SUBMIT FAIL: {resp}")
        return None
    while time.time() - t0 < timeout:
        try:
            h = get(f"{API}/history/{pid}")
        except Exception:
            h = {}
        if pid in h:
            st = h[pid].get("status", {}).get("status_str")
            if st in ("success", "error"):
                dt = time.time() - t0
                fn = [i.get("filename") for o in h[pid].get("outputs", {}).values()
                      for i in o.get("images", [])]
                print(f"[{tag}] {st} | {dt:.1f}s | {fn}")
                return dt
        time.sleep(3)
    print(f"[{tag}] TIMEOUT")
    return None

def wf_p01(prefix, seed, steps):
    return {
        "1": {"class_type": "UNETLoader", "inputs": {"unet_name": "krea2_turbo_int8_convrot.safetensors", "weight_dtype": "default"}},
        "2": {"class_type": "CLIPLoader", "inputs": {"clip_name": "qwen3vl_4b_fp8_scaled.safetensors", "type": "krea2"}},
        "3": {"class_type": "VAELoader", "inputs": {"vae_name": "qwen_image_vae.safetensors"}},
        "4": {"class_type": "CLIPTextEncode", "inputs": {"text": POS, "clip": ["2", 0]}},
        "5": {"class_type": "CLIPTextEncode", "inputs": {"text": NEG, "clip": ["2", 0]}},
        "6": {"class_type": "EmptyLatentImage", "inputs": {"width": 1024, "height": 768, "batch_size": 1}},
        "7": {"class_type": "KSampler", "inputs": {"seed": seed, "steps": steps, "cfg": 1.0, "sampler_name": "euler", "scheduler": "simple", "denoise": 1.0, "model": ["1", 0], "positive": ["4", 0], "negative": ["5", 0], "latent_image": ["6", 0]}},
        "8": {"class_type": "VAEDecode", "inputs": {"samples": ["7", 0], "vae": ["3", 0]}},
        "9": {"class_type": "SaveImage", "inputs": {"filename_prefix": prefix, "images": ["8", 0]}},
    }

def wf_p02(prefix, seed):
    return {
        "1": {"class_type": "LoadImage", "inputs": {"image": "role-concept-1.jpg"}},
        "2": {"class_type": "UNETLoader", "inputs": {"unet_name": "krea2_turbo_int8_convrot.safetensors", "weight_dtype": "default"}},
        "3": {"class_type": "CLIPLoader", "inputs": {"clip_name": "qwen3vl_4b_fp8_scaled.safetensors", "type": "krea2"}},
        "4": {"class_type": "VAELoader", "inputs": {"vae_name": "qwen_image_vae.safetensors"}},
        "5": {"class_type": "CLIPTextEncode", "inputs": {"text": POS, "clip": ["3", 0]}},
        "6": {"class_type": "CLIPTextEncode", "inputs": {"text": NEG, "clip": ["3", 0]}},
        "7": {"class_type": "ImageScale", "inputs": {"image": ["1", 0], "upscale_method": "lanczos", "width": 1024, "height": 768, "crop": "center"}},
        "8": {"class_type": "VAEEncode", "inputs": {"pixels": ["7", 0], "vae": ["4", 0]}},
        "9": {"class_type": "KSampler", "inputs": {"seed": seed, "steps": 28, "cfg": 1.0, "sampler_name": "euler", "scheduler": "simple", "denoise": 0.55, "model": ["2", 0], "positive": ["5", 0], "negative": ["6", 0], "latent_image": ["8", 0]}},
        "10": {"class_type": "VAEDecode", "inputs": {"samples": ["9", 0], "vae": ["4", 0]}},
        "11": {"class_type": "SaveImage", "inputs": {"filename_prefix": prefix, "images": ["10", 0]}},
    }

def wf_p03(prefix, seed):
    return {
        "1": {"class_type": "LoadImage", "inputs": {"image": "role-concept-1.jpg"}},
        "2": {"class_type": "UNETLoader", "inputs": {"unet_name": "krea2_turbo_int8_convrot.safetensors", "weight_dtype": "default"}},
        "3": {"class_type": "CLIPLoader", "inputs": {"clip_name": "qwen3vl_4b_fp8_scaled.safetensors", "type": "krea2"}},
        "4": {"class_type": "VAELoader", "inputs": {"vae_name": "qwen_image_vae.safetensors"}},
        "5": {"class_type": "EmptyLatentImage", "inputs": {"width": 1024, "height": 768, "batch_size": 1}},
        "6": {"class_type": "Krea2StyleReference", "inputs": {"vae": ["4", 0], "target_latent": ["5", 0], "reference_image": ["1", 0], "fit": "crop", "upscale_method": "lanczos"}},
        "7": {"class_type": "CLIPTextEncode", "inputs": {"text": POS, "clip": ["3", 0]}},
        "8": {"class_type": "CLIPTextEncode", "inputs": {"text": NEG, "clip": ["3", 0]}},
        "9": {"class_type": "Krea2StyleTransfer", "inputs": {"model": ["2", 0], "reference_latent": ["6", 0], "ref_conditioning": ["7", 0], "mode": "recommended", "style_strength": 1.0, "value_adain_strength": 0.65, "ref_value_mix": 1.0, "ref_k_strength": 1.06, "rf_mode": "flowturbo_pc", "gamma": 0.5, "beta": 2.5, "high_scale_start": 1.04, "high_scale_end": 0.0, "low_scale_start": 1.0, "low_scale_end": 1.1, "adain_strength": 0.85, "blocks": "7-27"}},
        "10": {"class_type": "KSampler", "inputs": {"seed": seed, "steps": 28, "cfg": 1.0, "sampler_name": "euler", "scheduler": "simple", "denoise": 1.0, "model": ["9", 0], "positive": ["7", 0], "negative": ["8", 0], "latent_image": ["5", 0]}},
        "11": {"class_type": "VAEDecode", "inputs": {"samples": ["10", 0], "vae": ["4", 0]}},
        "12": {"class_type": "SaveImage", "inputs": {"filename_prefix": prefix, "images": ["11", 0]}},
    }

def wf_p04(prefix, seed, steps):
    return {
        "1": {"class_type": "UNETLoader", "inputs": {"unet_name": "z_image_turbo_bf16.safetensors", "weight_dtype": "default"}},
        "2": {"class_type": "CLIPLoader", "inputs": {"clip_name": "qwen_3_4b.safetensors", "type": "lumina2", "device": "default"}},
        "3": {"class_type": "VAELoader", "inputs": {"vae_name": "ae.safetensors"}},
        "4": {"class_type": "CLIPTextEncode", "inputs": {"text": POS, "clip": ["2", 0]}},
        "5": {"class_type": "CLIPTextEncode", "inputs": {"text": NEG, "clip": ["2", 0]}},
        "6": {"class_type": "EmptySD3LatentImage", "inputs": {"width": 1024, "height": 768, "batch_size": 1}},
        "7": {"class_type": "ModelSamplingAuraFlow", "inputs": {"shift": 3.0, "model": ["1", 0]}},
        "8": {"class_type": "KSampler", "inputs": {"seed": seed, "steps": steps, "cfg": 1.0, "sampler_name": "res_multistep", "scheduler": "simple", "denoise": 1.0, "model": ["7", 0], "positive": ["4", 0], "negative": ["5", 0], "latent_image": ["6", 0]}},
        "9": {"class_type": "VAEDecode", "inputs": {"samples": ["8", 0], "vae": ["3", 0]}},
        "10": {"class_type": "SaveImage", "inputs": {"filename_prefix": prefix, "images": ["9", 0]}},
    }

if __name__ == "__main__":
    print("queue:", get(API + "/queue")["queue_running"], get(API + "/queue")["queue_pending"])
    results = {}
    run(wf_p01("GT_10_bond_P01_warmup", 2026091099, 8), "P01-warmup(krea2 冷加载)")
    results["P01"] = run(wf_p01("GT_10_bond_P01", 2026091001, 30), "P01 标准30步")
    results["P02"] = run(wf_p02("GT_10_bond_P02", 2026091002), "P02 denoise0.55")
    results["P03"] = run(wf_p03("GT_10_bond_P03", 2026091003), "P03 kref风格参考")
    run(wf_p04("GT_10_bond_P04_warmup", 2026091098, 8), "P04-warmup(z_image 冷加载)")
    results["P04"] = run(wf_p04("GT_10_bond_P04", 2026091004, 8), "P04 Z-Image 8步")
    print("\n=== BENCHMARK SUMMARY (秒) ===")
    for k, v in results.items():
        print(f"{k}: {v:.1f}s" if v else f"{k}: FAIL")
