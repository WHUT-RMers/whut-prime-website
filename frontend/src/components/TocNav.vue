<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { gsap } from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
import { prefersReducedMotion } from '../utils/motion'

const root = ref<HTMLElement | null>(null)
const railFill = ref<HTMLElement | null>(null)

const items = [
  { id: 'event', no: '01', label: '赛事' },
  { id: 'news', no: '02', label: '资讯' },
  { id: 'history', no: '03', label: '历史' },
  { id: 'groups', no: '04', label: '组别' },
  { id: 'recruit', no: '05', label: '投递' },
  { id: 'cooperate', no: '06', label: '合作' },
]

const activeId = ref('')
const reduced = prefersReducedMotion()

let cleanup: (() => void) | undefined
/** 目录当前是否已出现（首屏之下才显示） */
let shown = false
let rafPending = false

/**
 * 出现时机：首屏（HeroSection 全屏大图）基本滚出视口后才滑入，滚回首屏则收回。
 * 高度取首屏元素的实际值（兼容 max(100svh, 640px) 等矮屏兜底），取不到时退回视口高度；
 * 留一屏 10% 的提前量，尾部这点余量已看不到首屏主体，也让 #event 锚点直达时目录不会反被收起。
 */
const GATE_LEAD = 0.1

function gateY() {
  const hero = document.querySelector<HTMLElement>('.hero-carousel')
  const first = hero ? hero.offsetHeight : window.innerHeight
  return first - window.innerHeight * GATE_LEAD
}

function setShown(on: boolean) {
  const el = root.value
  if (!el) return
  // 减弱动态：直接显隐，不做位移动画
  if (reduced) {
    gsap.set(el, { autoAlpha: on ? 1 : 0 })
    return
  }
  gsap.to(el, {
    autoAlpha: on ? 1 : 0,
    x: on ? 0 : -18,
    duration: on ? 0.5 : 0.28,
    ease: on ? 'expo.out' : 'power2.in',
    overwrite: 'auto',
  })
}

function update() {
  rafPending = false
  const next = window.scrollY > gateY()
  if (next === shown) return
  shown = next
  setShown(shown)
}

/** 滚动 / 尺寸变化统一走 rAF 节流（显隐阈值依赖首屏高度，窗口变化后需重算） */
function schedule() {
  if (rafPending) return
  rafPending = true
  requestAnimationFrame(update)
}

onMounted(() => {
  const el = root.value
  shown = window.scrollY > gateY()
  // 首帧直接落到目标状态，避免刷新在页面中部时出现一次多余的入场动画
  if (el) gsap.set(el, shown ? { autoAlpha: 1, x: 0 } : { autoAlpha: 0, x: reduced ? 0 : -18 })

  const triggers = items
    .map((it) => {
      const node = document.getElementById(it.id)
      if (!node) return null
      return ScrollTrigger.create({
        trigger: node,
        start: 'top 45%',
        end: 'bottom 45%',
        onToggle: (self) => {
          if (self.isActive) activeId.value = it.id
        },
      })
    })
    .filter((t): t is ScrollTrigger => t !== null)

  /* 章节进度光柱 */
  const st = ScrollTrigger.create({
    start: 0,
    end: 'max',
    onUpdate: (self) => {
      if (railFill.value) gsap.set(railFill.value, { scaleY: self.progress })
    },
  })

  window.addEventListener('scroll', schedule, { passive: true })
  window.addEventListener('resize', schedule)

  cleanup = () => {
    window.removeEventListener('scroll', schedule)
    window.removeEventListener('resize', schedule)
    triggers.forEach((t) => t.kill())
    st.kill()
    if (root.value) gsap.killTweensOf(root.value)
  }
})

onBeforeUnmount(() => cleanup?.())
</script>

<template>
  <nav ref="root" class="toc" aria-label="页面目录">
    <div class="toc-rail" aria-hidden="true"><span ref="railFill"></span></div>
    <a
      v-for="it in items"
      :key="it.id"
      :href="'#' + it.id"
      class="toc-item"
      :class="{ active: activeId === it.id }"
    >
      <span class="toc-no">{{ it.no }}</span>
      <span class="toc-label">{{ it.label }}</span>
    </a>
  </nav>
</template>

<style scoped>
.toc {
  position: fixed;
  left: 18px;
  top: 0;
  bottom: 0;
  /* 垂直居中交给 margin: auto：不与 GSAP 的 x 位移抢 transform */
  margin-block: auto;
  height: fit-content;
  z-index: 55;
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding-left: 10px;
}
.toc-rail {
  position: absolute;
  left: 0;
  top: 8px;
  bottom: 8px;
  width: 2px;
  border-radius: 2px;
  background: var(--line);
  overflow: hidden;
}
.toc-rail span {
  display: block;
  height: 100%;
  transform: scaleY(0);
  transform-origin: top;
  background: var(--accent);
}
.toc-item {
  position: relative;
  display: flex;
  align-items: center;
  gap: 11px;
  padding: 7px 12px 7px 16px;
  border-radius: 0 10px 10px 0;
  font-family: var(--mono);
  font-size: 0.68rem;
  letter-spacing: 0.18em;
  color: var(--ink-dim);
  text-decoration: none;
  transition: color 0.3s, background 0.3s;
}
.toc-no { opacity: 0.8; transition: opacity 0.3s; }
.toc-item::before {
  content: "";
  position: absolute;
  left: 0;
  top: 50%;
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: var(--ink-faint);
  transform: translate(-70%, -50%) scale(0.6);
  transition: background 0.3s, transform 0.4s var(--ease-expo), box-shadow 0.3s;
}
.toc-item:hover { color: var(--ink); background: rgba(255, 255, 255, 0.02); }
.toc-item.active {
  color: var(--accent);
  background: rgba(45, 226, 166, 0.07);
}
.toc-item.active .toc-no { opacity: 1; }
.toc-item.active::before {
  background: var(--accent);
  transform: translate(-70%, -50%) scale(1);
}

@media (max-width: 1150px) {
  .toc { display: none; }
}
</style>
