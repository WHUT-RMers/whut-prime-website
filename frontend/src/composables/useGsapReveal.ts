import { onBeforeUnmount, onMounted, type Ref } from 'vue'
import { gsap } from 'gsap'
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

export interface RevealApi {
  /**
   * 重新扫描 root 内尚未入场的元素并执行入场。
   * 已入场元素记录在案不会重复播放，适合异步渲染完成后补跑
   * （如 NewsSection / NewsView 等列表数据加载后再触发卡片入场）。
   */
  reveal: () => void
}

/**
 * 通用滚动入场（motion-driven 版）：fade + rise + blur，expo.out 缓动。
 *
 * GSAP 规范要点：
 * - 显式 fromTo：起止状态一目了然，且 immediateRender 生效，避免
 *   `gsap.from` 在异步/重放场景下的可见闪烁（FOUC）。
 * - 每个批次一个 gsap.context：组件卸载时统一 revert，tween 与
 *   ScrollTrigger 不泄漏；reveal() 可多次调用（async 渲染后补跑）。
 * - 尊重 prefers-reduced-motion：跳过动画直接显示终态。
 */
export function useScrollReveal(rootRef: Ref<HTMLElement | null>, opts: RevealOptions = {}): RevealApi {
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

  const contexts: gsap.Context[] = []
  const seen = new Set<HTMLElement>()

  const reveal = (): void => {
    const root = rootRef.value
    if (!root) return
    const targets = Array.from(root.querySelectorAll<HTMLElement>(selector)).filter((el) => !seen.has(el))
    if (!targets.length) return

    // 减弱动态：跳过动画，直接呈现最终状态
    if (prefersReducedMotion()) {
      for (const el of targets) {
        seen.add(el)
        gsap.set(el, { clearProps: 'all' })
      }
      return
    }

    const ctx = gsap.context(() => {
      gsap.fromTo(
        targets,
        {
          y,
          x,
          scale,
          opacity: 0,
          filter: blur ? `blur(${blur}px)` : 'none',
        },
        {
          y: 0,
          x: 0,
          scale: 1,
          opacity: 1,
          filter: 'blur(0px)',
          duration,
          ease,
          stagger,
          scrollTrigger: { trigger: root, start, once: true },
          clearProps: 'transform,filter',
        },
      )
    }, root)

    contexts.push(ctx)
    for (const el of targets) seen.add(el)
  }

  onMounted(reveal)

  onBeforeUnmount(() => {
    // 各批次 context 依次 revert：kill 内部 tween 与 ScrollTrigger，还原内联样式
    for (const ctx of contexts) ctx.revert()
  })

  return { reveal }
}
