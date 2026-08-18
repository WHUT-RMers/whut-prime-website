import { onBeforeUnmount, onMounted, type Ref } from 'vue'
import { gsap } from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'

export interface RevealOptions {
  /** 要执行入场动画的元素选择器，默认 '[data-reveal]' */
  selector?: string
  /** 垂直位移量 */
  y?: number
  /** 元素间交错延迟 */
  stagger?: number
  /** ScrollTrigger start 位置 */
  start?: string
}

/**
 * 通用滚动入场：为根节点内匹配 selector 的元素做 fade + rise 入场。
 * 通过 gsap.context 绑定生命周期，组件卸载时自动 revert。
 */
export function useScrollReveal(rootRef: Ref<HTMLElement | null>, opts: RevealOptions = {}): void {
  const { selector = '[data-reveal]', y = 28, stagger = 0.09, start = 'top 80%' } = opts
  let ctx: gsap.Context | undefined

  onMounted(() => {
    const root = rootRef.value
    if (!root) return
    const targets = Array.from(root.querySelectorAll<HTMLElement>(selector))
    if (!targets.length) return
    ctx = gsap.context(() => {
      gsap.from(targets, {
        y,
        opacity: 0,
        duration: 0.9,
        ease: 'power3.out',
        stagger,
        scrollTrigger: { trigger: root, start, once: true },
      })
    }, root)
  })

  onBeforeUnmount(() => {
    ctx?.revert()
    ScrollTrigger.getAll().forEach((t) => t.kill())
  })
}
