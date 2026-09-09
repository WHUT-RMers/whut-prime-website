<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { gsap } from 'gsap'
import { prefersReducedMotion } from '../utils/motion'
import { useMouseFx } from '../composables/useMouseFx'
import type { HeroSlide } from '../data/hero'

/**
 * 首屏全屏大图轮播引擎。
 * - 交叉淡入（0.95s）+ 每屏图片持续「呼吸」（scale 1 → 1.06 正弦往复，一个周期约 10s）
 * - 自动播放由 GSAP tween 驱动，底部进度条与播放进度严格同步
 * - 自动播放只在标签页隐藏 / 滚出视口时停（首屏铺满全屏，不做悬停暂停，否则鼠标一动就停住）
 * - 交互：底部刻度 / 左右箭头 / 触摸滑动 / 键盘方向键
 * - 无障碍：carousel/slide 语义、非活动屏 inert + aria-hidden、刻度带 aria-current、实时播报
 */
const props = withDefaults(
  defineProps<{
    slides: HeroSlide[]
    /** 自动播放间隔（ms） */
    interval?: number
    /** 轮播区无障碍标签 */
    label?: string
  }>(),
  { interval: 5500, label: '战队风采轮播' },
)

const emit = defineEmits<{ change: [index: number] }>()

const root = ref<HTMLElement | null>(null)
const bar = ref<HTMLElement | null>(null)
const active = ref(0)
const hidden = ref(false)
const inView = ref(true)
const reduced = prefersReducedMotion()

useMouseFx(root)

/** 非响应式数组：仅用于命令式动画查询，避免无谓的重渲染 */
const slideEls: HTMLElement[] = []
function setSlideEl(el: unknown, i: number) {
  if (el instanceof HTMLElement) slideEls[i] = el
}

const total = computed(() => props.slides.length)
const current = computed(() => props.slides[active.value])
const shouldRun = computed(() => total.value > 1 && !reduced && !hidden.value && inView.value)

let autoTween: gsap.core.Tween | undefined
let kenTween: gsap.core.Tween | undefined
let observer: IntersectionObserver | undefined
let onKey: ((e: KeyboardEvent) => void) | undefined
let onVis: (() => void) | undefined
let swipe: { x: number; y: number; t: number } | null = null

function go(n: number) {
  if (total.value < 2) return
  const next = ((n % total.value) + total.value) % total.value
  if (next === active.value) return
  active.value = next
  emit('change', next)
}

/** 标题逐字 + 附属元素入场 */
function playText(el: HTMLElement) {
  const chars = el.querySelectorAll<HTMLElement>('.slide-title .char')
  const bits = el.querySelectorAll<HTMLElement>('[data-anim]')
  gsap.killTweensOf([...chars, ...bits])
  if (reduced) return
  gsap.fromTo(
    chars,
    { yPercent: 118, opacity: 0 },
    { yPercent: 0, opacity: 1, duration: 1.05, stagger: 0.04, ease: 'expo.out' },
  )
  gsap.fromTo(
    bits,
    { y: 26, opacity: 0 },
    { y: 0, opacity: 1, duration: 0.85, stagger: 0.09, ease: 'expo.out', delay: 0.24 },
  )
}

/** 呼吸：图片缓慢放大再收回（正弦往复，无限循环），奇数屏反向漂移避免千篇一律 */
function breathe(media: HTMLElement, index: number): gsap.core.Tween {
  const dir = index % 2 === 0 ? 1 : -1
  return gsap.fromTo(
    media,
    { scale: 1, xPercent: 0, yPercent: 0 },
    {
      scale: 1.06,
      xPercent: dir * 1.1,
      yPercent: -0.5,
      duration: 5,
      ease: 'sine.inOut',
      yoyo: true,
      repeat: -1,
    },
  )
}

/** 为当前屏重新装上呼吸动画 + 自动播放计时 */
function arm() {
  autoTween?.kill()
  kenTween?.kill()
  autoTween = undefined
  kenTween = undefined

  const el = slideEls[active.value]
  if (el) {
    const media = el.querySelector<HTMLElement>('.slide-media')
    if (media) {
      if (reduced) gsap.set(media, { scale: 1, xPercent: 0, yPercent: 0 })
      else kenTween = breathe(media, active.value)
    }
    playText(el)
  }

  if (reduced || total.value < 2) return

  const p = { v: 0 }
  if (bar.value) gsap.set(bar.value, { scaleX: 0 })
  autoTween = gsap.to(p, {
    v: 1,
    duration: props.interval / 1000,
    ease: 'none',
    onUpdate: () => {
      if (bar.value) gsap.set(bar.value, { scaleX: p.v })
    },
    onComplete: () => go(active.value + 1),
  })
  if (!shouldRun.value) {
    autoTween.pause()
    kenTween?.pause()
  }
}

function onPointerDown(e: PointerEvent) {
  if (e.pointerType === 'mouse') return
  swipe = { x: e.clientX, y: e.clientY, t: Date.now() }
}

function onPointerUp(e: PointerEvent) {
  if (!swipe || e.pointerType === 'mouse') return
  const { x, y, t } = swipe
  swipe = null
  const dx = e.clientX - x
  const dy = e.clientY - y
  if (Date.now() - t > 900) return
  if (Math.abs(dx) < 46 || Math.abs(dx) < Math.abs(dy)) return
  go(active.value + (dx < 0 ? 1 : -1))
}

watch(active, () => arm())

watch(shouldRun, (run) => {
  if (run) {
    autoTween?.resume()
    kenTween?.resume()
  } else {
    autoTween?.pause()
    kenTween?.pause()
  }
})

onMounted(() => {
  const el = root.value
  if (!el) return

  arm()

  observer = new IntersectionObserver(
    (entries) => {
      inView.value = entries[0]?.isIntersecting ?? true
    },
    { threshold: 0.2 },
  )
  observer.observe(el)

  onVis = () => {
    hidden.value = document.hidden
  }
  document.addEventListener('visibilitychange', onVis)

  onKey = (e: KeyboardEvent) => {
    if (!inView.value) return
    const t = e.target as HTMLElement | null
    if (t && /^(INPUT|TEXTAREA|SELECT)$/.test(t.tagName)) return
    if (e.key === 'ArrowLeft') go(active.value - 1)
    else if (e.key === 'ArrowRight') go(active.value + 1)
  }
  window.addEventListener('keydown', onKey)
})

onBeforeUnmount(() => {
  autoTween?.kill()
  kenTween?.kill()
  observer?.disconnect()
  if (onVis) document.removeEventListener('visibilitychange', onVis)
  if (onKey) window.removeEventListener('keydown', onKey)
})

defineExpose({ go })
</script>

<template>
  <section
    ref="root"
    class="hero-carousel"
    role="region"
    aria-roledescription="carousel"
    :aria-label="label"
    @pointerdown="onPointerDown"
    @pointerup="onPointerUp"
    @pointercancel="swipe = null"
  >
    <div class="hero-slides">
      <article
        v-for="(slide, i) in slides"
        :key="slide.id"
        :ref="(el) => setSlideEl(el, i)"
        class="slide"
        :class="[`tone-${slide.tone || 'accent'}`, { 'is-active': i === active }]"
        role="group"
        aria-roledescription="slide"
        :aria-label="`第 ${i + 1} 屏，共 ${total} 屏`"
        :aria-hidden="i !== active"
        :inert="i !== active ? true : undefined"
      >
        <div class="slide-media">
          <img
            v-if="slide.image"
            :src="slide.image"
            :alt="slide.alt || ''"
            :loading="i === 0 ? 'eager' : 'lazy'"
            :fetchpriority="i === 0 ? 'high' : 'auto'"
            decoding="async"
            :style="{ objectPosition: slide.focus || 'center' }"
          />
          <div v-else class="slide-art" aria-hidden="true">
            <span class="art-grid"></span>
            <span class="art-dots"></span>
            <span class="art-ring"></span>
            <span class="art-horizon"></span>
            <span class="art-bars"><i></i><i></i><i></i></span>
            <span class="art-no">{{ slide.no }}</span>
            <span class="art-scan"></span>
          </div>
        </div>

        <div class="slide-scrim" aria-hidden="true"></div>

        <div v-if="!slide.image" class="slide-marks" aria-hidden="true">
          <span class="art-tag">{{ slide.tag || '战队风采' }}</span>
          <span class="art-note">PHOTO PLACEHOLDER · 素材待替换</span>
        </div>

        <div class="container slide-inner">
          <slot name="slide" :slide="slide" :index="i" :active="i === active" />
        </div>
      </article>
    </div>

    <slot name="chrome" />

    <div class="hero-controls">
      <div class="container hero-controls-inner">
        <div class="ctrl-ticks" role="group" aria-label="选择轮播屏">
          <button
            v-for="(slide, i) in slides"
            :key="slide.id"
            type="button"
            class="tick"
            :class="{ 'is-active': i === active }"
            :aria-current="i === active ? 'true' : undefined"
            :aria-label="`第 ${i + 1} 屏：${slide.tag || slide.id}`"
            @click="go(i)"
          >
            <span></span>
          </button>
        </div>
        <div class="ctrl-arrows">
          <button type="button" class="sarrow sarrow-prev" aria-label="上一屏" @click="go(active - 1)">
            <span aria-hidden="true"></span>
          </button>
          <button type="button" class="sarrow sarrow-next" aria-label="下一屏" @click="go(active + 1)">
            <span aria-hidden="true"></span>
          </button>
        </div>
      </div>
    </div>

    <div class="hero-progress" aria-hidden="true"><span ref="bar"></span></div>

    <p class="sr-only" aria-live="polite">
      第 {{ active + 1 }} 屏，共 {{ total }} 屏{{ current?.tag ? '：' + current.tag : '' }}
    </p>
  </section>
</template>

<style scoped>
.hero-carousel {
  position: relative;
  min-height: 100svh;
  overflow: hidden;
  background: var(--bg);
  isolation: isolate;
  touch-action: pan-y;
}

/* ---- 轮播层 ---- */
.hero-slides { position: absolute; inset: 0; z-index: 0; }
.slide {
  /* 占位面板色调（随 slide.tone 切换） */
  --art: #2de2a6;
  --art-soft: rgba(45, 226, 166, 0.16);
  --art-line: rgba(45, 226, 166, 0.28);
  position: absolute;
  inset: 0;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.95s var(--ease);
  backface-visibility: hidden;
}
.slide.tone-blue {
  --art: #4da3ff;
  --art-soft: rgba(77, 163, 255, 0.16);
  --art-line: rgba(77, 163, 255, 0.28);
}
.slide.tone-warm {
  --art: #ffb45e;
  --art-soft: rgba(255, 180, 94, 0.15);
  --art-line: rgba(255, 180, 94, 0.26);
}
.slide.is-active { opacity: 1; pointer-events: auto; z-index: 1; }

.slide-media {
  position: absolute;
  inset: 0;
  will-change: transform;
  transform-origin: 55% 50%;
}
.slide-media img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  /* 照片向站点暗调靠拢：降饱和 + 提对比，压住杂色 */
  filter: saturate(0.9) contrast(1.06);
}

/* ---- 几何占位面板（素材到位后自动隐藏） ---- */
.slide-art {
  position: absolute;
  inset: 0;
  overflow: hidden;
  background:
    radial-gradient(118% 92% at 78% 14%, var(--art-soft), transparent 62%),
    linear-gradient(158deg, #0b0e16 0%, #07080d 54%, #04050a 100%);
}

.art-grid {
  position: absolute;
  left: -10%;
  right: -10%;
  bottom: -14%;
  height: 52%;
  background-image:
    linear-gradient(var(--art-line) 1px, transparent 1px),
    linear-gradient(90deg, var(--art-line) 1px, transparent 1px);
  background-size: 62px 62px;
  transform: perspective(820px) rotateX(64deg);
  transform-origin: top;
  opacity: 0.85;
  -webkit-mask-image: radial-gradient(74% 92% at 50% 0%, #000, transparent 78%);
  mask-image: radial-gradient(74% 92% at 50% 0%, #000, transparent 78%);
}
.art-dots {
  position: absolute;
  left: 4%;
  top: 14%;
  width: 38%;
  height: 42%;
  background-image: radial-gradient(var(--art-line) 1.2px, transparent 1.2px);
  background-size: 20px 20px;
  opacity: 0.75;
  -webkit-mask-image: radial-gradient(70% 70% at 0% 0%, #000, transparent 74%);
  mask-image: radial-gradient(70% 70% at 0% 0%, #000, transparent 74%);
}
.art-ring {
  position: absolute;
  right: 6%;
  top: 46%;
  width: min(46vw, 540px);
  aspect-ratio: 1;
  border: 1px solid var(--art-line);
  border-radius: 50%;
  transform: translateY(-50%);
  opacity: 0.85;
}
.art-ring::after {
  content: '';
  position: absolute;
  inset: 21%;
  border: 1px dashed var(--art-line);
  border-radius: 50%;
  opacity: 0.7;
}
.art-bars {
  position: absolute;
  right: -5%;
  top: 20%;
  display: flex;
  flex-direction: column;
  gap: 15px;
  transform: rotate(-20deg);
}
.art-bars i { display: block; height: 10px; background: var(--art); }
.art-bars i:nth-child(1) { width: 320px; opacity: 0.34; }
.art-bars i:nth-child(2) { width: 200px; opacity: 0.6; }
.art-bars i:nth-child(3) { width: 430px; opacity: 0.2; }
.art-no {
  position: absolute;
  right: 3%;
  bottom: 13%;
  font-family: var(--display);
  font-size: clamp(8rem, 22vw, 19rem);
  line-height: 0.9;
  color: transparent;
  background: linear-gradient(180deg, var(--art-soft), transparent 78%);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-stroke: 2px var(--art-line);
  opacity: 0.9;
  user-select: none;
}

/* 地平线：一条贯穿画面的细线 + 端点方块 */
.art-horizon {
  position: absolute;
  left: 0;
  right: 0;
  top: 58%;
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--art-line) 22%, var(--art-line) 78%, transparent);
  opacity: 0.8;
}
.art-horizon::before,
.art-horizon::after {
  content: '';
  position: absolute;
  top: -3px;
  width: 7px;
  height: 7px;
  background: var(--art);
  opacity: 0.7;
}
.art-horizon::before { left: 18%; }
.art-horizon::after { right: 18%; }
.art-scan {
  position: absolute;
  left: -10%;
  right: -10%;
  top: 0;
  height: 84px;
  opacity: 0.5;
  background: linear-gradient(180deg, transparent, var(--art-soft), transparent);
  animation: scan-move 9s linear infinite;
}

/* ---- 暗角 / 文字压暗层 ---- */
.slide-scrim {
  position: absolute;
  inset: 0;
  z-index: 2;
  pointer-events: none;
  background:
    linear-gradient(
      90deg,
      rgba(6, 7, 13, 0.94) 0%,
      rgba(6, 7, 13, 0.76) 26%,
      rgba(6, 7, 13, 0.3) 56%,
      rgba(6, 7, 13, 0.14) 78%,
      rgba(6, 7, 13, 0.62) 100%
    ),
    linear-gradient(
      180deg,
      rgba(6, 7, 13, 0.76) 0%,
      rgba(6, 7, 13, 0.1) 24%,
      rgba(6, 7, 13, 0.1) 44%,
      rgba(6, 7, 13, 0.86) 100%
    );
}

/* ---- 占位标注（压在暗角之上） ---- */
.slide-marks {
  position: absolute;
  inset: 0;
  z-index: 4;
  pointer-events: none;
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: calc(var(--nav-h) + 26px) var(--page-gutter) 0;
  align-items: flex-start;
  font-family: var(--mono);
}
.art-tag {
  display: inline-flex;
  align-items: center;
  gap: 9px;
  font-size: 0.66rem;
  letter-spacing: 0.26em;
  color: var(--ink-dim);
}
.art-tag::before {
  content: '';
  width: 6px;
  height: 6px;
  background: var(--art, var(--accent));
}
.art-note { font-size: 0.56rem; letter-spacing: 0.22em; color: var(--ink-faint); }

/* ---- 内容容器 ---- */
.slide-inner {
  position: relative;
  z-index: 3;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  padding-top: calc(var(--nav-h) + 40px);
  padding-bottom: clamp(168px, 21vh, 214px);
}

/* ---- 控制区 ---- */
.hero-controls {
  position: absolute;
  left: 0;
  right: 0;
  bottom: clamp(96px, 13vh, 128px);
  z-index: 5;
  pointer-events: none;
}
.hero-controls-inner {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 18px;
}
.hero-controls-inner > * { pointer-events: auto; }

.ctrl-ticks { display: flex; align-items: center; gap: 8px; }
.tick {
  width: 28px;
  height: 20px;
  padding: 0;
  border: 0;
  background: none;
  display: grid;
  place-items: center;
}
.tick span {
  display: block;
  width: 100%;
  height: 3px;
  background: var(--line-strong);
  transition: background 0.3s, transform 0.4s var(--ease-expo);
  transform-origin: left;
}
.tick:hover span { background: var(--ink-dim); }
.tick.is-active { width: 44px; }
.tick.is-active span { background: var(--accent); }

.ctrl-arrows { display: flex; gap: 8px; }
.sarrow {
  width: 42px;
  height: 42px;
  display: grid;
  place-items: center;
  border: 1px solid var(--line-strong);
  border-radius: 8px;
  background: rgba(6, 7, 13, 0.42);
  color: var(--ink-dim);
  transition: border-color 0.3s, color 0.3s, background 0.3s, transform 0.35s var(--ease-expo);
}
.sarrow span {
  width: 8px;
  height: 8px;
  border-top: 1px solid currentColor;
  border-right: 1px solid currentColor;
}
.sarrow-prev span { transform: rotate(-135deg); margin-left: 3px; }
.sarrow-next span { transform: rotate(45deg); margin-right: 3px; }
.sarrow:hover { border-color: var(--accent); color: var(--accent); background: rgba(45, 226, 166, 0.08); }
.sarrow:active { transform: scale(0.94); }

/* ---- 自动播放进度 ---- */
.hero-progress {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  height: 2px;
  z-index: 6;
  pointer-events: none;
}
.hero-progress span {
  display: block;
  height: 100%;
  background: var(--accent);
  transform: scaleX(0);
  transform-origin: left;
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  margin: -1px;
  padding: 0;
  overflow: hidden;
  clip-path: inset(50%);
  white-space: nowrap;
  border: 0;
}

@media (max-width: 900px) {
  .slide-inner { padding-bottom: clamp(152px, 20vh, 190px); }
  .hero-controls { bottom: clamp(92px, 12vh, 112px); }
}

@media (max-width: 640px) {
  .hero-carousel { min-height: max(100svh, 640px); }
  .slide-scrim {
    background: linear-gradient(
      180deg,
      rgba(6, 7, 13, 0.82) 0%,
      rgba(6, 7, 13, 0.26) 20%,
      rgba(6, 7, 13, 0.48) 46%,
      rgba(6, 7, 13, 0.95) 100%
    );
  }
  .slide-inner { padding-top: calc(var(--nav-h) + 24px); padding-bottom: 168px; }
  .hero-controls { bottom: 92px; }
  .hero-controls-inner { justify-content: space-between; gap: 12px; }
  .art-ring { right: -14%; width: 74vw; }
  .art-bars { right: -22%; }
  .art-no { right: -2%; font-size: clamp(7rem, 34vw, 12rem); }
  .slide-marks { padding-top: calc(var(--nav-h) + 16px); }
  .art-note { display: none; }
  .sarrow { width: 40px; height: 40px; }
  .ctrl-ticks { gap: 6px; }
  .tick { width: 22px; }
  .tick.is-active { width: 34px; }
}

@media (orientation: landscape) and (max-height: 620px) {
  .hero-carousel { min-height: 560px; }
  .slide-inner { padding-top: calc(var(--nav-h) + 20px); padding-bottom: 128px; }
  .hero-controls { bottom: 74px; }
  .art-no { font-size: clamp(6rem, 16vw, 11rem); }
}

@media (prefers-reduced-motion: reduce) {
  .slide { transition: none; }
}
</style>
