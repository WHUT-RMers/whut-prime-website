<script setup lang="ts">
import { computed, ref } from 'vue'
import { gsap } from 'gsap'
import { useScrollReveal } from '../composables/useGsapReveal'

const props = defineProps<{
  eyebrow: string
  title: string
  desc?: string
}>()

const root = ref<HTMLElement | null>(null)
useScrollReveal(root, { blur: 10 })

/** 从 eyebrow（如 "02 / 战队资讯"）提取章节序号作为底纹水印 */
const watermark = computed(() => props.eyebrow.slice(0, 2).trim())

let reset: (() => void) | undefined
function onParallax(el: HTMLElement | null) {
  if (!el) return
  const mm = gsap.matchMedia()
  mm.add('(prefers-reduced-motion: no-preference)', () => {
    gsap.fromTo(
      el,
      { y: 40 },
      { y: -40, ease: 'none', scrollTrigger: { trigger: el, start: 'top bottom', end: 'bottom top', scrub: 0.8 } },
    )
  })
  reset = () => mm.revert()
}
</script>

<template>
  <div ref="root" class="page-head">
    <span ref="onParallax" class="page-cover" aria-hidden="true">{{ watermark }}</span>
    <p class="eyebrow" data-reveal>{{ eyebrow }}</p>
    <h1 class="page-title" data-reveal>{{ title }}</h1>
    <p v-if="desc" class="page-desc" data-reveal>{{ desc }}</p>
  </div>
</template>

<style scoped>
.page-head {
  position: relative;
  padding: calc(var(--nav-h) + 70px) 70px 18px;
  max-width: 900px;
}
.page-cover {
  position: absolute;
  right: -20px;
  top: calc(var(--nav-h) - 10px);
  font-family: var(--display);
  font-size: clamp(7rem, 18vw, 14rem);
  line-height: 1;
  color: transparent;
  -webkit-text-stroke: 1px rgba(238, 242, 249, 0.07);
  user-select: none;
  pointer-events: none;
}
.page-title {
  margin-top: 22px;
  font-size: clamp(2rem, 4.5vw, 3.5rem);
  line-height: 1.2;
}
.page-desc { margin-top: 18px; color: var(--ink-dim); font-size: 1.02rem; max-width: 640px; }

@media (max-width: 640px) {
  .page-head { padding: calc(var(--nav-h) + 48px) 24px 12px; }
  .page-cover { right: 6px; font-size: 7rem; }
}
</style>
