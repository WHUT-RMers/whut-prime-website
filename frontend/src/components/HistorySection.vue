<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { gsap } from 'gsap'
import { useScrollReveal } from '../composables/useGsapReveal'

const root = ref<HTMLElement | null>(null)
useScrollReveal(root, { stagger: 0.08 })

const milestones = [
  { year: '2017', t: '建队', d: '武汉理工大学第一支 RoboMaster 战队成立，从一间仓库开始。' },
  { year: '2019', t: '南部赛区一等奖', d: '首获区域赛一等奖，拿到通往全国赛的门票。' },
  { year: '2021', t: '全国赛十六强', d: '首次站上全国赛舞台，闯入十六强。' },
  { year: '2023', t: '全国赛八强', d: '刷新队史最佳战绩，多款机器人完成自研迭代。' },
  { year: '2026', t: '新赛季', d: '全新赛季开启，整装待发。' },
]

const honors = ['全国八强', '全国十六强 ×2', '南部赛区一等奖 ×3', '最佳工程奖', '最佳新队奖', '优秀指导老师']

const stats = [
  { v: 9, suffix: '', label: '参赛赛季' },
  { v: 120, suffix: '+', label: '正式比赛场次' },
  { v: 6, suffix: ' 项', label: '国家级荣誉' },
]

onMounted(() => {
  const el = root.value
  if (!el) return

  const fill = el.querySelector<HTMLElement>('.history-line-fill')
  if (fill) {
    gsap.fromTo(
      fill,
      { scaleY: 0 },
      {
        scaleY: 1,
        transformOrigin: 'top',
        ease: 'none',
        scrollTrigger: { trigger: el, start: 'top 60%', end: 'bottom 70%', scrub: 0.6 },
      },
    )
  }

  el.querySelectorAll<HTMLElement>('[data-count]').forEach((node) => {
    const target = Number(node.dataset.count)
    const obj = { v: 0 }
    gsap.to(obj, {
      v: target,
      duration: 1.8,
      ease: 'power2.out',
      scrollTrigger: { trigger: node, start: 'top 88%', once: true },
      onUpdate: () => {
        node.textContent = String(Math.round(obj.v))
      },
    })
  })
})
</script>

<template>
  <section id="history" ref="root" class="history">
    <div class="container">
      <p class="eyebrow" data-reveal>03 / 历史与荣誉</p>
      <h2 class="history-title" data-reveal>九年，从仓库到赛场</h2>

      <div class="history-layout">
        <div class="timeline">
          <div class="history-line"></div>
          <div class="history-line-fill"></div>
          <article v-for="m in milestones" :key="m.year" class="milestone" data-reveal>
            <span class="year">{{ m.year }}</span>
            <h3 class="milestone-title">{{ m.t }}</h3>
            <p class="milestone-desc">{{ m.d }}</p>
          </article>
        </div>

        <aside class="honor-side">
          <h3 class="honor-title" data-reveal>荣誉墙</h3>
          <ul class="honor-list">
            <li v-for="h in honors" :key="h" data-reveal>{{ h }}</li>
          </ul>
          <div class="honor-stats">
            <div v-for="s in stats" :key="s.label" class="hstat" data-reveal>
              <p class="hstat-num"><span :data-count="s.v">0</span>{{ s.suffix }}</p>
              <p class="hstat-label">{{ s.label }}</p>
            </div>
          </div>
        </aside>
      </div>
    </div>
  </section>
</template>

<style scoped>
.history { padding: 0 0 150px; }
.history-title {
  margin-top: 22px;
  font-size: clamp(1.9rem, 4vw, 3.1rem);
}

.history-layout {
  margin-top: 60px;
  display: grid;
  grid-template-columns: minmax(0, 7fr) minmax(0, 5fr);
  gap: 64px;
}

.timeline { position: relative; padding-left: 30px; }
.history-line {
  position: absolute;
  left: 6px;
  top: 4px;
  bottom: 4px;
  width: 1px;
  background: var(--line);
}
.history-line-fill {
  position: absolute;
  left: 6px;
  top: 4px;
  bottom: 4px;
  width: 1px;
  background: var(--accent);
  box-shadow: 0 0 12px rgba(45, 226, 166, 0.6);
  transform-origin: top;
}

.milestone { position: relative; padding: 0 0 42px; }
.milestone::before {
  content: "";
  position: absolute;
  left: -30px;
  top: 8px;
  width: 13px;
  height: 13px;
  border-radius: 50%;
  border: 2px solid var(--accent);
  background: var(--bg);
}
.year {
  font-family: var(--mono);
  font-size: 0.82rem;
  letter-spacing: 0.22em;
  color: var(--accent);
}
.milestone-title { margin-top: 10px; font-size: 1.45rem; }
.milestone-desc { margin-top: 10px; color: var(--ink-dim); font-size: 0.96rem; max-width: 520px; }

.honor-side { position: sticky; top: 110px; align-self: start; }
.honor-title { font-size: 1.35rem; }
.honor-list { list-style: none; margin-top: 20px; display: flex; flex-wrap: wrap; gap: 10px; }
.honor-list li {
  font-family: var(--mono);
  font-size: 0.76rem;
  letter-spacing: 0.06em;
  padding: 7px 14px;
  border: 1px solid rgba(45, 226, 166, 0.35);
  border-radius: 999px;
  color: var(--ink);
  background: rgba(45, 226, 166, 0.05);
}

.honor-stats {
  margin-top: 40px;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 14px;
}
.hstat { border: 1px solid var(--line); border-radius: 12px; padding: 20px 14px; text-align: center; }
.hstat-num {
  font-family: var(--mono);
  font-size: 1.7rem;
  font-weight: 700;
  color: var(--accent);
  font-variant-numeric: tabular-nums;
}
.hstat-label { margin-top: 8px; font-size: 0.78rem; color: var(--ink-dim); }

@media (max-width: 880px) {
  .history-layout { grid-template-columns: 1fr; gap: 56px; }
  .honor-side { position: static; }
  .history { padding: 0 0 110px; }
}
</style>
