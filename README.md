# 新大地五金官网 v2

苏州新大地五金制品有限公司官网重写版。纯静态多页 HTML，零构建，双语（`/zh/` + `/en/`）。

旧站位于 `../新大地五金网站/`，保留不动，作为内容参考与回滚基线。

---

## 当前进度

| 阶段 | 内容 | 状态 |
|---|---|---|
| 1 | 设计令牌 + 基础样式 + 组件库 | ✅ 完成 |
| 1 | 中文首页、英文首页、根域语言跳转页 | ✅ 完成 |
| 2 | 产品中心（整屏分类橱窗 + 六个分类区块） | ✅ 完成 |
| 2 | 产品分类页（左目录 + 右产品列表，111 个型号实拍） | ✅ 完成 |
| 2 | 6 个 SKU 详情页（静态化） | ⬜ 待做，等产品图与规格 |
| 3 | 关于我们（双屏）/ 联系我们 / 404 | 🟡 关于我们 + 联系我们已完成，404 待做 |
| 4 | sitemap.xml、robots.txt、JSON-LD、hreflang 全量校验 | ⬜ 待做 |
| 5 | nginx 配置 + 上线检查 | ⬜ 待做 |

---

## 本地预览

```bash
cd 新大地五金网站-v2
python3 -m http.server 8902
# 打开 http://127.0.0.1:8902/zh/
```

不要直接双击 HTML 打开（`file://` 下相对路径正常，但语言跳转页会跳错目录）。

---

## 目录

```
assets/css/tokens.css   设计令牌。改配色只改这一个文件
assets/css/base.css     reset、排版基线、布局工具类
assets/css/site.css     页面组件（头部/首屏/卡片/表格/表单/页脚）
assets/css/about.css    关于我们双屏（仅 about.html 引用）
assets/css/products.css 产品中心橱窗 + 分类区块（仅 products.html 引用）
assets/css/category.css 产品分类页（仅 category.html 引用）
assets/js/category.js   分类切换、二级筛选、横向滚动条、头部变色；不生成正文
assets/img/products/    111 个型号的产品图（按分类分目录，webp 900×900）
assets/js/site.js       移动端菜单、年份、表单校验、头部变色、关于我们切屏、产品中心橱窗；不生成任何正文
assets/img/hero/        首页首屏背景图 slide-1.jpg（2400×822），slide-2~6 为原轮播备用图
assets/img/category/    六大分类背景图（1920×658，源图 2480×850）
assets/img/about/       苏州厂区 / 柬埔寨工厂航拍 / 中柬国旗 SVG
assets/img/logo/        公司标识、站点图标、首屏蒙版 frontier-mask.png（见下节）
zh/ en/                 双语页面，两套结构完全对应
PLAN.md                 重写方案与旧站问题诊断
```

## 产品中心（products.html）

参考稿：`~/Documents/新大地五金/官网材料整合/8.网页布局的流程/4.png`。
分类名称与卡片图来源：`~/Documents/新大地五金/官网材料整合/2.内页6张图1/`（六个子目录，一目录一分类）。
背景图：`~/Documents/新大地五金/官网材料整合/1.6张图/封面1.jpg`（固定一张，不随分类切换）。

**页面结构：只有一屏，往下没有内容**

`.pc-hero` 整屏橱窗（`min(100svh, 920px)`）→ 页脚。

- `.pc-bg-img` **单张固定背景**（`assets/img/category/showcase-bg.jpg`，源 封面1.jpg，2400×822 / 190KB），
  带 18s 极缓推近。⚠️ 客户明确取消「背景随分类切换」，不要再做成多层淡入
- `.pc-scrim` 三段压暗（顶部压头部 / 左侧压文字 / 底部压卡片）。这张底图上沿偏亮，顶部的渐变是必须的
- `.pc-body` 左侧大标题 + `Including` / 涵盖范围清单
- `.pc-rail` 分类卡横向滑动，默认高亮第一张；悬停/聚焦哪张，哪张放大（背景不动）
  - 卡片从容器左边界起排（与标题、涵盖范围同一竖线），右侧越过容器边界伸到屏幕外，第六张露一线提示可滑
  - 卡片 208×284，高亮时 256×348；轨道 16px 间距。改尺寸要同时改 1024 断点与矮屏断点，否则会跟标题撞上
  - 超宽屏（约 1920+）六个一屏放得下时，滑动条自动隐藏（`.pc-track-wrap.is-idle`），别留死控件
- `.pc-track` 底部滑动条，可拖动、可点击，键盘 ←/→ 也能推

⚠️ 老板明确要求：**这一页只做分类入口，往下不要再加任何东西**（产品卡、分类区块、CTA 条都砍掉了，
产品列表在 `category.html` 里）。`.pc-series` / `.pc-anchor` 那套样式也已一并删除，别再加回来。

**分类与链接**

| 序号 | `?cat=` | 中文 | English | 系列 | 背景图 |
|---|---|---|---|---|---|
| 01 | `cabinets` | 工具柜 | Tool Cabinets | TC | `cabinets.jpg` |
| 02 | `carts` | 工具车 | Tool Carts | MT | `carts.jpg` |
| 03 | `stands` | 支架 | Stands | TR | `stands.jpg` |
| 04 | `benches` | 工作台 | Workbenches | WB | `benches.jpg` |
| 05 | `grills` | 烧烤炉 | Grills | GG | `grills.jpg` |
| 06 | `others` | 其他钣金制品 | Other Sheet Metal Products | WC | `others.jpg` |

分类名以客户文案 `~/Documents/新大地五金/官网材料整合/7.文案/大标题和文案.png` 为准：
工具柜 / 工具车 / 支架 / 工作台 / 烧烤炉 / 其他钣金制品。卡片、全站页脚、各页 title 与 description 都已按这套名字统一，
改名前先跟老板确认（旧站叫 工具箱柜 / 工作桌 / 文件柜 / 工具支架 / 户外烤炉，别混用）。

六张卡片与全站页脚（index / contact / products / category）的分类链接统一指向 `category.html?cat=<上面的值>`。
⚠️ 不要再写回 `products.html#cabinets` 这类锚点——本页已无对应区块，点了不会动。

**分类卡片图**
卡片直接用 `assets/img/category/<id>.jpg` 这六张（与分类页横幅同一套素材，1920×658），不再有占位块。
原图是 2.92:1 横幅、卡面是 0.73:1 竖版，靠 `object-position` 逐个定裁切点（写死在 `products.css` 里）：

| 分类 | object-position |
|---|---|
| cabinets | 63% 50% |
| carts | 48% 50% |
| stands / benches / grills | 50% 50% |
| others | 34% 55% |

换图后若主体被裁掉，改这几行百分比即可。

**顶部导航**
本页头部为固定透明覆盖式（`body.page-products`），下滑 60px 转深蓝实色。
当前栏目**只用橙色区分，不加下划线**（`.page-products .nav__link[aria-current="page"]::after { display: none }`），
这是客户在参考稿上明确要求的，别改回下划线。

---

## 产品分类页（category.html）

参考稿：`~/Documents/新大地五金/官网材料整合/8.网页布局的流程/6.png`、`7.png`、`12.png`、`13.png`。
主图标题与广告语：`~/Documents/新大地五金/官网材料整合/7.文案/大标题和文案.png`（客户定稿，逐条照抄，勿改写）。

| # | 分类 id | 标题（zh / en） | 广告语（zh / en） |
|---|---|---|---|
| 1 | `cabinets` | 工具柜 / TOOL CABINETS | 坚固金属柜体，用于车库与车间工具收纳。/ DURABLE METAL STORAGE FOR GARAGE & WORKSHOP TOOLS. |
| 2 | `carts` | 工具车 / TOOL CARTS | 可移动金属推车，方便工具转运。/ MOBILE METAL TROLLEYS FOR EASY TOOL TRANSPORT. |
| 3 | `stands` | 支架 / STANDS | 稳固支撑框架，适配锯类及各类设备。/ STURDY SUPPORT FRAMES FOR SAWS AND EQUIPMENT. |
| 4 | `benches` | **工作台** / WORKBENCHES | 重载作业台面，满足车间加工使用。/ HEAVY-DUTY WORK SURFACES FOR WORKSHOP OPERATION. |
| 5 | `grills` | 烧烤炉 / GRILLS | 高品质金属烤具，用于户外烹饪。/ PREMIUM METAL BARBECUE UNITS FOR OUTDOOR COOKING. |
| 6 | `others` | 其他钣金制品 / OTHER SHEET METAL PRODUCTS | 定制钣金加工，满足多样化需求。/ CUSTOMIZED SHEET METAL FABRICATION FOR DIVERSE NEEDS. |

⚠️ 英文标题在 HTML 里存首字母大写，靠 `.ct-hero__title { text-transform: uppercase }` 显示全大写。
⚠️ 分类 4 客户文案写「工作台」，站内其它页面（index / about / contact / products）目前仍写「工作桌」，
待老板确认后统一。
素材来源：
- 主图（每个分类一张，随分类切换）：`3.内页6张图2/`，输出为 `assets/img/category/hero-<cat>.webp`（2480×850）
- 产品图与型号：`4.官网产品材料/`，输出为 `assets/img/products/<cat>/<slug>.webp`（900×900 透明底，单张约 45KB）

**页面结构**

1. `.ct-hero` 主图区：6 张分类图叠放，切换分类时淡入；左侧标题 + 该分类广告语（文案取自 `7.文案/`）
2. `.ct-nav` 左侧目录（sticky）：CATALOG 标题 → 6 个一级分类 → 当前分类的二级分类 → CONTACT US
   - 点一级分类：换主图 / 标题 / 广告语 + 换产品面板
   - 点二级分类：筛选产品（再点一次取消），按钮加深
   - 目录过长时只有列表内部滚动，CONTACT US 钉在底部
3. `.ct-panel` 右侧产品区：两行、横向拖动，底部自定义滚动条；卡片带叠层阴影
4. `.ct-modal` 产品规格弹窗：点卡片打开 → 客户原版规格图 + 三项参数
   - 分栏由 `.ct-col` 两两成组（对应参考稿「一行三个、两行」的读法）
   - 筛掉的卡片进 `.ct-pool` 隐藏池，**必须留在 DOM 里**，否则二次筛选找不回来

**数据来源与规范**

| 项 | 说明 |
|---|---|
| 分类 | 工具柜 31 / 工具车 31 / 支架 15 / 工作桌 10 / 烧烤炉 24 / 其他钣金制品 0（素材未到，走空态） |
| 排序 | 按源目录序号（`1.` `2.` … `14.`），不是字典序 |
| 卡片标题 | 型号加粗 + 类型名（顶柜/中柜/底柜/侧柜/壁柜/抽屉底柜…）；无型号的新品用类型名，右上角打 NEW |
| 图片挑选 | 优先 `png.png`（透明抠图）；没有则取最大的透明大图；只剩规格图时按固定比例裁出产品照片区 |
| 卡片正面 | 只显示型号 + 类型名，不显示尺寸（卡片太窄，且尺寸在弹窗里有完整版） |

⚠️ 分类里「工作桌 / 工作台」的写法见上方说明，客户文案用「工作台」。

## 规格弹窗（.ct-modal）

点产品卡 → 弹窗显示该型号的**第二张图（客户原版规格图）** + 下面三项参数。

**三项参数的口径与文案**（老板确认）

| # | 中文 | English | 对应规格图字段 |
|---|---|---|---|
| 1 | 产品尺寸（未包装） | Product Size (unpacked) | `总的来说` / `Overall` / `产品尺寸` |
| 2 | 包装尺寸（含外箱） | Packing Size (carton) | `套餐` / `Package` / `包装尺寸` |
| 3 | 40HQ 装箱量 | Loading Qty (40HQ) | `数量` / `Qty` / `集装箱的数量` |

> 客户原图里的 `总的来说` / `套餐` 是机器翻译（Overall / Package），站上已换成上面这套说法。

**图片已裁掉参数文字块**
规格图底部原本印着 `总的来说 / 套餐 / 数量`，和弹窗下方的三项参数重复。
`crop_specs.py` 用 OCR 的文字坐标找到参数块起始行，把整块裁掉，只保留「型号标题 + 产品照片」，
再裁四周白边、2 倍放大存 webp（共 2.3MB）。
- 裁了 100 张；1 张（`garage-storage-cabinet-3`）没有独立规格图，保持原样
- 10 张是**纯文字规格表**（`尺寸信息.png` / `参数.png`，如新品 Wall Cabinet、烟熏炉），本身没有产品照，
  这类卡片不打 `data-spec`，弹窗直接不显示图片区，避免又出现一块重复文字

**数据怎么来的（不是手写，也不是编的）**
1. `build_specs.py` 为每个型号挑出规格图 → `assets/img/specs/<cat>/<slug>.webp`（2 倍放大，单张约 30KB）
2. `parse_specs.py` 调 macOS Vision OCR（`~/.workbuddy/skills/macos-screenshot-ocr`）识别 111 张图，
   按标签分段取三个值 → `.workbuddy/tmp/spec_params.json`
3. `gen_category.py` 把参数写进卡片的 `data-size` / `data-pack` / `data-qty`，弹窗只做显隐赋值

**已知缺口（如实呈现，前端显示「详见规格图」）**

| 情况 | 数量 | 型号 |
|---|---|---|
| 规格表本身就没填数值 | 2 | `GARAGE STORAGE CABINET 2`（Overall/Package/Qty 全空）、`GARAGE STORAGE CABINET 3`（无独立规格图） |
| 该型号无规格图（只有一张产品图） | 1 | 工具车「新品」 |
| 有尺寸但无装箱量 | 28→32 张缺 qty | 主要是烧烤类与部分新品表 |
| 只有英寸没有 mm | 5 | 新品 Wall Cabinet 1/2、Drawer Bottom Cabinet 1/2、Side Locker |

⚠️ 客户原表里有 6 张的 mm 与 inch 互相矛盾（例：`723×390×540mm` 写成 `28.5×15.4×12.3 in`），
这类只保留 mm、丢掉英寸值，避免把笔误发到站上。

⚠️ **英文站目前仍显示中文规格图**（烧烤类 24 款、支架/工作桌部分型号，客户只给了中文表）。
需要客户补英文规格图；拿到后覆盖 `assets/img/specs/` 同名文件即可，HTML 不用改。

---


**生成脚本**：`.workbuddy/tmp/build_assets.py`（产品图）→ `build_specs.py`（规格图）→ `parse_specs.py`（OCR 取参数）→ `gen_category.py`（出 HTML）。
改了分类名、广告语、产品命名规则，改脚本重跑，不要手改 111 张卡片。

**入口**：`products.html` 的六张分类卡已指向 `category.html?cat=xxx`；页脚分类链接同样。

---


## 品牌标识

原稿：`~/Documents/新大地五金/官网材料整合/5.公司logo材料/新大地-大logo.png`（956×192，白色透明底）。
原稿图形紧贴画布边缘，已四周补 6% 透明留白后按宽 640 导出。

| 文件 | 用途 |
|---|---|
| `xindadi-logo-white.png` | **页面实际引用**。全站头部（首页透明/实色、关于、联系页均为深蓝底）与页脚统一用它 |
| `xindadi-logo-navy.png` | 备用浅底场景（白底 header、邮件签名、浅色物料） |
| `xindadi-mark-navy/white.png` | 只取椭圆 N 图形，正方形，用于头像、水印、深色底小标识 |
| `favicon-32/192.png`、`apple-touch-icon.png`、`favicon-512.png` | 站点图标：深蓝圆角方块 + 白色 N |

- 页面里统一写作 `<img class="brand__logo" src="...">`，高度由 CSS 控制（36px，页脚 40px，≤640px 时 30/34px），宽度自动
- 换色只需重导同名文件，HTML 不用动
- 若以后出现白底头部，把该处的 `src` 换成 `xindadi-logo-navy.png` 即可，不要用 CSS filter 反相（半透明边缘会发灰）

**内容全部写在 HTML 里，不用 JS 渲染** —— 这是与旧站最根本的区别，直接影响收录。
目前首页首屏也没有任何 JS 依赖（轮播已取消），禁用 JS 时整页照常显示。

---

## 首页首屏（静态背景）

结构：

| 部分 | 说明 |
|---|---|
| `.hero-stage` | 首屏容器，高度 `min(100svh, 920px)`，最矮 600px |
| `.hs-bg` | 静态背景图，`object-fit: cover`，固定使用 `assets/img/hero/slide-1.jpg`（封面 1） |
| `.hs-scrim` | 压暗层，左侧重、底部渐变，保证任何底图上的白字都清晰 |
| `.hs-body` | 前景文案：`XINDADI` + 两行副文案 + 一行小字 |
| `.hs-bar` | 右下椭圆描边按钮「联系我们 / Contact Us」→ `contact.html` |

- **轮播已取消**（原 6 张自动切换 + 左下指示点 + 缓推近全部移除），只留封面 1 一张静态底图，无动效
- 首页头部悬浮在首屏上（`.page-home`），下滑超过 60px 转为实色深蓝；
  首页顶部条（电话/邮箱）隐藏、头部「获取报价」按钮隐藏，转化入口只留首屏那个椭圆按钮
- 其他页面不受影响，仍是白底 sticky 头部 + 顶部条

**首页只有首屏 + 页脚**
老板要求「轮播图以下的东西不要了」，已删掉数字条 / 六大系列 / 制造工艺 / 关于 / 新闻 / 询价条六个区块，
`<main>` 里只剩首屏那一个 section，后面直接接页脚。
`site.css` 里 `.stat-strip` `.series-grid` `.process` `.split` `.news-grid` `.cta-band` 等样式**没删**，
留给产品中心 / 关于我们等页面复用，别当死代码清掉。

**换图**：替换 `assets/img/hero/slide-1.jpg`（同名覆盖即可，无需改代码）。
`slide-2.jpg ~ slide-6.jpg` 是原轮播的备用图，目前没有任何页面引用。

### 首屏 logo 镂空蒙版（`.hero-veil`）

按老板要求加在最上层：整屏纯黑，只有 logo 笔画处镂空，透过笔画看得到底图。
参考稿 `8.网页布局的流程/2.png`。

| 项 | 值 |
|---|---|
| 蒙版图 | `assets/img/logo/frontier-mask.png`（由 `5.公司logo材料/logo-黑色.png` 裁到笔画边界、缩到 1400×318 导出，约 47KB） |
| 合成方式 | 两层 mask + `mask-composite: exclude`：第 1 层整块不透明，第 2 层是 logo 的 alpha，相减＝除笔画外全黑 |
| 落定尺寸 | `--veil-hole: 48%`（占视口宽），≤900px 时 62% |
| 落定位置 | `--veil-y: 25%`（锚点在视口高度 25% 处，实测 logo 中心约在 30% 高度，即「顶部与居中的中间」） |
| 动画 | `veil-shrink` 1600ms + 150ms 延迟，`cubic-bezier(.22,1,.36,1)`；镂空宽度 340% → 48%，由大到小落定 |
| 层级 | veil `z-index:4`，压在 `.hs-body` 之上；`.hs-bar` 提到 `z-index:5`，**椭圆按钮始终露在蒙版之上可点** |
| 无障碍 | `aria-hidden="true"` + `pointer-events:none`；`prefers-reduced-motion` 时不播动画直接落定 |

⚠️ 这层是**常驻**的：动画结束后不会消失，首屏的 `XINDADI` 文案与底图都被盖住（只剩 logo 笔画里透出的画面）。
若改成「开场动画、播完淡出」，给 `.hero-veil` 追加一段 `animation: veil-shrink 1600ms ... , veil-out 600ms 2s forwards` 即可。

⚠️ 换 logo：把新 logo 的黑色稿裁到笔画边界、清成「透明底 + 纯黑笔画」，覆盖 `frontier-mask.png` 同名文件，CSS 不用动。

---

## 关于我们（深色双屏）

按客户参考稿 `~/Documents/新大地五金/官网材料整合/8.网页布局的流程/3.png` 落地。

| 部分 | 说明 |
|---|---|
| `.page-about` | 深蓝底（`--navy-900`，非纯黑），头部固定在顶部并反色 |
| `.about-slide` | 一屏一 section，`min-height: 100dvh`，`scroll-snap-align: start` |
| `#suzhou` | 第一屏 · 中国苏州：文字左 / 图片右，4 个指标（550800 / 150000 / 2 / 8） |
| `#cambodia` | 第二屏 · 柬埔寨西哈努克：图片左 / 文字右（`.about-slide--flip`），指标 960708 / 215000 / 5 / 15 |
| `.about-figure` | 圆角 14px + 立体投影（近 6/16、中 20/34、远 44/64 三层 + 冷色光晕 + 1px 亮边），`::before` 为贴地椭圆软影，`::after` 加顶部高光与底部压暗；高度 `clamp(280px, 52vh, 480px)` |

- 切换：滚轮一次手势一屏（≤900px 不劫持）、↑↓ / PageUp·PageDown / 空格 / Home·End、右侧圆点、触屏滑动
- `about.html#cambodia` 可直达第二屏
- ≤900px 取消全屏吸附改为单列自然滚动；矮屏（≤800px 高）压缩字号与图片高度
- 图片源：`官网材料整合/网页新布局/网页新布局_05.jpg`（2480px 宽）裁切去黑边，压缩到 760px 宽 q88
（第一张写 `src` 并带 `is-active`，其余写 `data-src` 懒加载）；指示点由 JS 按张数自动生成。

---

## 图片替换规范

页面里所有产品图位置目前是「蓝图网格 + 标签」的占位块。图到位后按下面替换，不要改布局：

**1. 文件放这里**

```
assets/img/hero/slide-1.jpg                首页首屏静态背景（横图 2400×822，宽幅 2.92:1）
assets/img/about/workshop.jpg               关于我们车间（横图 1600×1200）
assets/img/products/tc2d-1.jpg              产品主图（方图 1200×1200）
assets/img/products/tc2d-2.jpg              产品副图
```

首屏背景图已经到位（源图 2480×850 压到 2400×822 / 质量 75，约 330KB）。
其余产品图命名统一 `{sku 小写}-{序号}.jpg`，SKU 见 `PLAN.md` 第四节。

**2. 改 HTML**

把整块 `.media__label` 换成一行 `<img>`：

```html
<!-- 替换前 -->
<div class="media media--tall">
  <div class="media__label">…占位内容…</div>
</div>

<!-- 替换后 -->
<div class="media media--tall">
  <img class="media__img" src="../assets/img/hero/factory.jpg"
       alt="新大地五金苏州工厂全景" width="1200" height="1500"
       fetchpriority="high">
</div>
```

首屏图加 `fetchpriority="high"`，其余图加 `loading="lazy"`。`alt` 必须写实义描述，不要留空。

**3. 图片要求**

- 格式 JPG（照片）或 WebP；单张控制在 300KB 以内
- 长边不超过 2000px
- 产品图统一浅灰白背景，别用纯白（与页面白底会糊成一片）

---

## 设计约束（改动前必读）

橙色 `#f4731d` 对比度只有 2.87:1，**白底橙字和白字橙底都不过 AA**。所以：

- 橙色只用于：色条、分隔线、图标、大号数字（≥24px 粗体）
- 小字橙色文字用 `--cta-ink`（`#C2560C`）
- 主按钮一律深蓝底白字（11.5:1）

详见 `assets/css/tokens.css` 顶部注释。

---

## 待客户提供

1. **产品实拍图**（最重要，没有图视觉做不"像工厂"）
2. **Logo 源文件** AI/SVG —— 目前是字母 X 的占位方块
3. **ICP 备案号** —— 目前是 `苏ICP备XXXXXXXX号` 占位
4. 是否需要英文版公司简介的精修（现译文沿自旧站）
