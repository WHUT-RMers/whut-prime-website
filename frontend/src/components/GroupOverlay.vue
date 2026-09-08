<script setup lang="ts">
import { nextTick, onBeforeUnmount, ref, watch } from 'vue'
import { gsap } from 'gsap'
import { groupOverlay } from '../composables/useGroupOverlay'
import { prefersReducedMotion } from '../utils/motion'
import GroupDetailContent from './GroupDetailContent.vue'

/**
 * 组别详情全屏浮层：点击首页/列表页组别卡片时在当前页上弹出独立详情页。
 * - 左上角「← 返回」/ ESC 关闭，底层页面不卸载，滚动位置天然保留
 * - 打开期间锁定底层滚动（补偿滚动条宽度，避免页面横向跳动）
 */
const group = groupOverlay.group
const closeBtn = ref<HTMLElement | null>(null)
let lastFocus: HTMLElement | null = null

function lockScroll() {
  const w = window.innerWidth - document.documentElement.clientWidth
  document.documentElement.style.overflow = 'hidden'
  document.body.style.paddingRight = w > 0 ? w + 'px' : ''
}
function unlockScroll() {
  document.documentElement.style.overflow = ''
  document.body.style.paddingRight = ''
}

const onKey = (e: KeyboardEvent) => {
  if (e.key === 'Escape') groupOverlay.close()
}

watch(group, (g) => {
  if (g) {
    lastFocus = document.activeElement as HTMLElement | null
    lockScroll()
    window.addEventListener('keydown', onKey)
  } else {
    unlockScroll()
    window.removeEventListener('keydown', onKey)
  }
})

function onEnter(el: Element, done: () => void) {
  const finish = () => {
    nextTick(() => closeBtn.value?.focus())
    done()
  }
  if (prefersReducedMotion()) {
    gsap.set(el, { autoAlpha: 1, y: 0 })
    finish()
    return
  }
  gsap.fromTo(
    el,
    { autoAlpha: 0, y: 28 },
    { autoAlpha: 1, y: 0, duration: 0.5, ease: 'expo.out', clearProps: 'transform', onComplete: finish },
  )
}

function onLeave(el: Element, done: () => void) {
  if (prefersReducedMotion()) {
    gsap.set(el, { autoAlpha: 0 })
    done()
    return
  }
  gsap.to(el, { autoAlpha: 0, y: 18, duration: 0.32, ease: 'power2.in', onComplete: done })
}

function onAfterLeave() {
  lastFocus?.focus?.()
}

onBeforeUnmount(() => {
  unlockScroll()
  window.removeEventListener('keydown', onKey)
})
</script>

<template>
  <Transition @enter="onEnter" @leave="onLeave" @after-leave="onAfterLeave">
    <div
      v-if="group"
      class="ov"
      role="dialog"
      aria-modal="true"
      :aria-label="group.name + ' 组别详情'"
    >
      <div class="ov-top">
        <button
          ref="closeBtn"
          type="button"
          class="ov-back"
          aria-label="返回上一页"
          @click="groupOverlay.close()"
        >
          <span class="ov-back-arrow" aria-hidden="true">←</span>
          <span class="ov-back-text">返回</span>
        </button>
        <span class="ov-code" aria-hidden="true">{{ group.code }} / GROUP DETAIL</span>
      </div>

      <div class="ov-scroll">
        <div class="container">
          <GroupDetailContent :key="group.code" :group="group" immediate />
        </div>
      </div>
    </div>
  </Transition>
</template>

<style scoped>
.ov {
  position: fixed;
  inset: 0;
  z-index: 100; /* 高于导航(60)与返回顶部(90)，低于自定义光标(9999) */
  display: flex;
  flex-direction: column;
  background: var(--bg);
}

.ov-top {
  position: relative;
  z-index: 2;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 18px 28px 0;
}
.ov-back {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 10px 18px;
  border: 1px solid var(--line-strong);
  border-radius: 999px;
  background: var(--surface);
  color: var(--ink);
  font-family: var(--mono);
  font-size: 0.8rem;
  letter-spacing: 0.14em;
  cursor: pointer;
  transition: border-color 0.25s, background 0.25s, transform 0.4s var(--ease-expo);
}
.ov-back:hover { border-color: var(--accent); background: var(--surface-2); }
.ov-back:active { transform: scale(0.96); }
.ov-back-arrow { color: var(--accent); font-size: 1rem; font-family: var(--sans); }

.ov-code {
  font-family: var(--mono);
  font-size: 0.64rem;
  letter-spacing: 0.3em;
  color: var(--ink-faint);
}

.ov-scroll {
  flex: 1;
  overflow-y: auto;
  padding: 6px 0 90px;
  overscroll-behavior: contain;
}

@media (max-width: 640px) {
  .ov-top { padding: 14px 16px 0; }
  .ov-code { display: none; }
}
</style>