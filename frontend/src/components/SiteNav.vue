<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { gsap } from 'gsap'

const nav = ref<HTMLElement | null>(null)
const scrolled = ref(false)

const links = [
  { href: '#event', label: '赛事介绍' },
  { href: '#news', label: '战队资讯' },
  { href: '#history', label: '历史荣誉' },
  { href: '#groups', label: '组别技术' },
  { href: '#recruit', label: '投递简历' },
  { href: '#cooperate', label: '商业合作' },
]

let onScroll: (() => void) | undefined

onMounted(() => {
  gsap.from(nav.value, { y: -24, opacity: 0, duration: 0.8, ease: 'power3.out', delay: 0.2 })
  onScroll = () => (scrolled.value = window.scrollY > 24)
  window.addEventListener('scroll', onScroll, { passive: true })
  onScroll()
})

onBeforeUnmount(() => {
  if (onScroll) window.removeEventListener('scroll', onScroll)
})
</script>

<template>
  <header ref="nav" class="nav" :class="{ scrolled }">
    <div class="container nav-inner">
      <a href="#top" class="brand">
        <span class="brand-mark">P</span>
        <span class="brand-name">WHUT<span class="dot">·</span>PRIME</span>
      </a>
      <nav class="nav-links">
        <a v-for="l in links" :key="l.href" :href="l.href" class="nav-link">{{ l.label }}</a>
      </nav>
      <a href="#recruit" class="btn btn-primary nav-cta">加入战队</a>
    </div>
  </header>
</template>

<style scoped>
.nav {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 60;
  height: var(--nav-h);
  border-bottom: 1px solid transparent;
  transition: background 0.4s, border-color 0.4s, backdrop-filter 0.4s;
}
.nav.scrolled {
  background: rgba(6, 8, 12, 0.72);
  backdrop-filter: blur(14px);
  border-bottom-color: var(--line);
}
.nav-inner { height: 100%; display: flex; align-items: center; gap: 32px; }
.brand { display: flex; align-items: center; gap: 10px; }
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
.brand-name { font-family: var(--mono); font-weight: 600; letter-spacing: 0.14em; font-size: 0.86rem; }
.brand-name .dot { color: var(--accent); margin: 0 2px; }
.nav-links { display: flex; gap: 24px; margin-inline: auto; }
.nav-link { position: relative; font-size: 0.9rem; color: var(--ink-dim); transition: color 0.3s; }
.nav-link::after {
  content: "";
  position: absolute;
  left: 0;
  bottom: -6px;
  width: 100%;
  height: 1px;
  background: var(--accent);
  transform: scaleX(0);
  transform-origin: left;
  transition: transform 0.35s var(--ease);
}
.nav-link:hover { color: var(--ink); }
.nav-link:hover::after { transform: scaleX(1); }
@media (max-width: 980px) {
  .nav-links { gap: 16px; }
  .nav-cta { display: none; }
  .nav-link { font-size: 0.82rem; }
}
@media (max-width: 720px) {
  .nav-links { display: none; }
}
</style>
