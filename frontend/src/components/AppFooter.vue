<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { gsap } from 'gsap'
import { useScrollReveal } from '../composables/useGsapReveal'

const root = ref<HTMLElement | null>(null)
useScrollReveal(root, { blur: 8 })

const navLinks = [
  { to: '/event', label: '赛事介绍' },
  { to: '/history', label: '历史荣誉' },
  { to: '/groups', label: '组别技术' },
  { to: '/recruit', label: '投递简历' },
]

onMounted(() => {
  const mm = gsap.matchMedia()
  mm.add('(prefers-reduced-motion: no-preference)', () => {
    gsap.fromTo(
      '.footer-mark',
      { yPercent: 30, opacity: 0 },
      { yPercent: 0, opacity: 1, ease: 'none', scrollTrigger: { trigger: '.footer', start: 'top bottom', end: 'bottom bottom', scrub: 0.8 } },
    )
  })
})
</script>

<template>
  <footer ref="root" class="footer">
    <span class="footer-mark" aria-hidden="true">PRIME</span>
    <div class="container footer-inner">
      <div class="footer-brand" data-reveal>
        <span class="brand-mark">P</span>
        <span class="brand-name">WHUT·PRIME — ROBOMASTER</span>
      </div>
      <nav class="footer-nav" data-reveal>
        <RouterLink v-for="l in navLinks" :key="l.to" :to="l.to">{{ l.label }}</RouterLink>
      </nav>
      <p class="footer-line" data-reveal>
        武汉理工大学机甲大师 PRIME 战队官网 · 2027 赛季
      </p>
      <p class="footer-copy" data-reveal>© 2027 WHUT PRIME · 精研 覃思 笃志 力行</p>
    </div>
  </footer>
</template>

<style scoped>
.footer {
  position: relative;
  border-top: 1px solid var(--line);
  padding: 54px 0 64px;
  background: linear-gradient(180deg, rgba(10, 13, 23, 0.55), var(--bg));
  overflow: hidden;
}
.footer-mark {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  bottom: -4%;
  font-family: var(--display);
  font-size: clamp(8rem, 26vw, 22rem);
  line-height: 1;
  color: transparent;
  -webkit-text-stroke: 1px rgba(238, 242, 249, 0.05);
  user-select: none;
  pointer-events: none;
  will-change: transform, opacity;
}
.footer-inner { position: relative; display: flex; flex-direction: column; gap: 18px; }
.footer-brand { display: flex; align-items: center; gap: 12px; }
.brand-mark {
  width: 30px;
  height: 30px;
  display: grid;
  place-items: center;
  background: linear-gradient(140deg, var(--accent), #7cf0c8);
  color: var(--accent-ink);
  border-radius: 9px;
  font-family: var(--serif);
  font-weight: 400;
  font-size: 1.05rem;
  box-shadow: 0 0 16px rgba(45, 226, 166, 0.4);
}
.brand-name { font-family: var(--mono); letter-spacing: 0.14em; font-size: 0.86rem; }
.footer-nav { display: flex; gap: 24px; }
.footer-nav a { font-size: 0.86rem; color: var(--ink-dim); transition: color 0.3s, letter-spacing 0.4s var(--ease-expo); }
.footer-nav a:hover { color: var(--accent); letter-spacing: 0.1em; }
.footer-line { color: var(--ink-dim); font-size: 0.95rem; max-width: 560px; }
.footer-copy { font-family: var(--mono); font-size: 0.72rem; letter-spacing: 0.1em; color: var(--ink-faint); }
</style>
