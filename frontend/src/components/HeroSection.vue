<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { gsap } from 'gsap'
import { charsHtml } from '../utils/text'
import { prefersReducedMotion } from '../utils/motion'
import { useMouseFx } from '../composables/useMouseFx'

const root = ref<HTMLElement | null>(null)
const reduced = prefersReducedMotion()
let ctx: gsap.Context | undefined
let cleanup: (() => void) | undefined

useMouseFx(root)

onMounted(() => {
  const el = root.value
  if (!el) return

  if (!reduced) {
    ctx = gsap.context(() => {
      /* ---- 入场编排 ---- */
      const tl = gsap.timeline({ defaults: { ease: 'expo.out' } })
      tl.from('.hero-eyebrow', { y: 22, opacity: 0, duration: 0.9 }, 0.2)
        .from('.hero-title .char', { yPercent: 120, opacity: 0, duration: 1.15, stagger: 0.05 }, 0.35)
        .from('.hero-sub', { y: 26, opacity: 0, duration: 0.9 }, 0.8)
        .from('.hero-actions > *', { y: 16, opacity: 0, scale: 0.96, duration: 0.65, stagger: 0.12 }, 1.0)
        .from('.hero-notes li', { y: 14, opacity: 0, duration: 0.55, stagger: 0.1 }, 1.15)
        .from('.hero-hud > *', { opacity: 0, y: 12, duration: 0.55, stagger: 0.08 }, 0.85)
        .from('.scroll-cue', { opacity: 0, duration: 0.8 }, 1.5)

      /* ---- 战队数据计数 ---- */
      el.querySelectorAll<HTMLElement>('[data-count]').forEach((node) => {
        const target = Number(node.dataset.count)
        const obj = { v: 0 }
        gsap.to(obj, {
          v: target,
          duration: 1.9,
          ease: 'power3.out',
          delay: 1.35,
          onUpdate: () => {
            node.textContent = String(Math.round(obj.v))
          },
        })
      })

      /* ---- 扁平几何装饰：轮廓方块/菱形缓慢旋转 ---- */
      gsap.to('.shape-sq', {
        rotation: 360,
        duration: 46,
        repeat: -1,
        ease: 'none',
        transformOrigin: '50% 50%',
      })
      gsap.to('.shape-dia', {
        rotation: -360,
        duration: 60,
        repeat: -1,
        ease: 'none',
        transformOrigin: '50% 50%',
      })

      /* ---- 滚动视差（scrub） ---- */
      gsap
        .timeline({ scrollTrigger: { trigger: el, start: 'top top', end: 'bottom top', scrub: 0.6 } })
        .to('.hero-inner', { yPercent: -18, autoAlpha: 0.3, ease: 'none' }, 0)
        .to('.hero-watermark-wrap', { yPercent: 30, ease: 'none' }, 0)
        .to('.hero-bg', { yPercent: 8, ease: 'none' }, 0)
    }, el)

    /* ---- 指针视差（背景层轻微反向位移） ---- */
    if (window.matchMedia('(pointer: fine)').matches) {
      const bg = el.querySelector('.hero-bg')
      if (bg) {
        const xTo = gsap.quickTo(bg, 'x', { duration: 1.1, ease: 'power3.out' })
        const yTo = gsap.quickTo(bg, 'y', { duration: 1.1, ease: 'power3.out' })
        const onMove = (e: PointerEvent) => {
          const nx = e.clientX / window.innerWidth - 0.5
          const ny = e.clientY / window.innerHeight - 0.5
          xTo(nx * -22)
          yTo(ny * -16)
        }
        el.addEventListener('pointermove', onMove)
        cleanup = () => el.removeEventListener('pointermove', onMove)
      }
    }
  }
})

onBeforeUnmount(() => {
  cleanup?.()
  ctx?.revert()
})
</script>

<template>
  <section id="top" ref="root" class="hero">
    <div class="hero-bg" aria-hidden="true">
      <div class="hero-grid"></div>
      <span class="shape shape-sq shape-a"></span>
      <span class="shape shape-dia shape-b"></span>
      <span class="shape shape-sq shape-c"></span>
      <span class="hero-watermark-wrap"><span class="hero-watermark">PRIME</span></span>
      <span class="hero-scan"></span>
    </div>

    <div class="container hero-inner" data-spot>
      <div class="hero-main">
        <p class="eyebrow hero-eyebrow">
          <span class="eyebrow-dot" aria-hidden="true"></span>
          WHUT PRIME · 精研 覃思 笃志 力行 · 2027 SEASON
        </p>

        <h1 class="hero-title">
          <span class="line"><span v-html="charsHtml('以代码铸甲')"></span></span>
          <span class="line line-accent"><span v-html="charsHtml('以热血参战。')"></span></span>
        </h1>

        <p class="hero-sub">
          武汉理工大学机甲大师 PRIME 战队，2022 年成立，隶属人工智能学院。
          机械、电控、视觉算法、商业运营四大组别，百余名队员，
          连续四年征战机甲大师高校联盟赛。
        </p>

        <div class="hero-actions">
          <a href="#recruit" class="btn btn-primary" data-magnet>投递简历 <span aria-hidden="true">→</span></a>
          <a href="#event" class="btn btn-ghost" data-magnet>了解赛事</a>
        </div>

        <ul class="hero-notes">
          <li><span class="k"><span data-count="4">4</span></span> 大组别</li>
          <li><span class="k"><span data-count="100">0</span>+</span> 名队员</li>
          <li><span class="k"><span data-count="9">0</span></span> 项全国二等奖</li>
        </ul>
      </div>

      <div class="hero-hud" aria-hidden="true">
        <span class="hud-label">UNIT-01</span>
        <span class="hud-line"></span>
        <span class="hud-value">PRIME</span>
        <span class="hud-status"><i class="hud-dot"></i>SYSTEM ONLINE</span>
      </div>
    </div>

    <div class="scroll-cue" aria-hidden="true">
      <span class="cue-line"></span>SCROLL <i class="cue-tri">▾</i>
    </div>
  </section>
</template>

<style scoped>
.hero {
  min-height: 100svh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding-top: var(--nav-h);
  overflow: hidden;
}

/* ---- 背景层（扁平几何） ---- */
.hero-bg { position: absolute; inset: 0; z-index: 0; overflow: hidden; }
.hero-grid {
  position: absolute;
  left: -12%;
  right: -12%;
  bottom: -14%;
  height: 42%;
  background-image:
    linear-gradient(var(--line) 1px, transparent 1px),
    linear-gradient(90deg, var(--line) 1px, transparent 1px);
  background-size: 54px 54px;
  transform: perspective(720px) rotateX(60deg);
  transform-origin: top;
  opacity: 0.5;
  -webkit-mask-image: radial-gradient(70% 90% at 50% 0%, #000 0%, transparent 78%);
  mask-image: radial-gradient(70% 90% at 50% 0%, #000 0%, transparent 78%);
}
.shape {
  position: absolute;
  border: 1px solid rgba(45, 226, 166, 0.32);
  pointer-events: none;
  will-change: transform;
}
.shape-a { width: 120px; height: 120px; top: 12%; right: 7%; }
.shape-b { width: 84px; height: 84px; top: 42%; right: 30%; border-radius: 8px; transform: rotate(45deg); border-color: rgba(77, 163, 255, 0.32); }
.shape-c { width: 56px; height: 56px; bottom: 24%; left: 32%; border-color: rgba(77, 163, 255, 0.24); }

.hero-watermark-wrap {
  position: absolute;
  right: 0;
  top: 5%;
  pointer-events: none;
  user-select: none;
  z-index: 0;
  will-change: transform;
}
.hero-watermark {
  display: block;
  font-family: var(--display);
  font-size: clamp(8rem, 21vw, 18rem);
  line-height: 1;
  letter-spacing: 0.04em;
  color: transparent;
  background: linear-gradient(180deg, rgba(45, 226, 166, 0.32), rgba(77, 163, 255, 0.16) 70%);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-stroke: 1px rgba(45, 226, 166, 0.35);
  animation: float-mark 9s ease-in-out infinite;
}

.hero-scan {
  position: absolute;
  left: -10%;
  right: -10%;
  top: 0;
  height: 90px;
  background: linear-gradient(180deg, transparent, rgba(45, 226, 166, 0.05), transparent);
  border-top: 1px solid rgba(45, 226, 166, 0.08);
  animation: scan-move 8s linear infinite;
  pointer-events: none;
}

/* ---- 内容层 ---- */
.hero-inner {
  position: relative;
  z-index: 2;
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 40px;
}
.eyebrow-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--accent);
  animation: pulse-dot 2s ease-in-out infinite;
}
.hero-eyebrow { margin-bottom: 30px; }

.hero-title {
  font-size: clamp(2.6rem, 9vw, 6rem);
  line-height: 1.1;
  letter-spacing: 0.03em;
}
.line { display: block; overflow: hidden; padding-bottom: 0.08em; margin-bottom: -0.08em; }
.line-accent { color: var(--accent); }

.hero-sub {
  margin-top: 30px;
  max-width: 520px;
  font-size: 1.05rem;
  color: var(--ink-dim);
  text-wrap: pretty;
}

.hero-actions { display: flex; gap: 16px; margin-top: 42px; flex-wrap: wrap; }

.hero-notes {
  list-style: none;
  display: flex;
  gap: 40px;
  margin-top: 64px;
  color: var(--ink-dim);
  font-size: 0.95rem;
}
.hero-notes li { display: flex; align-items: baseline; gap: 8px; }
.hero-notes .k {
  font-family: var(--mono);
  font-size: 1.7rem;
  font-weight: 700;
  color: var(--ink);
  font-variant-numeric: tabular-nums;
}

/* ---- 右侧 HUD ---- */
.hero-hud {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 14px;
  padding-bottom: 12px;
  font-family: var(--mono);
}
.hud-label { font-size: 0.66rem; letter-spacing: 0.34em; color: var(--ink-faint); writing-mode: vertical-lr; }
.hud-line { width: 1px; height: 90px; background: linear-gradient(to bottom, var(--accent), transparent); }
.hud-value { font-size: 1.5rem; font-weight: 700; letter-spacing: 0.16em; color: var(--accent); writing-mode: vertical-lr; }
.hud-status { display: flex; align-items: center; gap: 7px; font-size: 0.56rem; letter-spacing: 0.24em; color: var(--ink-faint); }
.hud-dot { width: 5px; height: 5px; border-radius: 50%; background: var(--accent); animation: pulse-dot 1.8s ease-in-out infinite; }

/* ---- 浮动水印 ---- */
@keyframes float-mark {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-16px); }
}

/* ---- 滚动提示 ---- */
.scroll-cue {
  position: absolute;
  bottom: 26px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  font-family: var(--mono);
  font-size: 0.62rem;
  letter-spacing: 0.3em;
  color: var(--ink-faint);
}
.cue-line { width: 1px; height: 44px; background: linear-gradient(to bottom, var(--accent), transparent); animation: cue 1.8s var(--ease-expo) infinite; }
.cue-tri { font-style: normal; color: var(--accent); animation: pulse-dot 1.8s ease-in-out infinite; }

@media (max-width: 640px) {
  .hero-notes { gap: 22px; flex-direction: column; margin-top: 44px; }
  .hero-inner { flex-direction: column; align-items: flex-start; }
  .hero-hud { display: none; }
  .hero-watermark { opacity: 0.35; }
  .shape-a, .shape-b { display: none; }
}
</style>