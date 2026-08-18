<script setup lang="ts">
import { ref } from 'vue'
import { gsap } from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
import { useRoute } from 'vue-router'
import SiteNav from './components/SiteNav.vue'
import AppFooter from './components/AppFooter.vue'
import MouseCursor from './components/MouseCursor.vue'
import { prefersReducedMotion } from './utils/motion'

const route = useRoute()
const reduced = prefersReducedMotion()

/** 导航顺序：决定过场滑动方向（1 前进 / -1 后退） */
const order = ['home', 'news', 'history', 'groups', 'recruit', 'cooperate']
const prevIndex = ref(Math.max(0, order.indexOf(route.name as string)))
const dir = ref(1)

/**
 * 离场：旧页沿前进方向滑出（前进 → 向左滑走；后退 → 向右滑走），
 * 轻微淡化 + 退场比入场更快，节奏利落。
 */
function onLeave(el: Element, done: () => void) {
  const toIndex = order.indexOf(route.name as string)
  dir.value = toIndex >= prevIndex.value ? 1 : -1
  prevIndex.value = toIndex

  if (reduced) {
    gsap.to(el, { autoAlpha: 0, duration: 0.15, ease: 'power2.in', onComplete: done })
    return
  }
  gsap.fromTo(
    el,
    { xPercent: 0, autoAlpha: 1, willChange: 'transform' },
    {
      xPercent: -dir.value * 100,
      autoAlpha: 0.35,
      duration: 0.4,
      ease: 'power3.inOut',
      onComplete: done,
      clearProps: 'willChange',
    },
  )
}

/**
 * 入场：新页从前进方向的反侧滑入（前进 → 自右侧进入；后退 → 自左侧进入），
 * expo.out 缓出收尾干脆、无拖泥带水。
 */
function onEnter(el: Element, done: () => void) {
  if (reduced) {
    gsap.fromTo(
      el,
      { autoAlpha: 0 },
      { autoAlpha: 1, duration: 0.25, ease: 'power2.out', onComplete: done },
    )
    return
  }
  const tl = gsap.timeline({ onComplete: done })
  tl.fromTo(
      el,
      { xPercent: dir.value * 100, autoAlpha: 0, willChange: 'transform' },
      {
        xPercent: 0,
        autoAlpha: 1,
        duration: 0.55,
        ease: 'expo.out',
        clearProps: 'transform,willChange',
      },
      0,
    )
    .add(() => ScrollTrigger.refresh())
}
</script>

<template>
  <SiteNav />
  <main>
    <RouterView v-slot="{ Component }">
      <Transition mode="out-in" @leave="onLeave" @enter="onEnter">
        <component :is="Component" :key="route.path" />
      </Transition>
    </RouterView>
  </main>
  <AppFooter />

  <MouseCursor />
</template>