# -*- coding: utf-8 -*-
"""把规格图底部“参数文字块”裁掉，只留产品照片；纯文字的规格表标记为无图"""
import json, os, re
from PIL import Image

ROOT = "/Users/zhanghao/WorkBuddy/新大地五金网站-v2"
SRC  = "/Users/zhanghao/Documents/新大地五金/官网材料整合/4.官网产品材料"
OUT  = f"{ROOT}/assets/img/specs"
specs = json.load(open(f"{ROOT}/.workbuddy/tmp/specs.json"))

raw = open('/tmp/ocr_boxes.txt').read()
parts = re.split(r'#{5,}\s*/tmp/ocr_spec/(\d+)\.png\s*#{5,}', raw)
it = iter(parts[1:])
blocks = {int(i): b for i, b in zip(it, it)}

LABEL = re.compile(r'(总的来说|总的|Overall|OVERALL|产品尺寸|外形尺寸|热输入|烹饪区域|烹饪面积|Package|PACKAGE|套餐|包装尺寸|包装|数量|Qty|QTY|装柜|尺寸\s*[:：])', re.I)

def cut_y(index, h):
    """返回应当裁掉的下边界（像素，按 1x 原图）；None 表示保持原图"""
    body = blocks.get(index, '')
    cand = []
    for line in body.splitlines():
        bits = line.split('\t')
        if len(bits) < 5:
            continue
        try:
            x, ytop, w, hh = float(bits[0]), float(bits[1]), float(bits[2]), float(bits[3])
        except ValueError:
            continue
        text = bits[4].strip()
        if ytop < 0.30:          # 标题区，跳过
            continue
        if LABEL.search(text):
            cand.append(ytop)
    if not cand:
        return None
    y = min(cand)
    return max(0, int(h * y) - int(h * 0.015))   # 留 1.5% 余量

rows = []
for i, s in enumerate(specs):
    src_path = os.path.join(SRC, s['src'])
    im = Image.open(src_path).convert('RGB')
    w, h = im.size
    text_only = h < 300          # 只有几行字的规格表（315×109 / 714×70 等）
    cropped = False
    if not text_only:
        y = cut_y(i, h)
        if y and y > h * 0.35:   # 裁完还剩大半张图，才算有效裁剪
            im = im.crop((0, 0, w, y))
            cropped = True

    # 去掉四周纯白边
    px = im.load()
    def near_white(c): return c[0] > 248 and c[1] > 248 and c[2] > 248
    W, H = im.size
    top, bottom, left, right = 0, H, 0, W
    while top < H - 1 and all(near_white(px[x, top]) for x in range(0, W, 3)): top += 1
    while bottom > top + 1 and all(near_white(px[x, bottom - 1]) for x in range(0, W, 3)): bottom -= 1
    while left < W - 1 and all(near_white(px[left, y]) for y in range(top, bottom, 3)): left += 1
    while right > left + 1 and all(near_white(px[right - 1, y]) for y in range(top, bottom, 3)): right -= 1
    im = im.crop((left, top, right, bottom))

    # 2x 放大存 webp
    nw, nh = im.size
    scale = 2 if max(nw, nh) * 2 <= 1100 else 1
    if scale > 1:
        im = im.resize((nw * scale, nh * scale), Image.LANCZOS)
    out = f"{OUT}/{s['cat']}/{s['slug']}.webp"
    im.save(out, 'WEBP', quality=88, method=6)
    rows.append(dict(cat=s['cat'], slug=s['slug'], spec=s['spec'], src=s['src'],
                     text_only=text_only, cropped=cropped,
                     orig=f"{w}x{h}", now=f"{im.size[0]}x{im.size[1]}",
                     kb=round(os.path.getsize(out) / 1024)))

json.dump(rows, open(f"{ROOT}/.workbuddy/tmp/spec_crops.json", 'w'), ensure_ascii=False, indent=1)
print(f"处理 {len(rows)} 张：裁掉参数块 {sum(1 for r in rows if r['cropped'])}，"
      f"纯文字无图 {sum(1 for r in rows if r['text_only'])}，"
      f"未裁 {sum(1 for r in rows if not r['cropped'] and not r['text_only'])}")
print("体积:", round(sum(r['kb'] for r in rows) / 1024, 1), "MB")
for r in rows[:6]:
    print(f"  {r['slug']:28} {r['orig']:>9} → {r['now']:>9} {'裁' if r['cropped'] else ('纯文字' if r['text_only'] else '未裁')}")
