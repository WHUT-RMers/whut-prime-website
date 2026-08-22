import { onBeforeUnmount, onMounted, type Ref } from 'vue'
import { gsap } from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
import { prefersReducedMotion } from '../utils/motion'

export interface RevealOptions {
  /** 要执行入场动画的元素选择器，默认 '[data-reveal]' */
  selector?: string
  /** 垂直位移量 */
  y?: number
  /** 水平位移量 */
  x?: number
  /** 起始缩放 */
  scale?: number
  /** 起始模糊（px），0 关闭 */
  blur?: number
  /** 元素间交错延迟 */
  stagger?: number
  /** 动画时长 */
  duration?: number
  /** 缓动曲线 */
  ease?: string
  /** ScrollTrigger start 位置 */
  start?: string
}

/**
 * 通用滚动入场（motion-driven 版）：fade + rise + blur，expo.out 缓动。
 * 通过 gsap.context 绑定生命周期，组件卸载时自动 revert；
 * 尊重 prefers-reduced-motion（跳过动画直接显示）。
 */
export function useScrollReveal(rootRef: Ref<HTMLElement | null>, opts: RevealOptions = {}): void {
  const {
    selector = '[data-reveal]',
    y = 32,
    x = 0,
    scale = 1,
    blur = 6,
    stagger = 0.09,
    duration = 0.95,
    ease = 'expo.out',
    start = 'top 82%',
  } = opts
  let ctx: gsap.Context | undefined

  onMounted(() => {
    const root = rootRef.value
    if (!root) return
    const targets = Array.from(root.querySelectorAll<HTMLElement>(selector))
    if (!targets.length) return

    // 减弱动态：直接显示，不创建动画
    if (prefersReducedMotion()) {
      gsap.set(targets, { clearProps: 'all' })
      return
    }

    ctx = gsap.context(() => {
      gsap.from(targets, {
        y,
        x,
        scale,
        opacity: 0,
        filter: blur ? `blur(${blur}px)` : 'none',
        duration,
        ease,
        stagger,
        scrollTrigger: { trigger: root, start, once: true },
        clearProps: 'transform,filter',
      })
    }, root)
  })

  onBeforeUnmount(() => {
    // gsap.context 会一并 revert 内部创建的 ScrollTrigger，无需全局清理
    ctx?.revert()
    void ScrollTrigger
  })
}
