/**
 * 首屏（欢迎页）大图轮播内容。
 *
 * 图片槽位：slide.image 留空时渲染「扁平几何占位」面板（与全站占位风格一致），
 * 素材到位后只需填入地址即可，例如：
 *   image: '/static/hero/arena-battle.jpg'   // 文件放在 frontend/public/hero/ 下，构建后即 /static/hero/
 * 也可指向后端媒体：image: '/media/news/2026/09/xxx.jpg'
 * 建议横图 ≥ 1920×1080，深色、主体偏右，配合 focus 调整裁剪位置（如 '70% center'）。
 */

export type HeroCta = {
  label: string
  /** 站内路由（RouterLink） */
  to?: string
  /** 页面内锚点或外链 */
  href?: string
  /** 主按钮（实色） */
  primary?: boolean
}

export type HeroSlide = {
  id: string
  /** 序号，占位面板上的描边大字（有真图时不显示） */
  no: string
  eyebrow: string
  /** 标题分行，逐字入场 */
  title: string[]
  /** 该行标题用强调色（下标，缺省不加） */
  accentLine?: number
  sub: string
  ctas: HeroCta[]
  /** 大图地址，留空 → 几何占位 */
  image?: string
  /** 图片替代文本（装饰性图片留空即可） */
  alt?: string
  /** object-position，控制大图裁剪重心（移动端竖屏裁切主要靠它） */
  focus?: string
  /** 占位面板色调 */
  tone?: 'accent' | 'blue' | 'warm'
  /** 占位面板 / 刻度上的小标签 */
  tag?: string
}

export const heroSlides: HeroSlide[] = [
  {
    id: 'battle',
    no: '01',
    eyebrow: 'WHUT PRIME · 精研 覃思 笃志 力行 · 2027 SEASON',
    title: ['以代码铸甲', '以热血参战。'],
    accentLine: 1,
    sub: '武汉理工大学机甲大师 PRIME 战队，2022 年成立，隶属人工智能学院。机械、电控、视觉算法、商业运营四大组别，百余名队员，连续四年征战机甲大师高校联盟赛。',
    ctas: [
      { label: '投递简历', to: '/recruit', primary: true },
      { label: '了解赛事', href: '#event' },
    ],
    image: '/static/hero/arena-battle.jpg',
    alt: '赛场上对峙的步兵与英雄机器人',
    focus: '58% center',
    tone: 'accent',
    tag: '赛场 · 对抗',
  },
  {
    id: 'groups',
    no: '02',
    eyebrow: 'MEC · ELC · ALG · OPR',
    title: ['四大组别', '协同作战。'],
    accentLine: 1,
    sub: '结构设计与加工、嵌入式控制与视觉算法、品牌运营与商务合作——一台步兵机器人的诞生，由四个组别共同完成。',
    ctas: [
      { label: '组别技术', to: '/groups', primary: true },
      { label: '战队资讯', to: '/news' },
    ],
    image: '/static/hero/pits-debug.jpg',
    alt: '队员在赛场调试区检查机器人',
    focus: '52% center',
    tone: 'blue',
    tag: '调试区 · 组别',
  },
  {
    id: 'honors',
    no: '03',
    eyebrow: 'RMUL · 2022 — 2025',
    title: ['连续四年', '征战联盟赛。'],
    accentLine: 1,
    sub: '2022 年建队至今，PRIME 连续四个赛季出战机甲大师高校联盟赛，累计斩获 9 项全国二等奖，并持续向更高赛区发起冲击。',
    ctas: [
      { label: '历史荣誉', to: '/history', primary: true },
      { label: '商业合作', to: '/cooperate' },
    ],
    image: '/static/hero/team-group.jpg',
    alt: 'WHUT PRIME 战队在机甲大师高校联盟赛合影',
    focus: 'center',
    tone: 'warm',
    tag: '联盟赛 · 全队',
  },
  {
    id: 'operator',
    no: '04',
    eyebrow: 'OPERATOR · 第一视角',
    title: ['屏幕这头', '也是战场。'],
    accentLine: 1,
    sub: '操作手在操作间通过第一视角操控机器人，每一次走位与瞄准，都在毫秒之间决定攻防转换。',
    ctas: [
      { label: '战队资讯', to: '/news', primary: true },
      { label: '组别技术', to: '/groups' },
    ],
    image: '/static/hero/pit-operator.jpg',
    alt: '操作手在操作间操控机器人',
    focus: '60% center',
    tone: 'blue',
    tag: '操作间 · 操作手',
  },
  {
    id: 'courtside',
    no: '05',
    eyebrow: 'KEEP PUSHING · 备赛日常',
    title: ['登场三分钟', '备赛一整年。'],
    accentLine: 1,
    sub: '调车、复盘、改代码——赛场上每一次登场，背后都是整年备赛里反复推倒重来的日常。',
    ctas: [
      { label: '历史荣誉', to: '/history', primary: true },
      { label: '战队资讯', to: '/news' },
    ],
    image: '/static/hero/court-side.jpg',
    alt: '队员在场边观看比赛',
    focus: '40% center',
    tone: 'accent',
    tag: '场边 · 备赛',
  },
  {
    id: 'machines',
    no: '06',
    eyebrow: 'INFANTRY · HERO · ENGINEER',
    title: ['从图纸到赛场', '一台车一个赛季。'],
    accentLine: 1,
    sub: '结构、电控、算法在同一条产线上交汇，一台机器人从图纸走到赛场，要走完一整个赛季。',
    ctas: [
      { label: '组别技术', to: '/groups', primary: true },
      { label: '商业合作', to: '/cooperate' },
    ],
    image: '/static/hero/robot-duo.jpg',
    alt: '赛场上的两台步兵机器人',
    focus: '40% center',
    tone: 'warm',
    tag: '战车 · 兵种',
  },
]
