<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { gsap } from 'gsap'
import { prefersReducedMotion } from '../utils/motion'

const dot = ref<HTMLElement | null>(null)
const ring = ref<HTMLElement | null>(null)
let dotX: gsap.QuickToFunc | undefined
let dotY: gsap.QuickToFunc | undefined
let ringX: gsap.QuickToFunc | undefined
let ringY: gsap.QuickToFunc | undefined
let cleanup: (() => void) | undefined

onMounted(() => {
  const d = dot.value
  const r = ring.value
  if (!d || !r) return
  if (prefersReducedMotion() || !window.matchMedia('(pointer: fine)').matches) return

  document.documentElement.classList.add('mc-active')

  dotX = gsap.quickTo(d, 'x', { duration: 0.08, ease: 'power2.out' })
  dotY = gsap.quickTo(d, 'y', { duration: 0.08, ease: 'power2.out' })
  ringX = gsap.quickTo(r, 'x', { duration: 0.38, ease: 'power3.out' })
  ringY = gsap.quickTo(r, 'y', { duration: 0.38, ease: 'power3.out' })

  const onMove = (e: PointerEvent) => {
    dotX?.(e.clientX)
    dotY?.(e.clientY)
    ringX?.(e.clientX)
    ringY?.(e.clientY)
  }
  const onOver = (e: PointerEvent) => {
    const t = (e.target as HTMLElement).closest('a, button, [data-cursor], input, select, textarea, [role="button"]')
    gsap.to(r, { scale: t ? 1.7 : 1, duration: 0.3, ease: 'power3.out' })
    gsap.to(d, { scale: t ? 0.5 : 1, duration: 0.3, ease: 'power3.out' })
  }
  const onDown = () => gsap.to(r, { scale: 0.85, duration: 0.2 })
  const onUp = () => gsap.to(r, { scale: 1, duration: 0.3, ease: 'power3.out' })
  const onLeaveWin = () => {
    gsap.to(d, { opacity: 0, duration: 0.2 })
    gsap.to(r, { opacity: 0, duration: 0.2 })
  }
  const onEnterWin = () => {
    gsap.to(d, { opacity: 1, duration: 0.2 })
    gsap.to(r, { opacity: 1, duration: 0.2 })
  }

  window.addEventListener('pointermove', onMove, { passive: true })
  document.addEventListener('pointerover', onOver, { passive: true })
  window.addEventListener('pointerdown', onDown, { passive: true })
  window.addEventListener('pointerup', onUp, { passive: true })
  document.documentElement.addEventListener('mouseleave', onLeaveWin)
  document.documentElement.addEventListener('mouseenter', onEnterWin)

  cleanup = () => {
    window.removeEventListener('pointermove', onMove)
    document.removeEventListener('pointerover', onOver)
    window.removeEventListener('pointerdown', onDown)
    window.removeEventListener('pointerup', onUp)
    document.documentElement.removeEventListener('mouseleave', onLeaveWin)
    document.documentElement.removeEventListener('mouseenter', onEnterWin)
    document.documentElement.classList.remove('mc-active')
  }
})

onBeforeUnmount(() => cleanup?.())
</script>

<template>
  <div class="mc" aria-hidden="true">
    <span ref="dot" class="mc-dot"></span>
    <span ref="ring" class="mc-ring"></span>
  </div>
</template>

<style scoped>
.mc {
  position: fixed;
  left: 0;
  top: 0;
  z-index: 9999;
  pointer-events: none;
  display: none;
}
.mc-dot,
.mc-ring {
  position: fixed;
  left: 0;
  top: 0;
  border-radius: 50%;
  pointer-events: none;
  will-change: transform;
}
.mc-dot {
  width: 6px;
  height: 6px;
  margin: -3px 0 0 -3px;
  background: var(--accent);
  mix-blend-mode: difference;
}
.mc-ring {
  width: 36px;
  height: 36px;
  margin: -18px 0 0 -18px;
  border: 1px solid var(--ink);
  opacity: 0.7;
  mix-blend-mode: difference;
}
</style>
