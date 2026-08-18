# WHUT PRIME 设计规范（design system）

> 本项目所有页面 / 组件的视觉实现**必须**以本文档为准。
> 新增页面或组件时，先阅读本文档，严格按以下规范执行，保证全站风格统一。
> 实现载体：`frontend/src/style.css`（全局变量） + 各组件 scoped 样式。

---

## 1. 配色

主题：**夜黑 × 荧光青绿**（单强调色，整体克制、机甲/科技感）。

### 1.1 核心色板（:root 变量）

| 变量 | 色值 | 用途 |
|---|---|---|
| `--bg` | `#06080c` | 页面主背景（夜黑） |
| `--bg-soft` | `#0b0f16` | 次级背景：卡片底色 / 色块区 |
| `--accent` | `#2de2a6` | **主强调色**（荧光青绿）：按钮、链接、编号、时间线、高亮 |
| `--accent-ink` | `#06110c` | 主色之上的文字（按钮文字、色块文字） |
| `--ink` | `#e8ecf1` | 主文字（玉白） |
| `--ink-dim` | `#9aa6b2` | 次级文字：正文描述、标签、次级信息 |
| `--line` | `rgba(255,255,255,0.09)` | 边框 / 分割线 |

### 1.2 辅助色（局部使用，不作为主题色扩展）

| 名称 | 色值 | 用途 |
|---|---|---|
| 弱文字 | `#5b6673` | 最弱层级文字（日期、注释、小标签） |
| 青绿描边 | `rgba(45,226,166,0.4)` | 标签/徽章边框、CTA 提亮边框 |
| 蓝环境光 | `rgba(56,120,255,0.07)` | 背景左上角辅助光晕（仅一处） |
| 青绿光晕 | `rgba(45,226,166,0.10)` | 背景右上角主光晕、卡片 hover 顶部光 |

### 1.3 背景氛围（全局）

- 环境光：`body::before` 固定层，右上青绿 radial + 左上蓝 radial，叠加 `--bg`
- 颗粒噪点：`body::after`，opacity 0.05 的 SVG fractalNoise，fixed 覆盖全屏
- 选中色：背景 `--accent`、文字 `--accent-ink`

---

## 2. 字体

### 2.1 字体族

- 全站统一使用 `Inter`（自托管 woff2：`Inter-400.woff2` / `Inter-700.woff2`）
- 中文由系统无衬线回退：`PingFang SC → HarmonyOS Sans SC → Microsoft YaHei → Noto Sans SC`
- 统一栈：`--inter: "Inter", "PingFang SC", "HarmonyOS Sans SC", "Microsoft YaHei", "Noto Sans SC", "Helvetica Neue", Arial, sans-serif`（`--serif`/`--sans`/`--mono` 均指向它）
- 标题一律 700 字重；正文 400

### 2.2 字号 / 字重 / 行高规范

| 层级 | 字号 | 字重 | 行高 | 备注 |
|---|---|---|---|---|
| Hero 主标题 | `clamp(2.5rem, 8.5vw, 5.6rem)` | 700 | 1.12 | 字距 0.03em |
| 区块标题（各板块） | `clamp(1.9rem, 4vw, 3.1rem)` | 700 | 默认 | 标题前 `margin-top: 22px` |
| 详情页页头标题 | `clamp(2rem, 4.5vw, 3.5rem)` | 700 | 1.2 | 居中容器内 |
| 卡片标题 | `1.08rem – 1.7rem`（视卡片层级） | 700 | 1.35-1.4 | 卡片内标题如 1.08/1.15/1.35 |
| 正文 / 描述 | `0.9rem – 1.05rem` | 400 | 1.7 | 常用 0.95rem；正文色 `--ink-dim` |
| eyebrow 章节标签 | `0.72rem` | 400 | — | letter-spacing 0.28em、uppercase、`--accent` 色，前置 34px×1px 荧光横线 |
| 等宽感小标签（mono 槽位） | `0.6rem – 0.78rem` | 400 | — | letter-spacing 0.08~0.28em，用于编号/日期/技术栈标签 |

> 约定：新页面标题不要自创字号层级，复用上表；正文不超 1.05rem；小标签用 mono 槽位 + 大 letter-spacing。

---

## 3. 间距

### 3.1 全局栅格

- 内容容器 `.container`：`max-width: 1180px`，两侧留白 `24px`（`min(100% - 48px)`）
- 导航高度：`72px`（`--nav-h`），滚动锚点 `scroll-padding-top: calc(var(--nav-h) + 16px)`
- 动效曲线：`--ease: cubic-bezier(0.22, 1, 0.36, 1)`

### 3.2 模块间距（区块纵向节奏）

| 场景 | 值 |
|---|---|
| 区块上下留白（常规） | `padding: 130px 0 150px`（详情页大区块） |
| 小屏区块留白 | `padding: 0 0 110px` / `90px` |
| 区块头部（eyebrow 后） | 标题 `margin-top: 22px`，描述 `margin-top: 18px` |
| 区块内容与头部间距 | `margin-top: 54–56px`（标题下内容块） |
| 相邻内容组间距 | `48px / 64px / 90px`（按组重要性递进） |

### 3.3 页面常用间距

| 场景 | 值 |
|---|---|
| 卡片网格 gap | `16px`（标准）；双栏 `18px`；步骤网格 `14px` |
| 卡片内边距（普通卡） | `22px 20px / 24px 20px` |
| 卡片内边距（大卡：表单/联系/精选） | `30–36px` |
| 表单字段间 | `gap: 18px`；label 与输入框 `8px` |
| 输入框内边距 | `padding: 12px 14px` |
| 按钮内边距 | `padding: 14px 26px` |
| 按钮组 / 操作行 gap | `16px` |

---

## 4. 组件样式

### 4.1 按钮（`.btn`）

- 基础：`display: inline-flex; align-items: center; gap: 10px`；`padding: 14px 26px`；**`border-radius: 999px`**；`font-size: 0.95rem; font-weight: 700`；过渡 `0.35s var(--ease)`
- `btn-primary`：背景 `--accent`、文字 `--accent-ink`；hover：`translateY(-2px)` + 光晕 `box-shadow: 0 14px 34px -12px rgba(45,226,166,0.55)`
- `btn-ghost`：边框 `1px solid var(--line)`、文字 `--ink`、透明底；hover：边框/文字变 `--accent` + `translateY(-2px)`
- 按钮**不设固定阴影**（默认无阴影），仅 primary hover 有青色光晕

### 4.2 卡片

| 属性 | 规则 |
|---|---|
| 边框 | `1px solid var(--line)` |
| 圆角 | 小卡 **14px**；标准卡 **16px**；大卡（表单/联系/精选横幅）**18px** |
| 背景 | 渐变底 `linear-gradient(160deg, rgba(255,255,255,0.03), transparent 60%)`；纯色卡用 `--bg-soft` |
| hover | `border-color: rgba(45,226,166,0.45~0.5)` + `translateY(-4px)`（列表行可 `translateX(5px)`），过渡 `0.35s var(--ease)` |
| 阴影 | 默认无；hover 无投影（用位移 + 边框提亮表达反馈） |
| 顶部光 | 卡片 hover 或主要卡片可叠加 `radial-gradient(240px 140px at 50% 0%, rgba(45,226,166,0.10), transparent 70%)` 顶部光晕 |

### 4.3 导航栏（固定顶栏）

- 高度 72px、fixed top、z-index 60
- 常态：透明底、无底边；滚动后：`background: rgba(6,8,12,0.72)` + `backdrop-filter: blur(14px)` + 底边 `1px solid var(--line)`
- 链接：`font-size: 0.9rem`、`--ink-dim`；hover 变 `--ink` + 下划线 `::after`（1px accent，`scaleX(0→1)`，`0.35s var(--ease)`）；当前页（router-link-active）同 hover
- 链接间距 `gap: 24px`；品牌 mark：30×30、`border-radius: 8px`、accent 底
- 断点：980px 以下隐藏 CTA、720px 以下隐藏链接组

### 4.4 输入控件（表单）

- 输入框/选择/文本域：背景 `rgba(255,255,255,0.03)`、边框 `1px solid var(--line)`、**圆角 10px**、`padding: 12px 14px`、`font-size: 0.94rem`
- focus：`outline: none` + 边框 `--accent` + 背景 `rgba(45,226,166,0.04)`
- placeholder 色 `#5b6673`

### 4.5 标签 / 徽章（chips）

- 荧光标签（tag/编号）：`font-size: 0.66–0.72rem; letter-spacing: 0.12em`、`--accent` 字、边框 `1px solid rgba(45,226,166,0.4)`、**圆角 999px**、`padding: 3px 10px`
- 技术栈标签：同上但中性色 `--ink-dim`、边框 `--line`

### 4.6 其它组件约定

- **占位图**（图片未到位）：虚线边框 `1px dashed var(--line)`、圆角 14px、斜纹网格底（`--bg-soft`），居中相机图标 + 标注文字 + `PHOTO PLACEHOLDER`；替换成 `<img>` 时保持原有宽高比
- **时间线**：1px 竖线（`--line`，随滚动荧光填充线 `--accent`）+ 13px 圆点（2px accent 描边），年份 mono 槽位 accent 色
- **滚动条**：9px、轨道左 1px `--line`，滑块青绿渐变 + 圆角 99px + 微光晕，hover 提亮；Firefox 用 `scrollbar-color`

---

## 5. 响应式断点

| 断点 | 行为 |
|---|---|
| ≤1080px / ≤1000px | 4 列网格 → 2 列；详情页 5 档/组别列数收缩 |
| ≤980px | 导航隐藏 CTA、链接间距收紧 |
| ≤880px | 双栏布局（左文右图/双卡）→ 单栏 |
| ≤760px / ≤720px | 组别卡单列；导航隐藏链接组（仅品牌+CTA） |
| ≤640px / ≤620px / ≤560px | 区块留白减至 90–110px；卡片单列；页头内边距收窄 |

---

## 6. 动效（GSAP）约束

- 滚动入场统一用 `useScrollReveal`（元素加 `data-reveal`，fade + rise 28px，交错 0.06–0.09s，once）
- 页面切换过渡：旧页按点击方向左右消散（±72px + blur(4px)，0.38s），新页弹性弹入（scale 0.95→1，`back.out(1.6)` 0.55s）
- 微交互：卡片 hover 位移 + 边框提亮；按钮 hover 上浮 + 光晕
- 原则：**文案为先、动效为辅**，不做散射式动画

## 7. 合规检查清单（新增页面必查）

- [ ] 颜色取自 §1 色板变量（不新造色值）
- [ ] 标题字号 / 字重符合 §2.2 层级
- [ ] 区块留白按 §3.2 节奏（130/150px 或对应小屏值）
- [ ] 按钮 / 卡片 / 输入框的圆角、边框、hover 符合 §4
- [ ] 图片占位使用 `PlaceholderImage` 组件
- [ ] 断点按 §5 适配
- [ ] 滚动入场使用 `useScrollReveal`
