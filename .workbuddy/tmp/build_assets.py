# -*- coding: utf-8 -*-
import os, re, json
from PIL import Image

SRC = "/Users/zhanghao/Documents/新大地五金/官网材料整合/4.官网产品材料"
HERO = "/Users/zhanghao/Documents/新大地五金/官网材料整合/3.内页6张图2"
OUT  = "/Users/zhanghao/WorkBuddy/新大地五金网站-v2/assets/img"
IMG_EXT = ('.png', '.jpg', '.jpeg')

CAT = {  # 源目录序号 -> (id, 中文, 英文)
 '1.工具柜': ('cabinets', '工具柜', 'Tool Cabinets'),
 '2.工具车': ('carts',    '工具车', 'Tool Carts'),
 '3.支架':   ('stands',   '支架',   'Stands'),
 '4.工作桌': ('benches',  '工作桌', 'Workbenches'),
 '5.烧烤':   ('grills',   '烧烤炉', 'Grills'),
 '6.其他':   ('others',   '其他钣金制品', 'Other Sheet Metal'),
}
SUB_EN = {'工具箱':'Tool Box','组合柜':'Combination Cabinet','工具推车':'Tool Trolley',
 '焊接车':'Welding Cart','手推车':'Push Cart','铁板烧':'Griddle','气炉':'Gas Grill',
 '颗粒炉':'Pellet Grill','炭炉':'Charcoal Grill','柴火炉':'Fire Pit','桌面炉':'Tabletop Grill',
 '烟熏炉':'Smoker'}

def slugify(s):
    s = s.lower()
    s = s.replace('&',' and ')
    s = re.sub(r'[^a-z0-9]+','-',s).strip('-')
    return s

def pick_image(files):
    """返回 (文件名, 是否规格图需裁剪)"""
    names = [f for f in files if f.lower().endswith(IMG_EXT)]
    cut = [f for f in names if f.lower() in ('png.png','png.jpg')]
    if cut: return cut[0], False
    big = []
    for f in names:
        p = os.path.join(cur, f)
        im = Image.open(p)
        if im.mode in ('RGBA','LA','P') and im.size[0]*im.size[1] > 500*500:
            big.append((im.size[0]*im.size[1], f))
        elif im.size[0] > 1600 and im.size[1] > 1600:
            big.append((im.size[0]*im.size[1], f))
    if big:
        big.sort(reverse=True)
        return big[0][1], False
    # 只剩规格图（约 250x430 竖版）→ 需裁剪出产品图
    spec = [f for f in names if os.path.splitext(f)[1].lower() in ('.png','.jpg')]
    spec.sort(key=lambda f: -os.path.getsize(os.path.join(cur,f)))
    return spec[0], True

def crop_from_spec(im):
    """从规格图里裁出产品照片区（白框内），再自动去白边"""
    w, h = im.size
    box = (int(w*0.06), int(h*0.06), int(w*0.95), int(h*0.57))
    im = im.crop(box).convert('RGBA')
    # 自动去掉近白边框
    px = im.load()
    def near_white(c): return c[0] > 246 and c[1] > 246 and c[2] > 246
    W, H = im.size
    top, bottom, left, right = 0, H, 0, W
    while top < H and all(near_white(px[x, top]) for x in range(W)): top += 1
    while bottom > top and all(near_white(px[x, bottom-1]) for x in range(W)): bottom -= 1
    while left < W and all(near_white(px[left, y]) for y in range(top, bottom)): left += 1
    while right > left and all(near_white(px[right-1, y]) for y in range(top, bottom)): right -= 1
    return im.crop((left, top, right, bottom))

def to_square_webp(im, out_path, size=900, pad_ratio=0.045, white_bg=False):
    im = im.convert('RGBA')
    bbox = im.getbbox()
    if bbox: im = im.crop(bbox)
    if max(im.size) > 1400:          # 先降采样，避免大图占内存/耗时
        im.thumbnail((1400, 1400), Image.LANCZOS)
    w, h = im.size
    side = int(max(w, h) * (1 + pad_ratio*2))
    canvas = Image.new('RGBA', (side, side), (255,255,255,255) if white_bg else (255,255,255,0))
    canvas.paste(im, ((side-w)//2, (side-h)//2), im)
    canvas = canvas.resize((size, size), Image.LANCZOS)
    canvas.save(out_path, 'WEBP', quality=88, method=6)

products = []
for catdir in sorted(os.listdir(SRC)):
    if catdir not in CAT: continue
    cid, czh, cen = CAT[catdir]
    os.makedirs(f"{OUT}/products/{cid}", exist_ok=True)
    cpath = os.path.join(SRC, catdir)
    l1 = [d for d in sorted(os.listdir(cpath)) if os.path.isdir(os.path.join(cpath,d)) and not d.startswith('.')]
    if not l1: 
        print(f"[空分类] {catdir}"); continue
    has_sub = any(not [f for f in os.listdir(os.path.join(cpath,d)) if f.lower().endswith(IMG_EXT)] for d in l1)
    for d in l1:
        p1 = os.path.join(cpath, d)
        if has_sub:
            subzh = re.sub(r'^\d+\.','',d)
            prod_dirs = [os.path.join(p1,x) for x in sorted(os.listdir(p1)) if os.path.isdir(os.path.join(p1,x)) and not x.startswith('.')]
        else:
            subzh = ''
            prod_dirs = [p1]
        for pd in prod_dirs:
            print("  >>", os.path.basename(pd), flush=True)
            global cur
            cur = pd
            folder = re.sub(r'^\d+\.','', os.path.basename(pd))
            files = [f for f in os.listdir(pd) if not f.startswith('.')]
            fname, need_crop = pick_image(files)
            im = Image.open(os.path.join(pd, fname))
            if need_crop: im = crop_from_spec(im)
            # 型号 / 名称
            is_new = folder.startswith('新品')
            body = folder.replace('新品','').strip()
            m = re.match(r'^([A-Z]{2,6}[- ]?\d[A-Z0-9]*[A-Z0-9-]*)\s*(.*)$', body)
            if m:
                code, name = m.group(1), m.group(2).strip()
            elif re.match(r'^[A-Z]{2,6}-\d', body):
                code, name = body, ''
            else:
                code, name = '', body
            # 特殊情况：FP100701-火盆（带鼓风机）
            m2 = re.match(r'^([A-Z]{2,6}\d{4,})-(.+)$', body)
            if m2 and not code: code, name = m2.group(1), m2.group(2)
            if code.startswith('FP') and '火盆' in name:
                pass
            name = name.replace('SRORAGE','Storage').replace('BARCKET','Bracket').replace('cabniet','Cabinet')
            name = name.replace('with LID','With Lid').replace('with folding legs','With Folding Legs')
            name = name.replace('1 drawer','1-Drawer').replace('2 drawer','2-Drawer')
            name = re.sub(r'\s+',' ',name).strip()
            if name and name[0].islower(): name = name[0].upper()+name[1:]
            name = name.replace('cabinet','Cabinet').replace('chest','Chest').replace('locker','Locker')
            sl = slugify((code + ' ' + name).strip()) or f"{cid}-new-{len(products)+1}"
            out = f"{OUT}/products/{cid}/{sl}.webp"
            white = im.mode not in ('RGBA',) and fname.lower().endswith('.jpg')
            to_square_webp(im, out, white_bg=white)
            products.append(dict(cat=cid, sub=SUB_EN.get(subzh,''), subzh=subzh, code=code, name=name,
                                 img=f"assets/img/products/{cid}/{sl}.webp", is_new=is_new,
                                 src=os.path.relpath(os.path.join(pd,fname), SRC)))
# 主图
os.makedirs(f"{OUT}/category", exist_ok=True)
for catdir in sorted(os.listdir(HERO)):
    if catdir not in CAT: continue
    cid = CAT[catdir][0]
    f = [x for x in os.listdir(os.path.join(HERO,catdir)) if x.lower().endswith(('.jpg','.png'))][0]
    im = Image.open(os.path.join(HERO,catdir,f)).convert('RGB')
    im.save(f"{OUT}/category/hero-{cid}.webp", 'WEBP', quality=82, method=6)
    print("hero", cid, im.size, round(os.path.getsize(f"{OUT}/category/hero-{cid}.webp")/1024), "KB")

json.dump(products, open('/Users/zhanghao/WorkBuddy/新大地五金网站-v2/.workbuddy/tmp/products.json','w'), ensure_ascii=False, indent=1)
print("产品数", len(products))
for p in products:
    print(f"{p['cat']:9} {p['sub'][:14]:15} {p['code']:14} {p['name']:32} {'NEW ' if p['is_new'] else ''}{p['img'].split('/')[-1]}")
