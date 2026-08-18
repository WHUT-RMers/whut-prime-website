<script setup lang="ts">
import { ref } from 'vue'
import { useScrollReveal } from '../composables/useGsapReveal'
import PlaceholderImage from './PlaceholderImage.vue'

const root = ref<HTMLElement | null>(null)
useScrollReveal(root)

const points = [
  { t: '对抗', d: '7v7 多兵种机器人在 400㎡ 赛场同场竞技，工程与战术正面交锋。' },
  { t: '工程', d: '从结构设计到算法决策，一辆机器人的背后是一整条技术链。' },
  { t: '协作', d: '英雄、步兵、哨兵、工程、无人机与雷达分工协同，胜负在系统层面决定。' },
]
</script>

<template>
  <section id="event" ref="root" class="event">
    <div class="container">
      <div class="event-head">
        <p class="eyebrow" data-reveal>01 / 赛事介绍</p>
        <h2 class="event-title" data-reveal>机甲大师赛，是什么？</h2>
        <p class="event-lead" data-reveal>
          RoboMaster 机甲大师赛由大疆发起，面向全球高校的机器人竞技赛事。对抗、工程与协作，
          在一场比赛里同时发生。
        </p>
      </div>

      <div class="event-grid">
        <div class="event-media" data-reveal>
          <PlaceholderImage label="赛事现场 / 赛场照片" ratio="16 / 10" accent />
        </div>
        <div class="event-points">
          <article v-for="(p, i) in points" :key="p.t" class="point" data-reveal>
            <span class="point-no">{{ String(i + 1).padStart(2, '0') }}</span>
            <div>
              <h3 class="point-title">{{ p.t }}</h3>
              <p class="point-desc">{{ p.d }}</p>
            </div>
          </article>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.event { padding: 130px 0 150px; }
.event-head { max-width: 720px; }
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
  align-items: center;
}

.point { display: flex; gap: 20px; padding: 22px 0; border-bottom: 1px solid var(--line); }
.point:last-child { border-bottom: none; }
.point-no {
  font-family: var(--mono);
  font-size: 0.85rem;
  color: var(--accent);
  letter-spacing: 0.1em;
  padding-top: 6px;
}
.point-title { font-size: 1.25rem; }
.point-desc { margin-top: 8px; color: var(--ink-dim); font-size: 0.95rem; }

@media (max-width: 880px) {
  .event-grid { grid-template-columns: 1fr; gap: 36px; }
  .event { padding: 90px 0 110px; }
}
</style>
