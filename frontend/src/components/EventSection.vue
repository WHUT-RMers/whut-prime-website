<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { gsap } from 'gsap'
import { useScrollReveal } from '../composables/useGsapReveal'
import { prefersReducedMotion, countUp } from '../utils/motion'
import { useMouseFx } from '../composables/useMouseFx'
import PlaceholderImage from './PlaceholderImage.vue'

const root = ref<HTMLElement | null>(null)
useScrollReveal(root, { blur: 4, stagger: 0.08 })
useMouseFx(root)

const events = [
  {
    tag: 'RMUC',
    name: '机甲大师超级对抗赛',
    d: 'RoboMaster 最高级别赛事，侧重考察队员对理工学科的综合应用与工程实践能力，融合机器视觉、嵌入式系统设计、机械工程、自主导航、人机交互、射频前端等众多技术学科，将流行呈现方式与机器人竞技结合，对抗直观激烈。',
  },
  {
    tag: 'RMUL',
    name: '机甲大师高校联盟赛',
    d: '由地方学术机构及高校申办，辐射周边高校参赛，旨在促进区域性高校机器人技术交流，形成浓厚学术氛围，为地区科技创新发展助力。',
  },
  {
    tag: 'RMUA',
    name: '机甲大师高校人工智能挑战赛',
    d: '致力于发展人工智能前沿技术。自 2022 赛季起赛事规则拓展至感知定位、规划控制算法方向，设立无人飞行器赛项，加速推动智能感知、定位导航与自主控制等领域的技术创新。',
  },
]

const impact = [
  { v: 11, suffix: '', label: '年赛事历程' },
  { v: 400, suffix: '+', label: '全球参赛高校' },
  { v: 10, suffix: ' 万+', label: '青年工程师' },
]

onMounted(() => {
  const el = root.value
  if (!el || prefersReducedMotion()) return
  const q = gsap.utils.selector(el)

  /* 序号横向漂移视差 + 战役标记线生长 */
  q('.event-item').forEach((item: Element, i: number) => {
    const idx = item.querySelector('.event-index')
    if (idx) {
      gsap.fromTo(
        idx,
        { x: i % 2 ? 26 : -26 },
        { x: i % 2 ? -26 : 26, ease: 'none', scrollTrigger: { trigger: item, start: 'top bottom', end: 'bottom top', scrub: 0.8 } },
      )
    }
    const marker = item.querySelector('.event-marker')
    if (marker) {
      gsap.fromTo(
        marker,
        { scaleY: 0 },
        { scaleY: 1, transformOrigin: 'top', ease: 'none', scrollTrigger: { trigger: item, start: 'top 82%', end: 'bottom 55%', scrub: 0.6 } },
      )
    }
  })

  /* 影响数据计数 */
  el.querySelectorAll<HTMLElement>('[data-count]').forEach((node) => {
    const target = Number(node.dataset.count)
    countUp(node, target, 1.8, 'power2.out', 0.2)
  })
})
</script>

<template>
  <section id="event" ref="root" class="event">
    <div class="container">
      <div class="event-head">
        <p class="eyebrow" data-reveal>01 / 赛事介绍</p>
        <h2 class="event-title" data-reveal>RoboMaster 机甲大师高校系列赛</h2>
        <p class="event-lead" data-reveal>
          作为全国大学生机器人大赛旗下赛事之一，是专为全球科技爱好者打造的机器人竞技与
          学术交流平台。自 2013 年创办至今，始终秉承「为青春赋予荣耀，让思考拥有力量，
          服务全球青年工程师成为追求极致、有实干精神的梦想家」的理念。
        </p>
      </div>

      <div class="event-grid">
        <div class="event-items">
          <article v-for="(e, i) in events" :key="e.tag" class="event-item" data-reveal>
            <span class="event-marker" aria-hidden="true"></span>
            <span class="event-index">{{ String(i + 1).padStart(2, '0') }}</span>
            <div class="event-item-body">
              <div class="event-item-head">
                <span class="event-tag">{{ e.tag }}</span>
                <h3 class="event-item-title">{{ e.name }}</h3>
              </div>
              <p class="event-item-desc">{{ e.d }}</p>
            </div>
          </article>
        </div>
        <div class="event-media" data-reveal data-spot>
          <PlaceholderImage label="赛事现场 / 赛场照片" ratio="16 / 10" accent />
          <div class="event-impact">
            <div v-for="s in impact" :key="s.label" class="imp">
              <p class="imp-num"><span :data-count="s.v">0</span><span class="imp-suffix">{{ s.suffix }}</span></p>
              <p class="imp-label">{{ s.label }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.event { padding: 130px 0 150px; }
.event-head { max-width: 780px; }
.event-title {
  margin-top: 22px;
  font-size: clamp(1.9rem, 4vw, 3.1rem);
}
.event-lead { margin-top: 18px; color: var(--ink-dim); font-size: 1.02rem; }

.event-grid {
  margin-top: 56px;
  display: grid;
  grid-template-columns: minmax(0, 7fr) minmax(0, 5fr);
  gap: 48px;
  align-items: start;
}

.event-items { display: flex; flex-direction: column; gap: 34px; }
.event-item {
  position: relative;
  display: flex;
  gap: 22px;
  padding: 8px 16px 30px 8px;
  border-bottom: 1px solid var(--line);
}
.event-item:last-child { border-bottom: none; padding-bottom: 8px; }
.event-item:hover .event-item-head { transform: translateX(6px); }

.event-marker {
  position: absolute;
  left: 0;
  top: 10px;
  width: 3px;
  height: calc(100% - 40px);
  background: var(--accent);
  transform-origin: top;
}
.event-index {
  font-family: var(--mono);
  font-size: 0.9rem;
  color: var(--accent);
  letter-spacing: 0.1em;
  padding: 6px 0 0 26px;
}
.event-item-head { display: flex; align-items: center; gap: 14px; flex-wrap: wrap; transition: transform 0.35s var(--ease-expo); }
.event-tag {
  font-family: var(--mono);
  font-size: 0.72rem;
  letter-spacing: 0.12em;
  color: var(--accent);
  border: 1px solid rgba(45, 226, 166, 0.4);
  border-radius: 6px;
  padding: 3px 10px;
  background: rgba(45, 226, 166, 0.05);
}
.event-item-title { font-size: 1.4rem; }
.event-item-desc { margin-top: 10px; color: var(--ink-dim); font-size: 0.96rem; }

.event-media { display: flex; flex-direction: column; gap: 22px; }

.event-impact {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  padding: 22px 16px;
  background: var(--surface);
  border-left: 3px solid var(--accent);
}
.imp { text-align: center; }
.imp-num {
  font-family: var(--mono);
  font-size: 1.9rem;
  font-weight: 700;
  color: var(--ink);
  font-variant-numeric: tabular-nums;
}
.imp-suffix { color: var(--accent); font-size: 0.6em; }
.imp-label { margin-top: 8px; font-size: 0.78rem; color: var(--ink-dim); }

@media (max-width: 880px) {
  .event-grid { grid-template-columns: 1fr; gap: 36px; }
  .event { padding: 90px 0 110px; }
}
@media (max-width: 520px) {
  .event-impact { grid-template-columns: 1fr; }
}
</style>