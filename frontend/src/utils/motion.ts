import { gsap } from 'gsap'

/** 是否启用「减弱动态」 */
export function prefersReducedMotion(): boolean {
  return typeof window !== 'undefined' && window.matchMedia('(prefers-reduced-motion: reduce)').matches
}

/** 常用动效曲线 */
export const EASE = {
  expoOut: 'expo.out',
  expoInOut: 'expo.inOut',
  power3Out: 'power3.out',
} as const

/**
 * 数字滚动计数（data-count 目标值），可配合 ScrollTrigger once 使用。
 */
export function countUp(
  node: HTMLElement,
  target: number,
  duration = 1.8,
  ease = 'power2.out',
  delay = 0,
  onDone?: () => void,
): void {
  const obj = { v: 0 }
  gsap.to(obj, {
    v: target,
    duration,
    ease,
    delay,
    onUpdate: () => {
      node.textContent = String(Math.round(obj.v))
    },
    onComplete: () => onDone?.(),
  })
}
