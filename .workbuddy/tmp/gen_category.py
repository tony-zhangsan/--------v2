# -*- coding: utf-8 -*-
"""生成 zh/category.html 与 en/category.html（静态，正文全在 HTML 里）"""
import json, os, re, html

ROOT = "/Users/zhanghao/WorkBuddy/新大地五金网站-v2"
PRODUCTS = json.load(open(f"{ROOT}/.workbuddy/tmp/products_v3.json"))
PARAMS = json.load(open(f"{ROOT}/.workbuddy/tmp/spec_params_v3.json"))

# 产品图版本号：换图后 +1，强制浏览器重新下载
IMG_VER = 2

CATS = [
 dict(id='cabinets', zh='工具柜', en='Tool Cabinets', nav_zh='工具柜', nav_en='Tool Cabinets',
      ad_zh='坚固金属柜体，用于车库与车间工具收纳。',
      ad_en='Durable metal storage for garage & workshop tools.', subs=[], hero='hero-cabinets'),
 dict(id='carts', zh='工具车', en='Tool Cart', nav_zh='工具车', nav_en='Tool Cart',
      ad_zh='可移动金属推车，方便工具转运。',
      ad_en='Mobile metal trolleys for easy tool transport.', subs=[], hero='hero-carts'),
 dict(id='combination', zh='组合柜', en='Combination Cabinets', nav_zh='组合柜', nav_en='Combination Cabinets',
      ad_zh='模块化柜体，壁柜、底柜与侧柜可自由组合。',
      ad_en='Modular cabinets — wall, base and side units combine freely.', subs=[], hero='hero-combination'),
 dict(id='benches', zh='工作台', en='Workbench', nav_zh='工作台', nav_en='Workbench',
      ad_zh='重载作业台面，满足车间加工使用。',
      ad_en='Heavy-duty work surfaces for workshop operation.', subs=[], hero='hero-benches'),
 dict(id='stands', zh='支架', en='Stand', nav_zh='支架', nav_en='Stand',
      ad_zh='稳固支撑框架，适配锯类及各类设备。',
      ad_en='Sturdy support frames for saws and equipment.', subs=[], hero='hero-stands'),
 dict(id='grills', zh='烧烤炉', en='Grills', nav_zh='烧烤', nav_en='Grills',
      ad_zh='高品质金属烤具，用于户外烹饪。',
      ad_en='Premium metal barbecue units for outdoor cooking.',
      subs=[('griddle','铁板烧','Griddle'), ('gas-grill','气炉','Gas Grill'),
            ('pellet-grill','颗粒炉','Pellet Grill'), ('charcoal-grill','炭炉','Charcoal Grill'),
            ('fire-pit','柴火炉','Fire Pit'), ('tabletop-grill','桌面炉','Tabletop Grill'),
            ('smoker','烟熏炉','Smoker')], hero='hero-grills'),
 dict(id='others', zh='其他', en='Other Sheet Metal Products', nav_zh='其他', nav_en='Others',
      ad_zh='定制钣金加工，满足多样化需求。',
      ad_en='Customized sheet metal fabrication for diverse needs.', subs=[], hero='hero-others'),
]

# 产品类型名：英文规范写法 + 中译（行业通用叫法，未编造参数）
TYPE_EN = {
 'top chest': 'Top Chest', 'middle cabinet': 'Middle Cabinet', 'bottom cabinet': 'Bottom Cabinet',
 'side locker': 'Side Locker', 'wall cabinet': 'Wall Cabinet', 'drawer bottom cabinet': 'Drawer Bottom Cabinet',
 '1-drawer bottom cabinet': '1-Drawer Bottom Cabinet', '2-drawer bottom cabinet': '2-Drawer Bottom Cabinet',
 'garage storage cabinet': 'Garage Storage Cabinet', 'welding cart': 'Welding Cart',
 'wood bracket': 'Wood Bracket', 'with lid': 'With Lid', 'with folding legs': 'With Folding Legs',
 '4-drawer rolling tool cabinet': '4-Drawer Rolling Tool Cabinet',
 'fire pit with blower': 'Fire Pit with Blower', 'fire pit': 'Fire Pit',
}
TYPE_ZH = {
 'top chest': '顶柜', 'middle cabinet': '中柜', 'bottom cabinet': '底柜', 'side locker': '侧柜',
 'wall cabinet': '壁柜', 'drawer bottom cabinet': '抽屉底柜', 'garage storage cabinet': '车库储物柜',
 '1-drawer bottom cabinet': '单抽屉底柜', '2-drawer bottom cabinet': '双抽屉底柜',
 'welding cart': '焊接车', 'wood bracket': '木工支架', 'with lid': '带盖', 'with folding legs': '折叠腿',
 '4-drawer rolling tool cabinet': '四抽工具柜',
 'fire pit with blower': '火盆（带鼓风机）', 'fire pit': '火盆',
}

# 材质 / 板厚 / 结构：目前只有客户 2026-11-05 提供的 OPE704 产品结构表，
# 其余型号没有数据就整块不显示（不套用、不推测）。
MATERIALS = {
 'OPE704': {
   'zh': dict(material='SPCC 冷轧钢板',
              thickness='0.8 mm',
              structure='焊接柜体，双层顶板（顶板 + 衬板）'),
   'en': dict(material='Cold-rolled steel (SPCC)',
              thickness='0.8 mm',
              structure='Welded cabinet frame, double-layer top panel (TOP PANEL + roof liner)'),
 },
}
SUB_ZH = {s[2]: s[1] for c in CATS for s in c['subs']}


def _split_num(n):
    """'Wall Cabinet 2' -> ('wall cabinet', '2')"""
    m = re.match(r'^(.*?)\s*(\d+)$', n)
    if m and m.group(1).strip().lower() in TYPE_EN:
        return m.group(1).strip().lower(), m.group(2)
    return n.strip().lower(), ''


def norm_en_name(n):
    """规范英文写法；认不出的保持原样"""
    if not n:
        return ''
    base, num = _split_num(n)
    if base in TYPE_EN:
        return TYPE_EN[base] + (' ' + num if num else '')
    return n


def zh_name(p):
    n = p['name']
    if not n:
        return SUB_ZH.get(p['sub'], '')
    base, num = _split_num(n)
    if base in TYPE_ZH:
        return TYPE_ZH[base] + (' ' + num if num else '')
    return ''


def en_name(p):
    n = norm_en_name(p['name'])
    if n:
        return n
    return p['sub'] if p['sub'] else ''


def esc(s):
    return html.escape(s, quote=True)

def card_html(p, lang, eager=False):
    code = p['code']
    nm_en = en_name(p)
    nm_zh = zh_name(p)
    # 标题行放产品名（可空），浅灰条固定放型号
    name_txt = nm_zh if lang == 'zh' else nm_en
    title_txt = name_txt          # 没有名称就空着，不拿型号顶上来
    band_txt = code
    # 橙色 Mdl. 标常驻：产品名为空时也保留，只空出右侧名称位置
    mdl_html = '<span class="ct-card__mdl">Mdl.</span>'

    # alt / aria 文案跟页面语言走：中文页只出现中文，英文页只出现英文
    nm_alt = nm_zh if lang == 'zh' else nm_en
    cat_alt = p['cat_zh'] if lang == 'zh' else p['cat_en']
    alt = ' '.join(x for x in [code, nm_alt] if x)
    badge = '<span class="ct-card__new">New</span>' if p['is_new'] else ''
    # 型号灰条始终输出：没有名称时留占位，保证所有卡片高度一致
    band_inner = esc(band_txt) if band_txt else '&#160;'
    band_cls = 'ct-card__code' + ('' if band_txt else ' is-empty')
    band_html = f'\n                <p class="{band_cls}">{band_inner}</p>'
    loading = 'eager' if eager else 'lazy'

    # --- 三项参数（来自客户规格图 OCR，缺失就留空，由前端显示“详见规格图”） ---
    # 弹窗里的产品图直接用卡片这张 png.png，不再单独出规格图
    slug = os.path.splitext(os.path.basename(p['img']))[0]
    pm = PARAMS.get(slug, {})
    attrs = [
        f'data-size-mm="{esc(pm.get("size_mm",""))}"' if pm.get('size_mm') else '',
        f'data-size-in="{esc(pm.get("size_in",""))}"' if pm.get('size_in') else '',
        f'data-pack-mm="{esc(pm.get("pack_mm",""))}"' if pm.get('pack_mm') else '',
        f'data-pack-in="{esc(pm.get("pack_in",""))}"' if pm.get('pack_in') else '',
        f'data-qty="{esc(pm.get("qty",""))}"' if pm.get('qty') else '',
    ]
    # 材质 / 板厚 / 结构（仅 OPE704 有客户 BOM 数据，其余型号不输出这些属性）
    mat = MATERIALS.get(code, {}).get(lang, {}) if code else {}
    if mat:
        attrs += [
            f'data-material="{esc(mat.get("material",""))}"',
            f'data-thickness="{esc(mat.get("thickness",""))}"',
            f'data-structure="{esc(mat.get("structure",""))}"',
        ]
    attrs = ' '.join(a for a in attrs if a)
    label = ('查看 ' + (code or name_txt) + ' 规格｜' if lang == 'zh' else 'View specifications for ') + alt
    return f'''            <article class="ct-card" data-sub="{p['sub_slug']}" data-code="{esc(code)}" data-name="{esc(name_txt)}" {attrs}
                     role="button" tabindex="0" aria-haspopup="dialog" aria-label="{esc(label)}">{badge}
              <div class="ct-card__media">
                <img src="../{p['img']}?v={IMG_VER}" alt="{esc(alt)} — {esc(cat_alt)}" width="258" height="258" loading="{loading}" decoding="async">
              </div>
              <div class="ct-card__body">
                <p class="ct-card__title">{mdl_html}<span class="ct-card__name">{esc(title_txt)}</span></p>{band_html}
              </div>
            </article>'''

def pretty(name):
    """全大写单词转首字母大写（保留已混合大小写的词）"""
    return ' '.join(w.capitalize() if (w.isupper() and len(w) > 1) else w for w in name.split())


# --- 按源目录序号排序 ---
import re as _re
def _ord(p):
    parts = p['src'].split('/')
    folder = parts[-2]
    m = _re.match(r'^(\d+)', folder)
    return (int(m.group(1)) if m else 999)
PRODUCTS.sort(key=_ord)

# --- 预处理产品 ---
for p in PRODUCTS:
    cat = [c for c in CATS if c['id'] == p['cat']][0]
    p['cat_zh'] = cat['zh']
    p['code'] = (p['code'] or '').strip('-').strip()
    p['name'] = pretty((p['name'] or '').strip())
    if not p['code'] and not p['name']:
        p['name'] = p['sub'] or 'New'
    slug = None
    for s in cat['subs']:
        if s[2] == p['sub']:
            slug = s[0]
    p['sub_slug'] = slug or ''

def build(lang):
    L = dict(
      zh=dict(tag='zh-CN', nav=['主页','产品中心','关于我们','联系我们'], cur='产品中心',
              langlabel='中文', other='../en/category.html',
              title='产品分类｜工具柜 · 工具车 · 组合柜 · 工作台 · 支架 · 烧烤炉 — 新大地五金',
              desc='新大地五金产品分类目录：工具柜、工具车、组合柜、工作台、支架、烧烤炉及其他，全部型号与实拍图一览，支持按客户图纸定制。',
              catalog='产品目录', contact='联系我们', allp='全部产品', unit='款产品',
              empty_t='该分类产品资料整理中', empty_p='请直接联系我们获取最新产品目录与报价。',
              empty_btn='联系我们', note='点击左侧目录切换产品分类，产品区可左右拖动浏览。',
              note_cta='需要完整目录或报价？',
              spec_eyebrow='产品规格 · Specification', spec_close='关闭', spec_empty='详见规格图',
              spec_note='参数以规格图为准，如有差异以确认样为准。', spec_cta='索取报价',
              spec_mdl='Mdl.', spec_row_size='产品尺寸（宽 × 深 × 高）',
              spec_row_pack='包装尺寸（宽 × 深 × 高）', spec_row_qty='装箱量 / 40HQ（件）',
              spec_row_mat='材质', spec_row_thick='板厚', spec_row_struct='结构工艺'),
      en=dict(tag='en', nav=['Home','Products','About Us','Contact Us'], cur='Products',
              langlabel='EN', other='../zh/category.html',
              title='Product Categories｜Tool Cabinets, Tool Carts, Combination Cabinets, Workbenches, Stands, Grills — Xindadi Hardware',
              desc='Xindadi Hardware product catalogue: tool cabinets, tool carts, combination cabinets, workbenches, stands, grills and custom sheet metal fabrication. Browse all models with product photos.',
              catalog='Catalog', contact='Contact Us', allp='All Products', unit='products',
              empty_t='Catalogue under preparation', empty_p='Please contact us for the latest product catalogue and quotation.',
              empty_btn='Contact Us', note='Switch categories from the catalogue on the left; drag the product area sideways to browse.',
              note_cta='Need the full catalogue or a quotation?',
              spec_eyebrow='Specification', spec_close='Close', spec_empty='See specification sheet',
              spec_note='Parameters as per the specification sheet above; the confirmed sample prevails.',
              spec_cta='Request a quote',
              spec_mdl='Mdl.', spec_row_size='Product Dimension (W*D*H)',
              spec_row_pack='Packing Dimension (W*D*H)', spec_row_qty='QTY/40HQ (pcs)',
              spec_row_mat='Material', spec_row_thick='Thickness', spec_row_struct='Construction'),
    )[lang]
    langdir = 'zh' if lang == 'zh' else 'en'

    # 导航
    nav_html = '\n'.join(
        f'      <a class="nav__link" href="{"index.html" if i==0 else ("products.html" if i==1 else ("about.html" if i==2 else "contact.html"))}"'
        + (' aria-current="page"' if L['nav'][i] == L['cur'] else '') + f'>{L["nav"][i]}</a>'
        for i in range(4))

    # 侧栏
    groups_html, panels_html = [], []
    for c in CATS:
        items = [p for p in PRODUCTS if p['cat'] == c['id']]
        total = len(items)
        title = c['zh'] if lang == 'zh' else c['en']
        ad = c['ad_zh'] if lang == 'zh' else c['ad_en']
        subs_html = ''
        if c['subs']:
            for slug, szh, sen in c['subs']:
                label = szh if lang == 'zh' else sen
                subs_html += f'\n            <button type="button" class="ct-sub" data-sub="{slug}">{esc(label)}</button>'
            subs_html = f'\n          <div class="ct-subs">{subs_html}\n          </div>'
        elif items:
            subs_html = (f'\n          <div class="ct-subs">'
                         f'\n            <button type="button" class="ct-sub is-active" data-sub="">{esc(L["allp"])}</button>'
                         f'\n          </div>')
        groups_html.append(f'''        <div class="ct-group" data-cat="{c['id']}" data-title="{esc(title)}" data-ad="{esc(ad)}" data-count="{total} {L['unit']}" data-count-label="{L['unit']}">
          <button type="button" class="ct-group__btn">{esc(title)}
            <svg class="ct-chev" viewBox="0 0 12 12" fill="none" aria-hidden="true"><path d="M4 2l4 4-4 4" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/></svg>
          </button>{subs_html}
        </div>''')

        # 产品面板
        if items:
            cards = [card_html(p, lang, eager=(c['id'] == 'cabinets' and i < 6)) for i, p in enumerate(items)]
            cols = []
            for i in range(0, len(cards), 2):
                cols.append('          <div class="ct-col">\n' + '\n'.join(cards[i:i+2]) + '\n          </div>')
            body = ('        <div class="ct-viewport" id="vp-' + c['id'] + '" tabindex="0" aria-label="' + esc(title) + '">\n'
                    '          <div class="ct-track">\n' + '\n'.join(cols) + '\n          </div>\n        </div>\n'
                    '        <div class="ct-scroll" role="scrollbar" tabindex="0" aria-controls="vp-' + c['id'] + '" aria-label="' + esc(title) + '"><div class="ct-scroll__thumb"></div></div>')
        else:
            body = (f'''        <div class="ct-empty">
          <div class="ct-empty__title">{esc(L['empty_t'])}</div>
          <p class="ct-empty__text">{esc(L['empty_p'])}</p>
          <p><a class="btn btn--primary btn--sm" href="contact.html">{esc(L['empty_btn'])}</a></p>
        </div>''')
        active = ' is-active' if c is CATS[0] else ''
        panels_html.append(f'''      <div class="ct-panel{active}" id="cat-{c['id']}" data-cat="{c['id']}">
{body}
      </div>''')

    first = CATS[0]
    first_count = len([p for p in PRODUCTS if p['cat'] == first['id']])
    hero_bgs = '\n'.join(
        (f'      <div class="ct-hero__bg{" is-active" if c is CATS[0] else ""}" data-cat="{c["id"]}" style="background-image:url(\'../assets/img/category/{c["hero"]}.webp?v=3\')"></div>'
         if c.get('hero') else
         f'      <div class="ct-hero__bg ct-hero__bg--empty{" is-active" if c is CATS[0] else ""}" data-cat="{c["id"]}"></div>')
        for c in CATS)

    tpl = f'''<!DOCTYPE html>
<html lang="{L['tag']}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{L['title']}</title>
<meta name="description" content="{L['desc']}">
<link rel="canonical" href="https://www.xindadi.com/{langdir}/category.html">
<link rel="alternate" hreflang="zh-CN" href="https://www.xindadi.com/zh/category.html">
<link rel="alternate" hreflang="en" href="https://www.xindadi.com/en/category.html">
<link rel="alternate" hreflang="x-default" href="https://www.xindadi.com/en/category.html">

<meta property="og:type" content="website">
<meta property="og:site_name" content="{'新大地五金' if lang=='zh' else 'Xindadi Hardware'}">
<meta property="og:title" content="{L['title']}">
<meta property="og:description" content="{L['desc']}">
<meta property="og:url" content="https://www.xindadi.com/{langdir}/category.html">
<meta property="og:locale" content="{'zh_CN' if lang=='zh' else 'en_US'}">
<meta property="og:image" content="https://www.xindadi.com/assets/img/category/hero-cabinets.webp">

{(f'<link rel="preload" as="image" href="../assets/img/category/{CATS[0]["hero"]}.webp?v=3" fetchpriority="high">' if CATS[0].get('hero') else '')}
<link rel="stylesheet" href="../assets/css/tokens.css">
<link rel="stylesheet" href="../assets/css/base.css">
<link rel="stylesheet" href="../assets/css/site.css">
<link rel="stylesheet" href="../assets/css/category.css?v=21">
<link rel="icon" href="../assets/img/logo/favicon-32.png" sizes="32x32" type="image/png">
<link rel="icon" href="../assets/img/logo/favicon-192.png" sizes="192x192" type="image/png">
<link rel="apple-touch-icon" href="../assets/img/logo/apple-touch-icon.png">
</head>
<body class="page-category">

<a class="skip-link" href="#main">{'跳到主要内容' if lang=='zh' else 'Skip to main content'}</a>

<div class="topbar">
  <div class="container topbar__inner">
    <div class="topbar__meta">
      <a href="tel:+8651265717395">+86-512-6571-7395</a>
      <span class="topbar__sep" aria-hidden="true"></span>
      <a href="mailto:info@xindadi.com">info@xindadi.com</a>
    </div>
    <span class="topbar__tag">Est. 1999 · Suzhou, China</span>
  </div>
</div>

<header class="site-header">
  <div class="container site-header__inner">
    <a class="brand" href="index.html">
      <img class="brand__logo" src="../assets/img/logo/xindadi-logo-white.png"
           alt="{'新大地五金 — 工具储物与户外烤炉制造商' if lang=='zh' else 'Xindadi Hardware — Tool storage & outdoor grill manufacturer'}" width="165" height="36">
    </a>

    <nav class="nav" id="site-nav" aria-label="{'主导航' if lang=='zh' else 'Main navigation'}">
{nav_html}
    </nav>

    <div class="header__actions">
      <div class="lang-switch" aria-label="{'语言切换' if lang=='zh' else 'Language'}">
        <a href="../en/category.html" hreflang="en" lang="en"{' aria-current="true"' if lang=='en' else ''}>EN</a>
        <a href="../zh/category.html" hreflang="zh-CN" lang="zh-CN"{' aria-current="true"' if lang=='zh' else ''}>中文</a>
      </div>
      <a class="btn btn--primary btn--sm" href="contact.html">{'获取报价' if lang=='zh' else 'Get a Quote'}</a>
      <button class="nav-toggle" aria-expanded="false" aria-controls="site-nav" aria-label="{'打开菜单' if lang=='zh' else 'Open menu'}">
        <span></span><span></span><span></span>
      </button>
    </div>
  </div>
</header>

<main id="main">

  <!-- ===================== ① 主图（随分类切换） ===================== -->
  <section class="ct-hero" aria-label="{'产品分类主图' if lang=='zh' else 'Category hero'}">
    <div class="ct-hero__bgs">
{hero_bgs}
    </div>
    <div class="ct-hero__scrim"></div>

    <div class="container ct-hero__inner">
      <h1 class="ct-hero__title" data-hero-title>{esc(first['zh'] if lang=='zh' else first['en'])}</h1>
      <p class="ct-hero__ad" data-hero-ad>{esc(first['ad_zh'] if lang=='zh' else first['ad_en'])}</p>
      <p class="ct-hero__count" data-hero-count>{first_count} {L['unit']}</p>
    </div>
  </section>

  <!-- ===================== ② 左侧目录 + ③ 产品列表 ===================== -->
  <section class="ct-main">
    <div class="container ct-layout">

      <aside class="ct-nav" aria-label="{'产品分类目录' if lang=='zh' else 'Product catalogue'}">
        <div class="ct-nav__head">{L['catalog']}</div>
        <div class="ct-nav__list">
{chr(10).join(groups_html)}
        </div>
        <a class="ct-nav__contact" href="contact.html">{L['contact']}</a>
      </aside>

      <div class="ct-stage">
{chr(10).join(panels_html)}

        <div class="ct-note">
          <span>{L['note']}</span>
          <span><a href="contact.html">{L['note_cta']}</a></span>
        </div>
      </div>

    </div>
  </section>

  <!-- ===================== ④ 产品规格弹窗 ===================== -->
  <div class="ct-modal" id="ct-modal" role="dialog" aria-modal="true"
       aria-labelledby="ct-modal-title" aria-hidden="true" data-empty="{L['spec_empty']}">
    <div class="ct-modal__dialog">
      <div class="ct-spec__head">
        <span class="ct-spec__mdl">{L['spec_mdl']}</span>
        <h2 class="ct-spec__code" id="ct-modal-title" data-modal-title></h2>
        <span class="ct-spec__name" data-modal-sub></span>
        <span class="ct-spec__eyebrow">{L['spec_eyebrow']}</span>
        <button type="button" class="ct-modal__close" data-modal-close aria-label="{L['spec_close']}">
          <svg width="13" height="13" viewBox="0 0 14 14" aria-hidden="true"><path d="M2 2l10 10M12 2L2 12" stroke="currentColor" stroke-width="1.7"/></svg>
        </button>
      </div>

      <figure class="ct-modal__figure">
        <img data-modal-img alt="">
      </figure>

      <div class="ct-spec">
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

        <div class="ct-spec__mat" data-mat-block hidden>
          <div class="ct-spec__mat-row">
            <span class="ct-spec__mat-k">{L['spec_row_mat']}</span>
            <span class="ct-spec__mat-v" data-p="material"></span>
          </div>
          <div class="ct-spec__mat-row">
            <span class="ct-spec__mat-k">{L['spec_row_thick']}</span>
            <span class="ct-spec__mat-v" data-p="thickness"></span>
          </div>
          <div class="ct-spec__mat-row">
            <span class="ct-spec__mat-k">{L['spec_row_struct']}</span>
            <span class="ct-spec__mat-v" data-p="structure"></span>
          </div>
        </div>
      </div>

      <div class="ct-modal__foot">
        <span>{L['spec_note']}</span>
        <a href="contact.html">{L['spec_cta']}</a>
      </div>
    </div>
  </div>

</main>

<footer class="site-footer">
  <div class="container">
    <div class="footer-grid">
      <div class="footer-brand">
        <a class="brand" href="index.html">
          <img class="brand__logo brand__logo--footer" src="../assets/img/logo/xindadi-logo-white.png" alt="{'新大地五金' if lang=='zh' else 'Xindadi Hardware'}" width="183" height="40">
        </a>
        <p class="footer-brand__desc">
          {'苏州市新大地五金制品有限公司 — 专业生产工具柜、工具车、工作台及烧烤炉，产品 95% 出口欧美市场。' if lang=='zh' else 'Suzhou Xindadi Hardware Products Co., Ltd. — tool cabinets, tool carts, workbenches and outdoor grills, 95% exported to Europe and North America.'}
        </p>
      </div>

      <div class="footer-col">
        <h4>{'产品中心' if lang=='zh' else 'Products'}</h4>
        <a href="category.html?cat=cabinets">{'工具柜' if lang=='zh' else 'Tool Cabinets'}</a>
        <a href="category.html?cat=carts">{'工具车' if lang=='zh' else 'Tool Cart'}</a>
        <a href="category.html?cat=combination">{'组合柜' if lang=='zh' else 'Combination Cabinets'}</a>
        <a href="category.html?cat=benches">{'工作台' if lang=='zh' else 'Workbench'}</a>
        <a href="category.html?cat=stands">{'支架' if lang=='zh' else 'Stand'}</a>
        <a href="category.html?cat=grills">{'烧烤炉' if lang=='zh' else 'Grills'}</a>
        <a href="category.html?cat=others">{'其他' if lang=='zh' else 'Other Sheet Metal Products'}</a>
      </div>

      <div class="footer-col">
        <h4>{'公司' if lang=='zh' else 'Company'}</h4>
        <a href="about.html">{'关于我们' if lang=='zh' else 'About Us'}</a>
        <a href="contact.html">{'联系我们' if lang=='zh' else 'Contact Us'}</a>
      </div>

      <div class="footer-col">
        <h4>{'联系方式' if lang=='zh' else 'Contact'}</h4>
        <a href="tel:+8651265717395">+86-512-6571-7395</a>
        <a href="mailto:info@xindadi.com">info@xindadi.com</a>
        <a href="contact.html">{'在线询盘' if lang=='zh' else 'Online Inquiry'}</a>
      </div>
    </div>

    <div class="footer-bottom">
      <span>© <span data-year>2026</span> {'苏州市新大地五金制品有限公司 版权所有' if lang=='zh' else 'Suzhou Xindadi Hardware Products Co., Ltd.'}</span>
      <span>{'苏ICP备XXXXXXXX号' if lang=='zh' else 'All rights reserved.'}</span>
    </div>
  </div>
</footer>

<script src="../assets/js/site.js"></script>
<script src="../assets/js/category.js?v=8"></script>
</body>
</html>
'''
    open(f"{ROOT}/{langdir}/category.html", 'w').write(tpl)
    print("written", f"{langdir}/category.html", round(len(tpl.encode())/1024), "KB",
          "卡片数", tpl.count('class="ct-card"'))

build('zh')
build('en')
