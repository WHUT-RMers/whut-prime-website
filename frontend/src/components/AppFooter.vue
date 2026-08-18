<script setup lang="ts">
import { ref } from 'vue'
import { useScrollReveal } from '../composables/useGsapReveal'

const root = ref<HTMLElement | null>(null)
useScrollReveal(root)

const navLinks = [
  { href: '#event', label: '赛事介绍' },
  { href: '#history', label: '历史荣誉' },
  { href: '#groups', label: '组别技术' },
  { href: '#recruit', label: '投递简历' },
]
</script>

<template>
  <footer ref="root" class="footer">
    <div class="container footer-inner">
      <div class="footer-brand" data-reveal>
        <span class="brand-mark">P</span>
        <span class="brand-name">WHUT·PRIME — ROBOMASTER</span>
      </div>
      <nav class="footer-nav" data-reveal>
        <a v-for="l in navLinks" :key="l.href" :href="l.href">{{ l.label }}</a>
      </nav>
      <p class="footer-line" data-reveal>
        武汉理工大学 RoboMaster 战队官网 demo 版 · Vue 3 + GSAP + Django
      </p>
      <p class="footer-copy" data-reveal>© 2026 WHUT PRIME · 机甲与你，来日方长</p>
    </div>
  </footer>
</template>

<style scoped>
.footer {
  border-top: 1px solid var(--line);
  padding: 54px 0 64px;
  background: var(--bg-soft);
}
.footer-inner { display: flex; flex-direction: column; gap: 18px; }
.footer-brand { display: flex; align-items: center; gap: 12px; }
.brand-mark {
  width: 30px;
  height: 30px;
  display: grid;
  place-items: center;
  background: var(--accent);
  color: var(--accent-ink);
  border-radius: 8px;
  font-family: var(--serif);
  font-weight: 700;
  font-size: 1.05rem;
}
.brand-name { font-family: var(--mono); letter-spacing: 0.14em; font-size: 0.86rem; }
.footer-nav { display: flex; gap: 24px; }
.footer-nav a { font-size: 0.86rem; color: var(--ink-dim); transition: color 0.3s; }
.footer-nav a:hover { color: var(--accent); }
.footer-line { color: var(--ink-dim); font-size: 0.95rem; max-width: 560px; }
.footer-copy { font-family: var(--mono); font-size: 0.72rem; letter-spacing: 0.1em; color: var(--ink-dim); opacity: 0.7; }
</style>
