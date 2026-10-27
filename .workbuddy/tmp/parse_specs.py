# -*- coding: utf-8 -*-
"""OCR 结果 → 三项参数（标签分段 + 单位归一 + mm/inch 互校）"""
import json, re

ROOT = "/Users/zhanghao/WorkBuddy/新大地五金网站-v2"
specs = json.load(open(f"{ROOT}/.workbuddy/tmp/specs.json"))
raw = open('/tmp/ocr_all.txt').read()

parts = re.split(r'#{5,}\s*/tmp/ocr_spec/(\d+)\.png\s*#{5,}', raw)
it = iter(parts[1:])
blocks = {int(i): b for i, b in zip(it, it)}

LBL_SIZE = r'(总\s*的\s*来\s*说|总\s*的|Overall|OVERALL|产品\s*尺寸|外形尺寸|Size|尺寸)'
LBL_PACK = r'(套\s*餐|餐\s*[:：]|Package|PACKAGE|包装\s*尺寸|包装|Packing)'
LBL_QTY  = r'(数\s*量|Qty|QTY|装\s*箱\s*量|集装箱的数量|装柜数\s*量|装柜数量)'

NUM = r'(\d{1,5}(?:[.,]\d+)?)'
UNIT = r'(mm|MM|毫米|inch|INCH|Inch|in|IN|英寸)'
TRIPLE = re.compile(NUM + r'\s*[WDHLwdh"”]?\s*[x×*X]\s*' + NUM + r'\s*[WDHLwdh]?\s*[x×*X]\s*' + NUM + r'\s*[WDHLwdh]?\s*' + UNIT)
TRIPLE_BARE = re.compile(NUM + r'\s*[x\u00d7*X]\s*' + NUM + r'\s*[x\u00d7*X]\s*' + NUM + r'(?![\d"\u201d])')
QTY = re.compile(r'(\d{1,5})\s*(?:件|[Pp][Cc][Ss])?\s*[/|l1]\s*40\s*H\s*Q', re.I)
TRIPLE_IN = re.compile(NUM + r'\s*["\u201d]\s*[WDHLwdh]?\s*[x\u00d7*X]\s*' + NUM + r'\s*["\u201d]\s*[WDHLwdh]?\s*[x\u00d7*X]\s*' + NUM + r'\s*["\u201d]\s*[WDHLwdh]?')


def norm_text(t):
    t = t.replace('，', ',').replace('：', ':').replace('（', '(').replace('）', ')')
    t = t.replace('毫米', 'mm').replace('英寸', 'inch')
    t = re.sub(r'\s+', ' ', t)          # 换行/多空格一并折叠，OCR 常把“套餐”拆成两行
    return t


def fmt(nums, unit):
    a, b, c = [n.replace(',', '.').rstrip('.') for n in nums]
    u = 'mm' if unit.lower() in ('mm', '毫米') else 'in'
    return f"{a} × {b} × {c} {u}", u


def parse(body):
    t = norm_text(body)
    trip = []
    for m in TRIPLE.finditer(t):
        nums = (m.group(1), m.group(2), m.group(3))
        try:
            vals = [float(n.replace(',', '.')) for n in nums]
        except ValueError:
            continue
        if not all(4 <= v <= 6000 for v in vals):
            continue
        s, u = fmt(nums, m.group(4))
        trip.append((m.start(), s, u, vals))
    for m in TRIPLE_IN.finditer(t):
        nums = (m.group(1), m.group(2), m.group(3))
        try:
            vals = [float(n.replace(',', '.')) for n in nums]
        except ValueError:
            continue
        if not all(4 <= v <= 240 for v in vals):     # 英寸：上限 240in（≈6m）
            continue
        trip.append((m.start(), f"{nums[0]} × {nums[1]} × {nums[2]} in", 'in', vals))

    zones = {}
    for name, pat in (('size', LBL_SIZE), ('pack', LBL_PACK), ('qty', LBL_QTY)):
        m = re.search(pat, t, re.I)
        zones[name] = m.start() if m else None

    def pick(lo, hi, unit):
        out = []
        for pos, s, u, vals in trip:
            if u != unit:
                continue
            if lo is not None and pos < lo:
                continue
            if hi is not None and pos > hi:
                continue
            out.append((pos, s))
        out.sort()
        return [s for _, s in out]

    size_lo, size_hi = zones['size'], zones['pack']
    pack_lo, pack_hi = zones['pack'], zones['qty']

    if not trip and (size_lo is not None):
        # 整张表没有任何单位：产品尺寸 / 包装尺寸 后面跟 236*236*238 这类裸数字，按 mm 处理
        bare = [(m.start(), m.group(1), m.group(2), m.group(3)) for m in TRIPLE_BARE.finditer(t)]
        for pos, a, b, c in bare:
            trip.append((pos, f"{a} × {b} × {c} mm", 'mm', [float(a), float(b), float(c)]))

    size_mm = pick(size_lo, size_hi if size_hi and size_lo is not None and size_hi > size_lo else None, 'mm')
    size_in = pick(size_lo, size_hi if size_hi and size_lo is not None and size_hi > size_lo else None, 'in')
    pack_mm = pick(pack_lo, None, 'mm') if pack_lo is not None else []
    pack_in = pick(pack_lo, None, 'in') if pack_lo is not None else []

    # 没有标签（或标签识别失败）时退化为“按出现顺序”
    if not size_mm and not size_in:
        allmm = [s for _, s, u, _ in trip if u == 'mm']
        allin = [s for _, s, u, _ in trip if u == 'in']
        size_mm = allmm[:1]
        size_in = allin[:1]
        pack_mm = pack_mm or allmm[1:2]
        pack_in = pack_in or allin[1:2]

    # OCR 有时把“套 餐”拆开、把数值夹在中间：此时取标签前最近的一组作为包装尺寸
    if not pack_mm and zones['pack'] is not None:
        before = [(pos, s_) for pos, s_, u_, _ in trip
                  if u_ == 'mm' and pos < zones['pack'] and s_ != (size_mm[0] if size_mm else None)]
        if before:
            pack_mm = [before[-1][1]]
    if not pack_in and zones['pack'] is not None:
        after = [(pos, s_) for pos, s_, u_, _ in trip if u_ == 'in' and pos > zones['pack']]
        if after:
            pack_in = [after[0][1]]

    q = QTY.search(t)
    if not q:
        m = re.search(r'(装柜数\s*量|装箱量|装柜数量)\s*[:：]?\s*(\d{2,5})', t)
        q = re.match(r'.*?(\d+)', m.group(2)) if m else None
    qty = f"{q.group(1)} pcs / 40HQ" if q else ''

    # mm / inch 互校：偏差超 4% 视为 OCR 误读，丢掉该单位
    def nums_of(s):
        return [float(x) for x in re.findall(r'\d+(?:\.\d+)?', s)[:3]]
    def consistent(mm_s, in_s):
        try:
            a, b = nums_of(mm_s), nums_of(in_s)
        except Exception:
            return False
        if len(a) < 3 or len(b) < 3:
            return False
        return all(abs(x / 25.4 - y) <= max(1.2, x / 25.4 * 0.04) for x, y in zip(a, b))

    sm = size_mm[0] if size_mm else ''
    si = size_in[0] if size_in else ''
    pm = pack_mm[0] if pack_mm else ''
    pi = pack_in[0] if pack_in else ''
    # 原表格里 mm 与 inch 对不上的（客户表本身有笔误）→ 只保留 mm，不发布可能错误的英寸值
    flag = ''
    if sm and si and not consistent(sm, si):
        si = ''
        flag = 'size_unit_bad'
    if pm and pi and not consistent(pm, pi):
        pi = ''
        flag = (flag + ' pack_unit_bad').strip()

    return dict(size_mm=sm, size_in=si, pack_mm=pm, pack_in=pi, qty=qty,
                n_pack=len(pack_mm), flag=flag)


out = {}
for i, s in enumerate(specs):
    rec = parse(blocks.get(i, ''))
    rec['ok'] = bool(rec['size_mm'] or rec['size_in'])
    rec['no_spec'] = s['same_as_product']
    out[s['slug']] = rec

json.dump(out, open(f"{ROOT}/.workbuddy/tmp/spec_params.json", 'w'), ensure_ascii=False, indent=1)
full = [k for k, v in out.items() if v['size_mm'] and v['pack_mm'] and v['qty']]
print(f"{len(out)} 个型号：三项齐全 {len(full)}；有尺寸 {sum(1 for v in out.values() if v['ok'])}；完全没数据 {sum(1 for v in out.values() if not v['ok'])}")
print("多纸箱（≥2 组包装尺寸）:", sum(1 for v in out.values() if v.get('n_pack', 0) > 1))
print("\n仍缺数据的型号：")
for k, v in out.items():
    if not v['ok']:
        print('  ', k, '| no_spec' if v['no_spec'] else '')
print("\n抽查：")
for k in ('xtb2704a-top-chest', 'mac5602', 'xtb6302', 'xtc3', 'gs2401-wall-cabinet', 'wall-cabinet-1', 'gr21094b01'):
    v = out.get(k, {})
    print(f"  {k:26} {v.get('size_mm','—'):24} {v.get('size_in','—'):22} {v.get('pack_mm','—'):24} {v.get('qty','—')}")
