# AGENTS.md

> 武汉理工大学 RoboMaster（机甲大师赛）Prime 战队官网 —— Demo 版。
> 本文件为 AI 编码代理（Claude Code / Codex / Cursor 等）与人类开发者的项目说明书。

## 1. 项目概览

- **项目**：WHUT PRIME 战队官网（demo）。首页六个板块：赛事简介 / 战队简介 / 技术组别 / 战队相册 / 商务赞助 / 联系我们（末项在页脚）。顶部主导航为站点级路由：主页 / 战队资讯 / 战队荣誉 / 战队相册(/album) / 技术组别 / 商业合作 + 「加入我们」CTA。
- **后端**：Django 6.1 + django-simpleui（管理后台），SQLite。
- **前端**：Vue 3（Composition API + `<script setup lang="ts">`）+ Vite 7 + GSAP（ScrollTrigger）+ Tailwind v4（**只引 theme/utilities，故意不引 preflight**，见 `src/tailwind.css`；Tailwind 产物都在 `@layer` 里，本站无层样式优先级更高，不会互相顶掉）。
- **Git 仓库**：https://github.com/WHUT-RMers/whut-prime-website（public，默认分支 `main`）。

## 2. 目录结构

```
├── manage.py                # Django 入口
├── requirements.txt         # 后端依赖
├── .gitignore               # 根忽略（.venv / db.sqlite3 / __pycache__ 等）
├── whut_prime/              # Django 项目包
│   ├── settings.py          # SimpleUI、zh-hans、Asia/Shanghai、STATICFILES_DIRS
│   ├── urls.py              # /admin/、/demo/、/  → demo_page
│   └── views.py             # demo_page：渲染 frontend/dist/index.html
├── frontend/                # Vue 前端（Vite）
│   ├── vite.config.ts       # base: '/static/'（关键：与 Django 静态托管对齐）
│   ├── index.html
│   ├── package.json         # scripts: dev / build / preview / typecheck
│   ├── scripts/subset_font.py  # 遗留脚本：Maple Mono NF CN 子集化（现不再使用）
│   └── src/
│       ├── main.ts          # GSAP + ScrollTrigger 注册、挂载
│       ├── style.css        # 设计系统变量、@font-face、主题化滚动条
│       ├── utils/text.ts    # charsHtml() 逐字拆分（GSAP 字符动画）
│       ├── data/hero.ts     # 首屏大图轮播文案 + 图片槽位（slide.image 留空 → 扁平几何占位）
│       ├── composables/useGsapReveal.ts  # 滚动入场通用逻辑
│       ├── assets/fonts/    # woff2：Inter-400/700（latin 子集，中文回退系统字体）
│       └── components/      # 见 §5 组件清单
└── db.sqlite3               # ⚠️ 已 gitignore，不提交
```

## 3. 前后端集成方式（重要）

1. Vite `base: '/static/'`，`npm run build` 产物写入 `frontend/dist/`。
2. Django `STATICFILES_DIRS = [BASE_DIR / 'frontend' / 'dist']`，运行开发服务器时静态资源由 `/static/` 托管。
3. `whut_prime/views.py::demo_page` 直接读取并返回 `frontend/dist/index.html`。
4. **修改前端代码后必须重新 `npm run build`，Django 页面才会生效**（开发迭代用 `npm run dev` 走 Vite HMR，生产/联调走 build + Django）。

## 4. 常用命令（Windows PowerShell）

```powershell
# 后端（项目根目录）
.venv\Scripts\activate                          # 激活虚拟环境
.venv\Scripts\pip install -r requirements.txt   # 装依赖
python manage.py migrate                         # 迁移数据库
python manage.py createsuperuser                 # 创建管理员
python manage.py runserver                       # 启动 http://127.0.0.1:8000/

# 前端（frontend/）
npm install
npm run dev          # Vite HMR 开发服务器（5173 端口）
npm run typecheck    # vue-tsc 类型检查
npm run build        # 产物到 frontend/dist

# 字体：Russo One / Chakra Petch（latin 子集）覆盖西文与数字西文/数字，中文由系统无衬线（PingFang SC /
# HarmonyOS Sans SC / Microsoft YaHei / Noto Sans SC）回退，无需子集化。
# （subset_font.py 为 Maple Mono NF CN 遗留脚本，仅历史参考）
# 字体现状：Russo One（显示/标题）+ Chakra Petch（正文/等宽，400/600/700）自托管 latin 子集，
# 中文回退系统无衬线；位移动效辅助见 src/utils/motion.ts（prefersReducedMotion / countUp）
```

## 5. 前端组件清单（frontend/src/components/）

| 组件 | 职责 |
|---|---|
| `SiteNav.vue` | 固定导航：六大板块路由（主页 / 战队资讯 / 战队荣誉 / 战队相册 / 技术组别 / 商业合作）+ 「加入我们」CTA |
| `HeroSection.vue` | 首屏编排：轮播文案（`data/hero.ts`）+ 右侧 HUD + 底部数据条 + 滚动提示 |
| `HeroCarousel.vue` | **首屏全屏大图轮播引擎**：交叉淡入 + 图片呼吸（scale 1→1.06 正弦往复）、自动轮播（仅标签页隐藏/滚出视口时停，不做悬停暂停）、左右箭头/触摸滑动/方向键、carousel 无障碍语义（刻度指示器已移除，首屏只保留 3 屏）；`slide.image` 留空时渲染扁平几何占位面板 |
| `MarqueeBand.vue` | 兵种关键词无限滚动 |
| `TocNav.vue` | 首页左侧目录：六项锚点（末项 `#contact` 指向全站页脚的联系方式）；滚过首屏才滑入、滚回首屏收回，当前项按视口 45% 线实时判定、滚到页底点亮末项 |
| `EventSection.vue` | 01 赛事简介：要点 + 占位图 |
| `HistorySection.vue` | 02 战队简介：时间线（scrub 生长）+ 荣誉墙 + 计数动画 |
| `GroupsSection.vue` | 03 技术组别：四组 **2×2 卡片栅格**（机械 MEC / 电控 ELC / 视觉算法 ALG / 运营 OPR，⚠️ 硬件组已移除，勿加回），卡片为「占位图 + 组名 + 一句话 + 技术栈 + 招募」，外壳用 `BorderGlow` |
| `BorderGlow.vue` | **边缘发光卡片外壳**（Vue Bits 原版，Tailwind 工具类 + 内联 style）：指针靠近边缘时按方向点亮网格渐变描边与外发光，props 控制灵敏度/发光色/圆角/锥形张角等；当前用于技术组别四张卡 |
| `AlbumSection.vue` | 04 战队相册（首页）：标题区 + 占位相册；与 `views/AlbumView.vue`（/album 页）共用 `AlbumGallery.vue`（6 栅格占位） |
| `CooperateSection.vue` | 05 商务赞助：招商说明 + 赞助层级 + 赞助伙伴 |
| `AppFooter.vue` | 页脚（全站）三列：品牌 + 站点说明 + 版权 ｜ **导航**（竖排六项，与顶部共用 `data/nav.ts`）｜ **联系我们**（车队队长 / 车队经理 / 车队邮箱，单列竖排，锚点 `#contact`） |
| `PlaceholderImage.vue` | **图片占位组件**：写 `<PlaceholderImage label="..." ratio="16/9" />`，素材到位后替换为 `<img>` 即可 |

## 6. 设计系统（frontend/src/style.css）

- **风格**：motion-driven + **扁平化**（flat）：深空蓝黑底（`--bg: #07080d`）× 荧光青绿主强调（`--accent`），`--surface` 实色面板 + 1px 细线边框，几何装饰（点阵/线框方块/描边字），**无重玻璃拟态与辉光**（例外：技术组别四张卡用 `BorderGlow` 的边缘发光，见 §5）。
- **主题**：深色为默认；浅色由 `html[data-theme="light"]` 一键切换（`index.html` 内联防闪烁脚本 + 顶栏开关（SiteNav `.theme-btn`）+ localStorage `whut-prime-theme` 持久化，未手动设置时跟随系统 `prefers-color-scheme`）；所有组件颜色必须走 `:root` 语义 token（`--bg/--surface/--ink/--line/--accent...`），**首屏照片区用 `--hero-*` 亮色 token**（两种主题下都压在照片上，勿换成页面 token）；浅色调色板集中在 style.css 的 `:root[data-theme='light']`。
- **配色**：`--bg: #06070d`、`--accent: #2de2a6`（主强调）、`--accent-2: #4da3ff`（电光蓝）、`--accent-warm: #ffb45e`（暖橙点缀）。
- **字体**：标题/展示用 `Russo One`，正文/等宽用 `Chakra Petch`（均为自托管 latin woff2 子集，@font-face 优先 `local()` 回退打包文件）；中文由系统无衬线（PingFang SC / HarmonyOS Sans SC / Microsoft YaHei / Noto Sans SC）回退。
- **动效曲线**：`--ease-expo: cubic-bezier(0.16,1,0.3,1)`（expo 系），入场 expo.out、退场比入场快；按钮按下 scale(0.96) 回弹微交互。
- **鼠标互动**：`MouseCursor.vue`（自定义光标：点 + 迟滞环，difference 混合）；`composables/useMouseFx.ts` 提供 `data-tilt`（3D 跟手倾斜）/ `data-spot`（光标聚光斑 --mx/--my）/ `data-magnet`（磁吸按钮），仅桌面 fine 指针生效、尊重减弱动态。
- **无障碍**：全局尊重 `prefers-reduced-motion`（CSS 与 JS 双重降级），`:focus-visible` 焦点环、点击元素 cursor:pointer。
- **滚动条**：WebKit + Firefox 主题化（青绿→电光蓝渐变）。

## 7. GSAP 使用规范（motion-driven 要点）

- 路由切换为**方向感知滑动过场**（App.vue）：旧页沿导航方向滑出（0.4s power3.inOut），新页从反侧滑入（0.55s expo.out）；方向由导航顺序数组决定。注意 `:key` 必须挂在 `<component>` 上而非 `<Transition>` 上，否则 leave/enter 钩子不触发。
- 路由已全部**同步加载**（无懒加载），保证切页零空窗。
- 组别板块为 **四组 2×2 卡片栅格**（GroupsSection 已移除旧的 pin + 横向穿行；≥861px 两列、窄屏单列），别再往回加 pin/scrub。
- 跑马灯速率与**滚动速度联动**（MarqueeBand，ScrollTrigger.getVelocity → timeScale）。
- 首屏大图轮播（HeroCarousel）：自动轮播由 GSAP tween 驱动（底部进度条与计时同步，6.5s/屏），图片呼吸为独立 yoyo tween（5s 单程 + 无限 repeat），与逐字入场同屏编排；**首屏铺满全屏，故不做悬停暂停**（否则鼠标一动就停），只在标签页隐藏/滚出视口时 pause·resume；`prefers-reduced-motion` 下不自动播放、不呼吸。

## 8. GSAP 历史规范（承上）

- `gsap.registerPlugin(ScrollTrigger)` 只在 `main.ts` 执行一次。
- 通用滚动入场：组件内 `const root = ref(...)` + `useScrollReveal(root)`，元素加 `data-reveal` 属性；该 composable 基于 `gsap.context` 管理生命周期（卸载自动 revert）。
- 私有动画：组件 `onMounted` 内用 `gsap.context(() => {...}, root)` 包裹，作用域选择器 + 自动清理。
- 逐字动画：`charsHtml()` 生成 `<span class="char">`，配合外层 `overflow:hidden` 行做 yPercent 入场（见 HeroSection）。
- **文案为先、动效为辅**：demo 页面文字精简，动效编排（入场节奏 + 滚动触发 + 微交互），不要散射式动画。

## 9. 开发约定

- 页面文案一律中文，风格精炼、机甲主题（如「以代码铸甲，以热血参战」）。
- 提交信息遵循 Conventional Commits（`feat:` / `fix:` / `docs:` …），推送到 `main`。
- 西文/数字由 Russo One / Chakra Petch latin 子集覆盖、中文回退系统字体，新增字符无需子集化；改动样式后需重新 `npm run build`。改动页面时注意：滚动驱动的强动画若要做，用 `gsap.matchMedia` 绑断点并给移动端简化/降级（组别板块的 pin + 横向穿行已于 2026-09 移除，改为 2×2 栅格，勿加回）。
- 官方静态资源不落库：`frontend/dist/`、`frontend/node_modules/`、`.venv/`、`db.sqlite3` 均忽略。

## 10. 注意事项 / 陷阱

- **管理员密码**：`polarbear / 219200` 仅 6 位，低于 Django 默认 8 位校验；创建时必须程序化绕过（`User.objects.create_superuser` + `set_password`），`createsuperuser` 交互命令会被校验拦下。
- **db.sqlite3 未提交**：clone 后需 `migrate` + 重新创建管理员，才有后台账号。
- `SECRET_KEY` 为 demo 硬编码密钥；`ALLOWED_HOSTS=['*']`、`DEBUG=True` 仅限开发，公开部署前需处理。
- 简历表单在 `/recruit` 页面（首页已无投递板块，入口为顶部「加入我们」和各处 CTA），已接 portal 后端：`api.apply` / 邮箱验证码 / 报名状态查询。
- **后台报名查重**：RecruitmentApplicationAdmin 自带疑似重复比对（列表列 + 编辑页顶部提示条），规则：QQ / 微信 / 手机号 / 邮箱 任一相同，或 姓名+学院+专业班级 三者全同；命中提示「请勿重复提交」。注意 format_html 无参数会抛 TypeError，空结果显示请用 mark_safe。
- **首屏大图素材**：三张实拍横图在 `frontend/public/hero/`（`arena-battle.jpg` 赛场 / `pits-debug.jpg` 调试区 / `team-group.jpg` 全队合影，1620×1080、q82 渐进式 JPEG，各 180–270KB），`data/hero.ts` 用 `image: '/static/hero/xxx.jpg'` 引用，`focus` 控制 `object-position`（移动端竖屏裁切主要靠它）；把 `image` 留空即回退到扁平几何占位面板。
- 组别当前为 4 个（机械/电控/视觉算法/运营），导航、Hero CTA、投递表单、页脚等多处文案需同步，改动时全局搜索确认。
