# -*- coding: utf-8 -*-
"""为新产品集生成 3x 规格图（供 OCR）与索引"""
import json, os
from PIL import Image
ROOT="/Users/zhanghao/WorkBuddy/新大地五金网站-v2"
SRC="/Users/zhanghao/Documents/新大地五金/4.官网产品材料"
ps=json.load(open(f"{ROOT}/.workbuddy/tmp/products_v3.json"))
os.makedirs('/tmp/ocr3', exist_ok=True)
paths, mapping = [], []
for i,p in enumerate(ps):
    if not p.get('spec_src'): continue
    im=Image.open(os.path.join(SRC,p['spec_src'])).convert('RGB')
    w,h=im.size
    k = 3 if max(w,h)*3 <= 2400 else 2
    im=im.resize((w*k,h*k), Image.LANCZOS)
    o=f'/tmp/ocr3/{len(paths):03d}.png'
    im.save(o)
    paths.append(o); mapping.append(dict(idx=len(paths)-1, slug=os.path.splitext(os.path.basename(p['img']))[0]))
open('/tmp/ocr3_paths.txt','w').write('\n'.join(paths))
json.dump(mapping, open('/tmp/ocr3_map.json','w'), ensure_ascii=False)
print('待 OCR:', len(paths))
