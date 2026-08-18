<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { gsap } from 'gsap'
import { charsHtml } from '../utils/text'
import { prefersReducedMotion } from '../utils/motion'

const root = ref<HTMLElement | null>(null)
const reduced = prefersReducedMotion()
let ctx: gsap.Context | undefined
let cleanup: (() => void) | undefined

onMounted(() => {
  const el = root.value
  if (!el) return

  if (!reduced) {
    ctx = gsap.context(() => {
      /* ---- 入场编排（motion-driven） ---- */
      const tl = gsap.timeline({ defaults: { ease: 'expo.out' } })
      tl.from('.hero-eyebrow', { y: 22, opacity: 0, duration: 0.9 }, 0.2)
        .from(
          '.hero-title .char',
          { yPercent: 120, opacity: 0, duration: 1.15, stagger: 0.05 },
          0.35,
        )
        .from('.hero-sub', { y: 26, opacity: 0, filter: 'blur(8px)', duration: 1 }, 0.8)
        .from('.hero-actions > *', { y: 18, opacity: 0, scale: 0.96, duration: 0.7, stagger: 0.12 }, 1.0)
        .from('.hero-notes li', { y: 16, opacity: 0, duration: 0.6, stagger: 0.1 }, 1.15)
        .from('.hero-hud > *', { opacity: 0, y: 14, duration: 0.6, stagger: 0.09 }, 0.85)
        .from('.scroll-cue', { opacity: 0, duration: 0.9 }, 1.5)

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

      /* ---- 环境光斑漂浮 ---- */
      gsap.to('.orb', {
        x: () => gsap.utils.random(-70, 70),
        y: () => gsap.utils.random(-50, 50),
        duration: () => gsap.utils.random(8, 13),
        repeat: -1,
        yoyo: true,
        ease: 'sine.inOut',
        stagger: { each: 0.6 },
      })

      /* ---- 滚动视差（scrub） ---- */
      gsap
        .timeline({ scrollTrigger: { trigger: el, start: 'top top', end: 'bottom top', scrub: 0.6 } })
        .to('.hero-inner', { yPercent: -20, autoAlpha: 0.25, ease: 'none' }, 0)
        .to('.hero-watermark', { yPercent: 30, ease: 'none' }, 0)
        .to('.hero-bg', { yPercent: 10, ease: 'none' }, 0)
        .to('.hero-grid', { opacity: 0.12, ease: 'none' }, 0)
    }, el)

    /* ---- 指针视差（仅精细指针设备） ---- */
    if (window.matchMedia('(pointer: fine)').matches) {
      const bg = el.querySelector('.hero-bg')
      if (bg) {
        const xTo = gsap.quickTo(bg, 'x', { duration: 1.2, ease: 'power3.out' })
        const yTo = gsap.quickTo(bg, 'y', { duration: 1.2, ease: 'power3.out' })
        const onMove = (e: PointerEvent) => {
          const nx = e.clientX / window.innerWidth - 0.5
          const ny = e.clientY / window.innerHeight - 0.5
          xTo(nx * -26)
          yTo(ny * -20)
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
      <div class="orb orb-1"></div>
      <div class="orb orb-2"></div>
      <div class="orb orb-3"></div>
      <span class="hero-watermark">PRIME</span>
      <span class="hero-scan"></span>
    </div>

    <div class="container hero-inner">
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
          <a href="#recruit" class="btn btn-primary">投递简历 <span aria-hidden="true">→</span></a>
          <a href="#event" class="btn btn-ghost">了解赛事</a>
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

/* ---- 背景层 ---- */
.hero-bg { position: absolute; inset: 0; z-index: 0; overflow: hidden; }
.hero-grid {
  position: absolute;
  left: -12%;
  right: -12%;
  bottom: -16%;
  height: 46%;
  background-image:
    linear-gradient(rgba(45, 226, 166, 0.13) 1px, transparent 1px),
    linear-gradient(90deg, rgba(45, 226, 166, 0.13) 1px, transparent 1px);
  background-size: 46px 46px;
  transform: perspective(640px) rotateX(62deg);
  transform-origin: top;
  opacity: 0.32;
  -webkit-mask-image: radial-gradient(70% 90% at 50% 0%, rgba(0, 0, 0, 0.9), transparent 75%);
  mask-image: radial-gradient(70% 90% at 50% 0%, rgba(0, 0, 0, 0.9), transparent 75%);
}
.orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(90px);
  opacity: 0.5;
  z-index: 1;
  pointer-events: none;
  will-change: transform;
}
.orb-1 { width: 460px; height: 460px; background: rgba(45, 226, 166, 0.15); top: 6%; right: -6%; animation: hue-drift 14s ease-in-out infinite; }
.orb-2 { width: 340px; height: 340px; background: rgba(77, 163, 255, 0.13); bottom: 2%; left: -4%; animation: hue-drift 18s ease-in-out infinite reverse; }
.orb-3 { width: 200px; height: 200px; background: rgba(255, 180, 94, 0.1); top: 58%; left: 54%; animation: hue-drift 16s ease-in-out infinite 3s; }

.hero-watermark {
  position: absolute;
  right: -2%;
  top: 8%;
  font-family: var(--display);
  font-size: clamp(9rem, 24vw, 21rem);
  line-height: 1;
  letter-spacing: 0.04em;
  color: transparent;
  -webkit-text-stroke: 1px rgba(238, 242, 249, 0.06);
  background: linear-gradient(160deg, rgba(45, 226, 166, 0.14), rgba(77, 163, 255, 0.1));
  background-clip: text;
  -webkit-background-clip: text;
  pointer-events: none;
  user-select: none;
  z-index: 0;
}

.hero-scan {
  position: absolute;
  left: -10%;
  right: -10%;
  top: 0;
  height: 150px;
  background: linear-gradient(180deg, transparent, rgba(45, 226, 166, 0.055), transparent);
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
  box-shadow: 0 0 12px rgba(45, 226, 166, 0.9);
  animation: pulse-dot 2s ease-in-out infinite;
}
.hero-eyebrow { margin-bottom: 30px; }

.hero-title {
  font-size: clamp(2.6rem, 9vw, 6rem);
  line-height: 1.1;
  letter-spacing: 0.03em;
  text-shadow: 0 0 60px rgba(45, 226, 166, 0.18);
}
.line { display: block; overflow: hidden; padding-bottom: 0.08em; margin-bottom: -0.08em; }
.line-accent {
  color: var(--accent);
  text-shadow: 0 0 46px rgba(45, 226, 166, 0.5);
}

.hero-sub {
  margin-top: 30px;
  max-width: 520px;
  font-size: 1.05rem;
  color: var(--ink-dim);
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
.hud-label {
  font-size: 0.66rem;
  letter-spacing: 0.34em;
  color: var(--ink-faint);
  writing-mode: vertical-lr;
}
.hud-line {
  width: 1px;
  height: 90px;
  background: linear-gradient(to bottom, var(--accent), transparent);
  box-shadow: 0 0 12px rgba(45, 226, 166, 0.5);
}
.hud-value {
  font-size: 1.5rem;
  font-weight: 700;
  letter-spacing: 0.16em;
  color: var(--accent);
  writing-mode: vertical-lr;
  text-shadow: 0 0 18px rgba(45, 226, 166, 0.6);
}
.hud-status {
  display: flex;
  align-items: center;
  gap: 7px;
  font-size: 0.56rem;
  letter-spacing: 0.24em;
  color: var(--ink-faint);
}
.hud-dot {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: var(--accent);
  animation: pulse-dot 1.8s ease-in-out infinite;
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
.cue-line {
  width: 1px;
  height: 44px;
  background: linear-gradient(to bottom, var(--accent), transparent);
  animation: cue 1.8s var(--ease-expo) infinite;
}
.cue-tri { font-style: normal; color: var(--accent); animation: pulse-dot 1.8s ease-in-out infinite; }

@media (max-width: 640px) {
  .hero-notes { gap: 22px; flex-direction: column; margin-top: 44px; }
  .hero-inner { flex-direction: column; align-items: flex-start; }
  .hero-hud { display: none; }
  .hero-watermark { opacity: 0.5; }
}
</style>
