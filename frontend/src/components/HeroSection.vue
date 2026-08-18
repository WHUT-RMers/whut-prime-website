<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { gsap } from 'gsap'
import { charsHtml } from '../utils/text'

const root = ref<HTMLElement | null>(null)

onMounted(() => {
  const el = root.value
  if (!el) return
  const tl = gsap.timeline({ defaults: { ease: 'power3.out' } })
  tl.from('.hero-eyebrow', { y: 18, opacity: 0, duration: 0.7 })
    .from(
      '.hero-title .char',
      { yPercent: 120, opacity: 0, duration: 0.9, stagger: 0.035 },
      '-=0.3',
    )
    .from('.hero-sub', { y: 22, opacity: 0, duration: 0.8 }, '-=0.55')
    .from('.hero-actions > *', { y: 16, opacity: 0, duration: 0.6, stagger: 0.12 }, '-=0.5')
    .from('.hero-notes li', { opacity: 0, x: -12, duration: 0.5, stagger: 0.1 }, '-=0.35')
    .from('.hero-spec', { opacity: 0, scale: 0.9, duration: 0.9 }, '-=0.5')
    .from('.scroll-cue', { opacity: 0, duration: 0.8 }, '-=0.25')

  gsap.to('.orb', {
    x: 'random(-60, 60)',
    y: 'random(-40, 40)',
    duration: 'random(7, 11)',
    repeat: -1,
    yoyo: true,
    ease: 'sine.inOut',
    stagger: 0.4,
  })
})
</script>

<template>
  <section id="top" ref="root" class="hero">
    <div class="orb orb-1" aria-hidden="true"></div>
    <div class="orb orb-2" aria-hidden="true"></div>
    <div class="orb orb-3" aria-hidden="true"></div>

    <div class="container hero-inner">
      <div class="hero-main">
        <p class="eyebrow hero-eyebrow">WUHAN UNIVERSITY OF TECHNOLOGY · ROBOMASTER</p>

        <h1 class="hero-title">
          <span class="line" v-html="charsHtml('以代码铸甲')"></span>
          <span class="line line-accent" v-html="charsHtml('以热血参战。')"></span>
        </h1>

        <p class="hero-sub">
          武汉理工大学 RoboMaster 战队 PRIME：机械、电控、算法、运营，
          四个组别，一支军团。
        </p>

        <div class="hero-actions">
          <a href="#recruit" class="btn btn-primary">投递简历 <span aria-hidden="true">→</span></a>
          <a href="#event" class="btn btn-ghost">了解赛事</a>
        </div>

        <ul class="hero-notes">
          <li><span class="k">9</span> 个赛季</li>
          <li><span class="k">5</span> 大组别</li>
          <li><span class="k">50+</span> 名队员</li>
        </ul>
      </div>

      <div class="hero-spec" aria-hidden="true">
        <span class="spec-label">UNIT-01</span>
        <span class="spec-line"></span>
        <span class="spec-value">PRIME</span>
      </div>
    </div>

    <div class="scroll-cue" aria-hidden="true"><span class="cue-line"></span>SCROLL</div>
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
.hero-inner {
  position: relative;
  z-index: 2;
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 40px;
}

.hero-eyebrow { margin-bottom: 30px; }

.hero-title {
  font-size: clamp(2.5rem, 8.5vw, 5.6rem);
  line-height: 1.12;
  letter-spacing: 0.03em;
}
.line { display: block; overflow: hidden; padding-bottom: 0.08em; margin-bottom: -0.08em; }
.line-accent { color: var(--accent); }

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
.hero-notes .k {
  font-family: var(--mono);
  font-size: 1.6rem;
  font-weight: 700;
  color: var(--ink);
  margin-right: 6px;
  vertical-align: -0.08em;
}

.hero-spec {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 14px;
  padding-bottom: 12px;
  font-family: var(--mono);
}
.spec-label {
  font-size: 0.68rem;
  letter-spacing: 0.34em;
  color: var(--ink-faint, #5b6673);
  writing-mode: vertical-lr;
}
.spec-line {
  width: 1px;
  height: 90px;
  background: linear-gradient(to bottom, var(--accent), transparent);
}
.spec-value {
  font-size: 1.5rem;
  font-weight: 700;
  letter-spacing: 0.16em;
  color: var(--accent);
  writing-mode: vertical-lr;
}

.orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(90px);
  opacity: 0.5;
  z-index: 1;
  pointer-events: none;
}
.orb-1 { width: 420px; height: 420px; background: rgba(45, 226, 166, 0.14); top: 8%; right: -6%; }
.orb-2 { width: 320px; height: 320px; background: rgba(56, 120, 255, 0.12); bottom: 4%; left: -4%; }
.orb-3 { width: 180px; height: 180px; background: rgba(45, 226, 166, 0.16); top: 55%; left: 52%; }

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
  color: #5b6673;
}
.cue-line {
  width: 1px;
  height: 44px;
  background: linear-gradient(to bottom, var(--accent), transparent);
  animation: cue 1.8s var(--ease) infinite;
}
@keyframes cue {
  0% { transform: scaleY(0); transform-origin: top; }
  45% { transform: scaleY(1); transform-origin: top; }
  55% { transform: scaleY(1); transform-origin: bottom; }
  100% { transform: scaleY(0); transform-origin: bottom; }
}

@media (max-width: 640px) {
  .hero-notes { gap: 22px; flex-direction: column; margin-top: 44px; }
  .hero-inner { flex-direction: column; align-items: flex-start; }
  .hero-spec { display: none; }
}
</style>
