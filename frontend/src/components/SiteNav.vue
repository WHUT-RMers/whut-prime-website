<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { gsap } from 'gsap'
import { prefersReducedMotion } from '../utils/motion'

const nav = ref<HTMLElement | null>(null)
const prog = ref<HTMLElement | null>(null)
const drawer = ref<HTMLElement | null>(null)
const scrolled = ref(false)
const open = ref(false)
const reduced = prefersReducedMotion()

const links = [
  { to: '/', label: '主页', no: '01' },
  { to: '/news', label: '战队资讯', no: '02' },
  { to: '/history', label: '历史荣誉', no: '03' },
  { to: '/groups', label: '组别技术', no: '04' },
  { to: '/recruit', label: '投递简历', no: '05' },
  { to: '/cooperate', label: '商业合作', no: '06' },
]

let onScroll: (() => void) | undefined

onMounted(() => {
  if (nav.value && !reduced) {
    gsap.from(nav.value, { y: -26, opacity: 0, duration: 0.8, ease: 'expo.out', delay: 0.15 })
  }
  onScroll = () => {
    scrolled.value = window.scrollY > 28
    const max = document.documentElement.scrollHeight - window.innerHeight
    const p = max > 0 ? Math.min(1, window.scrollY / max) : 0
    if (prog.value) gsap.set(prog.value, { scaleX: p })
  }
  window.addEventListener('scroll', onScroll, { passive: true })
  onScroll()
})

onBeforeUnmount(() => {
  if (onScroll) window.removeEventListener('scroll', onScroll)
})

/** 移动端抽屉 */
watch(open, (v) => {
  const el = drawer.value
  if (!el) return
  if (v) {
    el.classList.add('is-open')
    el.setAttribute('aria-hidden', 'false')
    el.style.pointerEvents = 'auto'
    if (reduced) return
    gsap.fromTo(el, { clipPath: 'inset(0 0 100% 0)' }, { clipPath: 'inset(0 0 0% 0)', duration: 0.5, ease: 'expo.out' })
    gsap.fromTo(
      el.querySelectorAll('.drawer-link'),
      { y: 22, opacity: 0 },
      { y: 0, opacity: 1, duration: 0.45, stagger: 0.05, delay: 0.14, ease: 'power3.out' },
    )
  } else {
    el.setAttribute('aria-hidden', 'true')
    el.style.pointerEvents = 'none'
    gsap.to(el, {
      clipPath: 'inset(0 0 100% 0)',
      duration: 0.35,
      ease: 'expo.in',
      onComplete: () => el.classList.remove('is-open'),
    })
  }
})
</script>

<template>
  <header ref="nav" class="nav" :class="{ scrolled }">
    <div class="nav-progress" aria-hidden="true"><span ref="prog"></span></div>

    <div class="container nav-inner">
      <RouterLink to="/" class="brand">
        <span class="brand-mark">P</span>
        <span class="brand-name">WHUT<span class="dot">·</span>PRIME</span>
      </RouterLink>

      <nav class="nav-links" aria-label="主导航">
        <RouterLink v-for="l in links" :key="l.to" :to="l.to" class="nav-link">
          <span class="nav-idx">{{ l.no }}</span>{{ l.label }}
        </RouterLink>
      </nav>

      <div class="nav-right">
        <RouterLink to="/recruit" class="btn btn-primary nav-cta" data-magnet>
          加入战队 <i class="cta-dot" aria-hidden="true"></i>
        </RouterLink>
        <button
          class="nav-burger"
          :class="{ active: open }"
          :aria-expanded="open"
          aria-label="打开菜单"
          @click="open = !open"
        >
          <span></span><span></span><span></span>
        </button>
      </div>
    </div>

    <div ref="drawer" class="drawer" aria-hidden="true">
      <nav class="drawer-nav" aria-label="移动端导航">
        <RouterLink
          v-for="l in links"
          :key="l.to"
          :to="l.to"
          class="drawer-link"
          @click="open = false"
        >
          <span class="drawer-no">{{ l.no }}</span>
          <span class="drawer-label">{{ l.label }}</span>
          <i class="drawer-arrow" aria-hidden="true">→</i>
        </RouterLink>
      </nav>
      <RouterLink to="/recruit" class="btn btn-primary drawer-cta" @click="open = false">
        加入战队
      </RouterLink>
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
  background: var(--bg);
  border-bottom: 1px solid transparent;
  transition: background 0.35s var(--ease-expo), border-color 0.35s var(--ease-expo);
}
.nav.scrolled {
  background: rgba(8, 10, 17, 0.94);
  border-bottom-color: var(--line);
}

/* 阅读进度条：扁平实色 */
.nav-progress { position: absolute; left: 0; top: 0; right: 0; height: 2px; pointer-events: none; }
.nav-progress span {
  display: block;
  height: 100%;
  transform: scaleX(0);
  transform-origin: left;
  background: var(--accent);
}

.nav-inner { height: 100%; display: flex; align-items: center; gap: 32px; position: relative; }
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
  font-weight: 400;
  font-size: 1.05rem;
}
.brand-name { font-family: var(--mono); font-weight: 600; letter-spacing: 0.16em; font-size: 0.86rem; }
.brand-name .dot { color: var(--accent); margin: 0 2px; }

.nav-links { display: flex; gap: 26px; margin-inline: auto; }
.nav-link {
  position: relative;
  display: inline-flex;
  align-items: center;
  gap: 7px;
  padding: 6px 2px;
  font-size: 0.9rem;
  color: var(--ink-dim);
  transition: color 0.3s;
}
.nav-idx {
  font-family: var(--mono);
  font-size: 0.6rem;
  letter-spacing: 0.1em;
  color: var(--accent);
  opacity: 0.7;
  transition: opacity 0.3s;
}
.nav-link::after {
  content: "";
  position: absolute;
  left: 0;
  bottom: 0;
  width: 100%;
  height: 2px;
  background: var(--accent);
  transform: scaleX(0);
  transform-origin: left;
  transition: transform 0.35s var(--ease-expo);
}
.nav-link:hover { color: var(--ink); }
.nav-link:hover .nav-idx { opacity: 1; }
.nav-link:hover::after { transform: scaleX(1); }
.nav-link.router-link-active { color: var(--ink); }
.nav-link.router-link-active .nav-idx { opacity: 1; }
.nav-link.router-link-active::after { transform: scaleX(1); }

.nav-right { display: flex; align-items: center; gap: 14px; }
.cta-dot { width: 6px; height: 6px; border-radius: 50%; background: var(--accent-ink); animation: pulse-dot 1.6s ease-in-out infinite; }

.nav-burger {
  display: none;
  flex-direction: column;
  justify-content: center;
  gap: 5px;
  width: 42px;
  height: 42px;
  padding: 10px;
  border-radius: 8px;
  border: 1px solid var(--line-strong);
  background: transparent;
}
.nav-burger span { display: block; height: 2px; width: 100%; background: var(--ink); border-radius: 2px; transition: transform 0.35s var(--ease-expo), opacity 0.25s; }
.nav-burger.active span:nth-child(1) { transform: translateY(7px) rotate(45deg); }
.nav-burger.active span:nth-child(2) { opacity: 0; }
.nav-burger.active span:nth-child(3) { transform: translateY(-7px) rotate(-45deg); }

/* 移动端抽屉：扁平实色 */
.drawer {
  position: fixed;
  top: var(--nav-h);
  left: 0;
  right: 0;
  z-index: 55;
  display: flex;
  flex-direction: column;
  gap: 24px;
  padding: 18px 24px 34px;
  background: #0a0c13;
  border-bottom: 1px solid var(--line-strong);
  clip-path: inset(0 0 100% 0);
  pointer-events: none;
  visibility: hidden;
}
.drawer.is-open { visibility: visible; }
.drawer-nav { display: flex; flex-direction: column; }
.drawer-link {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 15px 4px;
  border-bottom: 1px solid var(--line);
  font-size: 1.02rem;
}
.drawer-no { font-family: var(--mono); font-size: 0.68rem; letter-spacing: 0.12em; color: var(--accent); }
.drawer-label { flex: 1; }
.drawer-arrow { font-style: normal; color: var(--ink-faint); transition: transform 0.3s var(--ease), color 0.25s; }
.drawer-link:hover .drawer-arrow { color: var(--accent); transform: translateX(5px); }
.drawer-cta { align-self: flex-start; }

@media (max-width: 980px) {
  .nav-links { gap: 18px; }
  .nav-cta { display: none; }
  .nav-link { font-size: 0.84rem; }
}
@media (max-width: 760px) {
  .nav-links { display: none; }
  .nav-burger { display: flex; }
}
</style>
