<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { gsap } from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
import { prefersReducedMotion } from '../utils/motion'

const track = ref<HTMLElement | null>(null)
const words = ['超级对抗赛 RMUC', '高校联盟赛 RMUL', '人工智能挑战赛 RMUA', '英雄机器人', '步兵机器人', '工程机器人', '哨兵机器人', '无人机', '雷达站', '机械组', '电控组', '视觉算法组']

let tween: gsap.core.Tween | undefined
let cleanup: (() => void) | undefined

onMounted(() => {
  const el = track.value
  if (!el || prefersReducedMotion()) return

  tween = gsap.to(el, { xPercent: -50, ease: 'none', duration: 32, repeat: -1 })

  const setSpeed = (v: number) => {
    if (tween) gsap.to(tween, { timeScale: v, duration: 0.7, ease: 'power2.out', overwrite: 'auto' })
  }

  /* 滚动速度 → 跑马灯速率：向下滚动加速、向上滚动减速/轻微倒放 */
  const st = ScrollTrigger.create({
    start: 0,
    end: 'max',
    onUpdate: (self) => {
      const vel = gsap.utils.clamp(-3, 3, self.getVelocity() / 450)
      setSpeed(1 + vel * 1.5)
    },
  })

  const onEnter = () => setSpeed(0.12)
  const onLeave = () => setSpeed(1)
  el.addEventListener('mouseenter', onEnter)
  el.addEventListener('mouseleave', onLeave)

  cleanup = () => {
    st.kill()
    el.removeEventListener('mouseenter', onEnter)
    el.removeEventListener('mouseleave', onLeave)
  }
})

onBeforeUnmount(() => {
  cleanup?.()
  tween?.kill()
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
  position: relative;
  border-top: 1px solid var(--line);
  border-bottom: 1px solid var(--line);
  background: linear-gradient(180deg, var(--bg-soft), rgba(10, 13, 23, 0.4));
  overflow: hidden;
  padding: 22px 0;
  -webkit-mask-image: linear-gradient(90deg, transparent, #000 8%, #000 92%, transparent);
  mask-image: linear-gradient(90deg, transparent, #000 8%, #000 92%, transparent);
}
.marquee-track { display: flex; width: max-content; will-change: transform; }
.marquee-group { display: flex; align-items: center; flex-shrink: 0; }
.word {
  display: inline-flex;
  align-items: center;
  gap: 16px;
  padding: 0 30px;
  font-family: var(--serif);
  font-size: 1.4rem;
  letter-spacing: 0.12em;
  color: var(--ink-dim);
  white-space: nowrap;
  transition: color 0.3s;
}
.marquee:hover .word { color: var(--ink); }
.star {
  font-style: normal;
  color: var(--accent);
  font-size: 0.72rem;
  opacity: 0.85;
  text-shadow: 0 0 10px rgba(45, 226, 166, 0.8);
}
</style>
