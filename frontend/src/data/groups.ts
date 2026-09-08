/**
 * 四大组别共享数据：首页 04 组别介绍（GroupsSection）、组别列表页（GroupsView）
 * 与组别详情页（GroupDetailView）统一从这里取数，保证文案一致。
 * 详情字段（intro / quote / stats / gallery）为占位内容，正式素材到位后替换。
 */

export interface GroupStat {
  v: number
  suffix: string
  label: string
}

export interface GroupInfo {
  code: string
  name: string
  en: string
  /** 卡片强调色相（hsl） */
  hue: number
  /** 一句话介绍（卡片 / 列表 / 详情页头部） */
  d: string
  /** 列表页主图占位标签 */
  image: string
  /** 详情页定位金句 */
  quote: string
  /** 详情页正文（占位段落） */
  intro: string[]
  stack: string[]
  tasks: string[]
  need: string
  /** 详情页数据占位 */
  stats: GroupStat[]
  /** 详情页图集占位标签 */
  gallery: string[]
}

export const groups: GroupInfo[] = [
  {
    code: 'MEC',
    name: '机械组',
    en: 'MECHANICAL',
    hue: 158,
    d: '负责机器人结构设计与加工装配：云台、底盘、发射机构、悬挂系统的机械美学与可靠性。',
    image: '机械结构设计 / 装配调试现场',
    quote: '把图纸变成能扛住赛场冲击的结构',
    intro: [
      '机械组负责 PRIME 全部在役机器人的结构设计与加工装配：云台、底盘、发射机构、悬挂系统……从概念草图到 CNC 出件，再到赛前紧张的装配联调，每一台战车都从这里下线。',
      '我们讲究「懂公差，也懂暴力美学」：既要在 SolidWorks 里把干涉检查做到零，也要让结构在赛场上扛住连续高速发射的冲击与对抗。',
    ],
    stack: ['SolidWorks', 'ANSYS', '碳纤维加工', '3D 打印', '公差分析'],
    tasks: ['底盘与云台结构设计', '发射机构研发', '轻量化材料工艺', '装配与调试支持'],
    need: '懂公差，也懂暴力美学；有设计软件基础者优先',
    stats: [
      { v: 12, suffix: '+', label: '赛季结构迭代版本' },
      { v: 30, suffix: '%', label: '车体平均轻量化' },
      { v: 360, suffix: '°', label: '云台全向转动范围' },
    ],
    gallery: ['云台结构装配台架', '碳纤维车架与 3D 打印件', '发射机构试射现场'],
  },
  {
    code: 'ELC',
    name: '电控组',
    en: 'EMBEDDED CONTROL',
    hue: 208,
    d: '负责嵌入式系统设计与机器人决策：让每一度转角都有依据，让每一帧信号都可靠。',
    image: '电控调试 / 硬件联调现场',
    quote: '让每一度转角都有依据，让每一帧信号都可靠',
    intro: [
      '电控组负责嵌入式系统设计与机器人决策：从 STM32 固件、FreeRTOS 任务编排，到 CAN 总线上几十个外设的联调，再到整车电气布线，是战车的「神经系统」。',
      '赛季里我们与机械、视觉高频对接：电机控制、弹道解算、传感器融合……在每一场对抗赛前把代码烧进车里，然后在调试区与时间赛跑。',
    ],
    stack: ['STM32', 'FreeRTOS', 'CAN 总线', 'PID', '射频前端'],
    tasks: ['驱动与底盘控制', '云台与弹道控制', '传感器融合', '整车电气布线'],
    need: '写过驱动，调过 PID；掌握 C / 嵌入式基础',
    stats: [
      { v: 40, suffix: '+', label: 'CAN 总线节点数' },
      { v: 2, suffix: ' kHz', label: '云台外环控制频率' },
      { v: 99, suffix: '%', label: '控制指令送达率' },
    ],
    gallery: ['电控调试台与示波器', '整车电气布线', '联调现场：车手视角'],
  },
  {
    code: 'VIS',
    name: '视觉算法组',
    en: 'VISION & ALGORITHM',
    hue: 268,
    d: '负责机器视觉与自主导航：让机器人看见、判断、自主行动，在赛场上快人一秒。',
    image: '视觉识别 / 算法调试现场',
    quote: '让机器人先看见，再判断，然后行动',
    intro: [
      '视觉算法组负责机器视觉与自主导航：自瞄、能量机关识别、反小陀螺、SLAM 定位……用 C++ / Python 和深度学习模型，让机器人在赛场上「快人一秒」。',
      '我们在仿真与真车之间反复横跳：数据集标注、模型蒸馏、端到端延迟优化，最后把推理管线部署到车上的计算平台里跑起来。',
    ],
    stack: ['C++', 'Python', 'OpenCV', '深度学习', 'SLAM / 自主导航'],
    tasks: ['自瞄与能量机关识别', '反小陀螺与目标跟踪', '导航与感知定位', '仿真与数据集'],
    need: '跑通过 Demo，更喜欢真枪实弹；熟悉 C++ 或 Python',
    stats: [
      { v: 30, suffix: ' fps', label: '自瞄推理帧率' },
      { v: 90, suffix: '%', label: '装甲板识别准确率' },
      { v: 2, suffix: ' ms', label: '端到端识别延迟' },
    ],
    gallery: ['自瞄调试界面', '能量机关识别模型', 'SLAM 构图可视化'],
  },
  {
    code: 'COM',
    name: '商业运营组',
    en: 'COMMERCIAL & OPERATION',
    hue: 32,
    d: '负责赛事运营、商业赞助与媒体矩阵：让战队的战绩被看见，让资源支撑梦想。',
    image: '运营企划 / 媒体内容制作',
    quote: '让战队的战绩被看见，让资源支撑梦想',
    intro: [
      '商业运营组负责赛事运营、商业赞助与媒体矩阵：从招商方案到赞助权益落地，从公众号推文到 B 站高光集锦，让 PRIME 的声音被更多人听到。',
      '我们写得了推文、剪得了视频、做得了方案、谈得了合作——把战队的每一点进步，都变成可被看见、可被记住的内容与资源。',
    ],
    stack: ['公众号 / 视频号', 'B 站 / 抖音', '平面设计', '项目管理'],
    tasks: ['招商与赞助对接', '社媒内容生产', '品牌视觉设计', '赛事运营与财务'],
    need: '能写能剪，也能谈合作；对新媒体敏感',
    stats: [
      { v: 100, suffix: '万+', label: '赛季全网曝光' },
      { v: 3, suffix: ' 个', label: '赞助合作方向' },
      { v: 6, suffix: ' 条/周', label: '内容更新产能' },
    ],
    gallery: ['赛事现场记录', '赞助品牌联名物料', '演播间解说与直播'],
  },
]

export function groupByCode(code: string): GroupInfo | undefined {
  return groups.find((g) => g.code === code.toUpperCase())
}

/** 组别详情页路由 */
export function groupRoute(code: string): string {
  return `/groups/${code.toLowerCase()}`
}