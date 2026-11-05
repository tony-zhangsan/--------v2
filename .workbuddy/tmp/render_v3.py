# -*- coding: utf-8 -*-
"""按 products_v3.json 生成产品图，支持分批：--from N --to M"""
import os, sys, json
from PIL import Image
ROOT="/Users/zhanghao/WorkBuddy/新大地五金网站-v2"
SRC="/Users/zhanghao/Documents/新大地五金/4.官网产品材料"
ps=json.load(open(f"{ROOT}/.workbuddy/tmp/products_v3.json"))
A=sys.argv[1:]
FROM=int(A[A.index('--from')+1]) if '--from' in A else 0
TO=int(A[A.index('--to')+1]) if '--to' in A else 10**6
for i,p in enumerate(ps):
    if not (FROM<=i<TO): continue
    out=os.path.join(ROOT,p['img'])
    os.makedirs(os.path.dirname(out), exist_ok=True)
    im=Image.open(os.path.join(SRC,p['src'])).convert('RGBA')
    b=im.getbbox()
    if b: im=im.crop(b)
    if max(im.size)>1400: im.thumbnail((1400,1400), Image.LANCZOS)
    w,h=im.size; side=int(max(w,h)*1.09)
    c=Image.new('RGBA',(side,side),(255,255,255,0))
    c.paste(im,((side-w)//2,(side-h)//2),im)
    c.resize((900,900), Image.LANCZOS).save(out,'WEBP',quality=86,method=4)
    print(f"[{i}] {p['cat']}/{os.path.basename(p['img'])}", flush=True)
print("done", FROM, TO)
