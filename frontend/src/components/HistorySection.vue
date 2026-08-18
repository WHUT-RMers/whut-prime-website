<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { gsap } from 'gsap'
import { useScrollReveal } from '../composables/useGsapReveal'

const root = ref<HTMLElement | null>(null)
useScrollReveal(root, { stagger: 0.08 })

const milestones = [
  { year: '2022', t: '建队', d: '武汉理工大学机甲大师 PRIME 战队成立，隶属于人工智能学院，得到本科生院、科学技术发展院、团委等多家单位大力支持。' },
  { year: '2023', t: '首战联盟赛', d: '首次代表学校参加 RoboMaster 机甲大师高校联盟赛，斩获全国奖项。' },
  { year: '2024', t: '再创佳绩', d: '连续第二年出征，全国获奖数量持续累积，队伍规模突破百人。' },
  { year: '2025', t: '深耕赛项', d: '第三年参赛，在超级对抗赛、高校联盟赛等赛项中全面练兵。' },
  { year: '2026', t: '四年磨砺', d: '连续四年征战高校联盟赛，累计全国二等奖 9 次、全国三等奖 17 次。' },
  { year: '2027', t: '新赛季', d: '2027 赛季招商开启，全新赛季整装待发。' },
]

const honors = ['全国二等奖 ×9', '全国三等奖 ×17', '连续四年参赛', '五大平台媒体矩阵', '全网粉丝 1500+', '累计流量 31w+']

const stats = [
  { v: 9, suffix: ' 次', label: '全国二等奖' },
  { v: 17, suffix: ' 次', label: '全国三等奖' },
  { v: 31, suffix: 'w+', label: '全网累计流量' },
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
      <h2 class="history-title" data-reveal>四年，从成立到屡获殊荣</h2>

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
