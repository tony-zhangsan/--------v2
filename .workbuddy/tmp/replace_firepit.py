# -*- coding: utf-8 -*-
"""替换 FP100701 / FP100702 产品图：白底抠透明 → 按 render_v3 口径出 900x900 webp

SCALE 控制产品在画布上的占比（1.0 = 老图 FOOT 1.09 口径铺满画布；
客户要求「小一点」，0.62 = 相对老图缩到 62%，四周留白加大）。
"""
import numpy as np
from PIL import Image, ImageFilter
from scipy.ndimage import binary_propagation, binary_erosion

ROOT = "/Users/zhanghao/WorkBuddy/新大地五金网站-v2"
SCALE = 0.62          # 产品尺寸相对老图的比例
FOOT = 1.09 / SCALE   # 画布边长 = 物体长边 × FOOT
JOBS = [
    ("/Users/zhanghao/.workbuddy/clipboard-images/clipboard-2026-11-06T02-31-08-812Z-035d0bdf.jpg",
     f"{ROOT}/assets/img/products/grills/fp100701.webp"),
    ("/Users/zhanghao/.workbuddy/clipboard-images/clipboard-2026-11-06T02-31-08-813Z-c59b8e10.jpg",
     f"{ROOT}/assets/img/products/grills/fp100702.webp"),
]


def cutout(src):
    im = Image.open(src).convert("RGB")
    a = np.asarray(im).astype(np.int16)
    # 近白判定：最暗通道也很亮
    near_white = a.min(axis=2) >= 244
    # 从四条边界向内传播，只去掉与边缘连通的白色区域（保住产品内部高光）
    seeds = np.zeros_like(near_white)
    seeds[0, :] = near_white[0, :]
    seeds[-1, :] = near_white[-1, :]
    seeds[:, 0] = near_white[:, 0]
    seeds[:, -1] = near_white[:, -1]
    bg = binary_propagation(seeds, mask=near_white)
    fg = ~bg
    # 收缩 1px 去掉产品边缘的白边光晕
    fg = binary_erosion(fg, iterations=1)
    alpha = Image.fromarray((fg * 255).astype(np.uint8), "L")
    alpha = alpha.filter(ImageFilter.GaussianBlur(0.8))  # 软边抗锯齿
    out = im.convert("RGBA")
    out.putalpha(alpha)
    return out


for src, dst in JOBS:
    im = cutout(src)
    b = im.getbbox()
    if b:
        im = im.crop(b)
    w, h = im.size
    side = int(round(max(w, h) * FOOT))
    c = Image.new("RGBA", (side, side), (255, 255, 255, 0))
    c.paste(im, ((side - w) // 2, (side - h) // 2), im)
    c.resize((900, 900), Image.LANCZOS).save(dst, "WEBP", quality=86, method=4)
    print(dst.split("/")[-1], "crop", (w, h), "obj%", round(max(w, h) / side * 100, 1), "-> 900x900")
