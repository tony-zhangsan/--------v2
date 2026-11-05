# -*- coding: utf-8 -*-
"""按新目录 4.官网产品材料 重建产品数据：7 个一级分类，图片统一用 png.png"""
import os, re, json
from PIL import Image

SRC = "/Users/zhanghao/Documents/新大地五金/4.官网产品材料"
OUT = "/Users/zhanghao/WorkBuddy/新大地五金网站-v2/assets/img/products"
TMP = "/Users/zhanghao/WorkBuddy/新大地五金网站-v2/.workbuddy/tmp"
IMG_EXT = ('.png', '.jpg', '.jpeg')

CAT = {  # 源目录 -> (id, 中文, 英文)
 '1.工具柜': ('cabinets',    '工具柜',   'Tool Cabinets'),
 '2.工具车': ('carts',       '工具车',   'Tool Carts'),
 '3.组合柜': ('combination', '组合柜',   'Combination Cabinets'),
 '4.工作桌': ('benches',     '工作台',   'Workbenches'),
 '5.支架':   ('stands',      '支架',     'Stands'),
 '6.烧烤':   ('grills',      '烧烤炉',   'Grills'),
 '7.其他':   ('others',      '其他钣金制品', 'Other Sheet Metal Products'),
}
SUB_EN = {'铁板烧':'Griddle','气炉':'Gas Grill','颗粒炉':'Pellet Grill','炭炉':'Charcoal Grill',
          '柴火炉':'Fire Pit','桌面炉':'Tabletop Grill','烟熏炉':'Smoker'}

def slugify(s):
    s = s.lower().replace('&', ' and ')
    return re.sub(r'[^a-z0-9]+', '-', s).strip('-')

def to_square(im, out, size=900, pad=0.045):
    im = im.convert('RGBA')
    b = im.getbbox()
    if b: im = im.crop(b)
    if max(im.size) > 1400: im.thumbnail((1400, 1400), Image.LANCZOS)
    w, h = im.size
    side = int(max(w, h) * (1 + pad * 2))
    canvas = Image.new('RGBA', (side, side), (255, 255, 255, 0))
    canvas.paste(im, ((side - w) // 2, (side - h) // 2), im)
    canvas.resize((size, size), Image.LANCZOS).save(out, 'WEBP', quality=86, method=4)

def norm_name(n):
    n = (n or '').replace('SRORAGE', 'Storage').replace('BARCKET', 'Bracket').replace('cabniet', 'Cabinet')
    n = n.replace('with LID', 'With Lid').replace('with folding legs', 'With Folding Legs')
    n = n.replace('1 drawer', '1-Drawer').replace('2 drawer', '2-Drawer')
    n = re.sub(r'\s+', ' ', n).strip()
    if n and n[0].islower(): n = n[0].upper() + n[1:]
    for a, b in (('cabinet', 'Cabinet'), ('chest', 'Chest'), ('locker', 'Locker')):
        n = n.replace(a, b)
    return ' '.join(w.capitalize() if (w.isupper() and len(w) > 1) else w for w in n.split())

import sys
A = sys.argv[1:]
FROM = int(A[A.index('--from')+1]) if '--from' in A else 0
TO   = int(A[A.index('--to')+1]) if '--to' in A else 10**6

products = []
seq = -1
for catdir in sorted(os.listdir(SRC)):
    if catdir not in CAT: continue
    cid, czh, cen = CAT[catdir]
    os.makedirs(f"{OUT}/{cid}", exist_ok=True)
    cpath = os.path.join(SRC, catdir)
    l1 = [d for d in sorted(os.listdir(cpath)) if os.path.isdir(os.path.join(cpath, d)) and not d.startswith('.')]
    if not l1:
        print(f"[空分类] {catdir}"); continue
    # 烧烤是三级结构（分类/子类/产品），其余扁平
    has_sub = any(not [f for f in os.listdir(os.path.join(cpath, d)) if f.lower().endswith(IMG_EXT)] for d in l1)
    for d in l1:
        p1 = os.path.join(cpath, d)
        if has_sub:
            subzh = re.sub(r'^\d+\.', '', d)
            prod_dirs = [os.path.join(p1, x) for x in sorted(os.listdir(p1)) if os.path.isdir(os.path.join(p1, x)) and not x.startswith('.')]
        else:
            subzh = ''
            prod_dirs = [p1]
        for pd in prod_dirs:
            seq += 1
            folder = re.sub(r'^\d+\.', '', os.path.basename(pd))
            if not (FROM <= seq < TO):
                # 跳过时仍要登记条目，保证序号/顺序一致
                files0 = [f for f in os.listdir(pd) if f.lower().endswith(IMG_EXT) and not f.startswith('.')]
                cut0 = [f for f in files0 if f.lower() in ('png.png', 'png.jpg')]
                img0 = cut0[0] if cut0 else (sorted(files0, key=lambda f: -os.path.getsize(os.path.join(pd,f)))[0] if files0 else '')
                spec0 = next((f for f in files0 if f != img0), '')
                body0 = folder.replace('新品','').strip()
                m0 = re.match(r'^([A-Z]{2,6}[- ]?\d[A-Z0-9]*[A-Z0-9-]*)\s*(.*)$', body0)
                code0, name0 = (m0.group(1), m0.group(2)) if m0 else ('', body0)
                m2 = re.match(r'^([A-Z]{2,6}\d{4,})-(.+)$', body0)
                if m2 and not code0: code0, name0 = m2.group(1), m2.group(2)
                products.append(dict(cat=cid, cat_zh=czh, cat_en=cen, sub=SUB_EN.get(subzh,''), subzh=subzh,
                    code=code0.strip('-').strip(), name=norm_name(name0), is_new=folder.startswith('新品'),
                    img='', src=os.path.relpath(os.path.join(pd, img0), SRC),
                    spec_src=os.path.relpath(os.path.join(pd, spec0), SRC) if spec0 else '',
                    order=int(re.match(r'^(\d+)', os.path.basename(pd)).group(1)) if re.match(r'^(\d+)', os.path.basename(pd)) else 999,
                    cat_order=list(CAT).index(catdir)))
                continue
            files = [f for f in os.listdir(pd) if f.lower().endswith(IMG_EXT) and not f.startswith('.')]
            # 展示图固定用 png.png；没有 png.png 时取剩下的那张里最大的
            cut = [f for f in files if f.lower() in ('png.png', 'png.jpg')]
            if cut:
                img_file = cut[0]
            else:
                files.sort(key=lambda f: -os.path.getsize(os.path.join(pd, f)))
                img_file = files[0]
            spec_file = next((f for f in files if f != img_file), '')

            is_new = folder.startswith('新品')
            body = folder.replace('新品', '').strip()
            m = re.match(r'^([A-Z]{2,6}[- ]?\d[A-Z0-9]*[A-Z0-9-]*)\s*(.*)$', body)
            if m:
                code, name = m.group(1), m.group(2)
            else:
                code, name = '', body
            m2 = re.match(r'^([A-Z]{2,6}\d{4,})-(.+)$', body)
            if m2 and not code: code, name = m2.group(1), m2.group(2)
            code = code.strip('-').strip()
            name = norm_name(name)
            if not code and not name: name = 'New Product'

            sl = slugify((code + ' ' + name).strip()) or f"{cid}-new-{len(products)+1}"
            out = f"{OUT}/{cid}/{sl}.webp"
            print(">>", cid, sl, img_file, flush=True)
            im = Image.open(os.path.join(pd, img_file))
            im.draft('RGB', (1400, 1400))          # JPEG 快速降采样（PNG 无效但无害）
            to_square(im, out)
            del im
            import gc; gc.collect()
            products.append(dict(
                cat=cid, cat_zh=czh, cat_en=cen,
                sub=SUB_EN.get(subzh, ''), subzh=subzh,
                code=code, name=name, is_new=is_new,
                img=f"assets/img/products/{cid}/{sl}.webp",
                src=os.path.relpath(os.path.join(pd, img_file), SRC),
                spec_src=os.path.relpath(os.path.join(pd, spec_file), SRC) if spec_file else '',
                order=int(re.match(r'^(\d+)', os.path.basename(pd)).group(1)) if re.match(r'^(\d+)', os.path.basename(pd)) else 999,
                cat_order=list(CAT).index(catdir),
            ))

products.sort(key=lambda p: (p['cat_order'], p['order']))
json.dump(products, open(f"{TMP}/products_v3.json", 'w'), ensure_ascii=False, indent=1)
from collections import Counter
c = Counter(p['cat'] for p in products)
print("产品总数:", len(products), dict(c))
print("无规格图:", [p['code'] or p['name'] for p in products if not p['spec_src']])
print("无 png.png（用了别的图）:", [p['src'] for p in products if not os.path.basename(p['src']).lower().startswith('png.')][:5])
