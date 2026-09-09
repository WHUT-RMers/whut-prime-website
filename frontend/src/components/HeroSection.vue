<script setup lang="ts">
import { onMounted } from 'vue'
import HeroCarousel from './HeroCarousel.vue'
import { heroSlides } from '../data/hero'
import { charsHtml } from '../utils/text'
import { countUp, prefersReducedMotion } from '../utils/motion'

/** 底部常驻数据条（不随轮播切换） */
const stats = [
  { value: 4, suffix: '', label: '大组别' },
  { value: 100, suffix: '+', label: '名队员' },
  { value: 9, suffix: '', label: '项全国二等奖' },
]

const reduced = prefersReducedMotion()

onMounted(() => {
  document.querySelectorAll<HTMLElement>('.hero-carousel [data-count]').forEach((node) => {
    const target = Number(node.dataset.count)
    if (reduced) {
      node.textContent = String(target)
      return
    }
    countUp(node, target, 1.9, 'power3.out', 1.2)
  })
})
</script>

<template>
  <HeroCarousel id="top" :slides="heroSlides" :interval="7000" label="WHUT PRIME 战队风采轮播">
    <template #slide="{ slide }">
      <div class="slide-copy">
        <p class="eyebrow slide-eyebrow" data-anim>
          <span class="eyebrow-dot" aria-hidden="true"></span>{{ slide.eyebrow }}
        </p>

        <h1 class="slide-title">
          <span
            v-for="(line, li) in slide.title"
            :key="li"
            class="line"
            :class="{ 'line-accent': li === (slide.accentLine ?? -1) }"
          >
            <span v-html="charsHtml(line)"></span>
          </span>
        </h1>

        <p class="slide-sub" data-anim>{{ slide.sub }}</p>

        <div class="slide-actions" data-anim>
          <template v-for="cta in slide.ctas" :key="cta.label">
            <RouterLink
              v-if="cta.to"
              :to="cta.to"
              class="btn"
              :class="cta.primary ? 'btn-primary' : 'btn-ghost'"
              data-magnet
            >
              {{ cta.label }} <span aria-hidden="true">→</span>
            </RouterLink>
            <a v-else :href="cta.href" class="btn btn-ghost" data-magnet>
              {{ cta.label }} <span aria-hidden="true">→</span>
            </a>
          </template>
        </div>
      </div>
    </template>

    <template #chrome>
      <div class="hero-hud" aria-hidden="true">
        <span class="hud-label">UNIT-01</span>
        <span class="hud-line"></span>
        <span class="hud-value">PRIME</span>
        <span class="hud-status"><i class="hud-dot"></i>SYSTEM ONLINE</span>
      </div>

      <div class="hero-foot">
        <div class="container hero-foot-inner">
          <ul class="hero-notes">
            <li v-for="s in stats" :key="s.label">
              <span class="k"><span :data-count="s.value">{{ s.value }}</span>{{ s.suffix }}</span>
              {{ s.label }}
            </li>
          </ul>
        </div>
        <div class="scroll-cue" aria-hidden="true">
          <span class="cue-line"></span>SCROLL <i class="cue-tri">▾</i>
        </div>
      </div>
    </template>
  </HeroCarousel>
</template>

<style scoped>
/* ---- 文案区 ---- */
.slide-copy { max-width: 780px; color: var(--hero-ink); }
.slide-eyebrow { margin-bottom: 26px; color: var(--hero-accent); }
.eyebrow-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--hero-accent);
  animation: pulse-dot 2s ease-in-out infinite;
}

.slide-title {
  font-size: clamp(2.6rem, 8vw, 5.6rem);
  line-height: 1.08;
  letter-spacing: 0.03em;
}
.slide-title .line {
  display: block;
  overflow: hidden;
  padding-bottom: 0.1em;
  margin-bottom: -0.1em;
}
.line-accent { color: var(--hero-accent); }

.slide-sub {
  margin-top: 26px;
  max-width: 560px;
  font-size: 1.05rem;
  color: var(--hero-ink-dim);
  text-wrap: pretty;
}

.slide-actions { display: flex; gap: 14px; margin-top: 36px; flex-wrap: wrap; }
/* 照片上：幽灵按钮无条件用亮色描边/文字（深、浅主题都不变暗） */
.slide-actions .btn-ghost {
  border-color: var(--hero-line-strong);
  color: var(--hero-ink-dim);
}
.slide-actions .btn-ghost:hover {
  border-color: var(--hero-accent);
  color: var(--hero-accent);
  background: rgba(45, 226, 166, 0.08);
}

/* ---- 右侧 HUD ---- */
.hero-hud {
  position: absolute;
  right: var(--page-gutter);
  top: 50%;
  transform: translateY(-50%);
  z-index: 5;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 14px;
  font-family: var(--mono);
}
.hud-label { font-size: 0.66rem; letter-spacing: 0.34em; color: var(--ink-faint); writing-mode: vertical-lr; }
.hud-line { width: 1px; height: 90px; background: linear-gradient(to bottom, var(--accent), transparent); }
.hud-value { font-size: 1.5rem; font-weight: 700; letter-spacing: 0.16em; color: var(--accent); writing-mode: vertical-lr; }
.hud-status { display: flex; align-items: center; gap: 7px; font-size: 0.56rem; letter-spacing: 0.24em; color: var(--ink-faint); }
.hud-dot { width: 5px; height: 5px; border-radius: 50%; background: var(--accent); animation: pulse-dot 1.8s ease-in-out infinite; }

/* ---- 底部数据条 ---- */
.hero-foot {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 4;
  height: 86px;
  display: flex;
  align-items: center;
  border-top: 1px solid var(--line);
  background: linear-gradient(180deg, rgba(6, 7, 13, 0), rgba(6, 7, 13, 0.88) 58%);
}
.hero-foot-inner { display: flex; align-items: center; }

.hero-notes {
  list-style: none;
  display: flex;
  gap: clamp(22px, 3.4vw, 46px);
  color: var(--hero-ink-dim);
  font-size: 0.92rem;
}
.hero-notes li { display: flex; align-items: baseline; gap: 8px; }
.hero-notes .k {
  font-family: var(--mono);
  font-size: 1.6rem;
  font-weight: 700;
  color: var(--hero-ink);
  font-variant-numeric: tabular-nums;
}

/* ---- 滚动提示 ---- */
.scroll-cue {
  position: absolute;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  font-family: var(--mono);
  font-size: 0.6rem;
  letter-spacing: 0.3em;
  color: var(--hero-ink-faint);
}
.cue-line { width: 1px; height: 24px; background: linear-gradient(to bottom, var(--hero-accent), transparent); animation: cue 1.8s var(--ease-expo) infinite; }
.cue-tri { font-style: normal; color: var(--hero-accent); animation: pulse-dot 1.8s ease-in-out infinite; }

@media (max-width: 1080px) {
  .hero-hud { display: none; }
}

@media (max-width: 900px) {
  .slide-title { font-size: clamp(2.5rem, 9.4vw, 4.4rem); }
  .slide-sub { max-width: 640px; font-size: 1rem; }
  .slide-actions { margin-top: 30px; }
  .hero-notes { gap: 24px; font-size: 0.86rem; }
  .hero-notes .k { font-size: 1.4rem; }
  .hero-foot { height: 78px; }
  .scroll-cue { display: none; }
}

@media (max-width: 640px) {
  .slide-eyebrow { margin-bottom: 20px; line-height: 1.75; }
  .slide-title { font-size: clamp(2.4rem, 12.6vw, 3.6rem); line-height: 1.1; }
  .slide-sub { margin-top: 22px; line-height: 1.85; }
  .slide-actions { margin-top: 28px; gap: 12px; }
  .hero-foot { height: 76px; }
  .hero-notes { gap: 10px 18px; flex-wrap: wrap; font-size: 0.78rem; }
  .hero-notes li { gap: 6px; }
  .hero-notes .k { font-size: 1.15rem; }
}

@media (max-width: 380px) {
  .slide-title { font-size: clamp(2.15rem, 12vw, 3rem); }
  .slide-actions .btn { flex: 1 1 140px; }
}

@media (orientation: landscape) and (max-height: 620px) {
  .slide-title { font-size: clamp(2.3rem, 7vw, 3.8rem); }
  .slide-sub { margin-top: 16px; max-width: 700px; font-size: 0.94rem; }
  .slide-actions { margin-top: 20px; }
  .hero-foot { height: 64px; }
  .hero-notes .k { font-size: 1.25rem; }
}
</style>
