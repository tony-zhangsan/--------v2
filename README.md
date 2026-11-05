# 新大地五金官网 v2

苏州市新大地五金制品有限公司官网重写版。纯静态多页 HTML，零构建，双语（`/zh/` + `/en/`）。

旧站位于 `../新大地五金网站/`，保留不动，作为内容参考与回滚基线。

---

## 当前进度

| 阶段 | 内容 | 状态 |
|---|---|---|
| 1 | 设计令牌 + 基础样式 + 组件库 | ✅ 完成 |
| 2 | 双语首页（首屏 + 页脚）、根域语言跳转页 | ✅ 完成 |
| 3 | 产品中心（整屏橱窗 + 六张分类卡） | ✅ 完成 |
| 4 | 产品分类页（6 分类 / 111 型号 + 规格弹窗） | ✅ 完成 |
| 5 | 关于我们（深色双屏） | ✅ 完成 |
| 6 | 联系我们（地图 + 联系信息 + 询盘表单） | ✅ 完成 |
| 7 | 404 页、sitemap.xml、robots.txt、JSON-LD | ⬜ 待做 |
| 8 | 上线：nginx 81 端口预览已跑通（`deploy/`） | 🔶 待切正式域名 |

---

## 本地预览

```bash
cd 新大地五金网站-v2
python3 -m http.server 8902
# 打开 http://127.0.0.1:8902/zh/
```

不要直接双击 HTML 打开（`file://` 下语言跳转页会跳错目录）。
桌面另有 `~/Desktop/启动新大地网站.command`，双击起 3212 端口并自动开浏览器。

---

## 目录

```
index.html              根域语言引导页（按浏览器语言跳 zh/en，noindex）
zh/ en/                 双语页面，两套结构完全对应
  index.html            首页（首屏 + 页脚）
  products.html         产品中心（整屏橱窗 + 七张分类卡）
  category.html         产品分类页（?cat=cabinets|carts|combination|benches|stands|grills|others）
  about.html            关于我们（深色双屏：苏州 / 柬埔寨）
  contact.html          联系我们（地图 + 联系信息 + 询盘表单）
assets/css/tokens.css   设计令牌。改配色只改这一个文件
assets/css/base.css     reset、排版基线、布局工具类
assets/css/site.css     公共组件（头部/首屏/卡片/表格/表单/页脚）
assets/css/products.css 产品中心专用，仅 products.html 引用
assets/css/category.css 分类页 + 规格弹窗专用
assets/css/about.css    关于我们专用
assets/js/site.js       移动端菜单、年份、表单校验、头部变色、关于我们切屏、产品中心橱窗
assets/js/category.js   分类页切换与规格弹窗（仅 category.html 引用）
assets/img/hero/        首页首屏背景图 slide-1.jpg（2200×1237，16:9 车间全景）
assets/img/category/    橱窗背景 showcase-bg.jpg、分类主图 hero-<cat>.webp、分类卡图 <cat>.jpg（工具柜主图暂缺）
assets/img/products/    产品图，按分类归档 <cat>/<slug>.webp（900×900 透明底；卡片与弹窗共用）
assets/img/about/       苏州厂区 / 柬埔寨工厂照片 + 中柬国旗 SVG
assets/img/logo/        公司标识、站点图标
assets/img/map/         联系页地图截图
deploy/                 服务器 nginx 配置与一键脚本
PLAN.md                 重写方案与旧站问题诊断
.workbuddy/tmp/         素材生成脚本与中间数据（不进发布包）
.workbuddy/backup/      历史快照与回退说明（不进发布包）
```

**内容全部写在 HTML 里，不用 JS 渲染** —— 这是与旧站最根本的区别，直接影响收录。
JS 只做交互（菜单、切屏、橱窗、弹窗、头部变色），不生成任何正文。

---

## 全站约定（改动前先看）

- **导航固定 4 项**：主页 / 产品中心 / 关于我们 / 联系我们（英文 Home / Products / About Us / Contact Us）。客户已定稿，不要再加第 5 项。
- **语言切换固定顺序「中文 | EN」**，不随当前语言调换；当前项白底高亮。10 个页面的结构、类名、aria 必须一致。
- **当前页导航项 = 变色 + 放大**（`transform: scale(1.1)`，不是 font-size，否则切页会抖），不加背景块。
- **顶部条（电话/邮箱）**：`index` / `products` / `category` 的 HTML 里还有这段，但三页 CSS 都 `display:none`；`about` / `contact` 已整块删除。实际全站都不显示。
- **头部有两种形态**：
  - 深色页（`page-home` / `page-products` / `page-category` / `page-about` / `page-contact`）：透明或深蓝底 + 白色 logo + 白色导航，首页/产品中心/分类页下滑 60px 转实色
  - Logo 全站统一用白色版 `xindadi-logo-white.png`（所有页面头尾都是深蓝底）
- **页头不再放「获取报价」按钮**（about / contact 已删；home / products / category 由 CSS 隐藏），转化入口交给各页自身的 CTA。

---

## 首页（index.html）

结构：**首屏 + 页脚**，中间没有其它区块（客户要求「轮播图以下的东西不要了」，已删数字条/产品系列/制造工艺/关于/新闻/询价条）。

| 部分 | 说明 |
|---|---|
| `.hero-stage` | 首屏容器，高度 `min(100svh, 920px)`，最矮 600px |
| `.hs-bg` | 静态背景图 `assets/img/hero/slide-1.jpg`，`object-fit: cover` |
| `.hero-stage::after` | 两层叠加：① 顶部 150px 渐隐（护导航与 logo）② 径向暗角（中心亮、四周渐深）。**没有整幅压暗**（已按客户要求删除） |
| `.hs-body` | 前景文案：`XINDADI` + 两行副文案 + 一行小字 |
| `.hs-bar` | 右下椭圆描边按钮「联系我们 / Contact Us」→ `contact.html` |

- 轮播已取消（原 6 张自动切换 + 指示点 + 缓推近全部移除），无动效、无 JS 依赖
- 首页顶部条隐藏、头部报价按钮隐藏，转化入口只留首屏椭圆按钮
- ⚠️ **原 `.hs-scrim` 整幅压暗层已删除**（客户 2026-10-27：图片比源图灰太多）。现在只有 `.hero-stage::after` 的顶部渐隐；要恢复整幅压暗，旧样式存在 `.workbuddy/backup/2026-10-27_1642_scrim-removed/`
- `slide-2.jpg ~ slide-6.jpg` 是原轮播备用图，当前无页面引用

---

## 产品中心（products.html）

整屏橱窗 `.pc-hero`：背景图 `assets/img/category/showcase-bg.jpg`，**七张**白框分类卡（`.pc-card`，图在 `assets/img/category/<cat>.jpg`）横排在 `.pc-rail` 上，悬停/聚焦哪张，哪张放大并同步左侧标题与 `Including` 涵盖范围清单。底部 `.pc-track` 滑轨可拖动 / 键盘 ←→。

| 卡片 | 链接 |
|---|---|
| 工具柜 / 工具车 / 组合柜 / 工作台 / 支架 / 烧烤炉 / 其他 | `category.html?cat=` `cabinets` / `carts` / `combination` / `benches` / `stands` / `grills` / `others` |

- 本页顶部条隐藏、头部报价按钮隐藏
- ⚠️ **原 `.pc-scrim` 整幅压暗层已删除**，改为：`.pc-hero::after` 顶部渐隐（护固定头部 + 左上标题/涵盖范围）+ 底部 170px 渐隐（护滑轨与提示）；卡片文字 `.pc-card__label` 自带半透明深色衬底。中间画面保持原图亮度，别再整幅压暗
- 分类口径以客户目录为准（工具柜 / 工具车 / 组合柜 / 工作台 / 支架 / 烧烤炉 / 其他钣金）
- 七张卡图放在 `assets/img/category/<cat>.jpg`，来自客户 `~/Documents/新大地五金/9.新7张图片替换1/1~7.jpg`
  （按 **1 工具柜 / 2 工具车 / 3 组合柜 / 4 工作台 / 5 支架 / 6 烧烤炉 / 7 其他** 对应），
  已按卡面 0.73:1 预先裁成 **512×700**，CSS 里不再做二次裁切（换图记得同比例重裁）
- 七张卡都在首屏，**不要加 `loading="lazy"`**，否则首屏会出现白块
- 改图后记得同步改 `<img src>` 上的 `?v=` 版本号，否则浏览器会用旧图

---

## 产品分类页（category.html）

`?cat=` 决定默认分类，**七个分类共 111 个型号**（数据源：`~/Documents/新大地五金/4.官网产品材料/`，客户 2026-10-27 重发包，以此为准）：

| cat | 中文 | English | 型号数 | 主图 |
|---|---|---|---|---|
| `cabinets` | 工具柜 | Tool Cabinets | 36 | `hero-cabinets.webp` |
| `carts` | 工具车 | Tool Carts | 9 | `hero-carts.webp` |
| `combination` | 组合柜 | Combination Cabinets | 17 | `hero-combination.webp` |
| `benches` | 工作台 | Workbenches | 10 | `hero-benches.webp` |
| `stands` | 支架 | Stands | 15 | `hero-stands.webp` |
| `grills` | 烧烤炉 | Grills | 24 | `hero-grills.webp` |
| `others` | 其他 | Other Sheet Metal Products | 0（素材未到，走空态） | `hero-others.webp` |

**七张分类主图**：客户 2026-10-27 给的 `~/Documents/新大地五金/10.新7张图片替换2(1)/1~7.jpg`，
按 **1 工具柜 / 2 工具车 / 3 组合柜 / 4 工作台 / 5 支架 / 6 烧烤炉 / 7 其他** 对应（与产品目录编号一致）。
原图 2480×850 → `hero-<cat>.webp`（q82，72–178KB）。
⚠️ 这七张**只给分类页横幅用**；产品中心那七张小卡是另一套素材（`9.新7张图片替换1/`），
两套图各自对应客户的两个压缩包，别互相覆盖。
⚠️ **组合柜**是这次新升的一级分类（原来是工具柜的子类）。组合柜的中文标题/广告语客户没给，是按产品形态写的客观描述，**待客户确认**。
⚠️ 除烧烤外，其余分类**没有二级分类**（客户把子类拆成了一级），侧栏只显示「全部产品」一个筛选块。

**结构**

1. `.ct-hero__bgs` 主图区：分类主图 `hero-<cat>.webp` 以 CSS 背景叠放，切分类时淡入；左下大标题 + 广告语 + 型号数
2. `.ct-nav` 左侧目录（sticky）：产品目录 → 7 个一级分类（`.ct-group`）→ 当前分类的二级分类（`.ct-sub`）→ CONTACT US
3. `.ct-panel` 右侧产品区：两行、横向拖动，底部自定义滚动条；卡片带叠层阴影
   - 卡片信息区（客户模板）：橙色 `Mdl.` 小标 + **类型名**（`Tool Chest` / `顶柜`）占一行，型号单独压在**灰条**（`#E8EDF2`）上
   - 没有类型名的型号（如支架）把型号放到标题行、不显示灰条；没有型号的（如 Garage Storage Cabinet 1）标题行放名称
   - 标题过长在窄屏省略号截断，不要换行撑高卡片
   - 筛掉的卡片进隐藏池，**必须留在 DOM 里**，否则二次筛选找不回来
4. `.ct-modal` 规格弹窗：点卡片弹出产品大图 + 三项参数

**图片策略（客户 2026-10-27 明确）**

| 用途 | 用哪张图 |
|---|---|
| 分类页卡片展示图 | `png.png`（透明底抠图） |
| 弹窗里的产品大图 | 同上，**复用同一张**（JS 从 `.ct-card__media img` 取） |
| 提取三项参数 | 同目录另一张（`型号.png` / `参数.png` / `尺寸信息.png`），只做 OCR，**不上站** |

**规格弹窗口径**（客户 2026-10-28 定稿的表格样式：橙色 `Mdl.` 标 + 深蓝/浅蓝双列）

| 行 | 中文 | English | 卡片属性 |
|---|---|---|---|
| 1 | 产品尺寸（宽 × 深 × 高） | Product Dimension (W*D*H) | `data-size-in` / `data-size-mm` |
| 2 | 包装尺寸（宽 × 深 × 高） | Packing Dimension (W*D*H) | `data-pack-in` / `data-pack-mm` |
| 3 | 装箱量 / 40HQ（件） | QTY/40HQ (pcs) | `data-qty` |

- 左格深蓝 `--navy-700` 放**英寸**，右格浅蓝 `#D9E1EC` 放**毫米**；左格右缘用 `clip-path` 做斜切，跟客户参考图一致
- 橙色 `Mdl.` 标签用品牌橙 `--cta`；型号加粗，类型名小字跟在后面
- 缺值时单格显示 `—`，只有装箱量缺值才显示「详见规格图」
- 参数由 `spec_params_v3.json` 提供（110 张规格表 OCR：106 有三项、4 个表本身空白）
- mm 与 inch 自相矛盾的（客户表本身笔误）只保留 mm
- AC41C 的规格表 OCR 断行严重（`686~1092 m / m`），已在 `parse_v3.py` 里用 `OVERRIDE` 写死

**产品卡片的点击 vs 拖动**：位移超过 10px 才算拖动，否则视为点击开弹窗（曾因阈值缺失导致每次点击都被吞掉）。

**生成脚本**：`scan_v3.py`（扫元数据，秒级）→ `render_v3.py --from N --to M`（出图，**必须分批**，
单张约 3.3 秒，111 张会超单条命令时限）→ `ocr_prep_v3.py` + macOS Vision OCR → `parse_v3.py` → `gen_category.py`（出 HTML）。

---

## 关于我们（about.html）

按客户参考稿 `~/Documents/新大地五金/官网材料整合/8.网页布局的流程/3.png` 落地。

| 部分 | 说明 |
|---|---|
| `.page-about` | 深蓝底（`--navy-900`，非纯黑），头部固定在顶部并反色 |
| `.about-slide` | 一屏一 section，`min-height: 100dvh`，`scroll-snap-align: start` |
| `#suzhou` | 第一屏 · 中国苏州：文字左 / 图片右，4 个指标（550800 / 150000 / 2 / 8） |
| `#cambodia` | 第二屏 · 柬埔寨西哈努克：图片左 / 文字右（`.about-slide--flip`），指标 960708 / 215000 / 5 / 15 |
| `.about-figure` | 按效果图拉高：`height:100%` 撑满行高 + `min-height: clamp(420px,66vh,660px)`，图片列最大 500px；圆角 14px + 立体投影（近 6/16、中 20/34、远 44/64 三层 + 冷色光晕 + 1px 亮边），`::before` 为贴地椭圆软影，`::after` 加顶部高光与底部压暗；矮屏 52vh、手机端恢复自适应 |

- 图片旁的文案（导语、公司简介、指标名）统一用无衬线系统字体（`--font-body`），不对齐 mono 字重
- 切换：滚轮一次手势一屏（≤900px 不劫持）、↑↓ / PageUp·PageDown / 空格 / Home·End、右侧圆点、触屏滑动
- `about.html#cambodia` 可直达第二屏
- ≤900px 取消全屏吸附改为单列自然滚动；矮屏（≤800px 高）压缩字号与图片高度
- 图片源：`官网材料整合/网页新布局/网页新布局_05.jpg`（2480px 宽）裁切去黑边，压缩到 760px 宽 q88
- 本页满屏展示，**没有页脚**

---

## 联系我们（contact.html）

深蓝整页（`.page-contact`），头部固定反色，**无顶部条**。

- `.contact-map` 百度地图嵌入 + 「在百度地图中打开」
- `.contact-list` 三项：地址（江苏省苏州市相城区黄埭镇高阳路 99 号，邮编 215143）、联系电话（总机 0512-6548-8105 / 传真 +86-512-6548-4169）、邮箱
- `.contact-form` 询盘表单：只做前端校验，未配置 action 时阻止真实提交并提示（后端接上后填 action 即可）
- ⚠️ 待确认：总机号按参考图取 `0512-6548-8105`，旧站写的是 `6571-7395`，确认后要全站统一

---

## 品牌标识

素材来自 `官网材料整合/5.公司logo材料/`。

| 文件 | 用途 |
|---|---|
| `xindadi-logo-white.png` | **页面实际引用**（全站头尾都是深蓝底） |
| `xindadi-logo-navy.png` | 备用（浅色底） |
| `xindadi-mark-navy/white.png` | 纯 N 图形标记 |
| `favicon-32/192.png`、`apple-touch-icon.png`、`favicon-512.png` | 站点图标（深蓝圆角方块 + 白 N） |

- 中英文站都用中文「新大地」横版标；英文站靠 `alt` 承载英文名
- 引用写法 `<img class="brand__logo" src="...">`，高度由 CSS 控制（头部 36px，页脚 40px，≤640px 时 30/34px），宽度自动
- 换色只重导同名文件，HTML 不用动；**不要用 CSS filter 反相**（半透明边缘会发灰）
- FRONTIER 英文标未上站（站内从未出现该品牌名，避免品牌分裂）

---

## 图片替换规范

产品图位置原本是「蓝图网格 + 标签」的占位块，图到位后按下面替换，不要改布局：

**1. 文件放这里**

```
assets/img/hero/slide-1.jpg        首页首屏背景（2200×1237，16:9；源图 11520×6480 压到 2200 宽 q72，约 420KB）
assets/img/category/hero-<cat>.webp  六分类主图（2480×850）
assets/img/category/<cat>.jpg        白框里的分类卡图（竖版 3:4，208×284）
assets/img/products/<cat>/<slug>.webp 产品图（900×900 透明底）
assets/img/specs/<cat>/<slug>.webp    规格图（弹窗用）
assets/img/about/workshop.jpg      关于我们车间（横图 1600×1200）
```

**2. 改 HTML**

把整块 `.media__label` 换成一行 `<img>`：

```html
<!-- 替换前 -->
<div class="media media--tall">
  <div class="media__label">…占位内容…</div>
</div>

<!-- 替换后 -->
<div class="media media--tall">
  <img class="media__img" src="../assets/img/about/workshop.jpg"
       alt="新大地五金苏州工厂车间" width="1600" height="1200" loading="lazy">
</div>
```

首屏图加 `fetchpriority="high"`，其余图加 `loading="lazy"`。`alt` 必须写实义描述，不要留空。

**3. 图片要求**

- 格式 JPG（照片）或 WebP；单张控制在 300KB 以内
- 长边不超过 2000px
- 产品图统一浅灰白背景，别用纯白（与页面白底会糊成一片）

---

## 素材与数据生成脚本

都在 `.workbuddy/tmp/`，改分类名、广告语、产品命名规则时改脚本重跑，**不要手改 111 张卡片**。

| 脚本 | 作用 |
|---|---|
| `build_assets.py` | 产品图 → `assets/img/products/<cat>/<slug>.webp` |
| `build_specs.py` | 挑出每个型号的规格图 → `assets/img/specs/` |
| `parse_specs.py` | 调 macOS Vision OCR 识别 111 张规格图 → `spec_params.json`（三项参数） |
| `crop_specs.py` | 裁掉规格图底部与弹窗重复的参数文字块 |
| `gen_category.py` | 生成 `category.html`（卡片 + data-size/pack/qty） |

产品数据来自 `官网材料整合/4.官网产品材料/`（111 个型号，每个两张图：透明底产品图 + 规格图），
分类主图来自 `2.内页6张图1/`，广告语来自 `7.文案/`。

---

## 设计约束（改动前必读）

橙色 `#f4731d` 对比度只有 2.87:1，**白底橙字和白字橙底都不过 AA**。所以：

- 橙色只用于：色条、分隔线、图标、大号数字（≥24px 粗体）
- 小字橙色文字用 `--cta-ink`（`#C2560C`）
- 主按钮一律深蓝底白字（11.5:1）

圆角克制在 2–6px（客户明确要求的那几处椭圆按钮除外）；动效只保留 120–280ms 的颜色/位移过渡。
字体纯系统栈，不引 Google Fonts（国内访问 + 服务器部署）。

详见 `assets/css/tokens.css` 顶部注释。

---

## 备份与回退

项目**没有 git**，回退靠 `.workbuddy/backup/` 里的快照，每个目录都有 `说明.md`：

| 目录 | 内容 |
|---|---|
| `2026-10-23_1030_pre-logo-mask/` | 加首屏 logo 蒙版之前的 4 个文件（首页×2 + site.css + site.js） |
| `2026-10-27_1511_veil-version/` | 带 logo 镂空蒙版的版本（已按老板要求回退，留档备用） |

发布包在 `../新大地五金网站-发布包/`（只打 `index.html` + `zh/` + `en/` + `assets/`，排除 `.preview/`、`.workbuddy/`、`PLAN.md`、`README.md`）。

---

## 待办 / 待客户提供

1. **404 页**、`sitemap.xml`、`robots.txt`、JSON-LD
2. **英文规格图**（烧烤 24 款等，客户只给了中文表）
3. **ICP 备案号** —— 目前是 `苏ICP备XXXXXXXX号` 占位
4. **总机号**确认（参考图 6548-8105 vs 旧站 6571-7395）
5. **全站「工作桌 / 工作台」用词统一**：分类页用法是「工作台」，其余页面仍写「工作桌」
6. 询盘表单后端（当前只做前端校验）
7. 正式上线：删 `X-Robots-Tag: noindex`、80 端口 server_name 切到 `www.xindadi.com`、H3C 网关加 `:81` 映射
