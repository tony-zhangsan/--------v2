# -*- coding: utf-8 -*-
"""为每个型号挑出规格图（第二张带参数的图），转 2x webp 供弹窗显示"""
import os, json, re
from PIL import Image

ROOT = "/Users/zhanghao/WorkBuddy/新大地五金网站-v2"
SRC  = "/Users/zhanghao/Documents/新大地五金/官网材料整合/4.官网产品材料"
OUT  = f"{ROOT}/assets/img/specs"
IMG_EXT = ('.png', '.jpg', '.jpeg')
PREFER = ('参数', '尺寸信息', '产品信息')

products = json.load(open(f"{ROOT}/.workbuddy/tmp/products.json"))

def spec_file(folder, chosen_name):
    files = [f for f in os.listdir(folder) if f.lower().endswith(IMG_EXT) and not f.startswith('.')]
    others = [f for f in files if f != chosen_name]
    for p in PREFER:
        hit = [f for f in others if p in f]
        if hit:
            return hit[0]
    if others:
        # 多个候选时选“竖版且面积偏小”的那张（规格图特征）
        def score(f):
            im = Image.open(os.path.join(folder, f))
            w, h = im.size
            return (0 if h > w else 1, w * h)
        others.sort(key=score)
        return others[0]
    return files[0]   # 只有一个文件：它就是规格图（产品图当时是从它裁的）

rows = []
for p in products:
    folder = os.path.join(SRC, os.path.dirname(p['src']))
    chosen = os.path.basename(p['src'])
    f = spec_file(folder, chosen)
    same = (f == chosen)
    src_path = os.path.join(folder, f)
    im = Image.open(src_path).convert('RGB')
    w, h = im.size
    # 2x 放大后存，弹窗里缩回来更清晰
    scale = 2 if max(w, h) * 2 <= 1000 else 1
    if scale > 1:
        im = im.resize((w * scale, h * scale), Image.LANCZOS)
    slug = os.path.splitext(os.path.basename(p['img']))[0]
    os.makedirs(f"{OUT}/{p['cat']}", exist_ok=True)
    out = f"{OUT}/{p['cat']}/{slug}.webp"
    im.save(out, 'WEBP', quality=86, method=6)
    rows.append(dict(cat=p['cat'], slug=slug, spec=f"assets/img/specs/{p['cat']}/{slug}.webp",
                     src=os.path.relpath(src_path, SRC), same_as_product=same,
                     size=f"{w}x{h}", kb=round(os.path.getsize(out)/1024)))

json.dump(rows, open("/Users/zhanghao/WorkBuddy/新大地五金网站-v2/.workbuddy/tmp/specs.json", "w"), ensure_ascii=False, indent=1)
print("规格图:", len(rows), "张")
print("与产品图同一张（无独立规格图）:", sum(1 for r in rows if r['same_as_product']))
print("总体积:", round(sum(r['kb'] for r in rows)/1024, 1), "MB")
for r in rows[:3]:
    print(r['spec'], r['size'], r['kb'], 'KB')
