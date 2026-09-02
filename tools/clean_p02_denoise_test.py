# -*- coding: utf-8 -*-
"""P-02 denoise 敏感度测试：测 0.35 / 0.20 两档，看哪个能出干净单人"""
import json, time, urllib.request, urllib.error, subprocess
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

NOAH = (
    "stylized 3D cartoon character portrait, full body, centered, "
    "vertical 3:5 portrait composition, character sheet pose, NOT 2D flat illustration. "
    "17-year-old boy mechanic prodigy, 4.5-head-body realistic proportions, "
    "wild short hair with green and blue dyed streaks, "
    "modded goggles on head, mechanical prosthetic right arm with visible metal joints and bolts, "
    "patchwork wasteland streetwear with metal parts decorations and visible stitches, "
    "energetic orange and modified blue color scheme, "
    "cargo pants with tool pockets, sturdy boots, fingerless gloves. "
    "P14: 朋克乐观野性，标志性 peace-sign 手势举至面颊旁，露齿自信笑；"
    "机械义肢右手金属光泽与齿轮螺栓细节清晰可见；斜侧 3/4 角度增加动感. " + STYLE)

W, H = 614, 1024


def post(url, payload):
    req = urllib.request.Request(url, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())

def get(url):
    with urllib.request.urlopen(url, timeout=30) as r:
        return json.loads(r.read())

def upload(img_path):
    abs_p = str(Path(img_path).resolve())
    proc = subprocess.run(
        ["curl", "-s", "-X", "POST", "http://127.0.0.1:8188/upload/image",
         "-F", f"image=@{abs_p};type=image/png"],
        capture_output=True, text=True, timeout=30)
    return json.loads(proc.stdout).get("name")

def wf_p02(ref_img, seed, prompt, prefix, denoise):
    return {
        "1": {"class_type": "LoadImage", "inputs": {"image": ref_img}},
        "2": {"class_type": "UNETLoader", "inputs": {"unet_name": "krea2_turbo_int8_convrot.safetensors", "weight_dtype": "default"}},
        "3": {"class_type": "CLIPLoader", "inputs": {"clip_name": "qwen3vl_4b_fp8_scaled.safetensors", "type": "krea2"}},
        "4": {"class_type": "VAELoader", "inputs": {"vae_name": "qwen_image_vae.safetensors"}},
        "5": {"class_type": "CLIPTextEncode", "inputs": {"text": prompt, "clip": ["3", 0]}},
        "6": {"class_type": "CLIPTextEncode", "inputs": {"text": NEG, "clip": ["3", 0]}},
        "7": {"class_type": "ImageScale", "inputs": {"image": ["1", 0], "upscale_method": "lanczos", "width": W, "height": H, "crop": "center"}},
        "8": {"class_type": "VAEEncode", "inputs": {"pixels": ["7", 0], "vae": ["4", 0]}},
        "9": {"class_type": "KSampler", "inputs": {"seed": seed, "steps": 28, "cfg": 1.0, "sampler_name": "euler", "scheduler": "simple", "denoise": denoise, "model": ["2", 0], "positive": ["5", 0], "negative": ["6", 0], "latent_image": ["8", 0]}},
        "10": {"class_type": "VAEDecode", "inputs": {"samples": ["9", 0], "vae": ["4", 0]}},
        "11": {"class_type": "SaveImage", "inputs": {"filename_prefix": prefix, "images": ["10", 0]}},
    }

def run_one(wf, tag, save_name, timeout=300):
    t0 = time.time()
    try:
        resp = post(API + "/prompt", {"prompt": wf, "client_id": f"gt-dn-{int(t0)}"})
    except Exception as e:
        print(f"[{tag}] FAIL: {e}"); return None
    pid = resp.get("prompt_id")
    if not pid:
        print(f"[{tag}] no pid: {resp}"); return None
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
                    print(f"[{tag}] no images"); return None
                src = imgs[0]
                tgt = OUT / save_name
                with urllib.request.urlopen(f"{API}/view?filename={src['filename']}&type={src.get('type','output')}&subfolder={src.get('subfolder','')}", timeout=60) as r:
                    tgt.write_bytes(r.read())
                sz = tgt.stat().st_size // 1024
                print(f"[{tag}] OK | {dt:.1f}s | {save_name} ({sz}KB)")
                return {"duration": dt}
            elif st == "error":
                print(f"[{tag}] error"); return None
        time.sleep(3)
    print(f"[{tag}] TIMEOUT"); return None

def write_meta(name, **fields):
    lines = [f"{k}: {v}" for k, v in fields.items()]
    (OUT / name.replace(".png", ".yaml")).write_text("\n".join(lines) + "\n", encoding="utf-8")

if __name__ == "__main__":
    # 上传裁剪图
    alara_ref = upload(OUT / "ref_alara_crop.png")
    noah_ref = upload(OUT / "ref_noah_crop.png")
    print(f"refs: alara={alara_ref}, noah={noah_ref}\n")

    # denoise 敏感度测试：艾拉拉各测 0.35 / 0.20
    for dn in [0.35, 0.20]:
        tag = f"alara-dn{dn}"
        name = f"alara_P02_dn{dn}.png"
        r = run_one(wf_p02(alara_ref, 2026094001, ALARA, f"alara_P02_dn{dn}", dn), tag, name)
        if r:
            write_meta(name,
                       需求="gt_character_test001", 图名="alara", 管线="P02",
                       迭代=f"dn_test", 批次=f"dn{dn}",
                       seed=2026094001, steps=28, cfg=1.0, denoise=dn, 尺寸=f"{W}x{H}",
                       生成耗时_s=round(r["duration"], 1),
                       提交时间=datetime.now().isoformat(timespec="seconds"),
                       参考图=alara_ref,
                       提示词状态="clean",
                       备注=f"denoise敏感度测试: {dn}")
        print()

    # 诺亚各测 0.35 / 0.20
    for dn in [0.35, 0.20]:
        tag = f"noah-dn{dn}"
        name = f"noah_P02_dn{dn}.png"
        r = run_one(wf_p02(noah_ref, 2026094002, NOAH, f"noah_P02_dn{dn}", dn), tag, name)
        if r:
            write_meta(name,
                       需求="gt_character_test001", 图名="noah", 管线="P02",
                       迭代=f"dn_test", 批次=f"dn{dn}",
                       seed=2026094002, steps=28, cfg=1.0, denoise=dn, 尺寸=f"{W}x{H}",
                       生成耗时_s=round(r["duration"], 1),
                       提交时间=datetime.now().isoformat(timespec="seconds"),
                       参考图=noah_ref,
                       提示词状态="clean",
                       备注=f"denoise敏感度测试: {dn}")
        print()

    print("=== 完成：4 张 denoise 测试图 ===")
