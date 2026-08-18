<script setup lang="ts">
import { ref } from 'vue'
import PageHeader from '../components/PageHeader.vue'
import PlaceholderImage from '../components/PlaceholderImage.vue'
import { useScrollReveal } from '../composables/useGsapReveal'

const root = ref<HTMLElement | null>(null)
useScrollReveal(root, { stagger: 0.08 })

const groups = [
  {
    code: 'MEC',
    name: '机械组',
    en: 'MECHANICAL',
    d: '负责机器人结构设计与加工装配：云台、底盘、发射机构、悬挂系统的机械美学与可靠性。',
    image: '机械结构设计 / 装配调试现场',
    stack: ['SolidWorks', 'ANSYS', '碳纤维加工', '3D 打印', '公差分析'],
    tasks: ['底盘与云台结构设计', '发射机构研发', '轻量化材料工艺', '装配与调试支持'],
    need: '懂公差，也懂暴力美学；有设计软件基础者优先',
  },
  {
    code: 'ELC',
    name: '电控组',
    en: 'EMBEDDED CONTROL',
    d: '负责嵌入式系统设计与机器人决策：让每一度转角都有依据，让每一帧信号都可靠。',
    image: '电控调试 / 硬件联调现场',
    stack: ['STM32', 'FreeRTOS', 'CAN 总线', 'PID', '射频前端'],
    tasks: ['驱动与底盘控制', '云台与弹道控制', '传感器融合', '整车电气布线'],
    need: '写过驱动，调过 PID；掌握 C / 嵌入式基础',
  },
  {
    code: 'VIS',
    name: '视觉算法组',
    en: 'VISION & ALGORITHM',
    d: '负责机器视觉与自主导航：让机器人看见、判断、自主行动，在赛场上快人一秒。',
    image: '视觉识别 / 算法调试现场',
    stack: ['C++', 'Python', 'OpenCV', '深度学习', 'SLAM / 自主导航'],
    tasks: ['自瞄与能量机关识别', '反小陀螺与目标跟踪', '导航与感知定位', '仿真与数据集'],
    need: '跑通过 Demo，更喜欢真枪实弹；熟悉 C++ 或 Python',
  },
  {
    code: 'COM',
    name: '商业运营组',
    en: 'COMMERCIAL & OPERATION',
    d: '负责赛事运营、商业赞助与媒体矩阵：让战队的战绩被看见，让资源支撑梦想。',
    image: '运营企划 / 媒体内容制作',
    stack: ['公众号 / 视频号', 'B 站 / 抖音', '平面设计', '项目管理'],
    tasks: ['招商与赞助对接', '社媒内容生产', '品牌视觉设计', '赛事运营与财务'],
    need: '能写能剪，也能谈合作；对新媒体敏感',
  },
]
</script>

<template>
  <div class="page">
    <div class="container">
      <PageHeader
        eyebrow="04 / 组别介绍"
        title="四大组别与技术栈"
        desc="一辆车从图纸到赛场，需要四双手。无论你擅长结构、代码、算法还是运营，PRIME 都有你的位置。"
      />
    </div>

    <div ref="root" class="container">
      <article v-for="(g, i) in groups" :key="g.code" class="group" data-reveal>
        <div class="group-media">
          <PlaceholderImage :label="g.image" ratio="4 / 3" accent />
        </div>
        <div class="group-body">
          <div class="group-head">
            <span class="group-index">{{ String(i + 1).padStart(2, '0') }}</span>
            <span class="group-code">{{ g.code }}</span>
            <span class="group-en">{{ g.en }}</span>
          </div>
          <h2 class="group-name">{{ g.name }}</h2>
          <p class="group-desc">{{ g.d }}</p>

          <div class="group-section">
            <p class="group-label">工作内容</p>
            <ul class="task-list">
              <li v-for="t in g.tasks" :key="t">{{ t }}</li>
            </ul>
          </div>

          <div class="group-section">
            <p class="group-label">技术栈</p>
            <div class="stack-list">
              <span v-for="s in g.stack" :key="s" class="stack-tag">{{ s }}</span>
            </div>
          </div>

          <p class="group-need"><span class="need-flag">招募</span>{{ g.need }}</p>
        </div>
      </article>

      <div class="cta-row" data-reveal>
        <p class="cta-text">找到属于你的组别了吗？</p>
        <RouterLink to="/recruit" class="btn btn-primary">投递简历 <span aria-hidden="true">→</span></RouterLink>
      </div>
    </div>
  </div>
</template>

<style scoped>
.page { padding-bottom: 150px; }

.group {
  margin-top: 64px;
  display: grid;
  grid-template-columns: minmax(0, 5fr) minmax(0, 7fr);
  gap: 40px;
  align-items: center;
  border: 1px solid var(--line);
  border-radius: 18px;
  padding: 34px;
  background: linear-gradient(160deg, rgba(255, 255, 255, 0.03), transparent 60%);
}
.group-media { min-width: 0; }

.group-head { display: flex; align-items: center; gap: 14px; }
.group-index { font-family: var(--mono); font-size: 0.85rem; color: var(--accent); letter-spacing: 0.1em; }
.group-code {
  font-family: var(--mono);
  font-size: 0.7rem;
  letter-spacing: 0.14em;
  color: var(--accent);
  border: 1px solid rgba(45, 226, 166, 0.4);
  border-radius: 6px;
  padding: 3px 8px;
}
.group-en { font-family: var(--mono); font-size: 0.6rem; letter-spacing: 0.14em; color: #5b6673; }

.group-name { margin-top: 16px; font-size: 1.7rem; }
.group-desc { margin-top: 12px; color: var(--ink-dim); font-size: 0.98rem; }

.group-section { margin-top: 22px; }
.group-label {
  font-family: var(--mono);
  font-size: 0.68rem;
  letter-spacing: 0.2em;
  color: var(--ink-dim);
}
.task-list { list-style: none; margin-top: 12px; display: flex; flex-wrap: wrap; gap: 10px; }
.task-list li {
  font-size: 0.86rem;
  color: var(--ink);
  border: 1px solid var(--line);
  border-radius: 999px;
  padding: 6px 14px;
  background: rgba(255, 255, 255, 0.02);
}
.stack-list { margin-top: 12px; display: flex; flex-wrap: wrap; gap: 8px; }
.stack-tag {
  font-family: var(--mono);
  font-size: 0.68rem;
  letter-spacing: 0.04em;
  padding: 4px 10px;
  border: 1px solid var(--line);
  border-radius: 999px;
  color: var(--ink-dim);
}

.group-need {
  margin-top: 22px;
  padding-top: 18px;
  border-top: 1px dashed var(--line);
  font-size: 0.9rem;
  color: var(--ink-dim);
}
.need-flag {
  font-family: var(--mono);
  font-size: 0.66rem;
  letter-spacing: 0.1em;
  color: var(--accent-ink);
  background: var(--accent);
  border-radius: 5px;
  padding: 2px 8px;
  margin-right: 10px;
}

.cta-row {
  margin-top: 70px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 24px;
  flex-wrap: wrap;
  border: 1px solid rgba(45, 226, 166, 0.3);
  border-radius: 18px;
  padding: 40px 32px;
  background: rgba(45, 226, 166, 0.04);
}
.cta-text { font-size: 1.15rem; }

@media (max-width: 880px) {
  .group { grid-template-columns: 1fr; padding: 24px; gap: 24px; }
  .group-media { max-width: 520px; }
}
</style>
