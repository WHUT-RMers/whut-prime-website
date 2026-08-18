<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { gsap } from 'gsap'

const track = ref<HTMLElement | null>(null)
const words = ['超级对抗赛 RMUC', '高校联盟赛 RMUL', '人工智能挑战赛 RMUA', '英雄机器人', '步兵机器人', '工程机器人', '哨兵机器人', '无人机', '雷达站', '机械组', '电控组', '视觉算法组']

onMounted(() => {
  if (!track.value) return
  gsap.to(track.value, { xPercent: -50, repeat: -1, duration: 26, ease: 'none' })
})
</script>

<template>
  <section class="marquee" aria-hidden="true">
    <div class="marquee-track" ref="track">
      <div v-for="n in 2" :key="n" class="marquee-group">
        <span v-for="w in words" :key="w + n" class="word">{{ w }}<i class="star">◆</i></span>
      </div>
    </div>
  </section>
</template>

<style scoped>
.marquee {
  border-top: 1px solid var(--line);
  border-bottom: 1px solid var(--line);
  background: var(--bg-soft);
  overflow: hidden;
  padding: 20px 0;
}
.marquee-track { display: flex; width: max-content; }
.marquee-group { display: flex; align-items: center; flex-shrink: 0; }
.word {
  display: inline-flex;
  align-items: center;
  gap: 14px;
  padding: 0 28px;
  font-family: var(--serif);
  font-size: 1.35rem;
  letter-spacing: 0.12em;
  color: var(--ink-dim);
  white-space: nowrap;
}
.star { font-style: normal; color: var(--accent); font-size: 0.8rem; opacity: 0.8; }
</style>
