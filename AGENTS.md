# AGENTS.md

> 武汉理工大学 RoboMaster（机甲大师赛）Prime 战队官网 —— Demo 版。
> 本文件为 AI 编码代理（Claude Code / Codex / Cursor 等）与人类开发者的项目说明书。

## 1. 项目概览

- **项目**：WHUT PRIME 战队官网（demo），六大板块：赛事介绍 / 战队资讯 / 历史与荣誉 / 组别介绍（技术栈）/ 简历投递 / 商业合作。
- **后端**：Django 6.1 + django-simpleui（管理后台），SQLite。
- **前端**：Vue 3（Composition API + `<script setup lang="ts">`）+ Vite 7 + GSAP（ScrollTrigger）。
- **Git 仓库**：https://github.com/niconieryr/whut-prime-website（public，默认分支 `main`）。

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
| `SiteNav.vue` | 固定导航：六大板块锚点 + 加入战队 CTA |
| `HeroSection.vue` | 首屏：字符级 GSAP 入场、环境光斑漂浮、战队数据 |
| `MarqueeBand.vue` | 兵种关键词无限滚动 |
| `EventSection.vue` | 01 赛事介绍：要点 + 占位图 |
| `NewsSection.vue` | 02 战队资讯：新闻卡片（日期/分类/占位图） |
| `HistorySection.vue` | 03 历史与荣誉：时间线（scrub 生长）+ 荣誉墙 + 计数动画 |
| `GroupsSection.vue` | 04 组别介绍：机械 MEC / 电控 ELC / 算法 ALG / 运营 OPR（⚠️ 硬件组已移除，勿加回） |
| `RecruitSection.vue` | 05 简历投递：表单（demo 仅前端提示，未接后端） |
| `CooperateSection.vue` | 06 商业合作：合作方向 + 合作邮箱 |
| `AppFooter.vue` | 页脚、站点声明 |
| `PlaceholderImage.vue` | **图片占位组件**：写 `<PlaceholderImage label="..." ratio="16/9" />`，素材到位后替换为 `<img>` 即可 |

## 6. 设计系统（frontend/src/style.css）

- **风格**：motion-driven + **扁平化**（flat）：深空蓝黑底（`--bg: #07080d`）× 荧光青绿主强调（`--accent`），`--surface` 实色面板 + 1px 细线边框，几何装饰（点阵/线框方块/描边字），**无重玻璃拟态与辉光**。
- **配色**：`--bg: #06070d`、`--accent: #2de2a6`（主强调）、`--accent-2: #4da3ff`（电光蓝）、`--accent-warm: #ffb45e`（暖橙点缀）。
- **字体**：标题/展示用 `Russo One`，正文/等宽用 `Chakra Petch`（均为自托管 latin woff2 子集，@font-face 优先 `local()` 回退打包文件）；中文由系统无衬线（PingFang SC / HarmonyOS Sans SC / Microsoft YaHei / Noto Sans SC）回退。
- **动效曲线**：`--ease-expo: cubic-bezier(0.16,1,0.3,1)`（expo 系），入场 expo.out、退场比入场快；按钮按下 scale(0.96) 回弹微交互。
- **鼠标互动**：`MouseCursor.vue`（自定义光标：点 + 迟滞环，difference 混合）；`composables/useMouseFx.ts` 提供 `data-tilt`（3D 跟手倾斜）/ `data-spot`（光标聚光斑 --mx/--my）/ `data-magnet`（磁吸按钮），仅桌面 fine 指针生效、尊重减弱动态。
- **无障碍**：全局尊重 `prefers-reduced-motion`（CSS 与 JS 双重降级），`:focus-visible` 焦点环、点击元素 cursor:pointer。
- **滚动条**：WebKit + Firefox 主题化（青绿→电光蓝渐变）。

## 7. GSAP 使用规范（motion-driven 要点）

- 路由切换为**方向感知滑动过场**（App.vue）：旧页沿导航方向滑出（0.4s power3.inOut），新页从反侧滑入（0.55s expo.out）；方向由导航顺序数组决定。注意 `:key` 必须挂在 `<component>` 上而非 `<Transition>` 上，否则 leave/enter 钩子不触发。
- 路由已全部**同步加载**（无懒加载），保证切页零空窗。
- 桌面端（≥1001px）组别板块为 **pin + scrub 横向穿行**（GroupsSection，gsap.matchMedia 隔离，移动端退化为纵向堆叠）。
- 跑马灯速率与**滚动速度联动**（MarqueeBand，ScrollTrigger.getVelocity → timeScale）。

## 8. GSAP 历史规范（承上）

- `gsap.registerPlugin(ScrollTrigger)` 只在 `main.ts` 执行一次。
- 通用滚动入场：组件内 `const root = ref(...)` + `useScrollReveal(root)`，元素加 `data-reveal` 属性；该 composable 基于 `gsap.context` 管理生命周期（卸载自动 revert）。
- 私有动画：组件 `onMounted` 内用 `gsap.context(() => {...}, root)` 包裹，作用域选择器 + 自动清理。
- 逐字动画：`charsHtml()` 生成 `<span class="char">`，配合外层 `overflow:hidden` 行做 yPercent 入场（见 HeroSection）。
- **文案为先、动效为辅**：demo 页面文字精简，动效编排（入场节奏 + 滚动触发 + 微交互），不要散射式动画。

## 9. 开发约定

- 页面文案一律中文，风格精炼、机甲主题（如「以代码铸甲，以热血参战」）。
- 提交信息遵循 Conventional Commits（`feat:` / `fix:` / `docs:` …），推送到 `main`。
- 西文/数字由 Russo One / Chakra Petch latin 子集覆盖、中文回退系统字体，新增字符无需子集化；改动样式后需重新 `npm run build`。改动页面时注意：强动画（pin/scrub）仅绑定桌面端（≥1001px），移动端已退化，勿全局开启。
- 官方静态资源不落库：`frontend/dist/`、`frontend/node_modules/`、`.venv/`、`db.sqlite3` 均忽略。

## 10. 注意事项 / 陷阱

- **管理员密码**：`polarbear / 219200` 仅 6 位，低于 Django 默认 8 位校验；创建时必须程序化绕过（`User.objects.create_superuser` + `set_password`），`createsuperuser` 交互命令会被校验拦下。
- **db.sqlite3 未提交**：clone 后需 `migrate` + 重新创建管理员，才有后台账号。
- `SECRET_KEY` 为 demo 硬编码密钥；`ALLOWED_HOSTS=['*']`、`DEBUG=True` 仅限开发，公开部署前需处理。
- 简历表单（§5 RecruitSection）目前只是前端 demo 提示，未接后端存储；接入时表单字段/提交接口按现有结构扩展。
- 组别当前为 4 个（机械/电控/算法/运营），导航、Hero、招新资讯、投递表单等多处文案需同步，改动时全局搜索确认。