<script setup lang="ts">
import { ref } from 'vue'
import { gsap } from 'gsap'
import { useRoute } from 'vue-router'
import SiteNav from './components/SiteNav.vue'
import AppFooter from './components/AppFooter.vue'

const route = useRoute()

/** 导航顺序（对应顶部栏目） */
const order = ['home', 'news', 'history', 'groups', 'recruit', 'cooperate']
const currentIndex = ref(order.indexOf(route.name as string) || 0)
/** 方向：-1 前进（目标在右边）/ +1 后退（目标在左边） */
const dir = ref(1)

/** 旧页正文：按点击方向消散（目标在右→向左消散；目标在左→向右消散） */
function onLeave(el: Element, done: () => void) {
  const toIndex = order.indexOf(route.name as string)
  dir.value = toIndex >= currentIndex.value ? -1 : 1
  currentIndex.value = toIndex
  gsap.to(el, {
    x: dir.value * 72,
    autoAlpha: 0,
    filter: 'blur(4px)',
    duration: 0.38,
    ease: 'power2.in',
    onComplete: done,
  })
}

/** 新页正文：从消散的反向弹出 */
function onEnter(el: Element, done: () => void) {
  gsap.fromTo(
    el,
    { scale: 0.95, autoAlpha: 0, x: -dir.value * 48 },
    {
      scale: 1,
      autoAlpha: 1,
      x: 0,
      duration: 0.55,
      ease: 'back.out(1.6)',
      clearProps: 'filter,transform',
      onComplete: done,
    },
  )
}
</script>

<template>
  <SiteNav />
  <main>
    <RouterView v-slot="{ Component }">
      <Transition mode="out-in" @leave="onLeave" @enter="onEnter">
        <component :is="Component" />
      </Transition>
    </RouterView>
  </main>
  <AppFooter />
</template>
