<script setup lang="ts">
import { ref } from 'vue'
import { useScrollReveal } from '../composables/useGsapReveal'

const root = ref<HTMLElement | null>(null)
useScrollReveal(root, { stagger: 0.06, y: 36 })

const groups = [
  {
    code: 'MEC',
    name: '机械组',
    en: 'MECHANICAL',
    d: '机器人结构设计与加工装配：云台、底盘、发射机构的机械美学。',
    stack: ['SolidWorks', 'ANSYS', '碳纤维加工', '3D 打印'],
    need: '懂公差，也懂暴力美学',
  },
  {
    code: 'ELC',
    name: '电控组',
    en: 'EMBEDDED CONTROL',
    d: '嵌入式控制与机器人决策：让每一度转角都有依据。',
    stack: ['STM32', 'FreeRTOS', 'CAN 总线', 'PID', '传感器融合'],
    need: '写过驱动，调过 PID',
  },
  {
    code: 'ALG',
    name: '算法组',
    en: 'VISION & ALGORITHM',
    d: '视觉感知与自动瞄准：让机器人看见、判断、开火。',
    stack: ['C++', 'Python', 'OpenCV', '深度学习', 'ROS'],
    need: '跑通过 Demo，更喜欢真枪实弹',
  },
  {
    code: 'OPR',
    name: '运营组',
    en: 'OPERATION & MEDIA',
    d: '宣传、财务与赛事运营：让战队的战绩被看见。',
    stack: ['剪辑', '平面设计', '文案', '项目管理'],
    need: '能写能剪，也能算账',
  },
]
</script>

<template>
  <section id="groups" ref="root" class="groups">
    <div class="container">
      <p class="eyebrow" data-reveal>04 / 组别介绍</p>
      <h2 class="groups-title" data-reveal>四大组别与技术栈</h2>
      <p class="groups-lead" data-reveal>一辆车从图纸到赛场，需要四双手。</p>

      <div class="groups-grid">
        <article v-for="g in groups" :key="g.code" class="group" data-reveal>
          <div class="group-top">
            <span class="group-code">{{ g.code }}</span>
            <span class="group-en">{{ g.en }}</span>
          </div>
          <h3 class="group-name">{{ g.name }}</h3>
          <p class="group-desc">{{ g.d }}</p>
          <div class="group-stack">
            <span v-for="s in g.stack" :key="s" class="stack-tag">{{ s }}</span>
          </div>
          <p class="group-need"><span class="need-flag">招募</span>{{ g.need }}</p>
        </article>
      </div>
    </div>
  </section>
</template>

<style scoped>
.groups { padding: 0 0 150px; }
.groups-title {
  margin-top: 22px;
  font-size: clamp(1.9rem, 4vw, 3.1rem);
}
.groups-lead { margin-top: 18px; color: var(--ink-dim); }

.groups-grid {
  margin-top: 54px;
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.group {
  position: relative;
  padding: 26px 24px 24px;
  border: 1px solid var(--line);
  border-radius: 14px;
  background: linear-gradient(160deg, rgba(255, 255, 255, 0.03), transparent 70%);
  overflow: hidden;
  transition: border-color 0.35s, transform 0.35s var(--ease);
}
.group::before {
  content: "";
  position: absolute;
  inset: 0;
  background: radial-gradient(240px 140px at 50% 0%, rgba(45, 226, 166, 0.10), transparent 70%);
  opacity: 0;
  transition: opacity 0.35s;
}
.group:hover { border-color: rgba(45, 226, 166, 0.5); transform: translateY(-4px); }
.group:hover::before { opacity: 1; }

.group-top { display: flex; align-items: center; justify-content: space-between; position: relative; }
.group-code {
  font-family: var(--mono);
  font-size: 0.72rem;
  letter-spacing: 0.14em;
  color: var(--accent);
  border: 1px solid rgba(45, 226, 166, 0.4);
  border-radius: 6px;
  padding: 3px 8px;
}
.group-en {
  font-family: var(--mono);
  font-size: 0.6rem;
  letter-spacing: 0.12em;
  color: var(--ink-faint, #5b6673);
}
.group-name { margin-top: 22px; font-size: 1.3rem; position: relative; }
.group-desc { margin-top: 12px; font-size: 0.9rem; color: var(--ink-dim); position: relative; }

.group-stack {
  margin-top: 18px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  position: relative;
}
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
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px dashed var(--line);
  font-size: 0.86rem;
  color: var(--ink-dim);
  position: relative;
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

@media (max-width: 760px) {
  .groups-grid { grid-template-columns: 1fr; }
  .groups { padding: 0 0 110px; }
}
</style>
