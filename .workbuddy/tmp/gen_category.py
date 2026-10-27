# -*- coding: utf-8 -*-
"""生成 zh/category.html 与 en/category.html（静态，正文全在 HTML 里）"""
import json, os, re, html

ROOT = "/Users/zhanghao/WorkBuddy/新大地五金网站-v2"
PRODUCTS = json.load(open(f"{ROOT}/.workbuddy/tmp/products.json"))
SPECS = {r['slug']: r for r in json.load(open(f"{ROOT}/.workbuddy/tmp/specs.json"))}
PARAMS = json.load(open(f"{ROOT}/.workbuddy/tmp/spec_params.json"))
CROPS = {r['slug']: r for r in json.load(open(f"{ROOT}/.workbuddy/tmp/spec_crops.json"))}

CATS = [
 dict(id='cabinets', zh='工具柜', en='Tool Cabinets', nav_zh='工具柜', nav_en='Tool Cabinets',
      ad_zh='坚固金属柜体，用于车库与车间工具收纳。',
      ad_en='Durable metal storage for garage & workshop tools.',
      subs=[('tool-box','工具箱','Tool Box'), ('combination-cabinet','组合柜','Combination Cabinet')]),
 dict(id='carts', zh='工具车', en='Tool Carts', nav_zh='工具车', nav_en='Tool Carts',
      ad_zh='可移动金属推车，方便工具转运。',
      ad_en='Mobile metal trolleys for easy tool transport.',
      subs=[('tool-trolley','工具推车','Tool Trolley'), ('welding-cart','焊接车','Welding Cart'),
            ('push-cart','手推车','Push Cart')]),
 dict(id='stands', zh='支架', en='Stands', nav_zh='支架', nav_en='Stands',
      ad_zh='稳固支撑框架，适配锯类及各类设备。',
      ad_en='Sturdy support frames for saws and equipment.', subs=[]),
 dict(id='benches', zh='工作台', en='Workbenches', nav_zh='工作台', nav_en='Workbenches',
      ad_zh='重载作业台面，满足车间加工使用。',
      ad_en='Heavy-duty work surfaces for workshop operation.', subs=[]),
 dict(id='grills', zh='烧烤炉', en='Grills', nav_zh='烧烤', nav_en='Grills',
      ad_zh='高品质金属烤具，用于户外烹饪。',
      ad_en='Premium metal barbecue units for outdoor cooking.',
      subs=[('griddle','铁板烧','Griddle'), ('gas-grill','气炉','Gas Grill'),
            ('pellet-grill','颗粒炉','Pellet Grill'), ('charcoal-grill','炭炉','Charcoal Grill'),
            ('fire-pit','柴火炉','Fire Pit'), ('tabletop-grill','桌面炉','Tabletop Grill'),
            ('smoker','烟熏炉','Smoker')]),
 dict(id='others', zh='其他钣金制品', en='Other Sheet Metal Products', nav_zh='其他', nav_en='Others',
      ad_zh='定制钣金加工，满足多样化需求。',
      ad_en='Customized sheet metal fabrication for diverse needs.', subs=[]),
]

# 产品类型名：英文规范写法 + 中译（行业通用叫法，未编造参数）
TYPE_EN = {
 'top chest': 'Top Chest', 'middle cabinet': 'Middle Cabinet', 'bottom cabinet': 'Bottom Cabinet',
 'side locker': 'Side Locker', 'wall cabinet': 'Wall Cabinet', 'drawer bottom cabinet': 'Drawer Bottom Cabinet',
 '1-drawer bottom cabinet': '1-Drawer Bottom Cabinet', '2-drawer bottom cabinet': '2-Drawer Bottom Cabinet',
 'garage storage cabinet': 'Garage Storage Cabinet', 'welding cart': 'Welding Cart',
 'wood bracket': 'Wood Bracket', 'with lid': 'With Lid', 'with folding legs': 'With Folding Legs',
}
TYPE_ZH = {
 'top chest': '顶柜', 'middle cabinet': '中柜', 'bottom cabinet': '底柜', 'side locker': '侧柜',
 'wall cabinet': '壁柜', 'drawer bottom cabinet': '抽屉底柜', 'garage storage cabinet': '车库储物柜',
 '1-drawer bottom cabinet': '单抽屉底柜', '2-drawer bottom cabinet': '双抽屉底柜',
 'welding cart': '焊接车', 'wood bracket': '木工支架', 'with lid': '带盖', 'with folding legs': '折叠腿',
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
    if lang == 'zh':
        bold = code or nm_zh or nm_en
        if code:
            sub_line = nm_zh
        else:
            sub_line = nm_en if (nm_en and nm_en != bold) else ''
    else:
        bold = code or nm_en
        sub_line = nm_en if code else ''

    alt = ' '.join(x for x in [code, nm_en] if x)
    badge = '<span class="ct-card__new">New</span>' if p['is_new'] else ''
    name_html = f'<p class="ct-card__name">{esc(sub_line)}</p>' if sub_line else ''
    loading = 'eager' if eager else 'lazy'

    # --- 规格图 + 三项参数（来自客户规格图 OCR，缺失就留空，由前端显示“详见规格图”） ---
    slug = os.path.splitext(os.path.basename(p['img']))[0]
    spec = SPECS.get(slug, {}).get('spec', '')
    pm = PARAMS.get(slug, {})
    def pair(mm, inch):
        if mm and inch:
            return f'{mm}|{inch}'
        return mm or inch or ''
    crop = CROPS.get(slug, {})
    text_only = crop.get('text_only', False)
    attrs = [
        f'data-spec="../{spec}?v=2"' if spec and not text_only else '',
        'data-noimg="1"' if text_only else '',
        f'data-size="{esc(pair(pm.get("size_mm",""), pm.get("size_in","")))}"' if (pm.get('size_mm') or pm.get('size_in')) else '',
        f'data-pack="{esc(pair(pm.get("pack_mm",""), pm.get("pack_in","")))}"' if (pm.get('pack_mm') or pm.get('pack_in')) else '',
        f'data-qty="{esc(pm.get("qty",""))}"' if pm.get('qty') else '',
    ]
    attrs = ' '.join(a for a in attrs if a)
    label = ('查看 ' + (code or bold) + ' 规格｜' if lang == 'zh' else 'View specifications for ') + alt
    return f'''            <article class="ct-card" data-sub="{p['sub_slug']}" data-code="{esc(code)}" data-name="{esc(sub_line or '')}" {attrs}
                     role="button" tabindex="0" aria-haspopup="dialog" aria-label="{esc(label)}">{badge}
              <div class="ct-card__media">
                <img src="../{p['img']}" alt="{esc(alt)} — {esc(p['cat_zh'])}" width="258" height="258" loading="{loading}" decoding="async">
              </div>
              <div class="ct-card__body">
                <h3 class="ct-card__code">{esc(bold)}</h3>
                {name_html}
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
              title='产品分类｜工具柜 · 工具车 · 支架 · 工作台 · 烧烤炉 — 新大地五金',
              desc='新大地五金产品分类目录：工具柜、工具车、支架、工作台、烧烤炉及其他钣金制品，全部型号与实拍图一览，支持按客户图纸定制。',
              catalog='产品目录', contact='联系我们', allp='全部产品', unit='款产品',
              empty_t='该分类产品资料整理中', empty_p='请直接联系我们获取最新产品目录与报价。',
              empty_btn='联系我们', note='点击左侧目录切换产品分类，产品区可左右拖动浏览。',
              note_cta='需要完整目录或报价？',
              spec_eyebrow='产品规格 · Specification', spec_close='关闭', spec_empty='详见规格图',
              spec_note='参数以规格图为准，如有差异以确认样为准。', spec_cta='索取报价',
              spec_rows=[('产品尺寸（未包装）','size'),('包装尺寸（含外箱）','pack'),('40HQ 装箱量','qty')]),
      en=dict(tag='en', nav=['Home','Products','About Us','Contact Us'], cur='Products',
              langlabel='EN', other='../zh/category.html',
              title='Product Categories｜Tool Cabinets, Tool Carts, Stands, Workbenches, Grills — Xindadi Hardware',
              desc='Xindadi Hardware product catalogue: tool cabinets, tool carts, stands, workbenches, grills and custom sheet metal fabrication. Browse all models with product photos.',
              catalog='Catalog', contact='Contact Us', allp='All Products', unit='products',
              empty_t='Catalogue under preparation', empty_p='Please contact us for the latest product catalogue and quotation.',
              empty_btn='Contact Us', note='Switch categories from the catalogue on the left; drag the product area sideways to browse.',
              note_cta='Need the full catalogue or a quotation?',
              spec_eyebrow='Specification', spec_close='Close', spec_empty='See specification sheet',
              spec_note='Parameters as per the specification sheet above; the confirmed sample prevails.',
              spec_cta='Request a quote',
              spec_rows=[('Product Size (unpacked)','size'),('Packing Size (carton)','pack'),('Loading Qty (40HQ)','qty')]),
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
        f'      <div class="ct-hero__bg{" is-active" if c is CATS[0] else ""}" data-cat="{c["id"]}" style="background-image:url(\'../assets/img/category/hero-{c["id"]}.webp\')"></div>'
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

<link rel="preload" as="image" href="../assets/img/category/hero-cabinets.webp" fetchpriority="high">
<link rel="stylesheet" href="../assets/css/tokens.css">
<link rel="stylesheet" href="../assets/css/base.css">
<link rel="stylesheet" href="../assets/css/site.css">
<link rel="stylesheet" href="../assets/css/category.css?v=20261023b">
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
      <div class="ct-modal__head">
        <div>
          <p class="ct-modal__eyebrow">{L['spec_eyebrow']}</p>
          <h2 class="ct-modal__title" id="ct-modal-title" data-modal-title></h2>
          <p class="ct-modal__sub" data-modal-sub></p>
        </div>
        <button type="button" class="ct-modal__close" data-modal-close aria-label="{L['spec_close']}">
          <svg width="13" height="13" viewBox="0 0 14 14" aria-hidden="true"><path d="M2 2l10 10M12 2L2 12" stroke="currentColor" stroke-width="1.7"/></svg>
        </button>
      </div>

      <figure class="ct-modal__figure">
        <img data-modal-img alt="">
      </figure>

      <div class="ct-modal__params">
{chr(10).join(f'''        <div class="ct-param"><span class="ct-param__label">{lb}</span><span class="ct-param__value" data-p="{key}"></span></div>''' for lb, key in L['spec_rows'])}
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
        <a href="category.html?cat=carts">{'工具车' if lang=='zh' else 'Tool Carts'}</a>
        <a href="category.html?cat=stands">{'支架' if lang=='zh' else 'Stands'}</a>
        <a href="category.html?cat=benches">{'工作台' if lang=='zh' else 'Workbenches'}</a>
        <a href="category.html?cat=grills">{'烧烤炉' if lang=='zh' else 'Grills'}</a>
        <a href="category.html?cat=others">{'其他钣金制品' if lang=='zh' else 'Other Sheet Metal Products'}</a>
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
<script src="../assets/js/category.js?v=20261023b"></script>
</body>
</html>
'''
    open(f"{ROOT}/{langdir}/category.html", 'w').write(tpl)
    print("written", f"{langdir}/category.html", round(len(tpl.encode())/1024), "KB",
          "卡片数", tpl.count('class="ct-card"'))

build('zh')
build('en')
