# -*- coding: utf-8 -*-
"""只扫描元数据（不处理图片），生成 products_v3.json —— 秒级完成"""
import os, re, json

SRC = "/Users/zhanghao/Documents/新大地五金/4.官网产品材料"
TMP = "/Users/zhanghao/WorkBuddy/新大地五金网站-v2/.workbuddy/tmp"
IMG_EXT = ('.png', '.jpg', '.jpeg')

CAT = {
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
    return re.sub(r'[^a-z0-9]+', '-', s.lower().replace('&', ' and ')).strip('-')

def norm_name(n):
    n = (n or '').replace('SRORAGE','Storage').replace('BARCKET','Bracket').replace('cabniet','Cabinet')
    n = n.replace('with LID','With Lid').replace('with folding legs','With Folding Legs')
    n = n.replace('1 drawer','1-Drawer').replace('2 drawer','2-Drawer')
    n = re.sub(r'\s+',' ',n).strip()
    if n and n[0].islower(): n = n[0].upper()+n[1:]
    for a,b in (('cabinet','Cabinet'),('chest','Chest'),('locker','Locker')):
        n = n.replace(a,b)
    return ' '.join(w.capitalize() if (w.isupper() and len(w)>1) else w for w in n.split())

def num(d):
    m = re.match(r'^(\d+)', d)
    return int(m.group(1)) if m else 999

products = []
for catdir in sorted(os.listdir(SRC)):
    if catdir not in CAT: continue
    cid, czh, cen = CAT[catdir]
    cpath = os.path.join(SRC, catdir)
    l1 = [d for d in sorted(os.listdir(cpath), key=num) if os.path.isdir(os.path.join(cpath,d)) and not d.startswith('.')]
    if not l1: continue
    has_sub = any(not [f for f in os.listdir(os.path.join(cpath,d)) if f.lower().endswith(IMG_EXT)] for d in l1)
    for d in l1:
        p1 = os.path.join(cpath, d)
        if has_sub:
            subzh = re.sub(r'^\d+\.','',d)
            prod_dirs = [os.path.join(p1,x) for x in sorted(os.listdir(p1), key=num) if os.path.isdir(os.path.join(p1,x)) and not x.startswith('.')]
        else:
            subzh = ''
            prod_dirs = [p1]
        for pd in prod_dirs:
            folder = re.sub(r'^\d+\.','', os.path.basename(pd))
            files = [f for f in os.listdir(pd) if f.lower().endswith(IMG_EXT) and not f.startswith('.')]
            cut = [f for f in files if f.lower() in ('png.png','png.jpg')]
            img_file = cut[0] if cut else (sorted(files, key=lambda f:-os.path.getsize(os.path.join(pd,f)))[0] if files else '')
            spec_file = next((f for f in files if f != img_file), '')

            is_new = folder.startswith('新品')
            body = folder.replace('新品','').strip()
            m = re.match(r'^([A-Z]{2,6}[- ]?\d[A-Z0-9]*[A-Z0-9-]*)\s*(.*)$', body)
            code, name = (m.group(1), m.group(2)) if m else ('', body)
            m2 = re.match(r'^([A-Z]{2,6}\d{4,})-(.+)$', body)
            if m2 and not code: code, name = m2.group(1), m2.group(2)
            code = code.strip('-').strip(); name = norm_name(name)
            if not code and not name: name = 'New Product'
            sl = slugify((code+' '+name).strip()) or f"{cid}-new-{len(products)+1}"

            products.append(dict(
                cat=cid, cat_zh=czh, cat_en=cen, sub=SUB_EN.get(subzh,''), subzh=subzh,
                code=code, name=name, is_new=is_new,
                img=f"assets/img/products/{cid}/{sl}.webp",
                src=os.path.relpath(os.path.join(pd,img_file), SRC),
                spec_src=os.path.relpath(os.path.join(pd,spec_file), SRC) if spec_file else '',
                cat_order=list(CAT).index(catdir), order=num(os.path.basename(pd)),
            ))

products.sort(key=lambda p:(p['cat_order'], p['order']))
json.dump(products, open(f"{TMP}/products_v3.json",'w'), ensure_ascii=False, indent=1)
from collections import Counter
print("产品", len(products), dict(Counter(p['cat'] for p in products)))
print("无规格图:", [p['code'] or p['name'] for p in products if not p['spec_src']])
