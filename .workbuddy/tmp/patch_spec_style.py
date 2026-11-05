# -*- coding: utf-8 -*-
"""把弹窗参数区改成参考图的橙蓝表格风格"""
import re

P = '/Users/zhanghao/WorkBuddy/新大地五金网站-v2/.workbuddy/tmp/gen_category.py'
s = open(P).read()

# ---------- 1) 卡片属性：拆成 mm / in 两个独立字段 ----------
old_attrs = """    def pair(mm, inch):
        if mm and inch:
            return f'{mm}|{inch}'
        return mm or inch or ''
    attrs = [
        f'data-size="{esc(pair(pm.get("size_mm",""), pm.get("size_in","")))}"' if (pm.get('size_mm') or pm.get('size_in')) else '',
        f'data-pack="{esc(pair(pm.get("pack_mm",""), pm.get("pack_in","")))}"' if (pm.get('pack_mm') or pm.get('pack_in')) else '',
        f'data-qty="{esc(pm.get("qty",""))}"' if pm.get('qty') else '',
    ]"""
new_attrs = """    attrs = [
        f'data-size-mm="{esc(pm.get("size_mm",""))}"' if pm.get('size_mm') else '',
        f'data-size-in="{esc(pm.get("size_in",""))}"' if pm.get('size_in') else '',
        f'data-pack-mm="{esc(pm.get("pack_mm",""))}"' if pm.get('pack_mm') else '',
        f'data-pack-in="{esc(pm.get("pack_in",""))}"' if pm.get('pack_in') else '',
        f'data-qty="{esc(pm.get("qty",""))}"' if pm.get('qty') else '',
    ]"""
assert old_attrs in s, 'attrs block not found'
s = s.replace(old_attrs, new_attrs)

# ---------- 2) 语言包：三行标签 ----------
s = s.replace("""              spec_rows=[('产品尺寸（未包装）','size'),('包装尺寸（含外箱）','pack'),('40HQ 装箱量','qty')]),""",
"""              spec_mdl='Mdl.', spec_row_size='产品尺寸（宽 × 深 × 高）',
              spec_row_pack='包装尺寸（宽 × 深 × 高）', spec_row_qty='装箱量 / 40HQ（件）'),""")
s = s.replace("""              spec_rows=[('Product Size (unpacked)','size'),('Packing Size (carton)','pack'),('Loading Qty (40HQ)','qty')]),""",
"""              spec_mdl='Mdl.', spec_row_size='Product Dimension (W*D*H)',
              spec_row_pack='Packing Dimension (W*D*H)', spec_row_qty='QTY/40HQ (pcs)'),""")

# ---------- 3) 弹窗结构 ----------
old_head = """      <div class="ct-modal__head">
        <div>
          <p class="ct-modal__eyebrow">{L['spec_eyebrow']}</p>
          <h2 class="ct-modal__title" id="ct-modal-title" data-modal-title></h2>
          <p class="ct-modal__sub" data-modal-sub></p>
        </div>"""
new_head = """      <div class="ct-spec__head">
        <span class="ct-spec__mdl">{L['spec_mdl']}</span>
        <h2 class="ct-spec__code" id="ct-modal-title" data-modal-title></h2>
        <span class="ct-spec__name" data-modal-sub></span>
        <span class="ct-spec__eyebrow">{L['spec_eyebrow']}</span>"""
assert old_head in s, 'head not found'
s = s.replace(old_head, new_head)

old_params = """      <div class="ct-modal__params">
{chr(10).join(f'''        <div class="ct-param"><span class="ct-param__label">{lb}</span><span class="ct-param__value" data-p="{key}"></span></div>''' for lb, key in L['spec_rows'])}
      </div>"""
new_params = """      <div class="ct-spec">
        <div class="ct-spec__band">{L['spec_row_size']}</div>
        <div class="ct-spec__vals">
          <span class="ct-spec__in" data-p="size-in"></span>
          <span class="ct-spec__mm" data-p="size-mm"></span>
        </div>

        <div class="ct-spec__band">{L['spec_row_pack']}</div>
        <div class="ct-spec__vals">
          <span class="ct-spec__in" data-p="pack-in"></span>
          <span class="ct-spec__mm" data-p="pack-mm"></span>
        </div>

        <div class="ct-spec__qty">
          <span class="ct-spec__qty-label">{L['spec_row_qty']}</span>
          <b class="ct-spec__qty-val" data-p="qty"></b>
        </div>
      </div>"""
assert old_params in s, 'params block not found'
s = s.replace(old_params, new_params)

open(P, 'w').write(s)
print('gen_category.py 已改：橙蓝表格结构')
