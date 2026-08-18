<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { gsap } from 'gsap'
import PageHeader from '../components/PageHeader.vue'
import PlaceholderImage from '../components/PlaceholderImage.vue'
import { useScrollReveal } from '../composables/useGsapReveal'

const root = ref<HTMLElement | null>(null)
useScrollReveal(root, { stagger: 0.07 })

const milestones = [
  { year: '2022', t: '建队', d: '武汉理工大学机甲大师 PRIME 战队成立，隶属于人工智能学院，得到本科生院、科学技术发展院、团委等多家单位大力支持。' },
  { year: '2023', t: '首战联盟赛', d: '首次代表学校参加 RoboMaster 机甲大师高校联盟赛，斩获全国奖项。' },
  { year: '2024', t: '再创佳绩', d: '连续第二年出征，全国获奖数量持续累积，队伍规模突破百人。' },
  { year: '2025', t: '深耕赛项', d: '第三年参赛，在超级对抗赛、高校联盟赛等赛项中全面练兵。' },
  { year: '2026', t: '四年磨砺', d: '连续四年征战高校联盟赛，累计全国二等奖 9 次、全国三等奖 17 次。' },
  { year: '2027', t: '新赛季', d: '2027 赛季招商开启，全新赛季整装待发。' },
]

const albums = [
  '赛场高光 / 联盟赛现场',
  '机器人整备 / 实验室日常',
  '技术答辩 / 赛季汇报',
  '团建合影 / 战队年会',
]

const competitions = [
  '中国汽车工程学会巴哈大赛', '中国大学生智能汽车竞赛',
  '中国机器人大赛暨 RoboCup 机器人世界杯中国赛', '中国国际大学生创新大赛',
  '西门子杯中国智能智造挑战赛', '全国大学生嵌入式芯片与系统设计竞赛',
  '中国机器人及人工智能大赛', '全国三维数字化创新设计大赛',
  '中国大学生计算机设计大赛', '全国周培源大学生力学竞赛',
  '学创杯全国大学生创业综合模拟大赛', '全国大学生电子设计竞赛',
  '全国大学生机械创新设计大赛', '全国大学生物理实验竞赛',
  '睿抗机器人开发者大赛', '大学生服务外包创新创业竞赛',
  '全国大学生统计建模竞赛', 'ACM-ICPC 国际大学生程序设计竞赛',
]

const stats = [
  { v: 9, suffix: ' 次', label: '全国二等奖' },
  { v: 17, suffix: ' 次', label: '全国三等奖' },
  { v: 31, suffix: 'w+', label: '全网累计流量' },
]

onMounted(() => {
  const el = root.value
  if (!el) return
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
  <div class="page">
    <div class="container">
      <PageHeader
        eyebrow="03 / 历史与荣誉"
        title="从 2022，走到全国赛场"
        desc="四年的深耕与积累——连续四年征战 RoboMaster 高校联盟赛，累计全国二等奖 9 次、全国三等奖 17 次。"
      />
    </div>

    <div ref="root" class="container">
      <!-- 相册占位 -->
      <div class="album-grid">
        <figure v-for="a in albums" :key="a" class="album" data-reveal>
          <PlaceholderImage :label="a" ratio="16 / 10" />
          <figcaption>{{ a }}</figcaption>
        </figure>
      </div>

      <!-- 时间线 -->
      <div class="timeline">
        <div class="timeline-line"></div>
        <article v-for="m in milestones" :key="m.year" class="milestone" data-reveal>
          <span class="year">{{ m.year }}</span>
          <h3 class="milestone-title">{{ m.t }}</h3>
          <p class="milestone-desc">{{ m.d }}</p>
        </article>
      </div>

      <!-- 数据 -->
      <div class="stats">
        <div v-for="s in stats" :key="s.label" class="stat" data-reveal>
          <p class="stat-num"><span :data-count="s.v">0</span>{{ s.suffix }}</p>
          <p class="stat-label">{{ s.label }}</p>
        </div>
      </div>

      <!-- 获奖赛事名录 -->
      <div class="comp-block">
        <h2 class="comp-title" data-reveal>队员获奖赛事名录</h2>
        <p class="comp-desc" data-reveal>依托 PRIME 平台，队员还活跃在全国各大高水平学科竞赛的赛场上。</p>
        <ul class="comp-list">
          <li v-for="c in competitions" :key="c" data-reveal>{{ c }}</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<style scoped>
.page { padding-bottom: 150px; }

.album-grid {
  margin-top: 56px;
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}
.album figcaption {
  margin-top: 10px;
  font-family: var(--mono);
  font-size: 0.72rem;
  letter-spacing: 0.08em;
  color: var(--ink-dim);
  text-align: center;
}

.timeline {
  position: relative;
  margin-top: 90px;
  padding-left: 28px;
}
.timeline-line {
  position: absolute;
  left: 6px;
  top: 6px;
  bottom: 6px;
  width: 1px;
  background: var(--line);
}
.milestone { position: relative; padding: 0 0 36px; }
.milestone::before {
  content: "";
  position: absolute;
  left: -27px;
  top: 8px;
  width: 13px;
  height: 13px;
  border-radius: 50%;
  border: 2px solid var(--accent);
  background: var(--bg);
}
.year { font-family: var(--mono); font-size: 0.8rem; letter-spacing: 0.2em; color: var(--accent); }
.milestone-title { margin-top: 8px; font-size: 1.4rem; }
.milestone-desc { margin-top: 8px; color: var(--ink-dim); font-size: 0.95rem; max-width: 620px; }

.stats {
  margin-top: 70px;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}
.stat {
  border: 1px solid var(--line);
  border-radius: 16px;
  padding: 34px 24px;
  text-align: center;
  background: var(--bg-soft);
}
.stat-num {
  font-family: var(--mono);
  font-size: 2.6rem;
  font-weight: 700;
  color: var(--accent);
  font-variant-numeric: tabular-nums;
}
.stat-label { margin-top: 10px; color: var(--ink-dim); font-size: 0.9rem; }

.comp-block { margin-top: 90px; }
.comp-title { font-size: clamp(1.6rem, 3vw, 2.4rem); }
.comp-desc { margin-top: 12px; color: var(--ink-dim); }
.comp-list {
  margin-top: 30px;
  list-style: none;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}
.comp-list li {
  font-size: 0.88rem;
  color: var(--ink-dim);
  border: 1px solid var(--line);
  border-radius: 10px;
  padding: 12px 14px;
  transition: border-color 0.3s, color 0.3s;
}
.comp-list li:hover { border-color: rgba(45, 226, 166, 0.45); color: var(--ink); }

@media (max-width: 1000px) {
  .album-grid { grid-template-columns: repeat(2, 1fr); }
  .comp-list { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 620px) {
  .album-grid { grid-template-columns: 1fr; }
  .comp-list { grid-template-columns: 1fr; }
  .stats { grid-template-columns: 1fr; }
}
</style>
