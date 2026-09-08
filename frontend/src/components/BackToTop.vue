<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { gsap } from 'gsap'
import { ScrollToPlugin } from 'gsap/ScrollToPlugin'
import { prefersReducedMotion } from '../utils/motion'

const btn = ref<HTMLElement | null>(null)
const ring = ref<SVGCircleElement | null>(null)

const R = 21
const CIRC = 2 * Math.PI * R
/** 滚动超过该阈值（首屏之下）才出现 */
const THRESHOLD = 480

let ctx: gsap.Context | undefined
let visible = false
let rafPending = false
const docStyle = document.documentElement.style

/** 关闭 CSS 平滑滚动：避免与 GSAP 逐帧赋值 scrollTop 打架（html 有 scroll-behavior: smooth） */
function setInstantScroll(on: boolean) {
  docStyle.scrollBehavior = on ? 'auto' : ''
}

function update() {
  rafPending = false
  const y = window.scrollY
  const max = document.documentElement.scrollHeight - window.innerHeight
  const p = max > 0 ? Math.min(1, y / max) : 0
  if (ring.value) ring.value.style.strokeDashoffset = String(CIRC * (1 - p))
  if (!btn.value) return

  const show = y > THRESHOLD
  if (show === visible) return
  visible = show

  // 减弱动态：直接显隐，不做位移动画
  if (prefersReducedMotion()) {
    gsap.set(btn.value, { autoAlpha: show ? 1 : 0, y: 0 })
    return
  }
  gsap.to(btn.value, {
    autoAlpha: show ? 1 : 0,
    y: show ? 0 : 16,
    duration: 0.45,
    ease: 'expo.out',
    overwrite: 'auto',
  })
}

const onScroll = () => {
  if (rafPending) return
  rafPending = true
  requestAnimationFrame(update)
}

function goTop() {
  if (prefersReducedMotion()) {
    setInstantScroll(true)
    window.scrollTo({ top: 0, behavior: 'instant' })
    setInstantScroll(false)
    return
  }
  setInstantScroll(true)
  gsap.to(window, {
    scrollTo: 0,
    duration: 0.9,
    ease: 'expo.out',
    overwrite: 'auto',
    onComplete: () => setInstantScroll(false),
  })
}

onMounted(() => {
  ctx = gsap.context(() => {
    if (btn.value) gsap.set(btn.value, { autoAlpha: 0, y: 16 })
  })
  window.addEventListener('scroll', onScroll, { passive: true })
  update()
})

onBeforeUnmount(() => {
  window.removeEventListener('scroll', onScroll)
  setInstantScroll(false)
  ctx?.revert()
})
</script>

<template>
  <button
    ref="btn"
    class="to-top"
    type="button"
    aria-label="返回顶部"
    title="返回顶部"
    @click="goTop"
  >
    <svg class="to-top-ring" viewBox="0 0 48 48" aria-hidden="true">
      <circle class="ring-track" cx="24" cy="24" :r="R" />
      <circle ref="ring" class="ring-fill" cx="24" cy="24" :r="R" :stroke-dasharray="CIRC" />
    </svg>
    <span class="to-top-inner">
      <svg class="to-top-arrow" viewBox="0 0 24 24" aria-hidden="true">
        <path d="M12 19V5m0 0-6 6m6-6 6 6" />
      </svg>
    </span>
  </button>
</template>

<style scoped>
.to-top {
  position: fixed;
  right: 28px;
  bottom: 28px;
  z-index: 90; /* 内容之上、自定义光标（9999）之下 */
  width: 48px;
  height: 48px;
  border-radius: 50%;
  border: 1px solid var(--line-strong);
  background: var(--surface);
  color: var(--accent);
  cursor: pointer;
  transition: border-color 0.25s, background 0.25s;
}
.to-top:hover { border-color: var(--accent); background: var(--surface-2); }

/* 按下缩放放在内层，避免与 GSAP 的外层 y 位移（transform）抢过渡 */
.to-top-inner {
  position: absolute;
  inset: 0;
  display: grid;
  place-items: center;
  border-radius: 50%;
  transition: transform 0.4s var(--ease-expo);
}
.to-top:active .to-top-inner { transform: scale(0.96); }

.to-top-arrow {
  width: 20px;
  height: 20px;
  fill: none;
  stroke: currentColor;
  stroke-width: 2;
  stroke-linecap: round;
  stroke-linejoin: round;
  transition: transform 0.35s var(--ease-expo);
}
.to-top:hover .to-top-arrow { transform: translateY(-2px); }

/* 滚动进度环（随页面滚动进度填充，逆时针从顶部起画） */
.to-top-ring {
  position: absolute;
  inset: -1px;
  width: 48px;
  height: 48px;
  transform: rotate(-90deg);
  pointer-events: none;
}
.ring-track { fill: none; stroke: var(--line); stroke-width: 2; }
.ring-fill {
  fill: none;
  stroke: var(--accent);
  stroke-width: 2;
  stroke-linecap: round;
}

@media (max-width: 520px) {
  .to-top { right: 18px; bottom: 18px; }
}
</style>